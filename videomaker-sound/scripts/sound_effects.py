#!/usr/bin/env python3
"""
sound_effects.py — 23 种音效库（PCM 合成 + WAV 输出）

纯 Python 标准库，零依赖。

每种音效返回一个 (samples, sample_rate) 元组，可直接用 wave 模块写文件。

支持的 23 种（来自 huashu-motion 整理的常用发布片音效）：
  thud        落地/物体碰撞（短促低频）
  whip        甩镜（快速扫频）
  typing      打字（短促敲击 + 多次）
  seal        盖章（单次中等频率 + 短混响）
  glitch      故障（高频随机噪声 + 短促）
  whoosh      风声/快速划过（扫频噪声）
  pop         弹跳（短促中频 + 快速衰减）
  click       点击（极短高频）
  bell        铃声（多次谐波 + 长衰减）
  chirp       鸟鸣/向上扫频
  boom        爆炸/重击（低频 + 噪声）
  swoosh      柔和划过（扫频正弦）
  pop_soft    软弹（轻微低频）
  chime       提示音（双音谐波）
  swoop       下降扫频
  rattle      摇动/噪声
  thud_heavy  重落地（更长低频）
  tap         轻敲（短中频）
  hammer      锤击（中低频 + 噪声）
  zipper      拉拉链（短噪声）
  laser       激光（快速扫频）
  drip        水滴（短低频 + 快速衰减）
  sparkle     闪光（高频谐波 + 快速衰减）

用法:
  python3 sound_effects.py <effect_name> <out.wav> [--duration 0.3]
"""
import argparse, math, random, struct, sys, wave


SR = 44100


def to_samples(samples):
    """归一化 + 16-bit PCM。"""
    peak = max(abs(s) for s in samples) or 1.0
    scale = 0.9 / peak
    return [int(s * scale * 32767) for s in samples]


def write_wav(path, samples, sr=SR):
    with wave.open(str(path), "w") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes(b"".join(struct.pack("<h", s) for s in to_samples(samples)))


def gen(name, duration):
    """调度。"""
    gen_fn = globals().get(f"sfx_{name}")
    if not gen_fn:
        raise ValueError(f"unknown sfx: {name}")
    return gen_fn(duration)


# === 23 种实现 ===

def sfx_thud(d):
    n = int(d * SR); out = []
    for i in range(n):
        t = i / SR
        # 衰减低频正弦
        env = math.exp(-8 * t)
        s = env * math.sin(2 * math.pi * 80 * t)
        out.append(s)
    return out

def sfx_whip(d):
    n = int(d * SR); out = []
    for i in range(n):
        t = i / SR
        f = 200 + 2000 * t / d
        env = math.exp(-3 * t)
        out.append(env * math.sin(2 * math.pi * f * t))
    return out

def sfx_typing(d):
    # 短促敲击 4 次
    out = []
    for k in range(4):
        offset = int((k + 0.5) * d / 5 * SR)
        for i in range(int(0.05 * SR)):
            t = i / SR
            env = math.exp(-50 * t)
            out.append(env * (random.random() * 0.5 + 0.5) * math.sin(2 * math.pi * 1500 * t))
        # 填零对齐
        while len(out) < offset:
            out.append(0)
    return out[:int(d * SR)]

def sfx_seal(d):
    n = int(d * SR); out = []
    for i in range(n):
        t = i / SR
        env = math.exp(-10 * t)
        out.append(env * (math.sin(2 * math.pi * 400 * t) + 0.5 * math.sin(2 * math.pi * 800 * t)))
    return out

def sfx_glitch(d):
    n = int(d * SR); out = []
    for i in range(n):
        t = i / SR
        env = math.exp(-5 * t)
        out.append(env * (random.random() * 2 - 1) * 0.3)
    return out

def sfx_whoosh(d):
    n = int(d * SR); out = []
    for i in range(n):
        t = i / SR
        f = 100 + 500 * math.sin(2 * math.pi * 5 * t)
        env = math.exp(-2 * t) * math.sin(math.pi * t / d)
        out.append(env * (random.random() * 2 - 1))
    return out

def sfx_pop(d):
    n = int(d * SR); out = []
    for i in range(n):
        t = i / SR
        env = math.exp(-30 * t)
        out.append(env * math.sin(2 * math.pi * 600 * t))
    return out

def sfx_click(d):
    n = int(d * SR); out = []
    for i in range(n):
        t = i / SR
        env = math.exp(-100 * t)
        out.append(env * math.sin(2 * math.pi * 2000 * t))
    return out

def sfx_bell(d):
    n = int(d * SR); out = []
    for i in range(n):
        t = i / SR
        env = math.exp(-2 * t)
        out.append(env * (math.sin(2 * math.pi * 800 * t) + 0.5 * math.sin(2 * math.pi * 1600 * t) + 0.3 * math.sin(2 * math.pi * 2400 * t)))
    return out

def sfx_chirp(d):
    n = int(d * SR); out = []
    for i in range(n):
        t = i / SR
        f = 800 + 2000 * t / d
        env = math.exp(-3 * t)
        out.append(env * math.sin(2 * math.pi * f * t))
    return out

def sfx_boom(d):
    n = int(d * SR); out = []
    for i in range(n):
        t = i / SR
        env = math.exp(-6 * t)
        noise = random.random() * 2 - 1
        s = env * (math.sin(2 * math.pi * 60 * t) + 0.4 * noise)
        out.append(s)
    return out

def sfx_swoosh(d):
    n = int(d * SR); out = []
    for i in range(n):
        t = i / SR
        f = 400 - 300 * t / d
        env = math.sin(math.pi * t / d)
        out.append(env * math.sin(2 * math.pi * f * t))
    return out

def sfx_pop_soft(d):
    n = int(d * SR); out = []
    for i in range(n):
        t = i / SR
        env = math.exp(-20 * t)
        out.append(env * math.sin(2 * math.pi * 300 * t))
    return out

def sfx_chime(d):
    n = int(d * SR); out = []
    for i in range(n):
        t = i / SR
        env = math.exp(-1.5 * t)
        out.append(env * (math.sin(2 * math.pi * 600 * t) + math.sin(2 * math.pi * 900 * t)))
    return out

def sfx_swoop(d):
    n = int(d * SR); out = []
    for i in range(n):
        t = i / SR
        f = 1500 - 1200 * t / d
        env = math.exp(-2 * t)
        out.append(env * math.sin(2 * math.pi * f * t))
    return out

def sfx_rattle(d):
    n = int(d * SR); out = []
    for i in range(n):
        t = i / SR
        env = 0.5 + 0.5 * math.sin(2 * math.pi * 20 * t)
        out.append(env * (random.random() * 2 - 1) * 0.4)
    return out

def sfx_thud_heavy(d):
    n = int(d * SR); out = []
    for i in range(n):
        t = i / SR
        env = math.exp(-5 * t)
        out.append(env * math.sin(2 * math.pi * 50 * t))
    return out

def sfx_tap(d):
    n = int(d * SR); out = []
    for i in range(n):
        t = i / SR
        env = math.exp(-60 * t)
        out.append(env * math.sin(2 * math.pi * 1000 * t))
    return out

def sfx_hammer(d):
    n = int(d * SR); out = []
    for i in range(n):
        t = i / SR
        env = math.exp(-20 * t)
        noise = random.random() * 2 - 1
        out.append(env * (math.sin(2 * math.pi * 200 * t) + 0.5 * noise))
    return out

def sfx_zipper(d):
    n = int(d * SR); out = []
    for i in range(n):
        t = i / SR
        env = 0.3 + 0.3 * math.sin(2 * math.pi * 30 * t)
        out.append(env * (random.random() * 2 - 1))
    return out

def sfx_laser(d):
    n = int(d * SR); out = []
    for i in range(n):
        t = i / SR
        f = 200 + 3000 * t / d
        env = math.exp(-2 * t)
        out.append(env * math.sin(2 * math.pi * f * t))
    return out

def sfx_drip(d):
    n = int(d * SR); out = []
    for i in range(n):
        t = i / SR
        env = math.exp(-40 * t)
        out.append(env * math.sin(2 * math.pi * 700 * t))
    return out

def sfx_sparkle(d):
    n = int(d * SR); out = []
    for i in range(n):
        t = i / SR
        env = math.exp(-15 * t)
        out.append(env * (math.sin(2 * math.pi * 3000 * t) + 0.5 * math.sin(2 * math.pi * 4500 * t)))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("effect"); ap.add_argument("out_wav")
    ap.add_argument("--duration", type=float, default=0.3)
    ap.add_argument("--seed", type=int, default=None)
    a = ap.parse_args()
    if a.seed is not None:
        random.seed(a.seed)
    samples = gen(a.effect, a.duration)
    write_wav(a.out_wav, samples)
    print(f"wrote {a.out_wav} ({a.duration}s, sfx={a.effect})")


if __name__ == "__main__":
    main()
