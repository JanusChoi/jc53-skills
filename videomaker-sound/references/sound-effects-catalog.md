# 23 种音效用法

来源：huashu-motion 整理的常用发布片音效。我们用 Python 标准库合成，零依赖。

## 用法

```bash
python3 sound_effects.py <name> <out.wav> [--duration 0.3]
```

例如：seg03 末 0.3s 加一个 `glitch` 音效（爆点）
```bash
python3 sound_effects.py glitch glitch.wav --duration 0.4
```

然后 ffmpeg 把它塞到对应时间点：
```bash
ffmpeg -i bgm.wav -i glitch.wav -filter_complex "[1:a]adelay=5400|5400[sfx];[0:a][sfx]amix=inputs=2" out.wav
```

## 全部 23 种

| 名字 | 何时用 | 默认时长 |
|------|--------|---------|
| `thud` | 物体落地 | 0.3s |
| `whip` | 镜头快速甩 | 0.2s |
| `typing` | 文字逐字打出（4 次敲击） | 0.4s |
| `seal` | 盖章 / 落定 | 0.3s |
| `glitch` | 故障 / 突变 | 0.4s |
| `whoosh` | 风声 / 快速划过 | 0.5s |
| `pop` | 弹跳 / 强调气泡 | 0.2s |
| `click` | 按钮点击 | 0.1s |
| `bell` | 铃声 / 提示完成 | 0.6s |
| `chirp` | 鸟鸣 / 上升 | 0.3s |
| `boom` | 爆炸 / 重击 | 0.4s |
| `swoosh` | 柔和划过 | 0.5s |
| `pop_soft` | 软弹 | 0.2s |
| `chime` | 提示音（双音） | 0.5s |
| `swoop` | 下降扫频 | 0.4s |
| `rattle` | 摇动 | 0.4s |
| `thud_heavy` | 重落地 | 0.6s |
| `tap` | 轻敲 | 0.1s |
| `hammer` | 锤击 | 0.2s |
| `zipper` | 拉拉链 | 0.3s |
| `laser` | 激光 | 0.4s |
| `drip` | 水滴 | 0.15s |
| `sparkle` | 闪光 | 0.3s |

## 用 `--duration` 调整

短促音效（click/tap/pop）：0.05-0.2s
持续音效（whoosh/swoosh/bell）：0.3-0.6s
爆发音效（boom/glitch）：0.4-0.8s

## 配合节奏单

每段 seg 的入场帧 / 重要动作帧，对应音效：
- 钩子段（seg01）：开画 0.3s `bell` 或 `chime`
- 起段（seg02）：第二段入场 `pop` 或 `whip`
- 升段（seg03）：爆发 `boom` 或 `glitch`
- 落段（seg04）：反转点 `glitch`，收尾 `chime`

## 自动插入（v2）

未来 skill 加一个 `add_sfx.py` 解析 prompt 里的 `data-sound="X"` 自动批量插入。**v1 手动**。
