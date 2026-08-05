# -*- coding: utf-8 -*-
u"""Card audit pass 3: DIRECTION and OWNERSHIP. Does a card benefit its holder?

Passes 1 and 2 checked that stated numbers are the numbers used. They cannot
check whether the effect moves those numbers the RIGHT WAY - and that is exactly
where tonight's two real bugs lived: `challenge` charging the rival twice, and
`ill_omen` reading "busted" on one seat and "scored nothing" on the other.

DIRECTION IS NOT PURELY A READING TASK. The sign is mechanical:

  WHOSE CARD    the enclosing loop - G.oCards is the patron's, G.pCards is the
                player's. Measured by brace extent, not by nearest text.
  WHO GAINS     G.oPts += / G.pPts += inside the branch, and which side `pts`
                or `total` is flowing to.

THE INVARIANT: a card in the PATRON's list should not hand points to the player,
and a card in the PLAYER's list should not hand points to the patron. Either is
a card working for the wrong side - which reads, in a match, as the opponent
inexplicably helping you or vice versa, and nothing logs it.

WHAT REMAINS UNCHECKABLE AFTER THIS: whether the magnitude is sensible, whether
the trigger condition matches the card's prose, and whether a card that moves
nothing (a reroll, a die swap) does the right thing to the right dice. Those are
the genuine reading list.
"""
import io, os, re, collections

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   'fark_proto.html')
s = io.open(SRC, encoding='utf-8').read()

# every card-list loop, by real brace extent
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

def owner_of(pos):
    best, span = None, None
    for a, e, side in loops:
        if a <= pos <= e and (span is None or e - a < span):
            best, span = side, e - a
    return best

def branch_at(pos):
    b = s.find('{', pos)
    if b < 0:
        return ''
    d, j = 0, b
    while j < len(s) and j - b < 2500:
        if s[j] == '{':
            d += 1
        elif s[j] == '}':
            d -= 1
            if d == 0:
                return s[b:j + 1]
        j += 1
    return s[b:b + 500]

rows = []
for m in re.finditer(r"mechanic\s*===\s*'([a-z_0-9]+)'", s):
    mech = m.group(1)
    side = owner_of(m.start())
    if side is None:
        continue
    body = re.sub(r'/\*.*?\*/', '', branch_at(m.end()), flags=re.S)
    # A TABLE ROW HIDES THE SIGN FROM A REGEX. Tonight's refactors moved the
    # arithmetic into SCORE_DRAIN / BUST_FX and rewrote challenge's deduction,
    # so three of fifteen score-touching branches stopped LOOKING like a += or
    # a -= while doing exactly the same thing. Measured: 15 touch a pool, the
    # textual patterns alone classified 12. Cleaner code, blinder instrument -
    # worth naming, because the fix is to teach the tool the new forms rather
    # than to read 12 and call it 15.
    gains_o = bool(re.search(r'G\.oPts\s*(?:\+=|=\s*\(?\(?G\.oPts(?:\|\|0\))?\s*\+)', body))
    gains_p = bool(re.search(r'G\.pPts\s*(?:\+=|=\s*\(?\(?G\.pPts(?:\|\|0\))?\s*\+)', body))
    loses_o = bool(re.search(r'G\.oPts\s*(?:-=|=\s*Math\.max\(0,\s*\(?\(?G\.oPts(?:\|\|0\))?\s*-)', body)) \
        or bool(re.search(r'G\.oPts\s*=\s*SCORE_DRAIN\.', body))
    loses_p = bool(re.search(r'G\.pPts\s*(?:-=|=\s*Math\.max\(0,\s*\(?\(?G\.pPts(?:\|\|0\))?\s*-)', body)) \
        or bool(re.search(r'G\.pPts\s*=\s*SCORE_DRAIN\.', body))
    if not (gains_o or gains_p or loses_o or loses_p):
        continue                       # moves no points; not this pass's job
    rows.append((mech, side, gains_o, gains_p, loses_o, loses_p))

print('%-20s %-8s %-22s %s' % ('mechanic', 'card of', 'moves', 'verdict'))
print('-' * 82)
bad = []
for mech, side, go, gp, lo, lp in sorted(rows):
    moves = []
    if go: moves.append('+patron')
    if gp: moves.append('+player')
    if lo: moves.append('-patron')
    if lp: moves.append('-player')
    # a patron's card must not simply hand the player points; a player's card
    # must not simply hand the patron points
    wrong = (side == 'o' and gp and not (go or lp)) or (side == 'p' and go and not (gp or lo))
    v = 'WRONG WAY' if wrong else 'ok'
    if wrong:
        bad.append((mech, side, moves))
    print('%-20s %-8s %-22s %s'
          % (mech, "patron's" if side == 'o' else "player's", ','.join(moves), v))

print('\n' + '=' * 82)
print('branches that move points: %d   pointing the wrong way: %d' % (len(rows), len(bad)))
for mech, side, moves in bad:
    print('   %-20s in the %s list but moves %s'
          % (mech, "patron's" if side == 'o' else "player's", ','.join(moves)))
print("""
A card working for the wrong side reads, in a match, as the opponent
inexplicably helping you - and nothing logs it. What this still cannot check:
magnitude, trigger-vs-prose, and cards that move dice rather than points.""")
