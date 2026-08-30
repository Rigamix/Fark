# -*- coding: utf-8 -*-
u"""P889b: record the first-paint discrepancy in the code, because the harness
can no longer see it.

MEASURED. The first _paintHalo after its scratch canvases are created or
resized differs from every later one by a constant 216 bytes - max 1 per
channel on about 160 pixels of an 860x1800 surface. Paints two through twelve
are mutually identical to the byte, and alternating target canvases after that
makes no difference at all. So it is a one-off on the first call, almost
certainly the freshly created mip canvases (430x900 down to 54x113) backing
differently from resized-and-cleared ones.

IT IS NOT WORTH FIXING - 1/255 on 0.04% of pixels is below anything a player
could see - but it IS worth writing down, for one reason: the probes now warm
the painter and discard that result, so the instrument that found it can no
longer see it. A discrepancy nothing can observe is one that gets rediscovered
from scratch.

AND THERE IS A CASE WHERE IT STOPS BEING COSMETIC. A form that paints ONCE and
briefly - a miss at 250ms, a handful of frames - may spend a meaningful share
of its life in that first call. For a selection glow that lives for seconds it
is nothing; for a one-shot state it is a larger fraction of what the player
actually sees. Whoever builds the short-lived forms should know the first frame
is not quite the same as the rest.
"""
import io, os, sys, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'fark_proto.html')
s = io.open(P, encoding='utf-8', newline='').read()

OLD = u"""    var S=this._haloS||(this._haloS=document.createElement('canvas'));
    if(S.width!==cv.width||S.height!==cv.height){S.width=cv.width;S.height=cv.height;}"""

NEW = u"""    /* P889b: THE FIRST CALL AFTER THESE SCRATCHES ARE CREATED OR RESIZED IS
       NOT QUITE THE SAME AS THE REST. Measured: it differs from every later
       paint by a constant 216 bytes, max 1 per channel on ~160 pixels of an
       860x1800 surface, and paints two through twelve are identical to the
       byte. Almost certainly the freshly created mip canvases below (430x900
       down to 54x113) backing differently from resized-and-cleared ones.
       Not worth fixing at 1/255 on 0.04% of pixels - recorded because the
       probes now warm the painter and discard that result, so the instrument
       that found it can no longer see it. It also stops being cosmetic for a
       form that paints ONCE and briefly: a 250ms one-shot spends a real share
       of its life in this call, where a selection glow living for seconds
       spends none. */
    var S=this._haloS||(this._haloS=document.createElement('canvas'));
    if(S.width!==cv.width||S.height!==cv.height){S.width=cv.width;S.height=cv.height;}"""

pat = re.escape(OLD).replace('\\\n', '\n').replace('\n', '\\r?\n')
ms = list(re.finditer(pat, s))
if len(ms) != 1:
    sys.exit('ANCHOR x%d (nothing written)' % len(ms))
m = ms[0]
rep = NEW.replace('\n', '\r\n') if '\r\n' in m.group(0) else NEW
s = s[:m.start()] + rep + s[m.end():]

if s.count('P889b: THE FIRST CALL') != 1:
    sys.exit('the note is not present exactly once (nothing written)')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: the first-paint discrepancy is recorded at _paintHalo')
