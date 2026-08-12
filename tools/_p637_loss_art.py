# -*- coding: utf-8 -*-
"""P637: the loss screen gets its painting, and the gold sits on the tilted sign.

Denis supplied Art/Assets/Loss/{banner,hands,panel}.png and a mockup, with the
layer order stated: "BG < wooden panel < hands < top banner", and "The panel is
tilted so the gold amount we lose should be also following that angle."

NO LOSS BACKGROUND WAS SUPPLIED, AND NONE IS NEEDED. The mockup's room is the
SAME tavern as the win screen's - same hanging flags, same round tables, same
stools - and win_standard_bg.png is that painting. So this reuses
assets/win/bg.webp rather than shipping a second copy of one image. If Denis
wants a darker or emptier room for a defeat, it is one file and one line.

THE ORDER IS NOT THE WIN'S, and that is deliberate rather than an oversight
carried over. The win paints bg, banner, panel, hands - its banner sits BEHIND
the mugs. Denis's loss order puts the banner in FRONT of everything. Followed as
given.

THE TILT IS MEASURED, NOT EYEBALLED. loss_standard_panel.png at 789x657, the
board's face isolated by colour (the ropes are greyer than the wood) and its
vertical centre tracked down 247 columns:
  * centreline slope 0.18416 -> 10.43 degrees, down to the right
  * the bottom edge alone gives 10.82 (residual 6.0px over 148 samples)
  * the top edge gives 8.29, and is the one to distrust - it carries the painted
    chip out of the middle of the board
10.5 degrees is taken as the axis: between the two trustworthy estimates, and
the top edge is excluded rather than averaged in.
The same pass gives the writable face: centred at 48.7% x, 67.7% y of the layer,
41.9% of its height thick, spanning 1.9-95.4% of its width. The board text is
placed on that centre and held to 74% width so it clears the carved ends.

THE PANEL'S GEOMETRY IS WRITTEN ONCE. .loss-panel and .loss-panel-box share a
single rule, so the sign and the text that sits on it cannot drift apart - the
box carries `aspect-ratio:789/657`, which is what keeps the number on the wood
at an aspect nobody has tested. The win screen's board is a fixed top:37.6% and
does drift; this is the better shape, not a bigger one.

BOTH NEW ELEMENTS ARE SELECTOR-QUALIFIED WITH #end-ov, for the reason already
written above .win-art: `#end-ov>*{position:relative}` further down this sheet
catches every direct child, and it collapsed that layer to 0x0 the first time.

THE NUMBER MOVES TO THE BOARD; THE ANIMATION STAYS WHERE IT IS. A patron loss
forfeits the seat's buy-in and a boss loss forfeits any Innkeep's Book stake -
both used to print a red "-Xg" under a draining coin. The caption is now on the
sign and the coins still drain, so the boss loss keeps its heart leaving the
screen, which is the part that is about a life rather than about money. When
nothing gold was lost - a boss loss with no stake - the board simply stays
empty, which is what the painting shows.

AND THE TITLE STEPS ASIDE, exactly as it does on a win: the banner already says
"lost", so "DEFEAT" printed over it is the same word twice.
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


# ── 1. the markup, in Denis's stated order ───────────────────────────────
sub(u"    <img class=\"win-hands\"  src=\"assets/win/hands.webp?v=1\"  alt=\"\">\n"
    u"  </div>",
    u"    <img class=\"win-hands\"  src=\"assets/win/hands.webp?v=1\"  alt=\"\">\n"
    u"  </div>\n"
    u"  <!-- THE PAINTED LOSS SCREEN. Denis's stated order, which is NOT the win's:\n"
    u"       \"BG < wooden panel < hands < top banner\". The win puts its banner\n"
    u"       behind the mugs; here it is in front of everything.\n"
    u"       The background is the WIN'S. Denis supplied three layers and no room,\n"
    u"       and the mockup's tavern is the same painting the win screen already\n"
    u"       loads - same flags, same tables, same stools. One image, one copy. -->\n"
    u"  <div class=\"loss-art\" aria-hidden=\"true\">\n"
    u"    <img class=\"loss-bg\"     src=\"assets/win/bg.webp?v=1\"      alt=\"\">\n"
    u"    <img class=\"loss-panel\"  src=\"assets/loss/panel.webp?v=1\"  alt=\"\">\n"
    u"    <img class=\"loss-hands\"  src=\"assets/loss/hands.webp?v=1\"  alt=\"\">\n"
    u"    <img class=\"loss-banner\" src=\"assets/loss/banner.webp?v=1\" alt=\"\">\n"
    u"  </div>\n"
    u"  <!-- WHAT THE SIGN SAYS. Its own box rather than a child of .loss-art,\n"
    u"       which is aria-hidden - this is a number the player needs read out.\n"
    u"       It shares .loss-panel's geometry rule, so the wood and the writing on\n"
    u"       it cannot drift apart. -->\n"
    u"  <div class=\"loss-panel-box\" aria-hidden=\"false\">\n"
    u"    <div class=\"loss-board\" id=\"lossBoard\">\n"
    u"      <span class=\"lb-coin\"></span><span id=\"lossGoldNum\">0</span>\n"
    u"    </div>\n"
    u"  </div>",
    'P637 the loss art markup')

# ── 2. the CSS, beside the win's ─────────────────────────────────────────
sub(u"/* the board is where the numbers live, so it must not be swallowed by the\n"
    u"   scanline veil that sits over this overlay */\n"
    u"#end-ov .res-title,#end-ov .res-scores,#end-ov .res-gold-wrap{z-index:3}",
    u"/* ══ THE LOSS PAINTING ══ four layers in DENIS'S order, which is not the\n"
    u"   win's: \"BG < wooden panel < hands < top banner\". The win's banner hangs\n"
    u"   behind the mugs; this one is in front of everything.\n"
    u"   #end-ov-QUALIFIED for the reason written above .win-art - the\n"
    u"   `#end-ov>*{position:relative}` rule further down this sheet catches every\n"
    u"   direct child and collapsed that layer to 0x0 the first time. */\n"
    u"#end-ov .loss-art{position:absolute;inset:0;z-index:0;pointer-events:none;\n"
    u"  opacity:0;transition:opacity .45s ease}\n"
    u"#end-ov.loss-art-on .loss-art{opacity:1}\n"
    u".loss-art img{position:absolute;left:50%;transform:translateX(-50%);\n"
    u"  image-rendering:auto;-webkit-user-drag:none;user-select:none}\n"
    u"/* COVER, like the win's: the room bleeds off the edges and a letterboxed\n"
    u"   tavern would show the page behind it. */\n"
    u".loss-bg{top:0;width:100%;height:100%;object-fit:cover;object-position:50% 50%}\n"
    u"/* THE WIDTHS COME FROM THE FILES, not from reading the mockup. The three\n"
    u"   layers were painted on one canvas and the hands span it edge to edge at\n"
    u"   1084px, so that is the canvas width: banner 1041/1084 = 96%, panel\n"
    u"   789/1084 = 72.8%. Only the vertical placements are by eye. */\n"
    u".loss-banner{top:6%;width:96%}\n"
    u".loss-hands {top:26%;width:100%}\n"
    u"/* ONE RULE FOR THE SIGN AND FOR THE WRITING ON IT. Two rules would be the\n"
    u"   two-copies bug in geometry - move the sign, leave the number behind.\n"
    u"   aspect-ratio rather than a second top%: the win board is pinned at a fixed\n"
    u"   37.6% and slides off its own panel as the viewport aspect changes. */\n"
    u"#end-ov .loss-panel,#end-ov .loss-panel-box{position:absolute;left:50%;\n"
    u"  top:36%;width:72.8%;aspect-ratio:789/657;transform:translateX(-50%)}\n"
    u"#end-ov .loss-panel-box{z-index:3;pointer-events:none;display:none}\n"
    u"#end-ov.loss-art-on .loss-panel-box{display:block}\n"
    u"/* ON THE WOOD, AT THE WOOD'S ANGLE. Measured off loss_standard_panel.png:\n"
    u"   the board face's centreline runs 10.43deg down to the right (its bottom\n"
    u"   edge alone says 10.82; its top edge says 8.29 and carries the painted chip,\n"
    u"   so it is excluded rather than averaged in). 10.5 is the axis.\n"
    u"   The face itself sits at 48.7% x / 67.7% y of the layer and is 41.9% of its\n"
    u"   height thick; 74% width keeps the line clear of the carved ends. */\n"
    u"#end-ov .loss-board{position:absolute;left:48.7%;top:67.7%;width:74%;\n"
    u"  transform:translate(-50%,-50%) rotate(10.5deg);\n"
    u"  display:flex;align-items:center;justify-content:center;gap:.32em;\n"
    u"  font-family:'JMH Beda',serif;font-size:clamp(20px,6.2vw,36px);line-height:1;\n"
    u"  /* gold on dark wood, not the red the old -Xg caption used: the subject is\n"
    u"     coins crossing the table and the coin beside it is gold. The dark cut\n"
    u"     under it is what keeps it off the grain. */\n"
    u"  color:#f0cf7d;letter-spacing:.02em;\n"
    u"  text-shadow:0 2px 0 rgba(28,14,4,.85),0 0 14px rgba(0,0,0,.5)}\n"
    u"#end-ov .loss-board.empty{display:none}\n"
    u"/* the game's own coin, the same one the win board uses */\n"
    u"#end-ov .loss-board .lb-coin{width:1.05em;height:1.05em;background-size:contain;\n"
    u"  background-repeat:no-repeat;background-position:50% 50%;\n"
    u"  background-image:url('Art/Assets/Icons/optimized/coin_opt.webp')}\n"
    u"/* what the painting replaces - the same list the win screen suppresses */\n"
    u"#end-ov.loss-art-on .res-scores,\n"
    u"#end-ov.loss-art-on .res-gold-wrap{display:none!important}\n"
    u"/* the board is where the numbers live, so it must not be swallowed by the\n"
    u"   scanline veil that sits over this overlay */\n"
    u"#end-ov .res-title,#end-ov .res-scores,#end-ov .res-gold-wrap{z-index:3}",
    'P637 the loss art CSS')

# ── 3. switch it on, and put the number on the sign ──────────────────────
sub(u"  /* THE PAINTING IS FOR WINS ONLY. There is no defeat art yet, and a\n"
    u"     half-dressed loss screen - a celebration room with the wrong word on it -\n"
    u"     reads worse than the plain dark one it already had. The banner itself says\n"
    u"     WON, so it cannot be reused either way. */\n"
    u"  ov.classList.toggle('win-art-on',!!win);",
    u"  ov.classList.toggle('win-art-on',!!win);\n"
    u"  /* P637: AND NOW THERE IS DEFEAT ART. The note that used to sit here said\n"
    u"     there was none and that half-dressing a loss read worse than not dressing\n"
    u"     it - true while it was true. Denis painted the three layers; the room is\n"
    u"     the win's, because the mockup's tavern IS that painting. */\n"
    u"  ov.classList.toggle('loss-art-on',!win);\n"
    u"  /* WHAT THE SIGN SAYS. A patron loss forfeits the seat's buy-in; a boss loss\n"
    u"     forfeits any Innkeep's Book stake, and often no gold at all - that one\n"
    u"     costs a life, and the heart still drains for it below. Read from the same\n"
    u"     two sources the old red caption used, so there is one answer and not a\n"
    u"     second derivation of it. */\n"
    u"  try{\n"
    u"    var _lb=document.getElementById('lossBoard'),_lbN=document.getElementById('lossGoldNum');\n"
    u"    var _lossGold=0;\n"
    u"    if(!win){\n"
    u"      if(G&&G._isBoss)_lossGold=(S&&S.run&&S.run._bookResult&&S.run._bookResult.lost)||0;\n"
    u"      else _lossGold=(typeof LO!=='undefined'&&LO&&LO.buyIn)||0;\n"
    u"    }\n"
    u"    if(_lbN)_lbN.textContent='\\u2212'+_lossGold.toLocaleString()+'g';\n"
    u"    /* an empty sign rather than a \"-0g\", which reads as a bug */\n"
    u"    if(_lb)_lb.classList.toggle('empty',!(_lossGold>0));\n"
    u"  }catch(e){}",
    'P637 switch the art on and fill the sign')

# ── 4. the title steps aside, as it does on a win ────────────────────────
sub(u"  /* the banner already says WON, so a VICTORY heading on top of it is the\n"
    u"     same word twice - the title steps aside on a win and keeps its job on a\n"
    u"     loss, where there is no art to say it */\n"
    u"  resTitle.textContent=win?'':'DEFEAT';",
    u"  /* the banner says the word, so a heading on top of it is the same word\n"
    u"     twice. P637: this used to keep DEFEAT on a loss because there was no art\n"
    u"     to say it; the loss banner reads \"lost\", so now neither outcome needs a\n"
    u"     title. Kept as an expression rather than deleted - a future outcome with\n"
    u"     no painting behind it still has somewhere to print. */\n"
    u"  resTitle.textContent='';",
    'P637 the title steps aside on a loss too')

# ── 5. the red caption is on the sign now; the coins still drain ─────────
sub(u"        if(resGoldText){resGoldText.textContent='\u2212'+_lostStake+'g';resGoldText.style.color='#e0606a';resGoldText.classList.add('show');}",
    u"        /* P637: the caption moved to the sign. The coins are untouched - the\n"
    u"           heart leaving the screen is about a life, not about money. */",
    'P637 drop the boss-loss caption')

# The patron-loss caption is the SIXTH edit and lives in tools/_p637b_patron_caption.py.
# It is split out because that site stores its minus sign as the six literal
# characters backslash-u-2-2-1-2 while the boss site forty lines up stores a real
# U+2212 - the same file, both encodings. Keeping it here would mean this script
# carrying two incompatible spellings of one character.
#
# AND NOTE WHAT SAVED THE FILE WHEN IT DID FAIL: sub() calls sys.exit BEFORE the
# single write below, so a missed anchor leaves fark_proto.html untouched rather
# than half-patched. Do not move the write earlier.

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('\n%d edits' % n)
