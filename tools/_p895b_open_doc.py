# -*- coding: utf-8 -*-
u"""P895b: two things for OPEN.md - the ladder cell that came back empty, and
the classes step 8 has just made inert.

OPEN.md is CRLF for its first four lines and LF after, so the sub() helper's
per-match line-ending detection is doing real work here, not being defensive.
"""
import io, os, sys, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'docs', 'OPEN.md')
s = io.open(P, encoding='utf-8', newline='').read()


def sub(old, new, label):
    global s
    pat = re.escape(old).replace('\\\n', '\n').replace('\n', '\\r?\n')
    ms = list(re.finditer(pat, s))
    if len(ms) != 1:
        sys.exit('ANCHOR x%d for %s (nothing written)' % (len(ms), label))
    m = ms[0]
    rep = new.replace('\n', '\r\n') if '\r\n' in m.group(0) else new
    s = s[:m.start()] + rep + s[m.end():]


NEW = u"""## THE LADDER RE-RUN IS STILL UNMEASURED, and the instrument was why

Band 2 ran for **two and a half hours across both seats and returned nothing** —
no result, no error, no screenshot, only the headers the shell echoed around it.

`shoot.js`'s `connect()` had handlers for `message`, `error` and `open` and none
for `close`. A dropped debug connection therefore left every pending call
unsettled, node's event loop emptied, and the process exited **0** having
printed nothing. A dead run and a good one were byte-for-byte the same in the
output. Reproduced deliberately — killing the browser mid-eval used to give an
empty log and rc 0, and now gives `FAILED: the browser closed the debug
connection mid-run` and rc 1 (P894).

Worse than the silence: the per-match lines only ever reached disk inside the
final result, so there is no way to know whether that cell died at match 20 or
match 129. 8981s ÷ 130 = 69s a match sits inside the measured 43–139s range, so
both stories fit what is on disk.

**Rebuilt as batches** — ~15 matches per invocation, each landing in about
twenty minutes, a per-invocation minute budget so a slot always returns what it
has, and three consecutive failed batches abandons a cell while keeping what is
banked. Traced against a stub before launching.

**Nothing is running.** You asked for everything stopped and it is: 0 shoot
processes, 0 browsers. The question this was going to answer is unchanged and
still the biggest one open — *if band 2 comes back near 0.44 the 4.6–10%
run-win projection stands and it is a real difficulty finding; near 0.62 and the
balance sim and the real engine disagree, and that is the finding.* Six hours of
wall-clock at two concurrent, whenever you want it started.

---

## Nine classes are now inert, and it is one decision, not nine — YOURS

Step 8 deleted thirteen CSS rules (P895). Four were painting nothing at all, so
nobody loses anything. The other nine were painting an **axis-aligned box
around a cube** — every one sat after `.die.d3on{box-shadow:none!important}` at
equal specificity, so every one won.

Three of those nine are now covered properly: frozen and dampened are CRUST
rows, blind is a VEIL, all measured in their own inks and surviving a roll,
which the old global `_rolling()` skip could not express.

**The other six were beats, and the JS still adds and removes their classes:**
`combo-glow`, `card-reroll`, `crr-blue`, `card-reroll-settle`, and the four
`eff-glow-*`. They are no-ops now. They are not silent — every `eff-glow` site
also calls `spawnPixelSparks`, which goes through `FX.emit`, the one pipeline
that always worked on a match die — but the die-local part of them is gone.

*Recommendation: route them through `_fxMark`, which already exists and already
paints transient beats on the state canvas, rather than deleting the call
sites.* That keeps the combo pulse and the reroll shimmer as light on the
silhouette instead of a square behind it, and P828's point survives the move —
encore is starstone blue against powder keg's gold, and the modifier has to
swap the whole thing, not just a static colour. It is about six one-line
changes. **Say the word and it goes in; I have not done it because it is a
decision about feel, not a mechanical follow-on to a deletion.**

*(Two small things found while doing it, neither needing an answer: `.die
.die-frozen-mark` and `.die.die-frozen-entry` are dead CSS with no
`classList.add` anywhere — §9's inventory missed them — and the first would
paint a box on a selected die if anything ever added it. Left in place, since
the brief did not list them.)*

---

"""

sub(u"""## `window.G` — ALL THREE FIXED (P886). One residual, and it is a real question.""",
    NEW + u"""## `window.G` — ALL THREE FIXED (P886). One residual, and it is a real question.""",
    'the two new entries')

if s.count('THE LADDER RE-RUN IS STILL UNMEASURED') != 1:
    sys.exit('the ladder entry is not present exactly once (nothing written)')
if s.count('Nine classes are now inert') != 1:
    sys.exit('the inert-classes entry is not present exactly once (nothing written)')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: docs/OPEN.md updated')
