# Ziggurat Pachinko — prototype

Live: https://georgeburda.github.io/pachinko-ziggurat-proto/

A pachinko-style game with a Babylon / ziggurat theme, built for a portrait phone. `index.html` (canvas + vanilla JS) plus `assets/` (raster art, about 1 MB in total).

## Rules
- **Tap** to play a round: **100 balls for 100 credits** (1 credit per ball). All balls drop at once as a waterfall. **Tap during the animation** to skip straight to the result.
- The ziggurat has 4 tiers (I at the bottom, IV at the top). Balls fall through the gold peg field into the 9 slots of the tier they are on:
  - **credit slots**: pay credits per ball (`–` = empty);
  - **GATE**: the ball rises to the next tier and falls again, where the slots pay more;
  - **jackpot slot**: one per tier and rare. It pays a multiple of the **total bet**: MINI 10× (1,000), MINOR 30× (3,000), MAJOR 150× (15,000), GRAND 1000× (100,000; the centre slot of tier IV).
- **Omen colours:** when balls reach tier II/III/IV, that tier's gate (or the Grand slot on IV) glows blue, red or gold. Gold means a ball is much more likely to go through (weights blue/red/gold: 15/35/50 if one will, 78/19/3 if none will).
- **Hanging Gardens** (kakuhen-style): reaching tier IV makes the tier I gate 2.5× more likely for the next 5 rounds.
- Every outcome is decided by the RNG when the round starts. The peg bounces are only an animation: each ball follows a randomised peg-by-peg path that ends in the slot it was already given.

## Slot tables (credits per ball; G = gate, J = jackpot)
| Tier | slots (left → right) | weights |
|---|---|---|
| I   | 5, 2, 1, –, G, –, 1, 2, MINI      | 1200, 3075, 14000, 31925, 800, 31925, 14000, 3075, 2 |
| II  | 150, 40, 20, –, G, –, 20, 40, MINOR | 4000, 11000, 16000, 12000, 6000, 12000, 16000, 11000, 80 |
| III | 1500, 400, 150, –, G, –, 150, 400, MAJOR | 2500, 9000, 16000, 10000, 12000, 10000, 16000, 9000, 280 |
| IV  | 5000, 1500, 500, 200, GRAND, 200, 500, 1500, 3000 | 3000, 10000, 18000, 15000, 250, 15000, 18000, 10000, 5000 |

## Math (exact calculation + Monte-Carlo, continuous play including Hanging Gardens)
- **RTP: exact long-run 94.01%.** Base rounds pay 91.48%; Hanging Gardens rounds pay 156.2% and make up 3.9% of all rounds.
- Monte-Carlo, 10M rounds: 94.26% = tier I 46.32% + II 20.43% + III 10.72% + IV 7.25% + jackpots 9.53%. Grand hits are rare and huge, so the sim figure varies by about ±0.2%.
- How often a round reaches each tier: II 56.5%, III 5.6% (1 in 18), IV 0.82% (1 in 123).
- Exact jackpot odds per round: MINI 1 in 501, MINOR 1 in 1,301, MAJOR 1 in 5,249, GRAND 1 in 46,167.
- Round result (credits back for a 100 bet):

  | Result | Share of rounds |
  |---|---|
  | <50 | 36.5% |
  | 50–80 | 37.1% |
  | 80–100 | 12.1% |
  | 100–200 | 8.4% |
  | 200–500 | 4.8% |
  | 500–1000 | 0.48% |
  | 1000–5000 | 0.66% |
  | 5000+ | 0.05% |

  Median 56, p90 124, p99 549, p99.9 3,061. Max seen in the sim: 100,443.

## Test URL parameters
`?seed=N` (repeatable RNG), `?tier=2|3|4` (force the next round to reach that tier), `?gardens=1` (start in Hanging Gardens), `?turbo=1` (faster animation). The balance is stored in localStorage (`pachinko_ziggurat_proto_v1`). If you reload during a round, its win is credited when the page loads again.

## v2 art and effects
- **Raster art** (`assets/*.webp`): generated locally with the open text-to-image model *stabilityai/sd-turbo* (prompts in `tools/prompts.json`), then cropped, keyed, recoloured and compressed with `tools/process.py`. It includes:
  - painted backdrops for each tier: the ziggurat at night, twilight terraces, the Hanging Gardens at sunset, and a golden summit at dawn;
  - Ishtar-gate lapis bricks;
  - lion and mushhushshu dragon friezes;
  - a gold filigree texture and carved sandstone;
  - a rosette medallion;
  - the gate portal;
  - jackpot plaques: MINI turquoise, MINOR lapis, MAJOR crimson, GRAND royal purple;
  - hanging vines with flowers.
- **Sprites** (`tools/sprites.py`, rendered with numpy shading): chrome, lapis, gold and ruby balls (a ball changes material as it climbs tiers I to IV), gold peg studs and a coin.
- **Font:** Cinzel and Cinzel Decorative (SIL OFL, bundled as subset woff2 in `assets/`).
- **Effects:**
  - motion trails, sparks off pegs, slot glow pops and value floaters;
  - tier climb: light beam, eased camera pan, light screen shake, then the new tier ignites (dark veil lifts, flash, rays);
  - omen glow on the gate or Grand slot (blue, red with rays, gold with fast rays);
  - jackpot plaque flash;
  - end-of-round celebrations, by round win:

    | Win | Celebration |
    |---|---|
    | under 3× bet | normal |
    | 3× bet or more | BIG |
    | 10× bet or more | MEGA, with coin shower |
    | any jackpot | jackpot plaque presentation, with coin shower |

    Balance and win roll up together during the celebration.
  - Hanging Gardens: vines and petals overgrow tier I;
  - ambient dust motes and sun rays on the summit.
- **Performance:** text, plates and balls are pre-rendered bitmaps, and the camera moves in whole device pixels. An adaptive quality governor steps down if frames are slow: trails, then peg sparks, then resolution 2× to 1.5×, then rays, then 1×. Dev parameters: `?q=0..5` forces a quality level, `?dpr=1.5` caps the resolution.
