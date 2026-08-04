# -*- coding: utf-8 -*-
"""P464 - the wild trio becomes one keyed lookup. The table shape, proven small.

RULED: build the mechanic table, ordered by where it pays. scoreRoll first
because it is one function with no mirror - the safest place to establish the
shape before betting handleBank + finOpp's 19 branches on it.

WHAT IS ACTUALLY COLLAPSIBLE IN scoreRoll IS THREE OF ITS SIX, and saying so
matters more than the headline count. The six are:

  wild_triple / wild_quad / wild_straight   a 3-arm else-if chain, and the arms
                                            differ ONLY by a number - PURE DATA
  triple_bonus / single1_bonus /            three separate accumulators at three
  single5_bonus                             separate sites, each adding to a
                                            different variable. NOT a chain, and
                                            nothing merges them.

So this patch takes the three that are genuinely one decision and leaves the
three that only share a function. Collapsing the accumulators too would be
grouping by location rather than by behaviour - the same mistake as reading
"branches in one function" as "branches that belong together", which is what
made the owner-signature finding wrong.

THE ARMS ARE IDENTICAL EXCEPT FOR wildLevel: 1, 2, 3. That is a lookup wearing
an if-chain, and it is the clearest possible demonstration that a keyed table
changes nothing about behaviour - the values move, the logic does not.

WHY THE else-if POSITION IS PRESERVED EXACTLY. The chain's FIRST arm is
`context._noWild`, which deliberately does nothing so a natural face is left
alone. The wild lookup must stay AFTER it or a _noWild die would be wilded
anyway - the bug the surrounding comment records having already been fixed once.
"""
import io, os

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   'fark_proto.html')
with io.open(SRC, encoding='utf-8') as f:
    s = f.read()
orig = s

CHAIN = u"""    else if(eff.mechanic==='wild_triple'){eVals[i]=-1;wildLevel[i]=1;}
    else if(eff.mechanic==='wild_quad'){eVals[i]=-1;wildLevel[i]=2;}
    else if(eff.mechanic==='wild_straight'){eVals[i]=-1;wildLevel[i]=3;}"""
assert s.count(CHAIN) == 1, 'wild chain matched %d' % s.count(CHAIN)

s = s.replace(CHAIN, u"""    /* P464: three arms that differed only by a number, now one lookup.
       STILL AFTER the _noWild arm above - that arm deliberately does nothing so
       a natural face is left alone, and moving this ahead of it would wild a
       die that asked not to be. */
    else if(WILD_LEVEL[eff.mechanic]){eVals[i]=-1;wildLevel[i]=WILD_LEVEL[eff.mechanic];}""")

# the table itself, declared immediately above scoreRoll
ANCH = u"function scoreRoll("
assert s.count(ANCH) == 1, 'scoreRoll def matched %d' % s.count(ANCH)
s = s.replace(ANCH, u"""/* WILD_LEVEL - the first row of the mechanic table, and the smallest honest
   one. mechanic -> how many of a kind the wild can stand in for. Three
   if-arms that differed only by this number; nothing else about them varied,
   which is what makes it data rather than a refactor of behaviour.
   A mechanic absent from this table reads undefined, which is falsy, so the
   chain falls through exactly as an unmatched else-if did. */
var WILD_LEVEL={wild_triple:1,wild_quad:2,wild_straight:3};

""" + ANCH)

assert s != orig, 'nothing changed'
assert s.count('var WILD_LEVEL={wild_triple:1,wild_quad:2,wild_straight:3};') == 1
assert s.count('WILD_LEVEL[eff.mechanic]') == 2   # test + read
# the branches are gone from executable code, not merely from sight
import re
body = re.sub(r'/\*.*?\*/', '', s, flags=re.S)
for m in ['wild_triple', 'wild_quad', 'wild_straight']:
    assert ("mechanic==='%s'" % m) not in body, '%s branch still live' % m
    assert m in body, '%s vanished entirely' % m
# the _noWild arm still precedes the lookup
i_now = body.index('_noWild')
i_wild = body.index('WILD_LEVEL[eff.mechanic]')
assert i_now < i_wild, '_noWild arm no longer precedes the wild lookup'
# the other three scoreRoll mechanics are untouched
for m in ['triple_bonus', 'single1_bonus', 'single5_bonus']:
    assert ("mechanic==='%s'" % m) in body, '%s should NOT have moved' % m

with io.open(SRC, 'w', encoding='utf-8', newline='') as f:
    f.write(s)
print('P464 applied: wild trio -> WILD_LEVEL lookup (3 branches -> 1)')
