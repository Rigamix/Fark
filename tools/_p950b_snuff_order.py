# -*- coding: utf-8 -*-
u"""P950b: snuff decided its outcome before it decided what it took.

MEASURED, NOT REASONED. A snuff armed on lane 2 took seat 2 - the rival was
dealt [0,1,3,4,5] and the published list read [2] - and recorded outcome 'miss'.
Under P951 that plays the dispersing-cloud animation over a snuff that worked.

WHY. The block spends first and takes seats second:

    _lmSpend('_snuff');            <- the mark dies here, outcome computed
    _snuffWant.forEach(function(L){
      if(left>1){ ... _lmHit(L); } <- and only here is it known what it took

_lmEnd had already run, so `hit` was false when the outcome was decided, and
_lmHit's own `if(!m.live)` guard then refused the late stamp. Both halves of
that are correct in isolation; the ORDER is what is wrong.

Fog and snare already do it the other way round - both determine what they took,
stamp, and spend last - so this was snuff alone, and it is the same one-of-three
asymmetry P945 and P946 both turned out to be.

THE FIX IS THE ORDER, NOT THE GUARD. Relaxing _lmHit to stamp dead marks would
let a site report a hit against a mark that ended on a previous turn, and would
leave the outcome already computed anyway. Moving the spend below the loop keeps
P878's ruling exactly - it is still unconditional, still charged whether the
snuff lands or not, because the loop has no early exit - while letting the
outcome be decided after the site has finished deciding.

The post-assert is structural rather than textual: for each of the three types,
the _lmHit that reports its landing must appear BEFORE the _lmSpend that ends it.
That is the invariant this bug violated, and it is checkable by position.
"""
import io, os, sys, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'fark_proto.html')
s = io.open(P, encoding='utf-8', newline='').read()
edits = []


def sub(old, new, label):
    global s
    pat = re.escape(old).replace('\\\n', '\n').replace('\n', '\\r?\n')
    ms = list(re.finditer(pat, s))
    if len(ms) != 1:
        sys.exit('ANCHOR x%d for %s (nothing written)' % (len(ms), label))
    m = ms[0]
    rep = new.replace('\n', '\r\n') if '\r\n' in m.group(0) else new
    s = s[:m.start()] + rep + s[m.end():]
    edits.append(label)


sub(u"""    _lmSpend('_snuff');
    /* THE ONE-DIE FLOOR IS PER SEAT TAKEN, not per mark due. Two snuffs on a
       two-die hand take one seat, not two, and the published list must hold
       only the seats actually dropped - otherwise a reader skips a seat that
       is still being dealt. */
    _snuffWant.forEach(function(L){""",
    u"""    /* THE ONE-DIE FLOOR IS PER SEAT TAKEN, not per mark due. Two snuffs on a
       two-die hand take one seat, not two, and the published list must hold
       only the seats actually dropped - otherwise a reader skips a seat that
       is still being dealt. */
    _snuffWant.forEach(function(L){""",
    '1 lift the spend off the top of the block')

sub(u"""        try{famLog('SNUFF — THEY PLAY ONE SHORT');}catch(e){}
      }
    });
  }""",
    u"""        try{famLog('SNUFF — THEY PLAY ONE SHORT');}catch(e){}
      }
    });
    /* P950b: SPENT AFTER THE SEATS ARE TAKEN, not before. It ran above the
       loop, so _lmEnd computed the outcome while `hit` was still false and a
       snuff that took a seat recorded a MISS - measured: the rival dealt
       [0,1,3,4,5] with published [2], and the mark said miss. Fog and snare
       already determine, stamp, then spend; snuff alone inverted it.
       P878's ruling is untouched and this is still the unconditional charge it
       demands - the loop has no early exit, so the spend runs whether any seat
       was taken or not. A due mark that finds no room has MISSED, and a miss
       costs an attempt exactly as a hit does. */
    _lmSpend('_snuff');
  }""",
    '2 spend after the seats are taken')

# ── post-asserts ───────────────────────────────────────────────────
code = re.sub(r'/\*[\s\S]*?\*/', '', s)

# THE INVARIANT, checked by position rather than by reading: for every type,
# the site reports what it took BEFORE the mark is ended.
for kind, hit_pat in ((u"_lmSpend('_fog')", u'_lmHit(_fl)'),
                      (u"_lmSpend('_snuff')", u'_lmHit(L)'),
                      (u"_lmSpend('_snare')", u'_lmHit(m.lane)')):
    if code.count(kind) != 1:
        sys.exit('%s is not called exactly once (nothing written)' % kind)
    if code.count(hit_pat) != 1:
        sys.exit('%s is not present exactly once (nothing written)' % hit_pat)
    if code.index(hit_pat) > code.index(kind):
        sys.exit('%s reports its landing AFTER %s ends the mark - the outcome '
                 'would be decided before the site knows it (nothing written)'
                 % (hit_pat, kind))

# and the snuff spend still runs unconditionally: it must sit outside the
# forEach's `if(left>1)` guard, i.e. after the closing of the loop
_sn = code.index(u"_lmSpend('_snuff')")
_loopEnd = code.rindex(u'});', 0, _sn)
if u'if(left>1)' in code[_loopEnd:_sn]:
    sys.exit('the snuff spend is now inside the floor guard - a miss would '
             'cost nothing (nothing written)')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d edits (%s)' % (len(edits), ', '.join(edits)))
