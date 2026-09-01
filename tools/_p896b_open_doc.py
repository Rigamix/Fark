# -*- coding: utf-8 -*-
u"""P896b: the inert-classes question is answered, so it is deleted rather than
marked - OPEN.md's own rule. One residual replaces it, and it is a real
question rather than a status line.

THE RESIDUAL. A beat's RIM paints on the OVER canvas, because that is where
P883 put the beat painter and its argument was good: a transient should read on
top of the state it belongs to. §13's table says RIM goes UNDER. Both cannot be
right, and the reason it has gone unnoticed is that _paintHalo punches its
subject out, so a rim is a ring by construction and looks identical on either
surface EXCEPT where two dice overlap.
"""
import io, os, sys, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'docs', 'OPEN.md')
s = io.open(P, encoding='utf-8', newline='').read()

start = s.find(u'## Nine classes are now inert')
if start < 0:
    sys.exit('the inert-classes entry is not there (nothing written)')
end = s.find(u'## `window.G`', start)
if end < 0:
    sys.exit('could not find the entry after it (nothing written)')

NEW = u"""## Which canvas does a beat's RIM belong on? — YOURS, and it is one line

The eight inert classes are routed (P896, 18 call sites). Doing it surfaced a
disagreement between two good arguments that has been sitting there since P883.

**§13 says RIM goes UNDER the dice.** P883 put the beat painter OVER them, and
its reason is sound: *"beats last, so a transient reads ON TOP of the state it
belongs to rather than under it."* A beat's rim is currently over.

**It has gone unnoticed because it almost never shows.** `_paintHalo` punches
its subject out of its own glow, so a rim is a ring by construction and looks
identical on either surface — the only case that differs is **two dice
overlapping**, where an over-rim draws across its neighbour and an under-rim
goes behind it.

*Recommendation: leave beats over.* A beat is a moment and should not be
occluded by the thing it is about; a state is a property of the die and should
sit behind it. That makes "the form decides the canvas" a rule about states,
with lifetime deciding it for beats — which is one extra sentence in §13 rather
than an exception. **The alternative is a one-word change** (`'over'` to
`'under'` in the beat painter's canvas), so this is cheap either way and I have
not guessed.

---

"""

s = s[:start] + NEW + s[end:]

if s.count('Nine classes are now inert'):
    sys.exit('the answered entry survived (nothing written)')
if s.count('Which canvas does a beat') != 1:
    sys.exit('the residual is not present exactly once (nothing written)')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: the answered entry is out, the residual is in')
