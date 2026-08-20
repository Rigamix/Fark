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
| steady_hand | player | PASS | arm→tap rerolled the 6 into the queued 5, charge billed AT THE TAP (arm is free), bank 150; leg B rerolled the only scorer into a dead table and the P535 re-derive BUSTED the turn paying nothing |
| retort | both | **FIXED (P814)** | bust half paid 400 on the nose both owners (boss bust cost the player exactly 400, once — no double-pay); the "hit by an opponent card" half was FULLY DEAD (driven hex hit paid 0, no seam existed). P814 wires famFire('cardHit') at the taking sites; hex hit now pays 400 (witnessed 900→500). Taxonomy note in OPEN.md |
| reprisal | player | PASS | trailing by 2000, a 100 bank stole exactly 25 (tier-1 quarter): pPts +125 / oPts −25; control with empty rival purse paid plain 100, rival untouched |
| powder_keg | player | PASS | committed 200 then detonated: kept emptied, all six rerolled from the stub, fresh triple banked EXACTLY 500 (no double-count); keg into a dead table busts (P535 re-derive); both charges spent |
| double_or_nothing | player | PASS | forced flips: lost nets +50 (half of a 100 bank), won nets +200; arm consumed. Spec-letter note: arms BEFORE the bank, spec describes a post-bank window (same information, see OPEN.md) |
| sacrifice | player | PASS | +800 landed the instant the die shattered, matchDice 6→5, next deal five, bank still clean, charge spent. DIVERGENCE: pays G.pPts (bust-proof); spec says current TURN total (at risk) — question in OPEN.md |
| short_fuse | player | PASS | keeps on rolls 1-2 plain, roll-3 keep doubled AND the bank-committed roll-4 keep doubled (bank total 400 exactly); lit bust burned exactly the lost turn (300) off the banked points |
| encore | player | PASS | kept 200 survived the encore, the four free dice rerolled from the stub, bank 800 exact; encore into a dead spread busts through its resolve window; both charges spent |
| ill_omen | player | PASS | landed: +800/−800 exact (handler witness, rival pts 0); missed: rival +400 with their bank riding on top; declaration consumed both ways |
| falling_star | player | PASS | tier-3 1000 bank → extra full turn with ZERO rival rolls (_oRollNum unchanged); flag consumed; control 100 bank → rival plays. NOTE: phase string briefly reads 'opp' during the skip — display-only |

## Open question (parked, not verdict-blocking)

Flake ledger: an ill_omen witness run once measured +400/−800 (irreproducible; the pPts write-trap run showed one write, +800 exact). Preserve: 3 of 11 headless runs ended the RETURN turn
paying zero (two signatures: dead die-tap + intact pPts; banked pPts
zeroed during the rival turn). Never reproduces under instrumentation
— numDice trap, exit wraps, and a pPts write-trap all ran green 8/8
(pPts written exactly twice, both handleBank, same G object). Suspect
SwiftShader/rAF stalls in headless; if a phone player ever reports a
vanished bank after a preserve turn, start here.

## Queue

AMBER, SILVER, OBSIDIAN, STARSTONE done. VAGABOND (pickpocket, tamper, vanguard_f,
for_keeps) → TAVERN (the_tab, hair_of_the_dog, marked_table,
high_table). Rival routes ride the parity-era probes
(tools/_probe_actor_pipe.js and the P765 sweeps) — rerun, not retired.

## Notes for the presentation pass (step 7)

- sleight: the rival's reroll happens pre-render — needs the visible
  land-pause-reroll beat (spec doc's own requirement).
- fog: effect lives inside the AI's choice — needs the lingering
  table visual Denis asked for + a clearer description.
