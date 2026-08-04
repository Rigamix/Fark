# -*- coding: utf-8 -*-
"""P463 - the boss's ill_omen onto the seam, reading "scored nothing".

RULED: the omen reads SCORED NOTHING, not BUSTED. Same wager the player-side
card already makes. THIS CHANGES THE BOSS'S BEHAVIOUR, deliberately and as the
point rather than as a side effect: today the boss does not pay out on a
blocked or stolen bank, and after this it does. The two sides of the card
disagreed before anything touched them, and "scored nothing" is what makes them
agree.

THE MIGRATION COLLAPSES TWO SITES INTO ONE, and it works because the bust path
ALREADY flows through endPTurn carrying zero:

  _bustTolls   paid the BOSS when the player busted        -> deleted
  endPTurn     paid the PLAYER when they did not bust      -> becomes both

So the surviving site branches on the same value the seam carries - exactly the
shape CFX.ill_omen uses for the player (`ev.pts <= 0`) - and the blocked/stolen
bank now reaches the "lands" arm because it arrives with pts 0. That is the
ruled change, arriving through the condition rather than bolted beside it.

TWO THINGS CARRIED ACROSS DELIBERATELY:

  The famDef NULL GUARD. The _bustTolls copy had one and the endPTurn copy did
  not - `famDef('ill_omen').p[...]` would throw if the id were ever retired.
  The surviving site is on the live path for BOTH outcomes now, so it takes the
  guarded version. Losing the guard while deleting its owner is how a migration
  quietly drops a fix.

  The CAP on what the boss can take: min(p[0], G.pPts). A boss cannot take more
  than the player has.
"""
import io, os

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   'fark_proto.html')
with io.open(SRC, encoding='utf-8') as f:
    s = f.read()
orig = s

# ── 1. the _bustTolls site goes away entirely ──
BUST = u"""    if(G._oIllOmen){/* they called your bust: pay them */
      /* famDef returns null for an id it does not carry. That could never
         bite while this sat in a branch nothing could reach; it is on the
         live bust path now, and a throw here would leave the turn with no
         route to endPTurn. */
      var _ioD=famDef('ill_omen');
      if(_ioD&&_ioD.p){
        var _ioP3=_ioD.p[(G._oIllOmen.tier||1)-1]||[0,0];
        var _ioTake=Math.min(_ioP3[0]||0,G.pPts||0);
        G.pPts=(G.pPts||0)-_ioTake;G.oPts=(G.oPts||0)+_ioTake;
        try{famLog('THEIR OMEN LANDS - THEY TAKE '+_ioTake);}catch(e){}
      }
      G._oIllOmen=null;try{updHUD();}catch(e){}
    }
"""
assert s.count(BUST) == 1, '_bustTolls omen block matched %d' % s.count(BUST)
s = s.replace(BUST, u"""    /* P463: the omen's payout left here. It reads SCORED NOTHING, not BUSTED,
       and a bust already flows through endPTurn carrying 0 - so both outcomes
       resolve at the single site there, off the same value the rivalTurn seam
       carries. Keeping a copy here would have re-created the disagreement the
       migration exists to remove. */
""")

# ── 2. the endPTurn site becomes both outcomes ──
END = u"""  if(G._oIllOmen){/* they called it and you did NOT bust: you gain */
    var _ioP2=famDef('ill_omen').p[(G._oIllOmen.tier||1)-1];
    G.pPts+=_ioP2[1];famLog('THEIR OMEN MISSES — YOU GAIN '+_ioP2[1]);
    G._oIllOmen=null;try{updHUD();}catch(e){}
  }"""
assert s.count(END) == 1, 'endPTurn omen block matched %d' % s.count(END)

NEW = u"""  if(G._oIllOmen){
    /* P463: BOTH outcomes, off _pTurnPts - the same value the rivalTurn seam
       carries and the same test CFX.ill_omen uses for the player (pts<=0).
       RULED "SCORED NOTHING", NOT "BUSTED": a bank blocked or stolen to zero
       is a turn that produced nothing, and the omen was always a bet on the
       outcome rather than on the dramatic version of it. This DOES change the
       boss's behaviour - it now pays out on those two cases - and that is the
       correction, not a side effect.
       The famDef null guard comes from the deleted _bustTolls copy: this site
       is on the live path for both outcomes now, and the guard must not be
       lost along with the branch that carried it. */
    var _ioD2=famDef('ill_omen');
    if(_ioD2&&_ioD2.p){
      var _ioP2=_ioD2.p[(G._oIllOmen.tier||1)-1]||[0,0];
      if((_pTurnPts||0)<=0){
        /* they called it and you scored nothing: they take, capped at what you have */
        var _ioTake2=Math.min(_ioP2[0]||0,G.pPts||0);
        G.pPts=(G.pPts||0)-_ioTake2;G.oPts=(G.oPts||0)+_ioTake2;
        try{famLog('THEIR OMEN LANDS — THEY TAKE '+_ioTake2);}catch(e){}
      }else{
        G.pPts=(G.pPts||0)+(_ioP2[1]||0);
        try{famLog('THEIR OMEN MISSES — YOU GAIN '+(_ioP2[1]||0));}catch(e){}
      }
    }
    G._oIllOmen=null;try{updHUD();}catch(e){}
  }"""
s = s.replace(END, NEW)

assert s != orig, 'nothing changed'
assert s.count('_oIllOmen') > 0, 'omen state gone entirely'
# exactly one payout site survives, and it handles both arms
assert s.count('THEIR OMEN LANDS') == 1, 'lands arm count %d' % s.count('THEIR OMEN LANDS')
assert s.count('THEIR OMEN MISSES') == 1, 'misses arm count %d' % s.count('THEIR OMEN MISSES')
# the guard survived the move
assert s.count('var _ioD2=famDef(\'ill_omen\');') == 1
# the player's own card is untouched
assert s.count('CFX.ill_omen={') == 1
assert s.count("famLog('THE OMEN LANDS") == 1
# the seam that enables this is still raised
assert s.count("famFire('rivalTurn',{actor:'o'") == 1
# comments must not be mistaken for the code they describe
import re
body = re.sub(r'/\*.*?\*/', '', s, flags=re.S)
assert body.count('THEIR OMEN LANDS') == 1
assert 'they called your bust' not in body, 'old bust branch still live'

with io.open(SRC, 'w', encoding='utf-8', newline='') as f:
    f.write(s)
print('P463 applied: boss ill_omen on one site, reading "scored nothing"')
