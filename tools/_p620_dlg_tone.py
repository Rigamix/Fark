# -*- coding: utf-8 -*-
"""P620 (Part 4): the tone fixes that exist in this build.

The brief lists seven fixes across six lines. TWO of the six "before" strings are
in fark_proto.html; the other four are not present in any form - not an
apostrophe-encoding miss, the distinguishing fragments ("People say more with
what they", "Every ledger tells a story", "Spend enough time alone and silence",
"thinks stew") return nothing at all.

That is consistent with the rest of the brief's arithmetic: it says it audited
~1,300 existing lines and that each patron has 6 backstory lines, where this
build has 371 rows total and 3 per patron. The audit was done against a larger
document than the one that ships, so Part 4 is applied to what is actually here
and the remaining four are reported rather than invented into place.

Not attempting a fuzzy match on the missing four. A "close enough" line rewritten
to the brief's "after" text would silently replace something the brief never
looked at.
"""
import io, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'fark_proto.html')
s = io.open(P, encoding='utf-8', newline='').read()
n = 0

FIXES = [
    ('DUNSTAN',
     u"Everything worth having gets hammered first. Applies to more than iron.",
     u"Everything worth having gets hammered first. I only mean the iron, before you ask."),
    ('TUCK',
     u"Bread rises whether you believe in it or not. Faith's got nothing to do with baking.",
     u"Bread doesn't care if you believe in it. Just rises."),
]

for who, before, after in FIXES:
    c = s.count(before)
    if c != 1:
        sys.exit('ANCHOR x%d for %s: %r' % (c, who, before[:60]))
    s = s.replace(before, after)
    n += 1
    print('  ok  %s' % who)

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('\n%d of 6 applied; 4 not present in this build:' % n)
for m in ('EIRA', 'CORBIN', 'THORNE', 'TUCK (second fix)'):
    print('   not found: %s' % m)
