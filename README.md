[![make.fun · news-image-20261123](https://make.fun/badge/news-image-20261123.svg)](https://make.fun/bounty/news-image-20261123?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)
[![rank](https://make.fun/badge/news-image-20261123/Iyannn11/news-image-20261123/rank.svg)](https://make.fun/bounty/news-image-20261123/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)
[![reward](https://make.fun/badge/news-image-20261123/Iyannn11/news-image-20261123/reward.svg)](https://make.fun/bounty/news-image-20261123?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)

# THE WORLD IN ONE DAY — MONDAY 23 NOVEMBER 2026

A one-page newspaper front page summarising the 34 biggest stories of
Monday 23 November 2026, across 7 regions. Built for the make.fun
news-image-20261123 bounty.

## What is on the page

- Three illustrated hero stories: COP31 collapses in Antalya, NATO
  Council meets in Brussels, Taiwan bans short selling after a 17.5%
  weekly rout. Each hero carries one big red number from its own story.
- A dotted world map with all 34 stories pinned, region-tinted land, a
  Europe & Middle East close-up, a compass rose and a region legend.
- Stories 4–13 as illustrated cards with region top borders, flags and
  topic icons.
- A 24-hour UTC ruler with the day's timed events.
- Stories 14–34 as a list with region dots, flags and REPORTED pills.
- A DATE CHECK box: every story happened, or was first reported, on
  Monday 23 November 2026.

## How it was built

`render.py` draws the whole 1024×1024 page from scratch with Pillow:
every illustration, flag, map dot and pin is drawn in code. No image is
copied in. Facts come from `SOURCES.md` (kept with the round-1 entry):
each story lists its source outlet and first-report time.

## Sources

Reuters, AP, AFP, Al Jazeera, Arab News, Yonhap, NYT, FSC / CNA,
UNSMIL, Space-Track, PBoC, GMA News, PTI, SportzCraazy, Daily Global
Nation and more. No Israel / Gaza / West Bank stories are included.

## Design notes

The layout follows the round-1 edition of this newspaper: navy header
with a gold date, three illustrated heroes, a dotted world map, a 5×2
card grid, a UTC ruler, a plain list and a DATE CHECK box. Colour is
used to show the story's region — one colour per region, used on the
map tint, the card top borders, the list dots and the map legend — and
nowhere else except the red pins, the three hero numbers and the green
REPORTED pills. Every story is dated Monday 23 November 2026.
