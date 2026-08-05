# -*- coding: utf-8 -*-
u"""Which of tonight's fixes can actually run? Per site, by enclosing card list.

generateOppCards begins `return [];` - a P1-cutover stub - so G.oCards is ALWAYS
empty and every branch inside a G.oCards loop is unreachable in this build.
G.pCards is populated normally, so those branches run once the player holds
cards.

I described several of tonight's fixes as live gameplay bugs without checking
they could execute. This is that check, per site rather than per patch, because
most patches touched BOTH copies of a mirrored mechanic - one live, one dead.

  LIVE   inside a G.pCards loop, or not card-gated at all (dice, feats, seams)
  DEAD   inside a G.oCards loop
  n/a    not inside any card loop - judged individually below

WHAT THIS DOES NOT CLAIM. "Live" here means REACHABLE, not exercised: the player
must actually hold the card for a pCards branch to fire. And a DEAD site is not
wasted work - it is what P5 switches on. The distinction being drawn is only
between "this changed what happens in a match today" and "this is correct and
waiting", which tonight's reporting blurred.
"""
import io, os, re, collections

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   'fark_proto.html')
s = io.open(SRC, encoding='utf-8').read()

# every card-list loop with its real brace extent
loops = []
for m in re.finditer(r'G\.([po])Cards\.(?:forEach|some|find|filter|map)\s*\(', s):
    b = s.find('{', m.start())
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
    loops.append((b, j, m.group(1)))

def where(pos):
    best, span = None, None
    for a, e, side in loops:
        if a <= pos <= e and (span is None or e - a < span):
            best, span = side, e - a
    return best

# the markers each patch left behind
PATCHES = [
    ('P464 WILD_LEVEL',      r'WILD_LEVEL\[',                    'wild dice'),
    ('P465 BANK_FX',         r'BANK_FX\.\w+\(',                  'bank arithmetic'),
    ('P466 BANK_TAKE',       r'BANK_TAKE\.\w+\(',                'steal_pct'),
    ('P466 SCORE_DRAIN',     r'SCORE_DRAIN\.\w+\(',              'periodic_drain'),
    ('P466 challenge rival', r'_chFromBank(?!P)',                'rival double-charge fix'),
    ('P467 challenge player',r'_chPenP',                         'player under-charge fix'),
    ('P468 BUST_FX',         r'BUST_FX\.\w+[\.\w]*\(',           'gain_pts / punish_busts'),
    ('P469 bust_immune',     r'oppTurnCount<=\(eff\.turns\|\|2\)','off-by-one fix'),
    ('P463 ill_omen',        r'_ioD2|_ioTake2',                  'boss omen migration'),
    ('P462 turn value',      r'_pTurnPts',                       'rivalTurn seam'),
]

print('%-24s %-6s %-6s %-6s %s' % ('patch', 'LIVE', 'DEAD', 'n/a', 'verdict'))
print('-' * 78)
summary = []
for name, pat, what in PATCHES:
    live = dead = na = 0
    for m in re.finditer(pat, s):
        w = where(m.start())
        if w == 'p':
            live += 1
        elif w == 'o':
            dead += 1
        else:
            na += 1
    if dead and not live:
        v = 'DEAD until P5'
    elif live and dead:
        v = 'BOTH copies - half live'
    elif live:
        v = 'live'
    else:
        v = 'not card-gated -> live'
    print('%-24s %-6d %-6d %-6d %s' % (name, live, dead, na, v))
    summary.append((name, live, dead, na, v, what))

print('\n' + '=' * 78)
print('THE ANSWER TO "did tonight change what happens in a match today":\n')
for name, live, dead, na, v, what in summary:
    tag = ('YES' if (live or (na and not dead)) else 'NO, waits for P5')
    print('  %-24s %-18s %s' % (name, tag, what))
print("""
A DEAD site is not wasted - it is exactly what P5 turns on, and it is correct
now rather than needing rediscovery then. The only thing being separated is
"changed a match today" from "correct and waiting", which is a distinction my
reporting collapsed.""")
