#!/usr/bin/env python3
"""
render_with_music.py — 视频 + BGM + 音效 → 成片（ffmpeg 合成）

用法:
  python3 render_with_music.py <video.mp4> <bgm.wav> <out.mp4> [--volume 0.6]
"""
import argparse, subprocess, sys
from pathlib import Path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video"); ap.add_argument("bgm"); ap.add_argument("out")
    ap.add_argument("--volume", type=float, default=0.6, help="BGM 音量 0.0-1.0")
    ap.add_argument("--sfx", nargs="*", default=[], help="可选音效文件 @ 时间点, 格式: 'path:sec'")
    a = ap.parse_args()

    cmd = [
        "ffmpeg", "-y", "-loglevel", "error",
        "-i", str(a.video),
        "-i", str(a.bgm),
        "-filter:a", f"volume={a.volume}",
        "-c:v", "copy",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        str(a.out),
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"ffmpeg failed: {r.stderr}", file=sys.stderr)
        sys.exit(1)
    sz = Path(a.out).stat().st_size
    print(f"wrote {a.out} ({sz} bytes, volume={a.volume})")


if __name__ == "__main__":
    main()
