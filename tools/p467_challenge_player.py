# -*- coding: utf-8 -*-
u"""P467 - challenge takes its stated penalty from the player too.

RULED: apply the same rule to both seats - pool plus bank, matching the rival.
The asymmetry had no signal behind it suggesting intent; it is the same
arithmetic mistake as the boss's, landing in the harmless direction by accident.

WHAT WAS WRONG. handleBank adds `total` to G.pPts AFTER the challenge branch
runs, so the player's Math.max(0, G.pPts - penalty) clamped against the POOL
ALONE and ignored the bank about to arrive:

    pool 1000 / bank 200  / penalty 500   lost 500
    pool 100  / bank 1000 / penalty 500   lost 100
    pool 0    / bank 1000 / penalty 500   lost 0     - the card does NOTHING

and it printed LOST 500 every time. It bites hardest early in a match, when a
low pool and a big bank are normal.

TWO SITES, AND ONLY ONE IS WRONG. `G.pPts=Math.max(0,G.pPts-...challengePenalty)`
appears twice: once here in handleBank and once on the BUST path (~25981). On a
bust the player banks nothing, so there is no bank to take from and pool-only is
the correct behaviour there. A global replace would have broken it. The bust
site is deliberately untouched.

THE MESSAGES NOW STATE WHAT IS ACTUALLY TAKEN, on both seats. The rival's
already announced `eff.penalty` while taking a capped `penalty` whenever it
could not afford the full amount - the same display-vouches-for-the-error shape,
smaller. If a number is printed next to a deduction it has to be the deduction.
"""
import io, os

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   'fark_proto.html')
with io.open(SRC, encoding='utf-8') as f:
    s = f.read()
orig = s

OLD = (u"if(total<G.npcCardState.challengeThreshold){\n"
       u"        G.pPts=Math.max(0,G.pPts-G.npcCardState.challengePenalty);\n"
       u"        bonusMsg+=' -'+G.npcCardState.challengePenalty+' '+npc.name;\n"
       u"        setStatusMsg(npc.name+' — LOST '+G.npcCardState.challengePenalty+'!','red');")
assert s.count(OLD) == 1, 'handleBank challenge block matched %d' % s.count(OLD)

NEW = (u"if(total<G.npcCardState.challengeThreshold){\n"
       u"        /* THE BANK PAYS FIRST, THEN THE POOL - the same rule the rival's side\n"
       u"           uses. `total` is added to G.pPts further down, so clamping against\n"
       u"           the pool alone ignored the bank about to arrive: pool 0 with a 1000\n"
       u"           bank lost NOTHING while printing LOST 500. The bust path keeps the\n"
       u"           pool-only form on purpose - a busted turn has no bank to take. */\n"
       u"        var _chPenP=Math.min(G.npcCardState.challengePenalty,(G.pPts||0)+total);\n"
       u"        var _chFromBankP=Math.min(total,_chPenP);\n"
       u"        total-=_chFromBankP;\n"
       u"        G.pPts=Math.max(0,(G.pPts||0)-(_chPenP-_chFromBankP));\n"
       u"        bonusMsg+=' -'+_chPenP+' '+npc.name;\n"
       u"        setStatusMsg(npc.name+' — LOST '+_chPenP+'!','red');")
s = s.replace(OLD, NEW)

# the rival's messages announced eff.penalty while taking a capped `penalty`
R1 = u"triggerCard(cid,npc.name+' −'+eff.penalty,true);"
assert s.count(R1) == 1, 'rival triggerCard matched %d' % s.count(R1)
s = s.replace(R1, u"triggerCard(cid,npc.name+' −'+penalty,true);")
R2 = u"setStatusMsg(npc.name+' — '+G.rung.name+' LOST '+eff.penalty+'!','gold');"
assert s.count(R2) == 1, 'rival setStatusMsg matched %d' % s.count(R2)
s = s.replace(R2, u"setStatusMsg(npc.name+' — '+G.rung.name+' LOST '+penalty+'!','gold');")

assert s != orig, 'nothing changed'
assert s.count('_chPenP') == 5, '_chPenP used %d times' % s.count('_chPenP')
assert s.count('_chFromBankP') == 3

import re
body = re.sub(r'/\*.*?\*/', '', s, flags=re.S)
# the BUST site keeps the pool-only form - exactly one left, and it is the bust one
assert body.count('G.pPts=Math.max(0,G.pPts-G.npcCardState.challengePenalty);') == 1, \
    'bust site count wrong: %d' % body.count('G.pPts=Math.max(0,G.pPts-G.npcCardState.challengePenalty);')
i = body.index('G.pPts=Math.max(0,G.pPts-G.npcCardState.challengePenalty);')
assert 'playerBustCount' in body[i:i + 400], 'the surviving pool-only site is not the bust path'
# no message announces a number it will not take
assert "LOST '+eff.penalty" not in body and "LOST '+G.npcCardState.challengePenalty" not in body
# P466's rival fix is undisturbed
assert body.count('_chFromBank=') == 1 and 'eff.penalty-penalty' not in body

with io.open(SRC, 'w', encoding='utf-8', newline='') as f:
    f.write(s)
print('P467 applied: player challenge takes pool+bank; both seats announce what they take')
