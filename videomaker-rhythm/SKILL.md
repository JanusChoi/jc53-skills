---
name: videomaker-rhythm
description: Use when 给 videomaker/H3 短片拍片前/后做节奏量化、3秒钩子/中段爆发/收尾静一拍三件套验证。
---

# videomaker-rhythm

## 何时调用
- 拍任何 videomaker 集之前：先写 `rhythm.md`
- 拍完后：跑 `rhythm_check.py` 验证实际节奏是否达标
- 用户说"感觉节奏不对" / "片子拖" / "钩子不够强"：先跑 rhythm_check 量化问题

## 来源
从 huashu-motion 的"导演规则"借来——他们用 FFmpeg 量过 21 支真实发布片（Apple/Nothing/GoPro/Vercel/Linear/Anthropic 等），得出三条硬规则：
- **3 秒钩子**：片子前 3 秒必须有视觉/听觉的强刺激，否则用户划走
- **中段爆发**：中段必须有 1-2 次节奏突变（cut / 音爆 / 画面变奏），防"全程平铺"
- **最响前停一拍**：最强烈的镜头出现前，先有 0.3-0.5 秒的"静"，让爆发更有冲击

## 标准流程

### 拍片前（agent 必做）

写到 `episodes/<集>/rhythm.md`：

```markdown
# cat-XX 节奏单

## 时长
- 总时长：24s（4 段 × 6s）
- 节奏参考 BPM：120（即每拍 0.5s）

## 4 段 × 拍位对齐

| 段 | 时间 | 拍位 | 钩子/起/升/落 | 描述 |
|----|------|------|--------------|------|
| seg01 | 0:00-0:06 | 1-12 | 钩子 | 宁静开场（墨团窗前看书）→ 3 秒内必须有"暖/冷光对比" |
| seg02 | 0:06-0:12 | 13-24 | 起 | 豆沙开始动（堆雪球） |
| seg03 | 0:12-0:18 | 25-36 | 升 | 中段爆发（墨团画雪猫） |
| seg04 | 0:18-0:24 | 37-48 | 落 | 收尾反转（吓抱→看清笑） |

## 3 秒钩子检查（seg01 末帧 vs seg01+0.5s 帧）
- 必须有可见的状态变化（光影/姿态/物件位置）
- 不得与 seg02 首帧 90% 像素相似（防"看起来没动"）

## 中段爆发检查（seg03 内）
- 必须有 1 次 cut 或 1 次音爆（BGM 音量 +6dB）
- seg02→seg03 不能"无缝"过渡

## 收尾停一拍（seg03 末 0.5s）
- seg03 末尾必须"静止/慢动作/降速"
- seg04 第一拍必须有显著的画面或声音启动
```

### 拍片后（必跑）

```bash
# $SKILL_DIR = 本 skill 安装目录（含 scripts/）
python3 "$SKILL_DIR/scripts/rhythm_check.py" \
  episodes/<集>/rhythm.md \
  episodes/<集>/takes/seg1/take1/clip.mp4 ...
```

输出 `rhythm_report.json`：
```json
{
  "hook_3s": {"passed": true, "frame_diff_pct": 12.3, "min_required": 5.0},
  "midpoint_burst": {"passed": false, "reason": "seg02→seg03 帧相似度 92%（应 <60%）"},
  "ending_hold": {"passed": true, "seg03_last_500ms_speedup_ratio": 0.7},
  "overall": "FAIL",
  "suggestions": ["中段加一次硬切（cat-03 seg12→13 cut 模式可参考）"]
}
```

## 节奏单模板（references/）

| 模板 | 适用 | 路径 |
|------|------|------|
| 4 段短版（24s） | cat-02 / 试片 | `references/template-4seg.md` |
| 20 段长版（120s） | cat-03 / ep01-03 | `references/template-20seg.md` |

## 已知陷阱

- **节奏单不是死规矩**：如果故事需要"全程安静"（eg 治愈系），可以豁免"中段爆发"，但要在 rhythm.md 顶部明示 `豁免原因：治愈系全程安静`
- **节奏对齐拍位而非秒数**：用 BPM（如 120BPM = 0.5s/拍），方便跟 ABC 谱对齐
- **"3 秒钩子"是按用户视角**：平台（B 站/抖音/油管）的留存曲线都在前 3 秒掉 50%+

## 验证 / 完成标准

✅ 拍片前 rhythm.md 写好（4 段版 / 20 段版模板套用）
✅ 拍片后 rhythm_check.py 跑过，输出 `overall: PASS` 或豁免说明
✅ report.json 落盘到 `episodes/<集>/rhythm_report.json`

## 跟其他 skill 的关系

- `video-workflow-analyzer` — 上游，处理已有 packs；rhythm 是新拍的
- `videomaker-qc-auto` — 平行的 QC 检查（rhythm 是节奏，qc 是角色/构图/雪质感）
- `videomaker-sound` — 节奏单里的拍位 = ABC 谱里的 `|:` 标记
