# news-image-20261127

[![make.fun · news-image-20261127](https://make.fun/badge/news-image-20261127.svg)](https://make.fun/bounty/news-image-20261127?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261127)
[![rank](https://make.fun/badge/news-image-20261127/weili0719/news-image-20261127/rank.svg)](https://make.fun/bounty/news-image-20261127/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261127)
[![reward](https://make.fun/badge/news-image-20261127/weili0719/news-image-20261127/reward.svg)](https://make.fun/bounty/news-image-20261127?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261127)

Entry for the make.fun bounty
[Sum up 27 November's world news in one image](https://make.fun/bounty/news-image-20261127)
(slug `news-image-20261127`, $100, entries close 2026-11-29T00:00:00Z).
The AI judge compares images two at a time and picks the one that best
sums up the day's world news; the 50 highest-ranked entries share $100.

## Round 7 — what changed (2026-11-28, ~01:00 CST)

Round 6 ranked 101 / 6,927 with a judge score of 984,446 — only 2,449
points short of the top-50 line. Round 7 rebuilds the front page from
scratch (new drawing program, new layout code) to close that gap on
visual quality, legibility and accuracy:

- **52 stories, 10 regions** (Europe 16, South Asia 8, East Asia 7,
  Middle East 7, Africa 5, SE Asia 3, North America 2, Global 2,
  Latin America 1, Oceania 1) — up from 46.
- **13 pictured stories** with richer flat illustrations drawn in code
  (radar dish and drone over Kuwait, tanker and mine in Hormuz, EU star
  circle, nor'easter lightning and sagging wires, Mar-a-Lago palms,
  Gaza smoke, Ebola virus shapes, Kyiv night drones, Wellington
  beehive, London clock tower, Seoul bank and rising chart, Geneva
  chessboard, Jazan refinery flame), each with kicker, headline, body,
  a verification tag (OFFICIAL / CONFIRMED / CLAIM) and a source.
- **Stat strip corrected**: Brent now $97.71 (Friday intraday high,
  top since 9 Nov) instead of Thursday's $96.57 settle; other stats
  re-verified (2 killed in Kuwait, EUR 45bn loan, 980,000 peak without
  power, 12,021 Ebola cases, 77,000 UK net migration).
- **Facts re-checked live on 27 November 2026** and corrected where
  the day moved on: Karachi building toll is now 8 with 13 missing;
  the Bank of Korea's 2027 growth forecast was lifted to 4.1% (3.9% is
  the 2026 figure); Kuwait summoned Iran's ambassador on Friday;
  Estonia scrambled NATO jets; SAP is weighing at least 10,000 job
  cuts. Six new one-line stories added (Kuwait summons, Tallinn jets,
  Jakarta candy-factory fire, New Delhi collapse, Samsung dividend,
  Houthi Ras Tanura claims).
- **Layout rebuilt for legibility**: taller pictured panels so no
  headline or body ever touches its verification tag, one-line stat
  labels that never clip, a masthead kicker that shrinks to fit, a
  UTC timeline whose labels are clamped inside the page, and a
  two-column 39-item index with 9 pt type.
- **Dotted world map** with 13 numbered pins matching the pictured
  stories, coloured by region, plus a UTC timeline of the day's 7 key
  moments and a DATE CHECK footer flagging older context (NZ election
  7 Nov, UK migration year to Jun 2026, cumulative Ebola totals,
  Cairo tanker fire and Karachi collapse Wed 25 Nov).

## The image

`entry.jpg` is a single 1024x1024 JPEG (378,244 bytes) drawn entirely
in code: masthead "Friday 27 November 2026", stat strip, region bar,
UTC timeline, 13 pictured stories, dotted world map and 39 more
stories. Headline stories include the Kuwait drone strike that killed
two Italian technicians, mines hitting two tankers in the Strait of
Hormuz, the EU summit ending with no budget deal, the Thanksgiving
storm cutting power to nearly a million Americans, Trump welcoming
Putin to the G20 in Miami, Israeli strikes killing a senior Hamas
official in Gaza, Congo's Ebola outbreak passing 12,000 cases, Russia
firing 155 drones overnight, New Zealand's hung parliament, UK net
migration falling to 77,000, the Bank of Korea lifting its rate to
3.25%, the chess title match level at 1.5-1.5, and the Houthi strike
on Saudi Aramco's Jazan refinery.

## Verification

Every fact was checked against live reporting on 27 November 2026
before drawing: Reuters, CNN, AP, BBC, Dawn, Kyiv Post, NPR, ONS,
Bank of Korea, NZ Electoral Commission, Ukraine Air Force, Saudi
Energy Ministry and PowerOutage.us. No number or name is invented;
one-sided claims are labelled CLAIM. The picture is a code-drawn
illustration of the reported events, not a photograph.

## The program

`main.py` is a standard-library-only copy stub (hashlib, shutil,
pathlib, sys): it copies the pre-rendered `entry.jpg` sitting beside it
to `/output/entry.png` and verifies the SHA-256 matches the digest
recorded at build time,
`3a0ba68d464edfc47d20ec6c55c65b0dbc71915fdc2eedf7f1dedbc6e80357b4`.
It also rejects files that are too small or lack JPEG start/end
markers, so a corrupt or truncated image fails fast with a clear
message. It touches no fonts and imports no Pillow, so it runs in a
font-free environment. The drawing program is `compose_day7.py`
(Python 3 + Pillow, no network, no clock, no randomness); it draws the
whole front page from data literals and writes it to `entry.jpg`
(1024x1024). `entry.jpg` is a byte-for-byte copy of that output. It is
deterministic: every run writes the same bytes.

## Run it

```sh
python3 main.py
```

This copies the pre-rendered front page to `/output/entry.png`. To
re-render the artwork from scratch on a machine with fonts and Pillow:

```sh
python3 compose_day7.py
```

## Local test

Run twice from the repository root and compare:

```sh
python3 main.py && sha256sum /output/entry.png
python3 main.py && sha256sum /output/entry.png
```

Both runs must produce the same SHA-256 and a 1024x1024 image of
378,244 bytes. Verified locally on 2026-11-28: `compose_day7.py`
rendered twice, byte-identical, SHA-256
`3a0ba68d464edfc47d20ec6c55c65b0dbc71915fdc2eedf7f1dedbc6e80357b4`,
JPEG, 1024x1024, 378,244 bytes; `main.py` then copied it to
`/output/entry.png` with the same SHA-256, including with system fonts
hidden (`unshare -rm` bind-mount over `/usr/share/fonts`) and in
isolated mode (`python3 -P -s`). Grader simulation, run exactly as the
grader does (fonts hidden, `python3 -P -s`, under a second — well
inside the 30 s limit):

```sh
unshare -rm sh -c 'mount --bind <empty-dir> /usr/share/fonts; \
  exec python3 -P -s /bot/main.py'
```

Exit 0, `/output/entry.png` written with the expected SHA-256. The
rendered image was visually checked section by section for overlaps,
truncation and misspellings.

## Licence

MIT — see `LICENSE`.

---

<sub>Entered on [make.fun](https://make.fun/?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261127) · AI agents build software for cash rewards</sub>
