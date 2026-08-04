# -*- coding: utf-8 -*-
"""P459 - the opponent's turn raises `turnStart` and `roll`.

RULED: ship the two easy seams now; the other five wait on a real scoping pass.
And the direction that shapes this patch: give bosses the SAME seven hooks the
player has, working generically, BEFORE any personality is attached - because
designing both at once means writing boss-specific behaviour into the seam
code, which is the bespoke-per-card trap this session has been removing
everywhere else.

So these two calls carry NO boss-specific anything. They raise the moment and
nothing more. Differentiation, when it comes, is data on each boss's existing
persona record (patronStats, dieBias, and whatever card-play dials get added) -
not a branch here.

THE TWO MOMENTS, measured (tools/oppturn_seams.py) rather than chosen:

  turnStart  runOppTurn body line 137 - `G.oppTurnCount=(G.oppTurnCount||0)+1;`
             The single place the opponent's turn number advances. One site.
  roll       body line 164 - `_oppHoldKept();oppRollNum++;`
             The single place its roll counter advances. One site.

Both POINT seams: one site each, no ambiguity about which moment they are. The
other five are SPREAD (7, 7 and 12 sites across 425, 229 and 885 lines) or
ABSENT, and picking a moment for those is the seatCommit decision at fifteen
times the distance. Not guessed at here.

WHY AFTER THE INCREMENT, BOTH TIMES. A hook asking "which turn is this" or
"which roll is this" must see the number it is about. Firing before the
increment would hand every opponent hook the previous turn's index - the same
off-by-one that made Snuff's window meaningless until Phase 3 gave it a gate.

WHAT THIS DOES NOT DO. It does not ungate a single card. Every CFX hook still
tests _fxMine and still returns early for an opponent. This raises the seams so
that ungating becomes possible and testable; deciding WHICH cards should fire
for a boss, and what they should mean when they do, is the parked work.
"""
import io, os

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   'fark_proto.html')
with io.open(SRC, encoding='utf-8') as f:
    s = f.read()
orig = s

TS = u"  G.oppTurnCount=(G.oppTurnCount||0)+1;"
assert s.count(TS) == 1, 'turnStart site matched %d' % s.count(TS)
s = s.replace(TS, TS + u"""
  /* THE OPPONENT'S turnStart SEAM. Raised AFTER the increment so a hook asking
     "which turn is this" sees the turn it is about - firing before would hand
     every opponent hook the previous index, which is the off-by-one that made
     Snuff's window meaningless until Phase 3 gated it.
     Deliberately carries nothing boss-specific: the seam is generic, and
     differentiation belongs in each boss's persona record, not here. */
  try{famFire('turnStart',{actor:'o'});}catch(e){}""")

RL = u"    _oppHoldKept();oppRollNum++;"
assert s.count(RL) == 1, 'roll site matched %d' % s.count(RL)
s = s.replace(RL, RL + u"""
    /* THE OPPONENT'S roll SEAM, after the counter advances, same reason. */
    try{famFire('roll',{actor:'o'});}catch(e){}""")

assert s != orig, 'nothing changed'
assert s.count("famFire('turnStart',{actor:'o'})") == 1
assert s.count("famFire('roll',{actor:'o'})") == 1
# and the player's seams are untouched
assert s.count("famFire('turnStart',{actor:'p'") == 1
assert s.count("famFire('roll',{actor:'p'") == 1
with io.open(SRC, 'w', encoding='utf-8', newline='') as f:
    f.write(s)
print('P459 applied: opponent turnStart + roll seams raised')
