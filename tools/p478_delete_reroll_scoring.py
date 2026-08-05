# -*- coding: utf-8 -*-
u"""P478 - delete reroll_scoring. Same ruling as block_low_bank, not a new one.

RULED: "if the card doesn't exist, remove it" is the general answer to
unreferenced mechanics, not something scoped to block_low_bank specifically.

reroll_scoring is the identical shape: implemented, and NO CARD ANYWHERE
declares `mechanic:'reroll_scoring'`. It is worse than merely unreached - it
gated on `(usedOnce[cid]||0) < eff.uses` where nothing supplies `uses`, so the
comparison ran against undefined and was always false. Dead twice over.

Cut by brace extent so nothing adjacent is clipped, with asserts naming the
neighbours that must survive - the same method P476 used, for the same reason:
these branches sit shoulder to shoulder inside one card loop and a line-range
delete would take part of the next one.
"""
import io, os, re

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   'fark_proto.html')
with io.open(SRC, encoding='utf-8') as f:
    s = f.read()
orig = s

assert s.count("mechanic:'reroll_scoring'") == 0, 'a card declares it - do not delete'

m = re.search(r"mechanic\s*===\s*'reroll_scoring'", s)
assert m, 'no dispatch found'
st = s.rfind('if(', 0, m.start())
b = s.find('{', m.end())
d, j = 0, b
while j < len(s):
    if s[j] == '{':
        d += 1
    elif s[j] == '}':
        d -= 1
        if d == 0:
            break
    j += 1
e = j + 1
while e < len(s) and s[e] in '\r\n':
    e += 1
ls = s.rfind('\n', 0, st) + 1
if s[ls:st].strip() == '':
    st = ls
s = s[:st] + s[e:]

# the explanatory comment above it goes too - it documents code that is gone
CMT = u"reroll_scoring: reroll one scoring die, up to eff.uses times."
if CMT in s:
    i = s.index(CMT)
    cs = s.rfind('/*', 0, i)
    ce = s.find('*/', i) + 2
    while ce < len(s) and s[ce] in ' \t':
        ce += 1
    if ce < len(s) and s[ce] == '\n':
        ce += 1
    cls = s.rfind('\n', 0, cs) + 1
    if s[cls:cs].strip() == '':
        cs = cls
    s = s[:cs] + s[ce:]

assert s != orig
body = re.sub(r'/\*.*?\*/', '', s, flags=re.S)
assert "mechanic==='reroll_scoring'" not in body, 'dispatch survives'
assert 'reroll_scoring' not in body, 'still referenced in executable code'
# neighbours in the same loop must be intact
for keep in ['reroll_all_kept', 'swap_best_to_3']:
    assert ("mechanic==='%s'" % keep) in body, '%s was clipped' % keep
assert body.count('_useCap(') == 19, '_useCap sites: %d (was 20, reroll_scoring had one)' % body.count('_useCap(')
assert body.count('BANK_FX.') == 8 and body.count('BUST_FX.') == 9

with io.open(SRC, 'w', encoding='utf-8', newline='') as f:
    f.write(s)
print('P478 applied: reroll_scoring deleted')
