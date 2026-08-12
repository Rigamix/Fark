# -*- coding: utf-8 -*-
"""P643: two mistakes in P641, both caught by photographing it.

1. THE SLOTS MOVED ANYWAY. Denis asked for the offer higher and the slots left
   alone, so P641 lifted .res-card by 5% and gave .fo-deck `padding-top:5%` back.
   That does not compensate: a PERCENTAGE PADDING RESOLVES AGAINST THE
   CONTAINING BLOCK'S WIDTH, not its height. .res-card is 80% of a 430px screen,
   so 5% bought 17px against a 44.5px move, and the slots came up 27px with the
   cards. In vh it is exact - #end-ov is fixed inset:0, so 1vh is one per cent of
   the overlay's own height, the same unit the move was made in.

2. THE LOSS BUTTON WRAPPED. "BACK TO THE ROOM" on a plate sized min-width:160px
   broke to two lines and sat badly on the art. It takes .fo-skip's 82% width, so
   the two screens' buttons are now the same plate at the same size as well as in
   the same place.

AND THE TWO BUTTONS ARE MEASURED AGAINST EACH OTHER, not eyeballed - Denis:
"those buttons should match position on the win, loss screens ideally". The loss
button is absolutely anchored 28px off the safe area; the win's SKIP flows at the
end of the offer. Rather than convert one layout into the other, the win's is
given the same anchor, which makes the match structural instead of a number that
holds until the offer's contents change.
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
        sys.exit('ANCHOR x%d (need 1) for %s:\n  %r' % (c, label, old[:130]))
    s = s.replace(old, new)
    n += 1
    print('  ok  %s' % label)


sub(u"#end-ov.win-art-on .fo-deck{padding-top:calc(6px + 5%)}",
    u"/* P643: vh, NOT %. A percentage padding resolves against the containing\n"
    u"   block's WIDTH - .res-card is 80% of 430px, so 5% bought 17px against a\n"
    u"   44.5px move and the slots came up with the cards anyway. #end-ov is fixed\n"
    u"   inset:0, so 1vh is one per cent of the overlay's height: the same unit the\n"
    u"   52%->47% move was made in, and therefore an exact cancellation. */\n"
    u"#end-ov.win-art-on .fo-deck{padding-top:calc(6px + 5vh)}",
    'P643 compensate the slots in the right unit')

sub(u"/* P641: LOWER AND LARGER, and anchored the same way #btnContinue is so the\n"
    u"   two screens' primary buttons land in the same place by construction rather\n"
    u"   than by tuning two different layout systems against each other. */\n"
    u".fo-skip{display:flex;align-items:center;justify-content:center;gap:.4em;\n"
    u"  cursor:pointer;margin:8px auto 0;width:82%;min-height:2.9em;padding:.55em 1em;",
    u"/* P641/P643: LOWER AND LARGER, and anchored the way #btnContinue is - 28px\n"
    u"   off the safe area - so the win and loss screens' primary buttons land in\n"
    u"   the same place BY CONSTRUCTION. Tuning a flowed button against an absolute\n"
    u"   one holds only until the offer above it changes height, which it does: the\n"
    u"   deck below the cards is three slots or three cards. */\n"
    u".fo-skip{display:flex;align-items:center;justify-content:center;gap:.4em;\n"
    u"  cursor:pointer;width:82%;min-height:2.9em;padding:.55em 1em;\n"
    u"  position:fixed;left:50%;transform:translateX(-50%);\n"
    u"  bottom:calc(28px + env(safe-area-inset-bottom,0px));z-index:6;",
    'P643 anchor the skip button like the loss button')

sub(u".fo-skip:active{transform:translateY(1px)}",
    u".fo-skip:active{transform:translateX(-50%) translateY(1px)}",
    'P643 keep the press offset from undoing the centring')

sub(u"  font-family:var(--font-ui);font-size:18px;letter-spacing:2px;\n"
    u"  color:var(--gold);background:none;border:none;\n"
    u"  padding:14px 48px;min-width:160px;\n"
    u"  overflow:hidden;border-radius:6px;",
    u"  font-family:var(--font-ui);font-size:18px;letter-spacing:2px;\n"
    u"  color:var(--gold);background:none;border:none;\n"
    u"  /* P643: .fo-skip's width, because \"BACK TO THE ROOM\" wrapped to two lines\n"
    u"     on a 160px plate and sat badly on the art. Same plate, same size, same\n"
    u"     place as the win screen's. */\n"
    u"  padding:.55em 1em;width:82%;justify-content:center;white-space:nowrap;\n"
    u"  overflow:visible;border-radius:6px;",
    'P643 the loss button stops wrapping')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('\n%d edits' % n)
