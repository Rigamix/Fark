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
- M2 THE NIGHT: DONE in dev copy (P3+P1+P2).
  - P3: pointsNeeded now [2,2,2,3,3,3,3,4]; TURN_CAP_PATRON=8 / TURN_CAP_BOSS=10;
    G.pTurns/G.oTurns (bank AND bust count); cap resolves in _handBackOrCap when
    the rival hands back (both sides equal turns -> trailing side always answers);
    tie -> extra full rounds until broken; HUD "TURN n/8" + OVERTIME.
  - P1: S.run.night {tier, roster, seatsPlayed, results, handicapSeat} built once
    per tier (_ensureNight, seats = pointsNeeded+2 +extraSeat perk); roster UI in
    #nightRoster (persona word, 6 dice chips, target, buy-in, WIN gold, handicap
    seat marked, WON/LOST stamps); old standard/handicap buttons hidden but kept
    for legacy canvas wiring; boss unlock leaves leftover seats playable;
    _checkNightFail in the settle path: all seats spent + points short -> -1 heart,
    points 0, roster reroll, LAST ORDERS splash on the tier screen (death at 0).
  - P2: NIGHT_BUYINS [10,15,25,35,50,65,80,100], clamped to purse (broke player
    pays what they have — no seat is ever locked); deduct + seat-consume ATOMIC at
    launch (pessimistic 'lost' result, so force-close/abandon can't refund or
    unspend); win pot = reward + buy-in back, folded into the coin count-up;
    pendingMatch snapshot carries seatIdx/pTurns/oTurns for resume.
  - Turn-boundary audit (vs cap): sudden_death runs its own 3-turn clock under
    target=inf (cap never binds); steeped/in_arrears/drill_order are per-roll or
    per-turn (neutral); leaky_cup every-4th-turn fires twice in 8 (fine);
    the_heir/turn-gated NPC actives all use early-turn gates (<=3) (fine);
    rising_stakes streaks neutral; The Tab escrow settles through the same
    endMatch path the cap uses. No blockers found.
  - Checklist verified live: fresh roster (4 seats T0), buy-in 100->90, seat
    consumed + LOST stamp on loss, win => +1 pt / WON stamp / +25 pot, night fail
    => heart 3->2 + LAST ORDERS + fresh roster + points reset, boss ready with 4
    seats still playable, cap unit tests (ahead/behind/tie/under-cap), legacy
    170-renown save => extraSeat granted + 5-seat roster + points kept, abandon
    mid-seat => no refund, seat stays spent, no heart.
- M3 next: retune targets/buy-ins/dice prices via sim acceptance (60-70% patron,
  45-55% boss, 5-7 median turns at intended gear).
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
