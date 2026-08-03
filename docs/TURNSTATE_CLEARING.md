# Turn-state clearing — the classification, and what it settles

**Measured before choosing a shape**, because 62 sites is enough that guessing
wrong would be expensive in a way none of today's other misses were.

## The instrument was wrong first, and its biggest number was the wrong one

The first classifier attributed each site to the nearest **preceding**
`function NAME` declaration. That is not scope. `_bustTolls` is 28 lines and
contains **zero** wipes, yet 26 sites were filed under it — everything between
where it ends and the next named declaration begins. The headline it produced,
*"77% cluster into four functions"*, was an artifact.

Corrected: brace-match every `function` keyword, named or anonymous, and
attribute each site to its **innermost enclosing named** function.

## The result

**62 sites across 13 functions.**

| function | sites | what it clears |
|---|---|---|
| `doBust` | 27 | kept×7 pool×7 row×7 turnPts×6 |
| `handleBank` | 12 | kept×3 pool×3 row×3 turnPts×3 |
| `startPTurn` | 6 | kept×2 row×2 pool×1 turnPts×1 |
| `_afterRollImpl` | 4 | **kept×2 turnPts×2 — and nothing else** |
| `endPTurn` | 2 | kept×1 turnPts×1 |
| `_zeroHourClose`, `_breakDie`, `handleRoll` | 2 each | pool + row |
| `activateDoubleDown` | 1 | **pool only** |
| `endMatch`, `doFlee`, `initMatchScreen` | 1 each | **row only** |

## The falsifier, stated before the run, and what it says

> *Few functions + consistent subsets → one ordered operation. Many functions
> or varying subsets → an ordering guarantee instead, leaving the sites alone.*

**It split.**

**Consistent, and repeated:** `doBust` and `handleBank` clear all four in
balanced counts — 7/7/7/6 and 3/3/3/3. That is the same full turn-end clear
performed once per exit path: seven bust paths (ward, amber, the saves, plain)
and three bank paths, each independently doing the same four things. **63% of
all sites.** That is a real repeated operation and it is where the Preserve-class
ordering bug will recur, because every one of those paths is a place a restore
could land on the wrong side of.

**Genuinely different, and must not be merged:** `_afterRollImpl` clears `kept`
and `turnPts` and **never** `pool` or the row — mid-roll you clear the score and
keep the dice. `activateDoubleDown` clears `pool` alone. Three functions clear
the row alone. These are not the full clear with a different reason; they are
different operations that happen to touch overlapping state.

## Therefore

**Scoped consolidation, not a universal one.** An ordered turn-end operation for
the `doBust` and `handleBank` paths — where the same four-part clear is repeated
ten times — and explicitly **not** applied to the partials, whose subsets are
load-bearing.

That is a smaller and safer change than "one operation for all 62", and it is
the change the measurement supports rather than the one the phase title implies.

## Not established

**Whether each of doBust's seven paths clears all four, or different threes.**
A three-line adjacency window found only 4 co-located full clears, which means
the clears inside a path are not contiguous — so the per-path subsets need
reading path by path before the consolidation is written. That is step one of
the implementation, not an assumption it can proceed on.

## Reproduce

```bash
python tools/turnstate_sites.py
```
