# -*- coding: utf-8 -*-
"""Which _cardArtImg call sites can a PLAYER actually reach?

_cardArtImg points at assets/Card_ART/<id>.png - the previous game's deck - and
has nine call sites. Denis's ruling is that nothing links to old art, so the
question is what each of those nine is, and the answer is not the same for all
nine: the draft screen turned out to be dead (its only reference is the `case
'draft'` in showScreen's switch; nothing calls showScreen('draft')), and a
screenshot of it looked exactly like a live screen showing old art.

REACHABLE BEFORE ACCURATE. Auditing what a surface shows before checking a
player can see it has produced wrong findings here three times. So this reports,
per call site, the enclosing function and whether anything calls that function -
and it counts CALLS specifically, not mentions, because a function's own
declaration and a switch `case` naming it are both textual matches that prove
nothing about reachability.
"""
import io, os, re, collections

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   'fark_proto.html')
s = io.open(SRC, encoding='utf-8').read()

# brace-matched scopes, same method the turn-state trace needed after
# nearest-preceding-name misfiled 26 sites
scopes = []
for m in re.finditer(r'\bfunction\s*([A-Za-z_$][\w$]*)?\s*\(', s):
    b = s.find('{', m.end())
    if b < 0: continue
    depth, j = 0, b
    while j < len(s):
        if s[j] == '{': depth += 1
        elif s[j] == '}':
            depth -= 1
            if depth == 0: break
        j += 1
    scopes.append((m.start(), j, m.group(1)))

def enclosing(pos):
    best, span = None, None
    for a, b, nm in scopes:
        if a <= pos <= b and nm and (span is None or b - a < span):
            best, span = nm, b - a
    return best

def call_count(fn):
    """CALLS, not mentions. `function foo(` and `case 'foo'` are not calls."""
    n = 0
    for m in re.finditer(r'\b' + re.escape(fn) + r'\s*\(', s):
        pre = s[max(0, m.start() - 12):m.start()]
        if re.search(r'function\s*$', pre): continue
        n += 1
    return n

# ── ONE LEVEL OF "does anything call it" IS NOT REACHABILITY ──────────────
# initDraftScreen has a caller - `case 'draft': initDraftScreen(data)` inside
# showScreen - and is still unreachable, because nothing ever calls
# showScreen('draft'). A function called only by dead code is dead. So: build
# the call graph, seed it with the things the PLAYER can actually trigger, and
# propagate.
#
# ROOTS are handlers named in HTML attributes (onclick=, onchange=, ...),
# addEventListener callbacks, and calls sitting at top level outside any
# function - those run without anyone calling them.
edges = collections.defaultdict(set)      # caller -> callees
for m in re.finditer(r'\b([A-Za-z_$][\w$]*)\s*\(', s):
    fn = m.group(1)
    if re.search(r'function\s*$', s[max(0, m.start() - 12):m.start()]): continue
    caller = enclosing(m.start())
    edges[caller].add(fn)                 # caller None == top level

roots = set(x for x in edges[None])
for m in re.finditer(r'\bon[a-z]+\s*=\s*["\']([^"\']*)["\']', s):
    for f in re.findall(r'([A-Za-z_$][\w$]*)\s*\(', m.group(1)):
        roots.add(f)
for m in re.finditer(r'addEventListener\([^,]+,\s*([A-Za-z_$][\w$]*)', s):
    roots.add(m.group(1))
# showScreen dispatches by STRING, so its switch arms are only reachable if
# that string is passed somewhere. Wire each case to its screen name instead of
# letting the switch body make every init look called.
screen_calls = set(re.findall(r"showScreen\(\s*'([a-z]+)'", s))
for m in re.finditer(r"case '([a-z]+)':\s*(\w+)\(", s):
    if m.group(1) not in screen_calls:
        edges['showScreen'].discard(m.group(2))

live, queue = set(), list(roots)
while queue:
    f = queue.pop()
    if f in live: continue
    live.add(f)
    queue.extend(edges.get(f, ()))

print('roots: %d   reachable functions: %d\n' % (len(roots), len(live)))
print('%-6s %-26s %-7s %s' % ('line', 'enclosing function', 'calls', 'reachable?'))
seen = collections.OrderedDict()
for m in re.finditer(r'_cardArtImg\(', s):
    pos = m.start()
    fn = enclosing(pos)
    if fn == '_cardArtImg': continue          # the declaration itself
    line = s[:pos].count('\n') + 1
    seen.setdefault(fn, []).append(line)

for fn, lines in seen.items():
    c = call_count(fn) if fn else 0
    r = (fn in live)
    print('%-6s %-26s %-7d %s' % (','.join(str(l) for l in lines)[:6], fn or '(top)',
          c, 'REACHABLE' if r else ('DEAD - no caller' if c == 0
              else 'DEAD - only dead callers')))
