# Phase 4 — the migration groups, measured 2026-08-03

`tools/cfx_coverage.js` (live) and `tools/cfx_bespoke.py` (static) rerun this.

## RESOLVED — the nine read by hand, and the answer is neither earlier one

**No card on the bus is duplicated.** Not one has the same behaviour in two
places. My "clean" claim was wrong and so was the retraction's framing of
`short_fuse` as drift.

**What is actually true: three cards have halves that live off the bus because
the bus has no hook for the moment they fire.**

| card | on the bus | off the bus | the missing moment |
|---|---|---|---|
| `short_fuse` | `turnStart`, `bust` | its x2, in `famCommitBonus` | **commit** — between roll and bank |
| `fools_gold_f` | `bust` (the double-fail burn) | the reroll, in `famFoolsGold` | **dead roll**, before the bust resolves |
| `ill_omen` | `canUse`, `use` (declaring it) | resolution, on the rival's turn | **rival turn** |

Each is one card doing two things at two times, with the bus reaching only one
of them. `fools_gold_f` is the clearest: *"Rolled nothing? Reroll everything.
But if the second roll fails too, the bust burns your turn AND the same amount
from your banked points."* Two moments, by design. `CFX.fools_gold_f.bust`
handles the burn; `famFoolsGold`, called from the no-scoring branch, handles the
reroll. Complementary, not duplicated.

### BUILT: the `commit` hook (P445)

First of the three seams. `famFire` gained `ev.mul()` beside `ev.add()`, and
`famCommitBonus` now fires `commit` and applies `pts*mul + add`. Four cards
moved onto it: `short_fuse`'s x2 plus `bloom`, `cultivate` and `vanguard_f` —
so **the retraction and three of the five group-2 cards closed in one patch.**

**Verified by fixture, 96 cases** — every subset of the four cards x three roll
shapes x two roll counts. Digest `300798530` before and after, zero differing
cases.

**And one claim I made about it was wrong.** The patch notes said the migration
*removes* an order dependence latent in the hand-written version. It does not.
Testing both orders against the pre-patch file — `[short_fuse,bloom]` and
`[bloom,short_fuse]`, 2300 either way — showed the old function called each card
in a **fixed written order**, held in the function body rather than the loadout,
so it was already order-independent.

The accurate claim is narrower and still justifies `ev.mul`: the dependence
would have been **introduced** by migrating onto an add-only bus, since
`famFire` iterates `G.pF` in equip order. It prevents a regression; it does not
fix a bug. Overstating it would have been the Ward mistake again — naming a
defect in code that was already correct.

### BUILT: `deadRoll` and `rivalTurn` (P446) — all three seams closed

- **`deadRoll`** — nothing scored, before the bust resolves. `fools_gold_f`
  rerolls here and can **claim** the roll, cancelling the bust.
- **`rivalTurn`** — the rival's turn resolved, with `ev.pts` as what they
  scored. `ill_omen` was declared a turn earlier on `use` and pays out here.

**`ev.claim()` is a fourth verb, not a number.** A dead roll has two outcomes —
the turn continues or it ends — and that is a decision. Encoding it as a
quantity means picking a sentinel every future claiming card has to know. Same
argument as Snare's `_lmRetire` being separate from `_lmSpend`.

**The NPC's own cards in that block are NOT migrated.** `slow_cook`,
`double_or_nothing`, `pickpocket` and `retort` resolve there via `_npcFamCard`
— the opponent-side implementation, deliberately separate until P5. `rivalTurn`
is for the *player's* cards that resolve during the rival's turn, a different
thing that happens to share a moment. Migrating them would quietly do P5's job
with none of P5's decisions.

### And the probe found a real crash in `famFire`

`ev.P` was computed as `var d=famDef(inst.id); return (d.p?…)` — **no null
guard**. `famDef` returns null for an id with no definition, and `d.p` then
throws on **every hook, not just that card's**.

It is reachable: `FAM_CARDS` lost four cards this rework. `anchor_f` and
`bookends_f` alias to `vanguard_f`, but **`insurance` and `ward` were cut
outright**, so a save still holding one crashes the whole effect bus.

Found because a fixture equipped an id with no definition — the same shape that
reaches a real player through an old save. Guarded.

**Still open:** the five tavern cards (`OPEN.md` §0), and `for_keeps` /
`tar_pit`, which need reading before anyone counts them as migratable.

**So Phase 4's blocker is not migration, it is missing seams.** Three moments
the seven hooks do not expose. And `bloom`, `cultivate` and `vanguard_f` — three
of the five cards waiting to be migrated — all live in `famCommitBonus` too, so
**`commit` alone unblocks four cards.**

### The other six resolved as already-known categories

- **`pickpocket`** — 4 sites are `_ruleActive('pickpocket',…)` and `G._tell.id`:
  the sealed-seat **table rule**, unrelated to the vagabond card. 1 is
  opponent-side.
- **`slow_cook`, `retort`, `double_or_nothing`, `encore`** — continuation lines
  of the `_npcFamCard` opponent blocks. The filter caught the first line of each
  block and not the lines below using `c`.
- **`sleight`** — UI targeting in `famRenderRow`/`famOppTap`, reading `G._oSleight`.
- **`ill_omen`'s other 4** — two UI targeting, two opponent-side.

**Reading nine sites by hand took less time than the two classifier passes that
got it wrong**, and produced a category neither of them had: *"off-bus for want
of a hook"* is not a value `CODE`/`string`/`opponent` could ever have returned.
A classifier can only sort into the buckets you thought of first.

## Superseded: CORRECTION (same day): group 1 is NOT clean

**The section below was published saying all 20 on-bus cards are clean. That is
wrong and it is retracted.** At least one card is genuinely half-on:

**`short_fuse` sits on `CFX` for `turnStart` and `bust`, and its x2 is
hardcoded in `famCommitBonus`** (line 13493, `famInst('short_fuse')`). Read by
eye, not inferred.

**Why the check missed it.** It classified any line where the id appeared inside
quotes as a log string. `famInst('short_fuse')` is quoted — and it is a lookup,
not a log. **The seventh instrument artifact of the day and the first false
NEGATIVE.** The other six invented work; this one hid it, which is worse here,
because a clean result *ends the investigation* and an invented one gets checked.

It also fits the pattern exactly as described: a number that visibly narrowed
from 18 to 1 to 0 reads as diligence — each correction looking like the process
working — and that earned trust the final answer had not separately earned.

**What is now established, all eye-verified:**

- `short_fuse` is genuinely half-on. Real.
- `_npcFamCard(...)` sites are the **opponent-side** implementation, separate by
  design — `PROTO_NOTES` has NPC usage landing in P5 with `G.oF` empty until
  then. Not drift.
- `pickpocket` in `_SEAL_POOL` is a **name collision**: the sealed-seat table
  rule and the vagabond card share a string and are unrelated. The same trap as
  Ward's shared prefix, one level down.

**What is NOT established: the final count.** After separating those two
categories, nine cards still show sites needing to be read individually. That
work is not done, and no migration has been built on any of it.

## ~~Group 1 is a no-op~~ — RETRACTED, see above

The plan says *"start where partial infrastructure exists, prove the machinery,
then take the hard cases."* Measured, the machinery is already proved:

~~**All 20 on-bus cards are genuinely on the bus.**~~ **RETRACTED.** The claim
rested on treating every quoted id as a log string; `famInst('short_fuse')` is
a lookup. At least `short_fuse` has a second implementation.

That was worth checking rather than assuming, because "has a CFX entry" and
"CFX is where its behaviour lives" are different claims, and a card that is both
on the bus and bespoke elsewhere is the worst case available — the entry makes
it look migrated, so the next change goes into `CFX` while the bespoke half
carries on doing the old thing.

**There is also no drift in the other direction:** zero `CFX` entries that match
no card.

## Group 2 is TEN cards, not nine

The plan lists nine: `bloom`, `cultivate`, `vanguard_f`, `for_keeps`, and the
five tavern cards.

| id | family | kind | live |
|---|---|---|---|
| cultivate | jade | passive | yes |
| bloom | jade | passive | yes |
| vanguard_f | vagabond | passive | yes |
| for_keeps | vagabond | active | yes |
| double_stakes | tavern | active | yes |
| the_tab | tavern | active | yes |
| hair_of_the_dog | tavern | passive | yes |
| marked_table | tavern | passive | yes |
| high_table | tavern | passive | yes |
| **tar_pit** | **amber** | **active** | **no** |

**`tar_pit` is the tenth** and the plan's list cannot see it, because the list
is of *live* cards and `tar_pit` is off `FAM_LIVE`.

This is the group-2 rationale recurring one level down. Group 2 exists because
*"a migration that enumerates the effect table structurally cannot see them"* —
and a list of group 2 that enumerates live cards cannot see `tar_pit`. The card
whose enumeration you trust is always the one that gets left behind. It needs a
`CFX` entry when it goes live, or an explicit note that it is retired.

## Hook usage, for whoever designs the next hook

| hook | consumers |
|---|---|
| canUse | 13 |
| use | 13 |
| bank | 4 |
| bust | 4 |
| turnStart | 2 |
| roll | 1 |
| bankBonus | 1 |

`roll` and `bankBonus` have **one consumer each, and it is the same card**
(`slow_cook`). A seven-hook bus where two hooks serve one card is worth knowing
before an eighth is added.

## Open question before group 2 is built

The plan flags it and it is still unanswered: **the five tavern cards may not
belong on a match-scoped bus at all — they act on the RUN.** Five of the ten are
tavern cards, so this decides half the group. It is in `OPEN.md`.

## Instrument note — six artifacts before the number was real

`cfx_bespoke.py` first reported **18 of 20 cards half-on**. The true answer is
zero. Every one of the six was caught by reading flagged lines rather than the
summary:

1. `\bpreserve\b` matches inside `preserve-3d` — a hyphen is a word boundary, so
   Preserve "had 15 bespoke sites", all of them CSS transforms.
2. Prose in `/* */` comments counted as code: one comment naming "POWDER KEG,
   ENCORE and STEADY HAND" scored three implementations.
3. The `FSIM` harness re-implements scoring **on purpose**, so it can run
   thousands of matches headless. Counting it as drift would have condemned the
   thing that measures drift.
4. `FAM_LIVE.tamper=1` — the live table is written two ways, and only the
   object-literal form was recognised.

The last one is the instructive one: it left **one** survivor out of an original
eighteen, which is exactly when a wrong finding is most believable — it looks
like a careful audit that narrowed to a single real problem.


---

# Run-scoped cards — measured before building the primitive

## The four do NOT share one lifecycle

The direction says to build a shared run-scoped primitive first, *"same
reasoning as lane markers before Snare/Snuff/Fog."* That reasoning includes the
step that mattered: measuring the candidates. Doing it here gives the Trade
result again.

| | arms it | carries | resolves |
|---|---|---|---|
| **Double Stakes** | player, in the Room | boolean | `launchSeat` |
| **For Keeps** | player, in the Room | boolean | `launchSeat` |
| **The Tab** | player (`famTabTake`) | **a quantity** (400) checked against gold | **two paths** — voluntary `famTabPay`, forced `_tabSettle` at last orders |
| **Hair of the Dog** | **an outcome, not the player** | boolean | **mid-match**, at the next first bank |

**Only two of the four share a shape** — Double Stakes and For Keeps are
player-armed booleans consumed at `launchSeat`, and they are genuinely
identical. The other two differ on a *different axis each*: The Tab carries a
quantity with two settlement paths and a night deadline; Hair of the Dog is
armed by an outcome the player did not choose and resolves inside a later match.

**A single arm/resolve primitive covering all four would have to invent a
"maybe the player armed it, maybe an outcome did" concept, and a resolve that
might be a seat boundary, a bank, or a night ending.** That is not a primitive,
it is a switch with three arms wearing one name. The honest shape is a small
one covering the two that match, and leaving the other two as what they are.

*Not built yet — this changes the scope the direction assumed, so it is a
finding to rule on rather than a decision to take unilaterally.*

## Bet Law: both fixes built and verified (P447)

Copy and mechanic, both from the direction verbatim.

- **Hair of the Dog** — *"…doubled — but bust before banking, and it costs an
  extra circle."* The automatic-on-loss trigger stays; the response is now the
  wager. `_hotdToll()` charges one circle if you bust with `_famBankCount===0`,
  and clears the flag so a second bust cannot charge twice.
- **Cursed Table** — *"…THREE circles, not two — lose, and it costs you two
  circles, not one."* Symmetric now.

**One helper, because this would have been the third copy.** The chalk board is
two structures — `S.run.points` and the parallel `S.run._chalkMeta` — and they
must move together or the board disagrees with its own history. That pairing was
already duplicated at the tab default and the cursed-seat loss. `_rubOutCircles(n)`
names it once; all three sites use it.

**Verified, 6 checks:** the helper moves both structures and floors at zero;
busting before a bank costs a circle; having banked costs nothing; unarmed costs
nothing; and it charges exactly once.

**`_hotdToll` had to be re-homed.** It first landed next to `_bustTolls` — which
is itself declared *inside* `doBust`, so the new function was invisible to
everything outside and untestable. Top level now.

## Markers (#1): the gap tracks a line, it isn't three oversights

Double Stakes, The Tab and For Keeps render an armed chip; Hair of the Dog,
Cursed Table and High Table render nothing. **That split is exactly the
"player does something" line** — the three with chips have them because they are
interactive *controls* (arm it, pay it), not because anyone built markers. So
#1 is not "add three more chips to the existing pattern"; those three have no
control to hang a chip on, which is a different build.

Worth knowing before it starts: the existing chip row is **hand-written twice**,
in `_gbRenderRoom` and `_ptRoom`, for all three cards. A marker step should
absorb that rather than add a third copy.
