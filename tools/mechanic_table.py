# -*- coding: utf-8 -*-
"""Scoping the mechanic table — relics and materials, 46 branches, 14 functions.

RULED: build the equivalent of BREAK_TRIGGERS for relics and materials. One
keyed table replacing scattered `effect.mechanic === '...'` branches, same move
that already works for the six death rows.

BREAK_TRIGGERS IS THE TEMPLATE AND IT IS WORTH SAYING WHY IT WORKS: it is keyed
by family, has TWO dispatch sites, and every row is data. Nothing reads a
family name in a branch. That is the target shape.

THIS FILE MEASURES WHAT WOULD HAVE TO MOVE, before any of it moves. Three things
decide whether one table can replace the branches, and only one of them is the
count:

  1. WHICH MECHANICS exist, and how many branches each has. A mechanic checked
     in one place is a table row. One checked in six places may be six
     different questions sharing a name - the Trade lesson.
  2. WHAT EACH BRANCH NEEDS from its surroundings. A branch reading only the
     die and a number is portable. One reading four locals from the middle of
     handleBank is not, and pretending otherwise is how a "shared" table ends
     up with a parameter for every caller.
  3. WHETHER THE SAME MECHANIC MEANS THE SAME THING in each place it appears.
     If `shatter_bonus` does one thing in scoreRoll and another in finOpp, the
     table has to carry two entries or the merge silently changes behaviour.

Nothing is built here. This is the pass that says whether the obvious move is
actually available, and the honest outcome may be "for some mechanics, not all".
"""
import io, os, re, collections

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   'fark_proto.html')
s = io.open(SRC, encoding='utf-8').read()

scopes = []
for m in re.finditer(r'\bfunction\s*([A-Za-z_$][\w$]*)?\s*\(', s):
    b = s.find('{', m.end())
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
    scopes.append((m.start(), j, m.group(1)))

def enclosing(pos):
    best, span = None, None
    for a, b, nm in scopes:
        if a <= pos <= b and nm and (span is None or b - a < span):
            best, span = nm, b - a
    return best

hits = collections.defaultdict(list)
# DIGITS BELONG IN THE CLASS. Without them this read 46 branches / 31 mechanics
# and silently dropped single1_bonus, single5_bonus and swap_best_to_3 - a
# character class narrower than the names it was matching, which is a false
# NEGATIVE, the kind that ends an investigation instead of prompting one.
for m in re.finditer(r"mechanic\s*===\s*'([a-z_0-9]+)'", s):
    mech = m.group(1)
    fn = enclosing(m.start()) or '(top)'
    ls = s.rfind('\n', 0, m.start()) + 1
    le = s.find('\n', m.start())
    hits[mech].append((fn, s[ls:le if le > 0 else len(s)].strip()))

print('%-22s %-6s %s' % ('mechanic', 'sites', 'functions it appears in'))
print('-' * 76)
one_place, several = [], []
for mech in sorted(hits, key=lambda k: -len(hits[k])):
    fns = sorted({f for f, _ in hits[mech]})
    print('%-22s %-6d %s' % (mech, len(hits[mech]), ', '.join(fns)[:46]))
    (one_place if len(fns) == 1 else several).append(mech)

print('\n' + '=' * 76)
# NOT "straight table rows" - that was this file's original claim and it was
# wrong. One function is where a mechanic APPEARS; it says nothing about whether
# the branch BODY can leave that function, which is what decides if a row is
# possible. mechanic_portable.py measures that and finds 2 of 18 portable as-is.
print('MECHANICS IN ONE FUNCTION ONLY (%d) - see mechanic_portable.py for' % len(one_place))
print('whether their bodies can actually move:')
print('   ' + ', '.join(one_place))
print('\nMECHANICS SPANNING SEVERAL FUNCTIONS (%d) - each needs reading before' % len(several))
print('it becomes one row, because the same name in two places may be two')
print('questions:')
print('   ' + ', '.join(several))

# how tangled is each branch in its surroundings?
print('\nWHAT THE MULTI-SITE ONES ACTUALLY DO, for the read:')
for mech in several[:6]:
    print('\n  %s' % mech)
    for fn, line in hits[mech]:
        print('    %-16s %s' % (fn, line[:58]))
