# THE WORLD IN ONE DAY — MONDAY 23 NOVEMBER 2026

[![make.fun · news-image-20261123](https://make.fun/badge/news-image-20261123.svg)](https://make.fun/bounty/news-image-20261123?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)
[![rank](https://make.fun/badge/news-image-20261123/Iyannn11/news-image-20261123/rank.svg)](https://make.fun/bounty/news-image-20261123/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)
[![reward](https://make.fun/badge/news-image-20261123/Iyannn11/news-image-20261123/reward.svg)](https://make.fun/bounty/news-image-20261123?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)

A one-image front page summing up the world's news of Monday 23 November
2026 — built for the [make.fun bounty](https://make.fun/bounty/news-image-20261123).

## The day in one image

`entry.png` (1024x1024) is a broadsheet front page on cream paper:

- **3 heroes** — COP31 collapses in Antalya (no deal, EU walks out over
  fossil fuels), the NATO Council meets in Brussels as Poland presses for
  more eastern troops, and Taiwan bans short selling after the Taiex's
  17.5% weekly rout. Each hero carries a red label chip, an illustration,
  a caption bar, a green REPORTED pill and its source outlet.
- **A real world map** — dotted world outline with 13 numbered pins and
  city labels, from Brussels to Sydney.
- **10 small cards** — each with a tiny national flag, headline, body and
  source outlet.
- **List 14–34** — one line per story: location prefix bold, numbers red.
- **THE DAY IN UTC** — six verified times of the day's events.
- **DATE CHECK** — every story happened, or was first reported, on Monday
  23 November 2026; other days' news is named as left out.

34 stories across 7 regions (Global, Europe, Asia, Middle East, Africa,
North America, Oceania). Every story names its source outlet on its card.
No Israel / Gaza / West Bank stories, by the entrant's standing rule.

## How it is built

`render.py` (Python 3, Pillow only, no network) draws the page
deterministically — two runs are byte-identical — and runs a text-only
pixel gap scan on every card (left 6–7px, right ≥10px). `main.ts`
(Node 22, standard library only) copies `entry.png` to
`$MAKEFUN_OUTPUT_DIR/entry.png` and verifies the copy byte-for-byte.

Run it:

```
python3 render.py            # rebuilds entry.png + gap scan
mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts
```

## Sources

See `SOURCES.md` for every story, its source outlet and the date evidence.
