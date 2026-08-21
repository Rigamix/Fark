# Raising patron aggression — measured, and inconclusive

Ruled: raise aggression. The measured problem is that **skill stops mattering
as tiers rise**, not that the game is too easy or hard — so the thing to watch
is agent spread widening back out with tier, not win rate moving.

`spread` = `max(win%) − min(win%)` across four agents. A max-minus-min over
four samples, which is inherently noisy.

## The baseline was two seeds, and that changed what counts as a result

| tier | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 |
|---|---|---|---|---|---|---|---|---|
| seed A | 60.9 | 42.7 | 42.7 | 31.4 | 30.5 | 30.5 | 35.0 | 23.6 |
| seed B | 55.0 | 45.0 | 39.1 | 28.2 | 26.8 | 34.1 | 30.0 | 28.2 |

**Per-tier noise: ±3–6.** The narrowing itself is real — a ~30-point fall dwarfs
that. But the published headline "60.9 → 23.6" is **one seed**; the other reads
"55.0 → 28.2". Direction established; magnitude not, to better than ~10 points.

## The change

`aggMin`/`aggMax` +0.06 on every tier, capped at 0.95. Uniform because nothing
measured says which rung needs it most; capped because tier 7 was already
.82–.90 and without a cap the top tiers would move a third as far as the
bottom, a shape nobody chose.

## The result: not resolvable at two seeds

| | t0 | t3 | t5 | t7 | fall t0→t7 |
|---|---|---|---|---|---|
| before (2-seed mean) | 58.0 | 29.8 | 32.3 | 25.9 | **32.1** |
| after (2-seed mean) | 56.6 | 28.2 | 25.3 | 30.7 | **25.9** |

The fall shrank by 6.2 — **but the same statistic varied by 10.5 between seeds
with no change at all.** Six of eight per-tier deltas sit inside the ±3–6 band.

**Tier 7 is the one worth noting:** 25.9 → 30.7, the largest single move and in
the intended direction. Still ~5 against a ±5 band.

Win rate barely moved (≈8–9% at high tiers either side), so the raise did not
make the game harder in win-rate terms either.

## What would settle it

Either **more seeds** — 5 or 6 per side would shrink the error on the trend
statistic enough to resolve a 6-point move — or **a larger bump**, accepting
that a bigger change is harder to walk back if the mechanism is wrong.

**The change is kept.** It is directionally consistent with the intent and
costs nothing if neutral. What is not claimed is that it worked.
