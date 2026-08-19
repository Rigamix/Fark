# -*- coding: utf-8 -*-
"""P779b: the gold warms up - the olive cast goes.

Screen-blending onto the table's brown (strong red, mid green, almost
no blue) drags any mid-amber toward yellow-olive - the last trace of
Denis's 'piss colour'. The core goes hotter and whiter (luminous
centre), the wide spill goes warmer (more red, less green), so the
summed light reads GOLD over the wood instead of olive.
"""
import io, os, sys, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'fark_proto.html')
s = io.open(P, encoding='utf-8', newline='').read()

old = """    octaves:[{r:3,col:'#fff3c4',passes:2},{r:8,col:'#ffd24a'},{r:20,col:'#ffb238',deep:true}]},"""
new = """    octaves:[{r:3,col:'#fff7dc',passes:2},{r:8,col:'#ffd24a'},{r:20,col:'#ff9e30',deep:true}]},"""
if s.count(old) != 1:
    sys.exit('ANCHOR x%d (nothing written)' % s.count(old))
s = s.replace(old, new)
io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: gold tint')
