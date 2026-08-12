# -*- coding: utf-8 -*-
"""P646: the deck slots arch and stop touching, the title centres, the tier stops
being printed twice, and the shelf row comes back down.

── THE SLOTS OVERLAPPED, AND THE NUMBERS SAY WHY ──
Denis: "still have some overlap on the card slots and more arch."

Measured rather than nudged. Each slot is 19% of a 344px column = 65.4 x 93.2px
with a 1.5% (5.2px) gap. A rectangle rotated by theta grows its bounding box by
(h*sin + w*cos - w)/2 per side; at the 4 degrees P641 used that is 3.17px from
each of two neighbours = 6.3px of encroachment into a 5.2px gap. So they were
overlapping by about a pixel - visible in the render as touching corners.

More arch makes that worse, so both numbers move together:
  angle   4deg -> 8deg, which needs 6.16px of clearance per side
  gap     1.5% -> 4%   (5.2px -> 13.8px), comfortably past it
  arch    5px of differential -> 14px (outer +8px, middle -6px), which is the
          part that actually reads as a curve rather than a tilt
Three slots at 19% with 4% gaps is 65% of the column, so there is room.

── "PICK A CARD" WAS LEFT-ALIGNED ──
.fo-wrap carries an inline `text-align:left` for the monospace debug text it was
built around, and the title inherited it. Centred on the title itself rather
than by removing the wrapper's alignment, because the deck and offer rows below
are grids and flex rows that do their own centring - changing the wrapper would
be a wider change with nothing to gain.

── THE TIER WAS PRINTED TWICE ──
Denis: "You can remove the card level next to their names as it shows on the
card itself with the tag." famCardHtml passes tierAlways:true to famCardArt,
which draws the numeral badge on the card, and THEN repeats it in the caption.
The caption's copy goes. The badge is the one that sits on the art, which is
what he is pointing at.
Two callers, both correct to change: the win offer and the debug card panel.

── THE SHELF WENT TOO FAR ──
"cards are too high on shelf screen now." 71.5 was crowding the dice, 69.5
overshot; 70.5 is the half of it. One constant, so the tilt's pivot follows.
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


# ── 1. the arch, and the room it needs ───────────────────────────────────
sub(u".fo-slot+.fo-slot{margin-left:1.5%}\n"
    u".fo-slot:first-child{transform:rotate(-4deg) translateY(2px)}\n"
    u".fo-slot:nth-child(2){transform:translateY(-3px);z-index:2}\n"
    u".fo-slot:last-child{transform:rotate(4deg) translateY(2px)}",
    u"/* P646: ARCHED, AND NO LONGER TOUCHING. A slot is 19% of a 344px column =\n"
    u"   65.4 x 93.2px. Rotating by theta grows its bounding box by\n"
    u"   (h*sin + w*cos - w)/2 per side, so the old 4deg took 3.17px from each of\n"
    u"   two neighbours - 6.3px of encroachment into a 5.2px gap, which is the\n"
    u"   overlap Denis is looking at. 8deg needs 6.16px per side; 4% is 13.8px.\n"
    u"   The arch is the 14px of vertical differential (was 5px) - that is the part\n"
    u"   that reads as a curve rather than as three tilted rectangles. */\n"
    u".fo-slot+.fo-slot{margin-left:4%}\n"
    u".fo-slot:first-child{transform:rotate(-8deg) translateY(8px)}\n"
    u".fo-slot:nth-child(2){transform:translateY(-6px);z-index:2}\n"
    u".fo-slot:last-child{transform:rotate(8deg) translateY(8px)}",
    'P646 the slots arch and clear each other')

# ── 2. the title centres ─────────────────────────────────────────────────
sub(u".fo-title{font-family:'JMH Beda',serif;font-size:clamp(15px,4.4vw,22px);\n"
    u"  letter-spacing:.06em;color:#e8d7a8;margin-bottom:6px;\n"
    u"  text-shadow:0 2px 3px rgba(0,0,0,.65)}",
    u"/* P646: centred. .fo-wrap carries an inline text-align:left left over from\n"
    u"   the monospace block this was built out of, and the title inherited it.\n"
    u"   Set here rather than on the wrapper: the rows below are a grid and a flex\n"
    u"   row that already centre themselves, so changing the wrapper would be a\n"
    u"   wider change with nothing to gain. */\n"
    u".fo-title{font-family:'JMH Beda',serif;font-size:clamp(15px,4.4vw,22px);\n"
    u"  letter-spacing:.06em;color:#e8d7a8;margin-bottom:6px;text-align:center;\n"
    u"  text-shadow:0 2px 3px rgba(0,0,0,.65)}",
    'P646 centre the title')

# ── 3. the tier stops being printed twice ────────────────────────────────
sub(u"  var cap='<div style=\"margin-top:4px;text-align:center;font-family:\\'JMH Beda\\',serif;letter-spacing:.05em\">'\n"
    u"    +'<div style=\"font-size:12px;color:#f0e3c6\">'+d.name.toUpperCase()\n"
    u"    +(d.fam==='tavern'?'':' <span style=\"color:'+col+'\">'+['I','II','III'][tier-1]+'</span>')+'</div>'\n"
    u"    +'</div>';",
    u"  /* P646: THE NAME ONLY. famCardArt already draws the tier as a numeral badge\n"
    u"     on the card itself (tierAlways:true, below), so the caption was printing\n"
    u"     it a second time an inch away. Denis: \"remove the card level next to\n"
    u"     their names as it shows on the card itself with the tag\". */\n"
    u"  var cap='<div style=\"margin-top:4px;text-align:center;font-family:\\'JMH Beda\\',serif;letter-spacing:.05em\">'\n"
    u"    +'<div style=\"font-size:12px;color:#f0e3c6\">'+d.name.toUpperCase()+'</div>'\n"
    u"    +'</div>';",
    'P646 drop the duplicated tier from the caption')

# ── 4. the shelf row comes back down ─────────────────────────────────────
sub(u"     71.5 -> 69.5 per Denis: off the top of the dice. */\n"
    u"  var _LO_CARD_ROW_Y=69.5;",
    u"     71.5 crowded the dice, 69.5 overshot (\"cards are too high on shelf screen\n"
    u"     now\"), 70.5 is the half of it. */\n"
    u"  var _LO_CARD_ROW_Y=70.5;",
    'P646 the shelf row settles at 70.5')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('\n%d edits' % n)
