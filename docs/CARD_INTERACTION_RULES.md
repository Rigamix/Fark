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

## Enrollment map — verified ids, all DRIVEN

Fam layer (handlers named, ids are the CFX keys):

| Mutation moment | Site | Driven |
|---|---|---|
| A die leaves the table (sacrifice, break, seizures, obsidian shatter) | `_removeDieAt` tail | ✔ sacrifice through its card + `_removeDieAt` directly |
| Steady Hand's reroll | its die-tap handler | ✔ |
| Transmute's face write | `_transPick` | ✔ |
| Seven Dice's reroll (P845b: an ARM — enrolls at the TAP, not dispatch) | its die-tap handler | ✔ |
| Powder Keg (whole table re-rolls) | `CFX.powder_keg.use` | ✔ |
| Encore (free dice re-roll) | `CFX.encore.use` | ✔ |

CARDS layer — **15 ids**, one hook after `activateCard`'s dispatch
switch. Every id verified three ways: present in the dispatch switch,
its handler classified as dice-mutating by reading the body (writes
`d.val`, splices the pool, or freezes), and **individually driven
through `activateCard` with the gate satisfied** (probe
`apv_card_interactions_sweep.js`):

`grogs_flask, finnicks_palm, brutus_fist, ambrose_grace,
vanishing_act, old_bones, frozen_die, double_down, wild_die,
coin_flip, the_nudge, alchemists_chisel, alchemist_touch,
twinning_charm, double_down_die`

(`seven_dice` was on this list in P844 and is NOT now: driving it
through its real gate showed it arms at dispatch and mutates at its
tap — the dispatch hook was stripping its freshly painted rings while
the hijack lived, an invisible arm. It moved to the ARM kind with
tap-time enrollment. The same driving found the P834 redesign
unreachable: its gate was `timing:'idle'` and the pool is always empty
at idle — fixed to `'choosing'`, P845.)

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
2. Does it mutate free dice — and WHEN? At play → join the
   `activateCard` id list or call `famTableChanged()` in its handler.
   At a later tap (two-stage) → enroll at the tap, NOT the dispatch
   (the seven_dice lesson).
3. Does it defer work? → re-derive the table inside the callback
   (P535) and guard G identity (`_ddG`).
4. Does it float a visual over a die? → lane-stamp it
   (`g.dataset.lane`) so `_famRefloatGhosts` can move or prune it.
5. Does its id exist in another table (NPC_RESCUES, NPC actives,
   relic dice)? → add it to the collision table above.

## Coverage — what was actually driven vs. what is structural

Driven, one leg per mutator, in `apv_card_interactions_sweep.js`
(each leg: fresh match → real roll → stargazer promise armed → the
mutator fired through its REAL path → asserted: the hook call counted,
ghosts 0, promise null): **22/22 legs green** — the 6 fam-layer
moments and all 15 CARDS-layer ids plus seven_dice's tap. Cards whose
handlers refund for want of a target still fire the hook (it sits
after the dispatch); that over-void on a refunded activation is known
and accepted. Also driven, in `apv_card_interactions.js`: the original
break pair, base stargazer un-regressed (promise lands on the right
lanes), honeytrap surviving a flag-only card, a stranded transmute arm
sweeping.

Structural (not driven, stated as such):
- The NPC-side tables (NPC_RESCUES, NPC actives) are argued safe by
  ordering (promises die at endPTurn before the rival acts), not
  driven. The rival's OWN peek (`G._oPeekVals`) is index-keyed and
  engine-sequenced within their turn; no player interleaving exists.
- `_famRefloatGhosts` after a drag reorder is verified by code reading
  and lane-stamps, not by a driven drag (headless drag gestures are
  not in the harness).

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
