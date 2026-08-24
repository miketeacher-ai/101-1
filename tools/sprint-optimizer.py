#!/usr/bin/env python3
"""
Sprint Optimizer — 45-Day Study & Application Portal
Analyzes sat/weak-area-tracker.md AND ielts/progress-tracker.md to suggest
next-day focus. Optimized for 12-14h/day sprint: never suggests adding hours,
only reallocating.

Usage:
    python tools/sprint-optimizer.py --student AZRA|ELA|ELFIIN [--day N]
"""
import argparse
import re
from datetime import date
from pathlib import Path

SPRINT_START = date(2026, 8, 24)   # Day 1 Mon Aug 24
SPRINT_END = date(2026, 10, 7)     # Day 45 Wed Oct 7

STUDENTS = {
    "AZRA": {"band_now": "5.0", "band_target": "6.5", "sat_target": 1300},
    "ELA": {"band_now": "5.5", "band_target": "6.5", "sat_target": 1400},
    "ELFIIN": {"band_now": "6.5", "band_target": "7.5", "sat_target": 1450},
}

# L1-L4 progressive difficulty ladder (toolkit/README.md)
LEVELS = [
    ("L1 Foundation", 1, 7),
    ("L2 Core", 8, 21),
    ("L3 Integration", 22, 35),
    ("L4 Exam", 36, 45),
]

SKIP_TOPICS = {"topic", "domain", "#", "status", "skill", "mock", "day",
               "notes", "fix", "item", "cause", "revisit", "date"}


def sprint_day(day_override=None):
    if day_override is not None:
        return max(1, min(45, day_override))
    delta = (date.today() - SPRINT_START).days + 1
    return max(1, min(45, delta))


def level_for_day(day):
    for name, lo, hi in LEVELS:
        if lo <= day <= hi:
            return name
    return LEVELS[0][0]


def parse_weak_areas(path: Path):
    """Parse sat/weak-area-tracker.md into {section: {topic: status}}."""
    sections = {}
    section = None
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except FileNotFoundError:
        return sections
    for line in text.splitlines():
        heading = re.match(r"^##\s+(.+)", line.strip())
        if heading:
            title = re.sub(r"\s*\(.*?\)\s*$", "", heading.group(1).strip())
            if "Error Log" not in title:
                section = title
                sections.setdefault(section, {})
            continue
        if section is None or not line.strip().startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 2 or set(cells[0].lower()) <= set("- "):
            continue
        status = None
        topic = None
        for i, c in enumerate(cells):
            if c.upper() in ("R", "Y", "G") and i >= 1:
                status = c.upper()
                topic = cells[i - 1]
                break
        if status and topic and topic.strip("-_ ") \
                and not topic.replace(".", "").isdigit() \
                and topic.lower() not in SKIP_TOPICS:
            sections[section][topic] = status
    return sections


def parse_progress(path: Path):
    """Parse ielts/progress-tracker.md: milestones + latest mock scores."""
    info = {"milestones_open": [], "milestones_done": 0, "latest_mock": None}
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except FileNotFoundError:
        return info
    for line in text.splitlines():
        stripped = line.strip()
        m = re.match(r"^-\s\[( |x|X)\]\s(.+)", stripped)
        if m:
            if m.group(1).lower() == "x":
                info["milestones_done"] += 1
            else:
                info["milestones_open"].append(m.group(2).strip())
            continue
        # Score trajectory rows: | Mock N | day | L | R | W | S | Overall |
        cells = [c.strip() for c in stripped.strip("|").split("|")]
        if len(cells) >= 7 and re.match(r"(?i)(diagnostic|mock\s*\d+|real)", cells[0]):
            scores = []
            for c in cells[2:7]:
                num = re.match(r"^(\d+(?:\.\d+)?)", c)
                scores.append(num.group(1) if num else "")
            if any(scores):
                info["latest_mock"] = (cells[0], scores)
    return info


def suggest(student: str, base: Path, day_override=None):
    cfg = STUDENTS[student]
    day = sprint_day(day_override)
    level = level_for_day(day)

    weak = parse_weak_areas(base / student / "sat" / "weak-area-tracker.md")
    progress = parse_progress(base / student / "ielts" / "progress-tracker.md")

    print(f"=== {student} Optimization Report — Day {day}/45 ({level}) ===")
    print(f"IELTS band {cfg['band_now']} -> {cfg['band_target']} | "
          f"SAT target {cfg['sat_target']}")

    # SAT weak areas by section
    reds_by_section = {}
    for sec, topics in weak.items():
        reds = [t for t, s in topics.items() if s == "R"]
        yellows = [t for t, s in topics.items() if s == "Y"]
        greens = [t for t, s in topics.items() if s == "G"]
        reds_by_section[sec] = reds
        total = len(topics)
        print(f"\n[{sec}] R:{len(reds)} Y:{len(yellows)} G:{len(greens)} of {total}")
        for t in reds[:2]:
            print(f"  - RED focus: {t} (20 min warm-up + 45 min timed set)")

    # IELTS side
    print(f"\n[IELTS] Milestones done: {progress['milestones_done']}, "
          f"open: {len(progress['milestones_open'])}")
    for ms in progress["milestones_open"][:2]:
        print(f"  - Next milestone: {ms}")
    if progress["latest_mock"]:
        name, scores = progress["latest_mock"]
        print(f"  - Latest scored row: {name} -> L/R {scores[0]}/{scores[1]}, "
              f"W/S est {scores[2] or '?'}/{scores[3] or '?'}")
    else:
        print("  - No mock scores logged yet — diagnostic must be logged Day 1.")

    # Reallocation plan
    active_reds = sum(len(r) for r in reds_by_section.values())
    print("\n--- Tomorrow's plan (reallocate, never add hours) ---")
    if active_reds:
        picks = []
        secs = [s for s, r in reds_by_section.items() if r]
        for i in range(min(3, active_reds)):
            sec = secs[i % len(secs)]
            if reds_by_section[sec]:
                picks.append(f"{reds_by_section[sec].pop(0)} [{sec}]")
        print("Warm-up order (rotate across sections):")
        for n, p in enumerate(picks, 1):
            print(f"  {n}. {p} — 20 min drill + 45 min timed set @ {level} pass standard")
        print("Reallocate from GREEN topics (two clean sets) to these REDs.")
    else:
        print("No REDs — shift 30 min from strongest area to newest topic for breadth.")
    print(f"Ladder check: all sets today must be tagged {level}; "
          f"logging an easier level means you are behind.")
    print("Next check: Sunday 45-min review — update trackers, then re-run.")


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Sprint Optimizer")
    p.add_argument("--student", choices=STUDENTS.keys(), default="AZRA")
    p.add_argument("--base", default=".")
    p.add_argument("--day", type=int, default=None,
                   help="Override sprint day (1-45); defaults to today's date")
    args = p.parse_args()
    suggest(args.student, Path(args.base), args.day)