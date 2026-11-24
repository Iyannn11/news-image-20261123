# THE WORLD IN ONE DAY — MONDAY 23 NOVEMBER 2026

![News 23](https://img.shields.io/badge/make.fun-News%2023-14263e)
![Stories](https://img.shields.io/badge/stories-34-c42a2a)
![Regions](https://img.shields.io/badge/regions-7-14263e)
![Date checked](https://img.shields.io/badge/date%20checked-Mon%2023%20Nov%202026-1e7d32)
![Size](https://img.shields.io/badge/image-1024x1024-555555)
![License](https://img.shields.io/badge/license-MIT-green)

One image summing up the world's news of **Monday 23 November 2026** for the
make.fun **News 23** bounty (`news-image-20261123`). Round 3 — a fresh rebuild
that upgrades round 2 toward the Top 10: one dominant lead story, bigger
text everywhere, a real world map with a Europe / Middle East close-up, and
a true 00–24h UTC timeline.

## The image

`entry.png` — 1024×1024, 34 numbered stories, 7 regions:

- **Lead (1):** COP31 collapses — no deal as the EU walks out over fossil
  fuels (headline ~34px, the day's most consequential story).
- **Stories 2–5:** headline + one line each (NATO Council, Taiwan short-
  selling ban, Kospi slide, India v NZ Day 5).
- **Stories 6–13:** headline-only cards with 20×14 SVG flags (Libya,
  Australia, Finland, Myanmar, Bahrain, Lebanon, South Korea, Denmark).
- **Map:** real world map (bundled outlines in `map_data.py`) with 18px
  numbered pins 1–13 and city labels, plus a Europe / Middle East close-up
  inset where the pins crowd together.
- **The Day in UTC:** a real timeline, 00:00–24:00, with a numbered dot at
  each event's true time (00:00 Seoul opens, 00:21 NZ 157/4, 01:00 Taiwan
  ban, 02:11 Starlink re-entry, 08:00 SA v BAN Test, 21:30 Trump speaks).
- **List 14–34:** three columns, one line each, max 8 words per item, bold
  lead phrase, minimum 13px text.
- **DATE CHECK box:** every story happened, or was first reported, on
  Monday 23 November 2026. Items dated 20–22 Nov were left out. No
  Israel / Gaza / West Bank stories.

## How it renders

```sh
python3 render.py   # writes entry.png (deterministic: byte-identical on re-run)
python3 main.py     # stdlib-only entry program: copies entry.png to /output
```

`render.py` uses only files in this repository — `fonts/` (Liberation Serif
and Sans, SIL Open Font License 1.1), `flags/*.svg` (drawn by the script's
own tiny SVG rasterizer), and `map_data.py`. No network, no system fonts,
no emoji. The entry program `main.py` is standard-library only and copies
the rendered image, so the grader's no-network sandbox run reproduces the
exact same bytes; that was verified locally by running it from a clean
directory and comparing SHA-256 hashes.

Checks run on the build: a gap scan over every drawn text box (0 issues —
no overlaps, no text outside the canvas, no truncation), story numbers 1–34
exactly once, map pins 1–13 matching their story numbers, and a
determinism check (two renders, identical bytes).

## Sources

Every story, its outlet, and its date evidence: [`SOURCES.md`](SOURCES.md).
All 34 stories happened, or were first reported, on Monday 23 November 2026
in some time zone.
