# -*- coding: utf-8 -*-
"""P426 - STICKY FINGERS moves back to Vagabond.

Denis's ruling on the Phase 4 decision. The P425 draft rewrote it onto amber's
break-trigger, which was wrong on the name: "sticky fingers" is a thief, not
something that holds. Tar Pit (the brief's condition) was Vagabond-flavoured,
and Vagabond's break row TAKES WHAT THEY HELD - a hand reaching into the
opponent's bank. Same family the condition always belonged to, and the name
now describes the mechanic.

The amber counter goes with it: it existed only for this feat.
"""
import io, os

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   'fark_proto.html')
with io.open(SRC, encoding='utf-8') as f:
    s = f.read()
orig = s

def sub_once(hay, old, new, what):
    n = hay.count(old)
    assert n == 1, 'anchor %s matched %d times (want 1)' % (what, n)
    return hay.replace(old, new)

# 1. The new hook - the branch where the steal actually took something. A steal
#    of zero (they busted their turn away) is not a steal.
s = sub_once(s,
  u"    var steal=Math.max(0,G._oLastBank||0);\n"
  u"    if(steal>0){\n"
  u"      G.turnPts=(G.turnPts||0)+steal;\n",
  u"    var steal=Math.max(0,G._oLastBank||0);\n"
  u"    if(steal>0){\n"
  u"      G._featSticky=(G._featSticky||0)+1;/* STICKY FINGERS - only a steal\n"
  u"        that TOOK something counts; a rival who busted their turn away\n"
  u"        leaves nothing to lift, and the row still fires. */\n"
  u"      G.turnPts=(G.turnPts||0)+steal;\n",
  'vagabond steal branch')

# 2. The amber counter existed only for the draft this replaces.
s = sub_once(s,
  u"    G._featAmberAte=(G._featAmberAte||0)+1;/* STICKY FINGERS */\n",
  u"",
  'amber counter removal')

# 3. The feat itself.
s = sub_once(s,
  u"  {id:'sticky_fingers',  label:'Sticky Fingers',   desc:'Win a match in which the amber held and ate a bust', renown:10,\n"
  u"    /* THE BRIEF SAYS TAR PIT, WHICH IS RETIRED. Rewritten onto amber's live\n"
  u"       identity — the tar that holds — rather than deleted. Exact wording is\n"
  u"       Denis's, flagged in the phase report. */\n"
  u"    check:function(G){return (G._featAmberAte||0)>=1;}},\n",
  u"  {id:'sticky_fingers',  label:'Sticky Fingers',   desc:'Win a match after lifting a rival bank', renown:10,\n"
  u"    /* THE BRIEF SAYS TAR PIT, WHICH IS RETIRED, and the first rewrite put\n"
  u"       this on amber — wrong on the name. Sticky fingers are a THIEF, not\n"
  u"       something that holds, and Tar Pit was Vagabond-flavoured to begin\n"
  u"       with. Vagabond's break row takes what the rival banked, which is a\n"
  u"       hand in someone else's purse: the family the feat always belonged to\n"
  u"       and a mechanic the name actually describes. */\n"
  u"    check:function(G){return (G._featSticky||0)>=1;}},\n",
  'sticky fingers feat')

assert s != orig, 'nothing changed'
assert '_featAmberAte' not in s, '_featAmberAte survives'
with io.open(SRC, 'w', encoding='utf-8', newline='') as f:
    f.write(s)
print('P426 applied. _featSticky hooks: %d' % s.count('_featSticky'))
