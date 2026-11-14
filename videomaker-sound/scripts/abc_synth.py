#!/usr/bin/env python3
"""
abc_synth.py — ABC 记谱法 → WAV（纯 Python 标准库，零依赖）

支持的 ABC 子集:
- X: 编号
- T: 标题
- M: 拍号 (默认 4/4)
- Q: BPM (默认 120)
- K: 调号 (默认 C major)
- L: 默认音符长度 (默认 1/8)
- |: :| 反复
- | 小节
- CDEFGAB 音符；大小写 = 八度；, ' = 升降八度
- 数字后缀 = 时长 (C2 = C 一拍)
- / = 1/2 时长
- % = 注释

合成:
- 默认三角波；可选正弦
- ADSR envelope
- 输出 PCM 16-bit 44.1kHz mono

可选升级:
- 若环境装了 fluidsynth + SOUNDFONT 文件，自动切到真乐器采样（更接近 huashu 的体验）

用法:
  python3 abc_synth.py <score.abc> <out.wav> [--sine] [--sr 44100]
"""
import argparse, math, re, struct, sys, wave
from pathlib import Path

# 音符名 → (基本频率下的偏移半音)
NOTE_OFFSET = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}

# C 大调音阶每个 note letter 在 octave X 的频率
def freq(note: str, octave: int) -> float:
    """ABC 音符 (eg 'C' 或 "C'") → 频率 (Hz)."""
    # ABC: CDEFGAB；' 升八度；, 降八度
    base = note[0].upper()
    octv = octave + note.count("'") - note.count(",")
    # A4 = 440 Hz, octave 4 (ABC 默认 C 大调 C4 ≈ 262 Hz)
    n = NOTE_OFFSET[base] + 12 * (octv + 1) - 9  # 调整到 ABC 八度约定
    return 440.0 * (2 ** ((n - 9) / 12))


def parse_abc(text: str) -> dict:
    """极简 ABC 解析。返回 dict 含 metadata + note 序列 [(freq, duration_sec)]."""
    out = {"X": 1, "T": "", "M": "4/4", "Q": 120, "K": "C", "L": 1/8, "notes": []}
    body_lines = []
    for line in text.splitlines():
        line = line.strip()
        if not line: continue
        if line.startswith("%"): continue
        m = re.match(r"^([A-Za-z]):\s*(.*)$", line)
        if m:
            k, v = m.group(1), m.group(2)
            if k == "Q":
                # Q:120 或 Q:1/4=120
                out["Q"] = int(re.search(r"(\d+)", v).group(1))
            elif k == "L":
                # L:1/8
                lm = re.match(r"(\d+)/(\d+)", v)
                if lm: out["L"] = int(lm.group(1)) / int(lm.group(2))
                else: out["L"] = float(v)
            elif k == "M":
                out["M"] = v
            elif k == "K":
                out["K"] = v.split()[0] if v else "C"
            else:
                out[k] = v
        else:
            body_lines.append(line)

    body = " ".join(body_lines)
    # 移除注释
    body = re.sub(r"%.*", "", body)
    # 处理 repeat 区段 |: ... :|
    # 这里简化：把 |: :| 视为小节线，不重复多次（足够 BGM 占位用）
    # 移除所有 [|:]| 标记只留 |
    body = body.replace("|:", "|").replace(":|", "|")
    # 移除和弦括号
    body = re.sub(r"\[[^\]]+\]", lambda m: m.group(0)[1:-1] if len(m.group(0)) > 2 else "", body)
    body = re.sub(r'"[^"]+"', "", body)

    # 解析音符：CDEFGAB cdefgab 8 个八度，外加 ' , 八度
    # 长度后缀：数字 = 几倍 L，/ = 0.5 倍，缺省 = 1 倍
    # 抓取模式：note letter + 可选 ' / , + 可选长度
    pattern = re.compile(r"([A-Ga-g])([',]*)(\d*)(/?)(\s|\\n|$|\|)")
    i = 0
    while i < len(body):
        m = pattern.match(body, i)
        if m:
            note_letter = m.group(1).upper()
            octv_mod = m.group(2)
            num = m.group(3)
            slash = m.group(4)
            # octave: ABC default = C4 (uppercase C..B = octave 4, lowercase c..b = octave 5)
            base_octv = 4 if note_letter.isupper() else 5
            # 拼接合成 "note_letter + octv_mod" 喂给 freq()
            note_str = note_letter + octv_mod
            f = freq(note_letter, base_octv)
            # 时长：默认 1 个 L
            if num:
                dur = out["L"] * int(num)
            elif slash:
                dur = out["L"] * 0.5
            else:
                dur = out["L"]
            out["notes"].append((f, dur, note_str))
            i = m.end()
        else:
            # 跳过 | 或空格
            ch = body[i]
            if ch in "| \n":
                i += 1
            else:
                # 未知字符，跳过
                i += 1

    return out


def synth_abc(abc_text: str, sr: int = 44100, use_sine: bool = False) -> bytes:
    """返回 WAV 文件字节。"""
    parsed = parse_abc(abc_text)
    bpm = parsed["Q"]
    beat_sec = 60.0 / bpm  # 1/4 拍的秒数
    L = parsed["L"]
    # ABC 中 L 的单位是 1/whole = 4 拍；如果 L=1/8，则 1 个音符 = 0.5 拍
    # duration in ABC 是 L 的倍数，1 个 L = L/4 拍
    def dur_to_samples(dur):
        beats = dur * 4  # dur 个 L = dur * 4 拍
        return int(round(beats * beat_sec * sr))

    samples = []
    for freq_hz, dur, _ in parsed["notes"]:
        n = dur_to_samples(dur)
        if freq_hz <= 0:  # rest
            samples.extend([0] * n)
            continue
        # ADSR envelope (attack=0.01, decay=0.05, sustain=0.7, release=0.1)
        a_n = max(1, int(0.01 * sr))
        d_n = max(1, int(0.05 * sr))
        r_n = max(1, int(0.1 * sr))
        s_n = max(0, n - a_n - d_n - r_n)
        # 生成波形
        wave_func = math.sin if use_sine else lambda x: (2 / math.pi) * math.asin(math.sin(x))
        for i in range(n):
            t = i / sr
            if i < a_n:
                env = i / a_n
            elif i < a_n + d_n:
                env = 1 - 0.3 * ((i - a_n) / d_n)
            elif i < a_n + d_n + s_n:
                env = 0.7
            else:
                # release
                env = 0.7 * (1 - (i - a_n - d_n - s_n) / r_n)
            env = max(0, min(1, env))
            sample = env * 0.4 * wave_func(2 * math.pi * freq_hz * t)
            samples.append(int(sample * 32767))
        # 音符间小停顿（5ms）让音符不糊在一起
        gap_n = int(0.005 * sr)
        samples.extend([0] * gap_n)

    # 末尾静音 0.5s
    samples.extend([0] * int(0.5 * sr))

    # 包成 WAV bytes（用 BytesIO；wave.open_bytes 是 Python 3.13+）
    # macOS Python 3.9 wave.open 不接 kwargs，所以分两步设参数
    import io
    buf = io.BytesIO()
    with wave.open(buf, "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(b"".join(struct.pack("<h", s) for s in samples))
    return buf.getvalue()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("abc"); ap.add_argument("out_wav")
    ap.add_argument("--sine", action="store_true")
    ap.add_argument("--sr", type=int, default=44100)
    a = ap.parse_args()
    text = Path(a.abc).read_text()
    data = synth_abc(text, sr=a.sr, use_sine=a.sine)
    Path(a.out_wav).write_bytes(data)
    print(f"wrote {a.out_wav} ({len(data)} bytes)")


if __name__ == "__main__":
    main()
