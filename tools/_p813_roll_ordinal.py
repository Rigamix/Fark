# -*- coding: utf-8 -*-
"""P813: the player's roll seam carries THIS roll's ordinal.

Card-audit catch (AMBER): a three-roll Slow Cook turn banked base only
- the accumulator never moved. Measured cause: the rival's roll seam
fires AFTER its counter advances and passes rollNum (the roll's own
ordinal); the player's fires BEFORE G.turnRollCount++ and passed
`rolls` - a field no handler reads - so slow_cook fell back to the
pre-increment counter and saw roll 3 as '2': accrual one roll late,
against the card's own text ('every roll past your second').

The seam now passes rollNum:(G.turnRollCount||0)+1 - the same
semantics as the rival's. The dead `rolls` field goes with it.
"""
import io, os, sys, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'fark_proto.html')
s = io.open(P, encoding='utf-8', newline='').read()
edits = []


def sub(old, new, label):
    global s
    if s.count(old) == 1:
        s = s.replace(old, new)
        edits.append(label)
        return
    pat = re.escape(old).replace('\\\n', '\n').replace('\n', '\\r?\n')
    hits = re.findall(pat, s)
    if len(hits) != 1:
        sys.exit('ANCHOR x%d for %s (nothing written)' % (len(hits), label))
    s = re.sub(pat, lambda m: new, s, count=1)
    edits.append(label)


sub("""  if(typeof famFire==='function'&&G&&G.phase!=='opp')famFire('roll',{actor:'p',rolls:G.turnRollCount||0});""",
    """  /* P813: THIS roll's ordinal - the rival seam's semantics (it fires
     after its counter advances; this one fires before it, and passed
     `rolls`, a field no handler reads, so slow_cook fell back to the
     pre-increment counter and accrued a roll late - measured: a
     three-roll turn banked base only). */
  if(typeof famFire==='function'&&G&&G.phase!=='opp')famFire('roll',{actor:'p',rollNum:(G.turnRollCount||0)+1});""",
    'the player roll seam carries the ordinal')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d (%s)' % (len(edits), ', '.join(edits)))
