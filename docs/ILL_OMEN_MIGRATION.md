# Migrating the boss's `ill_omen` onto the seam — the baseline first

P462 raised `rivalTurn` with `{actor:'o', pts:<what the player scored>}`. The
boss's copy still runs two hand-written sites. This is what has to hold true
after they move, written before anything moves.

## The two payouts, as they are today

| site | when | what happens |
|---|---|---|
| `_bustTolls` ~25681 | player **busted** | omen LANDS — boss takes `min(p[tier][0], G.pPts)` from the player |
| `endPTurn` ~26972 | player did **not** bust | omen MISSES — **player** gains `p[tier][1]` |

Both then clear `G._oIllOmen` and call `updHUD()`.

The player-side `CFX.ill_omen` already does both in one function, branching on
`ev.pts <= 0`.

## The hazard, and it is not hypothetical

**`pts === 0` is not the same set as "busted".** P462's own measurement found
seven call sites that reach `endPTurn` with `turnPts` cleared: five bust paths
**plus `steal_low_bank` and `block_low_bank`** — where the player banked
nothing but did *not* bust.

So a naive migration to `ev.pts <= 0` makes the boss's omen **land on a blocked
or stolen bank**, which today it does not. That is a behaviour change wearing a
refactor's clothing — the exact failure this migration was held back from P462
to avoid.

**Decide explicitly, do not inherit:** either the omen keeps meaning *bust*
(needs a bust marker the seam does not currently carry), or it comes to mean
*scored nothing* (a real design change, and arguably the better card — but a
change, and it should be made on purpose).

The player-side card has the same ambiguity today and resolves it as `pts<=0`,
so the two sides currently **disagree** about what the omen reads. That is worth
knowing on its own, independently of the migration.

## What the before/after has to pin

1. Player busts with the boss holding the omen → player `pPts` down by
   `min(p[0], pPts)`, boss `oPts` up by the same, capped at what the player had.
2. Player banks normally with the boss holding it → player `pPts` up by `p[1]`.
3. `G._oIllOmen` cleared in both, exactly once.
4. **The blocked/stolen-bank case**, which is where old and new can differ.

Cases 1–3 are the invariants. **Case 4 is the decision.**

## Status

**Baseline documented, migration not started.** The seam it needs is live and
verified (P462, all three checks). What is missing is not machinery — it is the
case-4 ruling, and inheriting it silently from `pts<=0` is the one option that
should not happen by default.
