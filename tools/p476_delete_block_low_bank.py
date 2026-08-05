# -*- coding: utf-8 -*-
u"""P476 - delete block_low_bank. No card declares it; it is dead code.

RULED: delete it. Not a design gap - nothing in NPC_CARDS carries
`mechanic:'block_low_bank'`, so the two branches have never run and cannot.

Found during the oppCards lift sizing: the mechanic is implemented on BOTH seats
and dealt by nobody. Dead in the opposite direction from everything else that
session, which is why it read as a gap rather than as debris.

DELETED BY BRACE EXTENT, not by line range, so the whole `if` block goes and
nothing adjacent is clipped. The comments naming it were already corrected in
P473 - they used to attribute it to iron_gate_npc, which carries steal_on_bust.
"""
import io, os, re

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   'fark_proto.html')
with io.open(SRC, encoding='utf-8') as f:
    s = f.read()
orig = s

assert s.count("mechanic:'block_low_bank'") == 0, 'a card declares it - do not delete'

def cut_block(src):
    m = re.search(r"mechanic\s*===\s*'block_low_bank'", src)
    if not m:
        return src, False
    st = src.rfind('if(', 0, m.start())
    b = src.find('{', m.end())
    d, j = 0, b
    while j < len(src):
        if src[j] == '{':
            d += 1
        elif src[j] == '}':
            d -= 1
            if d == 0:
                break
        j += 1
    # take any trailing newline+indent with it so no blank rubble is left
    e = j + 1
    while e < len(src) and src[e] in '\r\n':
        e += 1
    return src[:st] + src[e:], True

cuts = 0
while True:
    s, did = cut_block(s)
    if not did:
        break
    cuts += 1
    assert cuts < 6, 'runaway'

assert cuts == 2, 'expected 2 branches, cut %d' % cuts
assert s != orig
body = re.sub(r'/\*.*?\*/', '', s, flags=re.S)
assert "mechanic==='block_low_bank'" not in body, 'a dispatch survives'
# the neighbours must still be intact - these sit next to steal_low_bank
assert body.count("mechanic==='steal_low_bank'") == 2, 'steal_low_bank was clipped'
assert body.count("mechanic==='challenge'") >= 2, 'challenge was clipped'
assert body.count('BANK_FX.') == 8 and body.count('BUST_FX.') == 9

with io.open(SRC, 'w', encoding='utf-8', newline='') as f:
    f.write(s)
print('P476 applied: block_low_bank deleted, %d branches removed' % cuts)
