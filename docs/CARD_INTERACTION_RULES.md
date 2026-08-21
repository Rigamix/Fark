# CARD INTERACTION RULES

*What happens when a card is played after another card. Written P844,
revised P845/P845b (2026-08-21) after Denis's skeptical pass — which
was right on all four counts and found one shipped reachability bug
(seven_dice). Origin: the live break — Stargazer played, a second card
played, Stargazer's numbers stuck on screen. Measured before the fix:
stargazer → sacrifice left all six ghosts floating over five dice and
landed the promised faces lane-shifted onto the WRONG dice.*

Every rule here is enforced in code and every enforcement site has
been **individually driven** (the coverage table at the end says
exactly what was driven and how).

---

## The four kinds of card state

Every card effect that outlives its tap is one of these; its
interaction behaviour follows from which one it is:

1. **A PROMISE** — a claim about a future event, read from the table
   as it stood. *Stargazer* (`G._famPeekVals` + ghost floats),
   *Honeytrap* (`G._famHoneyVal` + honey marks). Consumed by the next
   real roll (`famApplyRollForces`); cleared by roll, turn end, turn
   start (`_clearRollForces` — the one exit, P556/P827). **Treatment
   on interference: VOID** (see R1).
2. **AN ARM** — a painted invitation waiting for a die tap; the
   mutation happens at the tap, not the play. *Steady Hand*
   (`G._steadyArmed`), *Transmute* (`G._transArmed` + the modal's
   stashed pick), *Seven Dice* (`G._sevenArmed` — reclassified here
   by P845b after driving proved it, see the coverage table). All wear
   `.break-target` rings and hijack die onclicks. **Treatment:
   DISARM** — flag and visuals atomically, via `_steadyDisarm` (which
   also clears `_sevenArmed` — same arm class, same exits) and
   `_transDisarm`.
3. **A LANE RECORD** — a claim on a *specific seat* that must survive
   the seats renumbering. `_fairTrade.lane`, `_tradeSwaps[].lane`,
   *Preserve*'s `_famPreserve.lane` / `_pvLane` / `_pvDie.lane`.
   **Treatment: MAINTAIN** — `_removeDieAt` repairs them on every
   removal (shift down above the hole, void at the hole) and the
   vagabond reorder carries them. This is preserve's honest home: it
   was filed as a flag in this doc's first version, but a card whose
   state needs lane-repair logic is not "nothing to invalidate" — it
   is a fourth shape, and the code already treated it as one.
4. **A FLAG** — points/wager/schedule state with no table claim.
   *Double or Nothing*, *Ill Omen*, *Sleight*, ledger/vow/hex-style
   actives. **Treatment: NOTHING.**

The asymmetry between kinds 1 and 3 is deliberate: a promise names
*faces*, which stop being true when the table changes; a lane record
names a *seat*, which is still meaningful after renumbering. Faces
void, seats follow.

## THE RULES

**R1 — A promise or an arm is about the table AS IT STOOD.** Any
effect that mutates the free pool outside the roll path — rewriting a
die's value, removing a die, un-committing the kept pile, freezing —
**voids** pending promises and disarms pending arms, values and
visuals together. The player is told (`THE STARS BLUR — THE TABLE
CHANGED`) when a promise actually died. Enforcer: `famTableChanged()`
(beside `_clearRollForces`). Voiding, not lane-repair, is the shipped
semantic for promises: the lane-shifted wrong-dice application was
measured. *(Denis can overrule per-card to follow-the-dice; void is
the safe default.)*

**R2 — Flag-only cards touch nothing.** A wager, an omen, a schedule
does not void a promise (driven: honeytrap survives Double or
Nothing). If a card doesn't change dice, it doesn't enroll.

**R3 — Cosmetic changes move visuals, never state.** A vagabond drag
reorder is the same dice in new seats: promises hold, lane records are
carried by the reorder's own maintenance, and the floats follow their
dice (`_famRefloatGhosts()`, lane-stamped ghosts).

**R4 — One exit path per lifecycle.** Promise values and their visuals
die in `_clearRollForces`, nowhere else. Arms die in their own
`_*Disarm` (flag + rings atomically; a stale hijacked onclick dies on
its flag guard). A second exit that clears the value but strands the
visual is exactly the stuck-numbers bug.

**R5 — Card plays don't serialize; effects defend themselves.** There
is deliberately no global lockout between card plays (`famUse` and
`activateCard` have none). The one exception: **Finnick's Palm**,
which sets `G._palmAnimating` for ~840ms — blocking ALL card
activations, die taps, roll and bank (`canActivateCard`, `toggleDie`,
`handleRoll`, bank all gate on it). Palm therefore has BOTH
mechanisms, in sequence: at dispatch the R1 hook voids any pending
promise (driven — see the coverage table), then its lock holds the
table closed while its own animation runs. The lock protects palm's
window; the hook protects everyone else's promises from palm. Every
other card gets no lock, and so must own two defenses:
- Any deferred callback (setTimeout resolve window) re-derives the
  table when it fires (the P535 pattern) **and** guards G identity
  (`var _g=G; … if(G!==_g)return;` — the `_ddG` pattern; encore got
  its guard in P844).
- `canUse` gates only phase and the card's own state — never another
  card's. Cross-card safety comes from R1's void, not from lockouts.

**R6 — Two-stage cards bill at the effect, not the arm.** An arm the
player walks away from costs nothing (steady_hand / transmute /
seven_dice return without billing; the tap pays). Corollary: the arm
must be voidable for free at any moment — which is why R1 can disarm
it.

## Enrollment — BY CONSTRUCTION (P846: the id roster deleted itself)

**`_setDieVal(d,v)`** — write + redraw + R1 void, at the mutation — is
the one way to rewrite a die's face outside the roll path. Every
player-side out-of-roll face write routes through it (17 sites: the
fam handlers, the CARDS handlers, Gambler's Eye's reroll branch, and
`famQuicksilver` — an ENCHANT, which no card list could ever have
covered). A card that writes through it is enrolled by construction; a
refund path that writes nothing voids nothing.

The P844/P845 dispatch-time id roster this replaces was the defect,
found by Denis's review: it enrolled six retired ids, missed the one
live card with the worst failure mode (Gambler's Eye — a whole-pool
reroll off the roll path, so a promise survived a reroll of every die
it covered), and voided on refunded no-ops (a flask with nothing to
reroll ate the player's promise).

Four mutations don't write a face; each keeps ONE explicit
`famTableChanged()` at its site:

| Non-val mutation | Site |
|---|---|
| A die leaves the table permanently | `_removeDieAt` tail (sacrifice, break, seizures, shatter) |
| Vanishing Act's turn-scoped splice | its handler (bypasses `_removeDieAt` by design — the die returns) |
| Frozen Die's freeze | its handler |
| Double Down's whole-table teardown | its handler |
| Alchemist's Chisel's mat swap ({mat,ench} is the die's identity) | its handler |

Stated exception: **Finnick's Palm** keeps its own write/redraw
choreography (the hardened 840ms reveal) with the void placed beside
its `target.val=` write.

Arms enroll at their TAP, where the mutation is: Steady Hand,
Transmute (`_transPick`), Seven Dice (P845b; the same driving found
the P834 redesign unreachable — `timing:'idle'` gates a card whose
pool is always empty at idle; fixed to `'choosing'`, P845).

**Still Waters rider (P846):** `rollFaceExclude` now carries the die
object to `_rollTable`, so `_famHushed` can see it — without it the
badge was bypassed at exactly its two live call sites (Gambler's Eye,
Grog's Flask). `rollFace` (the NPC + hot-dice roller) still rolls
die-less; measuring whether the badge should reach those paths is
queued in AUDIT_BACKLOG.

### Id collisions (the sticky_fingers lesson, checked per id)

Several ids on the list also exist in OTHER tables consumed by OTHER
systems. None cross-wire — different seat, different consumer — but
they are exactly where a future grep goes wrong, so they're recorded:

| id | Also lives in | Consumed by | Cross-wire risk |
|---|---|---|---|
| `old_bones`, `the_nudge`, `wild_die`, `brutus_fist`, `grogs_flask`, `ambrose_grace`, `coin_flip`, `finnicks_palm` | `NPC_RESCUES` (the P767 dead-roll rescue table, ~39435) | The RIVAL's turn flow, on the RIVAL's blank dice | None: player promises are cleared at `endPTurn` before the rival rolls |
| `twinning_charm` | NPC actives table (~39564, `moment:'roll'`) | `npcUseActive`, on `G.oppDice` | None: same-seat only |
| `finnicks_palm` | ALSO the relic-die table (~14189, `relic:'finnick'`, palm_adjacent scoring die) | The dice/scoring system | None today — but a **three-way** id collision; any future grep for this id must say which table it means |
| `seven_dice` | one id only — the CARDS row IS the P834 redesign in place (the old NPC arm deleted with it) | — | — |

**Checklist for a NEW card** (state in the patch header, per the
route-through-existing rule):
1. Which of the FOUR kinds is its state? Promise → clear in
   `_clearRollForces`. Arm → flag + disarm riding `_steadyDisarm` (or
   its own `_*Disarm` enrolled at the same moments). Lane record →
   maintenance in `_removeDieAt` AND the vagabond reorder. Flag →
   nothing.
2. Does it rewrite a die's face? → **write through `_setDieVal` — you
   already enrolled.** Direct `.val=` on a pool die outside the roll
   path is the bug. A non-val mutation (splice, freeze, un-commit, mat
   swap) → one `famTableChanged()` at the mutation site.
3. Does it defer work? → re-derive the table inside the callback
   (P535) and guard G identity (`_ddG`).
4. Does it float a visual over a die? → lane-stamp it
   (`g.dataset.lane`) so `_famRefloatGhosts` can move or prune it.
5. Does its id exist in another table (NPC_RESCUES, NPC actives,
   relic dice)? → add it to the collision table above.

## Coverage — what was actually driven vs. what is structural

Driven in `apv_card_interactions_sweep.js`, **25/25 legs, zero
tolerance** — the verdict asserts BOTH sides of the contract on every
leg (a mutated leg: hook fired AND ghosts 0 AND promise null; a
refunded leg: hook silent AND promise INTACT — the over-void is a
tested failure, not an accepted cost). Each CARDS id carries its
obtainability class so retired content can't pad the headline:

- **19 live legs**: the 6 fam moments, quicksilver (the enchant),
  seven_dice's tap, **gamblers_eye through its real flow** (activate →
  hold two dice → ROLL; the P846 headline hole), the flask REFUND leg
  (promise survives a no-op), and the 9 live/obtainable CARDS ids
  (grogs_flask, finnicks_palm, vanishing_act, frozen_die, double_down,
  coin_flip, the_nudge, alchemists_chisel, twinning_charm).
- **6 retired legs**, labeled: old_bones (dep, but NOT stripped from
  old saves — save-reachable), and brutus_fist / ambrose_grace /
  wild_die / alchemist_touch / double_down_die (dep + `_removedCards`
  — driven anyway: old content in an old save must still void
  honestly).

Also driven, in `apv_card_interactions.js`: the original break pair,
base stargazer un-regressed (promise lands on the right lanes),
honeytrap surviving a flag-only card, a stranded transmute arm
sweeping.

Structural (not driven, stated as such — P847 added the two
player-side pool rewrites Denis flagged as safe-but-unstated):
- **`famFoolsGold`** rewrites every free die with direct `.val=` — safe
  by an INVARIANT, not by one call site (Denis's correction to this
  entry's first version, which credited `handleRoll`'s disarm and
  cited the wrong line): **every path into a dead table has already
  disarmed and voided** — the main roll path via
  `famApplyRollForces`/`_clearRollForces`/`_steadyDisarm`, and every
  card path (powder keg, encore, steady's tap, seven dice's tap,
  quicksilver, gamblers_eye) via `famTableChanged` before its own bust
  check. Both fool's gold branches (rescue and burn) sit behind that
  invariant; the success branch's own `_steadyDisarm` is
  belt-and-braces. Whoever writes the next dead-roll consumer inherits
  the invariant, not a dependency on `handleRoll` running first.
- **The jade Break row** ("EVERYTHING ROLLS AGAIN") is direct-write ON
  PURPOSE and must NOT convert to `_setDieVal`: `_breakDie`'s tail
  resumes the interrupted roll ~320ms later, and a pending promise
  legitimately lands on THAT roll — converting the scatter would void
  the promise the resumed roll is about to consume. The scatter is
  cosmetic pre-roll noise (measured in the row's own comment).
- The NPC-side tables (NPC_RESCUES, NPC actives) are argued safe by
  ordering (promises die at endPTurn before the rival acts), not
  driven. The rival's OWN peek (`G._oPeekVals`) is index-keyed and
  engine-sequenced within their turn; no player interleaving exists.
- `_famRefloatGhosts` after a drag reorder is verified by code reading
  and lane-stamps, not by a driven drag (headless drag gestures are
  not in the harness).

Gambler's Eye's full story (P846→P848, driven at every step): its
ENTRY deselects the pool and rebinds onclicks → `famTableChanged()`
after the refund guard (arms disarm at activation — driven: steady
flag+rings die at entry). Its REROLL **is the main roll path** (P848):
the branch validates the split, freezes the holds, arms
`G._geExclude` (lane → old face, the "reroll must visibly differ"
rule as a flag on the roll, one exit in `_clearRollForces`), and falls
through — the deal rolls exactly the free unfrozen dice, so
`famFire('roll')`, the **deadRoll seam** (fool's gold rescues a GE
bust now — driven: charge spent, turn alive; before P848 the player
busted holding the charge), the tell hooks, `famApplyRollForces`,
`_afterRowSettle` and the real physics all come with it, now and for
whatever seam is added next. The branch had been a second roll
implementation needing seams grafted one at a time — the two-copies
bug in slow motion, ended by deleting the copy.

## Known remaining gaps (recorded, not fixed)

- **Resume mid-promise is invisible:** `_famPeekVals`/`_famHoneyVal`
  survive a save/reload (by design) but ghost floats are not
  re-minted — the force works, the player can't see it.
- **Honeytrap's pull is index-keyed** (`free[0]`) while its marks sit
  on the pair — after R1 it can't misfire across a removal, but the
  payer-vs-marks mismatch within an untouched table remains the
  card's documented quirk.
- **Preserve's amber-rider guard clear** nulls refs without unshelling
  the 3D die on a fled match — cosmetic, self-corrects at next match
  start.
