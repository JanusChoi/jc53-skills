#!/usr/bin/env python3
"""autonomous overnight batch driver for videomaker episodes.

Usage (from the episode root):
  # load env vars required by your render backend (via your secret mechanism)
  python3 <videomaker-batch-driver>/scripts/chained_drive.py \
      --ep /path/to/episodes/<id> \
      [--segs seg1,seg2,seg3,seg4] \
      [--refs-seg1 /path/ref1.png,/path/ref2.png] \
      [--duration 6] \
      [--edit-script edit.sh] \
      [--render]           # add BGM (requires score.abc + render_with_music.py)
      [--render-script /path/to/videomaker-sound/scripts/render_with_music.py] \
      [--log /tmp/proj_chain.log]

Sequence (for each seg in order):
  wait until takes/<seg>/take1/clip.mp4 exists (15s poll, configurable timeout)
  if not, fire: python3 run_seg.py <seg> take1 --refs <refs> --duration <duration>
  if it fails, log + stop (no retry — let the user review in the morning)
After all segs done:
  ./edit.sh → final/<id>.mp4
  if --render + score.abc exists, run videomaker-sound render_with_music.py
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time
from pathlib import Path

DEFAULT_SEGS = ["seg1", "seg2", "seg3", "seg4"]
DEFAULT_DURATION = 6
DEFAULT_EDIT_SCRIPT = "edit.sh"
# Prefer --render-script, else VIDEOMAKER_SOUND_RENDER, else sibling skill path.
DEFAULT_RENDER_WITH_MUSIC = os.environ.get(
    "VIDEOMAKER_SOUND_RENDER",
    str(
        Path(__file__).resolve().parents[2]
        / "videomaker-sound"
        / "scripts"
        / "render_with_music.py"
    ),
)


def log(msg: str, log_path: str):
    line = f"[{time.strftime('%H:%M:%S')}] {msg}"
    print(line, flush=True)
    with open(log_path, "a") as fh:
        fh.write(line + "\n")


def wait_clip(ep: Path, seg: str, timeout_s: int, log_path: str) -> bool:
    p = ep / "takes" / seg / "take1" / "clip.mp4"
    log(f"wait {seg} clip...  (timeout {timeout_s}s)", log_path)
    t0 = time.time()
    while not p.exists():
        if time.time() - t0 > timeout_s:
            log(f"TIMEOUT waiting {seg} clip >{timeout_s}s", log_path)
            return False
        time.sleep(15)
    sz = p.stat().st_size
    log(f"{seg} clip ready ({sz:,}B)  [{time.time()-t0:.0f}s wait]", log_path)
    return sz > 1024


def run_seg(
    ep: Path, seg: str, refs: list[str], duration: int, log_path: str
) -> bool:
    cmd = [
        "python3",
        str(ep / "run_seg.py"),
        seg,
        "take1",
        "--duration",
        str(duration),
    ]
    if refs:
        cmd += ["--refs"] + refs
    log(f"RUN {' '.join(cmd)}", log_path)
    r = subprocess.run(cmd, cwd=str(ep), capture_output=True, text=True)
    log(f"  → returncode={r.returncode}", log_path)
    if r.stdout:
        for ln in r.stdout.strip().splitlines()[-12:]:
            log(f"    stdout: {ln}", log_path)
    if r.returncode != 0:
        err_tail = r.stderr.strip().splitlines()[-5:] if r.stderr else ["(no stderr)"]
        log(f"  ✗ {seg} FAILED — stderr: {err_tail}", log_path)
    return r.returncode == 0


def run_edit(ep: Path, edit_script: str, log_path: str) -> bool:
    log(f"EDIT {edit_script}", log_path)
    r = subprocess.run(
        ["bash", edit_script], cwd=str(ep), capture_output=True, text=True
    )
    if r.stdout: log(f"  edit: {r.stdout.strip()}", log_path)
    if r.returncode != 0:
        log(f"  ✗ edit FAILED — {r.stderr.strip() if r.stderr else '(no stderr)'}", log_path)
    return r.returncode == 0


def run_render(ep: Path, render_script: str, log_path: str) -> bool:
    final = ep / "final" / f"{ep.name}.mp4"
    out = ep / "final" / f"{ep.name}-with-music.mp4"
    score = ep / "score.abc"
    if not score.exists():
        log(f"  render skipped (no score.abc)", log_path)
        return False
    if not final.exists():
        log(f"  render skipped (no {final})", log_path)
        return False
    if not Path(render_script).exists():
        log(f"  render skipped (script missing: {render_script})", log_path)
        return False
    cmd = ["python3", render_script, str(final), str(out), "--abc", str(score)]
    log(f"RENDER: {' '.join(cmd)}", log_path)
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode == 0:
        log(f"  ✓ {out.name}", log_path)
    else:
        log(f"  ✗ render FAILED — {r.stderr.strip()[-200:]}", log_path)
    return r.returncode == 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ep", required=True, help="episode root (with prompts/ and takes/)")
    ap.add_argument("--segs", default=",".join(DEFAULT_SEGS), help="comma-seg list")
    ap.add_argument("--refs-seg1", default="", help="comma-PNG for seg1 refs (or any seg if named)")
    ap.add_argument("--duration", type=int, default=DEFAULT_DURATION)
    ap.add_argument("--edit-script", default=DEFAULT_EDIT_SCRIPT)
    ap.add_argument("--render", action="store_true", help="also add BGM")
    ap.add_argument(
        "--render-script",
        default=DEFAULT_RENDER_WITH_MUSIC,
        help="path to videomaker-sound render_with_music.py",
    )
    ap.add_argument("--log", default="/tmp/chained_drive.log")
    args = ap.parse_args()

    ep = Path(args.ep).resolve()
    if not ep.exists():
        print(f"ep not found: {ep}")
        return 1
    segs = args.segs.split(",")
    refs_seg1 = [r for r in args.refs_seg1.split(",") if r]

    log(f"=== chained driver start ===", args.log)
    log(f"EP={ep}", args.log)
    log(f"LOG={args.log}", args.log)

    for i, seg in enumerate(segs):
        clip = ep / "takes" / seg / "take1" / "clip.mp4"
        if clip.exists() and clip.stat().st_size > 1024:
            log(f"{seg}: existing clip, skipping run", args.log)
            continue

        # first seg gets longer timeout (often manually-fired first take)
        timeout = 1200 if i == 0 else 900
        if not wait_clip(ep, seg, timeout, args.log):
            # if first seg not yet there, maybe we need to fire it
            if i == 0:
                log(f"first seg {seg} not seen after {timeout}s, firing myself", args.log)
                refs = refs_seg1 if seg == "seg1" else []
                if not run_seg(ep, seg, refs, args.duration, args.log):
                    log(f"STOPPED at {seg}", args.log); return 2
                continue
            log(f"STOPPED at {seg}", args.log); return 2

        # run next seg
        refs = refs_seg1 if seg == "seg1" else []
        if not run_seg(ep, seg, refs, args.duration, args.log):
            log(f"STOPPED at {seg}", args.log)
            return 2

    # edit
    final_mp4 = ep / "final" / f"{ep.name}.mp4"
    if not final_mp4.exists():
        if not run_edit(ep, args.edit_script, args.log):
            log("STOPPED at edit", args.log); return 3
    else:
        log(f"final mp4 exists, skipping edit", args.log)

    # render (optional)
    if args.render:
        run_render(ep, args.render_script, args.log)

    log("=== chained driver done ===", args.log)
    return 0


if __name__ == "__main__":
    sys.exit(main())
