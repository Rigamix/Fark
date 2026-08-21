# -*- coding: utf-8 -*-
"""P847: the two Gambler's Eye edges from Denis's P846 verification.

1. THE ENTRY GUARD. activateGamblersEye deselected the whole pool and
   rebound every free die's onclick with no disarm - an armed Steady
   Hand stayed flag-true with .break-target painted and taps toggling
   selection (outlined and inert, the exact symptom _steadyDisarm was
   written for), for as long as the player sat in GE mode. One
   famTableChanged() after the refund guard: deselect-all + rebind is
   the R1 mutation class, and the reroll is committed the moment the
   mode engages (there is no way out without a valid split), so the
   promise dying here rather than seconds later is the clearer moment.
   Placed AFTER the refund guard - a refunded no-op still voids
   nothing.

2. THE ROLL SEAM. The GE branch does G.turnRollCount++ and returns
   before _afterRollImpl, so famFire('roll') never fired - slow_cook
   (whose whole P813 fix was this seam carrying rollNum) missed every
   GE reroll. The seam now fires with the same payload shape as the
   main path (rollNum = count+1, before the increment). The post-roll
   TELL hooks (Steeped, Loaded Die, Gambler's Thumb, Hot Streak) are
   NOT copied here - that block wants extraction into one function
   with two callers, not a second copy; recorded in AUDIT_BACKLOG.
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
    ms = list(re.finditer(pat, s))
    if len(ms) != 1:
        sys.exit('ANCHOR x%d for %s (nothing written)' % (len(ms), label))
    m = ms[0]
    rep = new.replace('\n', '\r\n') if '\r\n' in m.group(0) else new
    s = s[:m.start()] + rep + s[m.end():]
    edits.append(label)


sub("""    refundActiveCardUse('gamblers_eye');
    return;}
  /* Deselect all current selections */""",
    """    refundActiveCardUse('gamblers_eye');
    return;}
  /* P847: the mode's entry deselects the pool and rebinds every free
     die's onclick - the R1 mutation class. Without this, an armed
     Steady Hand sat flag-true with rings painted and taps toggling
     selection for the whole GE window. After the refund guard on
     purpose: a no-op voids nothing. */
  try{famTableChanged();}catch(e){}
  /* Deselect all current selections */""",
    'GE entry guard')

sub("""    SFX.roll();G.turnRollCount++;
    setTimeout(function(){
      var free2=G.pool.filter(function(d){return !d.committed;});""",
    """    /* P847: this IS a roll - the player tapped ROLL - and it never
       reached the seam every roll-counting system reads (slow_cook's
       P813 accrual missed every GE reroll). Same payload shape as the
       main path at _afterRollImpl. The post-roll TELL hooks are still
       main-path-only: that block wants ONE extraction with two
       callers, not a copy here - AUDIT_BACKLOG carries it. */
    try{famFire('roll',{actor:'p',rollNum:(G.turnRollCount||0)+1});}catch(e){}
    SFX.roll();G.turnRollCount++;
    setTimeout(function(){
      var free2=G.pool.filter(function(d){return !d.committed;});""",
    'GE roll seam')

for needed in ['P847: the mode', "famFire('roll',{actor:'p',rollNum:(G.turnRollCount||0)+1});}catch(e){}\n    SFX.roll()"]:
    if needed not in s.replace('\r\n', '\n'):
        sys.exit('KEEPER MISSING (nothing written)')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d edits (%s)' % (len(edits), ', '.join(edits)))
