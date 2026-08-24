# Optimization Tools

**Sprint:** Day 1 Mon Aug 24 - Day 45 Wed Oct 7, 2026 | 12-14h/day | 3 students, 132 files

These tools exist to **reallocate** time, not add it. Every hour in the sprint is already budgeted.

## sprint-optimizer.py

Analyzes **both** trackers and suggests tomorrow's warm-up:

- `sat/weak-area-tracker.md` — R/Y/G counts per section (Math / Reading / Writing) + top RED topics
- `ielts/progress-tracker.md` — milestone progress + latest logged mock scores
- Sprint day auto-computed from today's date, mapped to the L1–L4 difficulty ladder

```bash
python tools/sprint-optimizer.py --student AZRA
python tools/sprint-optimizer.py --student ELA
python tools/sprint-optimizer.py --student ELFIIN
python tools/sprint-optimizer.py --student ELA --day 25   # override sprint day
```

Output: per-section R/Y/G tally, next open milestones, a 3-topic warm-up rotation
across sections at the current ladder level, plus the rule "shift 30 min from GREEN to RED".

Run it:
- Daily after error-loop (2 min)
- Sunday review (45 min) — update tracker first, then run

## Dashboard (index.html) — built-in optimizer

Each student's `index.html` already contains:
- **Rings:** overall + IELTS/SAT/Portfolio % (live from checkboxes)
- **Mastery grid:** 20 topics click-cycle weak→mid→OK (persisted)
- **Tally:** "X weak / Y mid / Z OK" live count
- **Chart:** 4 practice-test scores with reference lines (spec/stretch/target)
- **Word counters:** with gradient progress bars and over-limit red state
- **Countdowns:** to Oct 1 (IELTS), Oct 3 (SAT), Nov 1 (ED/EA), Jan 1 (RD)
- **University table:** filter All/Reach/Match/Safety + persisted Status select

All state persists via `localStorage` (`*_portal_v1`) so reallocation decisions survive browser close.

## Content Optimization Principles Applied

1. **Single source of truth:** `weak-area-tracker.md` exact topic names match `sat/content-creation/math-topics.md` — one rename breaks nothing.
2. **Free tools only:** Colab, World Bank/IMF/TCMB APIs, GitHub, Canva — zero paid dependencies.
3. **Pilot early:** Workshop pilot Day 18 (Azra/Ela) and muhtar permission Day 16 (Elfin) catch flaws before execution week.
4. **Reuse, not redo:** Research charts → workshop material; workshop metrics → essays and activities; scholarship essays reused across 8 programs with 1 evening tailoring each.
5. **Print CSS:** all dashboards print black-on-white task lists for daily PDF export without extra tooling.

## When to Optimize

- Same error cause 3 days → change drill tomorrow (progress-tracker.md Red Flags)
- Timing fails 2 mocks → one untimed accuracy week, then rebuild timing
- Skipped error logs 2×/week → cut secondary drill; the log is the system

No new hours. Just smarter allocation.
