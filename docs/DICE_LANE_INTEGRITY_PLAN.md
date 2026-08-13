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

---

## The card-by-card sweep — FAM_CARDS × CFX (done)

Method: the inventory is read off the **loaded page**, not grepped —
`tools/apv_famsweep_inventory.js` walks the live `FAM_CARDS`, `CFX` and
`FAM_LIVE` objects and scans each handler's real `.toString()`. Every
behavioural claim below was then confirmed by driving a real match
(`tools/shoot.js --eval-file`), never by absence of a name.

**Reachability.** 30 cards. 29 are on FAM_LIVE; only `tar_pit` is off, and it
has no CFX handler either — dead on both sides (the rival's picker filters on
FAM_LIVE too, 12723). `anchor_f`/`bookends_f` are FAM_LIVE keys with no card
(aliases to `vanguard_f`). No CFX handler is orphaned. Seven live cards have
no handler by design: for_keeps (RSX + endMatch), double_stakes, high_table
(RSX), the_tab, hair_of_the_dog, marked_table (hardcoded at their sites).

**Handlers that touch dice: 12, not the 8 an identifier scan finds.** Four
reach the dice through a *callee* or a *consumer* and name nothing:
fools_gold_f (`famFoolsGold`, 14183), preserve (startPTurn 24553), honeytrap
and stargazer (`famApplyRollForces`, 14166).

### Six defects, each confirmed on an executed path

1. **Fair Trade swaps the material and leaves the brand on the seat** —
   `CFX.fair_trade.use` writes `G.matchDice[worst]` (12992) and never
   `G._enchArr[worst]`. Measured: lane 0 warded, jade borrowed from the stash
   with its own Tithe; the die dealt into lane 0 came back
   `{mat:'jade', ench:'ward'}`. The lender's brand never travels; the benched
   die's brand is worn by the visitor for the length of the loan.
   (`tools/apv_famsweep_ft_ench.js`)

2. **Sacrifice does not shift `G._fairTrade.lane`** — `_removeDieAt` carries
   two pieces of loan bookkeeping (19144 hand-back, 19204 `ft.lane--`);
   `CFX.sacrifice` splices matchDice/_enchArr itself (14313) and mentions
   `_fairTrade` nowhere. Measured on a loadout whose weakest seat is lane 2
   (an all-bone loadout hides this — `worst` is 0 and no target is ever
   *below* the loan): sacrifice lane 1, matchDice shifts, the loan record
   still says lane 2, and startPTurn's expiry test reads
   `matchDice[2]!=='starstone'` → it declares the borrowed die dead, banks it
   in `_ftDead`, and the player's own die never comes home.
   (`tools/apv_famsweep_sac_loan.js`)

3. **Stargazer never fires on the roll it was played for, and fires a turn
   later on the wrong dice** — `famApplyRollForces` gates on
   `G._famPeekVals.length === free.length` (14169). Playing during 'choosing'
   then rolling means committing first, so the counts always differ, and the
   miss does **not** clear the peek. Measured across a full turn boundary:
   peeked `[2,2,6,3,1]`, next roll had 4 free → no apply, still armed; banked,
   rival played, and turn 2's opening roll of `[3,3,4,3,3]` — a bust — was
   overwritten with the stale `[2,2,6,3,1]`, which scores.
   (`tools/apv_famsweep_stargazer.js`)

4. **Steady Hand's bust check runs against a captured pool** — `use()` closes
   over `free` and the tap handler scores that array (12949-12950), never
   `G.pool`. Sacrifice is the reachable remover: both are FAM_LIVE actives
   usable in 'choosing'. Measured: armed with the only scoring face on lane 5,
   sacrificed lane 5, rerolled lane 0 to a 3 — live table `[3,2,3,2,3]`, no
   scorer anywhere, **no bust fired** and the turn continued on a die that had
   already shattered. (`tools/apv_famsweep_steady_stale.js`)

5. **Powder Keg recomputes numDice from pool length** — `G.numDice=G.pool.length`
   (14263), the mirror of the pattern P516 exists to kill. Normally a no-op.
   The one window where they legitimately disagree is written on purpose:
   `_removeDieAt`'s Fair-Trade branch (19152) drops the borrowed die from the
   pool, keeps the lane and deliberately skips `_dropLanes`. Measured: after
   that branch, numDice 6 / pool 5; Powder Keg then set numDice to 5, turning
   "one die short for this roll" into a lost lane for the turn.
   (`tools/apv_famsweep_keg_numdice.js`)

6. **Preserve benches the last seat, not the preserved one** — nothing records
   which lane the preserved die came from; `_dropLanes(1)` (24571) moves the
   count and the refill's free-lane walk simply runs out of budget on the
   highest lane. Measured on six distinct materials with a Ward on lane 5:
   preserved the **iron** on lane 1, and next turn lanes 0-4 rolled while
   **lane 5 (the warded starstone) sat out** — lane 1's iron appeared twice
   (once in the tray, once freshly rolled) and the Ward could not arm.
   (`tools/apv_famsweep_preserve_lane.js`)

### Three more, confirmed by reading the loaded code

- **Sleight is inert.** `CFX.sleight.use` sets `G._famSleight` (14387) and the
  only other reference in the entire loaded corpus is its own `canUse` guard —
  measured over every global function's source plus every inline `on*`
  attribute (1.07M chars). The rival's Sleight is a *different* flag,
  `G._oSleight`, and is implemented (25184).
- **Cultivate's growth dies with the turn.** `d._cult` (14223) lives only on
  the pool die object, and `G.pool=[]` at startPTurn (24426) and
  `_turnTableClear` (23164) replaces those objects. "For the rest of the
  match. Stacks." is at most one turn, and only pays on a second fire inside
  the same turn.
- **Honeytrap reads no tier.** `pairVal` is the last value with count ≥ 2
  (14347), not a tap and not the player's pick; tier III's four-of-a-kind
  clause has no code. `famApplyRollForces` then stamps it on `free[0]` — the
  lowest-lane free die.

### Divergences worth a ruling rather than a patch

- `CFX.sacrifice` never calls `_removeDieAt`. It reimplements five of its
  responsibilities and skips three: the loan hand-back, the `ft.lane` shift
  (defect 2), and the mid-turn re-snapshot (19232-19244). Measured: after a
  live sacrifice paying +800, `S.pendingMatch` still held six matchDice and
  numDice 6 with an empty `_diceOut`, so a resume rewinds the sacrifice
  entirely — die and charge back, points lost. A Break in the same spot is
  preserved across the resume by design. Not a points exploit; an
  inconsistency. It also skips `_firstStrikeRender()` (P515).
  (`tools/apv_famsweep_sac_snapshot.js`)
- `CFX.sacrifice` filters neither `_breakPreserved` nor `_breakBorrowed`,
  both of which Break honours (19055, 19273). Brief §1 says a borrowed die is
  an illegal Break target "full stop"; Sacrifice can still shatter one.
- `CFX.transmute` is the only card whose free set is
  `G.pool.filter(d=>!d.committed)` (14241) — every other card also excludes
  `_frozen`. A held die is a legal Transmute target and an illegal Steady
  Hand / Encore / Stargazer one.
- `CFX.powder_keg` sets `G.kept=[]` (14257). On a turn a Preserve resolved,
  that discards the preserved entry startPTurn wrote at 24556 while its chip
  stays in `#keptRow` — read, not driven.

---

# THE CARD-BY-CARD SWEEP — cross-reference, all five layers (done)

The previous sweep went site-by-site: it grepped the invariant identifiers and
audited what came back. That cannot see a card whose handler never names those
identifiers — one that calls a helper, mutates a die object, or relocates a die
by gesture. This one goes **card-by-card**: start from the inventory of every
effect that can touch dice, and for each ask what it actually mutates.

**Five layers were inventoried and each independently audited by a second
pass**: FAM_CARDS×CFX, NPC_CARDS, enchants+materials, tells/handicaps/rung
rules, and gestures. Where inventory and audit disagreed the audit is taken
unless noted; every reversal is called out at its row. Everything below marked
*measured* came off an executed path in a real headless browser
(`node tools/shoot.js --url http://localhost:8084/fark_proto.html --eval-file …`).

**Standing rule applied throughout: a grep returning zero is never sufficient.**
Reachability is stated with evidence at every row, because an entire legacy
player-card layer turned out to be dead (`initMatchScreen` line 31875 —
`const pCards=[];` — measured `G.pCards === []`, `#playerCards .mcard` count 0),
and a naive sweep would have filed a dozen findings against code no player can
reach.

Six facts, abbreviated in the tables:
**MD** `G.matchDice` · **EN** `G._enchArr` · **ND** `G.numDice` ·
**PL** `G.pool` membership · **DOM** the row · **LN** `d.lane`/`_laneOf`.

---

## 1. THE CROSS-REFERENCE TABLE

### 1a. FAM_CARDS × CFX — the player's familiar cards

30 cards, 23 CFX handlers. Read off the **loaded objects**, not grepped
(`tools/apv_famsweep_inventory.js` walks live `FAM_CARDS`/`CFX`/`FAM_LIVE` and
scans each handler's real `.toString()`).

**Reachability for the whole layer:** 29 of 30 are on `FAM_LIVE`; only `tar_pit`
is off (measured `FAM_LIVE.tar_pit === false`) and it has no CFX handler either
— dead on both sides. `anchor_f`/`bookends_f` are FAM_LIVE keys with no card
(aliases → `vanguard_f`). No orphaned CFX handler. **Correction to an earlier
reading in this thread: line 14436 is an ENABLE list, not a retirement list** —
measured `Object.keys(FAM_LIVE)` = 31 ids at runtime, and the draft filter
returns `draftablePowderKeg: true`. The UI chain was verified by reading and is
reachable: chip → `onclick="famCardTap(i)"` (13084) → sheet button →
`onclick="_gbSheetClose();(function(){famUse(i);})()"` (13468).

**12 handlers touch dice, not the 8 an identifier scan finds.** Four reach dice
through a callee or a consumer and name nothing: `fools_gold_f`
(→`famFoolsGold` 14183), `preserve` (→`startPTurn` 24553), `honeytrap` and
`stargazer` (→`famApplyRollForces` 14166).

| effect | reachable | mutates | omits | verdict |
|---|---|---|---|---|
| **sacrifice** | LIVE (FAM_LIVE measured; `use` driven) | all six: `d._shattered` 14285, DOM remove 14289, `MD.splice`+`EN.splice` 14313, `_dropLanes(1)` 14314, `PL` filter 14315, relane 14319, `_diceOut` | **the floor** (nothing stops `MD` reaching length 0); `_fairTrade.lane` shift; `_breakBorrowed`/`_breakPreserved` filters; the mid-turn re-snapshot 19232-19244; `_firstStrikeRender()`; `_steadyDisarm` | **BROKEN** — five separate defects, D1/D8/D9/D14 below |
| **preserve** | LIVE (driven) | consumer-side at startPTurn 24553: `G.kept`, `_dropLanes(1)` → **ND**, appends to `#keptRow` → **DOM** | **which lane** the die came from; the die's **enchant** (`_famPreserve` keys measured: `val, mat, pts, crack` — no `ench`; the tray die is minted `mkDie(...,null,true,null)`) | **BROKEN** — D6 |
| **powder_keg** | LIVE (draftable, measured) | die objects (`committed`,`_frozen`,`sel`,`val`) 14259-60, DOM classes, `G.kept=[]` 14257, **`G.numDice=G.pool.length` 14263** | a resolve guard (no phase change, no pending flag — encore's own comment at 13019 documents the fix and it never travelled); re-deriving `free` from `G.pool` inside the timeout | **BROKEN** — D5 |
| **steady_hand** | LIVE (driven) | `d.val=_rollD(d)`, `d.sel` 12945; `.break-target`, `d.el.onclick` | its bust check re-reading `G.pool` — it scores a **captured** `free` (12949-12950) | **BROKEN** — D4 |
| **stargazer** | LIVE (driven) | `use()` reads only; `famApplyRollForces` writes `d.val` positionally 14170 | clearing `G._famPeekVals` on a miss, and at the turn boundary | **BROKEN** — D7 |
| **honeytrap** | LIVE (driven) | `free[0].val` 14174 | clearing `G._famHoneyVal` at the turn boundary (measured surviving: `afterTurnBoundary.famHoneyVal = 4`); reading `inst.tier`; not clobbering the Stargazer peek | **BROKEN** — D7 (same defect class) |
| **fair_trade** | LIVE (driven) | **MD only** — `G.matchDice[worst]=inv[best]` 12992 | **EN** (the lender's brand never travels); a per-die identity (`_ftDead` and the loan record both store a *material* string) | **BROKEN** — D10 |
| **fools_gold_f** | LIVE (driven) | via `famFoolsGold` 14183: `d.val=_rollD(d)` for all free 14188, DOM face, onclick rebind | — | **CORRECT** — calls `_steadyDisarm` (14191); no lane/count/array contact |
| **transmute** | LIVE (driven) | `d.val` 14247 + face repaint | excludes `_frozen` from its free set (`G.pool.filter(d=>!d.committed)` 14241) — the only card that does | **CORRECT** on the six facts; the `_frozen` divergence is a ruling, D18 |
| **cultivate** | LIVE (driven) | `d._cult` 14223, on the pool die object | nothing — but nothing persists it either | **CORRECT** mechanically, **card text false** — D16 |
| **encore** | LIVE (driven) | `d.val=_rollD(d)`, `d.sel` 13031; classes, onclick; `turnRollCount`, `phase` | — | **CORRECT** — the only reroll card with a resolve guard (`G._encorePending`, `phase='rolling'`, 13019) and it calls `_steadyDisarm` 13038 |
| **sleight** | LIVE (draftable) | `G._famSleight` 14387 — nothing reads it | the entire advertised effect | **BROKEN (inert)** — D17 |
| **for_keeps** | LIVE (RSX 13253) | run-scoped only: win → `famFkTake` 13603 pushes `S.run.diceInv`; loss → 30238-30251 splices `S.run.dice`+`dieEnch` together | nothing G-side | **CORRECT** — see §3 for the brand-value asymmetry |
| bloom · slow_cook · retort · reprisal · double_or_nothing · short_fuse · ill_omen · falling_star · pickpocket(fam) · tamper · vanguard_f · double_stakes · the_tab · hair_of_the_dog · marked_table · high_table | LIVE | points, multipliers, gold, targets, opponent card instances — **no dice contact on any of the six facts** | — | **CORRECT** (16 cards) |
| tar_pit | **DEAD** (`FAM_LIVE.tar_pit === false`, measured; no CFX handler) | — | — | DEAD PATH |

### 1b. NPC_CARDS — the rival's cards

**Reachability for the whole layer:** NPC cards reach a match only through
`generateOppCards` (32361), whose three callers are 34075 gauntlet, 35695
patron, 35740 boss. **Patron matches deal zero NPC cards** — `pCardCount=0`
(11643) → `cardPool:[]` (11682) → `generateOppCards` returns at 32368. NPC
cards exist only in the **8 boss matches** and gauntlet rematches.
`S.npcWonCards` has **no writer anywhere in the file**, so the "cards the NPC
seized" branch at 32372 can never add anything.

| effect | reachable | mutates | omits | verdict |
|---|---|---|---|---|
| **`bust_survive`** (one_more_round) | LIVE — Grog's pool | `clearRow('oppDiceRow')` → **wipes `G._oppHeld`** at 23180; `G.oppDice=[]`; `step()` 28432 | resetting `left`, which still counts only the *unheld* dice | **BROKEN** — D2. Reverses the first inventory's "verified safe" |
| **`bust_immune_turns`** (hold_the_line, sundays_rest) | LIVE and **guaranteed** — `hold_the_line` is Brutus's `cardPool[0]` (10884) and 32384-32388 force-substitutes `cardPool[0]`; no random gate | reaches the same 28432 line | same | **BROKEN** — D2, and this is the carrier that fires in *every* Brutus match |
| **`brutus_grit`** | LIVE | same shape at 28368 | same | **BROKEN** — D2, third carrier; named by neither inventory |
| **`reroll_all_kept`** (crown_authority, blessed_dice) | LIVE — measured firing at Whisper, `usedOnce:{crown_authority:1}` | `k.dice[].val` 25510, **`k.vals=k.dice.map(...)` 25511**, `k.pts`, `G.turnPts` | that `k.vals` (post-`_splitIcons`) and `k.dice` (pre-split, 24926) are **not index-parallel** — P514 already established this; and `_enchRollM`, which every other reroll uses | **BROKEN** — D3 |
| **`swap_die`** best_for_worst (sticky_fingers_die) | LIVE — Finnick's `cardPool[0]`, so guaranteed | `G.matchDice[pBestIdx]` ↔ `G.matchOppDice[oWorstIdx]` 24620 | **EN** — and the comment directly above at 24618 says *"a swap, not a splice - lanes and brands stay aligned"*, which is false for brands | **BROKEN** — D11 |
| **`swap_die`** downgrade_best (collateral_die) | LIVE — Corvus | `G.matchDice[pBestIdx2]='bone'` 24634, twice | **EN**; and it defeats `_tradeRestore`'s material test *and* its `cnt` fallback | **BROKEN** — D11 |
| **`steal_die`** take_best (royal_seizure) | LIVE — Whisper | `MD.splice`, `_dropLanes(1)`, `EN.splice` 24670-24672, `_diceOut` | pool relane, `_fairTrade.lane` shift, mid-turn re-snapshot — **all three no-ops only because of where the block sits** (startPTurn empties `G.pool` at 24426, expires the loan at 24450-24469, and ends with `saveMatchState()` at 24692) | **CORRECT in place.** Move this block anywhere else and all three become live bugs. The `_tradeSwaps` ledger is match-long and therefore *not* protected by position |
| **`steal_die`** take_and_use (blessed_confiscation) | LIVE — Ambrose | as above **+ `G.matchOppDice.push` 24682** | that the rival's count is a local `let left=6` (27870) and its seats come from `_freeSeats[i]` for `i<rollDice` | **BROKEN** — D13. Seat 6 is *unconditionally* unreachable: the only two producers of `rollDice===7` (`left=7` at 27939, Seven Dice; `left=_oFullHand` at 28839, Double Down) are both dead — measured `npcHasActive_seven_dice:false`, `npcHasActive_double_down:false` |
| **`reduce_first_roll`** (mabels_pinch) | LIVE — Mabel's pool 10842. (`pocket_sand`: **NEVER DEALT** — in no cardPool, and `npcWonCards` has no writer) | `G.numDice=Math.min(G.numDice,5)` 24804 | decrementing rather than clamping | **BROKEN** — D15 |
| **`swap_best_to_3`** (grogs_bump, quick_hands) | LIVE — `quick_hands` is Finnick's `cardPool[0]`, guaranteed | `d.val` on live pool dice only 25451-25472 | nothing it should do | **CORRECT** — driven at Grog: pool `0:bone:1 … 5:starstone:1` → `0:bone:3 1:iron:3 2:lead:1 …`; lanes, materials, MD, ND all unchanged. Victims are picked by object, not index. (Minor: the non-D3 branch at 25469-25472 never sets `el._trueVal`) |
| `bust_bank_half`, `mabels_stitch`(npc), `second_wind`(npc) | LIVE | points only | — | **CORRECT** on the six facts; `bust_bank_half` and `mabels_stitch` end the turn rather than re-stepping, so they do not carry D2 |
| `sleight_of_hand` (29343), `whispers_hex` npc-armed (29328→24531), `blockade` (25105), `seven_dice` (27939) | **DEAD** — all gated on `G.oCards.includes(...)` with ids that appear in **no** boss `cardPool`; measured `npcActiveUses:{blessed_confiscation:1,blessed_dice:1}` in a real Ambrose match | `sleight_of_hand` would write `G.matchDice[pBestIdx]`/`G.matchOppDice[oBestIdx]` with no EN handling — D11's exact shape | EN | DEAD PATH (would be BROKEN if fed) |
| `honor_guard` (29025), `standard_bearer` (29031) | **DEAD** — gated on `G.oCards.includes` with legacy ids, measured `false` in a live Ambrose match | — | — | DEAD PATH |

### 1c. Enchants and die materials

**Reachability:** `ENCH_GRID` (33421) lists all eight and every entry resolves
through `_enchDef` — verified live. `_iconFaces` (33378-33386) restricts brands
to faces 1 and 5 and every material carries both.

| effect | reachable | mutates | omits | verdict |
|---|---|---|---|---|
| **break** | LIVE | removes a die via `_breakBegin` 19054 → `_breakDie` 19259 → `_removeDieAt`: MD, EN, ND (`_dropLanes(1)` 19185), PL, DOM, relane | — | **CORRECT.** Floor holds — measured `_breakBegin(lastDie) === false` at one die. Honours `_breakBorrowed` (19040) and `_breakPreserved` (19055) |
| **trade** | LIVE | `matchDice[L]` ↔ `matchOppDice[L]` 18407-18455, `_enchArr[L]=null`, the `_tradeSwaps` ledger with `cnt`, `_tradePaint` 18495 (`replaceChild`, so layout position and `dataset.seat` survive) | shifting `_tradeSwaps[].lane` when a player-side removal splices below it — recovers via the `cnt` fallback 18578-18581, measured `restored:1` | **CORRECT.** Adversarially re-verified: middle lane, brand on the neighbour above, `_enchArr[4]` untouched, `d.lane` and lane count unchanged, `S.run.dice` never saw the visitor. Closes the brief's standing "Trade never re-verified" item |
| **quicksilver** | LIVE | `d.val`, `d.sel` (19550-19558) | — | **CORRECT.** Lane/material/ench map measured byte-identical before and after |
| **ward** (the enchant) | LIVE | `G._wardArmed` 18337, `G._wardBoost` 18342; consumed at 26173-26183 (points only: `G.pPts += _half`), expired at 24434 | — | **CORRECT.** Armed→consumed is purely a flag plus a points computation — **no die is relocated or removed on either transition.** The source itself distinguishes the two systems at 18328-18329 |
| **snare** | LIVE | `_lmArm('_snare', c.lane, …)` 18357; consumed at 28219 against `_oFree[i].lane`, halving a number | — | **CORRECT** — no player-side mutation |
| **fog** | LIVE | splices `_fogV`/`_fogM`, which are `.slice()` copies (28172-28180) | — | **CORRECT** — real arrays untouched |
| **snuff** | LIVE | rival-side only: `left--` (28003) + the `_freeSeats` skip (28060) | keeping `left` and `_freeSeats` in agreement across a hot-dice reset | **BROKEN in combination** — D1. Snuff itself is correct; `left=6` at 28827 is what breaks it |
| **tithe** | LIVE | gold | — | **CORRECT** |
| **`shatter_bonus`** (obsidian, grogs_tooth) | LIVE | the sweep at 25272-25284 stamps `_shatterLane`, sorts **descending** and removes through `_removeDieAt` | a floor on `MD.length`; and the `else` branch at 25284 splices `PL` alone | **MOSTLY CORRECT.** Adversarially verified across four arrangements (middle lane with a brand above; two non-adjacent shatters with brands between and above; last lane; under an armed penalty) — all clean, with a working `chance:0` negative control. **One real hole:** if some shattered dice have lanes and one does not, `_shLanes` is non-empty so the `else` never runs and the laneless shattered die **stays in `G.pool` as a live scorer with its element deleted** — measured, `poolShattered:1`, lanes `[0,1,undefined,3,4]`, and its seat is never refilled because `needNew` is 0 |
| **`drag_reorder`** (vagabond) | LIVE — acquisition confirmed: `DICE_STORE` carries `{mat:'vagabond',price:700,stock:2}` at 10948, `_shopRollNight` 10958-10961 offers it 45%/night with a pity rule, and the drop handler at 33251 → `_stTrade` 33279 is a live pointer handler (driven: `_stTrade('vagabond',3)` → `dice[3]='vagabond'`, `dieEnch[3]=null`, gold −700) | `G.pool` order 36673, DOM order 36680-36683, mesh `phys.x` 36663 | `d.lane`, MD, EN, ND — **and `d.hx`**, the cached chip layout centre | **BROKEN** — D12 (tap desync) plus a ruling (D19, seat≠lane) |
| `palm_adjacent` (14129) · `fang` (14133, 26164) · `weight_bank` (27406) | LIVE | read positions / membership only | — | **CORRECT.** All three are implemented **by material id, never by mechanic string** — a grep on the mechanic would have been a false clear |
| `triple_bonus` · `wild_quad` · `wild_straight` · `wild_triple` · `single1_bonus` · `starstone_bonus` · `reckless` | LIVE | scoring only | — | **CORRECT.** `reckless` walks `G.matchDice` as bare ids (26465-26467), so it correctly stops charging for a shattered brass and correctly starts charging if Trade parks a rival brass in your loadout |
| `brutus_shield` | LIVE | carries no `effect`; works through `bornEnch:{t:'ward',face:5}` (12252) stamped by `_enchInit` 19463-19477 | — | **CORRECT** — the only material that *creates* an enchant |

### 1d. Tells, handicaps and rung rules

**Reachability:** `_SEAL_POOL` (11234) is live — measured a sealed seat giving
`G._sealRule='zero_hour'` with the badge rendered and `_ruleActive` true on both
sides. Sleeve is live (boss spoils 13634 → `famSleeveSet` → `_gbBossPeek`, wired
to `#ptBossName`/`#ptBossGo` at 16208/16260).
**All five handicaps are unreachable** — sole writer is
`var handicap=null;` at 35679; measured `G._handicap === null` in a live match.
**Every `rung._flag` rule and every player-card table rule is dead** — all gated
on `G.pCards`, measured `[]`.

| effect | reachable | mutates | omits | verdict |
|---|---|---|---|---|
| **rival hot dice** `left=6` 28827 | LIVE | resets the rival's dice count to a literal | that `_freeSeats` was built from `_rungAll.length` minus held minus **`_snuffLane`**, and `_snuffLane` (set once at 27998) is never cleared for the rest of the turn | **BROKEN** — D1 |
| `pickpocket` tell | LIVE | player: `G.pool.splice` + `_dropLanes(1)` (P510, correct). rival: `left--` 28016 | the callee `_maybeFireCutpurse` re-asks `G._tell.id` (11505) instead of `_ruleActive` | **BROKEN** — D20 |
| `zero_hour` | LIVE | `G.pool=[]` at the end of `_zeroHourClose` 18702 | — | **CORRECT** — the turn is ending and startPTurn re-derives from `matchDice.length` at 24426 |
| `drill_order` | LIVE | roll cap only | derivation on the rival side — 23541 derives via `_tellById`, 28011 is a literal `oppRollNum>=3`, 13114 a third copy | **CORRECT today** (measured `_tellById('drill_order').maxRolls === 3`), **latent divergence** — D22 |
| `last_call` · `reckoning` | LIVE | bank total / bank floor | — | **CORRECT** |
| `first_strike` | LIVE | renders MD/`matchOppDice` 18820 | being called on the NPC swap/steal route (24604-24689) and by `CFX.sacrifice` | **BROKEN (display)** — D21. `_firstStrikeRender` has four callers (17519, 18801, 19251, 24426); the block at 24604 runs *after* the startPTurn call and splices inline |
| `still_waters` | LIVE as a boss badge | pure predicate `_famHushed` 18869 | — | **CORRECT** mechanically; **cannot be sealed** — `_SEAL_POOL` substitutes the parked `steeped` for it, measured `sealPoolMissing: ["still_waters"]`. D23 |
| `kindred` | LIVE | `mult=2`, extending Snuff/Fog to two rival turns 18466/18479 | — | **CORRECT** — but it doubles the number of turns exposed to D1 |
| `steeped` | **PARKED** — on no boss; `S.run.tells` has exactly one writer (13634, boss spoils) and `tellGive` (11309) has no callers, so it can never be sleeved. Only route in is a sealed seat | player pays `G._tell.perRoll` 25201 (reads `G._tell`, not the rule); rival pays a hardcoded `100` 28859 | — | LATENT divergence — measured `wouldAdd === 50` against `PARKED_TELLS.steeped.perRoll === 100` |
| `_oTarPit` (24417-24419) / `_famTarPit` (27847) | **DEAD** — no writer; `FAM_LIVE.tar_pit === false` measured | 24418 `Math.min(numDice,5)` sits **nine lines above** the unconditional reset at 24426 and is wiped by it (measured: armed, `startPTurn()`, `numDice` came back **6** with the charge spent and the log reading "YOU ROLL 5"); 27847 writes `G.numDice` — the **player's** counter — inside `runOppTurn` | — | DEAD PATH, but both blocks would ship as-is on a re-enable. The control in the same probe: Whisper's Hex at 24531 does the identical operation *below* the reset and correctly returned 5 |
| `rung.chaotic` / `adaptive` / `minBank` / `diceStop` / `wager*` / `_highTable` | LIVE | AI aggression, banking thresholds, target — no dice | — | **CORRECT** |
| all 5 handicaps; `_jinx` (`left=5` 27966); `_sawdust`; `_shortPour`; `_coldShoulder`; `leaky_cup`; player-side `blockade`; `whispers_veil`; `iron_grip` | **DEAD** — `G._handicap === null` / `G.pCards === []`, both measured | — | — | DEAD PATH. Two consequences worth recording: the feat **`last_man_sitting`** (9813) is unearnable, and **`iron_grip` — the only counter to Pickpocket and the die-steal cards — is permanently false** (11790 records it as removed) |
| `mirror_match` dice swap | **DEAD** twice over | writer 35703-35708 and reader 32071-32077 have their field names inverted and the two inversions **cancel** — measured `playerChanged:false, oppChanged:false` | — | DEAD PATH. `_removeDieAt`'s comment at 19090-19094 records a live exception for it; that exception cannot fire |

### 1e. Gestures and cross-match die moves

| effect | reachable | mutates | omits | verdict |
|---|---|---|---|---|
| **Vagabond drag** `_commitVagabondDrag` 36651 | **LIVE** — die acquisition confirmed (§1c) | `G.pool` order, DOM order, mesh `phys.x` | `d.hx` (the cached chip layout centre, invalidated only on a row change at 22030 and in the no-physics branch at 22080); and `d.lane`/MD/EN/ND | **BROKEN** — D12; plus D19, a ruling |
| **`_stTrade`** (shop stall trade rack, 33279) | LIVE — driven | `S.run.dice[slot]` 33287, `_enchInit()`, `S.run.dieEnch[slot]=null` 33288 | — | **CORRECT** — the reference implementation for the brand-moves-with-the-die rule |
| **tier loadout drag** `_startLoadoutDieDrag` drop 34917-34919 | **DEAD (CSS)** — `#tierWrap` computes `display:none`; two independent `!important` rules kill it (1851 `#screen-gauntlet>*:not(#gbRoom)`, 1993 `.tier-loadout`); measured 6 `.tier-lo-die` present, **0 visible**. Handlers *do* attach — `_attachLoadoutDieDrag` executed 18× | swaps `S.run.dice[srcIdx]` ↔ `[tgtIdx]` | `S.run.dieEnch` entirely | **BROKEN, DEAD PATH.** Driven with the surface forced visible: `dice [bone,silver,…,obsidian,…] → [bone,obsidian,…,silver,…]`, `ench` unchanged — both brands now on the wrong die, and `_enchInit`'s illegal-face scrub is one-shot behind `if(S.run._enchV!==3)` (19369), so it neither repairs nor refunds |
| **dice-store drag** `_buyDieAtSlot` 33942 | **DEAD** — both hosts of `#dsGrid`/`#dsLoadout` (`_legacyInitShopScreen` 33737, `_showInlineDiceSection` 33757) have **zero call sites** by execution counter; measured on the live shop screen: `.ds-slot` count 0, `.dice-store-item` count 0 | `S.run.dice[slotIdx]=mat` 33954 | `S.run.dieEnch[slotIdx]` | **BROKEN, DEAD PATH** — L1's defect on a second surface |
| **For Keeps**, both directions | LIVE (RSX 13253) | win: `famFkTake` 13603-13620 pushes to `S.run.diceInv` then `_enchInit()` pads `dieEnchInv` and stamps born brands 19450-19476. loss: 30238-30251 splices `S.run.dice[di]` **and** `S.run.dieEnch[di]` together, refills `'bone'` at the end, pads to match | nothing structural | **CORRECT** — arrays stay parallel in both directions. See §3 for the brand-value asymmetry, which is a design question |
| `famDieShift` 14864 (the *correct* reorder — swaps `dieEnch` alongside `dice`) · `famDieEquip` 14880 · `famDieStash` | **DEAD** — measured **zero call sites** across every global function's `.toString()`, every inline `on*` attribute and the document HTML (3.1M chars scanned; `famDieShift` occurrence count 1 = its own definition). `famLoadoutShow()` renders 21,033 visible chars with none of the three in the output; its dice carry `onclick="_loFocus(this)"` (14612), inspect-only | `famDieEquip` would push a **branded bone** to `diceInv` with its enchant and no refund, victim picked by `lastIndexOf('bone')` 14885 | — | DEAD PATH. **There is no reachable loadout *reordering* in the build** — `_stTrade` is the only reachable way a die changes seat-content, and it is correct |
| `activateAlchemistsChisel` 31633 · `activateRoyalSeizurePlayer` 31531 · `activateBlessedConfiscationPlayer` 31541 · `activateStickyFingersPlayer` 31503 · `activateCollateralPlayer` 31516 · `activateDoubleDown` 31364 · `activateSevenDice` · `activateMabelsStitch` 31021 · `activateCoinFlip` 31589 · `activateTheNudge` 31611 | **DEAD** — `activateCard` has one caller, `_commitActivation` 23070, reachable only from an `.mcard` in `#playerCards`, fed by `buildCBar('playerCards',G.pCards,…)` 32150 with `const pCards=[]` 31875. Measured: `activateCard` executed **0** times across menu → gauntlet → shop → loadout; `canActivateCard('blessed_confiscation') === false`. The machinery is alive and only the feed is empty — calling `buildCBar('playerCards',['gamblers_eye'],…)` directly produced 1 mcard, 1 mcard-active | see §4 | — | DEAD PATH (10 sites). Catalogued in §4 because they are the inheritance if `params.pCards` is ever honoured |

### 1f. The engine sites the cards route through

| site | reachable | mutates | omits | verdict |
|---|---|---|---|---|
| `_removeDieAt` 19115 | LIVE | MD, EN, `_dropLanes(1)` 19185, PL, DOM, relane 19187, `_fairTrade.lane` 19204, re-snapshot 19232-19244, `_firstStrikeRender` 19251, `_diceOut` | a floor on `MD.length`; `_steadyDisarm`; shifting `_tradeSwaps[].lane` (recovers by the `cnt` heuristic); its `lane<0` guard **admits NaN** (19117) | **MOSTLY CORRECT** — the reference remover. The NaN admission is load-bearing for D8 |
| the refill 25118-25156 (P512) | LIVE | mints pool entries on free lanes ascending, DOM append, `G.pool=[...G.pool,...newEntries]` | a guard on `G.matchDice.length === 0`, where the overflow fallback `(G.pool.length+i)%G.matchDice.length` at 25130 evaluates `0%0` → **NaN** | **BROKEN in one arrangement** — D8 |
| player hot dice 24980 (P517) | LIVE | `numDice = Math.min(matchDice.length, numDice)` | — | **CORRECT** — closes the brief's "hot dice reset, player side" open item. But see D5: P517 turned Powder Keg's stale write into a live penalty that the old recompute used to mask |
| `_dropLanes` 19107 | LIVE | `numDice` only, floored at 1 | any floor on `MD` | **CORRECT** — seven sites converted, all verified |
| `startPTurn` 24426 `G.numDice=G.matchDice.length` | LIVE | the per-turn baseline | — | **CORRECT** — it is a recompute, but at the one moment no penalty is armed. Everything added *above* line 24426 is silently wiped (D24 hazard; `_oTarPit` is the existing casualty) |
| `handleBank` 27228 + 27427, `endPTurn` 27560: `G.numDice=6` | LIVE | hands a five-lane player six | deriving from `matchDice.length` | **CORRECT by accident.** Nothing reads `numDice` before the next `startPTurn` — but `saveMatchState()` (24692) snapshots the 6 to disk, so it is one accident deep, not zero. **Measured incidentally** in `tools/apv_xref_sac_empty.js`: a one-die loadout busted and came back `numDice: 6` against `matchDice.length: 1` |
| rival `left=6` initializer 27870 | LIVE | the rival's dice count | `_oFullHand` | **CORRECT today, LATENT.** All `RUNGS` and all generated patron loadouts are exactly 6 (measured `rungsDiceLens`/`rosterDiceLens` all 6; `generateDiceLoadout` hard-loops `i<6`) and the only live shrink path is on the player's MD |
| `_oFullHand` 28839 | LIVE (dead feature) | `(G.matchOppDice&&G.matchOppDice.length)||6` | — | **CORRECT** — the one derived rival-side write, at one of ten sites |
| the sim harness 36979 | LIVE (offline) | `var dice6=(rung.dice&&rung.dice.length===6?rung.dice:['bone'×6])` | — | **CORRECT but blinding.** A rival loadout that is not exactly six (Blessed Confiscation's push) is silently replaced with six bones before any balance number is computed off it |

---

## 2. CONFIRMED DEFECTS, ranked by player-visible impact

Only defects that survived the adversarial audit. Each carries the exact code
and the arrangement that exposes it.

### D1 — The rival's hot-dice reset is a literal `6`; under Snuff it deals a duplicate lane and refuses to empty the snuffed seat, for **every remaining roll of the turn**

> **CLOSED — P521, driven. D2 is NOT closed; see below.**
>
> `_oSeats(ignoreHeld)` is now the single source for the rival's free seats.
> The deal count is taken **from** that list (`Math.min(rollDice, seats.length)`)
> rather than computed alongside it, the `:i` index guess is deleted, and the
> hot-dice reset reads the hand size instead of the literal `6`.
>
> | arm | seats dealt, every roll of the turn |
> |---|---|
> | snuff on lane 2 | `[0,1,3,4,5]` — was `[0,1,3,4,5,5]` from roll 2 onward |
> | no snuff | `[0,1,2,3,4,5]` |
>
> Zero duplicate seats, zero material mismatches, no over-count, in both arms.
> The probe refuses a verdict unless the snuff provably fired — its first run
> reported "the snuffed seat was dealt" when the snuff had simply **never
> armed**: `runOppTurn` increments `G.oppTurnCount` at 28036, *before*
> `_lmDue('_snuff')` tests `turn===oppTurnCount`, so arming with the current
> count guarantees a miss. A red from an un-armed hook is the same class of
> worthless as a green from one.
>
> **D2 REMAINS OPEN, and the root-cause framing needs a correction.** The sweep
> called D1 and D2 duals of one cause. Half of that holds: both are the count
> and the seats disagreeing. But P521 only makes the two agree — it does not fix
> *what they agree on*. D2's mechanism is a separate write:
> `clearRow('oppDiceRow')` wipes `G._oppHeld` at 23227, and several mid-turn
> paths call it and then re-enter `step()` — **28457, 28521, 28935**. The seats
> are then re-derived from an empty held record, so the rival re-rolls dice it
> is still sitting on. `_oSeats()` reads that record faithfully; the record is
> what is wrong.
>
> Which of those call sites should preserve the held dice and which are
> legitimate whole-hand re-deals (28935 is Double Down, which explicitly rerolls
> everything) is not yet established, and is the next discrete piece rather than
> something to guess at now.

`fark_proto.html:28827`
```js
if(left===0){G._oLastHotDice=true;G._oppSweep=true;left=6;setTimeout(step,_oppDelay(1500));return;}
```
The seats are computed independently, 28059-28068:
```js
if(_heldSeats[_fs])continue;
if(_fs===_snuffLane)continue;      // the snuffed seat is removed from _freeSeats
const _seat=(_freeSeats[i]!==undefined)?_freeSeats[i]:i;   // ← the fallback
```
`_snuffLane` is set once at 27998 and **never cleared for the rest of the turn**,
so after the sweep `_freeSeats.length===5` while `left===6`. `i=5` misses,
falls back to `_seat=i`, and lands on a seat that is either already dealt
(duplicate) or the snuffed one (penalty cancelled).

**Reproduced twice by two independent authors.** Rival loadout
`['bone','iron','flint','lead','amber','jade']`, Snuff on lane 2:

| | seats | materials |
|---|---|---|
| roll 1 | `[0,1,3,4,5]` | bone, iron, lead, amber, jade — flint correctly withheld |
| roll 2 onward | `[0,1,3,4,5,5]` | bone, iron, lead, amber, jade, **jade** |

DOM confirms (`#oppDiceRow` seats `["0","1","3","4","5","5"]`). Snuff on the
**last** lane instead: roll 1 `[0,1,2,3,4]`, roll 2 `[0,1,2,3,4,5]` **including
the snuffed die** — the enchant is simply undone mid-turn. Control, no snuff:
`[0,1,2,3,4,5]` on all 51 rolls, clean.

**Not a one-roll artefact** — measured 14 consecutive corrupted rolls in one
turn, because `_snuffLane` is never reassigned inside `step()`. Kindred (18466)
doubles the number of *turns* affected, not the severity.

**Why the default state hides it:** it needs a snuffed seat *and* the rival
sweeping its whole hand in one turn. With no snuff, `_freeSeats.length===6===left`
and the fallback never fires. It also needs a rival whose materials differ, or
the duplicate is invisible.

**This is the lesson P517 already wrote down, on the other side of the table**
(24980: *"hot dice restores your hand, it does not GROW it"*). Fix shape:
`left=_freeSeats.length`, and give the `_seat` fallback a hard `break` rather
than an index guess. `_freeSeats` is `var`-scoped inside `step()`, so 28827 does
see the current invocation's copy.

### D2 — Every rival bust-save wipes the held-dice record and then re-rolls the seats the rival is still sitting on

> **CLOSED — P524, driven. Decided per site, as ruled.**
>
> Eleven callers of `clearRow('oppDiceRow')`; only three re-enter the deal loop.
>
> | site | what it is | call |
> |---|---|---|
> | 28500 | Brutus's Grit | **fixed** |
> | 28564 | the bust-save cascade | **fixed** |
> | 28978 | Double Down | **left alone** — rerolling everything is the card |
>
> The rest run `finOpp` and end the turn, where clearing is correct.
>
> **How the two were decided rather than guessed:** Grit's own comment claimed it
> "mirrors player `_runSave`". `_runSave` does
> `G.pool=G.pool.filter(d=>d.committed)` and says *"the save preserves the
> tray"* — the player keeps every committed die and re-rolls only what busted.
> The rival cleared the whole row. **The mirror claim was false**, which makes it
> the third wrong claim found in this source in one session, after P517's and
> P523's.
>
> **The fix is to stop bypassing the function that already did it right.**
> `_oppHoldKept` — which `step()` calls first — keeps the kept dice, removes only
> the busted ones, and empties `G.oppDice`. Both sites cleared the row *before*
> handing back, so it never got the chance to run. Same shape as P519: the
> canonical path existed and two call sites went around it.
>
> Not a bare deletion: `clearRow` was also removing `#oppTotal` and the
> `.oppTag`s, and `_renderOppTags` only runs when a roll **scores** — so on a
> bust nothing else clears them. The helper clears exactly that furniture and
> nothing else. Saving and restoring `G._oppHeld` around the clear was rejected:
> `clearRow` also removes the held dice's DOM elements, so the record would
> survive while the dice vanished — state and display disagreeing, which is the
> class of defect this whole cluster keeps finding.
>
> **Driven:** 237 samples across two live Grit saves, checking continuously that
> a seat in `G._oppHeld` never also appears in `G.oppDice`. Zero collisions. The
> probe injects a fake overlap at the end and requires the checker to catch it,
> so the zero is not the instrument being blind.

Three carriers, two lines. `fark_proto.html:28432` (`bust_survive` **and**
`bust_immune_turns`) and `:28368` (`brutus_grit`), both:
```js
setTimeout(function(){clearRow('oppDiceRow');G.oppDice=[];step();},_oppDelay(900));return;
```
and `clearRow`, `fark_proto.html:23180`:
```js
/* the held dice ARE row children - the wipe above already took them */
if(typeof G!=='undefined'&&G)G._oppHeld=[];
```
`left` is **not** reassigned between the deal and the bust branch — confirmed by
enumerating every `left` writer in `runOppTurn` (27870, 27939, 27966, 27969,
27971, 28003, 28016, 28824, 28827, 28839; 28824 is in the scoring branch, after
the bust branch returns). So at bust time `left` still counts only the *unheld*
dice, while `_freeSeats` has just been rebuilt from an empty `_heldSeats` as
`[0..5]`. `_freeSeats[i]` for `i<left` takes the **lowest** seats — exactly the
ones the rival is holding. Materials come from the seat (`_rungAll[_seat]`,
28069), so the rival re-rolls the wrong dice.

**Measured** (Grog, `one_more_round`, `matchOppDice=[bone,iron,lead,amber,jade,starstone]`):

| roll | seats stamped | materials asked for |
|---|---|---|
| 1 | 0,1,2,3,4,5 | bone,iron,lead,amber,jade,starstone |
| 2 | 2,3,4,5 | lead,amber,jade,starstone |
| **3 (after the save)** | **0,1,2,3** | **bone,iron,lead,amber** ← should be lead,amber,jade,starstone |

**The default state hides it exactly as predicted:** bust on roll 1 and
`_oppHeld` is already empty, so the wipe is a no-op and the seats come out right
by coincidence. It needs a bust on roll 2+ with dice held.

**`bust_immune_turns` is the carrier that matters most.** It has no random gate
(`G.npcCardState.oppTurnCount<=(eff.turns||2)`), and `hold_the_line` is Brutus's
`cardPool[0]` (10884), which 32384-32388 force-substitutes — so it is in **every
Brutus match**, firing on the rival's first two turns. `sundays_rest` (3 turns)
is 4-of-6 in Whisper's pool.

**This reverses a "verified safe" entry.** The first inventory cleared it on the
stated grounds that *"`left` and `G._oppHeld` are left intact"*, and separately
recorded *"`G._oppHeld` … has no assignment site outside `newG` (23180)"*. Line
23180 is inside **`clearRow`**, not `newG` (which closes well before
`_turnScoreClear` at 23163). The misattributed line number is what hid the bug
directly underneath the entry that cleared it.

Note the **hot-dice case is genuinely clean** and for a real reason, not by
luck: there all six dice were kept, so wiping `_oppHeld` and resetting `left=6`
agree. Measured `heldLanes:[]` after every sweep. D1 and D2 are duals of one
root cause — see §5.

### D3 — `reroll_all_kept` rescores from a non-parallel array; a punishment card becomes a 4× buff and folds an unbankable face into the score

> **CLOSED — P557, reproduced on the current build first.**
>
> 40 trials through the real dispatch: 9 ended with a die on its brand face and
> **all 9 folded it in** — `vals [1,1], icons [1], pts 200` on a group that went
> in at 50. The write-up's 4× reproduced independently a third time.
>
> **Two changes.** `k.vals` and the mats now come from `_splitIcons(k.dice).rest`
> after the roll — re-split rather than remembered, because that is also the
> correct rule: a branded die that rerolls OFF its face stops being an icon and
> should score, one that lands back on it should not. And `rollFace(dd.mat)` →
> `_rollD(dd)`, the brand-aware roller; the group records `ench`, so **the
> write-up's "the brand cannot survive the reroll" is stale** — only the roller
> was ignoring it.
>
> **The stale reachability comment is corrected in place.** The P509 block ended
> "those bosses can draw a card only the player can activate". False: the
> after-roll dispatch runs straight off `G.oCards` with no `type:'active'` gate.
>
> **Counted, not spot-fixed.** The other reroll site (`_playerRerollKeptArmed`,
> player-fired at the rival) works on `G.oppDice` — a flat array with `.kept`
> flags and no vals/dice pair — so it cannot have this bug. Its own
> "reroll means wipe" question stays OPEN §8.
>
> **The probe that found it passed green against the broken build first**, and
> that is worth carrying: its pool showed `[2,3]`, which busts, so
> `_afterRollImpl` returned at the bust path long before the NPC block and the
> kept group was never touched — an untouched group is trivially parallel. The
> tell was `sawIcon 40/40` when flint shows face 1 one time in six. It now gates
> the verdict on the block incrementing its own use counter, and requires
> `sawIcon` strictly between 0 and the trial count.

`fark_proto.html:25510-25511`
```js
k.dice.forEach(function(dd){ try{ dd.val=rollFace(dd.mat); }catch(e){} });
k.vals=k.dice.map(function(dd){ return dd.val; });
```
`k.vals` is `selVals`, derived from `_scoreDice` **post-`_splitIcons`**
(24824-24825). `k.dice` is `selDice`, **pre-split** (24926). P514 already
established these are not index-parallel — icon dice are in one and not the
other.

**Reproduced independently by two authors.** Whisper + `crown_authority`, tithe
brand face 1 on lane 5 flint:
```
roll:   0:bone:5 1:iron:5 2:lead:5 3:amber:5 4:jade:5 5:flint:1:tithe  (isIcon[5]=true)
keep:   vals:[5]  dice:[{5,bone},{1,flint}]  pts:50
after:  vals:[1,1] dice:[{1,bone},{1,flint}] pts:200  turnPts:200
```
A branded face that banks zero **by law** is folded back into the score, and a
card whose whole purpose is to punish becomes a 4×. `rollFace(dd.mat)` at 25510
also bypasses `_enchRollM`, the brand roll table every other reroll in the file
uses, and because 24926 records only `{val,mat}` the brand cannot survive the
reroll even if it lands on its own face.

**Reachability, and it closes an open source comment.** The comment at 11737
says *"STILL OPEN: both ids remain in boss cardPools (ambrose, whisper), so
those bosses can draw a card only the player can activate."* False — the
dispatch at 25488 fires straight off `G.oCards` with no `type:'active'` or
`npcActiveUses` gate. **Measured at Whisper: `usedOnce:{crown_authority:1}` —
the boss fired it.** `blessed_dice` is 5-of-6 in Ambrose's pool.

### D4 — Steady Hand's bust check runs against a captured pool; the turn continues on a die that has already shattered

`fark_proto.html:12949-12950` — `use()` closes over `free` and the tap handler
scores that array, never `G.pool`:
```js
var fv=free.map(function(x){return x.val;}),fm=free.map(function(x){return x.mat;});
if(!anyScoring(fv,effectiveCards(),fm,free)){if(!_tryBustSave(free))_delayedDoBust(free);return;}
```
Sacrifice is the reachable remover — both are FAM_LIVE actives usable in
`'choosing'`, and Sacrifice's `use` splices `G.pool` (14315) without telling any
armed card.

**The first inventory's evidence for this was wrong and the audit re-drove it.**
The original probe built `[3,2,3,2,3,1]` and asserted the survivors `[3,2,3,2,3]`
were non-scoring using a predicate that only knew about 1s and 5s — blind to
triples. Measured: `[3,2,3,2,3]` totals 300, `anyScoring` **true**. The live
table had a scorer, the two arrays never disagreed, and "no bust fired" was
correct behaviour. `ghostWasTheOnlyScorer:true` in that probe was a hardcoded
literal, not a measurement.

**Re-driven with survivors `[2,3,4,2,3]` (`anyScoring:false`, measured) and the
only scorer a 1 on lane 5:**
```
steadyCanUse true / sacCanUse true / phaseAtSac "choosing"   <- both through their real canUse
steadyStillArmed true                                        <- sacrifice never calls _steadyDisarm
poolAfterSac lanes [0,1,2,3,4]  numDice 5  matchDice 5
afterTap liveVals [2,3,4,2,3]  phase "choosing"  busted false  bustSaved false  charges 2
```
Mechanism precisely: `_steadyDisarm` (12908) has five callers — encore 13038,
fool's gold 14191, powder keg 14267, the quicksilver-shaped reroll 24767,
handleRoll 25055. **`CFX.sacrifice` and `_removeDieAt` are the two dice-removers
missing from that set.**

The lesson is not "add two more callers": see §5.

### D5 — Powder Keg, three defects, one of which P517 made live

> **D5(a) FIXED — P518, shipped and verified.** The report was right and the
> regression was mine. Driven end to end (`tools/probe_keg_p517_seam.js`) rather
> than inferred from the two halves, because the sweep said plainly the join had
> never been driven:
>
> | arm | turn start | roll-only window | after keg | at hot-dice reset | short |
> |---|---|---|---|---|---|
> | mismatch + keg | 6 | 6/5 | 6/5 | **6** | 0 |
> | mismatch only | 6 | 6/5 | — | 6 | 0 |
> | keg only | 6 | — | 6/6 | 6 | 0 |
>
> Before P518 the first arm read **5 at the reset against a 6-lane loadout**.
> The fix is `Math.max((G.numDice||0),G.pool.length)` — a max mirroring P517's
> min, for the same reason: a transient must never overwrite an authoritative
> count downward. Deleting the write was the alternative and was rejected;
> if anything ever puts a die in the pool without raising `numDice`, that write
> is what corrects it.
>
> **P517's comment was also wrong and is replaced.** It claimed "the loadout
> term stays so a stale-low numDice cannot strand them below their real lane
> count". The loadout term is the ceiling of a `min` and cannot floor anything.
> A comment vouching for a safety property the code does not have is worse than
> none — it is the same shape as a correct-looking number beside a wrong value.
>
> **Three instrument faults were caught inside this one verification**, each of
> which had already produced a green:
> 1. sampling `numDice` a second after the sweep read whatever the NEXT roll did
>    to it — a bust toll takes a die and lands as a phantom short-by-one. Now
>    latched at the instant the branch sets its flag.
> 2. "short" measured against the **loadout** counted a rival dice penalty as a
>    defect. The denominator is what the player had at the start of *this turn*.
> 3. an arm named "mismatch" whose `_removeDieAt` took the **normal** path had
>    decremented legally; scoring it as a lost lane reported `_dropLanes` doing
>    its job as a bug. Arms now prove they built the state they claim to test.
>
> **Flagged, not claimed:** across runs, the same `_removeDieAt(2)` call with
> `G._fairTrade` armed on lane 2 sometimes took the Fair-Trade branch (numDice
> untouched) and sometimes the normal one (numDice decremented). The branch
> clears `G._fairTrade` and writes `matchDice[lane]` *before* its `return true`,
> inside a `try` whose `catch` swallows, so a throw after those writes would
> fall through and apply both paths. Not driven, not confirmed — an observation
> from arm variance that deserves its own probe.

**(a) `G.numDice=G.pool.length` (14263)** — the mirror image of the pattern P516
exists to kill. Normally a no-op because the refill tops the pool up to
`numDice`. The one window where they legitimately disagree is written on
purpose, `_removeDieAt` 19150-19152:
```js
/* it is off the table for this roll like any destroyed die, but the lane
   it stood in keeps its number, so no other lane shifts */
G.pool=(G.pool||[]).filter(function(q){return q.lane!==lane;});
```
No `_dropLanes` — by design; the player is meant to stay at six, one die short
for this roll only. Measured after that branch: `numDice 6 / pool 5`; Powder Keg
then set `numDice` **5**, turning "one die short for this roll" into a lost lane
for the turn.

**Provenance, stated plainly:** the Fair-Trade branch is reachable and was
driven independently (loan armed mid-turn, borrowed obsidian shattered → `pool
lanes [0,1,3,4,5]`, `md[2]` back to `'bone'`, `numDice 6`, `_ftDead:['obsidian']`,
then the seat refilled mid-turn), and the keg's effect on a `numDice 6 / pool 5`
state was driven separately (`tools/apv_famsweep_keg_numdice.js`). **The join —
a real Fair-Trade shatter followed by a real keg — was never driven by anyone.**
Both halves are measured; the seam is not.

**And P517 made this worse.** P517's `Math.min` at 24980 is only correct if
every mid-turn `numDice` writer leaves a meaningful value. Powder Keg leaves a
stale 5 against a 6-lane loadout, so a later hot dice computes `Math.min(6,5)=5`
and the player stays one lane short for the rest of the turn. Pre-P517 that case
resolved to 6 correctly. **P517 converted a dormant stale write into a live
penalty**, at the one moment a player is most likely to reach for a keg.

**(b) No resolve guard.** `CFX.encore` (13019) sets `G._encorePending=true` and
`phase='rolling'` before its 500 ms check, with a comment naming the exact bug
("doBust ran twice, famFire('bust') twice, two of the player's eight turns
burned in one go"). `CFX.powder_keg.use` (14253-14278) changes no phase and sets
no pending flag. Measured inside its window: `window.phase "choosing"`,
`kegCanUseAgain true`, `sacCanUse true`, `transmuteCanUse true`,
`steadyCanUse true`. Tier II/III have 2 charges, so a second Powder Keg queues a
second `_delayedDoBust` against the same dice. **This is the encore bug,
unfixed, in the sibling card.**

**(c) The same stale-`free` bust hole as D4.** `var free=G.pool.slice()` (14268)
scored at +500 ms while removers stay legal. Measured: keg rerolls to
`[2,3,4,2,3,1]`, sacrifice takes lane 5 mid-window, live table `[2,3,4,2,3]`
(`anyScoring:false`), **`busted:false, bustSaved:false`, phase `'choosing'`**.
The correct shape already exists at **24765**, which re-derives `free2` from
`G.pool` *inside* the timeout.

**Not a defect, checked:** `G.kept=[]` (14257) does not leak points.
`refreshSelUI` recomputes `const locked=G.kept.reduce(...)` (25836) and
`G.turnPts=locked+…`, measured `turnPtsAfterKeg 0` from a seeded `kept` of 100.
The Preserve chip left standing in `#keptRow` is unmeasured — §4.

### D6 — Preserve benches the wrong seat, and drops the brand

> **(b) CLOSED — P559. (a) STILL OPEN, deliberately — see below.**
>
> Driven through `CFX.preserve.use`, same test data both sides:
>
> | | record keys | `ench` |
> |---|---|---|
> | before | `crack, mat, pts, val` | absent |
> | after | `crack, **ench**, mat, pts, val` | `{t:'tithe',face:5}` |
>
> with `preserveActuallyFired` and `materialSurvives` true on both sides — the
> gate, and P514's own fix as the control.
>
> Three touches on one identity: the capture takes `_pd.ench`, the restored kept
> group carries it into `dice[0]`, and `mkDie`'s fifth argument stops being a
> hardcoded `null`. Nothing needed in the snapshot — `famState` deep-clones
> `_famPreserve` whole.
>
> **The shape is the lesson.** P514 added `mat` to this capture and did not add
> `ench` beside it, though the two travel together everywhere else: the kept
> group's own dice entries are `{val,mat,ench}` — which is where `_pd` comes
> from — and `_removeDieAt`'s `_diceOut` record is `{lane,mat,ench}`. One
> capture was written with half the identity.
>
> **The probe's first test data was wrong and reported the landed fix as
> missing.** It branded face 1 on a die showing 1, which makes it an ICON —
> `_keptScorers` filters on `!_dieIsIcon(dd)`, so it was excluded, `_pd` came
> back undefined and the scan fell through to the legacy vals-only branch that
> has no die to read a brand from. A die on its brand face scores nothing and is
> correctly not a preserve candidate; **the case D6(b) is about is a brand on a
> face the die is NOT showing.**
>
> **(a) IS NOT FIXED, and it is not a small addition.** It needs the preserved
> LANE recorded, then *maintained across removals* — `_removeDieAt` shifts every
> lane above the one it takes, which is the same problem `_fairTrade.lane` has
> and solves with an explicit `if(ft.lane>lane)ft.lane--`. And the exclusion has
> to reach the refill's ascending free-lane walk, which runs on the **first
> roll**, not in `startPTurn` where the restore happens. A lane recorded and not
> honoured in both places is worse than none.
>
> Two candidate approaches, neither costed: carry `G._famPreserve.lane` through
> to `_freeLanes` and subtract it; or push the preserved die into `G.pool` as a
> committed entry at its lane, so `_occNow`, `needNew` and `_freeLanes` all
> account for it through machinery that already exists — but that trades
> `_dropLanes(1)`'s explicit "pay for the preserve" for an implicit one, and
> `numDice` is read widely enough that the swap needs its own measurement.

**(a) Wrong seat.** Nothing records the lane the preserved die came from;
`_dropLanes(1)` (24571) moves only the count, and the refill's free-lane walk
(25121-25124) iterates `i<needNew` over ascending free lanes, so the budget
simply runs out on the **highest** lane. Measured on
`['bone','iron','flint','lead','jade','starstone']` with a Ward on lane 5,
preserving the **iron on lane 1**:
```
turn2: numDice 5, lanes dealt [0,1,2,3,4], lane 5 (warded starstone) sat out
```
Lane 1's iron appears **twice** that turn — once in the tray, once freshly
rolled — and the Ward cannot arm.

**(b) The brand is destroyed.** P514 fixed the material capture (verified:
`record.mat === 'iron'`) but nothing captures the enchant. Measured —
`G._famPreserve` keys after preserving a `{val:1, mat:'starstone', ench:{t:'tithe'}}`
die: `val, mat, pts, crack`, `mat='starstone'`, **`ench=undefined`**. The restore
at 24556-24557 builds `dice:[{val,mat}]` and mints the tray die with
`mkDie(_fp.val,_fp.mat,null,true,null)` — enchant argument literally `null`.

### D7 — The roll-forces buffer is never cleared, so Stargazer and Honeytrap fire a turn late, on the wrong dice, and clobber each other

> **CLOSED — P556 / P556b, reproduced on the current build before the fix.**
>
> Re-derived rather than implemented as written, because the entry predates
> several patches. All three mechanisms still held:
>
> | arm | before | after |
> |---|---|---|
> | peek missed by one committed die | stayed armed `[4,2,3,6,4]` | `null` |
> | peek across `endPTurn` | unchanged | `null` |
> | honeytrap across `endPTurn` | `4`, with `keptAfter 0` | `null` |
>
> Arm three is the one that settles the design question: honeytrap's text ties
> it to a **kept pair** ("tap a kept pair… guaranteed triple"), and banking
> destroys the pair — so surviving a bank meant forcing a face to match
> something that no longer existed.
>
> **Two scopes, neither subsuming the other**, both through one
> `_clearRollForces()`: spent by the roll it was armed for (else roll 3 of the
> same turn takes a peek armed on roll 1), and dead at turn end (else the next
> turn's opening roll takes one that was banked on).
>
> Cleared at `endPTurn` as well as `startPTurn` **on purpose**. `startPTurn`
> alone was already sufficient in the live sequence — nothing applies the
> buffer during the rival's turn because `_afterRollImpl` gates on
> `phase!=='opp'` — which is safety by another function's guard rather than by
> this one's decision. One edit to that gate and a peek armed in your turn
> lands on the rival's roll.
>
> **The clobber is left as it is and is now measured rather than incidental**
> (`apv_roll_forces_scope` arm D): honeytrap runs second and takes lane 0 even
> when the peek just set it. Its promise is the stronger one, so it winning is
> the defensible reading.
>
> **NOT closed by this: the peek is rolled at USE time** over the dice free
> *then*, and applied to whatever is free at the next roll. Even at equal
> counts the composition can differ and `_rollD` is material-biased, so index
> `i` can be a different die. Delivering Stargazer's actual text needs a
> preview-and-decide flow that does not exist. Flagged, not invented.

`famApplyRollForces` gates on `G._famPeekVals.length === free.length` (14169).
Playing Stargazer during `'choosing'` then rolling means committing at least one
die first, so the counts usually differ — **and the miss does not clear the
peek.** Measured across a real turn boundary:
```
roll1 free 5 → peek stored [2,2,6,3,1]
roll2 free 4 → peekLen 5 ≠ 4 → applied:false, peekLeftArmed:true
bank, rival plays
turn2 roll1 free 5 → applied:true   valsBefore [3,3,4,3,3] → valsAfter [2,2,6,3,1]
```
`[3,3,4,3,3]` is a bust; the stale peek contains a 1 and silently rescues it.
`G._famPeekVals` measured surviving the real `startPTurn` (`famPeekVals: 6`).

**Corrected from the first inventory:** *"the counts always differ"* is false.
Equal counts pass and apply — measured `peekLen 6 === freeLen 6`, applied,
`peekClearedAfterApply true`, indices 1-5 exactly the peeked values. The
reachable equal-count case is **hot dice**: peek on roll 1 with nothing
committed, commit all six, the rebuilt pool is six free again. The practical
point (usually misses, never clears) stands; the absolute does not.

**Honeytrap has the identical staleness.** `G._famHoneyVal` is written 14349,
read 14173, cleared 14175, nowhere else. Measured across the real `startPTurn`:
`afterTurnBoundary.famHoneyVal = 4`. Play Honeytrap, bank without rolling, and
next turn's opening roll has `free[0]` forced.

**And the two clobber each other.** Both write inside `famApplyRollForces`;
honeytrap runs second and overwrites `free[0].val`. Measured: peek
`[1,6,5,2,5,2]` applied, then honeytrap stamped lane 0 → `[5,6,5,2,5,2]`.

Adjacent, confirmed by reading: Honeytrap **reads no tier**. `pairVal` is the
highest paired face (14347 — `Object.keys` over integer-like keys iterates
ascending, so "highest", not "arbitrary"); tier III's four-of-a-kind clause has
no code, and `use(inst)` never reads `inst.tier`. Tiers differ only in charges.

### D8 — Sacrifice has no floor; below it the refill mints a `lane: NaN` die that nothing can remove, and the match becomes unwinnable

> **CLOSED — P519, shipped and verified. D9 and D14 closed with it.**
> Ruled first by Denis, on the ground that the failure mode is silence.
>
> `_removeDieAt` is now the only way a die leaves the table. Four changes:
> a non-finite guard (`lane<0` cannot reject NaN), a floor of one lane
> (the floor Break always had), Sacrifice routed through it instead of
> hand-rolling its own splice, and a refill that will not stamp a lane
> that is not a real index.
>
> Driven, five arms:
>
> | arm | result |
> |---|---|
> | last die, every route | remove refused, sacrifice not offered, forcing it returns false, matchDice holds at 1, **zero non-finite lanes** |
> | ordinary sacrifice | md 6→5 and numDice 6→5 **at the call** — the card still works |
> | D9, loan lane | held at 1 when a die above went, shifted to 0 when one below went |
> | D9, loan ban | loan on lane 5 excluded from targets `[0,1,2,3,4]` |
> | D14, snapshot | live 6→5, snapshot 6→5, followed |
>
> **Two of those arms first reported FAIL, and both were the probe.** Arm 2
> sampled after a sleep and read the *next turn's* state as the sacrifice's
> effect. Arm 4 captured the target list before the call and compared it against
> a lane number the removal's relane had already shifted — the relane doing its
> job is what made a working ban look broken. Both now sample at the call.
>
> **One loose end, recorded rather than dropped:** the first arm-2 run showed
> `matchDice 5` with `numDice 6` after a turn boundary, where `startPTurn`
> should have set 5. Not reproduced in the immediate-sample runs and not caused
> by P519. It wants its own probe — what writes `numDice` at a turn boundary
> when the loadout has shrunk mid-turn.
>
> **A borrowed die is no longer a legal sacrifice target,** and that is a
> judgement, flagged as one. Routing through `_removeDieAt` sends a loaned die
> to the Fair-Trade branch, which returns early and costs no lane — so paying
> points for one would be points for free. The brief already answered this
> question for Break by banning the target rather than pricing it, after
> measuring the price at nothing. Sacrifice now follows the same rule.

**This is the most severe defect in the sweep and it was single-sourced, so it
was re-driven here on an independent arrangement**
(`tools/apv_xref_sac_empty.js`).

`_dropLanes` floors `numDice` at 1 (19112). Nothing floors `matchDice.length`.
`_breakBegin` (19055) requires a live target other than the committed source, so
Break floors at one die. `CFX.sacrifice.canUse` (14281) has no such test:
```js
canUse:function(){return G&&(G.phase==='choosing'||G.phase==='idle')&&
  G.pool.filter(function(d){return !d.committed&&!d._shattered;}).length>0;},
```

Measured, six lanes walked down to one through the shipped `_removeDieAt`, then
one Sacrifice charge:
```
walkDown  md ['bone','iron','flint','lead','amber'] nd 5  →  … → md ['bone'] nd 1
breakRefusesLastDie   true                      ← Break's floor holds
sacCanUse true / sacUsed true
afterSac  md [] mdLen 0  numDice 1  enchLen 0  phase 'choosing'
```
`matchDice` is now length 0 while `numDice` is 1. The roll control is a **div**,
not a button — `fark_proto.html:8930`:
```html
<div class="match-btn match-btn-roll" id="btnRoll" onclick="handleRoll()">
```
so the `disabled` class is cosmetic and cannot block a tap (measured
`rollBtnTag:"DIV"`, `rollBtnClass:"match-btn match-btn-roll disabled"`,
`rollBtnVisible:true`). Tapping the real element: `needNew = 1 − 0 = 1`,
`_freeLanes` is empty (its loop bound is `G.matchDice.length` = 0), and the
overflow fallback at **25130** evaluates `(0+0)%0`:
```
afterEmptyRoll  poolLanesAreNaN [true]  poolMats ['bone']  poolVals [5]
                numDice 1  domDice 1
```
A real, rolled, scoring die on `lane: NaN`, material `'bone'` from
`G.matchDice[NaN]||'bone'`.

**It cannot be repaired.** `_removeDieAt`'s guard at 19117 is `lane<0`, and
`NaN<0` is false, so it accepts the call; `lane<G.matchDice.length` is false so
there is no `_diceOut` record and no splice; and `G.pool.filter(q=>q.lane!==lane)`
**keeps** the die because `NaN!==NaN` is true. Measured:
```
removeNaN  returned:true  poolLenAfter:1  mdLenAfter:0  stillInPool:true
```
`_occLane[NaN]` blocks nothing and `_freeLanes` only walks
`0..matchDice.length-1`, so no refill will ever restore a real lane.

**The match is over but does not end.** Measured through the following turns:
`startPTurn` re-derives `numDice = matchDice.length` = **0**; every subsequent
roll deals zero dice, the turn instantly busts, and play cycles
`idle → rolling → opp → idle` forever. *Not* a hard soft-lock — I sampled at
1.5 s and saw phase `'rolling'`, waited 9 s and it had resolved to `'idle'` with
the roll button re-enabled. **The player is dealt zero dice for the rest of the
match and can only lose.**

**Reachability of the arrangement:** one Sacrifice charge plus a loadout already
down to one die. The earlier reading — *"only the passive shatter can empty
`matchDice`"*, needing 3,000 g of Obsidian at two-a-night shop stock — is
refuted; Break, obsidian shatter, Royal Seizure and Blessed Confiscation all
walk the loadout down, and Sacrifice takes the last step.

### D9 — Sacrifice does not shift `G._fairTrade.lane`, and the result is an exploit, not a loss

> **CLOSED — P519.** Sacrifice routes through `_removeDieAt`, which shifts `G._fairTrade.lane`. Driven: loan held at 1 when a die above went, shifted to 0 when one below went.

`_removeDieAt` carries two pieces of loan bookkeeping — the hand-back at 19144
and `if(ft.lane>lane)ft.lane--` at 19204, written because *"a seat destroyed
BELOW a live loan shifts it down, or that same expiry check reads the wrong
lane"*. `CFX.sacrifice` splices MD/EN itself (14313) and mentions `_fairTrade`
nowhere.

**Why the default hides it:** on an all-bone loadout `worst` is lane 0, so every
sacrifice target is *above* the loan and `ft.lane>lane` is never true. Measured
on `['jade','jade','bone','jade','jade','jade']` (loan at lane 2), sacrificing
lane 1:
```
before: matchDice ['jade','jade','starstone','jade','jade','jade']  ft.lane 2
after : matchDice ['jade','starstone','jade','jade','jade']         ft.lane 2  ← unmoved
```

**The first inventory framed this as a loss ("the player's own bone die never
comes home"). Driven through the *real* `startPTurn` it is an exploit:**
```
after sac        matchDice ['jade','starstone','jade','jade','jade']  ftLane 2
after startPTurn matchDice UNCHANGED  fairTrade null  ftDead ['starstone']  diceInv ['starstone']
```
`CFX.fair_trade.use` only fires when `dieRank(inv[best]) > dieRank(matchDice[worst])`,
so **the retained die is always better than the seat it took**. Borrow the best
stash die, sacrifice any lane below the loan, keep the upgrade for the match —
and the stash die is never spliced out of `diceInv`, only match-flagged. `_enchArr`
follows the splice, so the visitor also keeps wearing the host's brand at its new
index.

(Method note for the record: the original probe **reimplemented** startPTurn's
expiry test at its own lines 86-92 rather than running it. The conclusion
survived only because 24452-24455 happens to be identical. The real function has
now been driven.)

### D10 — Fair Trade: the brand never travels, and `_ftDead` retires dice by material string

> **(a) CLOSED — P569, and with it OPEN §9 is shipped at every site.** Fair
> Trade is a **loan**, so it needed a ledger like Trade's `myEn` rather than
> `_dieLeftSeat`'s one-line clear. Driven through the real handler:
>
> | | before | after |
> |---|---|---|
> | `matchDice[0]` | `bone` → `starstone` | same *(control)* |
> | **brand during the loan** | **`ward`** — the host's, worn by the visitor | **`tithe`** — the lender's, arrived with their die |
> | loan record | `{lane, was, borrowed}` | `+ invIdx, hostEn, lentEn` |
> | brand after expiry | `ward` | `ward` — but now a *return*, not a no-op |
> | lane 5, untouched *(control)* | `seal` | `seal` |
>
> **The expiry key passes pre-fix, for the wrong reason** — the ward never left
> the seat, so "it came home" and "it never moved" are indistinguishable at that
> instant. The probe therefore carries a separate key reading the seat at *both*
> moments, which can only be true if the brand actually travelled and returned.
>
> **(b) is half closed, and had to be.** The loan record stored `borrowed` as a
> **material string**, so it could not name *which* jade was lent — and without
> that there is no way to look up its brand. `_pick` now carries the stash
> index. Checked rather than assumed: the picked die is unchanged, because
> `filter` preserves order and both old and new take the first maximum with a
> strict `>`. **What remains of (b)** is `_ftDead` holding materials, so one dead
> die still retires every die of that material — the index now exists to fix it
> properly.
>
> **Deliberately not covered:** the died-on-loan branch, whose own comment
> already says *"DO NOT touch the lane — whatever holds it now is not ours to
> overwrite"*. The same argument covers the brand. Narrow residue: a borrowed
> die that dies in its seat with nothing re-branding the lane leaves the lender's
> brand behind. Recorded rather than papered over — the honest test needs
> identity the post-resume record cannot carry.

**(a)** `CFX.fair_trade.use` writes `G.matchDice[worst]=inv[best]` (12992) and
never `G._enchArr[worst]`. **Independently reproduced twice.** Lane 2 bone with
its own Ward, starstone lent from a stash where it carries a Tithe:
`dieDealtIntoTheLoanSeat {mat:'starstone', ench:'ward'}`. The lender's Tithe
never travels; the benched die's brand is worn by the visitor for the length of
the loan. `S.run.dieEnchInv` exists, so the claim is not vacuous.

**(b)** `canUse`/`use` filter the stash with `(G._ftDead||[]).indexOf(_d)<0`
(12972, 12980) over `S.run.diceInv`, which holds **materials**. Measured with
`diceInv ['jade','jade']`, `dieEnchInv [{t:'tithe'},null]`, `_ftDead ['jade']` →
`canUse false`, live count 0. **One dead die retires every die of that
material** — the same materials-as-identity shape as P513's `indexOf(d.mat)`.
The loan record `{lane,was,borrowed}` also stores a material, so it cannot name
*which* jade was lent.

### D11 — `swap_die` leaves the brand on the seat, and over a traded lane it conjures a die from nothing

> **CLOSED — P564, reproduced on the current build first, then matched
> before/after with only the guilty lanes moving.** Denis's OPEN §9 ruling: the
> brand **travels with the die**, matching Trade. Shipped as one batch across
> all five bodies plus Trade (P566), through a single helper `_dieLeftSeat` —
> grep that name for the complete census.
>
> | | before | after |
> |---|---|---|
> | Sticky Fingers, lane 0 jade + tithe | `bone` + **tithe** | `bone` + — |
> | Collateral, lanes 0–1 jade/starstone | both `bone`, **both brands kept** | both `bone`, both brands gone |
> | lane 1 under Sticky Fingers *(control)* | `seal` | `seal` |
> | lane 5, neither card *(control)* | `ward` | `ward` |
>
> **Only two of the five bodies are live**, which the write-up below did not
> distinguish: `sticky_fingers_die` (Finnick's `cardPool[0]`) and
> `collateral_die` (Corvus's). The other three are unreachable today —
> `sleight_of_hand` carries `dep:true` and sits in no `cardPool`, and both npc
> cards carry `npcOnly:true`, which every player draft pool filters out (34020,
> 34025, 34026, 35328, 35583). **They were fixed anyway**, and the reason is
> specific rather than defensive: both `npcOnly` cards already ship a
> `playerDesc` written for the player's hand, so those activators are a feature
> waiting on a delivery route, not dead ends.
>
> `activateCollateralPlayer` writes `matchOppDice` only, and `G._enchArr` is
> player-side and sole — there is no rival brand array, so there was nothing to
> move. Commented in place rather than skipped in silence.
>
> The **worse half** below (`_tradeRestore` defeated over a traded lane) is
> **not** closed by this: it is a ledger problem, tracked with D10.

`fark_proto.html:24618-24620`:
```js
/* a swap, not a splice - lanes and brands stay aligned */
var pOld=G.matchDice[pBestIdx],oOld=G.matchOppDice[oWorstIdx];
G.matchDice[pBestIdx]=oOld;G.matchOppDice[oWorstIdx]=pOld;
```
**The comment is false for brands.** `_enchArr[pBestIdx]` is untouched. Same at
24634 (`collateral_die`: `G.matchDice[pBestIdx2]='bone'`, twice) and at 29343
(`sleight_of_hand`, dead layer). Measured: lane 4 `jade + {tithe,face:1}` →
`bone + {tithe,face:1}` under both cards; the jade crosses to the rival
unbranded.

Contrast Trade, which explicitly moves the brand out and ledgers it (18415
`myEn`, 18432 `G._enchArr[L]=null`, 18444 `_tradeSwaps.push`). **Two same-seat
swaps, opposite brand rules, no recorded ruling.**

**The worse half, measured.** Over a lane that Trade already touched, the
restore is defeated *and* duplicates a material. Trade at lane 4
(jade ↔ starstone, ledger `{lane:4,mine:'jade',theirs:'starstone',cnt:1}`), then
Sticky Fingers moves the borrowed starstone to the rival's seat 0:
```
matchOppDice final: [starstone, bone, bone, bone, starstone, bone]   ← two starstones
matchDice   final: [bone, iron, lead, amber, bone, flint]            ← jade gone
```
`_tradeRestore()` returned 0, but line 18590 still fired
(`matchOppDice[4]==='jade'===t.mine`) and wrote `'starstone'` back. Same run for
`collateral_die`: `restoredCount:0`, `playerGotJadeBack:false`,
`rivalGotStarstoneBack:true`, `_enchArr[4]` left `null` — the trade brand never
goes home either.

**Correction to the first inventory:** it named `endMatch`'s `naked_run` read as
the downstream consumer. **There is no `naked_run` anywhere in the file** — only
three comments (18436, 18555, 29410). The feat is `bare_hands` (9826), already
hardened to read the *owned* loadout (`S.run.dice` first). The un-restore is
real; the named consumer is not — a claim inherited from a stale comment.

**And these two cards cannot be stopped.** `_consumeWard` guards
`reduce_first_roll` (24803) and `swap_best_to_3` (25456) but is absent from
`swap_die` (24612) and `steal_die` (24647) — **and the guard itself is inert.**
`_consumeWard` (11490) reads `G._wardCharges`, whose only origin is
`_wardCharges:pCards.includes('warded')?1:0` (23100) on the dead layer. Measured
on a real Ambrose entry: `wardCharges: 0`, `_consumeWard('PROBE') === false`.
All four disruption classes are unstoppable, not two. `_ironGrip` is permanently
false and 11790 records `iron_grip removed`.

### D12 — Vagabond's drag desyncs every tap target in the row for the rest of that roll

> **CLOSED — P520.** The reorder permutes lane, material and brand together, and clears the cached chip centre. Tap targets confirmed by Denis in play: *"it works now yes."*

> **P520 — the reorder is now real. Half verified, half explicitly not.**
> Ruled by Denis: *"genuine reordering... A drag that moves the die's visual
> position without moving its identity is the display lying about game state."*
> And reported by him in live play before the patch was written: *"when I
> selected scoring dice the selection was offset by one die and not where I was
> actually clicking"* — D12 reproducing in the hands of a player, which is the
> strongest confirmation any finding in this sweep has had.
>
> **(a) The permutation — DRIVEN.** The drag now moves `d.lane`,
> `G.matchDice` and `G._enchArr` together with the visible order, so `seat ==
> lane` again and Trade/Snuff/Fog act on the die the player is looking at. This
> is also the direct answer to Denis's separate question about moving enchanted
> dice: the brand used to stay on the seat.
>
> ```
> bone  + tithe    lane 0 -> lane 2    brand travelled
> flint + ward     lane 2 -> lane 1    brand travelled
> ```
> `seatMatchesLane` true, lanes a permutation of the occupied seats, no enchant
> lost or duplicated.
>
> Two details that are deliberate. Seats are read **from the dice and sorted**,
> never assumed to be `0..n-1` — a die destroyed earlier in the roll leaves a
> hole and the shuffle has to happen within the occupied seats. And every
> `(material, enchant)` pair is **captured before any is written**, or later
> dice read entries the loop has already overwritten.
>
> **(b) The tap targets — NOT DRIVEN, and this must not be read as verified.**
> The fix clears the cached layout centre `d.hx`, which is the mechanism
> `_homeOf` already uses (`if(d.hx===undefined)this._measureHomes()`, 20043).
> It cannot be tested headless: **`D3X.dice` is empty and `D3X.mount` is falsy
> under SwiftShader** — measured, not assumed — so the meshes that carry `hx`
> do not exist. The probe substitutes synthetic stand-ins carrying the real DOM
> chips, which exercises the permutation exactly and the cache not at all, and
> it reports `TAP_TARGETS_NOT_VERIFIED_HERE`.
>
> **CONFIRMED BY DENIS IN LIVE PLAY: "it works now yes."** He reported the
> original symptom from a real match and then re-checked the fix the same
> way. That is the strongest tier of evidence available here - stronger than
> the probe that could not run, and stronger than a self-check, because the
> person confirming it is the one who found it and was not looking at the
> patch. Both halves of P520 are now settled.
>
> `tx`/`ty` are deliberately left alone: `_rawCentre(chip,tx,ty)` removes exactly
> the translate currently applied, so the pair is self-consistent and zeroing one
> half would double-count.

`_commitVagabondDrag` (36651) reassigns the meshes' `phys.x` (36663) **and**
re-appends the `.die-wrap` children of `#playerDiceRow` (36680-36683).
`D3X._slaveHost` (20045) positions the DOM chip as
`layoutCentre + (meshScreenX − d.hx)`, where `d.hx` is the chip's layout centre
**cached on first bind** (20054-20059) from `_rawCentre` (21431) — which
measures the exact node the drag re-appends. `d.hx` is invalidated in only two
places: a **row change** (22030) and the no-physics branch (22080). A move
*within* the same row invalidates nothing, so the DOM-slot delta is added on top
of the mesh move and the chip lands one slot pitch away per position dragged.

Measured with two independent instruments — the mesh projected the way
`_slaveHost` does, against the chip rect:
```
after the drag        bone   jade   amber  obsidian starstone vagabond
  drawn (mesh x)      39     111    175    242      330       400
  tappable (chip x)   39     39     103    170      258       686
  gap                 0      -72    -72    -72      -72       +287
tap where each die is drawn → picks: bone, amber, obsidian, starstone, (none), (none)   1/6
```
Control before the drag: 6/6 correct. The dragged die's tap target sits at
x≈686 on a 430 px viewport — off-screen, untappable.

**Two corrections to the first write-up.** `_dieTapRouter` (23322) is *not* the
cause: native DOM hit-testing is wrong on exactly the same five dice, so
removing the router would change nothing — the chip box is the broken thing. And
the reported "two dice overlapping" secondary is the same chip artefact; drawn
gaps after the drag (72/64/67/88/70) are identical to before it and nothing
overlaps.

**Scope: exactly one roll, and this was attacked rather than assumed.**
`_measureHomes` only fires on a row **count** change (21793), and a committed die
keeps its element and its stale `hx` — so the adversarial case is commit one
scorer and re-roll five, count 6 both sides. Measured: gaps all 0, tap accuracy
6/6. The row transiently empties during the re-roll, so 21793 fires anyway. The
damage window is exactly the selection phase of the roll in which the player
rearranged — which is the only window the feature exists for.

Fix shape: the drag must do for every moved die what 22029-22032 already does on
a row change (`d.hx=undefined; d.tx=0; d.ty=0; d.chip.style.translate='';`), or,
smaller, call `D3X._measureHomes()` after the DOM re-append at 36684.

### D13 — Blessed Confiscation's seventh seat is unconditionally unreachable, and the die is not inert while it sits there

> **CLOSED — P522. Ruled by Denis: swap, not add.**
> `matchOppDice.push(stolen)` becomes a replacement of the rival's **worst** die,
> so the loadout stays six long and the stolen die lands in a seat that is
> actually dealt. The starstone bank bonus, the AI's EV table and the First
> Strike reveal all read `matchOppDice`, so all three stop counting a die that
> was never rolled — fixed for free by the array staying the right length.
>
> **The unit check found the swap backwards in one case and it was guarded
> before shipping.** `[starstone, jade, amber] + bone` replaced the amber with
> the bone: the rival made itself *worse*. The card takes the player's BEST die,
> but late on the player's best can sit beneath the rival's worst. The swap is
> now conditional on being an upgrade. The confiscation is unchanged either way —
> the player has already lost the die — so the only question was whether the
> rival plays it, and an opponent choosing a worse die is a behaviour bug.
>
> | rival holds | confiscated | result |
> |---|---|---|
> | bone iron flint lead amber jade | starstone | bone → **starstone** |
> | jade ×5, bone | starstone | bone → **starstone** |
> | bone ×6 | obsidian | bone → **obsidian** |
> | starstone jade amber | bone | **unchanged** — not an upgrade |
>
> **Not driven, and stated as such:** `take_and_use` needs a specific boss card
> to fire, so the selection logic is unit-checked against constructed loadouts,
> not exercised through the card. The integration claim that matters — that the
> seventh seat was never dealt — was already measured by the sweep on a real
> Ambrose match (seats 0-5 only).
>
> **`take_best` deliberately untouched.** It never pushed; the ruling was about
> the add.

`G.matchOppDice.push(stolen)` (24682) makes the array 7 long. `_freeSeats` is
built ascending over `_rungAll.length` (28057-28062) and consumed as
`_freeSeats[i]` for `i<rollDice` (28068), with `rollDice ≤ left ≤ 6`. Index 6 is
selected only when `rollDice===7`, and **both producers of that are dead**:
`left=7` at 27939 needs `npcHasActive('seven_dice')` and `left=_oFullHand` at
28839 needs `double_down` — `npcActiveUses` is populated only from
`params.oCards` (31961-31965), and `G.oCards` only ever holds NPC_CARDS ids from
boss pools. Measured in a real Ambrose match: `npcHasActive_double_down:false`,
`npcHasActive_seven_dice:false`.

Measured after a real `startPTurn` steal:
`matchOppDice = [amber,amber,jade,jade,jade2,starstone,jade]`; a full driven
rival turn touched **seats 0-5 only**.

**The die is not mechanically absent.** `matchOppDice` is read by the starstone
bank bonus (29252-29254, **ungated**: `filter(m=>m==='starstone').length*500`
per bank) and the AI's EV table (14004) — so the confiscated premium die
silently inflates the rival's scoring. The First Strike reveal renders **7 dice
on the THEM row** (18820) while the rival rolls 6, and the 7-long array survives
the turn-boundary snapshot (`S.pendingMatch.matchOppDice.length = 7`).
(`honor_guard`/`standard_bearer` were also named as consumers; both are dead —
measured `false`.)

Residual on the player's side: `_enchArr` stays 6 against a 7-long `matchDice`
in the mirror case, failing the resume length gate at 32092-32094 and falling
back to `S.run.dieEnch`.

**This is the card the brief already scoped as blocked on the rival-side
rework.** The sweep confirms the diagnosis and narrows it: seat 6 is
unconditionally unreachable, not conditionally.

### D14 — Sacrifice never calls `_removeDieAt`, and the resume rewinds it: a zero-cost savescum of a match-permanent decision

> **CLOSED — P519.** `_removeDieAt` re-snapshots mid-turn, so the resume no longer rewinds a match-permanent sacrifice. Driven: live 6→5, snapshot 6→5.

`CFX.sacrifice` reimplements five of `_removeDieAt`'s responsibilities and skips
four: the loan hand-back (19144), the `ft.lane` shift (D9), the mid-turn
re-snapshot (19232-19244), and `_firstStrikeRender()` (so P515's fix does not
cover it). Measured after a live sacrifice paying +800: live `matchDice` 5 /
`numDice` 5 / `_diceOut` 1, while `S.pendingMatch` still held **6 matchDice,
numDice 6, `_diceOut` 0**.

**Upgraded from "an inconsistency" to a defect.** Sacrifice writes `G.pPts+=P` —
**banked** points, bust-immune — and never re-snapshots. Quit-and-resume after a
regretted sacrifice returns the die *and* the charge, and the 800 is simply
re-earnable by playing the card again. The equivalent Break is explicitly
protected against exactly this at 19232-19244.

It also filters neither `_breakPreserved` nor `_breakBorrowed`, both of which
Break honours (19055, 19273). Brief §1 makes a borrowed die an illegal Break
target "full stop"; Sacrifice can still shatter one.

### D15 — `reduce_first_roll` clamps to a literal 5, so Mabel's Pinch is free against a player already down a die

> **CLOSED — P561, and the fix is NOT the one the title implies.**
>
> Both corrections in this entry hold, and reading the card text settled it:
> `mabels_pinch` and `pocket_sand` both say **"leaving you with five instead of
> six"**, so the clamp matches the card and `_dropLanes(1)` would contradict it.
> The clamp stays.
>
> **What was actually wrong is that the announcement did not depend on the
> effect.** With the player already at five, the clamp is a no-op and the game
> still said "MABEL'S PINCH — 5 DICE!" — a message vouching for a die that was
> never taken. Driven, control on both sides:
>
> | | at six *(control)* | at five |
> |---|---|---|
> | before | 6→5, announced | 5→5, **announced** |
> | after | 6→5, announced | 5→5, silent |
>
> The control matters: a fix that silenced the card everywhere would pass an
> announcement-only check and break it.
>
> **And the Ward was spent on the no-op** — `_consumeWard` ran before anything
> asked whether there was an effect to block. That half is **inert today**
> (D11 measured `G._wardCharges` as having no live origin), so it is a
> correctness fix rather than a live one, and the two are worth keeping apart.
>
> One gate does both: `G.numDice>5` is exactly the condition under which
> `Math.min(G.numDice,5)` changes anything.

`fark_proto.html:24804`
```js
G.numDice=Math.min(G.numDice,5);
```
Measured across three arrangements:

| arrangement | numDice before → after | pool lanes |
|---|---|---|
| 6 lanes, numDice 6 | 6 → 5 | 0,1,2,3,4 |
| 5 lanes (post-removal) | 5 → 5 (**no effect**) | 0,1,2,3,4 |
| 6 lanes, numDice 5 (armed penalty) | 5 → 5 (**no effect**) | 0,1,2,3,4 |

The card still announces "5 DICE". `mabels_pinch` is `npcOnly, owner:'mabel'`
(12032-12035) in Mabel's `cardPool` (10842), so this is live. `pocket_sand` is
in no cardPool and `npcWonCards` has no writer — **never dealt**.

**Two corrections.** (a) The first two write-ups called this a P516 instance and
proposed `_dropLanes(1)`. It is *not* the P516 shape — `Math.min` can only
lower, and never refunds an armed penalty, which is the entire content of that
rule. It is a non-stacking clamp. And `_dropLanes(1)` would be a **design
change**: it would take an already-seized player to four dice while the card
text says "five instead of six". (b) The proposed arrangement — a `take_best`
seizure earlier in the match — **cannot arise in a Mabel match**; her cardPool
holds no steal card. The clean live arrangement is an **obsidian die shattered
earlier**: 25283 → `_removeDieAt` → 19181-19185 splices MD and EN and calls
`_dropLanes(1)`, so `matchDice.length===5` permanently.

Second-order, confirmed: the refill fills `_freeLanes` ascending (25121), so the
pinched die is deterministically the **highest lane** — measured lanes
`[0,1,2,3,4]`, lane 5 never rolled.

### D16-D24 — lesser confirmed defects

> **RE-DERIVED against the current build before implementing any of them**, on
> the reasoning that D3, D7 and D15 all turned out partly stale on inspection.
> The list is **not one queue** — these are four different states:
>
> | | state |
> |---|---|
> | **D24** | **ALREADY CLOSED — by P528, never marked here.** The `else`-gated pool filter is gone; the filter is unconditional and P528's own comment names D24 as the case it closes. Nothing to do. |
> | **D21** | Held, now **FIXED (P562)** — see below. |
> | **D16** | Held, now **FIXED (P565 + P566)** — see below. |
> | **D17** | **CLOSED by ruling + P588.** Denis ruled: retire the player's Sleight rather than build it. P588 scoped the retirement to the broken side only (`FAM_PLAYER_RETIRED` — the rival's `G._oSleight` implementation keeps working for the vagabond bosses). The inert `CFX.sleight` remains reachable only from a legacy save that already holds the card. |
> | **D22** | **CLOSED — P567** (its own entry below says so; this row was never updated to match). |
> | **D20** | Held, now **FIXED (P563)** — see below. |
> | **D18** | **HALF CLOSED — P568** (Sacrifice half fixed; Transmute half withdrawn as a non-finding — see the entry). This row previously said NOT SETTLED and was never updated. |
> | **D23** | Part (a) **CLOSED — P568**; part (b) under re-derivation 2026-08-13. |
> | **D19** | **RULED AND CLOSED — P520** (Option A: the drag permutes lane, material and brand together; Denis confirmed in play). This row predated the closure recorded at the D12/P520 entry. The tail (committed dice participate in the reorder; Palm adjacency becomes aimable) is a balance question under the ruling, not an integrity defect. |
>
> **2026-08-13 re-derivation (nine investigators, current build):** D3, D7, D11,
> D15, D23(b) confirmed CLOSED at their recorded patches. D25 was STILL OPEN —
> its "unreachable" mitigation went stale when P615 revived the player hand —
> and D6(a) and D10(b) held exactly as recorded. **All three fixed by P691**,
> each verified by a driven probe: D25 swaps instead of pushing a seventh seat
> (arrays stay parallel), D10's dead-loan list holds stash indexes (legacy
> material strings still match conservatively), and D6's amber preserves the
> SEAT as well as the die (the deal walk leaves the preserved lane alone —
> dealt [0,1,3,4,5] with lane 2 claimed). |
>
> **A count is not a re-derivation, and this pass nearly got that wrong.** `_cult`
> came back with 4 hits against the entry's claim of 1, which looked like
> staleness — it was one line using `d._cult` twice plus a comment. Two real
> sites, entry correct. Checking instead of concluding is the only reason D16 is
> in the HOLD row rather than wrongly retired.
>
> **D17 has picked up an interaction with P555.** `_famSleight` is now carried
> across a resume, so "single-use forever" is *durable* where a reload used to
> reset it and accidentally refund the card. For an inert card the two states are
> equally worthless, so nothing got worse — but the interaction belongs on the
> record, because the real fix is to implement the effect or retire the card, and
> whoever does that will meet the snapshot field.

- **D16. Cultivate's growth dies with the turn.** `d._cult` (14223) is the only
  occurrence in the file and lives solely on the pool die object; `G.pool=[]` at
  startPTurn (24426) and `_turnTableClear` (23164) replace those objects. "For
  the rest of the match. Stacks." is at most one turn, and only pays on a second
  fire inside the same turn.

  > **CLOSED — P565 + P566, reproduced first, eight arms plus five controls.**
  > The store is now `G._cultArr`, lane-indexed beside `G._enchArr`, because a
  > lane is the only per-die identity that outlives the pool. Measured before:
  > 3 carriers all on pool objects, **0 reachable anywhere in `G` after the real
  > `startPTurn`**, 0 in the snapshot. After: 150 on `G`, 150 in the snapshot,
  > growth travels on Sticky Fingers and on Trade, slides correctly through a
  > `_removeDieAt` splice, and survives Powder Keg.
  >
  > **The entry understated it.** The growth only ever paid on a *later commit
  > including the same object*, and a committed die is never selectable again.
  > There are exactly two un-commit sites in the file: `powder_keg.use` (in
  > place) and `double_down` (which then does `G.pool=[]`). **Powder Keg was
  > therefore the only route by which Cultivate had ever scored a point** — which
  > is why the probe's Powder Keg arm is a control, not a curiosity.
  >
  > **P565 shipped a hole and P566 closed it: there are TWO snapshot writers.**
  > `saveMatchState` (10293) rebuilds `S.pendingMatch` whole at every turn
  > boundary; `_snapDiceOnly` (19530) updates the dice fields in place mid-turn.
  > P565 patched only the second, so the growth reached the snapshot during a
  > turn and was dropped by the next boundary — worse than never saving it.
  > `saveMatchState`'s own `_diceOut` comment is the warning, word for word.
  >
  > **What caught it was a control, not an assert.** The assert passed — the
  > line *was* in the file. And "growth not in snapshot" reads identically
  > whether the patch is wrong or `saveMatchState` never ran, since it wraps its
  > body in a swallowing `try/catch` behind an early return. The arm only became
  > readable once it carried a **sentinel brand on the line directly above the
  > growth's**: brand landed, growth did not, so the write ran and my line was
  > somewhere else.
- **D17. Sleight is inert *and* single-use forever.** `CFX.sleight.use` sets
  `G._famSleight` (14387); the only other reference in the loaded corpus is its
  own `canUse` guard (14385, `!G._famSleight`) — measured over every global
  function's `.toString()` plus every inline `on*` attribute, 1,071,965 chars,
  zero hits outside CFX. Nothing clears the flag: measured after `startPTurn`,
  `famSleight true, sleightCanUseAgain false, sleightCharges 2`. A 2-charge card
  that does nothing, once. The rival's Sleight is a *different* flag,
  `G._oSleight`, and **is** implemented (25184-25188).
- **D18. HALF CLOSED — P568, half WITHDRAWN.**

  > **The Transmute half is a non-finding and is withdrawn, not fixed.** It was
  > paired with Sacrifice on the strength of its *filter* alone. Its `use` runs
  > `var d=free[pick-1]` — **the player picks**. Transmuting your own held die
  > is a choice, not a theft.
  >
  > **The Sacrifice half is real and is fixed.** `_targets()` was
  > `!committed && !_shattered && lane!==ftLane` while `use` takes
  > `free[free.length-1]` with **no targeting prompt at all**, so a deliberately
  > held die is destroyed without ever being chosen. That filter is curated —
  > the loan lane and the one-die floor are both carved out on purpose — so
  > `_frozen` was never *considered*, not deliberately allowed. Measured 6
  > targets → 5 after the fix, with one die frozen.
  >
  > **No live effect today, and that is measured rather than assumed.**
  > `_frozen` has exactly two writers, both in the legacy player-active layer.
  > Driven on the current build (`tools/apv_frozen_reachable.js`): a real roll
  > yields 0 frozen dice, and `canActivateCard` refuses **every** id tried —
  > including ones from the same layer that are supposed to work — with
  > `effectiveCards()` and `pCards` both empty. That last one is the arm's void
  > check: it proves the layer is dead rather than that these two cards are
  > special. **Landmine removal** — the frozen mechanic is a feature someone
  > will revive.

- **D18 (original entry). Transmute and Sacrifice both admit `_frozen` dice; every other card
  excludes them.** Transmute: `G.pool.filter(d=>!d.committed)` (14241).
  Sacrifice: `filter(d=>!d.committed && !d._shattered)` (14281/14283). Since
  Sacrifice takes `free[free.length-1]` with **no targeting UI**, a player who
  froze their best die can have it shattered involuntarily. (The earlier claim
  that Transmute is "the only card" is false.)
- **D19. Vagabond's drag moves two of the six facts, and Trade then takes the
  wrong rival die.** The lane side stays internally consistent — no duplicate
  lanes, `G.matchDice[d.lane]===d.mat` still true for every die. What breaks is
  that lane is now detached from the seat the die visibly occupies. Driven
  through the real dispatch `def.fire({die,side,lane:_laneOf(d),mult})` (18668):
  vagabond dragged seat 2 → seat 6, `_laneOf(die)=1`, rival die in that lane
  **silver** (what Trade took) vs the rival die facing where it sits
  **starstone** (what the player is looking at). Trade's own text says "in the
  same seat" (18408); so do Snuff (18461) and Fog (18475). Needs a **ruling**,
  not a patch: either the drag permutes MD/EN/`d.lane` together so seat==lane
  always, or lanes are declared an invisible identity and those four effects
  stop presenting as seat-facing. *(Instrument flag: the original V2 seat
  numbers were computed from chip rects — the very instrument D12 disowns. They
  came out right because the whole row shifts by one uniform pitch, but re-derive
  from mesh positions before acting.)* Related, confirmed: `_vgRowInfo` (36564)
  has no committed-die test, so the drag reorders **committed** dice, which
  changes `_cRow.indexOf(_palm)` adjacency for Finnick's Palm (14127-14131) — a
  live relic commit effect.
- **D20. CLOSED — P563.** *A sleeved rule binds the rival and not the player.*
  **The caller already got this right** — `if(_ruleActive('pickpocket','p'))`
  schedules the palm — and the callee re-asked a different question (what is in
  `G._tell`) and refused. Driven, four arms, only the guilty one moved:

  | arm | before | after |
  |---|---|---|
  | tell **is** pickpocket *(control)* | fired, 2 tries | fired |
  | **sleeved over another tell** | **never, 120 tries** | **fired, 10** |
  | both *(control)* | fired | fired |
  | pickpocket nowhere *(over-correction control)* | silent, 120 | silent, 120 |

  `chance` was fixed too — it was read off `G._tell`, so past the gate a sleeved
  pickpocket would have rolled against whatever other rule held that slot. Now
  from its own record via `_tellById`, the same shape D22 documents for Drill
  Order. Latent today (both are .30); D22's point is exactly that a retune
  separates them silently.

  **The probe measured the wrong thing first** and reported zero palms in *all
  four* arms on *both* builds — the removal sits inside a `setTimeout` behind a
  650ms flight, so the pool had not changed yet. Control A failing is what
  exposed it immediately. It now reads `die-palmed`, the class the palm adds
  synchronously.

- ~~**D20. A sleeved rule binds the rival and not the player.**~~ `fark_proto.html:11505`
  `if(!G||!G._tell||(G._tell.id!=='cutpurse'&&G._tell.id!=='pickpocket'))return;`
  — the callee re-asks by `G._tell.id` what the file's own comments (18618,
  18787, 18829, 11259) say must be asked via `_ruleActive`. Measured matrix:

  | arrangement | `_ruleActive('pickpocket','p')` | `'o'` | palm fired |
  |---|---|---|---|
  | seat's tell **is** pickpocket | true | false | yes (pool 6→5, numDice 6→5) |
  | **tell `last_call` + sleeve pickpocket** | **true** | **true** | **no** |
  | tell + sleeve both pickpocket | true | true | yes |

  Root cause is broader than "boss seats": `_applySleeve` (11298) installs into
  `G._tell` only when it is **empty**, and `_applyTellAndSleeve` (11310) runs
  `_applyTell(); _applySeal(); _applySleeve();` — so the bug fires whenever
  *anything already occupies `G._tell`*, including a sealed patron seat carrying
  any other rule. Reachable path fully verified: beat Finnick → 13634 grants the
  tell → `_gbBossPeek` sleeve chip → `famSleeveSet('pickpocket')` → any boss
  match. A rule the brief says binds both sides binds one, in the player's
  favour, on a rule they had to beat Finnick to win. *(Every other `G._tell.id`
  read was enumerated: 24303 and 24504 are the same class but cosmetic; 29659 is
  dead behind `if(false&&…)`. 11505 is the only one with a mechanical
  consequence.)*
- **D21. The First Strike panel goes stale on the route P515 didn't cover.**
  `_firstStrikeRender` is called at the *top* of `startPTurn` (24426); the NPC
  swap/steal block runs at 24604-24689, after it, splicing inline rather than
  through `_removeDieAt` (which does call it, 19251). Corvus owns **both** the
  `first_strike` tell (10879) and `collateral_die` (10870), so the pairing is one
  match. Measured: panel text byte-identical before/after
  (`YOU BO IR LE AM JA ST`) while `matchDice` went
  `[bone,iron,lead,amber,jade,starstone]` → `[bone,iron,lead,amber,bone,bone]`.
  Bounded — stale for one player turn; 24426 repaints it next turn.
  `CFX.sacrifice` is on the same uncovered route (D14).
- **D22. CLOSED — P567.** *Drill Order's cap, derived six ways, one a literal.*

  > **Driven, not read**, because the defect is latent: every fallback is also
  > 3, so a build as shipped shows agreeing numbers. The probe **retunes the
  > record to 5** — the maintenance act the defect waits for — and asks each
  > surface. Before / after:
  >
  > | surface | before | after |
  > |---|---|---|
  > | player `_drillCap().cap` | 5 | 5 |
  > | sleeve chip | `1/5` | `1/5` |
  > | **rival, rolls per turn, rule sealed** | **3** | **5** |
  > | rival, rule off *(control)* | 14 | 4 |
  >
  > **The probe corrected the entry twice.** (1) The sleeve chip was listed as a
  > divergent derivation and is not — `_st` is `_tellById(G._sleeve)`, already
  > the record. (2) There are **six** derivations, not two, and one of them is
  > not a cap bug at all: the hot-dice dialogue re-asked
  > `G._tell.id==='drill_order'` instead of the rule system, **D20's shape
  > exactly**, so a *sleeved* Drill Order killed the ROLL button and withheld
  > the line explaining why. Enforced in silence. That half is a **behaviour
  > change**, not a refactor.
  >
  > **Two instrument faults on the way, both caught by the same control.** The
  > arm first waited on `G.phase !== 'opp'` (no such phase — counted one roll),
  > then on a 1.2s quiet period, which is *shorter than* `_oppDelay(1900)`: it
  > declared the turn over mid-turn, started the next trial, and let ghost
  > timers from the previous turn inflate the count — **an arm with a hard cap
  > of 3 reported 4**. Fixed by using `G._oppTurnActive`, which has two writers
  > and whose clear is the first line of `finOpp`, the single exit for bank,
  > bust and cap alike. Plus `oppShouldBank` stubbed to `false`, isolating the
  > roll cap from the banking policy.

- **D22 (original entry). Drill Order's cap is derived on the player's side and a literal on the
  rival's.** 23541 `var def=(G._tell&&G._tell.id==='drill_order')?G._tell:(_tellById('drill_order')||{}); var cap=def.maxRolls||3` versus 28011
  `if(_ruleActive('drill_order','o')&&oppRollNum>=3)`. Measured
  `_tellById('drill_order').maxRolls === 3`, so they agree **today**; retune the
  RUNGS record and the sealed/sleeved rule silently applies two different caps
  to the two sides. 13114 carries a third copy.
- **D23(a). CLOSED — P568.** *Still Waters could never be sealed.*

  > Censused off the live `RUNGS`: **eight boss tells, seven in `_SEAL_POOL`**,
  > with the parked `steeped` in the eighth slot. Aldric's was the only badge
  > with no cursed-seat route. **Not a judgement call — the file had already
  > made it**: the note above `_SEAL_POOL` records taking `still_waters` off a
  > *blocklist* precisely so a sealed or sleeved one would work, on the grounds
  > that a rule the player can win as boss spoils must be usable. Unblocked,
  > then never enrolled. Added rather than swapped: `steeped`'s place is
  > deliberate and documented.
  >
  > **Said out loud because it is a balance change**, not only a fix:
  > `_rollSealTell` picks uniformly, so every other rule moves from 1/8 to 1/9
  > on a cursed seat. Two consumers, both in the night builder; no other reader
  > of `_SEAL_POOL` exists.
  >
  > **The new probe asserts the class, not the instance.**
  > `tools/apv_seal_pool_covers_tells.js` derives the tell list from `RUNGS` and
  > fails the day a ninth boss lands unenrolled. Its census control earned its
  > place immediately: the first version walked `TIERS`, which carries no `tell`
  > field, so the walk returned `[]` and "nothing is missing" passed **over
  > nothing at all**. Membership and reachability are also separated — the
  > picker is driven 400 times, not read.
  >
  > **(b) is still open** — a double-rule seat shows one badge and enforces two.

- **D23. Two tell-HUD gaps.** `still_waters` can never be sealed — `_SEAL_POOL`
  (11234) has eight entries but substitutes the parked `steeped` for it,
  programmatically confirmed `sealPoolMissing: ["still_waters"]`; Aldric's is the
  only badge with no cursed-seat route, and 11244's comment ("Cursed seats
  already draw from the full rule pool") is false of it. And a **double-rule seat
  shows one badge and enforces two** — measured sealed `zero_hour` + sleeved
  `drill_order`: `#tellBadge` renders ZERO HOUR only, while `_drillCap()` returns
  `{active:true,cap:3}` and `_updateDrillLock` locks the ROLL button with no
  counter anywhere. `_updateTellHUD` (11429-11467) opens `var t=G._tell;` and
  keys every branch off `t.id`, so a second rule gets no HUD element by
  construction. The comment at 23520-23526 records fixing this symptom — it fixed
  the *enforcement* asymmetry, not the HUD.
- **D24. A laneless shattered die survives the sweep as a live scorer with its
  element deleted.** 25280-25284: `_shLanes` filters to numeric lanes, and the
  `else G.pool=G.pool.filter(d=>!d._shattered)` only runs when that list is
  **empty**. Measured on an executed path: two shattered dice, one laned and one
  not → `_shLanes=[1]`, the `else` never runs, `poolShattered: 1`, pool lanes
  `[0,1,undefined,3,4]`, and the seat is never refilled because `needNew` is 0.
  Today no producer leaves `d.lane` undefined — but **D8 shows two of the three
  producers (25031, 26392) stamp `i%G.matchDice.length`, which is NaN on an empty
  loadout**, so the "dead today" that this was previously filed under does not
  hold as stated. (26392 is separately on the dead card layer: it is gated on
  `G.activeCardState.stitchActive`, written only by `activateMabelsStitch`.)

---

## 3. THE BRIEF'S NEWLY-FLAGGED LIST, ADJUDICATED

The brief flagged these as pattern-matched from conversation rather than
checked. Checked.

| flagged item | verdict |
|---|---|
| **Vagabond's drag-to-reorder** | **CONFIRMED DEFECT ×1 + a ruling.** The suspicion was right and the mechanism is not the one predicted. It does **not** corrupt the lane invariant — no duplicate lanes, `matchDice[d.lane]===d.mat` holds for every die, MD/EN/ND untouched (measured). What it breaks is the **cached chip layout centre `d.hx`**, which desyncs every tap target in the row for the remainder of that roll (D12, measured 1/6 taps correct). Separately it detaches lane from visible seat, so Trade/Snare/Snuff/Fog — all of which advertise "the same seat" — target by `_laneOf` and hit a different rival die than the one the player is looking at (D19). Reachability confirmed at the *acquisition* end too, which nobody had checked: `DICE_STORE` stocks the vagabond at 700 g, `_shopRollNight` offers it 45 %/night with a pity rule, and `_stTrade` is reached from a live pointer handler at 33251. |
| **`reduce_first_roll`** | **CONFIRMED DEFECT, but not the predicted shape.** It is not "removes dice, same shape as Break and Sacrifice" — it removes nothing and splices nothing. It is a **clamp that no-ops whenever the player is already at five** (D15, measured across three arrangements), so Mabel's Pinch is free against anyone who has lost a die, while still announcing "5 DICE". The suggested `_dropLanes(1)` remedy is a **design change**, not a restoration of intent, and needs Denis. Live via Mabel's pool; the sibling `pocket_sand` is **never dealt**. |
| **`swap_die`** | **CONFIRMED DEFECT** (D11). Both modes write `G.matchDice[…]` and leave `G._enchArr[…]` behind, under a comment at 24618 that says the opposite. Both are guaranteed cards: `sticky_fingers_die` is Finnick's `cardPool[0]`, `collateral_die` is Corvus's. Worse than the brand loss: over a lane Trade already touched, `_tradeRestore` is defeated *and* line 18590 still fires, measured **conjuring a second starstone into the rival's loadout** while the player's jade vanishes. Neither card can be blocked — `_consumeWard` is not applied to them, and the guard itself is inert on the dead `pCards` layer. |
| **`swap_best_to_3`** | **CLEAN.** Driven at Grog on a real roll: pool before `0:bone:1 … 5:starstone:1`, after `0:bone:3 1:iron:3 2:lead:1 …`. Only `d.val` moved; lanes, materials, `matchDice`, `numDice` all unchanged (25451-25472). Victims are picked **by object, not by index**, which is precisely the arrangement that would break it — it does not. One cosmetic note: the non-D3 branch at 25469-25472 never sets `el._trueVal`. The earlier audit's separation of this from Trade was correct as caution and wrong as suspicion. |
| **Quicksilver's reroll** | **CLEAN.** 19550-19558 writes `d.val` and `d.sel` and nothing else. Measured: lane/material/enchant map **byte-identical** before and after, counts unchanged. |
| **Ward's armed-to-consumed** | **CLEAN — it is purely a flag, on both transitions.** Armed at 18337 (`G._wardArmed=true`, plus `G._wardBoost` at 18342); consumed at 26173-26183, which clears the flags, computes `_half` and does `G.pPts += _half`; expired at 24434. **No die is relocated, removed, re-laned or re-materialed on any path.** The source distinguishes the two ward systems itself at 18328-18329, and the distinction matters: the *card* ward `_wardCharges` (11490, `_consumeWard`) originates only from `pCards.includes('warded')` at 23100 on the dead layer — measured `wardCharges: 0`, `_consumeWard('PROBE') === false`. So the enchant is clean and the card is dead; the flag they share a name with is what makes D11's disruptions unstoppable. |
| **Powder Keg** | **CONFIRMED DEFECT ×3** (D5) — the "likely safe" guess was wrong on all three counts. `G.numDice=G.pool.length` (14263) is the fifth instance of the banned recompute-from-length and **P517 turned it from dormant into a live penalty**. It has no resolve guard, so a Tier II/III second charge queues a second `_delayedDoBust` — the exact bug `CFX.encore`'s own comment documents as fixed in the sibling card. And it scores a captured `free` (14268) with removers still legal, so it carries D4's stale-pool hole too. The brief's own reason for flagging it — "relevant again if the bust-save redesign ever picks a specific die by reference" — is already true: it picks `G.pool.slice()`. |
| **For Keeps** | **CLEAN as a lane/array question; one design question.** Both directions keep the arrays parallel. Win: `famFkTake` (13603-13620) pushes to `S.run.diceInv` then `_enchInit()` pads `dieEnchInv` to length and stamps born brands (19450-19476). Loss (30238-30251, **not** 30231-30240 as first cited): splices `S.run.dice[di]` and `S.run.dieEnch[di]` at the same index, refills `'bone'` at the end, pads `dieEnch` to match — surviving dice shift lane together with their brands. The `indexOf(best)` is P513's shape but is benign because `rank()` (30240) is material-only, so any die of that material is an equivalent pick. **The design question:** with two dice of one material, the arbitrary pick decides **which brand dies**, and brands are bought with gold — a player holding a plain silver in lane 0 and a Warded silver in lane 4 always loses the plain one (favourable-arbitrary, but a live asymmetry, not merely a future hazard). It becomes a real bug the moment `rank()` learns about brands or relics-by-instance. One further imprecision: if the ranked best came from `diceInv` but the same material also sits in the loadout, `di>=0` takes the loadout copy. **Read-verified only — a For Keeps loss was never driven.** |

**Scorecard for the flagged list: 4 confirmed defects, 3 clean, 0 dead — and
two of the four had a different mechanism than the one predicted.** The
"lower confidence, worth checking" half turned out to contain the worst card in
it (Powder Keg) and two genuinely clean ones (Quicksilver, Ward). Confidence
ordering was uninformative; only the checking was.

---

## 4. WHAT REMAINS UNCHECKED

**Stated plainly, so nothing here is mistaken for cleared.**

1. **The card-slot parallel — SWEPT (P555). It found a real defect, and NOT the
   one this item predicted.** The question asked was index/count desync. That
   half came back **clean, and was checked rather than assumed**: `famRenderRow`
   emits `famCardTap(i)` with the **source-array** index from its `forEach` over
   `G.pF`, not a running count of rendered cards — so the two `return`s that
   skip a card (no def, `fam==='tavern'`) cannot shift it. `famUse(i)` then
   reads `G.pF[i]`. The one positional-index smell named here is not a bug.

   **The desync is in TIME, not in position.** `tools/card_state_census.py`
   put every card-layer field against the snapshot and found nine that are
   written, live across a turn, and never saved. P511 taught the snapshot to
   carry `pF`/`oF` — the CHARGES — and did not carry the FLAGS those charges
   buy. Carrying one without the other is worse than carrying neither: before
   P511 the charge came back with the effect, so at least they agreed.

   Driven end to end (`tools/apv_opp_armed_resume.js`), arming through
   `_npcArmActives` rather than by setting flags:

   | | sleight | ill_omen |
   |---|---|---|
   | armed | 2 → 1, flag set | 2 → 1, flag set |
   | after RESUME MATCH | charge **1**, flag **gone** | charge **1**, flag **gone** |

   with two controls on the same reload — the spent charges stayed spent and
   `_oGrudgeStack` came back — so the loss is not a broken restore. The window
   is every ordinary turn boundary: `saveMatchState()` is the **last statement
   of `startPTurn`**, and both flags are armed in the rival's preceding turn and
   consumed after it.

   Nine fields now carried: `_oSleight`, `_oIllOmen`, the player's mirrors
   `_famSleight`/`_famIllOmen`, the roll-forces buffer
   `_famPeekVals`/`_famHoneyVal`/`_famKegTriple`, and `_famBankCount` /
   `_famMinBank` — the count seeds "is this your FIRST bank" (Hair of the Dog)
   and the minimum is reseeded from it, so losing it rewrote the smallest bank
   of the match.

   **What remains open here:** `CFX.tamper` mutating opponent card instances,
   and `S.run.cards` / the equip and tier UIs, were not reached.
2. **Charge accounting and UI reachability were never exercised for FAM
   cards.** Every probe in the FAM layer calls `CFX.<id>.use(inst)` directly,
   never `famUse(i)`. That still executes the real handler, so the behavioural
   claims hold — but it bypasses `canUse` in some probes and the charge
   decrement in all of them. **No measurement in this sweep proves a single
   FAM card's charge is spent correctly, or that the sheet button reaches it.**
   The chain was verified by *reading* (13084 → 13468 → `famUse`).
3. **The Powder Keg × Fair Trade seam (D5a).** Both halves driven, the join
   never. Per the project's own standard the measurement is not settled until a
   patch is written against it.
4. **Powder Keg over Preserve.** `G.kept=[]` (14257) discards the preserved
   entry startPTurn wrote at 24556 while its chip stays in `#keptRow`. Points
   are correctly forfeited (measured `turnPtsAfterKeg 0`); the orphaned chip is
   **read, not driven**.
5. **A completed Vagabond drag through the real gesture.** Neither pass could
   finish one — under SwiftShader the 3D layer tracks 0 dice, `_vgRowInfo()`
   returns `null`, and `_startVagabondDrag` returns immediately. Every V-finding
   was driven by applying the reorder `_commitVagabondDrag` performs, not by
   dragging. Consequently the guard at **36673**
   (`if(poolSeq.length===G.pool.length)G.pool=poolSeq;`) is untested: `poolSeq`
   is built by matching `G.pool[i].el === d.chip`, and `_tradePaint` (18507)
   **replaces the die's DOM node and reassigns `d.el`** — a nameable way to
   shorten `poolSeq` and leave the DOM reordered while `G.pool` is not, which
   would silently desync every position card from what the player sees.
   Reasoned, not executed.
6. **Whether `mi` can fall out of range at 14313**, where the MD/EN splices are
   guarded and the `_dropLanes(1)` beside them is not. `_removeDieAt` has the
   same asymmetry at 19183-19185. No arrangement was constructed; flagged shape,
   unproven reachability.
7. **`S.npcWonCards`.** It has no writer *found* — three passes looked, none
   traced what could write it. If anything can, three currently-dead literal
   count writers (`blockade`, `seven_dice`, `whispers_hex`) become live.
8. **The rival's obsidian never shatters.** Structurally sound — the sweep sits
   in `afterRoll`, whose three callers (25033, 25166, 26395) are all player-side,
   and `step()`'s rival roll has no family check — but **never executed** by
   anybody.
9. **A For Keeps loss.** Read-verified only (§3).
10. **Whether Preserve's dropped enchant (D6b) has a downstream consumer that
    would have paid.** Tithe-on-bank was not traced.
11. **A vagabond die actually appearing in a driven night's stall roll.** Code
    path and a driven `_stTrade('vagabond',3)` confirm obtainability; seeing one
    offered on screen requires `#gbShop.st-focus`, which was not driven.
12. **The dead player-card layer, catalogued but not fixed.** If
    `params.pCards` is ever honoured, this is the inheritance, all
    *read-verified only*: `activateAlchemistsChisel` writes
    `G.matchDice[leftPoolIdx]` at 31657 — **a pool index used as a lane index,
    the only such site in the file** (driven on a post-drag arrangement: it
    wrote lane 1 instead of lane 2, silently destroying the player's Vagabond
    die for the match and leaving its brand on an amber);
    `activateBlessedConfiscationPlayer` (31542) pushes to `matchDice` with no EN
    push and no ND adjustment; `activateRoyalSeizurePlayer` (31531) splices
    `matchOppDice` to 5 while `left` stays 6, so `_freeSeats[5]` is undefined and
    the rival rolls a phantom bone in a seat that no longer exists;
    `activateStickyFingersPlayer` (31503) and `activateCollateralPlayer` (31516)
    are D11's shape; `activateDoubleDown` (31364) and `activateSevenDice` are
    recompute-from-length; the three cancel blocks in `activateCoinFlip`
    (31589), `activateTheNudge` (31611) and `activateAlchemistsChisel` (31634)
    null `_vgDragState` using field names (`clone`, `srcEl`) that state does not
    have — the live shape is `{me,die,order,homes,from,to,info,target,raf,y0,onMove,onEnd}`,
    so both `if` bodies are dead and the die keeps `.vg-drag-origin`; the tier
    loadout drag (34917) and `_buyDieAtSlot` (33954) both move `S.run.dice`
    without `S.run.dieEnch`; and `famDieEquip` (14889) discards a branded bone
    with its enchant and no refund.
13. **Two vestigial reads.** `_loDragging` is read in the tooltip gates
    (22603-22604, 30649-30650) and **never assigned anywhere in the file**.
14. **Line-number drift warning for whoever reads next.** In the 31800-32100
    region the Read tool's numbering drifts by roughly 9 lines from
    grep/`sed -n`. Every anchor in this document was taken with grep/sed.

---

## 5. DOES ANY OF THIS WANT THE SHARED-HELPER TREATMENT?

`_dropLanes` (P516) settled the decrement rule and fixed no live bug — it gave a
rule a home. Three of the clusters here have the same shape: the correct
implementation already exists at one site and did not travel. **Ruled: three
helpers and one rule, in this order of payoff.**

### 5a. Make `_removeDieAt` the only way a die leaves the table — highest payoff by a distance

`CFX.sacrifice` reimplements five of `_removeDieAt`'s responsibilities and skips
four. `steal_die` (24668-24686) reimplements three and skips three more, which
are no-ops *only because of where the block sits*. Adopting the one remover
closes, in a single change: **D8** (add the floor there and every remover
inherits it), **D9** (`ft.lane` shift), **D14** (re-snapshot, `_firstStrikeRender`,
`_breakBorrowed`/`_breakPreserved`), and the `_steadyDisarm` half of **D4** —
five confirmed defects, four of them in one card.

Order by payoff, not by ease: this is not the easiest item on the list, but it
removes the most.

`_removeDieAt` needs two changes of its own first: a floor on `matchDice.length`
(it currently has none — `_dropLanes` floors only the count), and its guard at
19117 must reject non-finite lanes, not just `lane<0`. `NaN<0` is false, which is
how D8's die became unremovable.

### 5b. A rival-side seat/count helper — `_oDeal()` returning `{seats, count}`

**D1 and D2 are duals of one root cause.** `left` and `_freeSeats` are computed
independently and nothing keeps them in agreement:

- **D1**: `left` is reset to a literal 6 while `_freeSeats` still excludes the
  snuffed seat → count exceeds seats → the `_seat` fallback invents an index.
- **D2**: `_freeSeats` is rebuilt from a wiped `_oppHeld` while `left` still
  counts only unheld dice → seats exceed count → the first N seats are the
  *held* ones.

The brief already scoped the rival-side rework around the seven `left` writers
(there are ten — 27870, 27939, 27966, 27969, 27971, 28003, 28016, 28824, 28827,
28839; and the previously-tabled row at "28027" does not exist: 28032 assigns a
separate local `rollDice`, and `left=Math.min(left,5)` at 27969 is Whisper's
Veil, not a first-roll cap). This sweep says the writers are the symptom, not
the disease. **The helper is not "derive `left` correctly" — it is "one function
computes the seats and the count together, from `matchOppDice` + `_oppHeld` +
`_snuffLane`, and every deal point calls it."** Then `left=6` and the
`_freeSeats[i]!==undefined` fallback both stop existing. `_oFullHand` is the
existing correct fragment, at one of ten sites — the same "the right shape
exists and didn't travel" story as the decrement rule, in a second place.

D13 (Blessed Confiscation's seventh seat) falls out of this too, and does not
need it: the recommendation in the brief — swap rather than push — still stands
as the cheaper close, and this sweep strengthens it by showing seat 6 is
*unconditionally* unreachable.

### 5c. `_setLaneMat(lane, mat, ench)` — the brand must move with the die

Four live sites write a lane's material and leave `_enchArr` behind:
`fair_trade` 12992 (**D10a**), `swap_die` best_for_worst 24620 and
downgrade_best 24634 (**D11**), and `sleight_of_hand` 29343 (dead). Two more do
it on the run arrays: the tier loadout drag 34917-34919 and `_buyDieAtSlot`
33954 (both dead surfaces). **The correct implementations already exist, twice**
— Trade (18415/18432/18444, which moves the brand out and ledgers it),
`_stTrade` (33287-33288, `S.run.dieEnch[slot]=null`), and `famDieShift`
(14864-14869, which swaps `dieEnch` alongside `dice` and **has zero call
sites**). Three correct references and four wrong sites is the exact ratio that
produced `_dropLanes`.

This also wants a **ruling** alongside the helper: Trade nulls the brand on a
swap, `swap_die` keeps it. Two same-seat swaps, opposite rules, neither written
down.

### 5d. A rule, not a helper: re-derive from `G.pool` inside the timeout; never capture `free`

Steady Hand (12949-12950) and Powder Keg (14268) both score an array captured
before a 500 ms window in which removers stay legal (**D4**, **D5c**). The
correct shape already exists at **24765**, which re-derives `free2` from
`G.pool` inside the timeout. Adding `CFX.sacrifice` and `_removeDieAt` to
`_steadyDisarm`'s five callers would patch today's pair and leave the next
remover to rediscover it — which is exactly the failure `_dropLanes` was built
to stop. `_steadyDisarm` should shrink, not grow.

### 5e. Not worth a helper

- **D15 (`reduce_first_roll`)** — a single site, and its remedy is a design
  decision, not a rule. Do not fold it into `_dropLanes`; it is not that shape.
- **D6 (Preserve's lane)** — one site needs one new field on the record. The
  *brand* half (D6b) belongs to 5c.
- **D7 (the roll-forces buffer)** — two flags in one function; clear them in
  `startPTurn` beside `G._wardArmed` at 24434, which is where every other
  per-turn flag already dies.
- **D12/D19 (Vagabond)** — D12 is a one-line cache invalidation the codebase
  already performs at 22029-22032; D19 is a **ruling** first and a patch second,
  and the patch depends on which way the ruling goes.
- **D24 (`startPTurn`'s reset ordering)** — the general hazard that anything
  added *above* line 24426 is silently wiped is worth a **comment at 24426**,
  not a helper. `_oTarPit` at 24418 is the existing casualty; Whisper's Hex at
  24531 is the working control nine lines the other side of it.

---

### Probes from this sweep

All marked `SUITE: exclude`, so `run_probes.js` ignores them. Run pattern:
`node tools/shoot.js --url http://localhost:8084/fark_proto.html --eval-file tools/<probe>.js --out <scratch>.png`

**Cross-reference verification (this pass):**
`tools/apv_xref_sac_empty.js` — D8, driven end to end: the walk down to one die,
Break's floor holding, Sacrifice emptying `matchDice`, the `lane: NaN` mint, the
un-removable die, and what the next three turns deal.

**FAM layer:** `tools/apv_famsweep_inventory.js`, `apv_famsweep_ft_ench.js`,
`apv_famsweep_sac_loan.js`, `apv_famsweep_stargazer.js`,
`apv_famsweep_steady_stale.js` *(note: its verdict predicate is unsound — see
D4)*, `apv_famsweep_keg_numdice.js`, `apv_famsweep_preserve_lane.js`,
`apv_famsweep_sac_snapshot.js`, `apv_famaudit_anyscoring.js`,
`apv_famaudit_steady_redo.js`, `apv_famaudit_keg_window.js`,
`apv_famaudit_stale_flags.js`, `apv_famaudit_loan_upgrade.js`.

**Gestures:** `tools/probe_gesture_vg_taps.js`, `probe_gesture_vg_persist.js`,
`probe_gesture_vg_consequences.js` *(computes seat order from chip rects — the
instrument D12 disowns; re-derive from mesh before acting on its numbers)*,
`probe_gesture_vagabond_drag.js`, `probe_gesture_vg_committed.js`,
`probe_gesture_vg_shot.js`, `probe_gesture_loadout_drag.js`,
`probe_gesture_lo_reach.js`, `audit_gesture_mesh.js`, `audit_gesture_reach_a.js`,
`audit_gesture_reach.js`, `audit_gesture_chisel.js`, `audit_gesture_vagreach.js`,
`audit_gesture_scope.js`.

**NPC, enchants and tells** were driven from probes under the session scratchpad
rather than `tools/`; the load-bearing measurements are quoted inline above and
the arrangements are stated well enough to rebuild them.

### Instrument hazards recorded, each earned

- **`afterRoll` (25169) is a 515-character wrapper**; the body is
  `_afterRollImpl` (25183). `String(afterRoll).match(/G\.numDice\s*=/g)` returns
  `[]` — every "read off the live function" claim aimed at `afterRoll` is a
  false zero. Two passes hit this.
- **A probe that reimplements the code it is testing proves nothing.**
  `apv_famsweep_sac_loan.js:86-92` reimplemented startPTurn's expiry test; the
  conclusion survived only because 24452-24455 happens to be identical.
- **A verdict predicate is part of the instrument.** D4's original evidence
  failed on the predicate, not on the path: it tested for 1s and 5s and was
  blind to triples, so a scoring table was reported as non-scoring.
- **Chip rects are not die positions** after a Vagabond drag (D12). Two findings
  were computed from them; one happened to survive.
- **`G._snuff` set by hand will not fire** — `G.oppTurnCount` increments at
  27978, *before* the snuff check at 27997, so `_lmArm` is the only correct
  arming API.
- **Sampling once is not measuring.** D8's end state read as a hard soft-lock at
  1.5 s and had resolved to a normal idle turn by 9 s. The defect is "unwinnable
  match", not "frozen game", and only the second sample says so.

---

# THE SAFETY-COMMENT AND BRAND-TRAVEL SWEEP — static, nominations only

**Nothing in this whole part was executed.** It is static reading against
`pinned_e5b7705.html`, a copy of `fark_proto.html` taken at commit e5b7705
because the live file was being patched concurrently. No browser, no server, no
`tools/shoot.js`. Every item below is a **nomination**: the verbatim code, the
lines, the arrangement that would expose it, and what a probe must read to
settle it either way. Nothing here is a verdict, and nothing here may be cited
as "checked". §5 lists, in priority order, which ones most need driving.

**The pinned copy predates P519 and P520.** The highest patch marker in it is
P518 (14263). `CFX.sacrifice` still hand-rolls its own splice at 14322, the
refill still carries the overflow fallback at 25141, `CFX.sacrifice.canUse`
(14290) still has no floor, and `_commitVagabondDrag` (36662-36699) still moves
only `phys.x`, `G.pool` order and the DOM row — never `d.lane`, `G.matchDice`
or `G._enchArr`. So the fixes §5a and D12 record as shipped are **not in what
was read**. Every nomination whose mechanism one of those two patches closes is
marked **SUPERSEDED-CHECK** and must be re-read against the live file before
anyone acts on it. This is "check the input, not just the method" applied to a
sweep's own source: the method was fine and the file was nine commits stale.

**Line numbers.** All anchors below are `pinned_e5b7705.html`. Against this
document's existing `fark_proto.html` anchors the offset is **0** in the
12000s, about **+9** from 19000-24700, and about **+11** from 25100-28900. It
is not constant. Re-anchor by grepping the quoted text; never by adding a
number.

**Counts.** 60 candidates were raised and put to an adversarial reader.
**20 survived**, **31 were refuted** (§4), **9 were never judged** (§5).

---

## SAFETY CLAIMS THAT MAY NOT HOLD

Denis's ruling: this class is worse than the bugs. A comment invites the next
reader to trust it instead of re-checking, and that is the exact mechanism that
let the decrement-vs-recompute lesson sit unapplied for 5,000 lines while it was
needed twice more. Ranked by danger — how load-bearing the false assertion is,
how likely a reader is to hit it, and whether anything downstream is already
built on it.

### S1. "which startPTurn's baseline makes unreachable today" — sitting on the expression this document already measured minting a `lane: NaN` die

> **CLOSED — P519 (the guard) + P523 (the false comment).** The refill refuses a non-index lane and `matchDice` cannot reach length 0; the "unreachable today" claim is replaced with what is actually true.

`pinned_e5b7705.html:25136-25141`
```js
        /* overflow fallback: needNew beyond the free-lane count means
           numDice > matchDice.length, which startPTurn's baseline makes
           unreachable today and only the retired Seven Dice could cause.
           Holding the old expression there keeps that case byte-identical
           rather than inventing behaviour for it. */
        const _lane=(_freeLanes[i]!==undefined)?_freeLanes[i]:((G.pool.length+i)%G.matchDice.length);
```

**What it asserts.** That the `else` arm is unreachable in the shipped build,
and that keeping the old expression there is therefore inert.

**Why the expression cannot deliver it.** The unreachability argument reasons
only about `numDice` being pushed *above* `matchDice.length`. It never considers
`matchDice.length` being pushed *down to 0*. `_freeLanes` is built at 25134:
```js
      var _freeLanes=[];for(var _fl=0;_fl<G.matchDice.length;_fl++){if(!_occLane[_fl])_freeLanes.push(_fl);}
```
At `matchDice.length===0` that array is empty, every iteration takes the else
arm, and `(0+0)%0` is `NaN`. **This document already measured that state** —
D8, `poolLanesAreNaN [true]` — and the comment above the line says it cannot
happen. That is D8's own mechanism with a comment vouching for it.

**One correction to my own nomination, in the comment's favour.** I claimed
"the retired Seven Dice" was a live line because 24800 still executes:
```js
  if(G._sevenDiceArmed){
    G._sevenDiceArmed=false;
    G.numDice=Math.min(G.numDice+1,7);
```
The only writer of `G._sevenDiceArmed` is **31480**, inside `activateSevenDice`
on the dead `pCards` layer. The comment is *right* that Seven Dice is retired.
It is wrong about unreachability for a reason it never considered.

**The arrangement that would prove it.** Walk the loadout to one die through the
shipped removers (Break / obsidian shatter / royal_seizure), confirm
`_breakBegin` refuses the last die, then spend one Sacrifice charge so
`G.matchDice` is length 0 with `G.numDice` 1. Tap `#btnRoll` — it is a `DIV` at
8930, so the `disabled` class cannot block the tap — and let the refill run one
iteration.

**What a probe must read.** Immediately after the refill: `G.matchDice.length`,
`G.numDice`, `needNew` latched before the loop, `_freeLanes.length`, and for
every `G.pool` entry the tuple `{lane, Number.isNaN(lane), mat, val}`. Then call
`_removeDieAt(thatLane)` and re-read `G.pool.length` and the return value.

**SUPERSEDED-CHECK.** P519 is recorded as adding "a refill that will not stamp a
lane that is not a real index". If that landed, the NaN arm is closed live and
**the comment is the residue** — re-read 25136-25141 against the live file and
either delete it or make it say what is actually true.

### S2. "This is the whole fix" and "all six scored" — two comments in one function, and the else arm of the fix is the bug the comment names

These are duals of one root cause and are merged here. This is the doc's
existing D1/D2 seat-vs-count disease (§5b), catalogued for the first time as a
*comment* problem.

`pinned_e5b7705.html:28060-28065`
```js
    /* WHICH SEATS ARE ACTUALLY FREE. Everything the rival is still holding sits
       in a seat, and the snuffed seat is empty for the turn - so the dice about
       to be thrown go into what is left, in seat order. This is the whole fix:
       the loop below used to index materials and lanes by ITS OWN counter, which
       is the position of a die within this roll and has nothing to do with the
       seat it lives in. */
```
`pinned_e5b7705.html:28079-28080`
```js
      const _seat=(_freeSeats[i]!==undefined)?_freeSeats[i]:i;
      const dieMat=_rungAll[_seat]||rungDice[i]||'bone';
```

**What it asserts.** That indexing by seat rather than by loop counter is
complete — that a die can no longer take its seat from its position within the
roll.

**Why the expression cannot deliver it.** The else arm is `i`: the loop counter,
which the comment names as the defect. It is taken whenever
`i >= _freeSeats.length`, i.e. whenever `rollDice > _freeSeats.length`. Those
two quantities have different derivations and nothing reconciles them —
`rollDice` descends from `left`, `_freeSeats` from `_rungAll.length` minus
`_heldSeats` minus `_snuffLane` (28069-28073). A guard whose failure branch is
the original bug is a fix plus a fallthrough, and the comment claims a
completeness the ternary cannot provide. `dieMat` at 28080 falls back further to
`rungDice[i]`, a second counter-indexed source.

`pinned_e5b7705.html:28835-28838`
```js
      left=G.oppDice.filter(d=>!d.kept).length;
      /* all six scored: the next step deals a whole new row, so the held
         dice go with the old one */
      if(left===0){G._oLastHotDice=true;G._oppSweep=true;left=6;setTimeout(step,_oppDelay(1500));return;}
```

**What it asserts.** That `left===0` means all six of the rival's dice scored,
so resetting to the literal 6 restores the hand that was swept.

**Why the expression cannot deliver it.** `left` is recomputed one line above
from `G.oppDice`, which only ever received `rollDice` entries. `rollDice`
descends from a `left` that snuff, jinx, Whisper's Hex, Veil, the pickpocket
tell, Leaky Cup and Pocket Sand have all already written. So `left===0` means
"every die *in the last roll* was kept", not "all six". The literal 6 then
disagrees with `_freeSeats`, and in the other direction `_rungAll` is
`G.matchOppDice`, which `blessed_confiscation` pushes to length 7 at 24691 — so
"six" is wrong high as well as low. **A max cannot cap and a literal cannot
derive.** Together with S2's fallback: the literal supplies the excess count and
the fallback absorbs it into an invented seat.

**The arrangement that would prove it.** A rival with six distinct materials and
a live Snuff on a middle lane, driven until the rival keeps every die of a roll
and sweeps; a second arm with the snuff on the last lane; a control with no
snuff. (This is D1's measured arrangement — the new thing to read is the
*comment*'s claim, not the seat list.)

**What a probe must read.** Inside `step()` on the roll after the sweep, latched
at the deal loop: `left`, `rollDice`, the whole `_freeSeats`, `_snuffLane`,
`_rungAll.length`, and per iteration `i`, `_freeSeats[i]`, the resolved `_seat`,
whether the else arm was taken, and `_rungAll[_seat]` against `rungDice[i]`.
Plus `#oppDiceRow` children's `dataset.seat`.

### S3. The same rival hot-dice line, hand-copied 14,800 lines away, documented as "GUARANTEED" — with a numeric AI table built on the reading

> **CLOSED — P525, driven.** Prioritised by Denis on the ground that this is the
> one where something is *already standing on* the wrong reading rather than it
> merely misleading a future reader.
>
> **Two claims; P521 killed one and left the other standing.**
> - *"GUARANTEED to roll again"* — **still true.** The `return` still fires
>   before `oppShouldBank`. Kept, and now marked in-source as the half that holds.
> - *"A fresh six is dealt"* — **false since P521.** A sweep clears the held dice
>   but not the snuff, so the rival can be dealt five, and the table was reading
>   `bust[6]`/`gain[6]` for a five-die roll — the wrong row of a *measured*
>   table, in the one persona that actually calculates.
>
> Fixed in the shape ruled three times tonight: not a second computation but one
> published value. `G._oSnuffLane` carries the turn's snuffed seat,
> `_oHandAfterSweep()` answers it for readers outside `runOppTurn`, and `_oSeats`
> now reads the published value rather than the local it closed over — the same
> number before, the same *source* now.
>
> | loadout | snuff | hand | |
> |---|---|---|---|
> | 6 | none | 6 | OK |
> | 6 | lane 2 | 5 | OK |
> | 6 | lane 5 | 5 | OK |
> | 6 | lane 9, out of range | 6 | OK — does not subtract |
> | 3 | lane 1 | 2 | OK |
> | 1 | lane 0 | 1 | OK — floor |
>
> Plus the live path, because the arithmetic is worthless if the value is never
> published: a **real snuffed rival turn** published lane `3` and the helper
> returned `5` while it was live.

---

## RETRACTED: THE "TRIM AND DISCARD" FINDING WAS PICKPOCKET'S PALM

Recorded at the top of the open items as the most urgent thing outstanding —
"a real, player-owned die vanishes with nothing on screen explaining why" — and
**it is not a defect.** Traced, as ruled, before anyone touched it.

**What it actually is.** `_maybeFireCutpurse` splices the victim from `G.pool`
and calls `_dropLanes(1)`, both inside a `setTimeout` for the palm's flight
animation. That produces exactly the fingerprint that looked alarming: one pool
entry gone, `numDice` down one, `matchDice` unchanged, about a second after the
deal. The rival is stealing a die. It is supposed to.

**Confirmed against a control rather than from the fingerprint**, because a
matching signature is not proof:

| arm | palm fired | pool dropped | final lanes |
|---|---|---|---|
| pickpocket tell present | **2×** | yes, at 2311ms | — (turn ended) |
| no tell | **0×** | **no** | `[99,0,1,2,3,4,5]` — phantom *and* all six seats intact |

With the tell absent the pool does not shrink at all and the phantom sits there
untouched. The palm is the whole effect.

**Why I got it wrong.** The fixture ran a tier-2 boss, which carries the
pickpocket tell, and I read a delayed, designed removal as a mystery. The
phantom "surviving while a real die is discarded" was the palm choosing a real
die — which is correct, and in real play there is no phantom to choose instead.

**What this cost:** it was carried for several exchanges as the top open item
and shaped the priority order. **What it did not cost:** a patch. The rule that
produced that outcome — trace the mechanism before guessing at a fix — is the
only reason a designed rival effect was not "fixed" out of the game.

**One thing it leaves genuinely open**, much smaller: nothing sweeps an
un-shattered pool entry whose lane is not a real seat. P528 sweeps shattered
ones. No producer of such an entry is known in live play (P519 guards the mint
site, and 143 samples in the S5 gate saw none), so this is latent and stays
labelled latent.


## THE RUNNING LIST OF FALSE CLAIMS — THREE SHAPES, KEPT SEPARATE

Ruled by Denis: these are different mistakes with different fixes and must not
collapse into "another wrong comment".

1. **A bound reasoned in only one direction.** P517's "the loadout term stays so
   a stale-low numDice cannot strand them below their real lane count" — the
   ceiling of a `min`, which cannot floor anything. P523's "unreachable today" —
   argued from `numDice` going up, while the route taken was `matchDice.length`
   going down to zero.
   **Standing check:** does this hold in the direction nobody checked?
2. **A symmetry claim never checked against its target.** P524's "mirrors player
   `_runSave`" — `_runSave` keeps every committed die and says so; the rival
   cleared the whole row. Checkable in seconds *because* it names something
   concrete, which makes it worse that nobody had.
   **Standing check:** does this comment's claim about another function hold?
3. **A transcript that stopped tracking its source.** P525's hand-copied
   `left=6`, still quoted 14,800 lines away after P521 changed the line, with a
   scoring table built on the stale half.
   **Standing check:** does any comment quoting code still match that code?


`pinned_e5b7705.html:13992-13997`
```
       L===0 IS HOT DICE, now read rather than assumed. runOppTurn:
         if(left===0){G._oLastHotDice=true;G._oppSweep=true;left=6;
                      setTimeout(step,...);return;}
       A fresh six is dealt - and that `return` fires BEFORE oppShouldBank, so
       hot dice also skips the bank decision entirely and the rival is
       GUARANTEED to roll again. It is the best outcome on the board.
```

**What it asserts.** A fresh six, a guaranteed extra roll, and the best outcome
on the board — and it is the stated basis for scoring `L===0` at the top of the
`combo` persona's `value = pts + (1 - bust[L]) * gain[L]` table rather than at 0.

**Why it cannot deliver it.** "A fresh six is dealt" is the premise S2 refutes.
It is also a *copy*, and therefore free to drift from the line it quotes — it
already elides the delay argument as `...`. A comment that both asserts a
guarantee and is the declared input to a numeric table is the worst-case shape
of this class: the table cannot be re-derived without re-deriving the prose.

**The arrangement that would prove it.** S2's snuff arrangement, but reading the
rival's *decision* rather than its dice. Separately: a character-by-character
diff of 13992-13994 against 28838.

**What a probe must read.** The `combo` persona's computed `value` for the
`L===0` candidate, the `bust[L]`/`gain[L]` entries it used, then
`_freeSeats.length` and the distinct-seat count of `G.oppDice` on the post-sweep
roll, and `G.matchOppDice.length`.

### S4. "nothing is duplicated and nothing is skipped" — over a single-slot field, with two consumers

> **CONFIRMED then CLOSED — P526.** The audit's top priority, and the only
> nomination whose mechanism no shipped patch touched. Driven **before** the fix,
> which is the order that matters:
>
> ```
> first fire     pending points at: die0
> second fire    pending points at: die1
> brand fires 2 | breaks started 1 | first overwritten TRUE
> ```
>
> "Nothing is skipped" was false. `fire` **assigned** a single slot while
> `_iconFire` runs once per committed die and the consume is a single `if`
> after the loop.
>
> **A queue alone would not have been enough**, and that is the interesting part.
> `_breakBegin` opens a targeting UI and its callers `return`, so a second Break
> has nowhere to run until the first resolves. The fix needed a **drain point**:
> `_breakDie`, after the table is rebound.
>
> The drain is **skipped when the Break ended in a bank**, deliberately —
> Silver's row cashes out on a timer, and opening a new targeting prompt under a
> bank that is already ending the turn would have the player choosing a target
> for a turn that is over. The turn reset clears the queue, which is what has
> always happened to a brand that did not fire.
>
> A queued Break with **no legal target is skipped rather than stalling** the
> ones behind it — `_breakBegin` returning false means "nothing left to break",
> which must not block a Break that does have a target.
>
> **After:** queue length 1 then 2, both brands seen, **two** `_breakBegin` calls.
>
> *Scope, stated:* the probe calls `_iconFire` directly — the same call the commit
> loop makes per die. A real two-skull commit through the UI was not driven.

`pinned_e5b7705.html:24949-24956`
```js
  /* BREAK takes its target here - AFTER the commit has fully run, so nothing
     is duplicated and nothing is skipped, and BEFORE the row is rethrown, so
     the tap handlers survive. _breakBegin returns false when there is nothing
     left to break, and the turn simply carries on. */
  if(G._breakPending){
    var _bp=G._breakPending;G._breakPending=null;
    if(_breakBegin(_bp.src))return;
  }
```
against `pinned_e5b7705.html:18397`
```js
    fire:function(c){G._breakPending={src:c.die};}},
```

**What it asserts.** That deferring Break to after the commit makes it exact —
no double-fire and no lost fire.

**Why the expression cannot deliver it.** `G._breakPending` is a **single-value
slot, not a queue**. Two branded faces firing during one commit means the second
`fire` overwrites the first and one Break is silently skipped — precisely the
half the comment denies. Break has no per-loadout ownership cap: 33727 gates
only `if(k==='ward'&&_wardOwned(i))`, and `_wardOwned` (33417) is ward-specific,
so a loadout may carry two Break brands. `_iconFaces` (33389) restricts brands
to faces 1 and 5, both scoring faces, commonly committed together. The same
single slot is consumed from **two** places — 24953 and 26840, the bank path
whose own comment reads "Only handleRoll read _breakPending, so banking a skull
armed it".

**The arrangement that would prove it.** Break branded on two different dice,
both on faces the same commit can carry; roll until both show their branded face
and commit both in one selection. Variant: one skull committed on a roll, the
second on the next roll before the first was consumed.

**What a probe must read.** A counter instrumented on 18397 counting `fire`
invocations per commit; `G._breakPending` after each; the number of
`_breakBegin` entries; and `G.matchDice.length`, `G._diceOut.length` and
`G.numDice` before and after. **Two fires against one `_diceOut` entry is the
finding.**

### S5. "remove each shattered die by seat" — the list drops every shattered die that has no valid lane, and the else that would catch them cannot run

> **CLOSED — P528, both arms. Denis's gate was run first and it changed how one
> arm is described, not whether it was fixed.**
>
> **The gate: is a duplicate-lane producer still live post-P519?** Measured over
> **143 live pool samples** across four turns and sixteen rolls: **zero
> duplicates.** So the duplicate arm is **latent, not live**. 143 samples is
> absence, not impossibility — the overflow fallback still computes a modulo and
> nothing else dedupes — so it is fixed as cheap insurance rather than as an
> emergency, and labelled that way.
>
> **Arm one, the duplicate — real, and worse than "a seat removed twice".**
> A sort protects against *shifting*, not against duplicates.
>
> | | before | after |
> |---|---|---|
> | `_shLanes` | `[2,2]` | `[2]` |
> | matchDice | `[bone,iron,flint,lead,amber,brass]` | was `[bone,iron,amber,brass]`, now `[bone,iron,lead,amber,brass]` |
>
> Seat 2 held flint. Flint died — and so did **lead**, the neighbour that
> inherited seat 2 after the first splice. One shatter destroyed two dice.
>
> **Arm two, D24 — still live after P519, now closed.** The `>=0` filter drops a
> laneless shattered die from `_shLanes`, and the sweep that should catch it ran
> only when `_shLanes` was **empty**, so a *mixed* batch stranded it in the pool
> with its element already removed upstream — an invisible die that still counts.
> Driven: `_shLanes [0]`, one stranded. Now unconditional: zero stranded.
>
> **Two instrument notes, both self-inflicted and both worth recording.** The
> comment-stripping assertion helper introduced in P526 is a naive regex and
> mis-pairs `/*` against strings elsewhere in a 2 MB file — the same
> proxy-for-the-real-thing trap, one level up in the tooling. And the guard
> assertion asserted `== 1` when P520's Vagabond code legitimately uses the
> identical expression, so the count is 2. Neither was a defect in the patch;
> both cost a round trip.

`pinned_e5b7705.html:25289-25295`
```js
    /* remove each shattered die by seat, highest first so earlier seats stay
       valid while we go */
    var _shLanes=G.pool.filter(function(d){return d._shattered;})
      .map(function(d){return d._shatterLane!==undefined?d._shatterLane:d.lane;})
      .filter(function(L){return L!==undefined&&L>=0;}).sort(function(a,b){return b-a;});
    if(_shLanes.length)_shLanes.forEach(function(L){_removeDieAt(L,{permanent:false});});
    else G.pool=G.pool.filter(d=>!d._shattered);
```

**What it asserts.** That every shattered die is removed, and that descending
order keeps the remaining seat numbers valid.

**Why the expression cannot deliver it.** Two gaps in the word "each".
(1) `_shatterLane` is set to `-1` when `d.lane` is undefined (25283
`d._shatterLane=(d.lane!==undefined?d.lane:-1);`) and the `.filter(L=>L!==undefined&&L>=0)`
then drops it, while the `else` that would sweep it out of `G.pool` runs only
when `_shLanes` is *empty* — so a mixed batch leaves a laneless shattered die in
the pool with its element already removed at 25275. **This is D24, and it is
already measured** (`poolShattered:1`, lanes `[0,1,undefined,3,4]`).
(2) **New, and not in D24:** `.sort` descending protects against *shifting*, not
against *duplicates*. If two pool dice share a lane — which S1's fallback
produces — the same seat is handed to `_removeDieAt` twice and the second call
destroys an innocent neighbour. **A sort cannot dedupe.** S1 and S5 chain: S1
mints the duplicate, S5 spends it.

**The arrangement that would prove it.** Two obsidian (or grogs_tooth) dice
driven until both shatter on the same roll, one holding a lane and one with
`lane` undefined. Second arm: two pool dice sharing one lane, both shattering.

**What a probe must read.** Before the sweep, every pool entry's
`{lane,_shattered,_shatterLane,mat,val}`. After: the built `_shLanes`, any
`_shattered` entry still in `G.pool`, whether it has a live `el` in
`#playerDiceRow`, `G.matchDice`, `G._enchArr`, `G.numDice`, and whether it still
scores in the next `anyScoring`.

### S6. "G.pool cannot drift from G.pool" — the code does not compare G.pool with G.pool

> **CLOSED — P529, driven.** The tautology was about `G.pool`; the code compared
> a **set** with a **count**. `needNew` was `G.numDice - G.pool.length`, raw
> entries, while the lanes it feeds come from `_occLane`, keyed by lane — so
> duplicates collapse and `undefined`/`NaN` become string keys marking no seat.
> An entry occupying no seat still suppressed a refill, and a genuinely empty
> seat went undealt.
>
> **Fixed as the shape P521 used on the rival, applied to the player:** `needNew`
> counts **distinct valid seats**, and the deal loop is clamped to
> `min(needNew, _freeLanes.length)`. The two are now views of one set, and the
> clamp makes the overflow modulo unreachable rather than merely guarded — which
> is what P523's corrected comment says it should be.
>
> | arm | seeded | after the deal | seats |
> |---|---|---|---|
> | clean control | `[0]` | `[0,1,2,3,4,5]` | 6/6 |
> | lane out of range | `[99]` | `[99,0,1,2,3,4,5]` | 6/6 |
> | lane undefined | `[undefined]` | `[undefined,0,1,2,3,4,5]` | 6/6 |
>
> **RETRACTED — IT WAS NOT A DEFECT. See the correction directly below.**
>
> **NEW, found by this probe and NOT fixed — recorded rather than folded in.**
> The phantom entry survives the deal, and something later trims the pool back
> to `numDice` and evicts a **real** die: measured `[99,0,1,2,3,4,5]` at 430ms,
> `[99,0,1,2,3,4]` at 1300ms — seat 5's die gone while the lane-99 phantom
> stayed. Two questions this raises, neither answered: what performs that trim,
> and what (if anything) is supposed to sweep a pool entry whose lane is not a
> real seat. P528 now sweeps *shattered* laneless dice; nothing sweeps
> un-shattered ones. Not fixed blind — a pool entry may legitimately lack a lane
> on a flow I have not traced.
>
> **Two instrument faults, both mine, both recorded.** The first probe ran three
> arms in one browser session and the later two measured a pool of 0 — a shared
> fixture that degrades between arms reports the fixture, not the code. Fresh
> launches per arm did not fix it either; only **one arm per browser session**
> did. And it sampled 1100ms after the deal, which would have scored the
> separate late-trim defect as this fix failing.

`pinned_e5b7705.html:25130-25134`
```js
         Occupancy is read from G.pool itself because the whole defect is
         numDice and the pool disagreeing; G.pool cannot drift from G.pool.
         Mirrors _removeDieAt (19143-19144), the reference on the remove side. */
      var _occLane={};(G.pool||[]).forEach(function(_d){_occLane[_d.lane]=1;});
      var _freeLanes=[];for(var _fl=0;_fl<G.matchDice.length;_fl++){if(!_occLane[_fl])_freeLanes.push(_fl);}
```

**What it asserts.** That deriving occupancy from `G.pool` is self-consistent by
construction and cannot desync.

**Why the expression cannot deliver it.** The tautology is about `G.pool`; the
code compares a **set** with a **count**. `_occLane` is keyed by lane —
duplicates collapse, and `undefined`/`NaN` become the string keys `"undefined"`
/ `"NaN"` and mark no numeric lane — while `needNew` at 25071 is
`G.numDice - G.pool.length`, a raw count. A set and a count are two different
measurements of the same array and they diverge the moment any entry has a
duplicate, undefined or NaN lane, both of which this cluster is known to
produce (S1, S5). When they diverge `needNew` is smaller than `_freeLanes.length`
and a genuinely empty lane is never refilled — the die "sits out" the turn,
which is the same visible symptom D6 reports for Preserve from a different
cause. Separately, `_freeLanes`' loop bound is `G.matchDice.length`, so a pool
die standing at or above that bound is invisible to the occupancy test entirely.

**The arrangement that would prove it.** Two pool entries on one lane (via S1),
or one entry with `lane` undefined (via S5), then roll and count the lanes
dealt. Second arm: a pool die whose `lane` is `>= G.matchDice.length` after a
splice, then roll.

**What a probe must read.** Latched at the top of the refill: `G.numDice`,
`G.pool.length`, `G.pool.map(d=>d.lane)`, `Object.keys(_occLane)`, `_freeLanes`,
`needNew`, `G.matchDice.length`. Then which lane indices actually carry a die in
`#playerDiceRow` and which `matchDice` index was dealt none.

### S7. "the two can never disagree" — two readers of one expression agreeing is correlated failure, and it is stated here as a safety property

> **Arm (a) SUPERSEDED by P519; arms (b) and (c) CLOSED by P530.** Every seat-shrinking writer now maintains the loan, and an out-of-range loan protects nothing.

`pinned_e5b7705.html:19039-19045` and `19049-19059`
```js
   THE SEAT TEST IS THE ONE startPTurn'S LOAN-EXPIRY BLOCK ALREADY USES -
   matchDice[lane] still holding ft.borrowed - so the two can never disagree
   about whether the loan is still standing in its lane.
...
function _breakBorrowed(d){
  if(!d||!G)return false;
  try{
    var ft=G._fairTrade;
    if(!ft||ft.lane===undefined||ft.lane===null)return false;
    if(_laneOf(d)!==ft.lane)return false;
    if(!G.matchDice||ft.lane>=G.matchDice.length)return true;
    return G.matchDice[ft.lane]===ft.borrowed;
  }catch(e){}
  return false;
}
```

**What it asserts.** That sharing one expression with startPTurn's expiry check
makes the two consistent, and therefore that a borrowed die can never be an
illegal Break target.

**Why the expression cannot deliver it.** Agreement between two readers of one
expression is not correctness; it is **correlated failure**, and both inputs are
known-unstable. (a) `ft.lane` is shifted by `_removeDieAt` (19205
`if(ft.lane>lane)ft.lane--;`) but not by `CFX.sacrifice`, which splices
`matchDice` itself at 14322 and names `_fairTrade` nowhere — **D9**. After a
sacrifice below the loan both readers point at the wrong seat *and agree with
each other*. (b) `ft.borrowed` is a **material string**, so
`matchDice[ft.lane]===ft.borrowed` is satisfied by any die of that material —
**D10(b)**. (c) The `ft.lane>=G.matchDice.length` arm returns `true`, so on a
shrunk loadout the last seat's die is permanently un-breakable. This is
"convergence can be an artifact" written into a source comment as a guarantee.

**The arrangement that would prove it.** A loadout whose weakest seat is a
middle lane, so `worst` is not 0 — an all-bone loadout hides this entirely.
Borrow into lane 2, sacrifice lane 1, then attempt a Break on the die now
standing in lane 2 and on the die now standing where the borrowed die actually
is. Second arm: a loan whose `borrowed` material duplicates a die the player
already owns.

**What a probe must read.** Per candidate die: `_laneOf(d)`, the whole
`G._fairTrade`, the whole `G.matchDice`, what `_breakBorrowed(d)` returns, and —
evaluated separately on the same state — startPTurn's expiry predicate. Then
whether `_breakBegin` offered the die and whether `_breakDie` accepted the tap.
After the turn boundary, `G._ftDead` and `S.run.diceInv`.

**SUPERSEDED-CHECK on arm (a) only.** If P519 routed Sacrifice through
`_removeDieAt`, 19205 now runs and `ft.lane` stays true. Arms (b) and (c) are
untouched by P519.

> **ARMS (b) AND (c) CLOSED — P530, driven. And the audit's mechanism for (b)
> was wrong, which is worth recording rather than quietly correcting.**
>
> `_breakBorrowed` gates on the **lane first** (`if(_laneOf(d)!==ft.lane)return
> false;`), so "any die of that material is protected" cannot happen on its own —
> the material test is only ever reached for a die already standing in the loan's
> seat. The real mechanism is that **nothing maintained the loan's seat**:
>
> | seat-shrinking writer | maintained `_fairTrade.lane`? |
> |---|---|
> | `_removeDieAt` | yes |
> | Vagabond reorder | **no** — a gap P520 left when it made the reorder real |
> | Blessed Confiscation (two direct splices) | **no** |
>
> Reorder the row and the loan protects whichever die moved *into* the seat it
> used to hold. Shrink the loadout past the recorded lane and arm (c)'s
> `return true` protects a die on the strength of a record pointing at nothing.
> One root cause, filed as two arms.
>
> **Fixed as the canonical path for the sixth time.** Confiscation now routes
> both modes through `_removeDieAt`, which hands it the loan shift, the trade
> ledger shift, the `_diceOut` record, the one-die floor and the mid-turn
> snapshot — none of which it had. Its hand-rolled splice, `_dropLanes` and
> `_enchArr` splice are gone, exactly as Sacrifice's were in P519. The rival now
> only receives a die the player actually **lost**, since `_removeDieAt` can
> refuse and transferring on a refusal would duplicate the material rather than
> move it. The Vagabond reorder carries the loan's seat. And an out-of-range
> loan returns **false** — the backstop, not the fix.
>
> | arm | result |
> |---|---|
> | reorder | loan lane 2 → 1, still on its own die, seat holds obsidian |
> | removal below the loan | lane 4 → 3, seat holds obsidian |
> | one-die floor | held |
> | out-of-range loan | protects nothing |
>
> **One fixture fault, mine.** Arm A first reported FAIL because it set
> `matchDice[2]='obsidian'` while the die standing there still had `mat:'flint'`
> — a state real play cannot produce, since P520 deliberately takes the material
> from the **die** (what is painted). The fix wrote the true material back and
> the arm scored it as a failure. An internally inconsistent fixture tests
> nothing.

### S8. "no exceptions, no residue" and "the index does not have to be right for the repair to be" — the two halves of the restore are not gated together

> **CLOSED — P527. Denis asked the framing question before any code was written:
> a new check alongside the count, or "count of what died" becoming "identity of
> what is in each seat now"? It is the second, and the codebase already proved
> it — for the other record.**
>
> ```
> _removeDieAt shifts G._fairTrade.lane   TRUE   (ft.lane--)
> _removeDieAt shifts G._tradeSwaps.lane  FALSE
> anything else shifts it                 FALSE
> ```
>
> One lane record was maintained across removals and its sibling was not. The
> `have===t.cnt` comparison was never a safety check — it was an attempt to
> **guess back an index that was never kept**. Tightening it would have improved
> a reconstruction of information the code could simply have retained. Same
> counting-to-identity shift as P512.
>
> **A flaw in the first version of this fix, caught before driving it.** `t.lane`
> indexes **both** boards, but a player-side removal renumbers only the player's
> seats. Shifting the one lane fixed the player's repair and would have broken
> the rival's — the fix for one side breaking the other. The ledger now records
> `oLane` as well, shifted only on the side that actually renumbers, with a
> fallback to `lane` for records written before it existed.
>
> Three further changes: the two halves are **gated together** (the rival-side
> repair was a separate `if` and could fire alone — D11's measured
> `restoredCount:0, playerGotJadeBack:false, rivalGotStarstoneBack:true`); the
> count fallback must now resolve to a **unique** candidate rather than taking
> `indexOf` among several; and `var md=G.matchDice||[]` no longer aliases a
> throwaway array and reports repairs it did not make.
>
> **Driven, four arms:**
>
> | arm | result |
> |---|---|
> | remove a seat **below** the trade | ledger lane 4→3, jade home at seat 3, **brand followed**, rival repaired at its own unshifted seat 4 |
> | no removal | unchanged, still correct |
> | the traded seat itself destroyed | `seatGone`, restored 0, **neither** side repaired — no half-repair |

`pinned_e5b7705.html:18555-18578` (extract) and `18591-18599`
```js
/* BOTH SIDES BACK THE INSTANT THE MATCH ENDS - win, loss, flee, or the end of
   a resumed match - no exceptions, no residue.
...
   The index does not have to be right for the repair to be: matchDice holds
   MATERIALS, so every entry reading t.theirs is interchangeable and writing
   t.mine over any one of them yields the same loadout.
...
    if(k>=0){
      md[k]=t.mine;
      /* the brand only goes home to the seat it left. If the index moved, the
         seat now at k belongs to some other die and its brand is not ours to
         overwrite - the material repair above already stands on its own. */
      if(G._enchArr&&k===L)G._enchArr[L]=t.myEn;
      n++;
    }
    if(G.matchOppDice&&L>=0&&L<G.matchOppDice.length&&G.matchOppDice[L]===t.mine)G.matchOppDice[L]=t.theirs;
```

**What it asserts.** (a) Both sides of every trade are restored at every match
exit with no residue. (b) A stale lane index is harmless because materials are
interchangeable.

**Why the expression cannot deliver it.** (a) The player-side repair is inside
`if(k>=0)`; the rival-side repair at **18599 is a separate `if` with its own
condition**. When `k` resolves to `-1` but `matchOppDice[L]===t.mine` still
holds, the rival's side is restored while the player's is not — one material
duplicated on the rival's board and one destroyed on the player's. **This
document already measured exactly that**: D11, `restoredCount:0,
playerGotJadeBack:false, rivalGotStarstoneBack:true`. (b) Materials are
interchangeable in `matchDice`; `_enchArr` is lane-indexed against them, and the
code itself concedes this by refusing the brand write unless `k===L`. A repair
landing on the wrong seat therefore leaves lane `L` with a null brand the player
paid for and lane `k` wearing someone else's — which is residue, under a comment
that says there is none.

**A census hazard inside the same function.** `md` at 18582
(`var md=G.matchDice||[];`) is a **local alias**. A census grepping
`G.matchDice[` misses `md[k]=t.mine` entirely. It is not the only alias — see
§3. And when `G.matchDice` is falsy, `md` aliases a throwaway `[]` and `md[k]=`
writes into nothing.

**The arrangement that would prove it.** Fire Trade at lane 4, then Break or
shatter a die in a lane *below* 4 so `_removeDieAt`'s splice shifts the recorded
lane, then end the match. 18561-18566 states this arrangement in the source
itself. Second arm, and the one this sweep adds: fire Trade at a middle lane so
the rival's bone sits in `matchDice[L]`, then next turn play Fair Trade so
`worst` resolves to `L` — Fair Trade **overwrites** a seat rather than removing
one (12992), lowering `cnt`'s count with nothing having died, a case the
two-way `have===cnt` test cannot express.

**What a probe must read.** Before `_tradeRestore()`: the whole `G._tradeSwaps`
(`lane`, `mine`, `theirs`, `cnt`, `myEn`), `G.matchDice`, `G.matchOppDice`,
`G._enchArr`, `G._fairTrade`. Its return `n`. Per iteration the resolved `k`
against `L`, and whether 18599 fired independently of the `k>=0` branch. After:
`G.matchDice[L]`, `G.matchOppDice[L]`, `G._enchArr[L]`. **The settling read is
`G._enchArr[L] === null` while `G.matchDice[L]` holds the player's own
material.**

### S9. "a swap, not a splice - lanes and brands stay aligned" — true for lanes, false for brands, in four verbatim copies

`pinned_e5b7705.html:24627-24629`
```js
        /* a swap, not a splice - lanes and brands stay aligned */
        var pOld=G.matchDice[pBestIdx],oOld=G.matchOppDice[oWorstIdx];
        G.matchDice[pBestIdx]=oOld;G.matchOppDice[oWorstIdx]=pOld;
```

**Already recorded as D11.** Listed here because the *comment* was never
catalogued as a comment defect, and because the sweep found **three further
copies of the same two lines** that the D11 write-up does not name:
`29354` (`sleight_of_hand`, NPC route), `31223` (`activateSleightOfHand`) and
`31519` (`activateStickyFingersPlayer`) — the last two byte-identical to each
other. `downgrade_best` at 24643 (`G.matchDice[pBestIdx2]='bone';`, run twice)
has the same hole with **no comment at all**, which is the safer failure.

**Why it cannot deliver it.** The comment is true for lanes — no index shifts —
and false for brands: `G._enchArr[pBestIdx]` is not written, so the arriving
rival die is dressed in the player's brand at the next refill (25143
`const _en=(G._enchArr||[])[_lane]||null;`) while the player's branded die
crosses to `matchOppDice`, where no brand array exists. Contrast Trade at
18424/18441/18453, which moves the brand out and ledgers it. **Two same-seat
swaps, opposite brand rules, and only one of them has a comment — and it is the
wrong one.**

### S10. "belt-and-braces" — the guarantee is computed 650 ms before the removal it guards

`pinned_e5b7705.html:11521-11523` and `11541-11544`
```js
  /* If every candidate would force a bust, skip the palm entirely this roll.
     Worth firing only when at least one safe target exists. */
  if(_safeCandidates.length===0)return;
...
    /* Recheck scoring on remaining FREE dice — if nothing scoreable, bust.
       Note: the safe-candidate filter above guarantees at least one
       scoring option remains after a single palm. This re-check is a
       belt-and-braces guard for edge cases (e.g. weird die materials). */
```

**What it asserts.** That the `_safeCandidates` filter guarantees a scoring
option survives the palm, making the re-check inside the timeout redundant.

**Why it cannot deliver it.** `_safeCandidates` is computed synchronously at
11516-11520 from `free` and `effectiveCards()` at that instant; the splice
happens inside `setTimeout(..., 650)` closing at 11552. During those 650 ms the
pool is mutable by anything the player can still reach — the same stale-capture
shape as **D4** (Steady Hand) and **D5(c)** (Powder Keg at +500 ms).
`G._palmAnimating=true` is set at 11529, but nothing in this reading establishes
what consults it. **A guarantee established before a mutation window does not
hold after it**, and calling the re-check redundant is what would license
someone removing it.

**The arrangement that would prove it.** Fire the pickpocket tell on a roll
where exactly one scoring die exists among the free dice and it is *not* the
palm victim, then inside the 650 ms window remove or change that die —
`CFX.sacrifice` is usable in `'choosing'` and splices `G.pool` at 14324;
`CFX.transmute` rewrites a face. Control: same roll, no interference.

**What a probe must read.** First, whether **any** handler honours
`G._palmAnimating` — instrument the tap path and read the flag at click time; a
grep is not sufficient. Then, latched: `free` at filter time (vals + mats),
`G.pool` at the top of the timeout, the `fv` array built at 11545, what
`anyScoring(...)` returns, `_anchorRescues(...)`, and finally `G.phase`,
`G.busted`, `G.numDice`, `G.matchDice.length`.

---

## DOES THE BRAND TRAVEL WITH THE DIE?

Denis asked for this directly. Every site that moves a die or steals one, in one
table. "Brand" is `G._enchArr` on the match side and `S.run.dieEnch` /
`S.run.dieEnchInv` on the run side. **Verdicts are nominations, not clearances**
— "PAIRED" means the two writes sit together at that site in the pinned copy,
not that the site is correct.

| site | what moves | what is left behind | verdict |
|---|---|---|---|
| `trade` fire **18425 / 18441 / 18453** | material both ways; `G._enchArr[L]=null`; `myEn` into the `_tradeSwaps` ledger | the brand crossing to `matchOppDice`, which has no brand array | **PAIRED.** The one-way loss is ruled and deferred in writing at 18410-18412 — "do not invent one here" |
| `_tradeRestore` **18592 / 18596 / 18599** | `md[k]=t.mine` whenever `k>=0`; the brand **only** when `k===L`; the rival side on an independent `if` | on `k===-1`: the player's material; on `k!==L`: the brand, permanently | **NOMINATED — S8.** Two halves not gated together; measured as D11 |
| `fair_trade` borrow **12992** | material only: `G.matchDice[worst]=inv[best]` | the **host's** brand on the seat, worn by the visitor; the **lender's** brand inert in `S.run.dieEnchInv` | **NOMINATED — D10(a), independently re-derived.** `G._enchArr` is named nowhere in the handler |
| `fair_trade` hand-back **19155** | material back: `G.matchDice[lane]=_ftB.was` | nothing — the seat's brand is the returning owner's own | **PAIRED by accident of ownership.** A naive `_setLaneMat` here would *break* it — see §3 |
| `fair_trade` expiry **24464** | material back: `G.matchDice[_lane]=_ft.was` | same | **PAIRED, same reason.** `G._fairTrade` has no brand field: `{lane, was, borrowed}` |
| `swap_die` best_for_worst **24629** | material both ways | `G._enchArr[pBestIdx]` | **NOMINATED — D11 / S9** |
| `swap_die` downgrade_best **24643** | `'bone'` written over the best, twice | `G._enchArr[pBestIdx2]` | **NOMINATED — D11 / S9**, no comment to mislead |
| `steal_die` take_best **24679 / 24681** | `matchDice.splice` + `_enchArr.splice` + `_dropLanes(1)`; `_diceOut` record carries `ench` (24673-24675) | — | **PAIRED** |
| `steal_die` take_and_use **24688 / 24690 / 24691** | as above, **plus** `G.matchOppDice.push(stolen)` | the stolen die's brand, destroyed at the moment of theft | **NOMINATED as a RULING, not a bug.** 18410-18412 rules the one-way loss for Trade; nothing rules it for confiscation |
| `CFX.sacrifice` **14318-14324** | `_diceOut` record with `ench`; `matchDice.splice` + `_enchArr.splice`; `_dropLanes(1)`; pool filter; relane | — at the site | **PAIRED at the site, NOMINATED at the target filter.** 14292 excludes only `committed`/`_shattered`, so the victim may be the **borrowed** die and the brand spliced out is the **host's**, on a die that was only benched. **SUPERSEDED-CHECK (P519)** |
| `_removeDieAt` **19186-19191** | record, `matchDice.splice`, `_enchArr.splice`, `_dropLanes(1)`, pool filter, relane | — | **PAIRED.** The reference remover |
| Break **18397 → 24953 / 26840** | the die leaves through `_removeDieAt`, brand with it | — for the brand | **PAIRED on brand.** The single-slot `_breakPending` is a separate nomination — S4 |
| pickpocket palm **11536-11539** | `G.pool.splice` + `_dropLanes(1)` + DOM removal | `matchDice`, `_enchArr`, `_diceOut` — deliberately: the palm is turn-scoped and 24435 hands the lane back | **NOT A FINDING** (N6, refuted). The brand does not need to travel because the die does not leave the match |
| obsidian / grogs_tooth shatter **25291-25295** | through `_removeDieAt`, so paired | the `else` arm at 25295 filters `G.pool` alone; a laneless shattered die is in neither branch | **NOMINATED — S5 / D24** |
| Vagabond drag **36662-36699** | `phys.x`, `G.pool` **order**, DOM row order | `d.lane`, `G.matchDice`, `G._enchArr`, `G.numDice`, `d.hx` | **NOMINATED — M1, never judged.** The brand travels *because it is a property of the pool entry* (`ench` stamped at 25160, 25042, 26403), not because anything moved it. The **seat** does not move at all. **SUPERSEDED-CHECK (P520)** |
| `transmute` **14247** | `d.val` only | brand stays with its own die | **NOMINATED, low — N15.** `d.val` can be set to `d.ench.face` directly, bypassing `_enchRollM`, turning a wagered brand into an on-demand button; and its free set `G.pool.filter(d=>!d.committed)` (14241) admits `_frozen` dice |
| Preserve bench → restore **24580 + `G._famPreserve`** | `val, mat, pts, crack` | the **lane** and the **brand** — the record has neither field | **NOMINATED — M4/M5, never judged; = D6(b)** |
| `_stTrade` **33296-33299** | `S.run.dice[slot]=mat` then `S.run.dieEnch[slot]=null` | — | **PAIRED.** The reference for the run arrays |
| `famDieShift` **14874-14877** | `var d=S.run.dice; ... var e=S.run.dieEnch,te=e[i];e[i]=e[j];e[j]=te;` | — | **PAIRED, dead.** Note it writes through **local aliases `d` and `e`** — a second census blind spot after `md` |
| `famDieStash` **14884-14886** | `dice.splice` + `dieEnch.splice` + both padded | — | **PAIRED, dead** |
| `famDieEquip` **14891-14898** | `diceInv`/`dieEnchInv` splices, `dice[bi]`/`dieEnch[bi]` written together | — | **PAIRED, dead** |
| For Keeps loss **30256-30257** | `dice.splice` + `dieEnch.splice`, both refilled/padded | — | **PAIRED** |
| `famRunDraftPick` **13770-13771** | `S.run.dice[bi]=mt` at `lastIndexOf('bone')` | `S.run.dieEnch[bi]` | **NOMINATED, new — not in this document.** If that bone carried a paid brand, the upgraded material inherits it. Reachability of the `#famRunDraft` overlay **not traced** |
| `forge_night` **29458** | `S.run.dice[_fnPickIdx]=_fnNewMat` | `S.run.dieEnch[_fnPickIdx]` | **DEAD** — gated on `G.pCards.includes('forge_night')` and `G.pCards` is `[]` (N14). Would be a finding if the layer is ever fed |
| tier loadout drag **34928-34930** | `S.run.dice[srcIdx] ↔ [tgtIdx]` | `S.run.dieEnch` entirely | **DEAD (CSS)** — already this document's §1e |
| `_buyDieAtSlot` **33965** | `S.run.dice[slotIdx]=mat` | `S.run.dieEnch[slotIdx]` | **DEAD** — already this document's §1e |
| `rewardKeepDice` **34332** | `S.run.dice=[..._rewardDice]` — the whole array | `S.run.dieEnch` entirely | **DEAD** — `showScreen('bossreward')` has no caller (N13) |
| `activateSleightOfHand` **31223** · `activateStickyFingersPlayer` **31519** | material both ways | `G._enchArr` | **DEAD** — `G.pCards` is `[]`; already §4 item 12 |
| `activateBlessedConfiscationPlayer` **31553** | `G.matchDice.push(stolen)` | no `_enchArr` push | **DEAD** — same; and it is the **only** site in the file that can lengthen `G.matchDice` |
| `activateAlchemistsChisel` **31668** | `G.matchDice[leftPoolIdx]=newMat` | `G._enchArr`; and the index is a **pool** index | **DEAD** — already §4 item 12, already driven there |
| debug `?vagatest=1` **36712** | `S.run.dice=['vagabond'×6]` | `S.run.dieEnch` entirely | **DEAD unless the URL param is set.** Flagged only because the file's own comment says "Strip if shipping prod" |

**The one-line answer to the question.** On the **run** arrays the brand travels
with the die at every live site that was read. On the **match** arrays it
travels at every *removal* and at Trade, and it **does not travel at any
same-seat substitution** — `fair_trade` 12992, `swap_die` 24629 and 24643. The
brand belongs to the **seat**, and the only three live effects that change a
seat's occupant without removing anything are exactly the three that leave it
there.

---

## THE _setLaneMat CENSUS, INDEPENDENTLY DERIVED

**"Four against three" half held.** The **four** is right for the scope §5c
declared; the **three** is wrong, and the ratio it was used to justify is not
4:3.

**The four wrong sites hold.** §5c names `fair_trade` 12992, `swap_die`
best_for_worst 24620, downgrade_best 24634 and `sleight_of_hand` 29343 (dead).
In pinned line numbers those are **12992, 24629, 24643, 29354** and all four are
real: a material written into a lane with `G._enchArr` untouched. Three live,
one dead.

**The full census, derived without looking at §5c first.** Two greps over the
pinned copy — `G\.matchDice\[[^\]]*\]\s*=` and
`G\.matchDice\.(splice|push)|G\.matchDice\s*=` — plus a manual alias pass:

| kind | sites |
|---|---|
| element writes | **12992, 18425, 19155, 24464, 24629, 24643, 29354, 31223, 31519, 31668** (10) **+ 18592 via the alias `md`** = **11** |
| push | **31553** (1) — the only site that can lengthen `matchDice` |
| splice | **14322, 19190, 24679, 24688** (4) — all four paired with an `_enchArr.splice` |
| whole-array | **23110** (the `newG` object literal), **32032**, **32085** (3) |

**Four of the eleven are on the dead `pCards` layer** — 31223, 31519, 31668, and
the push at 31553. `initMatchScreen` hard-codes `const pCards=[];` at 31886 and
passes *that* to `newG` at 31896, `G.activeCardState.usedCards` is seeded at
31959 by iterating it, and `canActivateCard` therefore fails at 30846-30847
before `activateCard`'s switch is reached. **§4 item 12 already names all four**;
they are excluded from 5c on purpose, not missed.

**Two aliases, not one.** `md` at 18582 (`var md=G.matchDice||[];`) is invisible
to a `G.matchDice[` grep, and so is `famDieShift`'s pair at 14874-14877
(`var d=S.run.dice;` … `var e=S.run.dieEnch,te=e[i];`). Any future census must
be run twice: once on the identifier and once on `= *(G\.matchDice|S\.run\.dice)`
to catch the alias bindings. **This is the seventh time this session that a
name-based search under-counted.**

**The fair-trade family is three sites, not one — and a naive helper would
break two of them.** 12992 is the borrow; **19155** and **24464** are the two
returns:
```js
19155:      G.matchDice[lane]=_ftB.was;/* its owner walks back in */
24464:      G.matchDice[_lane]=_ft.was;/* loan simply expired */
```
Both restore the lane's **original owner**, so the brand currently sitting in
that seat is the one that belongs there. Passing an `ench` argument at those two
sites would need the value the loan displaced — and `G._fairTrade` records only
`{lane, was, borrowed}`, with **no brand field**. *`_setLaneMat` cannot be
adopted for Fair Trade until the loan record grows a field.* This is D6's shape
(one site needs one new field) and belongs in 5e alongside it, not in 5c.

**"Three correct references" does not hold.** Of the three §5c names, only
**Trade** operates on the arrays the helper would govern. `_stTrade`
(33296-33299) and `famDieShift` (14874-14877) pair the **run** arrays, whose
length invariant is enforced separately by `_enchInit` (19459-19462) — a
different contract. And the run side has at least three more correct pairs that
§5c does not count: `famDieStash` 14884-14886, `famDieEquip` 14896-14898, and
the For Keeps forfeit 30256-30257.

**The real ratio, stated by array:**

| array | correct pairs | unpaired writes |
|---|---|---|
| match (`matchDice`/`_enchArr`) | **1** — Trade 18425/18441 | **3 live** (12992, 24629, 24643) + **1 dead-NPC** (29354) + **4 dead-player** (31223, 31519, 31553, 31668) + **1 conditional** (18592/18596) |
| run (`S.run.dice`/`dieEnch`) | **5** — 33298/33299, 14876/14877, 14884/14885, 14897, 30256/30257 | **13771** (live, reachability untraced), 29458, 33965, 34332, 34929-34930, 36712 — all dead or debug except 13771 |

On the match arrays it is **1 correct against 4 wrong**, not 3 against 4. The
argument for building the helper survives — it is stronger, because the correct
reference is rarer than §5c thought — but the *evidence* offered for it in §5c
does not, and the two fair-trade returns must be excluded from the conversion
list until the loan record can carry a brand.

**One more ground-truth item, and it is a nomination in its own right:
nothing re-derives brands from materials.** The only derivation of `G._enchArr`
is 32100-32103, and it derives from `S.run.dieEnch` or the snapshot, **never
from `G.matchDice`**:
```js
  var _rdEnch=params&&params._resumeData&&params._resumeData._enchArr;
  G._enchArr=(Array.isArray(_rdEnch)&&_rdEnch.length===(G.matchDice?G.matchDice.length:0))
    ?_rdEnch.slice()
    :((S&&S.run&&S.run.dieEnch)?S.run.dieEnch.slice():[]);
```
The born-brand pass — the one place a material *implies* a brand — runs at
19473-19486 inside `_enchInit`, on `S.run.dice`/`S.run.dieEnch`, never on the
match arrays, and `_bornEnch` has exactly one call site (19476). So a mid-match
swap that brings a relic material into a lane gets **no** born brand, and one
that takes a relic out leaves `{born:true}` sitting on whatever replaced it. The
only pass that judges a brand against the match material,
`_scrub(G._enchArr,G.matchDice,false)` at 19418, is gated behind the one-shot
`if(S.run._enchV!==3)` migration at 19378 — at most once per save, never after a
swap. **Probe:** own Brutus's relic, let `downgrade_best` (24643) turn that lane
to `'bone'`, then read `G._enchArr[lane]` (expect `{t:'ward',face:N,born:true}`
still present) against `_bornEnch(G.matchDice[lane])` (expect null) and
`_iconFaces(G.matchDice[lane]).indexOf(G._enchArr[lane].face)` — a `-1` is a
brand on a face the material cannot show, which is exactly what the 19391
migration exists to refuse.

---

## REFUTED

31 nominations died. One line each, with the reason. A sweep that reports only
what it found and never what it threw out is unfalsifiable — and half of every
raw hit list this session has dissolved on contact.

**Safety-comment lane (12):**

1. **C4 — `_dropLanes`' rule comment says numDice "is never assigned from matchDice.length" and its own else arm does.** The comment is imprecise but the branch is unreachable: every `numDice` writer was walked (24427, 24435, 24540, 24765, 24800, 24813, 14272, 19121, 24991, 26267, 26389, 27239, 27438, 27571, 27858, 31375, 32026) and none produces NaN; the Gambler's Eye zero route is closed four lines above the write by `if(geSelected.length===0||geSelected.length>=geFree.length)return;`.
2. **C5 — "the record and the gap can never disagree" with the record inside a swallowing try.** No demonstrated throw: every `_diceOut` writer produces an array and the resume normalises at 32114, and `_enchInit` (19459-19460) forbids `_enchArr` being shorter than `matchDice`.
3. **C6 — the Fair-Trade early return sits in a swallowing try, so a throw applies both paths.** The only two statements that could throw are each wrapped in their own inner try (19162, 19164); the arm variance D5 flagged is explained by C16's stale `ft.lane` with no throw needed.
4. **C7 — resume uses array-length equality as proof of lane alignment.** Scoped finding that does not transfer: `G.matchDice` was set from the *same* snapshot at 32032, so the gate can copy a misalignment but cannot create one; its real job is catching the mirror re-seed at 32085.
5. **C8 — "the die cannot come back inside this match" omits every literal-6 numDice writer.** 24435 re-derives from `matchDice.length` at the top of every player turn and the only later writers lower it; `saveMatchState` has two call sites and neither runs between a literal 6 and the next reset.
6. **C10 — `clearRow`'s comment vouches for the held-dice wipe then clears the record the seat maths needs.** Every caller clears `G.oppDice` in the same statement (28379, 28443), so `_oppHeld` is legitimately empty on re-entry and `_freeSeats=[0..n-1]` is correct; the real asymmetry is that `left` is not recomputed, which is D2, a different claim.
7. **C14 — P518's max has no proof that raising numDice is always right.** Could not build the window: every penalty writer leaves the pool built to the reduced count, and the one writer that leaves numDice below `pool.length` (Gambler's Eye 24765) is followed by Powder Keg uncommitting every die, where raising is correct.
8. **C15 — Sacrifice's `_diceOut` record and its splice share a variable declared inside a swallowing try.** Nothing between the `try{` at 14310 and the assignment at 14316 can throw (`d._shattered=true` at 14294 runs outside it), and `_dropLanes(1)` at 14323 sits outside both `mi>=0` guards, so numDice cannot hold while the pool shrinks.
9. **C19 — the loadout panel's comment enumerates "every producer" of `_diceOut` and misses the palm and the shatter else-branch.** Ran the right test — who shrinks `matchDice` without writing a record — and the enumeration holds: exactly four `matchDice.splice` sites (14322, 19190, 24679, 24688), each preceded by its record. The palm and the else-branch touch only `G.pool`.
10. **C20 — Preserve's heading says "ONE FEWER THAN THE LOADOUT" and the code takes one fewer than numDice.** Self-correcting in place: the P514 block directly beneath the heading states the actual rule. The load-bearing observation buried in it (the record has no lane) is D6/S6's mechanism and belongs there.
11. **C21 — `_kindredActive` asserts `S.run.dieEnch` is stable for the match; the empty-array case is not covered.** `_enchInit` forces the array to `S.run.dice.length` (19459-19460) and 9439 pads to 6, so `[]` requires an empty loadout, in which case the fallback returns the same answer.
12. **C22 — "never a legal Break target" implements only the Break half of a ruling stated as inertness.** `_breakPreserved`'s object tests are dead: `G._famPreserve`'s sole constructor (14430) writes `{val,mat,pts,crack}` with no `die` and no `lane`, so Sacrifice's missing preserve filter is currently vacuous. (The missing *borrowed* filter is live and is S7/N2.)

**Brand-travel and steal lane (9):**

13. **N3 — hot dice still uses `i % G.matchDice.length`, so a short hand re-deals the low lanes.** P517's clamp at 24991 runs 20 lines earlier and caps `numDice` at `matchDice.length`, so the modulus can never wrap; and `G.pool=[]` at 24977 makes the free-lane walk byte-identical to the modulus here.
14. **N4 — Blessed Confiscation destroys the player's brand and hands the rival a die that cannot carry one.** Two of the three claims are conditional on a swap ruling the file does not implement; the third (no opponent-side brand array) is ruled and deferred in writing at 18410-18412.
15. **N6 — the pickpocket palm leaves `matchDice`/`_enchArr`/`_diceOut` untouched.** Wrong scope: `_removeDieAt` is the *match*-scoped remover and the palm is turn-scoped; 24435 hands the lane back next turn, `needNew` is 0 so no die inherits the vacated brand, and `matchDice[ft.lane]` still satisfies the loan's `_stillThere` test.
16. **N8 — Vagabond's comment claims "the enchant slots agree with what is now on the table".** The comment is loose but the outcome holds by a different mechanism: every pool entry carries its own `ench` **object**, stamped at 25160, 25042 and 26403, and `_laneOf` returns the stamp first (19357-19358), so reordering the array moves brands intact. (What the drag genuinely does not move is `d.lane` — that is M1, unjudged.)
17. **N9 — Snuff/Fog/Snare arm with a player lane and index the rival's seat array.** `royal_seizure` shrinks the *player's* `matchDice` and the marker only ever indexes `G.matchOppDice` (28053); mirroring the lane number is the card's stated design (18466-18468), and the only two writers that could shrink `matchOppDice` under a live marker are on the dead layer.
18. **N10 — `activateBlessedConfiscationPlayer` pushes to `matchDice` without padding `_enchArr`, tripping the resume length gate.** Unreachable: `initMatchScreen` declares `const pCards=[];` at 31886 and passes that local to `newG` at 31896; `usedCards` is seeded from it at 31959; `canActivateCard` bails at 30846-30847. This verdict kills every other player-side activator too.
19. **N12 — Mabel's Stitch and Second Wind rebuild the table with `G.numDice=G.matchDice.length`.** Both branches are gated on flags whose only writers are inside `activateCard` (31032, 31425) — dead by N10; and Second Wind's is followed immediately by `endPTurn()`, after which 24435 reassigns anyway.
20. **N13 — `rewardKeepDice` replaces the whole loadout array and leaves every brand behind.** The surface never opens: `showScreen` is the sole mechanism that adds `.active` (10376), every one of its ~38 call sites passes a string literal, and none passes `'bossreward'`.
21. **N14 — Forge Night leaves a brand on the new material.** `G.pCards.includes('forge_night')` at 29452 can never be true; and the reading it contrasts against is not parallel — `_stTrade` clears the mark because the outgoing *die leaves*, whereas forge_night upgrades the die standing in the slot.

**Census lane (10):**

22. **C1-count — 11 element writes, not 4, and 7 of them leave `_enchArr` behind.** The raw count reproduces exactly (I re-derived the same 11), but four of the "seven live" are on the dead `pCards` layer and §4 item 12 already names all four by function; 5c's scope is live sites.
23. **C2-31223 — `activateSleightOfHand` is missing from the four.** Dead by N10; and `sleight_of_hand` is `dep:true` (11791) and in no `cardPool`, so even the NPC route cannot draw it.
24. **C3-31519 — `activateStickyFingersPlayer` is missing from the four.** Dead by N10; the card's *live* implementation is the NPC block at 24629, which 5c already counts.
25. **C4-31668 — Alchemist's Chisel writes `matchDice` at a pool index.** Dead by N10, and "missing from the doc" is false — §4 item 12 names it, calls it the only such site in the file, and reports it **driven**.
26. **C5-31553 — Blessed Confiscation grows `matchDice` without growing `_enchArr`.** Dead by N10; the live `blessed_confiscation` does the opposite (splices `matchDice`, pushes to `matchOppDice`), so `matchDice.length > _enchArr.length` has no reachable producer.
27. **C6-groundtruth-index — the two arrays can diverge at birth, three ways.** All three close: `newG` calls `_enchInit()` before reading `S.run` and `_getS()` creates the run (9500) with six dice; the mirror re-seed is a measured no-op; and 31553's push is dead.
28. **C7-sparse — Trade's fire can mint a genuinely sparse `_enchArr`.** Requires the runless `G._enchArr=[]`, which C6 refutes; and Trade's own guard at 18420 refuses any lane outside `matchDice`, so 18441 always overwrites an existing slot.
29. **C8-shrink-guards — the four splice sites each use two independent guards.** Structurally true, but the failure needs `_enchArr.length < matchDice.length` and no reachable route to it was found; the 32101 fallback can only make `_enchArr` **longer**.
30. **C13-mirror — mirror_match's length test cannot distinguish "different loadout" from "same length".** The reseed is a measured no-op: writer 35714-35719 and reader 32085-32087 have inverted field names and the inversions cancel, so both branches carry identical content. Already this document's line 480.
31. **C14-linedrift — the 5c line numbers do not resolve in the pinned file, so the census was counted against a different revision.** The individual checks are right and the inference is wrong: 12992 lands exactly, 24620/24634 are deliberate block anchors, 33287-33288 is `_stTrade`'s header comment above the function. Only one cite (14864-14869 for `famDieShift`, which begins at 14873) is genuinely off, by four lines. The drift is this document's own §4 item 14, already recorded.

---

## NOT DRIVEN

**Stated plainly and up front: nothing in this part of the document was
executed.** No browser, no dev server, no `tools/shoot.js`. It is static reading
against `pinned_e5b7705.html`, a copy of `fark_proto.html` at commit **e5b7705**,
taken because the live file was being patched concurrently and could not be
read. Every item above is a **nomination awaiting a probe**. Where a nomination
coincides with an already-measured defect (D6, D8, D9, D10, D11, D24) the
measurement is this document's, not this sweep's, and is cited as such.

**And the pinned copy is stale against the live file.** Highest patch marker
P518. P519 and P520 are recorded in §2 as shipped and are **absent from what was
read**. The five nominations marked SUPERSEDED-CHECK — S1's NaN arm, S7's arm
(a), the Sacrifice row of §2, N2, and M1's whole basis — must be re-read against
the live file before a probe is written, or the probe measures a file nobody is
running.

### Priority order for driving

1. **S4 — Break's single-slot `_breakPending`.** Highest, because it is the only
   nomination here whose mechanism no shipped patch touches, whose arrangement
   is cheap (two Break brands, one commit), and whose failure is silent. **Read:**
   a `fire` counter instrumented at 18397, `G._breakPending` after each, the
   number of `_breakBegin` entries, and `G.matchDice.length` / `G._diceOut.length`
   / `G.numDice` across the commit. Two fires and one `_diceOut` entry settles it.
2. **S8 — `_tradeRestore`'s two ungated halves, under a live Fair Trade loan.**
   D11 already measured the `k===-1` case; the new arm is Fair Trade
   **overwriting** a traded seat (12992), which lowers `cnt` with nothing having
   died — a case the `have===cnt` test cannot express. **Read:** the whole
   ledger before the call, `n`, `k` against `L` per entry, whether 18599 fired
   independently, and `G._enchArr[L]` after.
3. **S5's duplicate-lane arm.** D24 measured the laneless case; the *duplicate*
   case has never been touched. **Read:** `_shLanes` as built, and whether
   `_removeDieAt` was handed the same seat twice — the second call's victim is
   an innocent neighbour. This one is cheap only if S1's producer still exists
   post-P519; check that first.
4. **S6 — the occupancy set against `needNew`.** The symptom is a die sitting
   out a turn, which is indistinguishable by eye from D6. **Read:** latched at
   the top of the refill, `G.numDice`, `G.pool.map(d=>d.lane)`,
   `Object.keys(_occLane)`, `_freeLanes`, `needNew`, `G.matchDice.length`; then
   which `matchDice` index was dealt no die.
5. **S7 arms (b) and (c) — `_breakBorrowed` by material string, and the
   out-of-range arm returning `true`.** P519 does not touch either. **Read:**
   `_breakBorrowed(d)` against startPTurn's expiry predicate on the same state,
   with a loan whose `borrowed` material duplicates a die the player already
   owns; and separately with `ft.lane >= G.matchDice.length`.
6. **S10 — whether anything honours `G._palmAnimating`.** This is a
   *reachability* read before it is a defect read, and it is one line of
   instrumentation on the tap path. If nothing consults the flag, the 650 ms
   window is open and D4/D5(c) have a third carrier.
7. **The `_setLaneMat` ground truth — a brand orphaned on a material that cannot
   show its face.** **Read:** `_enchArr[lane]` against `_bornEnch(matchDice[lane])`
   and `_iconFaces(matchDice[lane]).indexOf(_enchArr[lane].face)` after
   `downgrade_best` takes a relic lane to bone. A `-1` is a state the 19391
   migration exists to refuse and that nothing at runtime can reach to repair.
8. **`famRunDraftPick` 13770-13771 — reachability first.** Trace what opens the
   `#famRunDraft` overlay. If it is live, it is the only unpaired run-array write
   this sweep found on a reachable surface, and the whole run side's "brand
   travels" answer changes.
9. **S1, S9, S2/S3 last** — S1 and S9 because P519 and D11 respectively may
   already own them, S2/S3 because they are §5b's rework and the seat/count
   helper subsumes them. For S2/S3 the useful probe is not the seats — D1
   measured those — but the **`combo` persona's computed value for `L===0`**
   against the actual post-sweep `_freeSeats.length`.

## THE NINE, ADJUDICATED — and two defects the recent patches created

The adversarial pass was re-run against the current code. **M3 is DEAD as
stated**, and judging it surfaced two NEWLY-CREATED defects, both mine, both now
fixed and driven.

**P531 — the reorder carried the loan and left the trade ledger.** P520 made the
reorder real, P527 gave the ledger a player-side `lane` so it could be
maintained, P530 taught the reorder to carry `_fairTrade` — and stopped there.
Driven before the fix: die moved seat 0 → 3, loan followed to 3, ledger stayed
at 0. The loan was the control that proved the reorder *can* maintain a record.
Fixed; `oLane` deliberately does **not** move, because the rival's board does
not renumber when the player's does.

**P532 — the resume silently un-shipped P527.** Both snapshot writers deep-clone
the ledger, so `oLane` and `seatGone` reach the disk. The resume mapper
enumerates fields by hand and never learned either, so every resume dropped
them. That forced the rival-side repair onto its pre-P527 fallback — the very
path P527b exists to avoid — and unmarked a destroyed seat so the count
heuristic could repair an innocent die. Also fixed: `_removeDieAt`'s mid-turn
snapshot never carried the ledger at all, which was harmless until P527 made the
live copy correct and the snapshot's copy wrong.

| check | result |
|---|---|
| reorder carries ledger `lane` | 0 → 3, follows the die |
| reorder leaves `oLane` alone | held at 0 |
| resume keeps `oLane` | 4 survives against `lane` 1 |
| resume keeps `seatGone` | survives |
| a pre-P527 record | still falls back to `lane` |
| mid-turn snapshot vs live | both 3, agree |

**M3 itself is dead.** `_lmArm` stores one number and every reader of
`_snare`/`_snuff`/`_fog`'s `.lane` is inside `runOppTurn`, compared against the
rival's seats. There is **no player-side reader**, and the drag touches neither
those objects nor `matchOppDice`. Measured alongside: `_laneOf` does change
across a reorder (0 → 3), so a marker armed *after* a drag names the die's new
seat — which is the intended semantics of the P520 ruling, not a defect. Worth
knowing it makes seat-targeted effects aimable by rearranging.

**M5 SURVIVES and is the largest thing still open.** Preserve's `canUse` reads
`k.vals` (post-`_splitIcons`) and its picker reads `k.dice` (pre-split, still
holding icon dice). Brands sit on faces 1 and 5, so an icon die is by
construction a face that banks **zero** — and Preserve can bank it next turn at
100. Pre-existing; P514 created it by moving the picker to `k.dice` to fix the
wrong-material bug. Not driven yet.

**Dead or already-recorded:** M1 (superseded, with one latent degradation arm),
M2 (counterfactual; and only **two** live mint sites, not four), M4 (D6
restated — Preserve benches nothing), M6 and M7 (one dead surface, and "nine
lines apart" is wrong: one line apart, 20,348 lines away), M8 (unreachable
`pCards` layer; its second clause redundant), M9 (half is D10(a); the "both
legs" framing is wrong and acting on it would introduce a bug).

---

### Nine nominations never received a verdict

They were raised and the adversarial pass ran out before reaching them. They are
neither survivors nor refuted, and must not be counted as either. Recorded here
verbatim so they are not lost:

| id | nomination |
|---|---|
| **M1** | Vagabond's drag writes zero of the six facts except pool order and DOM order — `d.lane` never moves, so the seat stays put and only the picture moves. **SUPERSEDED-CHECK (P520)** |
| **M2** | For a genuine reorder, the naive patch (restamp `d.lane` only) is exactly the "brand stays on the seat" shape — and the only sites that would show it are the four mint sites |
| **M3** | A genuine reorder retargets Trade, Snare, Snuff and Fog at a different rival seat — the armed markers store a number that is a player lane and a rival lane at the same time |
| **M4** | Preserve benches a die and restores it stripped of its brand — and the bench record has no lane and no `ench` field at all |
| **M5** | Preserve can bench an ICON die — a branded face that banks zero by law — and hand it back next turn worth 100 or 50 points, unbranded |
| **M6** | The loadout drag swaps `S.run.dice` and never `S.run.dieEnch` — the reference-correct version of the same swap sits nine lines apart in `famDieShift` and is dead |
| **M7** | `_enchInit`'s born-brand pass is the only code in the file that moves a brand *with* a material — so under any reorder a born Ward follows its die while a paid brand stays on the seat, and the paid one is refunded and overwritten |
| **M8** | `activateAlchemistsChisel` uses a POOL INDEX as a `matchDice` index, and writes `matchDice` without `_enchArr` — the drag makes pool index and lane disagree |
| **M9** | Fair Trade's loan is material-only on BOTH legs — the record has no `ench` field, and the restore never writes `_enchArr` either |

M4/M5 and M9 are the two worth judging first: M4/M5 is D6(b) with a scoring
consequence nobody has priced, and M9 is the precondition that decides whether
`_setLaneMat` can be adopted for Fair Trade at all (§3).

---

# THE PARALLEL-REPRESENTATION HUNT

Six confirmed defects in one session turned out to share a single shape: **the
same fact stored, derived or enumerated twice, with the two copies maintained
separately.** Preserve's `canUse` reading `k.vals` while its picker reads
`k.dice`; the refill's `needNew` count against its lane set; the rival's `left`
against `_freeSeats`; the trade ledger's one lane field indexing two boards;
the resume's hand-written field list against a record it does not own;
`G.matchDice` beside `G._enchArr`. None of those were found by looking for the
shape — each was found separately, and the shape was noticed afterwards. Denis
asked the obvious next question: **before Preserve is patched as an isolated
bug, how many more of these are sitting unfound?** This section is the answer.
Forty nominations were raised against the pinned copy, twenty-six died on
contact, and what follows is the fourteen that did not — merged where two were
the same root cause in different clothes, and one demoted where a nomination
from the other half of the sweep had already settled it.

Fourteen nominations, twelve items after merging, eleven live: **G2 is M5**, the
survivor this document already carries, with its three producers now named;
**SR-03 and SR-04 are one defect** seen from the count side and the tray side;
**K2 is PA3** and PA3's producer census kills it, so it is recorded below as a
latent hazard rather than a finding.

---

## SURVIVORS, RANKED

### PR1 — Four derivations of "is this selection a legal keep", and the ROLL button lights for a selection the ROLL press then refuses

> **CONFIRMED LIVE, then CLOSED — P533.** Driven before the fix, in a real match:
> score **-1**; `handleRoll` and `_legalKeeps` refused; the button gate and
> `handleBank` accepted. **The ROLL button was lit and the ROLL press refused the
> same selection** — nothing committed, and the status line came back **empty**.
> A lit button that does nothing and says nothing.
>
> One predicate now, four callers. `_keepIsLegal(pts, iconCount, anchorLegal)`:
> a negative total is never legal, a positive one always is, and zero is legal
> only for an icon-only or anchor keep.
>
> **`anchorLegal` is a parameter because the sites legitimately differ** —
> `handleRoll` holds `_anchorDie` as a flag beside the bonus, while the preview
> folds the 600 into `pts` before testing and must pass `false`. Inventing an
> anchor term for the preview would have darkened the button for a keep the
> commit accepts: the same defect mirrored.
>
> | arm | score | accepted | button | commits | button = press |
> |---|---|---|---|---|---|
> | brand + unusable die | -1 | no | dark | no | yes |
> | an ordinary scorer | 100 | yes | lit | yes | yes |
> | icon-only keep | 0 | yes | lit | yes | yes |
>
> The two controls carry the weight: a fix that simply darkened the button would
> have passed the first arm alone.
>
> **Two faults in my own probe, both caught before the result was believed.** It
> first ran three arms in one browser session and the second could not build a
> pool — one arm per session, again. And it measured "did it commit" by kept-tray
> growth, which **cannot see an icon-only keep**: 25117 only pushes when `pts>0`
> or the post-split list is non-empty, so a legal icon keep never grows the tray.
> Measured on the dice instead.
>
> **The provenance is the lesson.** 25072-25089 records the forgiving reading
> being removed for a measured **+80.5 win-rate points [77.95, 82.69]**. Somebody
> proved the fix necessary, with a number, and it reached one of four sites.

The gate:

```
26108  /* Validity + total via scoreSelection — the SAME function the commit (ROLL)
26109     and bank paths use. ... */
26115  let pts=scoreSelection(selV,cards,locked,_selCtx,selMats,_pvEnch);
...
26135  const _selHasIcon=_pvIcons.length>0;
26136  if(!selV.length&&_selHasIcon)pts=0;
26137  const ok=pts>0||_selHasIcon;G.turnPts=locked+(pts>0?pts:0)+(G._turnBonusPot||0);updHUD();
26143  setBtns(ok&&(rem>0||allFreeSelected),ok);
```

The three acceptance predicates:

```
25090      if(pts<0||(pts===0&&!_anchorDie&&!_iconSel.length)){SFX.err();setStatusMsg('NO SCORE — TRY AGAIN','red');return;}   /* handleRoll */

27072      if(_bkScore.length===0&&_bkIcons.length)pts=0;                                                                      /* handleBank */
27073      if(pts>0||_bkIcons.length){
27131      if(pts<0)pts=0;

14078      if(pts<0||(pts===0&&!(sp.icons||[]).length)) continue;                                                              /* _legalKeeps */
```

**The two representations.** One question — is this selection a legal keep —
answered from the same inputs by four separately-written predicates. Two of
them (`handleRoll` 25090, `_legalKeeps` 14078) reject `pts<0`. Two of them
(the button gate 26137, `handleBank` 27073) do not, and `handleBank` then
launders the negative at 27131. `scoreSelection` returns `-1` when the non-icon
half of the selection holds a die the engine cannot use, so the term matters
exactly when a brand is in the selection.

**The write that moved one and not the other** is recorded in the file, at
25072-25089: *"THE SWEEP LIVED HERE: `if(pts<0&&_iconSel.length)pts=0;`,
removed"*, citing AUDIT_RESOLUTIONS #42 and a measured **+80.5 win-rate points
[77.95, 82.69]** for the wide reading. That rule was applied to `handleRoll`
and reached one of the four sites. The comment at 26108-26109 asserts the
preview uses *"the SAME function the commit (ROLL) and bank paths use"* — true
of the total and false of the validity test, which is the in-source-claim shape
S2, S6 and S9 each turned up.

**Exposing arrangement.** Any brand on the loadout (brands sit on faces 1 and 5,
`_dieIsIcon` 18675). Roll until a branded die shows its brand face, then select
it **together with one non-scoring plain die** — a 2, 3, 4 or 6 outside a
triple. The default state hides it two ways: the branded die alone is legal on
every path (25071/27072 pin it to zero), and a branded die beside dice that
*do* score gives `pts>0`, where all four agree.

**Read:** on that one selection, `pts` and `ok` inside `refreshSelUI`, plus
`btnRoll`/`btnBank` disabled state; then `handleRoll()` and whether `G.kept`
grew or the status line says NO SCORE; then reset to the identical selection,
`handleBank()`, and read `G.kept`, `G.pPts`, `d.committed` on the junk die, and
whether `_iconFire` ran (a Tithe brand pays 15g here). *Instrument check:* the
same three reads on an icon-free illegal selection, which all three must refuse
— otherwise the probe cannot see a refusal at all.

### PR2 — Preserve's gate reads `k.vals`, its picker reads `k.dice`, and which of three producers wrote the row decides whether those are parallel (= M5, with the producers named)

> **CLOSED — P534.** `k.dice` records the brand, and `_keptScorers` filters icon faces out using the same predicate `_splitIcons` uses.

```
14436  canUse:function(){
14437    if(!G||G.phase==='opp')return false;
14438    return (G.kept||[]).some(function(k){return (k.vals||[]).some(function(v){return v===1||v===5;});});
14439  },
...
14450       k.vals and k.dice are NOT index-parallel - vals comes from
14451       _scoreDice with icon faces split out by _splitIcons, dice comes from
14452       selDice - so this searches k.dice BY VALUE and never by position.
...
14456      var _pd=(k.dice||[]).filter(function(dd){return dd&&(dd.val===1||dd.val===5);})[0];
14457      if(_pd){found=_pd.val;foundMat=_pd.mat||k.mat||'bone';return true;}
```

This is **M5**, already recorded as the largest thing still open. What this pass
adds is the producer census, and it changes the arrangement. `vals` is
post-`_splitIcons` at all three producers; `dice` is not:

```
25125    if(pts>0||_scoreDice.length)G.kept.push({vals:selVals,mat:selDice[0].mat,pts,cursed:_cfHit,
25126      ss:_starstonePay(_scoreDice),
25127      dice:selDice.map(function(dd){return{val:dd.val,mat:dd.mat};})});          /* handleRoll — PRE-split */

27121            G.kept.push({vals:selV,mat:(_bkScore[0]||selD[0]).mat,pts:pts,
27123              dice:_bkScore.map(function(dd){return{val:dd.val,mat:dd.mat};})}); /* break-then-bank — POST-split */

27149        G.kept.push({vals:selV,mat:selD[0].mat,pts,cursed:_cfBank,
27151          dice:selD.map(function(dd){return{val:dd.val,mat:dd.mat};})});         /* handleBank — PRE-split */
```

So a row written by 27121 is index-parallel and a row written by 25125 or 27149
is not — the same field, three writers, two shapes. The `mat` field diverges
the same three ways, and P514's comment at 14446-14453 names `selDice[0].mat` as
the bug it worked around. The 25125 push is the sharpest evidence in the hunt
that this is an oversight and not a design: the comment four lines above it, at
25122-25124, states the distinction explicitly for the *sibling* field —
*"`_scoreDice`, not `selDice`: selDice still carries the icon-face dice this
keep is spending, and an icon keep banks zero"* — and the very next line writes
`dice:selDice.map(...)`.

**Payload.** A brand sits only on faces 1 and 5, so an icon die *is* a 1 or a 5
in `k.dice` and is absent from `k.vals`. `canUse` can be satisfied by a plain 5
while `use`'s `filter(...)[0]` picks the branded 1 that stands earlier in pool
order, and the consumer at 24712 mints `pts:_fp.pts+(_fp.crack||0)` — 100 points
for a face that banks zero by law.

**Exposing arrangement.** Commit **via the ROLL press** a selection whose first
die in pool order shows a brand face and which also holds a plain scoring 5
later in pool order. Committing the same selection through the break-then-bank
branch (27121) writes the parallel form and hides it.

**Read:** `G.kept.map(k=>({vals:k.vals,dice:(k.dice||[]).map(d=>d.val),mat:k.mat}))`
before playing Preserve; then `CFX.preserve.canUse()`, then `G._famPreserve`
after `use`; then advance a turn and read `G.kept[0].pts` and `G.turnPts` at
24714. A finding is `_famPreserve.val` present in `k.dice` and absent from
`k.vals`. Run all three producers. *Instrument check:* assert
`k.dice.length !== k.vals.length` on at least one row, or the probe never
entered the state.

### PR3 — `sealRule` is a launch-only parameter: three copies of that fact reach the disk and the fourth, the live one, does not  — **FIXED P540**

> **CLOSED, and closed by accident.** PR3 sat undriven in this queue while I
> found the same defect from the other end - checking whether PR7's 3-point win
> was reachable led straight to `sealRule` being absent from the snapshot.
> Worth recording as such: the queue had this one written down and ranked, and
> what actually surfaced it was chasing a different, ultimately COSMETIC bug.
>
> The entry under-stated it. PR3 frames the loss as a scoring one; it is also a
> RULES one. `_ruleActive` is `G._sealRule===id`, so a resumed match lost the
> sealed seat's rule outright for the remainder of play, not just its points.
>
> P540 stores the resolved value in the snapshot and hands it back through
> `resumeMatch`. Driven both ways - exact-id round-trip (not merely truthy,
> which the `===` would have rejected), `_ruleActive` agreeing afterwards, and
> an unsealed seat still resuming unsealed.
>
> **ONE QUESTION LEFT OPEN AND UNDER MEASUREMENT.** PR3's own framing says
> `G._sealRule` is a *fourth derivation* of facts already on disk
> (`night.sealTell`, `night.handicapSeat`, `seatIdx` - and `seatIdx` was already
> a snapshot field). By that reading the right fix is to RE-DERIVE on resume,
> and storing it adds a fourth copy - the very shape this plan exists to remove.
> The counter-argument is that a rebuilt night would re-randomise
> `handicapSeat`/`sealTell` and re-derivation would then silently produce a
> DIFFERENT seal. Which of those is true depends on whether `_ensureNight` can
> rebuild mid-match, and that is being measured rather than assumed. If it
> cannot, re-derivation is the better fix and P540 should be replaced by it.

```
36038  var sealRule=isSealed?night.sealTell:null;
36079      sealRule:sealRule,
32292  G._sealRule=params.sealRule||null;
```

`saveMatchState` (10241-10326) has no `sealRule` key of any kind — while
`handicap` does, at 10251 — and `resumeMatch` hand-writes twelve params without
it:

```
10332  setTimeout(function(){showScreen('match',{
10333    rungId:snap.rungId,rung:snap.rung||null,
10334    isBoss:!!snap.isBoss,isGauntlet:!!snap.isGauntlet,handicap:snap.handicap||null,
...
10339    _resumeData:snap
10340  });},80);
```

**The two representations.** `G._sealRule` is a fourth derivation of a fact
whose three sources — `S.run.night.sealTell`, `S.run.night.handicapSeat`,
`S.pendingMatch.seatIdx` — all survive to disk. It is computed once at launch
and never recomputed, so a resumed sealed seat runs with the seal gone while
the night still says the seat is sealed.

**What moves.** Two consumers read it. `_applySeal` (11312) binds the rule to
both sides and substitutes it into the tell slot when the patron has none
(11316-11320), so the badge and every `G._tell`-gated hook change with it. And
the payout:

```
29777  var isHandicap=!!G._handicap||!!G._sealRule;
29778  var pointsEarned=win?(isHandicap?((G._sealRule&&famOwnTier('marked_table')>0)?3:2):1):0;
30580          _rubOutCircles((G&&G._sealRule&&famOwnTier('marked_table')>0)?2:1);
```

`G._handicap` is the other disjunct and is measured `null` everywhere in this
document, so after a resume a won sealed seat pays **1 circle instead of 2 or
3**, and a lost one rubs 1 instead of 2. It cuts both ways, which makes it an
exploit as well as a loss: quit and resume to play the sealed seat without its
curse.

The contrast case is in the same machinery: a **sleeved** rule survives the
resume, because `_applySleeve` re-derives it from `S.run.sleeve` at 11291. Same
mechanism, different source, only one of the two persisted.

**Read:** before quit vs after resume — `G._sealRule`;
`_ruleActive(S.run.night.sealTell,'p')`; `G._tell&&G._tell.id`; the presence of
a `.tell-badge` node; and at settle, `pointsEarned` at 29778. Also read
`S.run.night.sealTell`, `S.run.night.handicapSeat` and `S.pendingMatch.seatIdx`
off disk to confirm the fix has everything it needs to re-derive. Take at least
one turn before quitting so 24893 runs.

### PR4 — Preserve's payout is match state that no snapshot carries, while the charge that bought it is deep-cloned; and the one field that *is* carried is guaranteed null (SR-03 + SR-04 merged)

> **CLOSED — P537, driven.** The boundary snapshot means *the state at the START
> of the turn*, and a resume replays the turn from the top. Preserve paid out at
> the top of `startPTurn` — `G.kept`, `G.turnPts` — and nulled `_famPreserve`
> **before** the snapshot, so the payout was on no snapshot and the one field
> that could have re-earned it was guaranteed null.
>
> Fixed by snapshotting the **pending** state rather than the payout:
> `_famPreserveAtTurnStart` is kept for the boundary write, so the replayed turn
> pays it out again. `kept`/`turnPts` are deliberately still absent — they are
> turn *progress*, and putting them in would break the replay contract the whole
> design rests on.
>
> After: `famState.famPreserve = {val:1, mat:'amber', pts:100, crack:0}`.
>
> **One correction to my own evidence.** The pre-fix measurement read
> `snapshot.famPreserve` at the top level; the field is nested inside
> `famState`. Right conclusion, wrong path — the guaranteed-null claim holds by
> construction (the payout nulls `_famPreserve` before the snapshot runs) and the
> measured "before" I have is for `kept`/`turnPts`, which were genuinely absent.

These were nominated separately, from the count side and the tray side. They are
one defect: `startPTurn` pays Preserve out and then, 180 lines later, snapshots
a turn boundary that records none of the payout.

```
24709  if(G&&G._famPreserve){
24710    var _fp=G._famPreserve;G._famPreserve=null;
24712    G.kept=[{vals:[_fp.val],mat:_fp.mat||'bone',pts:_fp.pts+(_fp.crack||0),
24713             dice:[{val:_fp.val,mat:_fp.mat||'bone'}]}];
24714    G.turnPts=G.kept[0].pts;
24727    _dropLanes(1);/* P516 */
...
24893  saveMatchState();
```

against the snapshot and its restore:

```
10256    pPts:G.pPts,oPts:G.oPts,target:G.target,turnNum:G.turnNum,numDice:G.numDice,
10323    famPreserve:G._famPreserve?JSON.parse(JSON.stringify(G._famPreserve)):null,
32361    G.pPts=rd.pPts;G.oPts=rd.oPts;G.turnNum=rd.turnNum;G.numDice=rd.numDice;
24582  G.phase='idle';G.turnPts=0;G.kept=[];G.numDice=G.matchDice?G.matchDice.length:6;
```

**Two representations, two failures, one cause.**

(a) `famPreserve` is cloned at 10323 by a writer that runs 183 lines after
24710 has already nulled it, on the same unconditional path — so the field can
never carry a live value from the turn-boundary writer. The comment at
10272-10277 makes exactly this observation about `_fairTrade` (*"Always null
HERE"*) and justifies keeping the field because `_removeDieAt` writes the same
dice mid-turn; no mid-turn writer carries `famState` at all except the
Fair-Trade branch at 19280, which is PR5.

(b) `numDice` is saved (10256), mapped back (32361) and then overwritten
unconditionally by 24582 two hundred milliseconds later — `_matchStartDelay` is
200 on a resume (32571) and `startPTurn` is on that timer (32635). The
snapshot's `numDice` is legitimately lower than `matchDice.length`, because it
is written at the *end* of `startPTurn`, after `_dropLanes(1)` at 24727. The
restore line is decoration: the penalty existed only in the derived count, and
the derived count is recomputed away. This is the P514/P516/P517
recompute-versus-decrement rule, reappearing across the save boundary instead of
inside one turn — the fifth instance.

Meanwhile the **cost** is in `famState.pF`, deep-cloned and restored (32470).
Charge spent, tray empty, `turnPts` 0, lane handed back.

**Exposing arrangement.** Play `preserve` on turn N, bank, let the rival answer,
let turn N+1 begin so 24709-24743 pays out and the die is minted into `#keptRow`
at 24734-24741. **Do not roll.** Force-quit; resume. The complementary arm —
quit *before* turn N+1 starts — must also be run: there the snapshot pre-dates
the play, so charge and effect should rewind together, which separates "resume
loses the effect" from "resume rewinds the whole play".

**Read:** on disk at the quit — `S.pendingMatch.famState.famPreserve` (predicted
null), the preserve instance's remaining charge in `famState.pF` (predicted
already spent), `S.pendingMatch.numDice` against
`S.pendingMatch.matchDice.length` (predicted 5 against 6). After the resume
mapper but before the 200 ms timer — `G.numDice` (predicted 5). After
`startPTurn` — `G.numDice` (predicted 6), dice dealt into `#playerDiceRow`
(predicted 6), `G.kept`, `G.turnPts`, `#keptRow` children, and the charge count.

*Adjacent, not nominated:* `G._oTarPit` is decremented at 24574 with
`G.numDice=Math.min(G.numDice||6,5)` **eight lines above** 24582's recompute. I
found no assignment of `_oTarPit` anywhere (five occurrences: 13093, 13137,
24573, 24574, 28092, and Tar Pit is recorded retired at 14470), so it is
probably dead — but a grep zero is not a finding here, and if a writer exists
this is a sixth instance in the same function. Settle it by instrumenting 24574,
not by searching for the name.

### PR5 — `_removeDieAt` has two exits with opposite snapshot policies, and the Fair-Trade exit calls the full `saveMatchState()` seventy lines above a comment forbidding exactly that

> **CLOSED — P536, driven.** One function, two exits, opposite policies. The
> main exit writes only the dice fields under a comment forbidding the
> alternative *in terms* and citing a measured exploit for it; the Fair-Trade
> exit, seventy lines above that comment, called the full `saveMatchState()`.
>
> Not a comment being wrong about code — the class found three times tonight.
> **Code violating an explicit warning** left by whoever measured the exploit,
> in the same function.
>
> `_snapDiceOnly()` now holds the targeted write and both doors call it, so they
> cannot drift and the rule lives in a named function rather than a comment
> beside one of the two places that needed it.
>
> **Driven against the exploit the comment describes**, on the Fair-Trade path:
>
> | | |
> |---|---|
> | live `pPts` mid-turn | 500 |
> | snapshot `pPts` after the break | **0** — the boundary held |
> | `matchDice[2]` | obsidian → flint, the owner's die back |
> | snapshot `matchDice` | followed |
>
> Both halves asserted deliberately: writing *nothing* would be as wrong as
> writing everything, since a resume has to know the owner's die walked back in.
>
> `G._ftDead` is match-scoped and dies with `G` by design, so it is in neither
> door's snapshot — checked, not assumed.

```
19267  try{
19268    var _ftB=G._fairTrade;
19269    if(_ftB&&_ftB.lane===lane){
19270      G._fairTrade=null;
19271      G.matchDice[lane]=_ftB.was;/* its owner walks back in */
19274      G._ftDead=(G._ftDead||[]).concat([_ftB.borrowed]);
19277      G.pool=(G.pool||[]).filter(function(q){return q.lane!==lane;});
19280      try{saveMatchState();}catch(e){}
19281      return true;
19282    }
19283  }catch(e){}
```

```
19353     DO NOT call saveMatchState() here. That snapshot means "the state at the
19354     START of a player turn" - startPTurn's last line is its only other
19355     writer - and a resume replays the turn from the top. Rewriting all of it
19356     mid-turn re-timestamps what the replayed turn is meant to hand back:
19357     measured, a Break landing after a shatter bonus and a spent active card
19358     moved the snapshot's pPts 0 -> 500 and recorded second_wind as used, so
19359     the resumed turn charged the player for a card use on a turn that never
19360     happened, and banked points it then let them earn again.
```

**The two representations.** `S.pendingMatch` as a whole record, whose declared
meaning is start-of-turn, against the six-field dice-only subset the same
function writes on its other exit (19372-19392). One record, one timestamp
semantics, two writers inside one function — and the early-returning one carries
the whole thing. `saveMatchState` refuses nothing here: its only guard is
`G._practice||G._endMatchFired` (10240).

**Exposing arrangement.** A live Fair Trade loan whose borrowed die is an
Obsidian — per 19243-19249 the passive shatter sweep is stated to be the only
remaining caller that reaches this branch, Break having been banned from
borrowed dice. Within one player turn: score something so `G.pPts` moves and/or
spend a familiar charge, then let the shatter fire so 19269 runs. Quit; resume.

**Read:** `S.pendingMatch.pPts`, `.activeCardState`, `.npcCardState.usedOnce`
and `.famState.pF` charge counts immediately before the shatter and immediately
after 19280 returns — the claim is that they moved mid-turn. Then the same
fields plus live `G.pPts` at the top of the replayed turn, against the identical
arrangement resolved by a plain Break, which routes through the 19372 subset
writer and should leave the snapshot's `pPts` unmoved.

### PR6 — `S.run` is written mid-turn and cannot be rewound; the snapshot only rewinds match state, so a replayed turn pays the same brand twice  — **FIXED P539**

> **CLOSED.** Driven, then fixed, then re-driven through a real `resumeMatch()`.
>
> The measurement, control first: the snapshot carries 52 keys and **none** of
> them is run-scoped, while the same reads see `matchDice` fine - so the
> absence is real and not a blind instrument. Tithe took gold 500 -> 515 on the
> commit, **515 on disk immediately** (its `fire` calls `save()`), and -> 530
> when the same commit was replayed. Hair of the Dog confirmed the opposite
> direction: armed, persisted, consumed mid-bank, and no record anywhere.
>
> P539 stashes both at turn start beside the P537 pair, persists them as
> `runGoldAtTurnStart` / `runHotdAtTurnStart`, and rewinds them on resume.
> `saveMatchState` has exactly ONE call site in code (startPTurn:24996, after
> the stash), so a mid-turn value can never be stamped in as the turn-start one.
>
> **The verification's second arm is the load-bearing one.** Earn 15 in turn
> one, cross a boundary, earn 15 in turn two, resume: 500 / 515 / 530 / **515**.
> A fix that rewound too far gives 500; one that did not rewind gives 530. Only
> a fix that rewinds to the CURRENT turn's start can produce the middle number,
> so the arm separates a correct fix from two distinct wrong ones.
>
> Sixth resume-path bug. The base rate that put PR6 next was right again.

```
18342  tithe:{name:'Tithe',price:150,glyph:'◉',ink:'#d8b054',doubles:true,
18343    desc:'Brand a coin on one face. Keep it: it banks nothing and pays you 15 gold.',
18344    fire:function(c){
18345      _getS();var g=15*(c.mult||1);
18346      S.run.gold=(S.run.gold||0)+g;try{save();}catch(e){}
```

**The two representations** are the two saved records a resume treats
differently: `S.pendingMatch`, rewound to the start of the turn, and `S.run`,
never rewound. The reasoning at 19353-19360 covers one direction only — it
protects the replayed turn from being re-**charged** — and says nothing about it
being re-**paid**.

Tithe is not alone. Two more run-scoped writes fire inside a match and persist
immediately:

```
27681      total*=2;S.run._hotdNext=false;try{save();}catch(e){}      /* Hair of the Dog, consumed */
27689      S.run.gold=(S.run.gold||0)+5;try{save();}catch(e){}        /* Corvus's Ledger, +5g per bank */
```

Both sit inside `handleBank`'s bank block, after the last boundary snapshot and
before the next one, so a quit taken there keeps the gold and the spent
doubling while the bank itself rewinds. Hair of the Dog runs the *other* way —
the player loses a consumable for a bank that never happened.

**Exposing arrangement.** A die carrying the `tithe` brand. Roll until the
branded face shows, commit it so `fire` runs and the famLog line appears, do not
bank, force-quit, resume, and make the same commit again. Kindred doubles
`c.mult`, so the second arm should read 30 rather than 15 and distinguishes a
real double-pay from a misread single. The Corvus arm needs the relic in the
loadout and a quit immediately after a bank.

**Read:** `S.run.gold` immediately before the commit, after `fire` returns, on
disk at the quit, after the resume mapper, and after the replayed commit —
predicted `g, g+15, g+15, g+15, g+30`. **Control:** the same turn played to a
bank with no quit, ending at `g+15`. Worth sweeping the rest of `ENCH_GRID`'s
`fire` handlers for other run-scoped writes on the same pattern.

### PR13 — two die renderers, two material tables, and ten materials only one of them knows  — **PARTLY FIXED P544**

> **The three `.dtype` copies AGREE.** 72 rules, 24 names, each appearing
> exactly 3x, byte-identical with comments stripped - measured on the running
> page. My worry that they had diverged is refuted; it is a maintenance hazard,
> not a colour bug.
>
> **`.dtype-lucky` did not exist at all,** and there is no `--dface` default, so
> a lucky die drawn by the grid-pip renderer resolved every custom property to
> nothing. P544 adds it to all three blocks - patching one would be the first
> thing to make them disagree - tinted from `D3X.MATCOL.lucky` so 2D and 3D
> agree.
>
> **STILL OPEN, needs a design call:** both grid-pip builders index
> `dice.faces` by ARRAY POSITION, so opposite faces do not sum to 7 on any
> material. Pairing largest-with-smallest fixes the 14 materials whose multiset
> is {1..6}; for the other 10 no arrangement can sum to 7, so it is a question
> about those dice, not a bug to patch. Do NOT reorder `DICE_TYPES.faces` to
> fix it - seven display sites join it in stored order and rely on ascending.
>
> Also still open: the `D3.TINT` / `MATCOL` gap for brass, crystal and the
> eight relics, whose player-visible reachability is still unestablished.


**NOT DRIVEN AS A PLAYER-VISIBLE BUG YET — the divergence is measured, the
on-screen consequence is not.**

The game draws dice two ways:

- **`D3`** — DOM/CSS. `d3slot > d3die > 6 x div.d3f`, one set of face art
  (`Art/Assets/Dice/bone_1..6.png`), and a **CSS filter string** per material
  out of `D3.TINT`. This is what the new-run offering screen shows; confirmed
  by driving the page (`hasTHREE` false, zero canvases in the overlay).
- **`D3X`** — three.js. Boots async, takes over only `group==='match'`. Owns
  the GLB, `MATCOL` hex tints and the painted `SKINS`.

```
D3.TINT   12 materials
D3X.MATCOL 22 materials
in MATCOL and NOT in TINT:
  brass, crystal, grogs_tooth, mabels_thimble, finnicks_palm,
  corvus_ledger_d, brutus_shield, aldrics_square, whispers_fang,
  ambrose_weight
```

`D3.make` reads `D3.TINT[opts.mat]||''`, so those ten get an **empty filter and
render as plain bone** wherever D3 draws. `_RELIC_FAM` does not help: it is
used only by `_matFam` for Break's family effects, never on a render path.

**Why this is worth a look.** MATCOL's own comment says the relic tints were
given distinct colours *specifically* so "a relic on the table was
indistinguishable from the ordinary die it is meant to be a trophy version of"
would stop being true. That fix was applied to one renderer. On the other, all
eight relics are still bone.

**What is NOT yet established, and must be before this is called a bug:**
whether a relic or brass/crystal die is ever actually drawn through `D3` on a
surface a player sees. `D3.make` has two call sites - the offering screen
(starter materials only) and the match row - and on the match row `D3X` takes
over once it boots. So the real question is what a player sees **before D3X is
ready**, and in the loadout panel. Reachability first, exactly as the
`brass`/`crystal` MATCOL entries were wrongly claimed reachable once already.


### PR7 — The chalkboard's count and its per-circle history: one win adds 3 to the count and 2 to the list, and the file says in writing that they must move together  — **FIXED P541; and it turned up P540, which matters more**

> **CLOSED.** Driven by extracting the real lines and evaluating them, not by
> reading them: `pointsEarned` is 3 for win+seal+Cursed Table, and the board
> goes 3/2, then 6/4, then 9/6. The defect is one character wide - line 30707
> gated the second push on `route._earned>=2`, **a boolean where a count is
> needed**. Reachability confirmed on the ordinary patron path: every night
> gets a sealed seat, and `isHandicap` is `!!G._handicap||!!G._sealRule` while
> `launchSeat` hard-codes handicap null, so the seal alone satisfies it.
>
> **THREE THINGS I WROTE HERE WERE WRONG AND ARE STRUCK:**
> 1. *"nothing repairs it / permanently one short"* - false. `_rubOutCircles`
>    floors points at 0 and converges the gap; three other writers zero both
>    together. Drift is bounded to the current tier's board.
> 2. *"the divergence widens"* - false. Flat +1 per cursed-table win.
> 3. The implied severity - **this half is COSMETIC.** `S.run.points`, the
>    number the boss unlock reads, was always correct; `_chalkMeta` feeds only
>    the crown glyph and circle FILL comes from points. The visible error needs
>    a second meta-pushing event AND a crown landing inside `tier.pointsNeeded`.
>
> **P541** pushes one entry per point. Identical for earned 1 and 2 - every
> other win in the game - and driven as such; only the 3 case changes. The
> migration PADS THE TAIL rather than re-gating the existing rebuild on length,
> because that branch fills all-'face' and would erase every crown it touched.
>
> **P540 came out of checking PR7's reachability, and outranks it.** `sealRule`
> was in no snapshot field and `resumeMatch` never passed it, so a force-close
> and resume set `G._sealRule` null. `_ruleActive` is `G._sealRule===id`, so the
> seat's **rule** died too; scoring followed, with `pointsEarned` 3 -> 1 and the
> cursed-loss rub 2 -> 1 - resume **punished a win and paid for a loss**.
> Driven both ways: the seal round-trips as its exact id (not merely truthy,
> which `_ruleActive`'s `===` would have rejected), `_ruleActive` agrees, and an
> unsealed seat still resumes unsealed - the arm that would have sealed every
> ordinary seat.
>
> **Seventh bug in the resume path.** Found while checking something else,
> which is the third time tonight that has been the more productive route.

```
13169 /* RUB OUT N CIRCLES. The chalk board is TWO structures - S.run.points is the
13170    count and S.run._chalkMeta is the per-circle history - and they must move
13171    together or the board disagrees with its own record. ... */
13179     S.run.points=Math.max(0,(S.run.points||0)-1);
13180     if(Array.isArray(S.run._chalkMeta))S.run._chalkMeta.pop();
```

The loss side honours it. The win side does not:

```
29778  var pointsEarned=win?(isHandicap?((G._sealRule&&famOwnTier('marked_table')>0)?3:2):1):0;
...
30560    route._earned=route.pointsEarned||1;
30561    S.run.points+=route._earned;
30564    S.run._chalkMeta=Array.isArray(S.run._chalkMeta)?S.run._chalkMeta:[];
30565    S.run._chalkMeta.push('face');
30566    if(route._earned>=2)S.run._chalkMeta.push('crown');
```

**The write that moves one and not the other:** `_earned===3` — a sealed seat
won while the player owns `marked_table` — adds 3 to the count and 2 to the
list. Nothing repairs it afterwards: the rebuild-from-count at 9566 is gated on
`!Array.isArray(S.run._chalkMeta)`, false once the array exists. The loss side
is symmetric (`_rubOutCircles(2)` at 30580 takes 2 from both), so one 3-point
win followed by any loss leaves the list permanently one short, and the renderer
indexes the list by circle position:

```
35789  for(var i=0;i<need;i++){
35790    var isFilled=i<filled;
35791    var isCrown=isFilled&&meta[i]==='crown';
```

Every crown after the drift renders on the wrong circle, and the results screen
draws `pointsEarned` marks (29936, 29973), so the two surfaces disagree about
the same win.

**Exposing arrangement.** Own `marked_table` (it is in the FAM_LIVE enable list
at 14479). Play the night's `handicapSeat` — `night.sealTell` is rolled for
every night (35815/35824) and `G._handicap` is hardcoded null at 36039, so the
sealed seat is the only live producer of `isHandicap`. Win it, win a plain seat,
then look at the board. Note PR3: if the sealed seat was **resumed**, `_earned`
is 1 and this does not fire — the two defects mask each other.

**Read:** `S.run.points` and `S.run._chalkMeta` (the array, not its length)
either side of the 30557 branch, plus `route.pointsEarned`; then which
`.cb-circles` index carries `.cb-crown` against which win was the sealed one.
Second arm: lose a sealed seat while the list is already short and read whether
`_rubOutCircles` empties the list while `points` is still positive.

### PR8 — The shatter sweep purges `G.pool` unconditionally and removes the seat conditionally, and it is the only one of three callers that ignores `_removeDieAt`'s refusal

> **REFUTED — driven, and the flagged contradiction with G5 resolves in G5's
> favour.** The report said PR8 survived only on the two-die arm and had to be
> reconciled with G5's kill before probing. It was, and the two-die arm dies too.
>
> ```
> _removeDieAt returns   [true, false]      the floor engaged on the second
> after the sweep        matchDice 1, numDice 1, pool 0    counts LEVEL
> next deal              pool 1, lanes [0]                 the die is back
> ```
>
> The description was accurate — the purge *is* unconditional while the seat
> removal is conditional — but the inference was wrong. A refusal skips
> `_dropLanes` as well, so the two representations move together or not at all,
> and the refill restores the die on the next deal.
>
> **One real thing came out of it:** the P528 comment justified the unconditional
> purge with *"_removeDieAt has already filtered the pool by lane"*, which is
> false on a refusal. Right behaviour, wrong reason — corrected in P536b rather
> than left as a fourth false-safety claim.
>
> Kept unconditional deliberately: that is what closes D24's stranded laneless
> die, the case the old `else` could never reach.

```
25541    if(_shLanes.length)_shLanes.forEach(function(L){_removeDieAt(L,{permanent:false});});
25542    /* P528: UNCONDITIONAL, was an `else`. ...
25547       Safe and idempotent here - _removeDieAt already filtered the pool by lane,
25548       so what reaches this line is exactly the set the `else` existed for. */
25549    G.pool=G.pool.filter(function(d){return !d._shattered;});
```

against the floor:

```
19242  if(G.matchDice&&G.matchDice.length<=1)return false;
```

**The two representations** are `G.pool` — what is on the table this roll — and
`G.matchDice`/`G.numDice` — how many seats exist. `_removeDieAt` is the one
writer that moves both together. On a refusal it moves neither, and 25549 then
removes the die from the pool anyway; its element was already gone on the 420 ms
timer at 25507. The claim at 25547-25548 is false in exactly that case.

The other two callers handle the refusal. `CFX.sacrifice` re-tests the floor
itself at 14322 with the reason written above it (*"testing afterwards would
leave a visually destroyed die still sitting in the pool"*), and `steal_die`
captures the return (`var _seized=_removeDieAt(...)`, 24832/24847). The sweep
does neither.

**CONTRADICTION, AND IT MUST BE SETTLED BEFORE THIS IS PROBED.** The same code
was nominated twice in this hunt. The other nomination (G5, refuted below) kills
the single-die case on three grounds I could not fault: on a refusal
`_dropLanes(1)` is also skipped so `numDice` stays equal to `matchDice.length`;
`startPTurn` reconciles pool and count in one statement (24582) before anything
reads them again; and reverting 25549 to conditional reopens D24, which P528
closed. What survives here beyond that kill is narrow and specific: **the
two-die arm**. `matchDice.length===2` with both dice shattering on one roll
gives `_shLanes [1,0]`; the first call succeeds and takes the length to 1, the
second hits the floor while 25549 still removes it from the pool. The 19240
promise — *"If Obsidian shatters the last die it now cracks and holds"* — is not
kept on that path, and the turn continues with an empty pool.

**Read:** the return value of each `_removeDieAt` call inside the 25541 forEach;
then immediately after 25549, `G.matchDice.length`, `G.numDice`,
`G.pool.length`, `G.pool.map(d=>d.lane)` and `#playerDiceRow`'s child count;
then whether control reaches the bust check at 25687 with `freeV` empty and what
the next `startPTurn` deals. **Negative control:** `matchDice.length` 3 with one
shatter, where the removal succeeds and the three numbers agree.

### PR9 — `npcCardState.playerTurnCount` is incremented before the snapshot its sibling is incremented after, so every resume counts the replayed turn twice

> **CLOSED — P537, driven.** Two counters of one fact. `turnNum` is bumped in
> `runOppTurn`, *after* the boundary snapshot; `playerTurnCount` was bumped
> inside `startPTurn`, *before* it. So a restore replayed the turn and
> incremented again, and repeated resumes compound. `periodic_drain` fires on
> `playerTurnCount % interval`, so a force-quit could skip or trigger a drain.
>
> | | before | after |
> |---|---|---|
> | snapshot `playerTurnCount` vs live | 6 vs 6 | **5** vs 6 |
> | restore + replay | 6 → **7** | 6 → **6** |
> | `turnNum` immune | yes | yes |
>
> **The increment is deliberately NOT moved.** `block_activations` and
> `limit_activations` read this counter *during* the player's turn. Both sit on
> the dead `pCards` layer today, and "currently unreachable" is not a reason to
> change when a counter advances — so only what gets persisted changed.

```
24746  G.npcCardState.playerTurnCount++;
24893  saveMatchState();
10310    npcCardState:JSON.parse(JSON.stringify(G.npcCardState||{})),
32384    if(rd.npcCardState)G.npcCardState=rd.npcCardState;
```

against the sibling counter of the same fact:

```
27826  G.phase='opp';G.turnPts=0;G.kept=[];G.numDice=6;G.turnNum++;
```

**Two counters of one fact — how many player turns this match has had.**
`turnNum` is bumped inside `runOppTurn`, *after* the boundary snapshot, so
restoring it and re-entering `startPTurn` does not double it. `playerTurnCount`
is bumped at 24746, *before* the snapshot at 24893, so restoring it and
re-entering `startPTurn` does. Repeated resumes compound. The consumer:

```
27525    if(npc.effect.mechanic==='periodic_drain'&&G.npcCardState.playerTurnCount>0&&G.npcCardState.playerTurnCount%npc.effect.interval===0){
```

**Read:** `G.turnNum` and `G.npcCardState.playerTurnCount` at the top of turn N,
on disk at the quit, and at the top of the replayed turn — predicted
`N/N/N` and `N/N/N+1`. For a behavioural consequence rather than a bookkeeping
one, confirm a `periodic_drain` card is actually in the boss's dealt `G.oCards`
first rather than assuming one exists, then read `G.pPts` across the rival's
answering turn against a no-quit control of the identical turn sequence.

### PR10 — Three mid-turn mutators of the same dice record carry three different subsets of it, and one carries none; the comment claiming they match is wrong

> **CLOSED — P538, driven.** Measured rather than read off the nomination:
> `_snapDiceOnly` wrote six fields and not `matchOppDice`; `_tradeSnap` wrote
> four including it; **`_commitVagabondDrag` wrote nothing at all** — its body
> filtered for `save(`, `saveMatchState`, `pendingMatch`, `_snapDiceOnly` and
> `_tradeSnap` came back empty on every one.
>
> **The third one is mine.** P520 made the reorder real, P530 taught it to carry
> the loan's seat and P531 the trade ledger's — and none of it was persisted, so
> a quit after a drag lost the whole permutation *and* both carries. Fifth bug in
> the resume path tonight.
>
> **One writer, three callers, one flagged difference.** The field-set difference
> is legitimate — a trade swaps a die with the rival and must persist
> `matchOppDice`; a removal or a reorder must not — so `_snapDiceOnly(alsoOpp)`
> puts that single difference in one place instead of letting three writers each
> hold their own idea of the record. Forcing the sets identical would have been
> the mirror of the mistake this cluster keeps finding.
>
> | | |
> |---|---|
> | reorder, live matchDice | `[iron, flint, lead, bone, amber, brass]` |
> | reorder, snapshot | identical — it follows now |
> | loan lane / ledger lane | live 3 / snap 3, both |
> | plain snapshot vs rival board | left alone |
> | trade snapshot vs rival board | written |
>
> The last two are the control: a fix that made everything write `matchOppDice`
> would have passed the first three.
>
> Also corrected: `_tradeSnap`'s claim to be *"exactly the shape `_removeDieAt`
> uses, for exactly the same reason"* — false, the sets differed. Fourth
> in-source false claim of the session.

```
18581    replayed turn for everything it has already spent. Exactly the shape
18582    _removeDieAt uses, for exactly the same reason.
18588 function _tradeSnap(){
18591     S.pendingMatch.matchDice=[...G.matchDice];
18592     S.pendingMatch.matchOppDice=[...G.matchOppDice];
18593     S.pendingMatch._enchArr=[...(G._enchArr||[])];
18594     S.pendingMatch._tradeSwaps=G._tradeSwaps?JSON.parse(JSON.stringify(G._tradeSwaps)):null;
```

`_removeDieAt`'s subset (19374-19390) writes six fields — `matchDice`,
`_enchArr`, `numDice`, `_fairTrade`, `_tradeSwaps`, `_diceOut` — and **not**
`matchOppDice`. `_tradeSnap` writes four, including `matchOppDice`. So the
asserted shape equality at 18581-18582 does not hold; it is the same class of
false in-source claim as P517, P523 and D2.

The consequence lives in the third mutator. `_commitVagabondDrag`
(37011-37129) permutes `matchDice`, `_enchArr`, `_fairTrade.lane` and
`_tradeSwaps[].lane`:

```
37078            if(_ftBefore>=0&&c.die&&c.die.lane===_ftBefore)G._fairTrade.lane=_slots[i];
37083            if(G.matchDice&&L<G.matchDice.length&&c.mat!==undefined)G.matchDice[L]=c.mat;
37084            if(G._enchArr&&L<G._enchArr.length)G._enchArr[L]=c.ench;
37085            c.die.lane=L;
```

and calls no writer at all — I filtered the whole function body for `save(`,
`saveMatchState` and `pendingMatch` and got zero. A quit after a drag and before
any removal or Trade resumes the pre-drag seating; a `_removeDieAt` or a Trade
afterwards silently rescues it through its own writer, which is why the ordering
is the arrangement.

**Read:** `G.matchDice`, `G._enchArr`, `G.pool.map(d=>d.lane)`,
`G._fairTrade&&G._fairTrade.lane`, `G._tradeSwaps.map(t=>t.lane)` right after the
drag; the same five off `S.pendingMatch` at the quit; the same five off live `G`
after the resume. Predicted: new permutation live, old one on disk, old one
restored. **Second arm:** drag, then Break — the reorder must survive, or the
probe is reading noise. Sharpest with position-scoring cards equipped and a live
loan, so `_fairTrade.lane` moved too.

### PR11 — Fair Trade's gate proves a lendable die exists; its action adds a rank test and refuses in silence, so the sheet offers PLAY and nothing happens  — **FIXED P542**

> **CLOSED.** `dieRank` is the SHOP PRICE, which is what makes this common:
> bone, lucky and all eight relics cost 0, and the test is `<=`, so each ties
> with a bone seat and refuses. The two paths that produce it are REWARDS -
> take the boss relic, or take a die at For Keeps, where every generated patron
> carries a lucky die so a cost-0 prize is always offered. The window reopens
> every player turn. Measured 7 silent states of 17; the charge is not spent,
> so nothing is lost but the tap - and the uses-left counter not moving is
> exactly why no surface tells the player anything happened.
>
> Fixed the way P519 fixed Sacrifice: eligibility in ONE place, read by canUse
> and use alike. `_pick()` returns the trade or null and deliberately does not
> log. Driven on 9 states: gate and action agree on all of them, and both
> working trades still fire and still change the board - the control that a
> "make canUse always false" fix would have failed.


```
12971    return !!(G&&!G._fairTrade&&(G.phase==='idle'||G.turnRollCount===0)&&
12972      (S.run.diceInv||[]).filter(function(_d){
12973        return (G._ftDead||[]).indexOf(_d)<0;}).length);},
...
12982    if(!inv.length||!G.matchDice||!G.matchDice.length)return false;
12988    if(dieRank(inv[best])<=dieRank(G.matchDice[worst]))return false;
```

```
13147  if(fx.canUse&&!fx.canUse(inst)){famLog('NOT NOW');return;}
13148  if(fx.use(inst)){inst.charges--;famRenderRow();}
```

**The two representations** are the gate's condition (a non-empty, non-dead
stash) and the action's (that, plus a stash die outranking the weakest seat).
`famUse` logs `NOT NOW` when the **gate** refuses and prints nothing at all when
the **action** does. There is in fact a third: `famCardTap`'s `usable` at 13129
is `d.kind==='active'&&inst.charges>0&&CFX[inst.id]&&CFX[inst.id].use` — it
never consults `canUse`, so the sheet says PLAY on charges alone.

The correct pattern is already in the file, written by P519 for Sacrifice, four
hundred lines below: *"eligibility in ONE place, read by canUse and use alike,
so the button can never offer a sacrifice that use() then refuses"*
(14299-14301, with `_targets()` at 14306). It did not travel.

**Read:** with a stash holding only dice ranked at or below the weakest die in
the loadout — `CFX.fair_trade.canUse(inst)` (expect true), `dieRank(inv[best])`
against `dieRank(G.matchDice[worst])`, the return of `use` (expect false),
`inst.charges` either side, `G._fairTrade` (expect null), and the last entry in
the fam log queue — an empty log after a PLAY press is the player-facing half.
*Instrument check:* add one better die to the stash and require the same
sequence to produce a non-null `G._fairTrade`.

### PR12 — The die-tap flourish scores the unsplit selection; every other path splits icons out first, for a reason its own neighbour states  — **FIXED P543, severity corrected DOWN to feedback-only**

> **CLOSED, and it is smaller than this entry claimed.** `pts` in `toggleDie`
> has exactly ONE consumer, the `if(pts>0)` VFX branch; it writes nothing to G
> and nothing to the DOM, and `refreshSelUI()` - which splits correctly - is
> the function's last statement. So the player got a pop, a commit sound and a
> heavier haptic, and then read a correct number. No score was ever wrong.
>
> Real all the same, and reachable without any relic: a brand bought through
> the shop's own path reproduces it, and it survives a force-close and resume.
> This was the only live site handing `scoreSelection` the raw selection.
>
> Driven with the control that mattered: branded 1 alone 100 -> 0, a branded 1
> beside a plain 5 still flourishes at 50 (the 5 alone), plain 1 unchanged at
> 100. A fix that suppressed the flourish whenever an icon was present would
> have closed the bug and broken every mixed keep.


```
24515      var selD=G.pool.filter(function(x){return x.sel&&!x.committed;});
24516      var _tdCtx=_pCrowsForScore()||{};_tdCtx._bookendsEligible=_bookendsEligible(selD);
24517      var pts=scoreSelection(selD.map(function(x){return x.val;}),effectiveCards(),
24518        G.kept.reduce(function(a,k){return a+k.pts;},0),_tdCtx,
24519        selD.map(function(x){return x.mat;}));
24520      if(pts>0){
```

against 26097-26101, 25024-25026 and 27045-27046, all of which pass
`_splitIcons(...).rest`:

```
26097  /* icons are withheld from the maths here for the same reason as at commit:
26098     the engine must never see a die it would happily score. Without this a
26099     branded 1 previewed as +100 and then banked nothing. */
```

**Two readings of one question, ten lines apart:** `toggleDie` fires the scoring
flourish (`die-sel-pop`, `SFX.commitAt`, the stronger haptic) for a branded 1,
and `refreshSelUI()` one call later (24562) correctly previews it as worth
nothing. 24517 is also the only call site that omits the enchant argument
entirely, so it is the odd one out twice.

**Read:** on one tap of a branded die showing its brand face, the `pts` at 24517
and the `pts` at 26115 for the same selection, side by side, plus whether
`.die-sel-pop` was applied and `SFX.commitAt` called. Two numbers for one
selection is the finding. *Instrument check:* tap a plain scoring 1 and require
both numbers to agree.

### DEMOTED — `_famDiceMigrate` vs `S.run.dieEnchInv` (K2, settled by PA3)

The code reading is right and verifies verbatim: 9452-9456 filters `diceInv`
and never `dieEnchInv`, and `_enchInit` then "reconciles" them by length alone
(`while(S.run.dieEnchInv.length<(S.run.diceInv||[]).length)...push(null);` /
`S.run.dieEnchInv.length=(S.run.diceInv||[]).length;`, 19608-19609), which
shifts every stash brand at or above the removed slot and deletes the tail. K2's
own probe instruction was *"reachability must be established first… if no live
save carries a retired material in `diceInv` this is a latent hazard, not a
bug — say so rather than filing it."* PA3 did that census and it comes back
empty, and I re-ran the parts that mattered: `'brass'`, `'crystal'`, `'ruby'`
and `'jade3'` appear in exactly seven places in the file (12301, 12305, 12320,
12330 — the `DICE_TYPES` entries themselves — and 12461/12465, two `PERSONAS`
`dieBias` arrays), and 11623 filters `dieBias` against `ps.dicePool`, whose
eight definitions (10993-11030) are bone/iron/lead/flint/amber/jade/jade2/
starstone only. The file states the same conclusion and retracts an earlier
claim to the contrary at 19820-19836. **Latent hazard, not a survivor.** It
becomes live the moment any retired material enters a pool or the shop, and the
fix is to filter the two arrays as a pair rather than equalise their lengths.

---

## PRESERVE — CLOSED, P534, and the shared fix was not the obvious one

Denis asked whether the siblings wanted one shared fix **before** anything was
touched. They did, and asking first changed what got written.

**Driven before fixing.** A real commit of a triple plus a branded 1:

```
k.vals   [3,3,3]                                  the split works
k.dice   [3/bone, 3/iron, 3/flint, 1/flint]       the branded die is IN
dice entries carry brand info:  FALSE
```

Preserve, given that row and a second row holding a real 5, **banked the
branded 1 for 100 points** and passed over the legal 5 worth 50. A branded face
banks **zero by law** — that is what `_splitIcons` enforces — and brands sit on
faces 1 and 5, which are the only faces Preserve hunts.

**The obvious fix was impossible.** "Make Preserve filter icons out of `k.dice`"
cannot be written: the entries were `{val,mat}` and carried no brand, so **no
consumer could tell an icon die from a plain one.** The reader was not the
broken part. The record was.

**Two roles, one field.** `k.dice` is the *display* record — `refreshKeptTray`
renders every entry, and a branded die the player committed belongs there.
Preserve reads the same field as a *scoring* record. Both readings are
legitimate; the field could only serve both once it said which dice were which.

So: every producer now records `ench`, and `_keptScorers(k)` is the canonical
"which of these could score" accessor. It **reuses `_dieIsIcon`** — the same
predicate `_splitIcons` itself uses — so the split and the filter cannot drift,
which is exactly how the two lists stopped agreeing in the first place.

| | result |
|---|---|
| branded 1 vs legal 5 | takes the **5 on amber for 50** — was the branded 1 for 100 |
| control, a plain 1 | still preserved, 100 points, unbroken |

**Flagged, not changed.** The three producers disagree about whether `k.dice`
holds the whole selection or the post-split subset — two write the full
selection, one writes `_bkScore`. Adding `ench` is safe and additive; making the
odd one consistent would change what the kept tray renders on that path, and
whether that tray is ever seen has not been established. Recorded rather than
guessed at, on the same reasoning that stopped the trim-and-discard fix.

---

## IS PRESERVE ISOLATED?

**No. It is the most expensive member of a family, and the family has at least
four unrelated branches.** Two answers, at two scopes, with different
confidence.

**Narrow scope — gate-and-action pairs among the live familiar cards: Preserve
is currently unique, and that is not reassuring.** I read all nine `CFX` cards
with both a `canUse` and a `use`. `steady_hand` (12917/12927) and `encore`
(13025/13028) write the *same predicate twice*, which is the shape but cannot
drift. `honeytrap` (14381/14388) walks `k.vals` on both sides. `sacrifice` was
consolidated by P519 into a single `_targets()` read by both, with a comment
naming the rule. `fair_trade` (PR11) adds a condition in `use` that `canUse`
does not test — a divergence, but of the same *array*. Preserve is the only one
whose gate and action read **different arrays**. So the exact defect is
one-of-one — which means nothing on its own, because the thing that made those
two arrays non-parallel is not Preserve.

**Wider scope — the icon split is the shared cause, and it has three other live
sites.** `_splitIcons` introduced a second representation of "the selection",
and the conversion was done site by site. It reached `refreshSelUI`,
`handleRoll`, `handleBank` and `_legalKeeps` for the *values*; it did not reach
`toggleDie` at all (PR12); the `pts<0` rule that goes with it reached one of
four predicates (PR1); and inside a single `G.kept` row the split is applied to
`vals` at all three producers and to `dice` at only one of three (PR2). Patching
Preserve's picker without touching those leaves three siblings live and leaves
`k.dice` still meaning two different things depending on which button committed
the row. **Preserve should not be patched alone**; the row's contract — is
`k.dice` the whole keep or the scoring remainder — should be decided once and
made true at 25125, 27121 and 27149 together, which is the same "one function,
one exit path" ruling §5a already made for `_removeDieAt`.

**Widest scope — the shape is not about icons at all.** Four survivors here
share nothing with the selection code: the chalkboard's count against its
per-circle history (PR7), the snapshot's hand-written field lists against the
record they copy — three writers, three different subsets, one of them with a
comment asserting they match (PR10) — the seal's four copies of one fact, three
persisted and one not (PR3), and a removal's return value against the pool
filter that runs regardless (PR8). Add the already-shipped P529/P530/P531/P532
and this is now a dozen instances in one codebase. It is a systemic property of
this file, not a Preserve problem.

**Confidence.** High — call it 85% — on the narrow claim, because it rests on
verbatim code I read in the pinned copy and on a complete enumeration of the
nine `CFX` gate/action pairs rather than on a search. Medium-high, 65-70%, on
the wider claim, for one reason and it is the standing one: **nothing here was
driven.** Twenty-six of forty nominations died on contact, most of them to
reachability, and this document's own record says half of every raw hit list
dissolves. I would expect one or two of the twelve to die the same way under a
probe — PR9 and PR12 are the likeliest, PR1 and PR2 the least likely, because
both are arithmetic on code paths this document has already measured executing.

---

## REFUTED

Twenty-six nominations died. One line each, with the reason. A hunt that reports
only what it found is unfalsifiable.

**Gate-versus-action lane (7):**

1. **G3 — the Anchor probe index is computed against the unsplit selection and read out of the split arrays.** All three blocks are behind `cards.includes('anchor')` with `cards=effectiveCards()`, whose first statement is `return [];` (24488). Dead layer; revive with G9 as one item if the P1 cutover is ever reversed.
2. **G4 — `_removeDieAt` has two ways to refuse and four callers never read the answer.** Structurally true (14361, 19441, 25541 discard the boolean) but each priced caller is protected by a gate that cannot disagree with the refusal: Sacrifice re-tests the floor at 14322 in the same synchronous block and guards on `_sacL>=0`; `_breakBegin` returns false at one lane so the Break tap handler is never attached. The only caller that can receive a refusal is the shatter sweep, judged as PR8.
3. **G5 — the shatter sweep loses a die the loadout keeps.** The single-die case does not cash out: on a refusal `_dropLanes(1)` is skipped too, so `numDice` stays equal to `matchDice.length`; the only disagreement is pool 0 against matchDice 1, and 24582 reconciles both before anything reads them; the in-turn consumer busts, which is what every "last free die left the table" case does; and the 19240 behaviour it measures against is the one P528 deliberately replaced to close D24. What survives is the two-die arm, carried forward as PR8 — and PR8 must reconcile with this kill before it is probed.
4. **G6 — Encore's gate counts uncommitted dice and its action counts uncommitted-and-unfrozen.** Enumerated all six writers of `d._frozen`: four set it false, and the two that set it true (24954, 31634) are reachable only through `activateCard`'s dead `pCards` layer; `frozen_die` is on `_npcActiveSkip` (32306). With no reachable `_frozen=true` the two predicates enumerate the identical set.
5. **G9 — `_bookendsEligible` is handed the unsplit selection at four sites and the split remainder at the fifth.** Census confirmed (14070, 24516, 25047, 26105 raw; 27049 post-split), and dead for the same single reason as G3. One item with G3, not two.
6. **G10 — Sacrifice's filter excludes the loaned seat by `d.lane` and its removal resolves by `matchDice.indexOf(d.mat)`.** The fallback needs a laneless pool die; every mint stamps a lane (25233, 25392, 26657), the one measured producer also sets `_shattered` which 14310 filters, and the NaN arm is closed twice (19236 and `_sacL>=0`). Default to dead.
7. **G11 — Pickpocket's safe-target filter and its post-palm re-check ask one question with two predicates.** The predicate arm is constant-equal today because the only difference is `_anchorRescues`, which returns false against `effectiveCards()`. The window arm is real and is already S10 in this document, at #6 in its own driving order; fold the `famUse`-ignores-`_palmAnimating` observation into S10's probe.

**Count-versus-collection lane (9):**

8. **K1 — the player's row is filled with a bare `appendChild`, so a bust-save permanently desyncs seat order from lane order.** Two kills: every route into `_runSave` is gated on `G.pCards`, which is the empty local declared at 32221 and passed to `newG` at 32231; and no consumer joins DOM order to lane — `_laneOf` reads `d.lane` off the pool entry, `_tradePaint` replaces in place, the tap router hit-tests by distance. (Kept from it, and it is *not* what was filed: `_removeDieAt`'s Fair-Trade branch removes a pool entry without `_dropLanes`, which is a live producer of DOM/lane divergence — see PR5.)
9. **K3 — the trade ledger's frozen `cnt` against a `matchDice` two live cards rewrite.** `cnt` is the third branch of a chain and each scenario is consumed by an earlier test: a duplicate elsewhere leaves `md[L]===t.theirs` true, so the primary branch fires; a death routes through `_removeDieAt`, which sets `seatGone` and forces `k=-1` before the count is consulted. The live-writer half is already D11.
10. **K4 — the rival's `left` is recomputed from dice dealt while seats come from `_oSeats()`.** The clamp with a stated per-roll scope (28361) is fed entirely from `G.pCards` and is dead; the live producer, the palm at 28345, behaves exactly as the player-side palm does (`_maybeFireCutpurse` splices the pool and drops a lane for the rest of the turn). Mirror, not drift.
11. **K5 — Snuff's `left--` is gated on `left>1` and its seat removal is not.** Both arms unreachable: `left` is never below 5 when 28283 is evaluated, and `_snuffLane` is a player lane bounded by `matchDice.length`, which is never longer than `matchOppDice` (six everywhere; the only two shrinking writers are on the dead layer).
12. **K6 — handleRoll's Gambler's Eye branch assigns `numDice` the size of a strict subset of the pool.** Verified verbatim at 24943-24957 and behind `G._gamblersEyeActive`, written in exactly one place inside `activateCard`'s dead layer; the NPC route is closed by `_npcActiveSkip`. Inheritance for whoever revives `params.pCards`.
13. **K7 — two consumers count dice from `k.vals.length` while the dice are in `k.dice`.** The divergent pair is real (and is PR2's), but both readers are dead: `_bankDiceUsed` has one call site behind `G._handicap==='bounty_board'` with `G._handicap` measured null, and `totalCommitted` has one consumer behind `G.pCards.includes('half_measure')`.
14. **K8 — `D3X.tick` watches a cached count of the row, so a same-size membership change never re-measures homes.** The named consequence is already patched: P520 ends the vagabond reorder with `d.hx=undefined` plus an explicit `_measureHomes()` (37115-37116), `_homeOf` re-measures any tracked die with no cached home (20152), and every throw calls `_measureHomes` unconditionally (21482).
15. **K9 — the refill computes lane occupancy twice with different validation.** True, and no producer can separate the two walks: every lane assignment in the file is numeric (25233, 25392, 26657, 19312, 37085), and `Math.min(needNew,_freeLanes.length)` absorbs the residue. Worth a comment tying 25340 to 25274; not a defect.
16. **K10 — the rival's active cards carry two independent use budgets from two card tables.** They never gate the same card: the twenty cards `npcHasActive` asks about cannot enter `G.oCards` (no boss pool holds them; the patron pool builder excludes every `type:'active'` card by construction; `S.npcWonCards` has no writer), and the two that *are* seeded (`quick_hands`, `sticky_fingers_die`) have no `npcHasActive` reader. One budget moves, the other is a dead write.

**Parallel-array lane (6):**

17. **PA3 — `_famDiceMigrate` filters `diceInv` and never `dieEnchInv`, and the pad repairs it from the wrong end.** Correct reading, no reachable producer — see the DEMOTED entry above, which merges K2 into this verdict.
18. **PA4 — three sites push to `S.run.diceInv` and only two run the pad.** Real asymmetry (and a fourth un-padded pusher at 13772 the nomination missed), but no misalignment is created: the new tail slot reads `undefined` where it would read `null`, and every reader treats both as falsy. The born-brand window has no consumer because `_enchInit` is self-healing in both directions and runs first at every surface, including `_wardOwned`.
19. **PA5 — `_diceOut[].lane` is snapshotted by three writers, shifted by none, read by nobody.** The last clause is the kill: a field nothing reads has nothing on the other side of the correspondence. The source already ruled on it at the write site (19298-19300): the number is a note of where the die was, which is why the panel names the die and never the seat.
20. **PA6 — Sequence is the only position card that reconciles `G.pCards` against `S.run.cards`.** Two unconditional kills: `effectiveCards()` returns `[]` at 24488 and `&&` short-circuits before the extra test is evaluated; and `G.pCards` is the empty local at 32221 regardless of what `launchSeat` computed.
21. **PA7 — `rungLanes`, the rival's second seat list, still built and snuff-shifted, read by nothing.** `rungLanes` is a `var` local inside `step()` inside `runOppTurn` — "nothing reads it" is a scoping fact, not a search result. One representation and one orphan; a deletion, not a finding.
22. **PA8 — the Stargazer peek is index-paired to a free array it was not built from, gated on length alone.** This is D7, including the equal-count arm the nomination offers as new — the plan doc already corrected itself on that point at lines 884-889 and measured the cross-turn arm at 876-881. One sliver belongs appended to D7, not filed separately: `_rollD` is per-material *and* per-brand (19705), so a peeked 4 or 6 can be stamped onto a crystal, whose faces are `[1,1,2,3,5,5]`.

**Serialise-versus-rehydrate lane (4):**

23. **SR-07 — the resume mapper assigns six sub-records by reference while the famState block below deep-clones four.** The aliasing is real; the leak is not. Zero `save()` calls between the mapper and `startPTurn`'s own `saveMatchState()` at 24893, which rebuilds `S.pendingMatch` as a fresh literal with `JSON.parse(JSON.stringify(...))` on all six and breaks every alias before any player input is possible.
24. **SR-09 — Stargazer's peek and Honeytrap's stamped value survive a turn boundary but are in no snapshot, while the charge is.** Requires the arm to be alive *at* the boundary, which is D7's measured survival. The ruled D7 fix — clear the arm at the boundary — produces exactly the outcome SR-09 reports as the defect. Double-counting.
25. **SR-10 — `_diceOut`'s restore is gated on `_enchArr`'s length test, using one array as a proxy for another's validity.** The proxy holds: `newG`'s first statement is `_enchInit()` (23247), which forces `dieEnch` to `dice.length` before `matchDice` is built from the same array, and all three snapshot writers move the pair together. Both arms offered to break it (mirror_match, an empty `_enchArr`) are closed.
26. **SR-11 — `_shiftBreak` tolerates "a single record from an older save" for a field no save path has ever written.** `_breakPending` appears at eight sites, none of them a snapshot writer, and it is reset to `[]` at 24591 before the boundary write at 24893. A stale comment with no behavioural claim behind it.

---

## NOT DRIVEN

**Nothing in this section was executed.** No browser, no dev server, no
`tools/shoot.js`, nothing driven. It is static reading against
`pinned_168c7d1.html`, a copy of `fark_proto.html` at commit **168c7d1**, and
every item above is a **nomination awaiting a probe**. Where an item coincides
with a measurement this document already carries (M5, D7, D11, D24, S10) the
measurement is this document's and is cited as such. Every verbatim block above
was re-read in the pinned copy rather than trusted from the nomination; three
nominations changed verdict in the process, and two of the twelve survivors
gained material that was not in the original filing (PR2's producer census,
PR6's two extra run-scoped writers).

### Priority order for driving

1. **PR1 — the four keep predicates.** Cheapest arrangement in the set: one
   brand, one junk die, no quit cycle, three reads. It settles a rule the file
   itself prices at +80.5 win-rate points, and it is the only survivor a player
   meets in ordinary play with no save/resume involved.
2. **PR2 — Preserve's `k.vals`/`k.dice`.** Same rig, same session, one more
   commit. It is already this document's largest open item and it is the one
   Denis's question is actually about; it should not be patched until PR1 and
   PR12 are measured beside it, because all three want one ruling on what the
   split means.
3. **PR3 — the sealed rule across a resume.** One quit/resume, four reads, and
   it decides whether the whole sealed-seat payout path can be trusted. Run PR7
   in the same session: PR3 suppresses PR7's producer, so measuring either one
   without the other risks a clean result that means nothing.
4. **PR4 — Preserve across the resume.** Same rig as PR3, one turn later, and
   the complementary arm (quit before the payout) is the control that makes the
   reading interpretable.
5. **PR6 — the run-scoped writes.** Same rig again; the read is one number at
   five points, with a no-quit control. Cheap enough to ride along with PR3/PR4.
6. **PR7 — the chalkboard.** No match instrumentation needed past a win; two
   fields off `S.run` and one DOM query.
7. **PR8 — the shatter sweep's two-die arm.** *Reconcile the contradiction
   first.* G5's kill of the single-die case is on the record above; if the
   two-die arm falls to the same reconcile argument this item dies with it, and
   that is a ten-minute read, not a probe.
8. **PR5 — the Fair-Trade exit's full snapshot.** Real and nasty, but the
   arrangement is expensive: a live loan, a borrowed Obsidian, a shatter, a
   quit. Worth building only after the cheap resume rig from 3-5 exists.
9. **PR10, PR9, PR11, PR12 last.** PR10 and PR9 are silent-state and need a
   control run each; PR11 and PR12 are cosmetic and are two-line reads once a
   probe harness is already up.

**Instrument hazards, carried forward.** Every survivor above states its own
instrument check, and they are not optional: PR2 must assert
`k.dice.length !== k.vals.length` before believing anything downstream, PR1 must
prove it can see a refusal, PR8 needs its three-die negative control, and PR6
needs the no-quit control before any double-pay is claimed. A clean result from
any of these without its check is a zero from an instrument that was never shown
to be looking at the right thing — which this document has now recorded
happening more than once.

### D25 — the player's Blessed Confiscation still pushes a seventh seat

Found by Denis reviewing `docs/CARD_ART_NEEDED.md`, chasing a stale card
description; the description was stale *because of* a fix whose twin was never
made.

`activateBlessedConfiscationPlayer` ends with:

```js
G.matchOppDice.splice(oBestIdx,1);
G.matchDice.push(stolen);
```

**That is exactly the shape P522 removed from the rival's side** — and P522's own
comment is the argument against it: a seventh seat is never dealt, because seats
are consumed as `_freeSeats[i]` for `i < rollDice` and nothing live makes
`rollDice` seven. The die is never rolled, but the array is one longer, which
feeds `numDice`, the loadout panel and the First Strike reveal.

**And it is worse here than it was there**, because of tonight's work: `push`
grows `G.matchDice` without growing `G._enchArr`, so every lane past the new one
is brand-misaligned — the parallel-array desync P564/P565/P569 spent the session
closing.

**Unreachable today**, and that is measured rather than assumed: it is reached
through `activateCard`, and the legacy player-active layer is dead — driven in
`tools/apv_frozen_reachable.js`, `canActivateCard` refuses every id tried
including ones from that layer meant to work, with `effectiveCards()` and
`pCards` both empty.

**Not fixed with P570, on purpose.** P570 was a wording change; this is a
behaviour decision. The fix is almost certainly P522's — swap over the player's
worst seat rather than push — since the same seat machinery constrains both
sides, but it should be chosen rather than assumed. **P570 corrected the
`playerDesc` to describe the swap, so the text now describes the intended
mechanic and this entry is the gap between text and code.**
