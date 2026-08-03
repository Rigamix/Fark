# -*- coding: utf-8 -*-
"""Do the four run-scoped cards actually share a lifecycle?

The direction says to build a shared run-scoped primitive before the six cards,
"same reasoning as lane markers before Snare/Snuff/Fog". That reasoning includes
the step that mattered most: MEASURING THE CANDIDATES FIRST. Doing that for the
lane markers found Trade was not one of them - it had no window at all, and a
primitive built from the other three would have imposed one on the one card
designed without it.

The claim to test is from the direction doc: Double Stakes, The Tab, Hair of the
Dog and For Keeps "all have some version of 'something is set now, something
happens later'". True at that level of description - and so was "four lane
markers with a placement, a window and an expiry", which was three.

So this reports, per card, the three things a run-scoped lifecycle consists of:

  ARM      where the state is set, and BY WHOM - the player choosing, or an
           outcome setting it. That distinction is the one most likely to break
           a shared primitive, because an armed state the player did not choose
           is not a wager they can be shown pending.
  CARRY    what is stored - a boolean, or a quantity with its own arithmetic
  RESOLVE  where it is read out and cleared, and WHEN that moment is

If the four disagree on any of those, a single arm/resolve pair cannot express
them and the honest answer is fewer primitives covering fewer cards.
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

CARDS = [
    ('Double Stakes',    '_dsArmed'),
    ('The Tab',          '_tabOwed'),
    ('Hair of the Dog',  '_hotdNext'),
    ('For Keeps',        '_fkArmed'),
]

for name, var in CARDS:
    print('\n' + '=' * 76)
    print('%s   S.run.%s' % (name, var))
    print('=' * 76)
    rows = []
    for m in re.finditer(r'\b' + re.escape(var) + r'\b', s):
        ls = raw.rfind('\n', 0, m.start()) + 1
        le = raw.find('\n', m.start())
        line = raw[ls:le if le > 0 else len(raw)].strip()
        tail = s[m.end():m.end() + 24]
        # WRITE vs READ, and `=` is not `==` - the mistake that cost three
        # false findings in the lane-marker audit.
        if re.match(r'\s*=(?!=)', tail):
            val = re.match(r'\s*=\s*([^;,)]{0,26})', tail)
            kind = 'SET  -> ' + (val.group(1).strip() if val else '?')
        elif re.match(r'\s*(\+\+|--|\+=|-=)', tail):
            kind = 'MUTATE'
        else:
            kind = 'read'
        rows.append((s[:m.start()].count('\n') + 1,
                     enclosing(m.start()) or '(top level)', kind, line))
    for ln, fn, kind, line in rows:
        print('  %-6d %-22s %-22s %s' % (ln, fn, kind, line[:56]))
    sets = [r for r in rows if r[2].startswith('SET')]
    print('  --> %d set site(s), %d read/mutate' % (len(sets), len(rows) - len(sets)))

print("""
WHAT TO READ OFF THIS. The four share a shared primitive only if they agree on
who ARMS (player choice vs an outcome), what is CARRIED (a flag vs a quantity)
and when it RESOLVES. Disagreement on any one of those is the Trade result
again: a family that shares a sentence but not a shape.""")
