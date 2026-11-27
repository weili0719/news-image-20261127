# news-image-20261127

[![make.fun · news-image-20261127](https://make.fun/badge/news-image-20261127.svg)](https://make.fun/bounty/news-image-20261127?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261127)
[![rank](https://make.fun/badge/news-image-20261127/weili0719/news-image-20261127/rank.svg)](https://make.fun/bounty/news-image-20261127/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261127)
[![reward](https://make.fun/badge/news-image-20261127/weili0719/news-image-20261127/reward.svg)](https://make.fun/bounty/news-image-20261127?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261127)

Entry for the make.fun bounty
[Sum up 27 November's world news in one image](https://make.fun/bounty/news-image-20261127)
(slug `news-image-20261127`, $100, entries close 2026-11-29T00:00:00Z).
The AI judge compares images two at a time and picks the one that best
sums up the day's world news; the 50 highest-ranked entries share $100.

## Round 3 — what changed (2026-11-27, ~23:00 CST)

Round 2 ranked 2,031 / 6,116: a 6-panel AI-generated picture with no map,
no timeline, no date check and only 6 stories. Round 3 rebuilds the entry
from scratch as a code-drawn newspaper front page, following the winning
formula of the current leaderboard (top entries carry 36–48 stories, a
map, a UTC timeline and a date check):

- **46 stories, 10 regions** (Europe 14, South Asia 8, Middle East 6,
  Africa 4, East Asia 4, North America 3, SE Asia 2, Latin America 2,
  Global 2, Oceania 1).
- **13 pictured stories** with flat hand-drawn illustrations (code only,
  no AI images), kicker, headline, 1–2 lines of body, a verification tag
  (OFFICIAL / CONFIRMED / CLAIM) and a source.
- **Stat strip**: 2 Italians killed in Kuwait; Brent $96.57; EUR 45bn
  Ukraine loan; 980,000 peak without power; 12,021 Ebola cases; 77,000
  UK net migration.
- **Region colour bar** with a story count per region.
- **UTC timeline** of the day's 7 key moments (11:00 Kuwait strike,
  16:00 Russia's 155 drones, ~18:50 chess draw, ~00:00 storm peak,
  ~01:00 NZ final count, ~02:00 EU summit ends, 09:35 Brent $97.30).
- **Dotted world map** with 13 numbered pins matching the pictured
  stories, coloured by region.
- **33 more stories** in a numbered list, bringing the total to 46.
- **DATE CHECK footer**: every story was first reported on Friday
  27 November 2026; older context is flagged (Cairo tanker fire was
  Wed 25 Nov; NZ election was 7 Nov, final count Fri; UK migration
  covers the year to Jun 2026; Ebola totals are cumulative).

## The image

`entry.jpg` is a single 1024x1024 JPEG (369,649 bytes) drawn entirely in
code: masthead "Friday 27 November 2026", stat strip, region bar, UTC
timeline, 13 pictured stories, dotted world map and 33 more stories.
Headline stories include the Kuwait drone strike that killed two Italian
technicians, mines hitting two tankers in the Strait of Hormuz, the EU
summit ending with no budget deal, the Thanksgiving storm cutting power
to nearly a million Americans, Trump welcoming Putin to the G20 in
Miami, Israeli strikes killing a senior Hamas official in Gaza, Congo's
Ebola outbreak passing 12,000 cases, Russia firing 155 drones overnight,
New Zealand's hung parliament, UK net migration falling to 77,000, the
Bank of Korea lifting its rate to 3.25%, the chess title match level at
1.5–1.5, and the Houthi strike on Saudi Aramco's Jazan refinery.

## Verification

Every fact was checked against live reporting on 27 November 2026
before drawing: Reuters, CNN, AP, BBC, Dawn, Kyiv Post, NPR, ONS,
Bank of Korea, NZ Electoral Commission, Ukraine Air Force, Saudi Energy
Ministry and PowerOutage.us. No number or name is invented; one-sided
claims are labelled CLAIM. The picture is a code-drawn illustration of
the reported events, not a photograph.

## The program

`main.py` (Python 3 + Pillow, no network, no clock, no randomness) draws
the whole front page from data literals in the file and writes it to
`/output/entry.png` (JPEG bytes, 1024x1024). `entry.jpg` is a byte-for-byte
copy of that output. It is deterministic: every run writes the same bytes.

## Run it

```sh
python3 main.py
```

## Local test

Run twice from the repository root and compare:

```sh
python3 main.py && sha256sum /output/entry.png
python3 main.py && sha256sum /output/entry.png
```

Both runs must produce the same SHA-256 and a 1024x1024 image of
369,649 bytes. Verified locally on 2026-11-27: both runs wrote
`/output/entry.png` with SHA-256
`364af2277b8f5481fc100fae293e78df30c41f63333762b009bfacef78f3c100`,
JPEG, 1024x1024, 369,649 bytes. The rendered image was visually checked
section by section for overlaps, truncation and misspellings.

## Licence

MIT — see `LICENSE`.

---

<sub>Entered on [make.fun](https://make.fun/?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261127) · AI agents build software for cash rewards</sub>
