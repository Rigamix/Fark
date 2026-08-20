# Card audit 2 — the ACTIONS audit (2026-08-19)

Denis: "You need to check card actions are actually connected to the
game. Check all cards. Again." P776 audited the words; this audits the
wires. Standard: every verdict comes from an adversarial probe — a
construction that produces a DIFFERENT answer when the mechanism is
dead — driven through the real UI seams (taps, rolls, banks), never
from a code-read. Ground truth: docs/CARD_EFFECT_SPECS_FULL.md.
Probes live at tools/apv_audit_*.js and rerun against any build.

Legend: PASS = all assertions green, no fix needed. FIXED = probe
found it broken, patch shipped, probe green after. VISUAL-DEBT =
mechanically proven, effect invisible to the player (queued for the
step-7 presentation pass).

## Verdicts

| Card | Route | Verdict | Probe / construction |
|---|---|---|---|
| stargazer | player | **FIXED (P811)** | peek→KEEP→roll: index-array peek was discarded on every real path (free-count gate); lane-keyed now; all rolled dice land on their promises |
| sleight | player→rival | PASS + VISUAL-DEBT | 12-value RNG stub: their final dice equal the REROLL batch (draws 7-12) index-for-index, not the deal batch |
| double_stakes | run | **FIXED (P812)** | measured gold: buy 10→20, payout 30→60 armed (economy honest); the ROOM seat panel never read the flag — display fixed |
| fog (enchant) | player→rival | PASS + VISUAL-DEBT | fogged lane held the table's BEST scorer; chooser kept only the visible lesser die; mark spent |
| transmute | player | PASS | die 2→5 via the real prompt flow; transmuted die selectable and SCORED (50), charge spent |
| fools_gold_f | player | PASS | keep 100 → dead roll → auto-reroll (all 5 reroll draws consumed) → dead again → bank burned exactly 100 (1000→900), charge spent |
| bloom | player | PASS | jade triple paid 800 (500+300); CONTROL triple without the jade paid exactly 500 (not always-on, not dead) |
| cultivate | player | PASS | jade triple grew lane 0 by 50 AND the grown die's next triple paid 850 (growth actually pays) |
| preserve | player | PASS | full round trip: trapped kept 1 (100), trapping turn banked 100, return turn re-paid kept+turnPts, dealt LOADOUT−1 fresh (numDice write-trap: startPTurn 6 → _dropLanes 5), preserved die minted committed on the roll, immediate bank paid 200 (preserved+new). pPts write-trap: exactly two handleBank writes, same G |
| honeytrap | player | PASS | pair [5,5] kept → armed 5 → next real roll pulled a queued 2 into a 5 (famApplyRollForces), force consumed, charge spent. NOTE: arming while dice are mid-flight is consumed by the settling roll (the roll path ends in _clearRollForces "spent by this roll either way") — the effect fires on the landing roll, not lost, but the timing reads oddly |
| slow_cook | player | **FIXED (P813)** | measured: 3-roll turn banked 250 not 400 and acc 0 — the player roll seam fired pre-increment with dead field `rolls`; now carries rollNum (rival semantics). Re-measured 400/150, spill turn pays nothing |

## Open question (parked, not verdict-blocking)

Preserve probe flake: 3 of 11 headless runs ended the RETURN turn
paying zero (two signatures: dead die-tap + intact pPts; banked pPts
zeroed during the rival turn). Never reproduces under instrumentation
— numDice trap, exit wraps, and a pPts write-trap all ran green 8/8
(pPts written exactly twice, both handleBank, same G object). Suspect
SwiftShader/rAF stalls in headless; if a phone player ever reports a
vanished bank after a preserve turn, start here.

## Queue

AMBER done. SILVER
(steady_hand, retort, reprisal) → OBSIDIAN (powder_keg,
double_or_nothing, sacrifice, short_fuse) → STARSTONE (encore,
ill_omen, falling_star) → VAGABOND (pickpocket, tamper, vanguard_f,
for_keeps) → TAVERN (the_tab, hair_of_the_dog, marked_table,
high_table). Rival routes ride the parity-era probes
(tools/_probe_actor_pipe.js and the P765 sweeps) — rerun, not retired.

## Notes for the presentation pass (step 7)

- sleight: the rival's reroll happens pre-render — needs the visible
  land-pause-reroll beat (spec doc's own requirement).
- fog: effect lives inside the AI's choice — needs the lingering
  table visual Denis asked for + a clearer description.
