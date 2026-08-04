# Aggression, re-measured at five seeds — still not resolvable, and now we know why

Ruled: re-measure, because the baseline was known-noisy and tonight's `challenge`
fixes moved real difficulty numbers underneath it.

**Two findings. The second matters more than the first.**

## 1. Five seeds do not resolve it — the noise is wider than the effect

`tools/sim_tier_sweep.js`, five seeds, N=120 per agent per tier.
**N=120, not the original's 220** — so this is noisier by construction and the
numbers are not directly comparable to the archived table. What *is* comparable
is the seed-to-seed variation, which is the whole question.

| tier | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 |
|---|---|---|---|---|---|---|---|---|
| spread (mean of 5) | 58.7 | 41.7 | 39.7 | 30.7 | 30.8 | 32.2 | 31.8 | 30.0 |
| min across seeds | 51.7 | 36.7 | 32.5 | 25.8 | 27.5 | 24.2 | 27.5 | 25.8 |
| max across seeds | 65.8 | 45.8 | 45.8 | 34.2 | 35.8 | 38.3 | 35.0 | 33.3 |

**Fall t0→t7 = 28.7**, sitting between the archived before (32.1) and after
(25.9). The claimed improvement was 6.2. **A single tier's spread varies by
8–14 points across seeds alone.**

So the original doc's proposed fix — more seeds — **does not work at this N**.
Averaging five noisy draws still leaves a band wider than the signal. Resolving
a 6-point trend move needs higher N per seed, or a statistic less brittle than
max-minus-min over four agents. `spread` throws away three of four data points
by construction; that is why it will not settle.

## What IS robust across all five seeds

**The narrowing completes by tier 3 and then plateaus.** 58.7 → 41.7 → 39.7 →
30.7, then 30.8, 32.2, 31.8, 30.0 — flat within noise for five straight tiers.
Win rate does the same: 19.3 at t0, then 8–9.3 from t3 on.

That is a cleaner statement of the original concern than any before/after delta,
and it holds at every seed: **the ladder stops differentiating after tier 3.**
Tiers 4–7 are not harder than tier 3 for skilled or unskilled play alike.

## 2. The instrument cannot see half of what a patron does

Found while checking whether the re-measure was even meaningful.

| path | how the sim runs it | patron card effects |
|---|---|---|
| player banks | **the real `handleBank`** | **fire** — all 10 branches |
| patron banks | `F.oppTurn`, a reimplementation | **never fire** — 0 branches |

`F.oppTurn` deals `oCards` and passes them to `scoreRoll`, but contains no
`getNpcCard`, no `mechanic` dispatch, no `effect` reads. The harness's own
comment says it "reproduces its LOOP" — the loop, not the effects.

**So every tier number this sim has ever produced models a patron whose cards
punish the player but never help itself.** `flat_bonus`, `double_first_bank`,
`gain_when_ahead`, `steal_pct` on the patron's own bank — all invisible.

**This understates patron strength systematically**, and it is the instrument
that the aggression change was tuned against.

It also means tonight's two `challenge` fixes land unevenly here: P467 (player
side) **is** exercised, P466 (rival side) **is not**.

## Recommendation

**Do not tune difficulty against this sim again until `F.oppTurn` applies card
effects.** The narrowing-plateau finding survives — it is visible at every seed
and does not depend on the missing branches. The aggression delta does not, and
no number of seeds will rescue it while the instrument is missing half the
patron and the statistic discards three-quarters of each sample.
