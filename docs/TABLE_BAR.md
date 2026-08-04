# Does a 3-branch table clear the bar? No — and branch count was never the bar

Asked directly: given tonight's shape, does a 3-branch table earn building, or
has "no blocker" quietly become the only reason left?

**"No blocker" is the only reason left, for most of what remains.** But the line
does not fall where branch count falls.

## What actually made the tables worth building

| table | why it earned it |
|---|---|
| `WILD_LEVEL` | three arms differing **only by a number** — a lookup wearing an if-chain |
| `BANK_FX`, `BANK_TAKE`, `SCORE_DRAIN` | **the same formula written twice**, once per seat, free to drift apart silently |

Both are the same bar: **a table earns its place when it removes a copy.** Not
when it removes a branch. A branch is cheap and readable; a second copy of a
formula is what goes wrong unwatched, which is precisely what `challenge` proved
twice tonight.

## By that bar, the remainder splits — and not by size

**Clears it — the bust-path mirrors, 7 mechanics:**

| mechanic | appears in |
|---|---|
| `bust_immune_turns`, `bust_survive` | `_tryBustSave` + `step` |
| `bust_bank_half` | `doBust` + `step` |
| `gain_pts`, `punish_busts` | `_oppBustOut` + `doBust` |
| `single1_bonus`, `single5_bonus` | `scoreRoll` + `step` |

Same shape as `handleBank`/`finOpp` at smaller scale: **player function paired
with opponent function, same rule twice.** These are worth doing, and worth the
same `mirror_diff` pass first — that pass is what found the double-charge.

**Does not clear it — the single-site clusters:**
`steal_die`, `swap_die`, `reroll_scoring`, `reroll_all_kept`, `swap_best_to_3`,
`shatter_bonus`, `reckless`, `starstone_bonus`, `immune_modifiers`,
`block_activations`, `limit_activations`, `hidden_cards`, `reduce_first_roll`.

Each appears **once**. There is no second copy to diverge from. Tabulating them
moves unrelated function bodies into an object literal and adds a dispatch —
three branches becoming one lookup plus three rows is not fewer moving parts, and
the `_noWild` ordering assert is a reminder that moving code past a guard is
itself a risk. **That is ceremony, and the honest recommendation is not to.**

## So the answer

**Do the bust-path mirrors. Stop there.** The remaining 13 single-site mechanics
should stay as branches unless a *second* copy of one appears — at which point
the bar is met by the duplication, not by the count.

This is the ordering lesson one level down: the payoff was never in "how many
branches", it was in "how many copies of the same rule". Every table built
tonight removed a copy. None of the remaining single-site ones would.
