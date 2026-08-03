# -*- coding: utf-8 -*-
"""Turn-state clearing — what are the 62 sites actually clearing FOR?

The ordered operation has to express the intents that exist, not the ones that
would make a tidy API. Forcing one shape on sites that mean different things is
the powder_keg mistake at larger scale.

THE FIRST VERSION OF THIS FILE WAS WRONG, and wrong in its biggest number. It
attributed each site to the nearest PRECEDING `function NAME` declaration, which
is not scope: `_bustTolls` is 28 lines and contains ZERO wipes, yet 26 sites
were filed under it — everything between where it ends and the next named
declaration begins. The headline "77% cluster into four functions" was an
artifact of the instrument.

This version brace-matches every `function` keyword, named or anonymous, and
attributes a site to its INNERMOST ENCLOSING NAMED function. Anonymous
callbacks resolve outward to whatever named function contains them, which is
the attribution that answers the design question.
"""
import io, os, re, collections

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   'fark_proto.html')
s = io.open(SRC, encoding='utf-8').read()

# ── real scopes: every `function` keyword, brace-matched ──
scopes = []   # (start, end, name or None)
for m in re.finditer(r'\bfunction\s*([A-Za-z_$][\w$]*)?\s*\(', s):
    name = m.group(1)
    b = s.find('{', m.end())
    if b < 0: continue
    depth, j = 0, b
    while j < len(s):
        c = s[j]
        if c == '{': depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0: break
        j += 1
    scopes.append((m.start(), j, name))

def enclosing_named(pos):
    """innermost NAMED scope containing pos — anonymous callbacks resolve out"""
    best, best_span = '(top level)', None
    for a, b, nm in scopes:
        if a <= pos <= b and nm:
            span = b - a
            if best_span is None or span < best_span:
                best, best_span = nm, span
    return best

WIPES = [
    (r'G\.kept\s*=\s*\[\]', 'kept'),
    (r'G\.pool\s*=\s*\[\]', 'pool'),
    (r"clearRow\('playerDiceRow'\)", 'row+kept'),
    (r'G\.turnPts\s*=\s*0', 'turnPts'),
]

sites = []
for pat, kind in WIPES:
    for m in re.finditer(pat, s):
        pos = m.start()
        sites.append({'pos': pos, 'kind': kind,
                      'line': s[:pos].count('\n') + 1,
                      'fn': enclosing_named(pos)})

by_fn = collections.defaultdict(list)
for st in sites: by_fn[st['fn']].append(st)

print('TURN-STATE WIPE SITES: %d\n' % len(sites))
print('by variable:')
for k, n in collections.Counter(st['kind'] for st in sites).most_common():
    print('  %-10s %d' % (k, n))
print('\nby ENCLOSING NAMED FUNCTION (brace-matched, innermost):')
for fn, group in sorted(by_fn.items(), key=lambda kv: -len(kv[1])):
    kinds = collections.Counter(g['kind'] for g in group)
    print('  %-26s %2d   %s' % (fn, len(group),
          ' '.join('%s×%d' % (k, v) for k, v in kinds.most_common())))
print('\ndistinct functions that clear turn state: %d' % len(by_fn))
