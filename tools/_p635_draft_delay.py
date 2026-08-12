# -*- coding: utf-8 -*-
"""P635: the win screen stops waiting for an animation that already finished.

Denis: "On the win screen the bottom UI takes a long time to appear but there
should be no reason. A card dotted line slot isn't heavy to render, or text. So
what gives?"

HE IS RIGHT THAT IT IS NOT RENDER COST. The whole lower half of the end screen
sits behind one hard-coded setTimeout - `_draftDelay` - whose comment calls it
"after animation sequence". Nothing is being computed during it. So the only
question is whether the animation sequence really lasts that long.

IT DOES NOT, and here is the sequence with every duration read from the rules
that declare it rather than guessed:
    100ms  title       resPop .6s                    -> ends  700
    500ms  scores      resFadeAbs .5s                -> ends 1000
    700ms  title+scores  transition top .6s          -> ends 1300
    900ms  gold wrap   resFadeAbs .5s                -> ends 1400
    900ms  coins       coinBigSpin .9s, +200ms each  -> ends 1800 (+stagger)
   1050ms  gold count  _tweenGold 600ms              -> ends 1650
   1600ms  coins       coinBounce .35s               -> ends 1950
   1600ms  coins       coinSheen .6s                 -> ends 2200
THE LAST THING THAT MOVES STOPS AT 2200ms. The bottom UI appears at 3200. That
is a full second sitting on a finished, motionless screen, which is exactly the
thing you feel and cannot name.

AND THE BOSS PATH ALREADY HAS IT RIGHT: 2400ms against the same 2200ms sequence
- one beat, then the offer. The patron path is 800ms longer than its own sibling
for no reason anywhere in the code. So this is not a new taste call; it is the
patron path adopting the number the boss path already uses.

Measured live too, not only read (tools/apv_win_screen_delay.js): draft card
shown at 3232ms, gold text reaching its final value at 2448ms.

THE LOSS PATH IS LEFT ALONE at 2800ms. Its sequence is different - coinDrain
.8s and coinDrainBurst .3s, on a timeline this has not measured - and shortening
it on the assumption that it matches the win would be exactly the guess this
patch is replacing.

THE NUMBERS ARE NAMED NOW. They were three literals inside a ternary; they are
the pacing of the most-looked-at screen in the game and Denis should be able to
find and turn them without reading endMatch.
"""
import io, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'fark_proto.html')
s = io.open(P, encoding='utf-8', newline='').read()
n = 0


def sub(old, new, label):
    global s, n
    c = s.count(old)
    if c != 1:
        sys.exit('ANCHOR x%d (need 1) for %s:\n  %r' % (c, label, old[:120]))
    s = s.replace(old, new)
    n += 1
    print('  ok  %s' % label)


sub(u"  /* Show draft (wins) or CONTINUE button (losses) after animation */\n"
    u"  var _draftDelay=win?(isBoss?2400:3200):2800;",
    u"  /* HOW LONG THE END SCREEN HOLDS ITS LOWER HALF BACK. Denis: \"the bottom UI\n"
    u"     takes a long time to appear but there should be no reason\".\n"
    u"     The reveal sequence is fully declarative and its last moving part is the\n"
    u"     coin sheen, coinSheen .6s starting at 1600ms - so EVERYTHING STOPS AT\n"
    u"     2200ms. Everything above it lands earlier: title 700, scores 1000, the\n"
    u"     lift 1300, gold wrap 1400, the count-up 1650, the coin bounce 1950.\n"
    u"     P635: the patron win was 3200, a full second of sitting on a finished\n"
    u"     screen, and the boss win beside it was already 2400 - one beat past the\n"
    u"     same sequence. Nothing in the code wanted the extra 800ms, so the patron\n"
    u"     path takes the number its sibling already uses.\n"
    u"     THE LOSS IS UNCHANGED. It animates coinDrain .8s + coinDrainBurst .3s on\n"
    u"     a timeline nothing here has measured, and assuming it matches the win is\n"
    u"     the guess this replaced.\n"
    u"     Named rather than left as literals in a ternary: this is the pacing of\n"
    u"     the most-looked-at screen in the game, and it should be findable. */\n"
    u"  var _DRAFT_DELAY={bossWin:2400,patronWin:2400,loss:2800};\n"
    u"  var _draftDelay=win?(isBoss?_DRAFT_DELAY.bossWin:_DRAFT_DELAY.patronWin):_DRAFT_DELAY.loss;",
    'P635 name the delays and cut the patron win to the boss win\'s')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('\n%d edits' % n)
