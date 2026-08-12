# -*- coding: utf-8 -*-
"""P638: the shelf draws its own card slots, so they cannot disagree with the cards.

Denis: "I've updated the shelf background image so there are no visual card
slots. Keep the cards placed where they should but just create the dotted lines
yourself, that way we ensure they match the card aspect ratio."

HE IS FIXING A REAL MISMATCH, not just moving work around. P636 measured the
painted slots at 89.3px wide on the 430px stage against a card authored at
92.5px - 3.6% out - which is why a gold hairline showed along the outer edge of
the left and right cards after they were laid onto the plane. A slot drawn from
the card's own box cannot be out by any amount.

DRAWN INSIDE #loCardPlane, so a slot is on the same ground plane P636 measured
off the old painting and tilts with the card that will sit in it. Same width
(21.5%), same aspect-ratio (911/1298, .fcv's own), same translate(-50%,-50%)
against the same SLOTS coordinates - the box is not restated, it is the card's.

AND THE HOUSE DASH, not a new one. `2px dashed` over a dark translucent fill is
what .lo-hand-slot and .draft-slot already are; this is the same look in cqw so
it scales with the shelf instead of pinning to a device pixel.

ONLY WHERE THERE IS NO CARD. A slot under a filled position would be a hairline
of dash peeking out from behind card art at every anti-aliased edge, which is
the artefact this patch exists to remove.

IT ALSO CLOSES A SMALL HOLE. The old loop was `fcards.slice(0,3).forEach` with
`if(!d)return`, so a card id that no longer resolves - a retired card in an old
save - rendered NOTHING at that position, and the painted slot underneath was
the only thing saying a card belonged there. With the painting gone that would
have been a silently empty stretch of table. The loop is now over the three
POSITIONS rather than over the cards, so an unresolvable id shows an empty slot,
which is the truth.

THE BACKGROUND ITSELF was the other half of this and is not in this patch:
Art/Assets/Shelf/optimized/shelf_bg_opt.webp is what the game loads and it was
still the 2026-07-29 encode of the old painting. Re-encoded with
tools/webp_shelf.js. A stale optimized copy is the worst kind of art bug - the
master is right, the screen is wrong, and nothing between them says so.
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


# ── 1. the slot's look, taking its box from the card ─────────────────────
sub(u".loCard{position:absolute;width:21.5%;transform:translate(-50%,-50%);cursor:pointer;pointer-events:auto}",
    u".loCard{position:absolute;width:21.5%;transform:translate(-50%,-50%);cursor:pointer;pointer-events:auto}\n"
    u"/* P638: THE EMPTY SLOT, DRAWN RATHER THAN PAINTED. Denis repainted the shelf\n"
    u"   without its three marked places so these could be generated from the card's\n"
    u"   own box - the painted ones were 89.3px wide against a 92.5px card, 3.6% out,\n"
    u"   which is where the gold hairline along the outer cards came from.\n"
    u"   Every value here is .loCard's or .fcv's: same width, same aspect-ratio, same\n"
    u"   centring, and it lives inside #loCardPlane so it lies on the same tilted\n"
    u"   plane the card will. A mismatch is not possible rather than merely unlikely.\n"
    u"   `2px dashed` over a dark fill is what .lo-hand-slot and .draft-slot already\n"
    u"   are - the same look, in cqw so it scales with the shelf. */\n"
    u"#loCardPlane .loSlot{position:absolute;width:21.5%;aspect-ratio:911/1298;\n"
    u"  transform:translate(-50%,-50%);pointer-events:none;\n"
    u"  border:0.5cqw dashed rgba(214,176,96,.38);border-radius:6%;\n"
    u"  background:rgba(26,15,6,.26)}",
    'P638 the drawn slot')

# ── 2. loop over POSITIONS, not over the cards ───────────────────────────
sub(u"  /* the three marked table slots wear the painted cards */\n"
    u"  var SLOTS=[[19.6,71.5],[50.5,71.5],[78.5,71.5]];\n"
    u"  var cHtml='';\n"
    u"  S.run.fcards.slice(0,3).forEach(function(c,i){\n"
    u"    var d=famDef(c.id);if(!d)return;\n"
    u"    cHtml+=famCardArt(c.id,c.tier||1,{cls:'loCard',\n"
    u"      style:'left:'+SLOTS[i][0]+'%;top:'+SLOTS[i][1]+'%'});\n"
    u"  });",
    u"  /* the three places on the table. P638: OVER THE POSITIONS, not over the\n"
    u"     cards. The old loop was fcards.slice(0,3).forEach with an `if(!d)return`,\n"
    u"     so a card id that no longer resolves rendered nothing at all and the\n"
    u"     painted slot underneath was the only thing saying a card belonged there -\n"
    u"     and the painting no longer has one. Now the position always draws\n"
    u"     something: the card if it resolves, an empty slot if it does not. */\n"
    u"  var SLOTS=[[19.6,71.5],[50.5,71.5],[78.5,71.5]];\n"
    u"  var cHtml='';\n"
    u"  for(var _si=0;_si<3;_si++){\n"
    u"    var _sPos='left:'+SLOTS[_si][0]+'%;top:'+SLOTS[_si][1]+'%';\n"
    u"    var _sc=S.run.fcards[_si],_sd=_sc&&famDef(_sc.id);\n"
    u"    if(_sd)cHtml+=famCardArt(_sc.id,_sc.tier||1,{cls:'loCard',style:_sPos});\n"
    u"    else cHtml+='<div class=\"loSlot\" style=\"'+_sPos+'\"></div>';\n"
    u"  }",
    'P638 draw a slot wherever there is no card')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('\n%d edits' % n)
