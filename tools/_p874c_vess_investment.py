# -*- coding: utf-8 -*-
u"""P874c: the one struck-word survivor.

The voice brief's section 5 says to grep its struck list against the final
tables, and "any survivor is a line that is still wearing the wrong century".
Driven over every row in the file, there is exactly one: Vess - a HIGH voice -
using a word that belongs in a 19th-century counting house rather than a
tavern.

It is NOT one of the new rows. It is an older win/loss line the voice pass did
not reach, which is exactly why the check greps the whole table rather than
the diff: a pass that only inspects what it changed cannot find what it
missed.
"""
import io, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'fark_proto.html')
s = io.open(P, encoding='utf-8', newline='').read()

OLD = u"""{p:'patron:vess:loss',s:0,g:'l1',t:"Bad investment, that."},"""
NEW = u"""{p:'patron:vess:loss',s:0,g:'l1',t:"An ill bargain, that."},/* P874c */"""

if s.count(OLD) != 1:
    sys.exit('ANCHOR x%d (nothing written)' % s.count(OLD))
s = s.replace(OLD, NEW)

if 'Bad investment' in s:
    sys.exit('the struck word survives (nothing written)')
if 'An ill bargain' not in s:
    sys.exit('the replacement did not land (nothing written)')
io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: Vess loses the counting-house word')
