# news-image-20261127

[![make.fun · news-image-20261127](https://make.fun/badge/news-image-20261127.svg)](https://make.fun/bounty/news-image-20261127?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261127)
[![rank](https://make.fun/badge/news-image-20261127/weili0719/news-image-20261127/rank.svg)](https://make.fun/bounty/news-image-20261127/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261127)
[![reward](https://make.fun/badge/news-image-20261127/weili0719/news-image-20261127/reward.svg)](https://make.fun/bounty/news-image-20261127?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261127)

Entry for the make.fun bounty
[Sum up 27 November's world news in one image](https://make.fun/bounty/news-image-20261127)
(slug `news-image-20261127`, $100, entries close 2026-11-29T00:00:00Z).
The AI judge compares images two at a time and picks the one that best
sums up the day's world news; the 50 highest-ranked entries share $100.

## Round 10 — what changed (2026-11-28, ~13:00–14:00 CST)

Round 9 ranked 11 / 9,983 with a judge score of 990,558 — 2,682 points
above the top-50 line but one place outside the top 10. Round 10 rebuilds
the front page from scratch (new drawing program, new layout code) to
close that gap on visual impact and legibility, the two things the
previous day's winners do best:

- **Taller, brighter hero pictures.** The top-3 stories now get 112 px
  tall illustrations on pale skies with big, simple subjects — a large
  drone over the Kuwait radar site, a big red tanker burning off Oman,
  the EU parliament under a gold star circle — instead of the small,
  dark pictures round 9 had.
- **WHY IT MATTERS lines** on all three heroes, one short line each,
  so the judge sees at a glance why each top story matters.
- **Masthead date fixed.** "Friday 27 November 2026" is drawn in a
  single navy colour with the red kicker on its own clear band below it;
  round 9's red "7" overlap is gone.
- **Dark scenes re-lit.** Kyiv is now bright dusk (orange horizon,
  violet sky, lit windows, yellow drone trails) instead of near-black
  night; the storm, Gaza and refinery pictures are all drawn on pale
  daylight skies.
- **Map pins un-crowded.** The dotted world map now uses leader lines:
  each numbered pin is nudged away from its true spot with a thin line
  back to it, so the Europe and Gulf clusters no longer overlap.
- **Same coverage, same facts.** Still 52 stories, 10 regions, 13
  pictured stories, the 6-number stat strip, the UTC timeline, the
  region bar, and the DATE CHECK / HOW SURE footers — all facts from
  the verified round-9 set (Reuters, AP, BBC, CNN, Dawn, Kyiv Post,
  NPR, ONS, Bank of Korea, NZ Electoral Commission, DRC health
  ministry, Ukraine Air Force, Saudi Energy Ministry).

## Files

- `main.py` — the graded entry point. Standard library only: it checks
  `entry.jpg` (JPEG magic bytes, exact size, SHA-256) and copies it to
  `/output/entry.png`. It draws nothing and needs no fonts or network.
- `compose_day10.py` — the drawing program (Pillow + DejaVu fonts on
  the build machine). Run it twice to confirm the render is
  byte-identical; it writes `entry.jpg` (1024x1024, 350,073 bytes).
- `entry.jpg` — the rendered front page.

## Reproduce

```sh
python3 compose_day10.py   # writes entry.jpg
python3 compose_day10.py   # second run: same SHA-256
python3 -P -s main.py      # writes /output/entry.png
```

Verified 2026-11-28: two renders of `entry.jpg` are byte-identical
(SHA-256 `aaccf148de9dbc058ec13ee904722ecaa9cbe7dbf84a70a9efec15c0a07a8e21`,
350,073 bytes, 1024x1024). Grader simulation — `python3 -P -s` with the
system fonts hidden (`unshare -rm`, empty bind over
`/usr/share/fonts`), 30 s limit — exits 0 in ~0.06 s and the written
`/output/entry.png` matches the same SHA-256.

## Round 10 fix — truncated card bodies (2026-11-28, ~13:15–13:30 CST)

Blind review of the first round-10 render found 7 of the 10 smaller
pictured stories had body text cut off mid-sentence (the body box fits
2 lines and the texts were too long). All 7 bodies were shortened so
each wraps to exactly 2 lines at the measured 10 px / 178.4 px box
(PIL text measurement, not guesswork); facts unchanged, only wording
trimmed:

- #5 Trump: "Trump says Putin "would like to make a deal" on Ukraine."
- #6 Gaza: "Hamas official Abu Nada killed in Gaza, third since Tue."
- #7 Ebola: "12,021 cases, 5,304 dead; fighting forces responders out."
- #8 Kyiv: "110 downed, hits at 27 sites; Estonia scrambles jets."
- #9 NZ: "Coalition holds 65 of 130, one short; Opportunity (7) now decides."
- #11 Korea: "Third hike since July, 5-2; 2027 growth lifted to 4.1% on chips."
- #12 Chess: "Game 3 ends in a 60-move draw; Gukesh holds Black. Game 4 Sat."

Re-rendered twice (byte-identical, new SHA-256 above); all 13 pictured
bodies verified complete by PIL measurement and by viewing the render
at full size and in 2x zoomed crops — every body ends with a period and
reads as a complete sentence, and every headline, WHY IT MATTERS line,
stat, timeline label, list item and footer is complete with no
overflow onto another card. Region bar sums to 52 across 10 regions;
note its two smallest segments (LATAM 1, OCEANIA 1, ~19 px each) carry
no label and N AMER / GLOBAL show a bare "2" — pre-existing round-10
design, left as-is (a 19 px segment cannot hold a name+number label).

## Licence

MIT — see `LICENSE`.
