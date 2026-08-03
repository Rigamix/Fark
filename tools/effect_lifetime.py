# -*- coding: utf-8 -*-
"""Phase 3 groundwork - how does each lane marker express its LIFETIME today?

Phase 3 settles effect lifetime: Ward's armed window, and Snare / Snuff / Fog /
Trade, which the re-plan describes as "lane markers with a placement, a window
and an expiry rather than effects with a moment".

BEFORE DESIGNING A SHARED LIFETIME, MEASURE THE FIVE THAT EXIST. Phase 2 is the
argument for doing it this way round: `_fxFreeDice()` looked like one shared
query across four sites and turned out to be four different things, and folding
them would have silently taken Powder Keg's "kept dice included" away from it.
A lifetime primitive built from three of these five and imposed on the other
two would be the same mistake with a longer blast radius, because lifetime
governs WHEN things fire rather than what one card does.

So this reports, per marker, the three things a lifetime actually consists of:

  PLACEMENT  where the state is armed (assigned truthy)
  WINDOW     where it is READ - the sites whose behaviour it changes
  EXPIRY     where it is retired

and WHICH FUNCTION each sits in, because "expires at end of turn" and "expires
when the opponent banks" are different lifetimes that look identical in a grep.
Position misled this project three times inside doBust alone, so attribution is
by brace-matched enclosing scope, never by proximity.
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

MARKERS = [
    ('ward',  [r'G\._wardArmed', r'G\._wardCharges', r'G\._wardBanks', r'G\._wardBoost']),
    ('snare', [r'G\._snare\b']),
    ('snuff', [r'G\._snuff\b']),
    ('fog',   [r'G\._fog\b']),
    ('trade', [r'G\._tradeSwaps']),
]

# THE FIRST VERSION REPORTED "NO EXPIRY SITE" FOR SNARE, SNUFF AND FOG, AND ALL
# THREE EXPIRE. It recognised only `G._fog = null` - the whole marker being
# replaced - and these markers retire themselves by flipping one of their own
# fields: `else G._fog.live=false`. That read as just another mention, so it was
# filed under WINDOW and the summary announced, in capitals, that the marker was
# never cleared.
#
# Worth naming for WHAT it would have caused rather than that it was wrong: the
# output was three loud false alarms beside two quiet correct rows, and the
# false alarms were the interesting-looking part. An instrument whose failure
# mode is MANUFACTURING findings is more dangerous than one that misses them,
# and this is the second today - the font probe's first pass "found" overflow on
# dice that contain no text.
CLEAR_RHS  = re.compile(r'^\s*=\s*(null|false|0|\[\]|\{\}|undefined)\s*[;,)\}]')
CLEAR_PROP = re.compile(r'^\.\w+\s*=\s*(null|false|0|undefined)\s*[;,)\}]')
PLACE_RHS  = re.compile(r'^\s*=\s*(?!=)')

for name, pats in MARKERS:
    rows = {'PLACEMENT': [], 'EXPIRY': [], 'WINDOW': []}
    for pat in pats:
        for m in re.finditer(pat, s):
            tail = s[m.end():m.end() + 40]
            line = s[:m.start()].count('\n') + 1
            fn = enclosing(m.start()) or '(top level)'
            if CLEAR_RHS.match(tail) or CLEAR_PROP.match(tail):
                kind = 'EXPIRY'
            elif PLACE_RHS.match(tail):
                kind = 'PLACEMENT'
            else:
                kind = 'WINDOW'
            rows[kind].append((line, fn))
    print('\n' + '=' * 72)
    print('%-6s  placement %d   window %d   expiry %d'
          % (name.upper(), len(rows['PLACEMENT']), len(rows['WINDOW']),
             len(rows['EXPIRY'])))
    print('=' * 72)
    for kind in ('PLACEMENT', 'WINDOW', 'EXPIRY'):
        seen = collections.Counter(fn for _, fn in rows[kind])
        txt = ', '.join('%s x%d' % (f, c) if c > 1 else f
                        for f, c in seen.most_common())
        print('  %-9s %s' % (kind, txt or '-'))
    if not rows['EXPIRY']:
        print('  !! NO EXPIRY SITE - this marker is never retired.')

    # ── IS THE WINDOW FIELD ACTUALLY READ? ────────────────────────────────
    # The three lane markers are armed with the same shape - {lane, live, turn}
    # - where `turn` IS the window: the specific opponent turn this is armed
    # for. A marker that WRITES that field and never READS it has no window; it
    # fires the next time its check happens to run.
    # The word boundary matters and is easy to get wrong: `.turn` without it
    # also matches `.turns`, the Kindred two-turn counter, which is a different
    # field. A first pass here conflated the two.
    # AND `=` IS NOT THE SAME CHARACTER AS `==`. The pass before this one used
    # (?!\s*=) to mean "not an assignment" and so rejected `G._snare.turn===
    # G.oppTurnCount` - a COMPARISON - counting the read as a write and
    # reporting all three markers as never reading their own window field. Two
    # of the three do read it; only snuff does not. A single character of regex
    # turned one real finding into three false ones.
    # Third correction to this tool. Each was caught the same way: by reading
    # the lines it was describing and finding they said something else.
    var = 'G._' + name
    reads  = re.findall(re.escape(var) + r'\.turn\b\s*(?!=[^=])', s)
    writes = re.findall(re.escape(var) + r'\.turn\b\s*=(?!=)', s)
    lit    = re.findall(re.escape(var) + r'\s*=\s*\{[^}]*\bturn\s*:', s)
    if (writes or lit) and not reads:
        print('  !! .turn is SET (%d) and READ 0 times - armed for a turn it '
              'never checks' % (len(writes) + len(lit)))
    elif reads:
        print('  .turn read %d, set %d - the window gate is honoured'
              % (len(reads), len(writes) + len(lit)))

print('\n\nWHAT TO READ OFF THIS: a marker whose EXPIRY sits in one function has')
print('one lifetime. One whose expiry is spread across several has a lifetime')
print('that is currently a CONVENTION, and that is what Phase 3 has to name.')
