# The `generateOppCards` lift, measured on its own

Ruled: lift it, with a same-seed before/after so the delta is attributable to
**this** and not blended with the aggression pass or the `challenge` fix — the
third change on that axis this session, which is what `OPEN.md` §6 exists for.

**Method.** `sim_tier_sweep`, five seeds, N=120, four agents. The baseline was
taken earlier tonight on **identical game code** (`fark_proto.html` last changed
at `8afa24d`, before the baseline ran) and measured **twice with identical
results**, so it is a stable reading rather than a single sample. Only
`generateOppCards` differs between the two.

## The prediction, made before the run

Generated patrons draw cards at **0% on tier 0** (pool size 0 by design) and
**100% on tiers 1–7** (2–3 cards each). So tier 0 had to stay flat and tiers 1–7
had to move toward the patron. **A tier-0 move would have meant the measurement
was wrong**, not that the lift did something interesting.

## Result

| tier | win before | win after | Δ win | spread before | spread after |
|---|---|---|---|---|---|
| **0** | 19.3 | **19.3** | **0.0** | 58.7 | **58.7** |
| 1 | 11.8 | 11.0 | −0.8 | 41.7 | 38.2 |
| 2 | 11.2 | 7.4 | **−3.8** | 39.7 | 28.0 |
| 3 | 8.5 | 5.3 | **−3.2** | 30.7 | 20.8 |
| 4 | 9.2 | 6.1 | **−3.1** | 30.8 | 22.0 |
| 5 | 9.2 | 6.5 | −2.7 | 32.2 | 24.2 |
| 6 | 9.3 | 7.7 | −1.6 | 31.8 | 29.3 |
| 7 | 8.0 | 6.9 | −1.1 | 30.0 | 23.3 |

**Tier 0 is identical to the decimal on both metrics.** The control held.

## What can and cannot be claimed

**CAN: bosses got stronger at every tier that draws cards.** Win rate falls
0.8–3.8 points, consistently, in one direction, with the no-card tier pinned at
exactly zero change. Win rate is a mean over 4 agents × 120 matches × 5 seeds —
far more stable than `spread`.

**CANNOT: that the ladder's shape changed.** `spread` fell 2.5–11.7, which looks
dramatic and **is not resolvable by this statistic**. Per `SPREAD_AUDIT.md`,
max−min over four agents is sound for "these are equal" and for a landslide, and
**unsound for exactly this size of delta** — the measured seed-to-seed range at a
single tier was 8–14 points. A −8 move sits inside that. Reporting the spread
column as a finding would repeat the aggression pass's error with fresh numbers.

## Attribution, which was the point

This delta belongs to the lift alone. It does **not** blend with:

- the **aggression pass** — unproven, on noisy data, `OPEN.md` §6
- the **`challenge` double-charge fix** — real, boss-side, measured separately

Three changes, three separate readings. §6 can now name which is which instead
of carrying "bosses got harder tonight" as one undifferentiated entry.

## Note on magnitude

The sweep is the **night-1 control**: six bone dice, no player cards, no
enchants. Nobody plays tier 7 on that build. It measures how the ladder scales
with player power held still, so these are **not** the win rates a real run
sees — the direction and the tier-0 control are what transfer.
