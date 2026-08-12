# -*- coding: utf-8 -*-
"""P636: the shelf's three cards lie on the plane their slots are painted on.

Denis: "In the Shelf screen, there are 3 areas for the cards to sit in. If you
look at the art you can see those are drawn with a perspective, but the cards
are sitting straight with no perspective on them. Fix that."

MEASURED OFF DENIS'S OWN PAINTING, not eyeballed. shelf_bg.png at 2160x4476,
the middle slot's two long edges tracked down 64 scan rows clear of the corner
arcs:
  * its top edge is at y=2924, its bottom at y=3466
  * its width goes 402.9 -> 494.2, a ratio of 1.2266
  * its centre stays at x=1075 against an image centre of 1080 - so it is
    SYMMETRIC, and the vanishing point is directly above the middle slot
  * the row's centre sits at 71.38% of the image height, against the 71.5% the
    SLOTS array already places the cards at. 0.12% apart.
A symmetric taper with a vanishing point above centre is one ground plane, which
is the same thing #famRowP and #famRowO are already built out of. So this is the
existing idiom applied to a third surface, not a new mechanism.

TWO NUMBERS, EACH FROM A DIFFERENT MEASUREMENT, AND THEY AGREE.
  rotateX comes from HEIGHT: the slot is 107.9px tall on the 430px stage and the
    card is authored 131.7px tall, so the plane is tilted acos(107.9/131.7) =
    35.00 degrees.
  perspective comes from WIDTH: at 35 degrees, the distance that produces a
    1.2266 top-to-bottom taper across a 131.7px card is 371px.
Neither was fitted to the other, and the card's 131.7px comes from the CSS
rather than from the image, so the agreement is not the detector talking to
itself. Both reproduce their target exactly on the back-check.

THE ORIGIN IS WHY THIS IS SAFE. transform-origin sits on the slot row itself, so
all three card CENTRES are on the plane's origin line and do not move at all -
only their shapes change. That matters beyond looks: _loCardFocus measures the
card's rect to work out how far to fly it, and an origin anywhere else would
have quietly moved the thing it measures.

AND THE PLANE FLATTENS FOR THE FOCUS, because it has to. The focus panel sits
near 36% of the screen, far above the plane's origin, where the perspective
divide would draw the card small and hard trapezoidal. So _loCardFocus adds
`flat` to the plane and _loUnfocus takes it off, on a transition matched to the
card's own flight - the card un-tilts as it rises, which is the movement Denis
asked for in the same note. A CLASS RATHER THAN .lo-focus: a DIE focus must
leave the plane alone, or the cards would silently un-tilt behind the scrim and
tilt back as they faded in.

Z-INDEX, DELIBERATELY, AND ONLY WHILE FLAT. A transform makes a stacking
context, so .loCard.zoom's z-index:60 stops meaning anything outside the plane -
the exact regression P594 shipped on the leader's flag. The plane is therefore
lifted to 60 in the same rule that flattens it, so it clears #loFocusScrim (50)
only while a card is actually out of it, and normal stacking is untouched the
rest of the time.

pointer-events: the plane covers the whole stage, so it is transparent to taps
and the cards opt back in. Without that it would eat every tap meant for the
dice, the feats and the badges underneath.
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


# ── 1. the plane's CSS, beside the rule it governs ───────────────────────
sub(u".loCard{position:absolute;width:21.5%;transform:translate(-50%,-50%);cursor:pointer}",
    u"/* P636: THE GROUND PLANE THE SLOTS ARE PAINTED ON. Measured off shelf_bg.png:\n"
    u"   the middle slot's width runs 402.9 -> 494.2 top to bottom (ratio 1.2266) and\n"
    u"   its centre holds at the image centre, so the three slots share one plane\n"
    u"   with the vanishing point above the middle one. rotateX is acos of the slot's\n"
    u"   107.9px height over the card's authored 131.7px = 35deg; the perspective is\n"
    u"   the distance that gives that taper at that angle = 371px. Two measurements,\n"
    u"   one from height and one from width, neither fitted to the other.\n"
    u"   THE ORIGIN IS ON THE SLOT ROW (71.4%, against the 71.5% the SLOTS array\n"
    u"   uses), so all three card centres sit on it and do not move - only their\n"
    u"   shapes change. _loCardFocus measures those rects to aim its flight.\n"
    u"   Transparent to taps: it covers the whole stage, and the dice, feats and\n"
    u"   badges underneath still need theirs. */\n"
    u"#loCardPlane{position:absolute;inset:0;pointer-events:none;\n"
    u"  transform-origin:50% 71.4%;transform:perspective(371px) rotateX(35deg);\n"
    u"  transition:transform .55s cubic-bezier(.3,1.35,.35,1)}\n"
    u"/* FLAT WHILE A CARD IS OUT OF IT. The focus panel sits near 36% of the screen,\n"
    u"   far above the origin, where the divide would draw the card small and hard\n"
    u"   trapezoidal - so the plane lays down and the card un-tilts as it rises.\n"
    u"   A class set by _loCardFocus, NOT .lo-focus: a DIE focus must leave the plane\n"
    u"   alone or the cards flip flat behind the scrim and back as they fade in.\n"
    u"   The z-index rides with it because a transform is a stacking context, so\n"
    u"   .loCard.zoom's 60 means nothing outside this element - P594's bug exactly.\n"
    u"   Lifted only while flat, so ordinary stacking is untouched. */\n"
    u"#loCardPlane.flat{transform:none;z-index:60}\n"
    u".loCard{position:absolute;width:21.5%;transform:translate(-50%,-50%);cursor:pointer;pointer-events:auto}",
    'P636 the plane CSS')

# ── 2. wrap the three cards in it ────────────────────────────────────────
sub(u"      +fHtml+'<div id=\"loWallVig\"></div>'+bHtml+cHtml+dHtml",
    u"      +fHtml+'<div id=\"loWallVig\"></div>'+bHtml\n"
    u"      /* P636: the cards go inside the tilted plane. inset:0 on the plane means\n"
    u"         their % placements resolve against the same box as before, so the\n"
    u"         SLOTS array is untouched. */\n"
    u"      +'<div id=\"loCardPlane\">'+cHtml+'</div>'+dHtml",
    'P636 wrap the cards')

# ── 3. lay the plane down for a card focus, and stand it back up ─────────
sub(u"  el.classList.add('zoom');\n"
    u"  ov.classList.add('lo-focus');\n"
    u"  window._loFocSp=el;",
    u"  el.classList.add('zoom');\n"
    u"  /* P636: the plane lays down so the card arrives flat, and rises out of the\n"
    u"     stacking context its own transform creates. Same duration as the flight\n"
    u"     above, so the un-tilt and the travel are one movement. */\n"
    u"  try{var _pl=document.getElementById('loCardPlane');if(_pl)_pl.classList.add('flat');}catch(e){}\n"
    u"  ov.classList.add('lo-focus');\n"
    u"  window._loFocSp=el;",
    'P636 flatten on focus')

sub(u"function _loUnfocus(){\n"
    u"  var ov=document.getElementById('gbLoadout');\n"
    u"  if(!ov||!ov.classList.contains('lo-focus'))return;\n"
    u"  ov.classList.remove('lo-focus');",
    u"function _loUnfocus(){\n"
    u"  var ov=document.getElementById('gbLoadout');\n"
    u"  if(!ov||!ov.classList.contains('lo-focus'))return;\n"
    u"  ov.classList.remove('lo-focus');\n"
    u"  /* P636: unconditional, because it is idempotent and a die focus never set\n"
    u"     it - the alternative is remembering which kind of focus this was, which is\n"
    u"     a second piece of state for no gain. */\n"
    u"  try{var _pl=document.getElementById('loCardPlane');if(_pl)_pl.classList.remove('flat');}catch(e){}",
    'P636 stand the plane back up')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('\n%d edits' % n)
