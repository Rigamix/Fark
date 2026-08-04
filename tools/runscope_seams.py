# -*- coding: utf-8 -*-
"""The run-scoped domain's SEAMS - at which moments do these effects fire?

RULED: build the run-scoped domain as a genuine parallel system, with the same
discipline the match-scoped one got. That discipline started with a
measurement, not a design: _lm* was named after reading what Snare, Snuff and
Fog actually did, and the reading is what kept Trade out of it.

STATE HAS ALREADY BEEN MEASURED (runscope_lifetime.py): who arms each card,
what it carries, when it resolves. That found two cards sharing a shape, one
standalone, one needing no new code. Those findings stand.

THIS ASKS THE OTHER HALF OF THE QUESTION, and it is the half `famFire` answers
for the match domain: WHERE ARE THE MOMENTS. A bus is not a state container -
it is a set of named instants that content can attach to. The match bus has
ten. The run domain has never had its instants named at all; every one of the
six cards reaches into whatever function happens to run at the right time.

So: for each of the six, find the function its effect fires in, and group by
that function. A moment shared by several cards is a seam worth naming. A
moment used once is a call site, and naming it would be the sample-size-of-one
mistake the Tab ruling already rejected.

WHAT WOULD MAKE THIS MEASUREMENT WRONG, stated so the output is not overtrusted:
attribution is by innermost enclosing named function, which is a proxy for "the
moment". Two cards firing in the same function are not necessarily firing at
the same instant - endMatch is long. Any seam this suggests gets read by hand
before it gets built, exactly as the nine sites were.
"""
import io, os, re

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   'fark_proto.html')
raw = io.open(SRC, encoding='utf-8').read()

def blank_comments(t):
    out = list(t)
    for m in re.finditer(r'/\*.*?\*/', t, re.S):
        for i in range(m.start(), m.end()):
            if out[i] != '\n':
                out[i] = ' '
    return ''.join(out)

SIM = raw.find('BALANCE SIM HARNESS')
s = blank_comments(raw)
s = s[:SIM] + re.sub(r'[^\n]', ' ', s[SIM:])

scopes = []
for m in re.finditer(r'\bfunction\s*([A-Za-z_$][\w$]*)?\s*\(', s):
    b = s.find('{', m.end())
    if b < 0:
        continue
    d, j = 0, b
    while j < len(s):
        if s[j] == '{': d += 1
        elif s[j] == '}':
            d -= 1
            if d == 0:
                break
        j += 1
    scopes.append((m.start(), j, m.group(1)))

def enclosing(pos):
    best, span = None, None
    for a, b, nm in scopes:
        if a <= pos <= b and nm and (span is None or b - a < span):
            best, span = nm, b - a
    return best

# the state each card's EFFECT reads or writes - not its UI, not its arming
CARDS = {
    'Double Stakes':   [r'_dsArmed', r'_dsPlay'],
    'The Tab':         [r'_tabOwed'],
    'Hair of the Dog': [r'_hotdNext'],
    'For Keeps':       [r'_fkArmed', r'_fkPlay', r'_forKeeps'],
    'Cursed Table':    [r"famOwnTier\('marked_table'\)"],
    'High Table':      [r'_highTable', r"famOwnTier\('high_table'\)"],
}
# rendering is not a seam - it is a view of one
VIEWS = {'_gbRenderRoom', '_ptRoom', '_gbPeek', '_ptSeatSheet', '_seatTarget',
         '_seatTargetRaised', '_ptRoomHeader', None}

seams = {}
for card, pats in CARDS.items():
    for pat in pats:
        for m in re.finditer(pat, s):
            fn = enclosing(m.start())
            if fn in VIEWS:
                continue
            seams.setdefault(fn, set()).add(card)

print('RUN-SCOPED MOMENTS, by the function the effect fires in')
print('(view/render functions excluded - a display is not a seam)\n')
print('%-26s %-6s %s' % ('function', 'cards', 'which'))
print('-' * 76)
for fn, cards in sorted(seams.items(), key=lambda kv: (-len(kv[1]), kv[0] or '')):
    print('%-26s %-6d %s' % (fn or '(top level)', len(cards), ', '.join(sorted(cards))))

shared = {f: c for f, c in seams.items() if len(c) > 1}
print('\nMOMENTS SHARED BY MORE THAN ONE CARD: %d' % len(shared))
for fn, cards in sorted(shared.items(), key=lambda kv: -len(kv[1])):
    print('  %-24s %s' % (fn, ', '.join(sorted(cards))))
print("""
READ THIS AS: a moment several cards reach into is a candidate seam - the run
domain's equivalent of `bank` or `bust`. A moment one card uses is a call site,
and naming it would be the sample-size-of-one mistake the Tab ruling rejected.
Candidates get read by hand before anything is built on them; enclosing
function is a PROXY for the instant, and endMatch is long.""")
