# -*- coding: utf-8 -*-
"""Can any REACHABLE code path put an old-roster card into a hand?

Frozen is not the same as retired - a roster could be untouched because it is
finished. So this asks the other question directly: what reads CARDS, what could
deal from it, and can a player get there.

THE OVER-APPROXIMATION IS DELIBERATE AND POINTS THE SAFE WAY. The call graph
resolves names textually, so it will call things reachable that are not. That
means a "REACHABLE" verdict here is weak evidence and a "DEAD" verdict is strong
one - which is the direction you want when the decision on the other side is
deleting authored content. Anything this reports as live gets read by hand
rather than trusted.

WHAT COUNTS AS DEALING. Not every read of CARDS matters. CARDS_MAP, CARD_COVERS
and the icon lookups read the array to RENDER a card someone already has; they
cannot introduce one. What matters is a site that can put an id into
S.run.cards, G.pCards or G.oCards - the three places a held card lives.
"""
import io, os, re, collections

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   'fark_proto.html')
s = io.open(SRC, encoding='utf-8').read()

# ── scopes, brace-matched ──
scopes = []
for m in re.finditer(r'\bfunction\s*([A-Za-z_$][\w$]*)?\s*\(', s):
    b = s.find('{', m.end())
    if b < 0: continue
    d, j = 0, b
    while j < len(s):
        if s[j] == '{': d += 1
        elif s[j] == '}':
            d -= 1
            if d == 0: break
        j += 1
    scopes.append((m.start(), j, m.group(1)))

def enclosing(pos):
    best, span = None, None
    for a, b, nm in scopes:
        if a <= pos <= b and nm and (span is None or b - a < span):
            best, span = nm, b - a
    return best

# ── call graph, seeded with what a player can actually trigger ──
edges = collections.defaultdict(set)
for m in re.finditer(r'\b([A-Za-z_$][\w$]*)\s*\(', s):
    if re.search(r'function\s*$', s[max(0, m.start() - 12):m.start()]): continue
    edges[enclosing(m.start())].add(m.group(1))
roots = set(edges[None])
for m in re.finditer(r'\bon[a-z]+\s*=\s*["\']([^"\']*)["\']', s):
    roots |= set(re.findall(r'([A-Za-z_$][\w$]*)\s*\(', m.group(1)))
for m in re.finditer(r'addEventListener\([^,]+,\s*([A-Za-z_$][\w$]*)', s):
    roots.add(m.group(1))
# showScreen dispatches by string: an arm is only live if that string is passed
shown = set(re.findall(r"showScreen\(\s*'([a-z]+)'", s))
for m in re.finditer(r"case '([a-z]+)':\s*(\w+)\(", s):
    if m.group(1) not in shown:
        edges['showScreen'].discard(m.group(2))
live, q = set(), list(roots)
while q:
    f = q.pop()
    if f in live: continue
    live.add(f)
    q.extend(edges.get(f, ()))

# ── the sites that can DEAL, not merely render ──
DEAL = [
    (r'CARDS\.forEach\(function\(c\)\{if\(c\.rarity', 'builds a draft/shop pool from CARDS'),
    (r'S\.run\.cards\s*=\s*\[', 'assigns the run loadout directly'),
    (r'S\.run\.cards\.push', 'pushes into the run loadout'),
    (r'G\.pCards\s*=', 'assigns the player hand'),
    (r'G\.oCards\s*=', 'assigns the opponent hand'),
]
print('%-6s %-28s %-9s %s' % ('line', 'enclosing function', 'reach', 'what it does'))
rows = []
for pat, what in DEAL:
    for m in re.finditer(pat, s):
        fn = enclosing(m.start())
        rows.append((s[:m.start()].count('\n') + 1, fn, fn in live, what))
for line, fn, r, what in sorted(rows):
    print('%-6d %-28s %-9s %s' % (line, fn or '(top level)',
          'LIVE' if r else 'dead', what))

# ── and the hardcoded id lists: which roster do they name? ──
old_ids = set()
m = re.search(r'\bconst CARDS\s*=\s*\[', s)
i = s.index('[', m.end() - 1); d, j = 0, i
while j < len(s):
    if s[j] == '[': d += 1
    elif s[j] == ']':
        d -= 1
        if d == 0: break
    j += 1
old_ids = set(re.findall(r"\{id:'([a-z0-9_]+)'", s[i:j + 1]))

print('\nHARDCODED card-id lists assigned to a hand:')
for m in re.finditer(r"S\.run\.cards\s*=\s*\[([^\]]*)\]", s):
    ids = re.findall(r"'([a-z0-9_]+)'", m.group(1))
    fn = enclosing(m.start())
    hit = [x for x in ids if x in old_ids]
    print('  line %-6d %-24s %-6s old-roster ids: %s'
          % (s[:m.start()].count('\n') + 1, fn or '(top)',
             'LIVE' if fn in live else 'dead', hit or 'none'))
print('\nold roster size: %d' % len(old_ids))
