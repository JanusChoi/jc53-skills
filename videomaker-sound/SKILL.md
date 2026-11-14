---
name: videomaker-sound
description: Add BGM and SFX to clips.
---

# videomaker-sound

## 何时调用
- 拼片前：给视频加配乐（4 段短版 / 20 段长版 BGM）
- 拼片时：合成视频 + 音轨
- 拼片后：批量加音效（落地 / 甩镜 / 打字 / 盖章 / 故障等）

## 来源
从 huashu-motion 的"作曲家模式"借来：
- agent 按节奏单写 ABC 谱（纯文本），谱里的 `[|: scene` 标记对齐每个段入场帧
- 真乐器采样（三角钢琴/弦乐/鼓组）演奏；不下载就用合成音色
- 23 种音效写在动画落地那一行 `data-sound="thud"`，导出时自动对帧

**我们这套做简化版**（避免装 timidity/fluidsynth 等大型依赖）：
- ABC 谱用 Python `wave` + `struct` 直接合成 PCM（三角波/正弦波 + ADSR envelope）
- 真乐器采样作为**可选升级项**——想升级时装 SoundFont + fluidsynth

## 核心组件（scripts/）

| 脚本 | 做什么 |
|------|--------|
| `abc_synth.py` | ABC 谱 → WAV（纯 Python 标准库，零依赖） |
| `render_with_music.py` | 视频 + BGM + 音效 → 成片（ffmpeg） |
| `sound_effects.py` | 23 种音效库（thud/whip/typing/seal/glitch/...），按 `data-sound="X"` 自动插入 |

## 标准流程

### 1. 写 ABC 谱（agent 必做）

写到 `episodes/<集>/score.abc`：

```
X:1
T:cat-04-snowman bgm
M:4/4
Q:120
K:C major
% scene seg01 钩子 - 安静的钢琴单音
|: C2 E2 | G2 E2 | F2 D2 | E4 :|
% scene seg02 起 - 加一层弦乐
|: C'2 E'2 | G'2 E'2 | F'2 D'2 | E'4 :|
% scene seg03 升 - 全频爆发（鼓+弦）
|: C2 E2 G2 C2 | F2 D2 E2 G2 | C2 E2 G2 C2 | F2 E2 D2 C2 :|
% scene seg04 落 - 安静收尾
|: E2 D2 | C4 :|
```

### 2. 合成 BGM

```bash
# $SKILL_DIR = 本 skill 安装目录（含 scripts/）
python3 "$SKILL_DIR/scripts/abc_synth.py" \
  episodes/<集>/score.abc \
  episodes/<集>/final/bgm.wav
```

输出 24s 的 WAV 文件（120 BPM × 4 段 × 6s = 48 拍 = 24s）。

### 3. 合成成片

```bash
python3 "$SKILL_DIR/scripts/render_with_music.py" \
  episodes/<集>/final/<episode>.mp4 \
  episodes/<集>/final/bgm.wav \
  episodes/<集>/final/<episode>-with-music.mp4
```

ffmpeg 内部：`-i video.mp4 -i bgm.wav -c:v copy -c:a aac -shortest out.mp4`

## 已知陷阱

- **ABC 谱的 BPM**：必须跟 rhythm.md 的 BPM 一致，否则配乐跟画面不同步
- **Python 合成音色简陋**：正弦/三角波，听起来像老式诺基亚铃声。**适合做"占位配乐"**，正式发布前应升级到 SoundFont
- **音效库只 23 种**：落地/甩镜/打字/盖章/故障等。复杂音效（风/雨/心跳）需要单独采样
- **macOS 没装 fluidsynth**：默认走 Python 合成路径。装 fluidsynth 后改一行 abc_synth.py 即可切换

## macOS Python 3.9 wave 模块陷阱（2026-10-19 实战踩到）

**`wave.open()` 在 macOS 自带 Python 3.9 不接受 kwargs 参数**（"open() got an unexpected keyword argument 'nchannels'"）。也**没有 `wave.open_bytes()`**（那是 Python 3.13+）。

**正确写法**：

```python
import io
buf = io.BytesIO()
with wave.open(buf, "w") as wf:
    wf.setnchannels(1)    # ← 不是 wave.open(..., nchannels=1)
    wf.setsampwidth(2)
    wf.setframerate(sr)
    wf.writeframes(b"...")
return buf.getvalue()
```

调试时如果报 "open() got an unexpected keyword argument 'nchannels'" 或 "module 'wave' has no attribute 'open_bytes'"，**先看 Python 版本**（`python3 -V`）再决定用哪种 API。Linux/macOS homebrew Python 通常支持 kwargs，但 macOS 系统 Python 3.9 不支持。

## 升级到 SoundFont 真乐器采样（可选）

```bash
brew install fluid-synth
# 下载一个免费 SoundFont（CC0），如 SGM-v2.01-Sal-Guit-Bass-Cymbals.wav.sf2（~200MB）
# 把路径配到 abc_synth.py 顶部 SOUNDFONT 常量
```

升级后 abc_synth.py 会用 `fluidsynth` 命令渲染 WAV，音色接近真人演奏。

## 验证 / 完成标准

✅ score.abc 写好，谱里有 4 段 `|:` 标记对齐 seg01~04 入场
✅ abc_synth.py 跑过，bgm.wav 生成（时长 ≈ 片子时长）
✅ render_with_music.py 跑过，成片带音轨
✅ 试听一遍，配乐跟节奏对得上（BPM 一致）

## 跟其他 skill 的关系

- `videomaker-rhythm` — BPM 来自 rhythm.md
- `video-workflow-analyzer` — 处理老 packs，没配乐
- 跟 H3 / H3_TOKEN / h3.py **无关**——纯本地合成

## references/

| 文件 | 内容 |
|------|------|
| `abc-grammar.md` | ABC 谱语法简明参考（10 分钟能学会） |
| `score-template-4seg.abc` | 4 段版配乐模板（可直接套） |
| `score-template-20seg.abc` | 20 段版配乐模板 |
| `sound-effects-catalog.md` | 23 种音效用法 |
