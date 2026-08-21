# Sizing the keep wiring — the `total` reconciliation

The policies are built and verified (P493). This sizes the patch that makes them
actually run, because the reconciliation is the whole difficulty and guessing at
it under momentum is how §11 got created in the first place.

## What modifies `total` between the score and the keep loop

363 lines, eight assignments. They split into two kinds, and the distinction is
the entire design:

**Multiplicative / zeroing — `used` untouched:**

| line | what |
|---|---|
| 27928 | snare: `total=Math.floor(total/(_snX2?4:2))` |
| 27935 | snake oil: `total=0` |
| 27942 | Aldric's Vow: `total*=2` |
| 27957 | `total=0` |

**Fresh scorings — replace `total` *and* `used` together:**

| line | source | free list |
|---|---|---|
| 27906 | initial, fogged | `_oFree` (built earlier) |
| 27972 | encore | `_encFree` |
| 28048 | reprisal | local rebuild |
| 28244 | quick_hands | local rebuild |
| 28261 | gilded_bones | local rebuild |
| 28377 | slippery_table | `G.oppDice`, fully un-kept first |

## The design that falls out

**Choose at each of the six scoring sites, not once before the keep loop.**

Choosing late looks cheaper but is wrong: by the keep loop `total` may already
have been halved by snare or doubled by the Vow, so replacing it with the chosen
candidate's `pts` would silently discard those. Recovering them would mean
reconstructing "what was the maximal at the time" — a number nothing tracks.

Choosing immediately after each scoring keeps every downstream modifier applying
to the chosen total exactly as it applies to the maximal one today. The
multiplicative group needs no changes at all.

**All six, not the easy ones.** Wiring only the initial site would make a
persona's choice evaporate the moment any disruption card fired — the same shape
as the `slippery_table` re-keep found in the first sizing, and the same argument
that forced all seven call sites in P489. A boss whose personality switches off
because the player played a card is worse than no personality.

**At site 27906 the choice must come *after* the fog re-expansion** (P491), or
the mask is built against indices that are one short.

## The shape of the helper

```
_oppPickKeep(freeD, total, used, bank) -> {total, used}
  bust or no candidates -> unchanged
  otherwise             -> pick.pts, and a mask of pick.sel over freeD
```

`pick.sel` holds the same objects passed in, so the mask is an `indexOf`, not a
value match — no ambiguity between two dice showing the same face.

## The control this patch gets

A `hoard` or `combo` persona takes the maximal candidate, and the maximal
candidate's points equal the scorer's total — **measured, 852 bone rolls, 0
divergences**. So:

> With a maximal persona on bone dice, the wiring must change **nothing**.

That is the tier-0 arm, same as `bestMatchesMaximal` for P481 and the 923-roll
no-wild arm for P489. If it moves, the patch changed something other than the
choice and the persona delta would be unattributable.

The jade arm will **not** be zero, and should not be: 32 keep divergences remain
after P489 and they are choice, not scoring — the rival currently takes
strictly dominated keeps (400 holding five dice where 1000 holding three
exists). Closing that is the point.

## What is NOT in this patch

`combo` still holds at maximal. Its value-per-live-die is unmeasured, and the
P493 assert fails if anyone gives it a branch. Measuring it is its own pass,
after the wiring makes the other five observable.
