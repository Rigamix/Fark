# -*- coding: utf-8 -*-
u"""Card audit pass 5: the BANK-modifying branches pass 3 could not see.

Pass 3 checked direction by watching G.pPts / G.oPts. Ten branches never touch a
pool: they change `total` or `pts` - the BANK - and the money reaches a pool
outside the branch. So pass 3 silently skipped them, and pass 4's first cut
mislabelled them as dice-movers because they had no score-pool signature.

That is the same blindness pass 3 found, one layer wider: four of the ten now
route through the BANK_FX table built tonight, which means the arithmetic no
longer looks like arithmetic at the call site either.

THE INVARIANT NEEDS THE ENCLOSING FUNCTION, not just the card list, because the
function decides WHOSE bank is on the table:

  handleBank  the PLAYER banks    -> a patron's card should LOWER it,
                                     a player's card should RAISE it
  finOpp      the PATRON banks    -> a patron's card should RAISE it,
                                     a player's card should LOWER it

A card that raises the bank of the side it is working against is the same class
of bug as a score-pool branch pointing the wrong way, and it is invisible in a
match: the opponent simply banks more than it should, which looks like variance.

NOTE ON THE PREVIOUS DRAFT: an earlier version of this printed a hardcoded 'ok'
column. That is a display, not a check, and it is exactly the shape of thing this
audit exists to catch. The verdict here is computed.
"""
import io, os, re

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   'fark_proto.html')
s = io.open(SRC, encoding='utf-8').read()

def span_of(name):
    m = re.search(r'\bfunction\s+' + name + r'\s*\(', s)
    if not m:
        return None
    b = s.index('{', m.end() - 1)
    d, j = 0, b
    while j < len(s):
        if s[j] == '{':
            d += 1
        elif s[j] == '}':
            d -= 1
            if d == 0:
                return (b, j)
        j += 1
    return None

HB = span_of('handleBank')
# THE PATRON'S BANK CODE IS NO LONGER ALL INSIDE finOpp. P470 extracted its four
# card-effect loops into _oppFxOwnA/B/Player/Drain earlier tonight, so a span
# check against finOpp alone reported five of ten branches as "(other)" and
# refused to judge them. That is the SAME refactor blindness this tool was
# written to catch, landing inside the tool - which is worth keeping rather than
# quietly fixing, because it is the third instance and the first two were also
# only found by looking.
FO_SPANS = [sp for sp in (span_of('finOpp'), span_of('_oppFxOwnA'),
                          span_of('_oppFxOwnB'), span_of('_oppFxPlayer'),
                          span_of('_oppFxDrain')) if sp]

loops = []
for m in re.finditer(r'G\.([po])Cards\.(?:forEach|some|find|filter|map)\s*\(', s):
    b = s.find('{', m.start())
    if b < 0:
        continue
    d, j = 0, b
    while j < len(s):
        if s[j] == '{':
            d += 1
        elif s[j] == '}':
            d -= 1
            if d == 0:
                break
        j += 1
    loops.append((b, j, m.group(1)))

def owner(pos):
    best, sp = None, None
    for a, e, side in loops:
        if a <= pos <= e and (sp is None or e - a < sp):
            best, sp = side, e - a
    return best

def branch_at(pos):
    b = s.find('{', pos)
    d, j = 0, b
    while j < len(s) and j - b < 2500:
        if s[j] == '{':
            d += 1
        elif s[j] == '}':
            d -= 1
            if d == 0:
                return s[b:j + 1]
        j += 1
    return s[b:b + 600]

RAISE = re.compile(r'\b(?:total|pts)\s*\+=|=\s*BANK_FX\.(?:flat_bonus|gain_when_ahead|double_first_bank)')
LOWER = re.compile(r'\b(?:total|pts)\s*-=|=\s*BANK_FX\.halve_first_bank|\b(?:total|pts)\s*=\s*0')

print('%-20s %-9s %-9s %-7s %s' % ('mechanic', 'card of', 'in', 'effect', 'verdict'))
print('-' * 74)
bad, rows = [], 0
for m in re.finditer(r"mechanic\s*===\s*'([a-z_0-9]+)'", s):
    body = re.sub(r'/\*.*?\*/', '', branch_at(m.end()), flags=re.S)
    if re.search(r'G\.[po]Pts', body):
        continue                                  # pass 3 owns these
    side = owner(m.start())
    if side is None:
        continue
    raises, lowers = bool(RAISE.search(body)), bool(LOWER.search(body))
    if not (raises or lowers):
        continue
    if HB and HB[0] <= m.start() <= HB[1]:
        fn, whose_bank = 'handleBank', 'p'
    elif any(a <= m.start() <= e for a, e in FO_SPANS):
        fn, whose_bank = 'finOpp/_oppFx', 'o'
    else:
        fn, whose_bank = '(other)', None
    rows += 1
    if whose_bank is None:
        v = 'n/a'
    else:
        helps = 'o' if (raises and whose_bank == 'o') or (lowers and whose_bank == 'p') else 'p'
        v = 'ok' if helps == side else 'WRONG SIDE'
        if v == 'WRONG SIDE':
            bad.append((m.group(1), side, fn, 'raises' if raises else 'lowers'))
    print('%-20s %-9s %-9s %-7s %s'
          % (m.group(1), "patron's" if side == 'o' else "player's", fn,
             'raises' if raises else 'lowers', v))

print('\n' + '=' * 74)
print('bank-modifying branches: %d   helping the wrong side: %d' % (rows, len(bad)))
for mech, side, fn, op in bad:
    print('   %-20s %s card %s the bank in %s'
          % (mech, "patron's" if side == 'o' else "player's", op, fn))
print("""
These were invisible to pass 3 because the money reaches a pool OUTSIDE the
branch. Four of them now route through BANK_FX, so the arithmetic does not look
like arithmetic at the call site either - the same refactor blindness pass 3
found, one layer wider.""")
