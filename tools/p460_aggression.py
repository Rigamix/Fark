# -*- coding: utf-8 -*-
"""P460 - raise patron aggression.

RULED: raise aggression. The measured problem is not that the game is too easy
or too hard - it is that SKILL STOPS MATTERING as tiers rise (agent spread
narrows), so the thing to watch is spread widening back out with tier, not win
rate moving.

BASELINE FIRST, AND IT CHANGED WHAT COUNTS AS A RESULT. `spread` is
max(win%) - min(win%) across four agents - a max-minus-min over four samples,
which is inherently noisy. Two seeds of the tier sweep:

    tier   0     1     2     3     4     5     6     7
    seedA  60.9  42.7  42.7  31.4  30.5  30.5  35.0  23.6
    seedB  55.0  45.0  39.1  28.2  26.8  34.1  30.0  28.2

Per-tier noise is +/-3 to 6. The NARROWING IS REAL - a ~30 point fall dwarfs
that - but the headline "60.9 -> 23.6" is one seed; the other reads
"55.0 -> 28.2". Direction established, magnitude not to better than ~10 points.

So any change smaller than that cannot be called from a single before/after
pair, and this patch is measured against two seeds either side rather than one.

THE RAISE: +0.06 on both ends of every tier's band, capped at 0.95.

Uniform because there is no measurement saying which tiers need it most - the
spread narrows steadily rather than breaking at one rung. Capped because tier 7
is already .82-.90 and has almost no headroom; without the cap the top tiers
would move a third as far as the bottom ones, which would be a shape nobody
chose. +0.06 is deliberately modest: large enough to clear the noise band if
the mechanism works, small enough that a wrong direction is cheap to revert.

WHAT IT IS EXPECTED TO DO, so the check is falsifiable rather than a hunt for
any movement: a more aggressive patron busts more often, and a rival that
sometimes throws away a turn gives a skilled player room a metronome does not.
If spread does NOT widen, the mechanism is wrong and the number is not the fix.
"""
import io, os, re

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   'fark_proto.html')
with io.open(SRC, encoding='utf-8') as f:
    s = f.read()
orig = s

BUMP, CAP = 0.06, 0.95
pat = re.compile(r'aggMin:(\.\d+),aggMax:(\.\d+)')
found = pat.findall(s)
assert len(found) == 8, 'expected 8 tier bands, found %d' % len(found)

def raise_band(m):
    lo, hi = float(m.group(1)), float(m.group(2))
    lo2, hi2 = min(CAP, round(lo + BUMP, 2)), min(CAP, round(hi + BUMP, 2))
    return 'aggMin:%s,aggMax:%s' % (repr(lo2).lstrip('0'), repr(hi2).lstrip('0'))

s = pat.sub(raise_band, s)
assert s != orig, 'nothing changed'
after = pat.findall(s)
assert len(after) == 8, 'band count changed'
for (a, b), (c, d) in zip(found, after):
    assert float(c) >= float(a) and float(d) >= float(b), 'a band went down'
    assert float(c) <= CAP and float(d) <= CAP, 'a band passed the cap'
print('P460: 8 aggression bands raised by %.2f (cap %.2f)' % (BUMP, CAP))
for (a, b), (c, d) in zip(found, after):
    print('   %s-%s -> %s-%s' % (a, b, c, d))
with io.open(SRC, 'w', encoding='utf-8', newline='') as f:
    f.write(s)
