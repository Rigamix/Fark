# -*- coding: utf-8 -*-
"""P462 - the player's turn value, and the rivalTurn seam's mirror.

RULED: a bust is a turn worth ZERO, not no turn. Thread a real number, zero on
bust, one signal - not a flag that suppresses the seam.

WHAT THE MEASUREMENT FOUND (tools/endpturn_value.py), because the plan nearly
shipped on an assumption that was only accidentally true:

  TEN call sites, not six. My earlier count was wrong.
  Seven of them clear turnPts before reaching endPTurn; three leave it live.

AND THE SEVEN ARE THE RIGHT SEVEN. Five are _bustTolls - a bust, so zero is
correct. The other two are handleBank's steal_low_bank and block_low_bank early
returns, which set _bankAborted: the player banked NOTHING, so zero is correct
there too. The NORMAL bank does not appear in that list at all - it routes
showYieldButton -> handleYield -> endPTurn, and handleYield never touches
turnPts. So at the top of endPTurn the value already IS the ruled signal:

  normal bank      the banked total
  bust             0
  stolen/blocked   0

That had to be checked rather than assumed. Had handleBank's success path
cleared turnPts too, a capture here would read 0 on EVERY path and the card
would ship carrying a constant - rendering fine, erroring nowhere.

THE MIRROR. finOpp already fires rivalTurn with {actor:'p', pts:<what the rival
scored>} - the PLAYER's cards reacting to the RIVAL's turn resolving. The
inverse is exactly this moment: {actor:'o', pts:<what the PLAYER scored>}, so a
BOSS-held card sees its own rival's turn resolve. Trigger and payoff flip
together, which is the ruling.

THIS UNGATES NOTHING. CFX.ill_omen still tests _fxMine and still returns early
for an opponent owner; the boss's copy still runs through its own hand-written
sites at 25681/26953. This raises the MOMENT with a real value attached. Moving
those two bespoke sites onto the seam is the next step and is deliberately not
folded in here - that migration has to preserve two different payouts (bust
pays the boss, no-bust pays the player) and belongs in its own patch with its
own before/after.
"""
import io, os

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   'fark_proto.html')
with io.open(SRC, encoding='utf-8') as f:
    s = f.read()
orig = s

ANCH = u"  G.phase='opp';G.turnPts=0;G.kept=[];G.numDice=6;G.turnNum++;"
assert s.count(ANCH) == 1, 'endPTurn reset line matched %d' % s.count(ANCH)

NEW = u"""  /* THE PLAYER'S TURN VALUE, captured before the very next statement destroys
     it. A bust is a turn worth ZERO, not no turn - it happened and it produced
     a value. So this is a real number, never a flag that suppresses the seam,
     and "they scored nothing" stays readable as information.
     Measured (tools/endpturn_value.py): of ten endPTurn call sites, the seven
     that clear turnPts first are the five bust paths plus steal_low_bank and
     block_low_bank - all cases where the player banked nothing, so 0 is the
     right answer. The normal bank routes via handleYield, which never touches
     turnPts, so it arrives carrying its real total. */
  var _pTurnPts=(G.turnPts||0);
  G._pTurnPts=_pTurnPts;
""" + ANCH + u"""
  /* THE rivalTurn SEAM, MIRRORED. finOpp fires {actor:'p', pts:<rival scored>}
     so the PLAYER's cards see the rival's turn resolve. This is the inverse:
     {actor:'o', pts:<player scored>}, so a BOSS-held card sees ITS rival's
     turn resolve. Trigger and payoff flip together rather than half.
     Ungates nothing - CFX.ill_omen still tests _fxMine and returns early for
     an opponent owner. This raises the moment; which cards fire for a boss is
     the separate question. */
  try{famFire('rivalTurn',{actor:'o',pts:_pTurnPts});}catch(e){}"""

s = s.replace(ANCH, NEW)

assert s != orig, 'nothing changed'
assert s.count("G._pTurnPts=_pTurnPts;") == 1
assert s.count("famFire('rivalTurn',{actor:'o'") == 1
# the original player-side raise is untouched
assert s.count("famFire('rivalTurn',{actor:'p',pts:pts});") == 1
# and the reset line still exists exactly once, not duplicated by the splice
assert s.count(ANCH) == 1, 'reset line now appears %d times' % s.count(ANCH)

with io.open(SRC, 'w', encoding='utf-8', newline='') as f:
    f.write(s)
print('P462 applied: player turn value captured + rivalTurn mirrored (actor o)')
