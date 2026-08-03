# -*- coding: utf-8 -*-
"""doBust's exit paths — which BRANCH reaches which clear.

Textual position has now failed twice in this investigation: nearest-preceding-
name was not lexical scope (26 sites misattributed), and a three-line adjacency
window undercounted co-located clears. So this does not ask "what is near
what". It walks doBust statement by statement, tracks the branch nesting each
clear sits under, and reports per PATH.

The risk being checked is specific: doBust's aggregate counts are kept×7,
pool×7, row×7, turnPts×6 — which LOOK uniform, exactly the way the 62 sites
looked collapsible before they were read. If one path clears a different subset
for a real reason, the way _afterRollImpl deliberately does elsewhere, an
ordered operation built off the aggregate would normalise it away silently, in
the most delicate function in the game.
"""
import io, os, re

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   'fark_proto.html')
s = io.open(SRC, encoding='utf-8').read()

m = re.search(r'\nfunction doBust\(\)\s*\{', s)
assert m, 'doBust not found'
i = s.find('{', m.start())
depth, j = 0, i
while j < len(s):
    if s[j] == '{': depth += 1
    elif s[j] == '}':
        depth -= 1
        if depth == 0: break
    j += 1
body = s[i:j + 1]
base_line = s[:i].count('\n') + 1
print('doBust spans %d lines\n' % (body.count('\n') + 1))

WIPES = {
    'kept':    re.compile(r'G\.kept\s*=\s*\[\]'),
    'pool':    re.compile(r'G\.pool\s*=\s*\[\]'),
    'row':     re.compile(r"clearRow\('playerDiceRow'\)"),
    'turnPts': re.compile(r'G\.turnPts\s*=\s*0'),
}

# walk the body tracking brace depth and the condition that opened each block
lines = body.split('\n')
stack = []          # (depth_at_open, condition_text)
depth = 0
events = []
for n, raw in enumerate(lines):
    l = raw.strip()
    # record clears with the branch stack in force
    hits = [k for k, rx in WIPES.items() if rx.search(l)]
    if hits:
        cond = ' > '.join(c for _, c in stack) or '(function body)'
        ret = 'return' in l
        events.append({'line': base_line + n, 'clears': hits,
                       'cond': cond[-96:], 'ret': ret})
    # crude but explicit block tracking
    opens = l.count('{') - l.count('}')
    cm = re.match(r'(?:\}\s*else\s+)?if\s*\((.+?)\)\s*\{?$', l) or \
         re.match(r'\}\s*else\s*\{', l)
    if cm:
        cond = cm.group(1) if cm.lastindex else 'else'
        stack.append((depth, re.sub(r'\s+', '', cond)[:60]))
    depth += opens
    while stack and depth <= stack[-1][0]:
        stack.pop()

print('%-7s %-9s %s' % ('line', 'clears', 'branch condition in force'))
for e in events:
    print('%-7d %-9s %s%s' % (e['line'], '+'.join(e['clears']),
                              e['cond'][:74], '   [returns]' if e['ret'] else ''))

# group by condition to see the paths
from collections import defaultdict
paths = defaultdict(set)
for e in events:
    paths[e['cond']].update(e['clears'])
print('\n\nPER PATH — the question the aggregate cannot answer:')
allfour = {'kept', 'pool', 'row', 'turnPts'}
for cond, cl in paths.items():
    missing = allfour - cl
    print('  %-58s %s%s' % (cond[:58], '+'.join(sorted(cl)),
          '   MISSING: ' + '+'.join(sorted(missing)) if missing else '   (all four)'))
print('\ndistinct branch paths that clear: %d' % len(paths))
