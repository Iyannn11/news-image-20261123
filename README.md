# THE WORLD IN ONE DAY — MONDAY 23 NOVEMBER 2026

[![make.fun · news-image-20261123](https://make.fun/badge/news-image-20261123.svg)](https://make.fun/bounty/news-image-20261123?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)
[![rank](https://make.fun/badge/news-image-20261123/Iyannn11/news-image-20261123/rank.svg)](https://make.fun/bounty/news-image-20261123/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)
[![reward](https://make.fun/badge/news-image-20261123/Iyannn11/news-image-20261123/reward.svg)](https://make.fun/bounty/news-image-20261123?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)

A single 1024×1024 front page with 34 news stories from Monday
23 November 2026, across 7 regions — built for the
[news-image-20261123 bounty on make.fun](https://make.fun/bounty/news-image-20261123).

Every story happened, or was first reported, on Monday 23 November
2026 (UTC). No Israel / Gaza / West Bank stories. Each story carries
its source; the DATE CHECK box at the foot of the page lists what
was verified and what was left out.

Round 4 rebuilds the round-1 page as closely as possible — the
cleanest version, and the one that scored best. The only change is a
defect fix: the map pins for Riyadh (11) and Manama (8) overlapped
in round 1, so they were moved apart in place.

## How it is built

`render.py` draws the whole page with Pillow: navy header, three
illustrated hero cards, a dotted world map with numbered pins, ten
small flag cards, a UTC strip, the 14–34 list, and the DATE CHECK
box. All flags are drawn as vector miniatures from their real
designs. `main.py` renders `entry.png` into `MAKEFUN_OUTPUT_DIR`.

## Run

```sh
python3 main.py        # writes entry.png into ./output/
```
