---
name: videomaker-qc-auto
description: Auto QC frame signals + checks for take decisions.
---

# videomaker-qc-auto

## 何时调用
- 每段 take 拍完后：跑 `qc.py` 抽信号（帧差、sharpness、光流、长度）
- 拍完整集后：用 vision_analyze 看 qc 抽出的关键帧，做 accept / retry / reject 决策
- 用户说"感觉哪段不对"：先跑 qc 看客观信号，再人工判断

## 来源
从 huashu-motion 的 `om check`（脚本语法/缺文件/对比度）+ `om qa`（一闪而过的单帧/空档/硬切）借来。

## 设计：双层 QC

**Layer 1 — `qc.py`（纯 Python，零 LLM 依赖）**
抽 raw signals：
- 帧间像素差（PSNR）→ 检测"一闪而过的单帧"、"硬切"
- 每帧 sharpness（拉普拉斯方差）→ 检测"糊了"
- 时长 / 帧率 / 分辨率
- 末帧是否包含预期主体（颜色直方图粗判）
- 输出 `qc_signals.json` + 把关键帧复制到 `qc_frames/` 供 agent 看

**Layer 2 — Agent（用 vision_analyze 工具看帧）**
- 读 qc_signals.json
- 对每个 segment 选 3 帧（首 / 中 / 末）做 vision_analyze
- 问结构化问题（角色是否在、雪质感是否对、构图是否合理）
- 汇总成 `qc_report.json` + 决策（accept / retry_specific_seg / reject_all）

## 标准流程

### 1. 跑 Layer 1（每段 take 完成后必跑）

```bash
python3 ~/.hermes/profiles/cio/skills/video/videomaker-qc-auto/scripts/qc.py \
  episodes/<集>/takes/seg1/take1/
```

输出：
- `qc_signals.json` — 客观信号
- `qc_frames/` — 抽出的 8 帧（首/1s/2s/3s/4s/5s/末/best_tail）

### 2. Agent 看帧（Layer 2）

读取 `qc_signals.json` + 用 vision_analyze 看 `qc_frames/*.png`：

```python
# 伪代码
for seg in qc_signals['segs']:
    frames = sorted(qc_frames_dir.glob(f"{seg['name']}_*.png"))
    for f in frames[:3]:  # 首/中/末
        result = vision_analyze(image_url=str(f), question=q)
        qc_report['segs'][seg['name']]['vision'].append(result)
```

### 3. 决策

| 情况 | 决策 |
|------|------|
| 所有 signals + vision 通过 | `accept` |
| 1-2 段 vision 不通过（如角色缺失） | `retry_specific_seg` |
| 大部分 signals 异常（如时长不对、帧全糊） | `reject_all` |

## qc.py 信号清单

| 信号 | 阈值 | 含义 |
|------|------|------|
| `duration_sec` | == request.duration | 实际时长是否正确 |
| `width/height` | == 1344x768 (final) / 864x480 (preview) | 分辨率是否对 |
| `fps` | == 24 | 帧率 |
| `sharpness_avg` | ≥ 80 | 平均清晰度（拉普拉斯方差） |
| `sharpness_min` | ≥ 50 | 最糊的一帧也得 ≥50 |
| `max_frame_diff` | ≥ 5% | 中段必须有变化 |
| `min_frame_diff` | ≤ 50% | 单帧差不能突然变大（防"一闪而过"） |
| `freeze_frames` | == 0 | 连续 5+ 帧完全相同 = 冻屏 |

## 已知陷阱

- **vision_analyze 不是免费的**（虽然是 Hermes 内置，但每次都消耗 tokens）—— Layer 1 signals 优先，Layer 2 vision 只在 signals 异常时用
- **PSNR 计算**：ffmpeg `psnr` filter 比 numpy 更准，qc.py 默认用 ffmpeg
- **sharpness 拉普拉斯方差**：阈值因风格而异，猫系列阈值 80 适合；3D 渲染阈值要降到 30
- **角色识别**：vision_analyze 看到的"黑白猫"和 prompt 说的"墨团"是不同概念 —— 问问题时要用 prompt 里写的具体特征描述（"戴金圆框眼镜、穿深蓝围裙的奶牛猫"）

## ffmpeg 调用陷阱（3 个 2026-10-19 实战踩到）

1. **PSNR 字段名**：`[Parsed_psnr_0 @ ...] PSNR r:.. g:.. b:.. average:21.36` —— 正则用 `PSNR.*average:` 而不是 `psnr_avg:`。ffmpeg 版本间可能改字段，调试时直接看 stderr 抓完整行
2. **loglevel 屏蔽**：`psnr`、`signalstats` filter 都是 **info 级别**输出。`-loglevel error` 会让 stderr 全空 → 正则无匹配 → 全 0。**永远用 `-loglevel info` 跑这两个 filter**
3. **ffmpeg 7.x signalstats filter 失效**：macOS homebrew ffmpeg 7.1 上 `signalstats` filter 完全不输出 stats（metadata 模式也报 "Option not found"）。**fallback：用 PIL + numpy 算拉普拉斯方差**（qc.py 已经这样做了）：

```python
from PIL import Image
import numpy as np
a = np.asarray(Image.open(png).convert("L"), dtype=np.float32)
lap = a[1:-1, 1:-1] * 4 - a[:-2, 1:-1] - a[2:, 1:-1] - a[1:-1, :-2] - a[1:-1, 2:]
return float(lap.var())  # 标准 sharpness 公式
```

调试 signals 全 0 时，**先看 stderr 是不是空的**（被 loglevel 屏蔽了）—— 别瞎改正则。

## 跟其他 skill 的关系

- `videomaker-rhythm` — 节奏检查是 rhythm_check，QC 检查是 qc.py，分工不重叠
- `video-workflow-analyzer` — 上游处理老 packs，没 QC 自动化
- `videomaker-sound` — QC 在拍片后，配乐在拼片后，时序：拍→QC→retry（如果需要）→拼片→加配乐

## references/

| 文件 | 内容 |
|------|------|
| `vision-prompts.md` | vision_analyze 的结构化提问模板（猫系列 / 通用） |
| `thresholds.md` | 各风格/各 tier 的 sharpness / frame_diff 阈值 |
