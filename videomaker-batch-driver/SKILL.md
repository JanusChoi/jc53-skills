---
name: videomaker-batch-driver
description: Use on overnight N-take videos. Runs chained_drive.py.
---

# videomaker-batch-driver

## 何时调用
- 用户委托"明天 X 点看成片 / 你自主搞 / 一晚上搞定 N 段"——典型的过夜批量拍片
- 一集 ep 的 take1 列表都已经写到 `prompts/segN.txt` + 必要的 ref PNG 路径已知
- 没有手动单条 run_seg / 等 done 的耐心，要串行
- ⚠️ **不要用**：只是想试 1-2 段看看效果（手动 `run_seg.py` 更直观），或 GPU 没空（H3 queue 已经有 N 个 pending jobs，串行排队会卡死）

## 来源 / 思路
猫系列 ep（cat-01~cat-05）一直需要 take1 → qc → edit → bgm 一条龙。原来每段手动跑、要等 notification、再下决定、再跑下一段——成本高、易忘、易错。

chained driver 模式：把 take 列表 + 每段的 ref PNG 路径写到一个 shell 描述文件，**单进程轮询 `takes/<seg>/take1/clip.mp4` 出现 → 立刻 fire 下一段 run_seg.py → 全部完成后跑 edit.sh + render_with_music.py → 退出**。

**关键性质**：
- 单实例、长跑（30-90 分钟），适合 background=true + notify_on_complete=true 自然唤醒
- 撞车自愈：H3 一次只能 1 个 running，`run_seg.py` 内 `wait_idle()` 拉 /jobs 排队；如果自己跑多个 driver 不撞车（各自 wait），资源浪费但不损坏
- 失败优退：每段跑前先看 `clip.mp4` 是否已存在且 > 1 KB，存在就 skip；不存在就 fire；fire 完不健康就停

## 标准流程

### 1. 准备

```bash
# 在 episode 根（继承 cat-04 模板）
EP=/Users/januswing/Downloads/video-workflow-extracted/episodes/<cat-id>
ls $EP/{prompts,docs,takes,final}    # 都要有
cp ../cat-04-snowman/run_seg.py $EP/   # 继承 H3 client 包装（路径已修）
cp ../cat-04-snowman/edit.sh    $EP/   # concat demuxer
ls /Users/januswing/.hermes/profiles/cio/skills/video/videomaker-sound/scripts/render_with_music.py  # 必须有
```

### 2. 写 chained_drive.py（customize 每集）

放在 `$EP/chained_drive.py`。最小骨架（参考 cat-05-catrush 实测版本）：

```python
EP = "/path/to/episodes/<cat-id>"
SEGS = ["seg1", "seg2", "seg3", "seg4"]
REFS_BY_SEG = {
    "seg1": ["/Users/januswing/Downloads/cow-cat1.png",
             "/Users/januswing/Downloads/3flower-cat.png"],
    # segN 不传 ref（首轮纯文本）
}

def wait_clip(seg, timeout_s=900):
    p = Path(f"{EP}/takes/{seg}/take1/clip.mp4")
    t = time.time()
    while not p.exists():
        if time.time()-t > timeout_s:
            return False
        time.sleep(15)
    return p.stat().st_size > 1024

def run_seg(seg):
    refs = REFS_BY_SEG.get(seg, [])
    cmd = ["python3", "run_seg.py", seg, "take1", "--duration", "6"]
    if refs: cmd += ["--refs"] + refs
    return subprocess.run(cmd, cwd=EP).returncode == 0

def main():
    for seg in SEGS:
        if wait_clip(seg, 1200 if seg=="seg1" else 900):
            continue                       # 已经拍过
        if not run_seg(seg):
            log(f"{seg} FAILED — STOPPED")
            return 2
    subprocess.run(["bash","edit.sh"], cwd=EP)
    # render_with_music.py 拼音轨（可选）
    return 0
```

**关键点**：
- `wait_clip` 时长：seg1 容忍长（用户手动 fire 的等到 1200s）；seg2-4 各 900s
- **clip 存在性优于大小判断**：`> 1024` 字节足够（H3 出来的 mp4 至少 200KB；<1KB 大概率 failure 异常产物）
- **失败即停**：不要 retry，retry 会烧 GPU 时间、人工 review 更靠谱
- log 文件 `tee /tmp/<proj>_chain.log`，失败点从 log 一眼可见

### 3. 启动 + 监控

```bash
set -a; source ~/.hermes/profiles/cio/.env; set +a   # 必！launchd 不读 .zshrc
cd $EP
nohup python3 chained_drive.py 2>&1 | tee /tmp/<proj>_chain.log &   # 如果 nohup 被 sandbox 拦，用 terminal(background=true, notify_on_complete=true) 启动
```

**为啥 background=true**：用户在睡，notification 唤醒。

### 4. 次日 review

```bash
cat /tmp/<proj>_chain.log | tail -50
ls $EP/final/                # 应有 cat-XX.mp4 + cat-XX-with-music.mp4
ls $EP/takes/seg*/take1/    # 看每段 8 帧 contact.png + qc_signals.json
# vision_analyze contact.png 做 vision 验证（如果 seg 角色不对）
```

如果 final/ 有 mp4 但 vision 报告有瑕疵→手动 fire `run_seg.py segN take2 --refs ...`（take2 不覆盖 take1，自动建新目录）。

## 已知陷阱

### 1. H3 queue 不空 = 一切变慢
`videomaker-box` 是 mac 上的 Tailscale userspace 出口节点，status 长期 offline 别紧张——**H3 实际跑在远程 Windows `hawking`**，跟 mac 节点无关。验证方式：`python3 h3.py health` 真假为准。如果有别人在跑（queue 有 job 跑 N 分钟），chained driver 会 wait，但 6 小时窗口可能不够。

### 2. chained driver 双副本
之前 reload wrapper 时容易无意中跑出两个 python chained_drive（两个都 polling）。**内核 euid=6611 隔离 → agent 无法 kill 由 wrapper 启动的子进程**。规避：先 `pkill -f chained_drive.py` 后再启动；或改用 wrapper 名（`python3 ... -u "$(realpath cat-id/chained_drive.py)"`）+ supervisor lock file。

### 3. shell wrapper 的 `date "=== ..."` 字串
`date "%H:%M:%S"` 没问题，但 `date "=== ... ==="` 把 `===` 当作 format 字符会报 `illegal time format` → wrapper 崩但 python 子进程已 spawn 仍在跑。debug 时检查 wrapper stdout。

### 4. run_seg.py 不传 ref = 无角色稳定性
新角色（无现成 PNG ref）首轮纯文本 prompt 跑 take1 通常能粗过，但角色一致性差。**take2 再补 ref PNG 重拍是常态**。所以 plan 时段要预算"5-6 段 take × 2 take 轮次 ≈ 10-15 段 take1 提交"。

### 5. macOS Python 系统 3.9 wave 模块 kwargs
如果用 `wave.open(buf, "w", nchannels=1)` 会崩。**用 `setnchannels(1)` 之后调**。见 `videomaker-sound` SKILL.md 详细。

### 6. chained driver 跟 seg1 手动 fire 协调
典型模式：user 启动 seg1 手动 fire（看初始 take 没问题）→ 之后切到 chained driver 跑剩余。chained driver 必须**先 wait seg1 clip 文件存在**再继续。所以首段 timeout 给 1200s 不要抠。

## 跟其他 skill 的关系

- `videomaker-rhythm` — 上游：rhythm.md 决定 seg 时长 / 拍位
- `videomaker-qc-auto` — 拍完每段跑 qc.py 出 signals.json
- `videomaker-sound` — 拼片后跑 render_with_music.py 加 BGM
- H3 client — 走 h3-bridge + h3.py，不在本 skill 里展开

## 验证 / 完成标准

✅ takeN/clip.mp4 全部 4+ 段产出
✅ qc_signals.json 4 段都生成（freeze=0 / sharpness_avg >50 / duration 在 ±10% 范围内）
✅ final/cat-XX.mp4（24-30s 无音）+ final/cat-XX-with-music.mp4（含音轨两版）
✅ /tmp/<proj>_chain.log 显示每段 transition 时间 + edit/bgm 步骤的成功行
✅ vision_analyze 抽查 contact.png，角色对得上 prompts/ 里的 6 猫描述

## scripts/

| 文件 | 干什么 |
|---|---|
| `chained_drive.py` | 单实例过夜批处理 driver；wait_clip → run_seg → edit → render_with_music；失败优退 |

`references/` 留空（适用面窄，本 skill 自己代码即文档）。
