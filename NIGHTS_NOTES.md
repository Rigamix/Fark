# NIGHTS rework — working notes

Dev build: `fark_nights.html` (full playable copy of index.html).
Isolation: save key `gambit4_nights`, service worker disabled, title marked.
The live game (index.html / main branch) is untouched until sign-off.

Brief: FARK_LOOP_BRIEF.md (P1..P9). Status:
- M0 sim harness: DONE. `_runBalanceSim(cfg)` in fark_nights.html, or open
  fark_nights.html?sim=1 for the overlay table. Drives the real scoreRoll /
  oppShouldBank / generatePatron / dice faces. Cards limited to deterministic
  effects (amber/jade/crystal in-scoring + starstone bank adder) by design.
- M1 quick wins: DONE in dev copy.
  - P5: _oppDelay() funnels all 27 NPC-turn delays. SWIFT RIVALS setting (0.4x,
    boss first encounter exempt), tap-board-to-fast-forward (0.15x, rest of
    turn), one-line end-of-turn ledger via setStatusMsg.
  - P4: slots 1+2 base; 60-renown Trusted Hand = 4th slot; 160-renown replaced
    by extraSeat "House Favourite" (+1 seat, consumed by M2); migration grants
    extraSeat to old secondBoss holders. Nobody loses a slot.
  - P7: draft SKIP -> "DECLINE +Xg" (5 + tier*5), gold awarded in draftSkip.
- M2 next: P3 pointsNeeded [2,2,2,3,3,3,3,4] + turn caps (HUD pips) ->
  P1 night roster/seats -> P2 buy-ins -> LAST ORDERS fail -> migrations ->
  turn-structure card audit (sudden_death, Steeped, The Tab, delayed-bank
  saboteur, Leaky Cup, Dead Air, last-licks).
- M3: retune targets/buy-ins/dice prices via sim acceptance (60-70% patron,
  45-55% boss, 5-7 median turns at intended gear).

## Baseline sim (150 iters, bank300 policy, intended-gear diagonal)

UNCAPPED (current live rules):
tier gear      patW%  medTurns  bossW%  bossMedT
T0   G0-bone   47     5         43      7
T1   G1-early  45     6         43      8
T2   G1-early  35     8         31      11
T3   G2-mid    45     10        62      11
T4   G2-mid    45     12        52      17
T5   G2-mid    50     16        32      20
T6   G3-late   84     13        95      18
T7   G3-late   75     17        95      23

WITH 8-TURN CAP (brief P3), same cells:
T0 48/5 35/-, T1 43/6 35/-, T2 41/8 23/-, T3 43/8 57/-, T4 43/8 53/-,
T5 55/8 32/-, T6 85/8 92/-, T7 76/8 87/-   (all medians pin at 8)

Findings:
1. The cap alone fixes match LENGTH (medians 10-23 -> 8) with win rates within
   noise. P3 validated before building.
2. Win rates sit 35-55% at intended gear vs the 60-70% acceptance band ->
   target compression needed in M3 (especially T2 dip and T5 boss at 32%).
3. T6-7 gear (G3) overshoots (75-95%) — late-tier targets AND gear curve need
   the M3 pass; brief's "compress the top" holds.
4. Bone-dice T7 reality check: 5% win over 23-median-turn matches — the 4-hour
   run diagnosis, quantified.
