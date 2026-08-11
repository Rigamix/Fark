# -*- coding: utf-8 -*-
"""P624: label the pre-existing stage-1 boss rows so the de-dup covers them too.

Found while checking P621: same-GROUP back-to-back is 0 across 600 draws, but
the counter also showed 3 "repeats" that turned out to be undefined===undefined -
the two ORIGINAL stage-1 rows in each boss pool carry no `g`, so they sit outside
the mechanism entirely. Two consequences, one cosmetic and one real:
  - an ungrouped pick does not update _dlgLastG, so it cannot exclude anything
  - measured, the identical LINE repeated back to back 7 times in 600 draws, and
    every one of those was an ungrouped row following itself
The new content cannot repeat that way. The 32 rows that predate it can.

GROUPED MECHANICALLY, AND THAT IS A DELIBERATE LIMIT. Each pool's originals get
one shared label rather than being hand-sorted into the new sentiment groups.
That guarantees they never follow each other and are excluded after either
fires, which is the whole defect. What it does NOT do is notice that a legacy
line might mean the same thing as one of the new groups - so a legacy
ledger-ish line can still follow a new ledger-callback one. Fixing that properly
means a human reading all 32 and deciding; this closes the mechanical hole and
leaves that judgement visible rather than pretending it was made.
"""
import io, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'fark_proto.html')
s = io.open(P, encoding='utf-8', newline='').read()

start = s.index('var PATRON_LINES=[')
end = s.index('\n];', start)
blk = s[start:end]

# a boss stage-1 row with no g:  {p:'boss:x:win',s:1,t:"..."}
pat = re.compile(r"\{p:'(boss:[a-z]+:(?:win|loss))',s:1,t:")
hits = pat.findall(blk)
if not hits:
    sys.exit('no ungrouped stage-1 boss rows found - already labelled?')


def repl(m):
    return "{p:'%s',s:1,g:'stage1-original',t:" % m.group(1)


newblk = pat.sub(repl, blk)
io.open(P, 'w', encoding='utf-8', newline='').write(s[:start] + newblk + s[end:])
print('P624: labelled %d pre-existing stage-1 boss rows across %d pools'
      % (len(hits), len(set(hits))))
