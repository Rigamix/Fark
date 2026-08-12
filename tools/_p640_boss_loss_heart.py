# -*- coding: utf-8 -*-
"""P640: the boss loss keeps its heart. P637 hid it, and only the boss arm showed that.

P637 copied the win screen's suppression list without checking that the two
screens keep different things in the same element. On a win, .res-gold-wrap
holds coins whose job the painted board takes over, so hiding it is right. On a
LOSS the same wrapper holds THE HEART - a boss defeat costs a life, and
`.as-heart` swaps that coin's face for a heart and then a broken one as it
drains. Hiding the wrapper deleted the only thing on screen that says a life
was lost.

CAUGHT BY THE SECOND ARM, not by the first. The patron render looked finished
and correct; the boss render reported goldWrapVisible:false with a sign reading
-120g and no heart anywhere. A one-arm probe would have shipped this.

THE PATRON LOSS IS UNAFFECTED BY UN-HIDING IT. P637 deleted the only code that
showed the wrapper on a patron loss - that block existed purely to print the
red -Xg, and set the coin to display:none while doing it - so the wrapper stays
at its default opacity:0 there. Only the boss branch calls fade-in on it now.

PLACED UNDER THE SIGN rather than at its own top:35%, which is across the hands.
The order below the painting reads: the sign says what it cost in coin, the
heart says what it cost in lives, then the rival speaks. #resDlg moves down to
make room, which is the same rule P639 already moved once for the same reason.
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


sub(u"/* what the painting replaces - the same list the win screen suppresses */\n"
    u"#end-ov.loss-art-on .res-scores,\n"
    u"#end-ov.loss-art-on .res-gold-wrap{display:none!important}",
    u"/* what the painting replaces. NOT the same list as the win's, and P640 is the\n"
    u"   correction: .res-gold-wrap holds COINS on a win and THE HEART on a boss\n"
    u"   loss, so hiding it there deleted the only thing saying a life was spent.\n"
    u"   The scores go, because the banner and the sign say it. */\n"
    u"#end-ov.loss-art-on .res-scores{display:none!important}\n"
    u"/* UNDER THE SIGN, not at its own top:35% which is across the hands. The\n"
    u"   painting reads down: what it cost in coin, what it cost in lives, then the\n"
    u"   rival's line. On a patron loss nothing shows this wrapper at all - P637\n"
    u"   deleted the block that did, and it existed only to print the red caption\n"
    u"   the sign now carries - so this rule is the boss loss's alone in practice. */\n"
    u"#end-ov.loss-art-on .res-gold-wrap{top:66%!important}\n"
    u"#end-ov.loss-art-on .res-coin-big{width:62px;height:62px}",
    'P640 keep the heart, place it under the sign')

sub(u"/* CLEAR OF THE SIGN. #resDlg's own top is calc(38% + 200px), which put it\n"
    u"   under the hanging board's lower edge at 65%. */\n"
    u"#end-ov.loss-art-on #resDlg{top:67%!important}",
    u"/* CLEAR OF THE SIGN, AND NOW OF THE HEART TOO. #resDlg's own top is\n"
    u"   calc(38% + 200px), which put it under the hanging board's lower edge at\n"
    u"   65%; P640 moved the boss loss's heart into the gap that opened, so the\n"
    u"   rival speaks below both. */\n"
    u"#end-ov.loss-art-on #resDlg{top:78%!important}",
    'P640 make room for it')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('\n%d edits' % n)
