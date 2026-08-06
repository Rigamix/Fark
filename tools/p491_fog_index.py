# -*- coding: utf-8 -*-
u"""P491 - under FOG the rival keeps the WRONG DICE. Live, and it blocks §10.

FOUND while sizing the keep wiring. FOG hides one seat from the rival's own
reckoning by SPLICING it out of the array that gets scored:

    var _fogV=fV.slice(); ... _fogV.splice(_fi,1);
    var{total,used,...}=_scoreRollBest(_fogV,...);

so `used` is indexed against the SHORTENED array. But every downstream reader
indexes it with a position from the FULL free list:

    L27815  snare:     used[_snIdx]   (_snIdx scanned over _oFree)
    keep loop:         used[i]        (i over G.oppDice.filter(!kept))

Every index at or above the fogged seat is off by one.

MEASURED with the real scorer, free=[1,2,5,1,3,5], fog hiding index 2:
    game would keep  [1,5,3]
    correct keep     [1,1,5]
So it keeps a 3 - a die that scored nothing - and drops a scoring 1.

THE SIM ALREADY HAD THIS RIGHT: sim_harness carries
`/* index shift: used is indexed against the fogged array */` and compensates.
Someone found it there and never carried it into the game - the same two-copies
problem as P479 and P489, in the third direction: this time the SIM was correct
and the game was not.

THE FIX IS RE-EXPANSION, NOT PER-SITE COMPENSATION. Adjusting each read site
would be wrong within a few lines: `used` is REASSIGNED five times downstream
(encore, reprisal, quick_hands, gilded_bones, slippery_table) from arrays built
off the FULL free list, so those are already full-length and shifting them would
introduce the very bug being fixed. Instead, put the fogged seat back into
`used` as `false` immediately after scoring. `used` is then full-length for its
whole life and every existing index - present and future - is correct with no
further thought.

`false` is the right value, not a placeholder: the rival cannot see that seat,
so it never keeps it. The sim says the same thing in words -
`/* unseen seat is never kept */`.
"""
import io, os, re

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   'fark_proto.html')
with io.open(SRC, encoding='utf-8') as f:
    s = f.read()
orig = s

# ── 1. remember where the splice happened ──
OLD_HEAD = u"""      var _fogV=fV.slice(),_fogM=fMats.slice();
      if(_lmDue('_fog')){"""
assert s.count(OLD_HEAD) == 1, 'fog head matched %d' % s.count(OLD_HEAD)
s = s.replace(OLD_HEAD, u"""      var _fogV=fV.slice(),_fogM=fMats.slice();
      /* P491: which seat got spliced out, so `used` can be put back to full
         length below. -1 means no fog this roll. */
      var _fogCut=-1;
      if(_lmDue('_fog')){""")

OLD_SPLICE = u"""          _fogV.splice(_fi,1);_fogM.splice(_fi,1);
          try{famLog('FOG — THEY MISREAD A SEAT');}catch(e){}"""
assert s.count(OLD_SPLICE) == 1, 'fog splice matched %d' % s.count(OLD_SPLICE)
s = s.replace(OLD_SPLICE, u"""          _fogV.splice(_fi,1);_fogM.splice(_fi,1);_fogCut=_fi;
          try{famLog('FOG — THEY MISREAD A SEAT');}catch(e){}""")

# ── 2. re-expand `used` the moment it exists ──
OLD_SCORE = (u"      var{total,used,context:newCtx}=_scoreRollBest(_fogV,G.oCards,oppBank,crowsCtx,_fogM);"
             u"crowsCtx=newCtx||crowsCtx;")
assert s.count(OLD_SCORE) == 1, 'scoring line matched %d' % s.count(OLD_SCORE)
s = s.replace(OLD_SCORE, OLD_SCORE + u"""
      /* P491 - PUT THE HIDDEN SEAT BACK. `used` came from the spliced array,
         so it was one short, while the snare check and the keep loop both
         index it with positions from the FULL free list - every index at or
         above the fogged seat was off by one and the rival kept the wrong
         dice. Measured: free [1,2,5,1,3,5] with seat 2 fogged kept [1,5,3]
         instead of [1,1,5], holding a die that scored nothing.
         Re-expanding here rather than compensating at each read site, because
         `used` is REASSIGNED five times below from full-length arrays and
         shifting those would recreate the bug. false is correct, not a
         filler: the rival cannot see that seat, so it never keeps it. */
      if(_fogCut>=0&&used&&used.length<fV.length)used.splice(_fogCut,0,false);""")

# ── gates, BEFORE the write ──
assert s != orig, 'nothing changed'
body = re.sub(r'/\*.*?\*/', '', s, flags=re.S)
assert body.count('_fogCut') == 4, '_fogCut count %d' % body.count('_fogCut')
assert body.count('used.splice(_fogCut,0,false)') == 1
# the five downstream reassignments must be untouched - they are already full length
for tok in ['used=_encRs.used', 'used=_resR.used', 'used=_qhR.used',
            'used=_gbR.used', 'used=_stR.used']:
    assert body.count(tok) == 1, '%s disturbed' % tok
# and P489 must survive intact
assert body.count('_scoreRollBest(') == 8
assert body.count('function _scoreRollBest(') == 1
assert body.count('function _legalKeeps(') == 1

with io.open(SRC, 'w', encoding='utf-8', newline='') as f:
    f.write(s)
print('P491 applied: used is re-expanded after fog, so every index is right')
