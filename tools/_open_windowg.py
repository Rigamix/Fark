# -*- coding: utf-8 -*-
u"""Add the window.G finding to docs/OPEN.md, at the top where new items go.

OFFSET INSERT, not a line split. docs/OPEN.md has MIXED line endings - the
first four lines are CRLF and the rest is LF - so splitting on either one
leaves embedded terminators in the "lines" and matches nothing, which is what
happened on the first two attempts. Finding one offset and inserting at it
leaves every other byte in the file exactly as it was, which also keeps every
other patch's anchors valid.
"""
import io, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'docs', 'OPEN.md')
s = io.open(P, encoding='utf-8', newline='').read()

if u'window.G` IS UNDEFINED' in s:
    sys.exit('the entry is already there (nothing written)')

# the rule that closes the header block, in the LF region
MARK = u'\n---\n'
i = s.find(MARK)
if i < 0 or i > 400:
    sys.exit('header rule not found near the top (nothing written)')
cut = i + len(MARK)

ENTRY = u"""
## `window.G` IS UNDEFINED — THREE LIVE SITES STILL READ IT

`G` is declared `let G=null,LO=null;` (30882). A `let` at top level makes a
global BINDING, never a property of `window`, so **`window.G` is undefined for
the life of the page** and any guard beginning `window.G&&` is dead.

The file already knows: 31018 carries the note verbatim, earned when the same
mistake silently no-opped a whole migration. I walked into it anyway building
moment 2 — the beat was unreachable until P884c — which is how I found the rest.

**Three more sites read it, and all three are yours, because each is a
behaviour change rather than a typo.** I have not touched them.

**1. `12561` — a pressure ratio that is permanently 1.**
`if(window.G&&G.target&&G.pPts){var p=G.pPts/G.target; r=p>=0.95?1.5:...}`
The guard never passes, so `r` never leaves 1 and the 1.15 / 1.3 / 1.5 steps
have never fired. Whatever this scales has never scaled near target.
*Recommendation: fix, but look at what `r` feeds first — fixing it makes
something stronger in the last stretch of a night, and that is a difficulty
change you should see coming rather than discover.*

**2. `46902` — a function that has never run.**
`if(!(window.G&&G._oppTurnActive))return;` always returns early.
*Recommendation: read what follows the guard before fixing it. An
always-returning guard can be load-bearing by accident, and turning on a path
that has never executed in play is not a one-line change.*

**3. `46654` / `46877` — a sim isolation that does not isolate.**
`var _savedG=window.G; window.G=null;` around the sim, restored after, with the
stated intent that `oppShouldBank` be neutral during it. It writes a window
property nothing reads, so the live `G` is visible to the sim throughout.
*Recommendation: fix. The intent is written down, the sim is meant to be
isolated, and this is the one of the three where the current behaviour is
clearly not what anybody chose.*

**The general form, if you want one guard rather than three fixes:** anything
matching `window.G&&` in this file is dead by construction. That is a
grep-able invariant and it could be a line in the parse gate.

---
"""

io.open(P, 'w', encoding='utf-8', newline='').write(s[:cut] + ENTRY + s[cut:])
print('OPEN.md: window.G entry inserted at offset %d' % cut)
