# P489 — the rival scores wilds the way the player does

Ruled §11: yes, matching the player exactly, as its own measured change before
the keep wiring. Law 6 as widened: *whatever the player can do, an NPC can do —
every capability, every system, every rule.*

## The fix

`_scoreRollBest(vals, cards, locked, ctx, mats, enchs)` — `scoreRoll`, but when
a wild material is present it also scores with `_noWild` and returns **the whole
result of whichever pass scored higher**, not just its total. `used` decides
which dice the rival keeps, so it has to come from the pass that won.

Not `scoreSelection`: that returns a number, and it gates on validity (every
selected die must be used) because a *selection* must be entirely scoring dice.
A *roll's* `used` is partial by nature, and that is the point of it.

**All seven rival call sites, plus the sim.** Converting some would have made a
jade worth different amounts depending on which disruption card had fired —
worse than the bug. And `F.oppTurn` has its own `scoreRoll` call, so leaving it
would have made the harness blind to the change it was measuring.

## Control arm, and it is the load-bearing half

| | |
|---|---|
| bone rolls swept (no wild present) | **923** |
| differences from plain `scoreRoll` — total *and* `used` | **0** |

If that were non-zero the patch had changed the game everywhere rather than only
where wilds are, and the difficulty delta below would be unattributable.

## The fix arm — parity, not merely "better"

| | |
|---|---|
| jade-6 rolls | 462 |
| improved | 6 |
| **scored worse** | **0** |
| **took anything other than the better pass** | **0** |
| `23456` | rival **50 → 750**; player **750** |

`123456` went 500 → 1500. The claim is parity: the better of the two passes is
exactly what `scoreSelection` already gave the player.

## Difficulty, same seeds, with the control repeated per seed

`F.oppTurn`, n=4000 turns per arm. `_scoreRollBest` is a function declaration, so
the "before" arm reassigns it to plain `scoreRoll` **inside one run** — no stash,
no second build, and nothing else can drift between arms.

| seed | jade before → after | delta | bone control |
|---|---|---|---|
| 20260806 | 635.3 → 646.1 | +1.70% | **0** |
| 991733 | 629.4 → 641.1 | +1.86% | **0** |
| 20250214 | 632.4 → 643.0 | +1.68% | **0** |

Stable at **1.68–1.86%**, control pinned at zero on every seed.

**Stated limit:** `meanRolls` is ~1.17, so the rival banks after about one roll
in this setup — this measures per-turn scoring, not full-match dynamics. The
delta is a controlled comparison (both arms share seed, dice and state); it is
not a win-rate number, and it should not be quoted as one.

## What this does and does not unblock

`scoreSelectionBeatsScoreRoll` went **3 → 0**: the scoring asymmetry is closed.

Divergences between `_legalKeeps`' best candidate and the rival's maximal keep
went 38 → **32**, exactly the 6 rolls the fix improved. **The remaining 32 are
choice, not scoring**, and that was verified rather than assumed —
`11226` with a jade 6:

| | |
|---|---|
| rival maximal | 400, keeping all five dice |
| **player scoring the same whole roll** | **400** — parity |
| best candidate `{1,1,jade}` | **1000** |
| player scoring that subset | **1000** |

Both seats now value identical dice identically. What differs is that the rival
takes `used[]` and a player can pick the subset — and the rival's keep here is
strictly dominated: 400 keeping five dice, against 1000 keeping three and
leaving two live.

So the keep wiring will **not** be inert for wild dice, and should not be
expected to be — the wiring *is* the fix for that gap. What P489 bought is that
its delta is now attributable to **choice alone**, instead of being choice and
scoring mixed together with no way to separate them. That was the point of
"fix it first".
