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

- **D16. Cultivate's growth dies with the turn.** `d._cult` (14223) is the only
  occurrence in the file and lives solely on the pool die object; `G.pool=[]` at
  startPTurn (24426) and `_turnTableClear` (23164) replace those objects. "For
  the rest of the match. Stacks." is at most one turn, and only pays on a second
  fire inside the same turn.
- **D17. Sleight is inert *and* single-use forever.** `CFX.sleight.use` sets
  `G._famSleight` (14387); the only other reference in the loaded corpus is its
  own `canUse` guard (14385, `!G._famSleight`) — measured over every global
  function's `.toString()` plus every inline `on*` attribute, 1,071,965 chars,
  zero hits outside CFX. Nothing clears the flag: measured after `startPTurn`,
  `famSleight true, sleightCanUseAgain false, sleightCharges 2`. A 2-charge card
  that does nothing, once. The rival's Sleight is a *different* flag,
  `G._oSleight`, and **is** implemented (25184-25188).
- **D18. Transmute and Sacrifice both admit `_frozen` dice; every other card
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
- **D20. A sleeved rule binds the rival and not the player.** `fark_proto.html:11505`
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
- **D22. Drill Order's cap is derived on the player's side and a literal on the
  rival's.** 23541 `var def=(G._tell&&G._tell.id==='drill_order')?G._tell:(_tellById('drill_order')||{}); var cap=def.maxRolls||3` versus 28011
  `if(_ruleActive('drill_order','o')&&oppRollNum>=3)`. Measured
  `_tellById('drill_order').maxRolls === 3`, so they agree **today**; retune the
  RUNGS record and the sealed/sleeved rule silently applies two different caps
  to the two sides. 13114 carries a third copy.
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

1. **The entire card-slot parallel — NOT REACHED.** The brief's fourth standing
   item ("do card slots suffer the same index/count-desync class of bug that
   dice lanes did?") was **not investigated by this sweep**. Every layer here
   was indexed by *die* lane. Card slots have their own ordering
   (`G.pF`, the familiar bar, RSX slots, `S.run.cards`, the equip/tier UIs) and
   at least three adjacent smells were noticed in passing without being chased:
   `CFX.tamper` mutates opponent card *instances*; `famUse(i)` indexes the
   familiar bar by position; and P511 already found a charge-accounting bug on
   save/resume, which is the card-side analogue of the dice-side resume bugs.
   **Assume nothing. This is the largest single gap and should be the next
   sweep.**
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

### S8. "no exceptions, no residue" and "the index does not have to be right for the repair to be" — the two halves of the restore are not gated together

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
