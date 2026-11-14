#!/usr/bin/env python3
"""
rhythm_check.py — 验证 videomaker 短片节奏是否满足"3 秒钩子 / 中段爆发 / 收尾静一拍"三件套

用法:
  python3 rhythm_check.py <rhythm.md> <clip1.mp4> [clip2.mp4 ...]

输出:
  rhythm_report.json — 同目录落盘
  stdout — 简明结果

原理:
- 用 ffmpeg 抽帧
- 计算相邻帧像素差（hsum diff / pixels）
- 帧差大的地方 = 视觉爆发点
"""
import json, os, re, subprocess, sys, tempfile
from pathlib import Path


def extract_frames(mp4: Path, out_dir: Path, fps: int = 4) -> list:
    """从 mp4 抽帧，每秒 fps 帧。返回帧文件路径列表。"""
    out_dir.mkdir(parents=True, exist_ok=True)
    cmd = [
        "ffmpeg", "-y", "-loglevel", "error",
        "-i", str(mp4),
        "-vf", f"fps={fps}",
        str(out_dir / "f%04d.png"),
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    return sorted(out_dir.glob("f*.png"))


def frame_diff(p1: Path, p2: Path) -> float:
    """两帧之间的平均像素差（0-1）。用 ffmpeg 信号比较（更稳）。"""
    cmd = [
        "ffmpeg", "-y", "-loglevel", "error",
        "-i", str(p1), "-i", str(p2),
        "-lavfi", "psnr=stats_file=-",
        "-f", "null", "-",
    ]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        # ffmpeg 实际输出格式: "PSNR r:... g:... b:... average:21.36 min:.. max:.."
        # psnr 是 info 级别，必须 loglevel info
        m = re.search(r"PSNR.*average:([\d.]+)", r.stderr)
        if m:
            psnr = float(m.group(1))
            diff_pct = 100 * math.pow(10, -psnr / 20)
            return min(diff_pct, 100.0)
    except Exception:
        pass
    return 0.0


def parse_rhythm_md(md_path: Path) -> dict:
    """解析 rhythm.md，提取 BPM、段表、豁免说明。"""
    text = md_path.read_text()
    out = {"bpm": 120, "segs": [], "exemptions": []}

    # 豁免：豁免原因：xxx
    for m in re.finditer(r"豁免原因[:：](.+)", text):
        out["exemptions"].append(m.group(1).strip())

    # BPM
    m = re.search(r"BPM[:：]\s*(\d+)", text)
    if m:
        out["bpm"] = int(m.group(1))

    # 段表：| seg01 | 0:00-0:06 | ... |
    for m in re.finditer(r"\|\s*(seg\d+)\s*\|\s*([\d:]+)-([\d:]+)\s*\|\s*([\d-]+)\s*\|\s*(\S+)\s*\|", text):
        out["segs"].append({
            "name": m.group(1),
            "start": m.group(2),
            "end": m.group(3),
            "beats": m.group(4),
            "phase": m.group(5),  # 钩子/起/升/落
        })
    return out


def t_to_seconds(t: str) -> float:
    """MM:SS -> 秒。"""
    parts = t.split(":")
    if len(parts) == 2:
        return int(parts[0]) * 60 + float(parts[1])
    return float(parts[0])


def check_rhythm(md_path: Path, clips: list) -> dict:
    rhythm = parse_rhythm_md(md_path)
    segs = rhythm["segs"]
    if not segs:
        return {"overall": "FAIL", "reason": "rhythm.md 没解析到任何段"}

    # 抽帧所有 clip（每个 clip 一个临时目录）
    all_frames = []
    for i, c in enumerate(clips):
        with tempfile.TemporaryDirectory() as td:
            frames = extract_frames(Path(c), Path(td) / f"clip{i}", fps=4)
            all_frames.append([str(f) for f in frames])

    report = {
        "bpm": rhythm["bpm"],
        "segs_count": len(segs),
        "clips_count": len(clips),
        "exemptions": rhythm["exemptions"],
        "checks": {},
        "overall": "PASS",
        "suggestions": [],
    }

    # === 1. 3 秒钩子检查 ===
    # 取 seg01 的帧序列（如果 clips[0] 对应 seg01）
    if all_frames and all_frames[0]:
        f0 = all_frames[0][0]
        f1 = all_frames[0][min(3, len(all_frames[0]) - 1)]  # 1 秒后
        f3 = all_frames[0][min(8, len(all_frames[0]) - 1)]  # 2 秒后
        diff_0_1 = frame_diff(Path(f0), Path(f1))
        diff_1_3 = frame_diff(Path(f1), Path(f3))
        avg_diff = (diff_0_1 + diff_1_3) / 2
        passed = avg_diff >= 3.0  # 经验阈值：3 秒内平均帧差 ≥ 3%
        report["checks"]["hook_3s"] = {
            "passed": passed,
            "frame_diff_pct": round(avg_diff, 2),
            "min_required": 3.0,
            "raw": {"0_to_1s": round(diff_0_1, 2), "1s_to_3s": round(diff_1_3, 2)},
        }
        if not passed:
            report["overall"] = "FAIL"
            report["suggestions"].append(f"前 3 秒平均帧差仅 {avg_diff:.1f}%（<3%），画面几乎不动 → 加 cut 或视觉变化")

    # === 2. 中段爆发检查 ===
    # 找"升"那段（一般在中段位置 = 总段数//2）
    midpoint_idx = len(segs) // 2
    midpoint_seg = segs[midpoint_idx] if segs else None
    if midpoint_seg and midpoint_idx < len(all_frames) and all_frames[midpoint_idx]:
        # 检查中段段内是否有显著帧差
        frames = all_frames[midpoint_idx]
        max_diff = 0
        for i in range(len(frames) - 1):
            d = frame_diff(Path(frames[i]), Path(frames[i + 1]))
            max_diff = max(max_diff, d)
        passed = max_diff >= 8.0  # 经验阈值：中段必须有 ≥8% 单帧差
        report["checks"]["midpoint_burst"] = {
            "passed": passed,
            "max_frame_diff_pct": round(max_diff, 2),
            "min_required": 8.0,
            "phase": midpoint_seg.get("phase"),
        }
        if not passed:
            if "全程安静" not in str(report["exemptions"]):
                report["overall"] = "FAIL"
                report["suggestions"].append(f"中段（{midpoint_seg['name']}）最大帧差仅 {max_diff:.1f}%，缺爆发 → 加 cut 或镜头切换")

    # === 3. 收尾静一拍检查 ===
    # 倒数第二段（落的前一段）的末 0.5s vs 末 1s
    if len(segs) >= 2 and len(all_frames) >= 2 and all_frames[-2]:
        frames = all_frames[-2]
        if len(frames) >= 4:
            # 末 0.5s 内（2 帧 @4fps）帧差
            tail_diffs = [frame_diff(Path(frames[i]), Path(frames[i + 1])) for i in range(len(frames) - 2, len(frames) - 1)]
            tail_avg = sum(tail_diffs) / len(tail_diffs) if tail_diffs else 0
            # 末 1s 内（4 帧）帧差
            late_diffs = [frame_diff(Path(frames[i]), Path(frames[i + 1])) for i in range(len(frames) - 4, len(frames) - 1)]
            late_avg = sum(late_diffs) / len(late_diffs) if late_diffs else 0
            # "静一拍" = 末 0.5s 比末 1s 更慢
            # 如果全程完全静止（所有 diff 都是 0），无法判断静一拍 —— 视为未通过
            if late_avg < 0.5:
                passed = False
                slowdown = 1.0
            else:
                passed = tail_avg <= late_avg * 0.85
                slowdown = late_avg / tail_avg if tail_avg > 0 else 1.0
            report["checks"]["ending_hold"] = {
                "passed": passed,
                "seg_last_500ms_avg_diff": round(tail_avg, 2),
                "seg_last_1s_avg_diff": round(late_avg, 2),
                "slowdown_ratio": round(slowdown, 2),
                "min_slowdown": 1.15,
            }
            if not passed:
                report["overall"] = "FAIL"
                report["suggestions"].append(f"末段（{segs[-2]['name']}）收尾未减速（ratio={slowdown:.2f}）→ 加慢动作或定格")

    return report


def main():
    if len(sys.argv) < 3:
        print("Usage: rhythm_check.py <rhythm.md> <clip1.mp4> [clip2.mp4 ...]", file=sys.stderr)
        sys.exit(2)
    md_path = Path(sys.argv[1])
    clips = sys.argv[2:]
    if not md_path.exists():
        print(f"rhythm.md not found: {md_path}", file=sys.stderr)
        sys.exit(2)

    report = check_rhythm(md_path, clips)

    # 落盘到 rhythm.md 同目录
    out = md_path.parent / "rhythm_report.json"
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2))

    # stdout 简明结果
    print(f"=== Rhythm Check ===")
    print(f"BPM: {report['bpm']}  segments: {report['segs_count']}  clips: {report['clips_count']}")
    if report["exemptions"]:
        print(f"豁免: {'; '.join(report['exemptions'])}")
    for name, c in report["checks"].items():
        flag = "✅" if c["passed"] else "❌"
        print(f"  {flag} {name}: {c}")
    print(f"Overall: {report['overall']}")
    if report["suggestions"]:
        print("Suggestions:")
        for s in report["suggestions"]:
            print(f"  - {s}")
    print(f"\n→ {out}")

    sys.exit(0 if report["overall"] == "PASS" else 1)


if __name__ == "__main__":
    main()
