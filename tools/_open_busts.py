# -*- coding: utf-8 -*-
u"""Replace the bustsPerMatch loose-thread note in docs/OPEN.md: it is found,
fixed and measured, and my description of it was wrong in a way worth stating.

Offset-based: OPEN.md has MIXED line endings, CRLF for the first four lines and
LF after, so splitting on either corrupts it.
"""
import io, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'docs', 'OPEN.md')
s = io.open(P, encoding='utf-8', newline='').read()

HEAD = u'**One loose thread found in passing'
i = s.find(HEAD)
if i < 0:
    sys.exit('the bustsPerMatch note is not there (nothing written)')
end = s.find(u'\n---', i)
if end < 0:
    sys.exit('no closing rule after the note (nothing written)')

NEW = u"""**The flat `bustsPerMatch` is found, fixed and measured (P888) — and it was
not a metric bug.** `simTurn` gave a free bust save to any loadout containing a
silver die: a per-turn counter, spent by returning `bank()` instead of
`bust()`, and a turn reaches that check at most once. So **one silver die was
100% bust immunity every turn for the whole run**, on the rival's seat as well
as yours, and it did not even need to still be in hand.

Silver's own definition says the save was retired — *"the old bust-save is
gone… it never removes the zero"* — and its `effect` is `null`. It pays through
its weighted roll table, which the sim already gets for free, so the line was
counting a retired mechanic twice.

Measured, 100 tier-0 matches, one bone swapped for one silver: 91 busts with
bone, **zero** with silver and 84 saves consumed, 80 with a clone of silver's
roll table under a different id. After the fix: bone 0.78, silver 0.62, clone
0.58. The persona path went from exactly 0.000 on all six personas to
0.13–0.247.

**This is a balance-measurement defect, not a display one.** Every `patronWin`
and `bossWin` ever produced for a silver-bearing loadout is inflated — at tier
0, patronWin ran 18% / 24% / 22% across none / silver / clone, so about half of
silver's apparent gain was the retired save. It lands before the ladder re-run,
alongside the sim's `G` isolation.

**Correction to what I told you.** I said every row read `bustsPerMatch: 0`. It
did not — it was zero exactly when the gear contained silver, which is G2-mid
and G3-late, half the default table, and normal for G0-bone and G1-early. The
rows I was looking at came through callers that pin a silver-bearing gear, so I
generalised from a filtered view.
"""

io.open(P, 'w', encoding='utf-8', newline='').write(s[:i] + NEW + s[end:])
print('OPEN.md: bustsPerMatch note replaced with the resolution')
