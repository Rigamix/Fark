# -*- coding: utf-8 -*-
"""P831: fool's gold is player-only by DECLARATION, not by accident.

The anchor extraction flagged the shape; the reachability check made
it live: the rival's dead-roll path fires famFire('deadRoll',
{actor:'o'}) at ~35443, and a boss CAN hold fools_gold_f (jade family
deal). Today the corner survives only because famFoolsGold reads the
PLAYER's instance (famInst -> G.pF): a boss-held copy no-ops alone.
But when BOTH sides hold the card, the rival's dead roll passes the
mine-gate on THEIR copy, then the body bills the PLAYER's charge for
the rival's rescue and arms a burn on the PLAYER's instance that the
player's next bust pays - the cross-owner tangle.

Same lesson as P556b: safety by another function's accident, not this
one's decision. The hook gates on the owner outright, and the burn
dock re-asserts it locally.
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


sub("""  deadRoll:function(ev){if(!_fxMine(ev))return;
    if(famFoolsGold(ev.free))ev.claim();},""",
    """  deadRoll:function(ev){if(!_fxMine(ev))return;
    /* P831: PLAYER-ONLY by declaration. The rival's dead-roll path fires
       this seam too (actor:'o', ~35443), and famFoolsGold reads the
       PLAYER's instance - a rival-owned copy passing the mine-gate would
       bill the player's charge for the rival's rescue and arm a burn the
       player's next bust pays. The rival's rescue chain is
       NPC_BUST_SAVES; this card's rival half is undealt design. */
    if(ev.owner!=='p')return;
    if(famFoolsGold(ev.free))ev.claim();},""",
    'the hook declares player-only')

sub("""  bust:function(ev){if(!_fxMine(ev)||!ev.me.state.burn)return;
    var burn=ev.lost||0;""",
    """  bust:function(ev){if(!_fxMine(ev)||!ev.me.state.burn)return;
    if(ev.owner!=='p')return;/* P831: the dock writes G.pPts - the invariant lives HERE, not in the arm site's guard */
    var burn=ev.lost||0;""",
    'the dock re-asserts it')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d (%s)' % (len(edits), ', '.join(edits)))
