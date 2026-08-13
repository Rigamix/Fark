# -*- coding: utf-8 -*-
"""P699: dice shadows a shade stronger, per Denis from his phone.

One number: the base band 0.45 -> 0.58 (the breathing term stays). Both the
blur path and the P694 concentric-fill path scale from this same alphaB, so
desktop and iPhone darken together.
"""
import io, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'fark_proto.html')
s = io.open(P, encoding='utf-8', newline='').read()

old = u"  var sMul=1+0.05*f,alphaB=0.45+0.09*f;"
new = u"  var sMul=1+0.05*f,alphaB=0.58+0.09*f;/* P699: stronger, per Denis on device */"
c = s.count(old)
if c != 1:
    sys.exit('ANCHOR x%d (need 1)' % c)
io.open(P, 'w', encoding='utf-8', newline='').write(s.replace(old, new))
print('  ok  P699 dice shadow strength')
