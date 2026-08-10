# -*- coding: utf-8 -*-
"""Do D10 and D11 share a root cause? And how many other sites share it?

THE ASSUMPTION UNDER TEST. Both entries read as "a die moved and its brand did
not", which invites treating them as one bug with one fix. That is a
thematic resemblance, and thematic resemblance is what produced the Ward
withdrawal (four features grouped by a shared prefix, three of which had no
lifetime at all). So it gets checked rather than assumed.

WHAT COUNTS AS THE SHAPE. `G.matchDice` and `G._enchArr` are index-parallel by
lane: position i is a material and position i is that lane's brand. Any site
that writes one at an index without writing the other at the same index moves a
die out from under its brand. `_removeDieAt` is the site that does it correctly
- it splices both, adjacently - so the file already contains the pattern.

WHAT THIS DELIBERATELY DOES NOT CLAIM. A site that writes matchDice without
_enchArr is a CANDIDATE, not a defect: assigning the same material back, or
writing a lane whose brand is meant to be dropped, are both legitimate. The
report names the enclosing function and the distance to the nearest _enchArr
touch so each can be read, and says so rather than counting them as findings.

Run: python tools/brand_travel_census.py
"""
import io, re, sys

SRC = io.open('fark_proto.html', 'rb').read().decode('utf-8').replace('\r\n', '\n')
LINES = SRC.split('\n')


def line_of(pos):
    return SRC.count('\n', 0, pos) + 1


FN_STARTS = sorted([(line_of(m.start()), m.group(1))
                    for m in re.finditer(r'^function\s+([A-Za-z0-9_$]+)\s*\(', SRC, re.M)])
CFX_STARTS = sorted([(line_of(m.start()), 'CFX.' + m.group(1))
                     for m in re.finditer(r'^CFX\.([a-z_0-9]+)\s*=', SRC, re.M)])
ALL_STARTS = sorted(FN_STARTS + CFX_STARTS)


def enclosing(line):
    name = '(top level)'
    for ln, nm in ALL_STARTS:
        if ln <= line:
            name = nm
        else:
            break
    return name


# every INDEXED write to either die array — the shape that can desync a lane
WRITE_RE = re.compile(r'G\.(matchDice|matchOppDice)\[([^\]]{1,40})\]\s*=(?!=)')
ENCH_RE = re.compile(r'G\._enchArr\b')

ench_lines = set(line_of(m.start()) for m in ENCH_RE.finditer(SRC))

rows = []
for m in WRITE_RE.finditer(SRC):
    ln = line_of(m.start())
    arr, idx = m.group(1), m.group(2).strip()
    near = min((abs(e - ln) for e in ench_lines), default=9999)
    rows.append(dict(line=ln, arr=arr, idx=idx, fn=enclosing(ln), enchWithin=near,
                     text=LINES[ln - 1].strip()[:96]))

print('indexed writes to matchDice / matchOppDice: %d\n' % len(rows))
print('%-6s %-16s %-26s %-6s %s' % ('line', 'array', 'in', '_ench', 'code'))
for r in rows:
    print('%-6d %-16s %-26s %-6s %s'
          % (r['line'], r['arr'], r['fn'],
             (str(r['enchWithin']) if r['enchWithin'] < 40 else '-'), r['text']))

far = [r for r in rows if r['enchWithin'] >= 40]
print('\nNO _enchArr TOUCH WITHIN 40 LINES (%d of %d) - candidates, read each:'
      % (len(far), len(rows)))
by_fn = {}
for r in far:
    by_fn.setdefault(r['fn'], []).append(r['line'])
for fn in sorted(by_fn):
    print('  %-30s lines %s' % (fn, by_fn[fn]))
print('\nProximity is a HINT, not a verdict - a paired write can sit further off,')
print('and a nearby _enchArr line can belong to a different lane. Read the site.')
