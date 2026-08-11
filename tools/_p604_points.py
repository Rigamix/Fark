# -*- coding: utf-8 -*-
"""P604: the Cursed Table card says what it means, and chalk circles become points.

Denis: "the cursed table card description/tooltip is very obscured. A patron that
has smoke around their portrait is CURSED, that's the term for it. and we don't
win circles anymore, call them points."

THE OLD LINE NEVER SAID THE WORD. "Beat the patron the smoke clings to" describes
the art and leaves the player to infer the term; CURSED is the name of the state,
and the card is the place it should be learned. The rewrite leads with the
definition, then the effect.

WRITTEN AS A SCRIPT, NOT A HEREDOC, because every one of these strings carries a
literal \\u2014 and the project rule - already recorded after it bit once - is
that backslash patches go through a Python file where the escaping is explicit.
Doing it in a bash heredoc is exactly what failed a moment ago.

EVERY ANCHOR IS ASSERTED UNIQUE. A silent zero-match here would rewrite nothing
and read as success.
"""
import io, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'fark_proto.html')
s = io.open(P, encoding='utf-8', newline='').read()

SUBS = [
    # ── the card Denis named ──
    (u"'Beat the patron the smoke clings to and the board chalks you THREE "
     u"circles, not two \\u2014 lose, and it costs you two circles, not one.'",
     u"'A CURSED patron has smoke around their portrait. Beat one and you take "
     u"THREE points instead of two \\u2014 lose to one and it costs two, not one.'"),

    # ── "circles" retired from every other player-facing string ──
    (u"or it costs a chalk circle.'",
     u"or it costs a point.'"),
    (u"bust before banking, and it costs an extra circle.'",
     u"bust before banking, and it costs an extra point.'"),
    (u"+' circles / lose '+",
     u"+' points / lose '+"),
    # anchored on what precedes it, to keep the middot out of the pattern
    (u"t.pointsNeeded+' circles ",
     u"t.pointsNeeded+' points "),
    (u"bust first and a circle goes</div>'",
     u"bust first and a point goes</div>'"),
]

for old, new in SUBS:
    n = s.count(old)
    if n != 1:
        sys.exit('ANCHOR MATCHED %d TIMES (need exactly 1): %r' % (n, old[:70]))
    s = s.replace(old, new)

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('P604: %d strings rewritten' % len(SUBS))
