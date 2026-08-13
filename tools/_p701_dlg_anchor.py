# -*- coding: utf-8 -*-
"""P701: the dialogue bubble stops moving. At all.

Denis (third time): "Dialogue box still shifts up and down depending on
what's on screen rather than being over everything and not be nudged."

Driven to the movers:
 1. #dlgBox lived INSIDE #diceArea. The bust shake animates a transform on
    #diceArea, and a transform makes an ancestor the containing block for
    fixed descendants - so for the whole 0.4s the bubble's top resolved from
    #diceArea's own top (which depends on everything rendered above it), then
    snapped back. The codebase documents this exact mechanism for #tellBadge
    (~12905) and moved the badge out; the bubble never followed. Now it does:
    a direct child of #screen-match, nothing left to hijack it.
 2. The box is height:0 and the bubble centred on it - so its top edge moved
    with its OWN line count, one line-height per message. A fixed-height
    .dlg-inner centres 1-line and 3-line bubbles on the same line; --dlg-y
    drops 25cqw -> 13cqw so the bubble's centre stays exactly where it was
    (13 + half of 24 = 25).
 3. z-index 90 -> 9500 in-match: over the focus (9000/9001), over the dice,
    under the end-of-match overlay (same 9500, later in DOM). 'Over
    everything and not be nudged.'
position:fixed -> absolute: #screen-match's container-type already made it
the de-facto containing block; absolute says so honestly and matches the
badge pattern.
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
        sys.exit('ANCHOR x%d (need 1) for %s' % (c, label))
    s = s.replace(old, new)
    n += 1
    print('  ok  %s' % label)


# 1) out of #diceArea...
sub(u"  <!-- Dialogue box -->\n"
    u"  <div class=\"dlg-box\" id=\"dlgBox\">\n"
    u"    <div class=\"dlg-inner\">\n"
    u"      <div class=\"dlg-portrait\" id=\"dlgPortrait\">\n"
    u"        <img id=\"dlgImg\" src=\"\" alt=\"\">\n"
    u"      </div>\n"
    u"      <div class=\"dlg-scroll\" id=\"dlgScroll\">\n"
    u"        <canvas id=\"dlgCanvas\"></canvas>\n"
    u"        <div class=\"dlg-text\" id=\"dlgText\">\"Welcome to the table, stranger.\"</div>\n"
    u"      </div>\n"
    u"    </div>\n"
    u"  </div>\n"
    u"\n"
    u"  <div class=\"dice-spacer\" style=\"flex:var(--sp-before,3)\"></div>",
    u"  <!-- P701: the dialogue box moved OUT of this container - see it below,\n"
    u"       a direct child of #screen-match, out of the bust shake's reach. -->\n"
    u"  <div class=\"dice-spacer\" style=\"flex:var(--sp-before,3)\"></div>",
    'P701 bubble leaves #diceArea')

# 2) ...and in as a direct child of #screen-match
sub(u"  <div class=\"dice-spacer\" style=\"flex:var(--sp-after,0)\"></div>\n"
    u"</div>\n"
    u"\n"
    u"<!-- PLAYER CARD BAR (fanned, tucked under controls) -->",
    u"  <div class=\"dice-spacer\" style=\"flex:var(--sp-after,0)\"></div>\n"
    u"</div>\n"
    u"\n"
    u"<!-- Dialogue box - P701: a DIRECT child of #screen-match, the #tellBadge\n"
    u"     fix (~12905) applied to the bubble at last. The bust shake's transform\n"
    u"     on #diceArea made #diceArea the containing block for this box, so the\n"
    u"     bubble jumped by #diceArea's screen offset - an offset that varies\n"
    u"     with whatever renders above the dice - and #diceArea's\n"
    u"     overflow:hidden clipped it mid-shake. No ancestor, no hijack. -->\n"
    u"<div class=\"dlg-box\" id=\"dlgBox\">\n"
    u"  <div class=\"dlg-inner\">\n"
    u"    <div class=\"dlg-portrait\" id=\"dlgPortrait\">\n"
    u"      <img id=\"dlgImg\" src=\"\" alt=\"\">\n"
    u"    </div>\n"
    u"    <div class=\"dlg-scroll\" id=\"dlgScroll\">\n"
    u"      <canvas id=\"dlgCanvas\"></canvas>\n"
    u"      <div class=\"dlg-text\" id=\"dlgText\">\"Welcome to the table, stranger.\"</div>\n"
    u"    </div>\n"
    u"  </div>\n"
    u"</div>\n"
    u"\n"
    u"<!-- PLAYER CARD BAR (fanned, tucked under controls) -->",
    'P701 bubble mounts at the match root')

# 3) fixed -> absolute
sub(u".dlg-box{\n"
    u"  position:fixed;",
    u".dlg-box{\n"
    u"  /* P701: absolute, not fixed - #screen-match's container-type already\n"
    u"     made it the containing block; this says so honestly (the badge\n"
    u"     pattern), and no ancestor transform can re-anchor it now. */\n"
    u"  position:absolute;",
    'P701 absolute in the match root')

# 4) over everything + a stable centre line
sub(u"#screen-match .dlg-box{--dlg-y:25cqw}",
    u"/* P701: 13 + half the fixed 24cqw inner = the old 25cqw centre, so the\n"
    u"   bubble sits exactly where it did - it just stops moving. z 9500: over\n"
    u"   the card focus (9000/9001) and the dice; the end overlay (same 9500,\n"
    u"   later in DOM) still covers it. */\n"
    u"#screen-match .dlg-box{--dlg-y:13cqw;z-index:9500}\n"
    u"/* the anchor is the BOX, not the text's own midpoint: with a fixed-height\n"
    u"   inner, a one-liner and a three-liner centre on the same line instead of\n"
    u"   raising the top edge a line-height per message */\n"
    u"#screen-match .dlg-inner{height:24cqw}",
    'P701 z + stable centre')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('\n%d edits' % n)
