# -*- coding: utf-8 -*-
"""Sizing seam coverage by measuring runOppTurn, not by estimating it.

The opponent's turn raises ONE of eight CFX seams (`bank`). The other seven -
turnStart, roll, bust, commit, bankBonus, deadRoll, rivalTurn - fire with
actor 'p' only. Making boss cards work means raising those seven from the
opponent's turn.

TWO WRONG SIZE ESTIMATES FOR THIS AREA TODAY means a third is worth nothing.
So this measures the same thing the run-scoped seam pass measured: for each
seam, does a corresponding MOMENT exist in the opponent's turn, and is it a
single identifiable point or spread across a long function?

That distinction is what decided matchArmed (three consecutive lines - a real
seam) against endMatch (four cards across 619 lines - a shared function, not a
shared moment) and seatCommit (three cards with load-bearing work between).
It is the only thing that separates "add a call" from "restructure a turn".

WHAT THIS PRODUCES: a per-seam answer of EXISTS / SPREAD / ABSENT, with the
evidence. Not a time estimate - a shape, which is what the run-scoped pass
produced and what turned out to be the useful thing.
"""
import io, os, re

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   'fark_proto.html')
s = io.open(SRC, encoding='utf-8').read()

def span(name):
    m = re.search(r'\nfunction ' + name + r'\s*\(', s)
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
                return (b, j, s[:b].count('\n') + 1)
        j += 1
    return None

sp = span('runOppTurn')
assert sp, 'runOppTurn not found'
b, e, base = sp
body = s[b:e + 1]
lines = body.count('\n') + 1
print('runOppTurn: lines %d-%d (%d lines)\n' % (base, base + lines - 1, lines))

# the moments an opponent turn actually has, by what the code does
MOMENTS = [
    ('turnStart', r'oppTurnCount\s*=\s*\(G\.oppTurnCount\|\|0\)\+1|function step\(\)'),
    ('roll',      r'oppRollNum\+\+|oppRollNum\s*=\s*oppRollNum\+1|rollOpp|_oppRoll'),
    ('commit',    r'scoreRoll\('),
    ('bank',      r"famFire\('bank',\{actor:'o'"),
    ('bankBonus', r'oppBank\s*\+=|finOpp\('),
    ('bust',      r'oppBust|_oppBust|bust\(\)'),
    ('deadRoll',  r'anyScoring\('),
]
print('%-11s %-7s %s' % ('seam', 'hits', 'where in the body (line, % in)'))
print('-' * 74)
found = {}
for name, pat in MOMENTS:
    hits = []
    for m in re.finditer(pat, body):
        ln = body[:m.start()].count('\n') + 1
        hits.append((ln, int(100 * ln / lines)))
    found[name] = hits
    if hits:
        loc = ', '.join('%d (%d%%)' % h for h in hits[:5])
    else:
        loc = '-- no such moment in this function --'
    print('%-11s %-7d %s' % (name, len(hits), loc))

print('\n' + '=' * 74)
print('SHAPE PER SEAM')
for name, hits in found.items():
    if not hits:
        print('  %-11s ABSENT  - the opponent turn has no such moment here'
              % name)
        continue
    lo, hi = min(h[0] for h in hits), max(h[0] for h in hits)
    spread = hi - lo
    if len(hits) == 1 or spread <= 6:
        print('  %-11s POINT   - %d hit(s) within %d lines: one place to raise it'
              % (name, len(hits), spread))
    else:
        print('  %-11s SPREAD  - %d hits across %d lines: raising one call would'
              % (name, len(hits), spread))
        print('  %-11s           pick a moment the code does not currently have'
              % '')

print("""
READ THIS AS: POINT seams are an added call. SPREAD seams need a decision about
WHICH moment is the seam, the same decision seatCommit failed. ABSENT seams
mean the opponent's turn does not do that thing at all, and a card depending on
it cannot work for a boss however it is gated.""")
