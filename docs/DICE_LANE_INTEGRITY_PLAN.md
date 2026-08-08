# Dice, lane, and card positional integrity — full brief

Supersedes the original plan below. That plan's hypothesis was tested and
refuted early — lane position already uses a stable per-die id, not array
index, so no architectural rework was needed. What follows is everything
found and shipped since, by investigating the actual reported bug, plus the
full remaining scope.

---

## Shipped and verified — six patches (P510-P515)

Every one below was verified by constructing the specific state that exposes
the defect and computing what the old code would have produced on that exact
state, side by side with the fix — not by asserting correctness.

**P510 — Pickpocket.** The original report. The palm spliced `G.pool`
without lowering `numDice`. Missed by two earlier sweeps because both keyed
on `matchDice.splice` specifically; the actual site was `G.pool.splice`.

**P511 — resume exploit.** Family charges refunded on save/resume: 4 -> 2 ->
4 across a save/load cycle. Now 4 -> 2 -> 2. Also found and closed in the
same pass: the rival's hand was being re-drawn at random on resume,
savescummable until the boss drew something harmless.

**P512 — the refill (load-bearing).** `(pool.length+i) % matchDice.length`
was the actual wraparound source behind the whole class of bugs. Verified:
removed lane 2 (flint) with `numDice` stale at 6 — new die correctly took
lane 2 and came back flint. The old expression, evaluated on the identical
state, would have picked lane 5 and produced a duplicate brass with the
flint die silently gone.

**P513 — `CFX.sacrifice`, three defects in one handler.**
- Double decrement: two separate `numDice--` lines (P504 added a second
  without removing or checking for the first), so one sacrifice cost two
  lanes.
- Wrong-index splice: `indexOf(d.mat)` finds the first die of that material,
  not the one that shattered. Verified: victim was the lane-3 bone; old code
  would have spliced lane 0's *different* bone, destroying the wrong die's
  enchantment while the wrong die also vanished from the lane count.
- No relane: survivors above the removed lane never had their lane number
  decremented.
Test required deliberately committing lanes 4-5 first, forcing the sacrifice
target to be the *last* free die — sacrifice takes `free[free.length-1]`, so
with dice free in original order `indexOf` resolves correctly by luck and
the bug is invisible. A naive test would have passed against broken code.

**P514 — Preserve, two defects.**
- Wrong material captured: `k.mat` read `selDice[0].mat` — the first die of
  the *whole* keep group, not the die that actually scored. `k.vals` is not
  index-parallel with `k.dice` (different derivations — one post-icon-split,
  one from the raw commit), so the fix searches by value, not index, with
  the old scan kept as fallback for entries lacking a `dice` array (which
  `canUse` depends on). Verified: a lone 1 on lead amid a triple of 3s on
  bone/iron/flint — old code stored bone, fix stores lead.
- `numDice` recompute erasing an armed penalty: assigning
  `numDice=matchDice.length` instead of decrementing silently refunds any
  already-applied Hex. The correct pattern was already written as a comment
  on `_removeDieAt`, ~5,000 lines away, regarding Break's interaction with
  Tar Pit/Pocket Sand/Seven Dice — never applied here. Verified: six lanes,
  Hex armed — old code gave 5 (wrong, refunds Hex), decrement gives 4
  (correct).
Same adversarial requirement as P513: the scoring die had to be last in the
commit, or `k.mat` is right by coincidence.

**P515 — stale First Strike panel.** Display-only. `_firstStrikeRender` has
exactly two callers, neither per-turn, so Break/Sacrifice/steal leaves the
panel showing a loadout that no longer exists. **The first patch attempt
passed every gate and silently did nothing** — the hook was anchored inside
an `if(S.pendingMatch)` block that only runs when a saved match exists; a
fresh match never triggers it. Only driving the game and reading the actual
panel text caught it. Moved to the function's always-executed exit; re-
verified live.

---

## Two standing lessons, ruled on

**The default state hides these bugs — now proven three times running
(P513, P514, and implicitly in why P510/P512 survived earlier sweeps).**
Every real bug in this cluster required deliberately constructing the
specific adversarial arrangement — a die last in a commit order, a lane
targeted mid-list — rather than testing whatever state happened to be lying
around. A naive test passes against broken code by default in this
codebase. Treat this as the standard going forward: adversarial construction
is the required effort for verifying any lane/count-touching fix, not an
extra step reserved for suspicious cases.

**Decrement, never recompute-from-length, when an armed penalty might be
in play — three instances of the same unwritten rule (the `_removeDieAt`
comment, P513, P514).** RULED: build a shared helper encoding this, since
the lesson written down once in a comment demonstrably did not travel 5,000
lines to where it was needed twice more.

---

**P516 - `_dropLanes`.** The ruled shared helper. Encodes decrement-never-
recompute in one place, with the floor as a parameter (Whisper's Hex clamps at
3 and is a penalty, not a removal, so it does not call this). Seven sites
converted; every one was already correct, so it fixed no live bug - it gives
the rule a home instead of a comment 5,000 lines away. All four lane probes
re-run with no behaviour change.

**P517 - hot dice stops refunding per-turn penalties.** Found by the audit
`_dropLanes` made possible, not by a report - the fourth instance of the same
rule. The player's hot-dice reset assigned `numDice = matchDice.length`, so
Whisper's Hex or Pocket Sand was cancelled mid-turn by a clean sweep. Ruled by
Denis: the penalty holds for its stated duration. Fixed as a MINIMUM, not a
decrement, since hot dice must still restore a hand. Verified: Hex armed,
loadout 6, turn start 5, after hot dice 5 (was 6); no-Hex case 6 to 6.
**The rival's hot-dice reset must match and does not yet** - `left=6` is one of
the seven local writers below, so it lands with that rework.

---

## The rival-side rework — scoped, not started, bigger than expected

Found while sizing Blessed Confiscation (below). The rival's lane/dice-count
is a **local variable** (`let left=6` inside `runOppTurn`), not state on
`G` — no player-side helper can ever reach it, regardless of what gets built
above.

**Seven independent writers, six of them wrong:**

| write | source |
|---|---|
| `left=6` | literal |
| `left=7` | literal (NPC Seven Dice) |
| `left=5` | literal (jinx) |
| `left--` | snuff |
| `left--` | pickpocket tell |
| `left=6` | literal (hot dice) |
| `left=_oFullHand` | **derived — the only correct one** |

Two further sites (Leaky Cup, Pocket Sand) test `left===6` as a proxy for
"full hand" rather than deriving it — grow the rival's dice count past six
and both silently stop firing.

`_oFullHand` already does this correctly:
`(G.matchOppDice&&G.matchOppDice.length)||6` — at one of seven sites. Same
"the correct shape exists and didn't travel" problem as the decrement
lesson, in a second place.

**This is not a bug to hand-patch.** Fixing any single rival-side card that
touches dice count means touching the initializer, the hot-dice reset, both
full-hand tests, and reconciling with the Seven Dice and jinx literals. It's
a rework on the scale of the effect-system phases already completed this
session, not a P51x-sized patch.

**Blessed Confiscation is the specific card blocked on it.** Grows
`matchOppDice` to 7; `runOppTurn` opens at `left=6` regardless, so the
stolen die is never actually dealt or rolled — the card announces a theft
it mechanically doesn't use. **Design question for Denis, not a bug fix:**
should the card swap a die instead of adding a seventh? That closes the bug
without the rework, but changes what "TOOK YOUR DIE AND USES IT" means
narratively. Recommendation: swap, given the rework isn't currently
scheduled and the card is fully broken until it lands either way.

---

## Still open from the original plan's scope

- **Snuff** (temporary hold, returns after one opponent turn) — untouched.
- **Trade's material swap** — the one originally-assumed-safe exception.
  Never re-verified under the adversarial standard this cluster established;
  worth confirming rather than continuing to assume safe.
- **Hot dice reset, player side** — the rival-side hot-dice writer is now
  known-wrong (one of the seven literals above); the player-side reset was
  never separately checked against the same class of bug.
- **The entire card-slot parallel** — do card slots suffer the same
  index/count-desync class of bug that dice lanes did? Never investigated at
  all. Given how much was hiding in the dice half, this should not be
  assumed clean by default.

## Newly flagged this session, not yet investigated

**High confidence — same shape as bugs already found:**
- **Vagabond's drag-to-reorder.** Genuinely distinct from Trade — Trade
  swaps material between two fixed lanes; Vagabond directly relocates which
  lane a die occupies, live, mid-match, via player gesture rather than a
  card effect resolving. Never covered by anything in this thread.
- **`reduce_first_roll`** — removes dice from a roll, same shape as Break
  and Sacrifice, both of which had real bugs.
- **`swap_die` / `swap_best_to_3`** — this session's own earlier card audit
  explicitly separated these from Trade as different mechanisms, not
  variants of the verified-safe one.

**Lower confidence, worth checking rather than assuming:**
- Quicksilver's single-die reroll (should only touch face value, not lane —
  worth confirming given the pattern)
- Ward's armed-to-consumed transition (does "consumed" ever relocate or
  remove the die, or is it purely a flag)
- Powder Keg's full-roll reroll including kept dice (likely safe; relevant
  again if the bust-save-throw redesign from the ideas backlog ever picks a
  specific die by reference)
- For Keeps' cross-match die move (different scope — between matches, not
  mid-match — but it is literally relocating a die)

**Caveat on this whole "newly flagged" section:** built from pattern-
matching across a long conversation, not from a fresh check against the
real card list — exactly the kind of thing that's failed this session eight
or nine times when done by memory or grep instead of direct verification.
Starting point, not a substitute for the sweep below.

---

## Standing ask: systematic sweep, not another hand-built list

Before closing this thread out, do a full sweep rather than continue
checking items one at a time from a memory-built list: every consumer of
`matchDice`, `_enchArr`, `numDice`, and the lane-assignment functions,
cross-referenced against every card and enchant that touches dice, not
enumerated by recall. Add whatever it finds to this document, not to chat —
the original version of this plan lived only in conversation for several
hours and was invisible to every doc-based accounting as a result; don't
repeat that.
