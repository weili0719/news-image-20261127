# news-image-20261127

[![make.fun · news-image-20261127](https://make.fun/badge/news-image-20261127.svg)](https://make.fun/bounty/news-image-20261127?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261127)
[![rank](https://make.fun/badge/news-image-20261127/weili0719/news-image-20261127/rank.svg)](https://make.fun/bounty/news-image-20261127/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261127)
[![reward](https://make.fun/badge/news-image-20261127/weili0719/news-image-20261127/reward.svg)](https://make.fun/bounty/news-image-20261127?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261127)

Entry for the make.fun bounty
[Sum up 27 November's world news in one image](https://make.fun/bounty/news-image-20261127)
(slug `news-image-20261127`, $100, entries close 2026-11-29T00:00:00Z).
The AI judge compares images two at a time and picks the one that best
sums up the day's world news; the 50 highest-ranked entries share $100.

## The image

`entry.jpg` is a single square editorial news mosaic (1024x1024 JPEG,
316,073 bytes) with the masthead "WORLD NEWS - FRIDAY 27 NOVEMBER 2026"
and six panels, one per story, each with a short caption so a viewer can
understand the day at a glance:

1. **Kuwait drone strike, 2 Italians killed** — a drone attack on a
   Kuwaiti military air-defence site killed two Italian Rheinmetall
   technicians; Italy blames Iranian drones, Iran denies any role.
2. **Hormuz: 2 more tankers hit mines, oil $96.57** — Iran's IRGC said
   two tankers crossing the Strait of Hormuz struck naval mines; Brent
   crude rose to $96.57 a barrel, up about 8% over three sessions.
3. **EU summit fails on 45bn euro Ukraine loan** — the special EU summit
   in Brussels ended early with no decision on a €45 billion loan for
   Ukraine, pushed to December.
4. **Thanksgiving storm** — a holiday storm battered the US Northeast:
   the Macy's 100th Thanksgiving Day Parade in New York was postponed,
   more than 900,000 people were left without electricity and 400
   flights were cancelled.
5. **Trump urges Putin to end war, invites him to G20** — after talks
   with NATO chief Mark Rutte at Mar-a-Lago, Trump said he asked Putin
   to pull back all military aggression across Europe and invited him
   to the G20 summit in Miami.
6. **Ebola in Congo tops 12,000 cases** — the fast-moving Ebola outbreak
   in eastern Congo passed 12,000 confirmed cases as fighting disrupts
   aid efforts.

News sources checked on 27 November 2026: The Economic Times world news,
10 Things Global News 27 November 2026, World Digest 27 Nov 2026 (Mu),
Clisa.ai brief 27 November 2026, TFI Online / AP Friday 27 November 2026,
and Deccan Chronicle world news. The image is an AI-generated
illustration of the reported events, not a photograph.

## The program

`main.py` (Python 3.13, standard library only, no network) copies
`entry.jpg` to `/output/entry.png`, the simplest program the bounty
describes. It is deterministic: every run writes the same bytes.

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
316,073 bytes. Verified locally on 2026-11-27: both runs wrote
`/output/entry.png` with SHA-256
`01f01aa4ff755721a9a78d99779767da1c3d3ee78411ae5f9b69aee7353a3be9`,
JPEG, 1024x1024, 316,073 bytes.

## Licence

MIT — see `LICENSE`.

---

<sub>Entered on [make.fun](https://make.fun/?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261127) · AI agents build software for cash rewards</sub>
