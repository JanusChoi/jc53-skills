#!/usr/bin/env python3
"""
qc.py — videomaker-qc-auto Layer 1：抽 raw signals（零 LLM 依赖）

输入: take 目录（episodes/<集>/takes/<seg>/<take>/）
  必须含 clip.mp4 + request.json
  其它 png/contact.png/tail/ 自动跳过

输出:
  - qc_signals.json  — 客观信号（duration/fps/sharpness/frame_diffs/freeze 帧）
  - qc_frames/      — 抽出的关键帧（首/1s/2s/3s/4s/5s/末/best_tail）供 agent 看

用法:
  python3 qc.py <take_dir> [--fps-check 24] [--sharp-min 50]
"""
import argparse, json, math, re, shutil, subprocess, sys, tempfile
from pathlib import Path


def ffprobe_meta(mp4: Path) -> dict:
    """用 ffprobe 拿 width/height/duration_sec/fps。"""
    cmd = ["ffprobe", "-v", "error",
           "-select_streams", "v:0",
           "-show_entries", "stream=width,height,r_frame_rate,nb_frames:format=duration",
           "-of", "json", str(mp4)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        return {}
    d = json.loads(r.stdout)
    s = d.get("streams", [{}])[0]
    f = d.get("format", {})
    fps_s = s.get("r_frame_rate", "0/1")
    n, den = fps_s.split("/")
    fps = int(n) / int(den) if int(den) else 0
    return {
        "width": int(s.get("width", 0)),
        "height": int(s.get("height", 0)),
        "fps": round(fps, 2),
        "duration_sec": float(f.get("duration", 0)),
        "nb_frames": int(s.get("nb_frames", 0)),
    }


def extract_frames(mp4: Path, out_dir: Path, n: int = 8) -> list:
    """抽 N 帧均匀分布 + 末帧。返回帧文件路径列表。"""
    out_dir.mkdir(parents=True, exist_ok=True)
    paths = []
    # 用 fps=1 抽 1Hz 帧
    cmd = ["ffmpeg", "-y", "-loglevel", "error",
           "-i", str(mp4),
           "-vf", f"fps=1",
           str(out_dir / "f%02d.png")]
    subprocess.run(cmd, check=True, capture_output=True)
    paths = sorted(out_dir.glob("f*.png"))
    # 加末帧（如果 best_tail.png 已存在则用之，否则抽末帧）
    return paths


def sharpness(png: Path) -> float:
    """拉普拉斯方差 → 清晰度。用 PIL + numpy（标准库方式）。
    经典公式：Laplacian(kernel=[[0,1,0],[1,-4,1],[0,1,0]])，var 越大越锐。"""
    try:
        from PIL import Image
        import numpy as np
        a = np.asarray(Image.open(png).convert("L"), dtype=np.float32)
        # 拉普拉斯（4 邻接）：中心 -4，上下左右 -1
        lap = a[1:-1, 1:-1] * 4 - a[:-2, 1:-1] - a[2:, 1:-1] - a[1:-1, :-2] - a[1:-1, 2:]
        return float(lap.var())
    except Exception:
        return 0


def frame_diff(p1: Path, p2: Path) -> float:
    """两帧 PSNR → 像素差 %。高 PSNR = 相近，差小。
    ffmpeg 输出格式: 'PSNR r:.. g:.. b:.. average:21.36 min:.. max:..'
    注意: psnr 是 info 级别，loglevel error 会屏蔽掉。"""
    cmd = ["ffmpeg", "-y", "-loglevel", "info",
           "-i", str(p1), "-i", str(p2),
           "-lavfi", "psnr=stats_file=-",
           "-f", "null", "-"]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        m = re.search(r"PSNR.*average:([\d.]+)", r.stderr)
        if m:
            psnr = float(m.group(1))
            diff_pct = 100 * math.pow(10, -psnr / 20)
            return min(diff_pct, 100.0)
    except Exception:
        pass
    return 0.0


def detect_freeze(frames: list, threshold_pct: float = 0.5) -> int:
    """连续 5+ 帧 diff < threshold 算冻屏。返回 freeze_count。"""
    if len(frames) < 6:
        return 0
    diffs = []
    for i in range(len(frames) - 1):
        diffs.append(frame_diff(frames[i], frames[i + 1]))
    # 找连续低 diff 段（>=5 帧）
    freeze = 0
    cur = 0
    for d in diffs:
        if d < threshold_pct:
            cur += 1
            if cur >= 5:
                freeze += 1
        else:
            cur = 0
    return freeze


def load_request(take_dir: Path) -> dict:
    """读 request.json（run_seg.py 写下的）。"""
    p = take_dir / "request.json"
    if p.exists():
        return json.loads(p.read_text())
    return {}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("take_dir")
    ap.add_argument("--sharp-min", type=float, default=50.0, help="min sharpness 单帧")
    ap.add_argument("--freeze-dur", type=float, default=0.5, help="freeze 检测阈值（diff %）")
    a = ap.parse_args()
    take = Path(a.take_dir).resolve()
    clip = take / "clip.mp4"
    if not clip.exists():
        print(f"clip.mp4 not found in {take}", file=sys.stderr)
        sys.exit(2)

    meta = ffprobe_meta(clip)
    req = load_request(take)

    signals = {
        "take": str(take),
        "clip": str(clip),
        "request": req,
        "meta": meta,
        "thresholds": {
            "duration_match_within_pct": 1.0,
            "sharpness_min": a.sharp_min,
            "freeze_threshold_pct": a.freeze_dur,
        },
        "checks": {},
    }

    # === 1. 时长匹配 ===
    target_dur = req.get("duration")
    if target_dur:
        diff = abs(meta["duration_sec"] - float(target_dur))
        pct = diff / float(target_dur) * 100
        signals["checks"]["duration"] = {
            "passed": pct < signals["thresholds"]["duration_match_within_pct"],
            "target_sec": float(target_dur),
            "actual_sec": meta["duration_sec"],
            "diff_pct": round(pct, 2),
        }

    # === 2. 分辨率 ===
    signals["checks"]["resolution"] = {
        "passed": meta["width"] > 0 and meta["height"] > 0,
        "width": meta["width"],
        "height": meta["height"],
    }

    # === 3. fps ===
    signals["checks"]["fps"] = {
        "passed": meta["fps"] >= 20 and meta["fps"] <= 60,
        "fps": meta["fps"],
    }

    # === 4. 抽帧 + sharpness + frame_diff ===
    frames_dir = take / "qc_frames"
    if frames_dir.exists():
        shutil.rmtree(frames_dir)
    with tempfile.TemporaryDirectory() as td:
        td_frames = Path(td) / "raw"
        frames = extract_frames(clip, td_frames, n=8)
        # sharpness 每帧
        sharps = [sharpness(f) for f in frames]
        # 帧间 diff
        diffs = []
        for i in range(len(frames) - 1):
            diffs.append(frame_diff(frames[i], frames[i + 1]))

        # 把帧复制到 qc_frames/（供 agent 看）
        frames_dir.mkdir(exist_ok=True)
        for i, f in enumerate(frames):
            shutil.copy(f, frames_dir / f"frame_{i:02d}.png")

        if sharps:
            signals["checks"]["sharpness"] = {
                "passed": min(sharps) >= a.sharp_min and sum(sharps)/len(sharps) >= a.sharp_min,
                "avg": round(sum(sharps)/len(sharps), 1),
                "min": round(min(sharps), 1),
                "max": round(max(sharps), 1),
                "frame_sharpness": [round(s, 1) for s in sharps],
            }
        if diffs:
            signals["checks"]["frame_diff"] = {
                "passed": max(diffs) >= 1.0,  # 中段至少有 1% 变化（很宽松）
                "avg": round(sum(diffs)/len(diffs), 2),
                "max": round(max(diffs), 2),
                "min": round(min(diffs), 2),
                "frame_diffs": [round(d, 2) for d in diffs],
            }

        # === 5. freeze 帧 ===
        freeze_count = detect_freeze(frames, threshold_pct=a.freeze_dur)
        signals["checks"]["freeze"] = {
            "passed": freeze_count == 0,
            "freeze_sequences": freeze_count,
        }

    # 综合 decision hint
    fails = [name for name, c in signals["checks"].items() if not c.get("passed", True)]
    signals["decision_hint"] = "accept" if not fails else f"review_needed: {','.join(fails)}"

    # 落盘
    out = take / "qc_signals.json"
    out.write_text(json.dumps(signals, ensure_ascii=False, indent=2))

    # stdout 简明
    print(f"=== QC Layer 1: {take} ===")
    print(f"  duration: {meta.get('duration_sec', '?')}s (target {req.get('duration', '?')}s)")
    print(f"  resolution: {meta.get('width')}x{meta.get('height')}  fps: {meta.get('fps')}")
    if "sharpness" in signals["checks"]:
        s = signals["checks"]["sharpness"]
        print(f"  sharpness: avg={s['avg']} min={s['min']} max={s['max']} {'✅' if s['passed'] else '❌'}")
    if "frame_diff" in signals["checks"]:
        f = signals["checks"]["frame_diff"]
        print(f"  frame_diff: avg={f['avg']}% max={f['max']}% min={f['min']}% {'✅' if f['passed'] else '❌'}")
    if "freeze" in signals["checks"]:
        print(f"  freeze: {signals['checks']['freeze']['freeze_sequences']} sequences {'✅' if signals['checks']['freeze']['passed'] else '❌'}")
    print(f"  → decision_hint: {signals['decision_hint']}")
    print(f"  → {out}")
    print(f"  → frames in {frames_dir}/")


if __name__ == "__main__":
    main()
