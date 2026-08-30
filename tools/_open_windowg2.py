# -*- coding: utf-8 -*-
u"""Replace the window.G entry in docs/OPEN.md: all three are fixed (P886), and
what is left is one thing I deliberately did not change.

Offset-based, because OPEN.md has MIXED line endings - CRLF for the first four
lines and LF after - so splitting on either corrupts it.
"""
import io, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'docs', 'OPEN.md')
s = io.open(P, encoding='utf-8', newline='').read()

HEAD = u'## `window.G` IS UNDEFINED'
i = s.find(HEAD)
if i < 0:
    sys.exit('the window.G entry is not there (nothing written)')
# the entry ends at its own closing rule
end = s.find(u'\n---', i)
if end < 0:
    sys.exit('no closing rule for the entry (nothing written)')
end += len(u'\n---')

NEW = u"""## `window.G` — ALL THREE FIXED (P886). One residual, and it is a real question.

`G` is a `let`, so `window.G` was undefined for the life of the page and every
`window.G&&` guard was dead. All three are now on the binding, driven 18/18:

- **The bank sound pitches again.** Measured 520/660/900 at 20% of target,
  598/759/1035 at 70%, 676/858/1170+**1287** at 88%, 780/990/1350+**1485** at
  98%. The hot harmonic had never played.
- **Tap-to-fast-forward works.** A real pointerdown on the board takes
  `_ffMult` 1 → 0.15 and `_oppDelay(1900)` from 1900ms to 285ms; off the board,
  on a button, and outside a rival turn all correctly do nothing.
- **The sim really isolates `oppShouldBank` now.** 10,733 calls during a sim,
  not one of which saw a live `G` or an active sealed rule, and a forced throw
  still restores the binding through the `finally`. **Safe for the ladder
  re-run.**

**THE RESIDUAL — yours, because it is a judgement about feel, not a bug.**
With the tap live, `_afterOppSettle`'s `MIN = _oppDelay(260)` drops from 260ms
to **40ms**. That window exists to cover the 3D layer picking the dice up. It is
a pre-existing shape — the shipped `fastRival` setting already takes it to
104ms — and I could not time it honestly on a ~1fps harness, so I changed
nothing and am telling you instead of guessing. If a fast-forwarded rival turn
ever looks like it skips a beat rather than running fast, this is the line:
flooring it (`Math.max(160, _oppDelay(260))`) keeps the pickup window while
still accelerating everything else. *Recommendation: ship as-is and watch for
it; the floor is a one-line change if you see it.*

**One loose thread found in passing, unrelated to `window.G`:** every balance-sim
row reports `bustsPerMatch: 0`, identical across every tier, policy and repeat.
A player policy pushing to a 500 threshold with four dice left should bust
sometimes. A flat zero on a stochastic counter is the shape of a metric that is
never incremented — worth a look at `playMatch`'s bust accumulation before the
ladder numbers are trusted.

---"""

io.open(P, 'w', encoding='utf-8', newline='').write(s[:i] + NEW + s[end:])
print('OPEN.md: window.G entry replaced with the fixed status + residual')
