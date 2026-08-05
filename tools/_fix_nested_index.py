# -*- coding: utf-8 -*-
u"""Repair the one P477 site with a NESTED index, and the assert that missed it.

`G.npcCardState.playerOnce[G.pCards[_omrI]]` has brackets inside brackets. The
transform's capture was `[^\\]]+`, which stops at the FIRST `]`, so it produced

    (G.npcCardState.playerOnce[G.pCards[_omrI]||0)<_useCap(G.pCards[_omrI)]

- unbalanced, and the parse gate caught it. The matching `=true` on the next
line was left untouched for the same reason (the pattern needed `]=true` and the
text has `]]=true`), AND the assert meant to catch a surviving `=true` used the
same `[^\\]]+`, so it was blind to it too.

Worth stating: one bad character class produced a syntax error, a silently
skipped conversion, and an assert that could not see either. The parse gate is
what stopped it - the asserts agreed with the bug because they shared its
assumption.
"""
import io, os

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   'fark_proto.html')
s = io.open(SRC, encoding='utf-8').read()

BAD_GATE = (u"(G.npcCardState.playerOnce[G.pCards[_omrI]||0)"
            u"<_useCap(G.pCards[_omrI)]")
assert s.count(BAD_GATE) == 1, 'broken gate matched %d' % s.count(BAD_GATE)
s = s.replace(BAD_GATE,
              u"(G.npcCardState.playerOnce[G.pCards[_omrI]]||0)"
              u"<_useCap(G.pCards[_omrI])")

BAD_SET = u"G.npcCardState.playerOnce[G.pCards[_omrI]]=true;"
assert s.count(BAD_SET) == 1, 'unconverted set matched %d' % s.count(BAD_SET)
s = s.replace(BAD_SET,
              u"G.npcCardState.playerOnce[G.pCards[_omrI]]="
              u"(G.npcCardState.playerOnce[G.pCards[_omrI]]||0)+1;")

# now a bracket-balanced check, not the one that shared the bug's assumption
import re
for m in re.finditer(r'_useCap\(([^)]*)\)', s):
    a = m.group(1)
    assert a.count('[') == a.count(']'), 'still unbalanced: %s' % a
assert not re.search(r'npcCardState\.(usedOnce|playerOnce)\[[^=]{0,60}\]\s*=\s*true', s), \
    'a boolean set still survives'

io.open(SRC, 'w', encoding='utf-8', newline='').write(s)
print('nested-index site repaired: gate rebalanced, set converted')
