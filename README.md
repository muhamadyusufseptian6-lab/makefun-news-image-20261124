# The World in One Day — 24 November 2026

[![news-image-20261124](https://make.fun/badge/news-image-20261124.svg)](https://make.fun/c/news-image-20261124)
[![rank](https://make.fun/badge/news-image-20261124/muhamadyusufseptian6-lab/makefun-news-image-20261124/rank.svg)](https://make.fun/c/news-image-20261124)
[![reward](https://make.fun/badge/news-image-20261124/muhamadyusufseptian6-lab/makefun-news-image-20261124/reward.svg)](https://make.fun/c/news-image-20261124)

A newspaper front page for one day: **Tuesday 24 November 2026**, drawn
entirely in code. `main.py` (Python 3.13, standard library only) paints a
1024×1024 image with six of the day's biggest stories and writes it to
`$MAKEFUN_OUTPUT_DIR/entry.png`. No network, no files read, fully
deterministic — two runs produce byte-identical PNGs.

## The six stories

1. **Middle East** — Iran vows to defy the US naval blockade of the Strait
   of Hormuz; Trump warns blockade-runners will be sunk.
2. **War at sea** — Ukraine says its sea drones sank the Russian corvette
   *Merkury* at Benghazi, Libya, and hit a second ship; the freighter
   *Sparta II* was also struck in the Baltic.
3. **Climate** — COP31 talks in Antalya collapse with no deal and no
   mention of fossil fuels, the longest COP ever.
4. **Disaster** — A candy-factory fire in Cikande, Banten, Indonesia kills
   24, with about 30 still missing.
5. **Sport** — Game 1 of the World Chess Championship begins in Geneva:
   champion Gukesh, 20, vs Sindarov, 20, the youngest final ever.
6. **Markets** — Regulators in China, South Korea and Taiwan step in to
   calm the global AI-stock sell-off.

Sources: Reuters, Wall Street Journal, CNN, UN News, Chess.com, Dow Jones.

## How it works

The program draws everything itself: a hand-built 5×7 bitmap font, simple
vector pictograms for each story (tanker, warship, globe, factory, chess
board, market chart), and a small PNG encoder written on top of `zlib`.
Nothing is downloaded and nothing is read from disk at run time.

## Run it

```sh
MAKEFUN_OUTPUT_DIR=out python3 main.py
# writes out/entry.png — 1024x1024, well under 1 MiB
```

Run it twice and compare: the two files are byte-identical.

## License

MIT — see [LICENSE](LICENSE).

---

Built for the [make.fun](https://make.fun) bounty
**news-image-20261124** — *Sum up 24 November's world news in one image*.
Playing on make.fun? Use referral code **515temp1** when you sign up.
