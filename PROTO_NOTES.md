# fark_proto.html — mechanics prototype ledger

Vehicle for the MASTER_PLAN phases. Save key `gambit4_proto`. index.html,
fark_nights.html, and _mockups untouched. New-system UI = bare black/white,
color accents only (family colours), system fonts.

## P0 — audit + scaffolding (done)

Brief §1 vs code:
- seats = pointsNeeded+2 ✓ (_nightSeats; extraSeat perk dies in P7)
- handicap: win=2 circles ✓ double gold ✓ loss rubs a circle ✓
- cap: highest tally ends ✓, dead-even → extra round ✓
- ADDED: trailing player final answer turn at cap (_handBackOrCap +
  endPTurn short-circuit, G._finalAnswerUsed). Sim harness cap loop does
  NOT model final answer yet — align in P8.

Old card system map (for P1 cutover):
- const CARDS at ~9348, 116 ids. Consumers: pCards ~204 refs, oCards ~122,
  activeCard ~88. Effect code is inline throughout scoring/turn/opp AI.
- Engine seams (line refs at P0): scoreRoll 10070, startPTurn 12456,
  endPTurn 14560, runOppTurn 14736, finOpp 15508, endMatch 16031,
  launchSeat 21711, generatePatron 9256, generateOppCards 19318.
- P1 strategy: build EV engine + FAM_CARDS beside old system; cut over
  offer/generation first, then delete old effect sites in one sweep;
  keep positional trio (vanguard/anchor/bookends) migrating into Vagabond.

## Decisions

- Proto keeps existing Room/match UI as scaffolding; new systems render
  as plain overlays/panels until the loop is proven.
