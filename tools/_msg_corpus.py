# -*- coding: utf-8 -*-
"""How long are the in-match messages, really?

The status line is `white-space:nowrap` at 5cqw, so any message wider than the
strip runs off BOTH edges - which is what Denis photographed. Before sizing a
fix, measure the corpus it has to hold: the literal strings handed to famLog and
setStatusMsg. Concatenated ones are longer still, so these are a floor.
"""
import io, re, statistics

s = io.open('fark_proto.html', encoding='utf-8').read()

pat = re.compile(r"(?:famLog|setStatusMsg)\(\s*'((?:[^'\\]|\\.)*)'")
msgs = sorted({m.group(1) for m in pat.finditer(s)}, key=len, reverse=True)

print('%d literal messages\n' % len(msgs))
for m in msgs[:15]:
    print('%3d  %s' % (len(m), m))

L = [len(m) for m in msgs]
L.sort()
print('\nlen: max %d   p90 %d   median %d' % (L[-1], L[int(len(L) * .9)], statistics.median(L)))
for n in (26, 30, 34, 40):
    print('  over %d chars: %d of %d' % (n, sum(1 for x in L if x > n), len(L)))
