# CARD INTERACTION RULES

*What happens when a card is played after another card. Written P844
(2026-08-21) after the live break: Stargazer played, a second card
played, Stargazer's numbers stuck on screen. Measured before the fix:
stargazer → sacrifice left all six ghosts floating over five dice and
landed the promised faces lane-shifted onto the WRONG dice.*

Every rule here is enforced in code, not aspirational. The enforcement
sites are named so the next card knows where to enroll.

---

## The three kinds of card state

Every card effect that outlives its tap is one of these, and its
interaction behaviour follows from which one it is:

1. **A PROMISE** — a claim about a future event, read from the table
   as it stood. *Stargazer* (`G._famPeekVals` + ghost floats),
   *Honeytrap* (`G._famHoneyVal` + honey marks). Consumed by the next
   real roll (`famApplyRollForces`), cleared by roll, turn end, and
   turn start (`_clearRollForces` — the one exit, P556/P827).
2. **AN ARM** — a painted invitation waiting for a die tap.
   *Steady Hand* (`G._steadyArmed`), *Transmute* (`G._transArmed`),
   both wearing `.break-target` rings and hijacking die onclicks.
   Disarmed by their own tap, by any roll, and (P844) by any table
   change — flag and visuals together (`_steadyDisarm` /
   `_transDisarm`).
3. **A FLAG** — points/wager/schedule state with no table claim.
   *Double or Nothing*, *Ill Omen*, *Sleight*, *Preserve* (its
   restore is a turn-boundary system with its own lane maintenance),
   ledger/vow/hex-style actives. No visuals on the dice, nothing to
   invalidate.

## THE RULES

**R1 — A promise or an arm is about the table AS IT STOOD.** Any
effect that mutates the free pool outside the roll path — rewriting a
die's value, removing a die, un-committing the kept pile, freezing —
**voids** pending promises and arms, values and visuals together. The
player is told (`THE STARS BLUR — THE TABLE CHANGED` in the fam log)
when a promise actually died. Enforcer: `famTableChanged()`
(fark_proto.html, beside `_clearRollForces`). Voiding, not
lane-repair, is the shipped semantic: a promise that survives a
removal lands on the wrong dice (measured), and a "wrong promise kept
alive" is worse than a clean void. *(Denis can overrule per-card to
follow-the-dice; the void is the safe default.)*

**R2 — Flag-only cards touch nothing.** A wager, an omen, a schedule
does not void a promise (probe leg D: honeytrap survives Double or
Nothing). If a card doesn't change dice, it doesn't enroll.

**R3 — Cosmetic changes move visuals, never state.** A vagabond drag
reorder is the same dice in new seats: the promise holds, the floats
follow their dice (`_famRefloatGhosts()`, lane-stamped ghosts). Same
rule for anything that repositions without mutating.

**R4 — One exit path per lifecycle.** Promise values and their visuals
die in `_clearRollForces`, nowhere else. Arms die in their own
`_*Disarm` (flag + rings + onclick restore atomically). A second exit
that clears the value but strands the visual is exactly the stuck-
numbers bug.

**R5 — Card plays don't serialize; effects defend themselves.** There
is deliberately no global lockout between card plays (`famUse` and
`activateCard` have none; only Finnick's Palm briefly locks via
`G._palmAnimating`). Two consequences every card must own:
- Any deferred callback (setTimeout resolve window) must re-derive
  the table when it fires (the P535 pattern) **and** guard G identity
  (`var _g=G; … if(G!==_g)return;` — the `_ddG` pattern; encore got
  its guard in P844).
- `canUse` gates only phase and the card's own state — never another
  card's. Cross-card safety comes from R1's void, not from lockouts.

**R6 — Two-stage cards bill at the effect, not the arm.** An arm the
player walks away from costs nothing (steady_hand/transmute return
`false` from `use()`; the tap pays). Corollary: the arm must be
voidable for free at any moment — which is why R1 can void it.

## Enrollment map (where R1 is enforced)

| Mutation moment | Site |
|---|---|
| A die leaves the table (sacrifice, break, seizures, obsidian shatter) | `_removeDieAt` tail |
| Steady Hand's reroll | its die-tap handler |
| Transmute's face write | `_transPick` |
| Powder Keg (whole table re-rolls) | `CFX.powder_keg.use` |
| Encore (free dice re-roll) | `CFX.encore.use` |
| The 16 dice-mutating actives (flask, palm, fist, grace, vanishing act, old bones, frozen die, double down, wild die, seven dice, coin flip, nudge, chisel, touch, twinning, double-down die) | one hook after `activateCard`'s dispatch, keyed on the classified id list |

**Checklist for a NEW card** (add to the patch header per the
route-through-existing rule):
1. Which of the three kinds is its state? Promise → clear in
   `_clearRollForces`. Arm → own `_*Disarm` owning flag+visuals.
   Flag → nothing.
2. Does it mutate free dice? → join the enrollment map (the
   `activateCard` id list, or a `famTableChanged()` call in its
   handler).
3. Does it defer work? → re-derive the table inside the callback
   (P535) and guard G identity (`_ddG`).
4. Does it float a visual over a die? → lane-stamp it
   (`g.dataset.lane`) so `_famRefloatGhosts` can move or prune it.

## Known remaining gaps (recorded, not fixed)

- **Resume mid-promise is invisible:** `_famPeekVals`/`_famHoneyVal`
  survive a save/reload (by design) but the ghost floats are not
  re-minted — the force works, the player can't see it. Lesser bug
  than a stuck visual; needs a re-mint at match re-entry once dice
  DOM exists.
- **Honeytrap's pull is index-keyed** (`free[0]`) while its marks sit
  on the pair — after R1 this can no longer misfire across a removal
  (the promise voids), but the payer-vs-marks mismatch within an
  untouched table remains the card's documented quirk.
- **Preserve's amber-rider guard clear** (`_fkAmberChip` isConnected
  path) nulls refs without unshelling the 3D die on a fled match —
  cosmetic, self-corrects at next match start.
