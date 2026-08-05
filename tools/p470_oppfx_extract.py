# -*- coding: utf-8 -*-
u"""P470 - extract finOpp's four card-effect loops so the sim can call them.

RULED: build it. The sim's F.oppTurn reimplements the opponent's turn loop and
so runs NO bank-triggered card effects for either seat.

VERBATIM EXTRACTION, DELIBERATELY. Each loop's body moves unchanged into a
named function; finOpp calls it. Nothing is reordered, merged or tidied. That
makes the behaviour claim trivially checkable - the suite either still passes or
the move was wrong - and it is the only honest first step when the sim that
would catch a subtle change is itself the thing being fixed.

FOUR FUNCTIONS, NOT ONE, mirroring the structure rather than reorganising it.
The loops span 24%-94% of a 30,000-character function with other logic between
them, and the last runs AFTER `G.oPts+=pts` lands. Making them contiguous would
move code across the point where the bank lands - the same ordering dependency
that made the two-phase turn clear necessary, and not worth paying for tidiness.

  _oppFxOwnA(pts)     G.oCards  flat_bonus, double_first_bank
  _oppFxOwnB(pts)     G.oCards  gain_when_ahead
  _oppFxPlayer(pts)   G.pCards  steal_pct, steal_low_bank, block_low_bank,
                                challenge, halve_first_bank
  _oppFxDrain()       G.pCards  periodic_drain - after the bank, no pts

MEASURED FIRST: every loop contains ONLY its mechanic branches (no other card
ids), and `pts` is the sole free variable from finOpp's scope. An earlier scan
also reported `it`, which was the English word inside a comment - the scan did
not strip comments. So each signature is (pts) -> pts, and the drain loop needs
neither.

WHY G.pCards APPEARS HERE AT ALL: finOpp fires BOTH seats' cards, symmetric with
handleBank. Six of the nine are the PLAYER's cards taking from the patron's
bank. That is why the earlier "the sim cannot let the patron help itself"
framing was wrong and had to be retracted.
"""
import io, os, re

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   'fark_proto.html')
with io.open(SRC, encoding='utf-8') as f:
    s = f.read()
orig = s

m = re.search(r'\bfunction\s+finOpp\s*\(', s)
b = s.index('{', m.end() - 1)
d, j = 0, b
while j < len(s):
    if s[j] == '{':
        d += 1
    elif s[j] == '}':
        d -= 1
        if d == 0:
            break
    j += 1
fin = s[b:j + 1]
FIN_START = b

def loop_at(lo):
    """The whole `X.forEach(function(cid){...});` statement starting at lo."""
    bb = fin.index('{', lo)
    dd, k = 0, bb
    while k < len(fin):
        if fin[k] == '{':
            dd += 1
        elif fin[k] == '}':
            dd -= 1
            if dd == 0:
                break
        k += 1
    e = k + 1
    while e < len(fin) and fin[e] in ');':          # consume `);`
        e += 1
        if fin[e - 1] == ';':
            break
    return fin[lo:e]

SPECS = [
    (7049,  '_oppFxOwnA',   True,  'flat_bonus, double_first_bank'),
    (8489,  '_oppFxOwnB',   True,  'gain_when_ahead'),
    (10159, '_oppFxPlayer', True,  'steal_pct, steal_low_bank, block_low_bank, challenge, halve_first_bank'),
    (28233, '_oppFxDrain',  False, 'periodic_drain - runs AFTER the bank lands'),
]

fns = []
# highest offset first so earlier offsets stay valid
for lo, name, takes_pts, what in sorted(SPECS, key=lambda x: -x[0]):
    body = loop_at(lo)
    assert body.rstrip().endswith(');'), '%s: statement did not end in ); -> %r' % (name, body[-40:])
    assert s.count(body) == 1, '%s: loop text appears %d times in the file' % (name, s.count(body))
    sig = '(pts)' if takes_pts else '()'
    call = ('pts=%s(pts);' % name) if takes_pts else ('%s();' % name)
    fns.append((name, sig, body, takes_pts, what))
    s = s.replace(body, u"/* %s - extracted verbatim so the sim can run it too (P470) */\n      %s"
                  % (name, call))

DEFS = u"".join(
    u"""/* %s - %s.
   Lifted UNCHANGED out of finOpp so tools/sim_harness.js can call the same code
   instead of a reimplementation that ran none of it. */
function %s%s{
  %s
  %s}

""" % (name, what, name, sig, body, ('return pts;\n' if takes_pts else ''))
    for name, sig, body, takes_pts, what in reversed(fns))

ANCH = u"function handleBank("
assert s.count(ANCH) == 1
s = s.replace(ANCH, DEFS + ANCH)

assert s != orig, 'nothing changed'
for name, sig, body, takes_pts, what in fns:
    assert s.count(u'function %s%s{' % (name, sig)) == 1, '%s not defined once' % name
    expect = (u'pts=%s(pts);' % name) if takes_pts else (u'%s();' % name)
    assert s.count(expect) == 1, '%s not called once' % name

body_only = re.sub(r'/\*.*?\*/', '', s, flags=re.S)
# every mechanic still present exactly as before, just relocated
for mech in ['flat_bonus', 'double_first_bank', 'gain_when_ahead', 'steal_pct',
             'steal_low_bank', 'block_low_bank', 'challenge', 'halve_first_bank',
             'periodic_drain']:
    assert ("mechanic==='%s'" % mech) in body_only, '%s lost in the move' % mech
# finOpp no longer contains them
m2 = re.search(r'\bfunction\s+finOpp\s*\(', s)
b2 = s.index('{', m2.end() - 1)
d2, k2 = 0, b2
while k2 < len(s):
    if s[k2] == '{':
        d2 += 1
    elif s[k2] == '}':
        d2 -= 1
        if d2 == 0:
            break
    k2 += 1
fin2 = re.sub(r'/\*.*?\*/', '', s[b2:k2 + 1], flags=re.S)
for mech in ['flat_bonus', 'steal_pct', 'periodic_drain']:
    assert ("mechanic==='%s'" % mech) not in fin2, '%s still inside finOpp' % mech
# the earlier tables are untouched
assert body_only.count('BANK_FX.') == 8 and body_only.count('BUST_FX.') == 9

with io.open(SRC, 'w', encoding='utf-8', newline='') as f:
    f.write(s)
print('P470 applied: 4 loops extracted verbatim, finOpp now calls them')
