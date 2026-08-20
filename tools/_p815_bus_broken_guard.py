# -*- coding: utf-8 -*-
"""P815: a broken card does not fire - the bus gets the guard.

Card audit (VAGABOND): tamper breaks the rival's highest-tier card,
but famFire has no broken check, so a broken PASSIVE keeps paying.
Driven: rival's tampered retort t2 was 'broken for the night' and its
bust payment still took 700 from the player. Every NPC LEVER site
already filters !o.broken (34486-35562) and tamper zeroes charges (so
actives die twice over) - the bus was the one dispatcher without the
rule.
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


sub("""      var inst=list[i],fx=CFX[inst.id];
      if(!fx||!fx[hook])continue;""",
    """      var inst=list[i],fx=CFX[inst.id];
      if(!fx||!fx[hook])continue;
      /* P815: TAMPERED MEANS SILENT. Every NPC lever filters !o.broken
         and tamper zeroes charges, but a broken PASSIVE rode this loop
         untouched - driven: a tampered retort's bust payment still took
         700. The bus is where 'broken for the night' becomes true. */
      if(inst.broken)continue;""",
    'the bus skips broken cards')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d (%s)' % (len(edits), ', '.join(edits)))
