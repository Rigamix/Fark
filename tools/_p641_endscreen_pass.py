# -*- coding: utf-8 -*-
"""P641: Denis's pass over the two end screens and the shelf row.

His list, in his order, with what each turned into.

── LOSS ──
"move the panel a bit to the left side" - left:50% -> 46%, which puts the sign
at 9.6-82.4% of the screen against the 10-77% his mockup shows.

"Make the gold amount, icon, etc much bigger since it's the only thing on it"
- the sign carries one line and had it at clamp(20,6.2vw,36). Now
clamp(34,11vw,62), and the coin grows with it because it is sized in em.

"The Back to the Room button should match the ones on the Win screen ... What
you currently have is an old game button." Correct, and literally so: it draws
itself with drawPixelPanel onto a <canvas>, which is the pre-art pixel-panel
look. It now wears Button_new_01, the same painted plate .fo-skip uses. The
canvas is left in the markup but hidden - handleContinue and the resize path
both still reference it, and removing an element three call sites reach for is
a separate change from restyling a button.

── SHELF ──
"Move the cards and cards slot a few pixels up so they don't flirt with the top
of the dice." Both move because both are placed from ONE constant now:
_LO_CARD_ROW_Y, 71.5 -> 69.5. It also writes the plane's transform-origin
inline, so the row's position and the tilt's pivot cannot drift apart - they
were two numbers a tenth of a per cent apart in P636 and would have needed
editing in lockstep forever.

── WIN ──
"Move the pick a card and the cards themselves a bit higher but leave the cards
slots where they are" - two moves, not one: .res-card lifts 52% -> 47%, and
.fo-deck takes back the same distance in padding so the slots stay put.

"spread them out horizontally a bit so they don't overlap as much and match
their look closer to the slots on the shelf screen" - the -5% overlap becomes
+1.5% of clear air, the fan angle drops from 7 to 4 degrees, and the empty slot
takes the shelf's dash: same colour, same weight in cqw, same 6% radius, and no
"+" glyph, because the shelf's have none.

"Move the skip button a touch lower (those buttons should match position on the
win, loss screens ideally)" - both are now anchored to the same distance off the
bottom safe area rather than one flowing and one absolute, so they land in the
same place by construction instead of by tuning.

"make the text/icon inside larger" - clamp(14,4.2vw,20) -> clamp(17,5.2vw,25).

"make the gold won, points earned and diamond icons larger" - score
clamp(19,5.6vw,30) -> clamp(23,6.8vw,36); gold clamp(17,5vw,27) ->
clamp(21,6.2vw,33); the win-count plate 2.1em -> 2.6em.

"gold amount text is too close in color to the panel color" - MEASURED off the
render rather than adjusted by eye. The parchment samples at (189,147,95); the
score's #3b2a16 sits at 2.89:1 against it and the gold's #6b4d15 at 1.79:1. The
gold goes to #3d2a06, which is 2.92:1 - the same weight as the score beside it,
and still the warmer hue.

"Gold coin icon is very aliased" - and the cause is not the asset: coin_opt.webp
is 213x212 for a ~25px slot. `body{image-rendering:pixelated}` is inherited by
everything on the page, so every painted icon is being resampled
nearest-neighbour. .win-art img already opts out with `image-rendering:auto` for
exactly this reason; the coins and the win-count plate now do the same.
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


# ══ LOSS: the sign moves left and speaks up ══════════════════════════════
sub(u"#end-ov .loss-panel,#end-ov .loss-panel-box{position:absolute;left:50%;\n"
    u"  top:36%;width:72.8%;aspect-ratio:789/657;transform:translateX(-50%)}",
    u"/* P641: left:50% -> 46%, per Denis. The sign now spans 9.6-82.4% of the\n"
    u"   screen, against the 10-77% his mockup places it at. */\n"
    u"#end-ov .loss-panel,#end-ov .loss-panel-box{position:absolute;left:46%;\n"
    u"  top:36%;width:72.8%;aspect-ratio:789/657;transform:translateX(-50%)}",
    'P641 loss sign moves left')

sub(u"  font-family:'JMH Beda',serif;font-size:clamp(20px,6.2vw,36px);line-height:1;",
    u"  /* P641: MUCH bigger - Denis, and he is right that one line on a board this\n"
    u"     size was reading as a caption. The coin is in em, so it grows with it. */\n"
    u"  font-family:'JMH Beda',serif;font-size:clamp(34px,11vw,62px);line-height:1;",
    'P641 the sign speaks up')

# ══ LOSS: the button stops being from the old game ═══════════════════════
sub(u"#btnContinue:active,#btnStore:active{filter:brightness(1.3);transform:scale(.96)}\n"
    u"#btnContinue canvas,#btnStore canvas{\n"
    u"  position:absolute;inset:0;width:100%;height:100%;\n"
    u"  pointer-events:none;border-radius:6px;z-index:0;image-rendering:pixelated;\n"
    u"}\n"
    u"#btnContinue span,#btnStore span{position:relative;z-index:1}\n"
    u"#btnContinue span{color:#7ddc84}",
    u"#btnContinue:active,#btnStore:active{filter:brightness(1.3);transform:scale(.96)}\n"
    u"/* P641: THE PAINTED PLATE, not the drawn one. Denis: \"What you currently have\n"
    u"   is an old game button.\" Literally so - drawPixelPanel renders a pixel panel\n"
    u"   onto this canvas, which is the look the painted buttons replaced everywhere\n"
    u"   else. Same background the win screen's .fo-skip wears, so the two screens\n"
    u"   agree.\n"
    u"   THE CANVAS STAYS IN THE MARKUP, hidden. Three places still reach for\n"
    u"   #cvBtnContinue - the draft-delay block sizes and draws it - and deleting an\n"
    u"   element out from under its callers is a different change from restyling a\n"
    u"   button. It paints nothing now because nothing can see it. */\n"
    u"#btnContinue canvas,#btnStore canvas{display:none}\n"
    u"#btnContinue,#btnStore{\n"
    u"  background-image:url('Art/Assets/Buttons/optimized/Button_new_01_opt.webp');\n"
    u"  background-size:100% 100%;background-repeat:no-repeat;\n"
    u"  border-radius:0;overflow:visible;min-height:2.9em}\n"
    u"#btnContinue span,#btnStore span{position:relative;z-index:1}\n"
    u"/* the painted plate carries its own colour, so the old green is off */\n"
    u"#btnContinue span{color:#f6e6bd;text-shadow:0 2px 2px rgba(0,0,0,.6)}",
    'P641 the loss button wears the painted plate')

# ══ WIN: the board's three cells grow, and the gold reads ════════════════
sub(u".win-board .wb-score{font-family:'JMH Beda',serif;font-size:clamp(19px,5.6vw,30px);\n"
    u"  color:#3b2a16;line-height:1;letter-spacing:.01em;\n"
    u"  text-shadow:0 1px 0 rgba(255,245,220,.55)}\n"
    u".win-board .wb-gold{gap:.3em;\n"
    u"  font-family:'JMH Beda',serif;font-size:clamp(17px,5vw,27px);color:#6b4d15}",
    u"/* P641: bigger, per Denis - \"you have some room\". */\n"
    u".win-board .wb-score{font-family:'JMH Beda',serif;font-size:clamp(23px,6.8vw,36px);\n"
    u"  color:#3b2a16;line-height:1;letter-spacing:.01em;\n"
    u"  text-shadow:0 1px 0 rgba(255,245,220,.55)}\n"
    u"/* P641: AND DARKER, measured rather than nudged. The parchment samples at\n"
    u"   (189,147,95); the score's #3b2a16 sits at 2.89:1 against it and the old\n"
    u"   #6b4d15 at 1.79:1, which is Denis's \"too close in color to the panel\".\n"
    u"   #3d2a06 is 2.92:1 - the same weight as the score, still the warmer hue. */\n"
    u".win-board .wb-gold{gap:.3em;\n"
    u"  font-family:'JMH Beda',serif;font-size:clamp(21px,6.2vw,33px);color:#3d2a06;\n"
    u"  text-shadow:0 1px 0 rgba(255,245,220,.5)}",
    'P641 the board cells grow and the gold reads')

sub(u".win-board .wb-coin{width:1.15em;height:1.15em;background-size:contain;\n"
    u"  background-repeat:no-repeat;background-position:50% 50%;\n"
    u"  background-image:url('Art/Assets/Icons/optimized/coin_opt.webp')}",
    u"/* P641: `image-rendering:auto`, and the asset was never the problem -\n"
    u"   coin_opt.webp is 213x212 for a ~25px slot. `body{image-rendering:pixelated}`\n"
    u"   is inherited by the whole page, so every painted icon was being resampled\n"
    u"   nearest-neighbour. .win-art img already opts out for the same reason. */\n"
    u".win-board .wb-coin{width:1.15em;height:1.15em;background-size:contain;\n"
    u"  background-repeat:no-repeat;background-position:50% 50%;image-rendering:auto;\n"
    u"  background-image:url('Art/Assets/Icons/optimized/coin_opt.webp')}",
    'P641 unpixelate the board coin')

sub(u".win-board .wb-dmds{display:flex;align-items:center;height:2.1em}\n"
    u".win-board .wb-dmds img{height:100%;width:auto;-webkit-user-drag:none;\n"
    u"  image-rendering:auto}",
    u"/* P641: 2.1em -> 2.6em, the third of Denis's three cells */\n"
    u".win-board .wb-dmds{display:flex;align-items:center;height:2.6em}\n"
    u".win-board .wb-dmds img{height:100%;width:auto;-webkit-user-drag:none;\n"
    u"  image-rendering:auto}",
    'P641 the win-count plate grows')

sub(u".fo-coin{width:1.15em;height:1.15em;flex:none;background-size:contain;\n"
    u"  background-repeat:no-repeat;background-position:50% 50%;\n"
    u"  background-image:url('Art/Assets/Icons/optimized/coin_opt.webp')}",
    u"/* P641: same nearest-neighbour inheritance as the board's coin */\n"
    u".fo-coin{width:1.15em;height:1.15em;flex:none;background-size:contain;\n"
    u"  background-repeat:no-repeat;background-position:50% 50%;image-rendering:auto;\n"
    u"  background-image:url('Art/Assets/Icons/optimized/coin_opt.webp')}",
    'P641 unpixelate the skip coin')

# ══ WIN: the deck slots spread, and take the shelf's dash ════════════════
sub(u".fo-slot{width:19%;aspect-ratio:911/1298;border-radius:6px;flex:none;\n"
    u"  transition:transform .18s ease}\n"
    u".fo-slot+.fo-slot{margin-left:-5%}\n"
    u".fo-slot:first-child{transform:rotate(-7deg) translateY(2px)}\n"
    u".fo-slot:nth-child(2){transform:translateY(-3px);z-index:2}\n"
    u".fo-slot:last-child{transform:rotate(7deg) translateY(2px)}\n"
    u".fo-slot.filled{cursor:pointer}\n"
    u".fo-slot.filled:active{transform:translateY(-4px) scale(1.04);z-index:3}\n"
    u".fo-slot.empty{border:1px dashed #554;display:flex;align-items:center;\n"
    u"  justify-content:center;color:#554;font-size:18px}",
    u"/* P641: SPREAD, and wearing the shelf's dash. Denis: \"spread them out\n"
    u"   horizontally a bit so they don't overlap as much and match their look\n"
    u"   closer to the slots on the shelf screen\". The -5% overlap becomes +1.5% of\n"
    u"   clear air and the fan drops 7deg -> 4deg. */\n"
    u".fo-slot{width:19%;aspect-ratio:911/1298;border-radius:6%;flex:none;\n"
    u"  transition:transform .18s ease}\n"
    u".fo-slot+.fo-slot{margin-left:1.5%}\n"
    u".fo-slot:first-child{transform:rotate(-4deg) translateY(2px)}\n"
    u".fo-slot:nth-child(2){transform:translateY(-3px);z-index:2}\n"
    u".fo-slot:last-child{transform:rotate(4deg) translateY(2px)}\n"
    u".fo-slot.filled{cursor:pointer}\n"
    u".fo-slot.filled:active{transform:translateY(-4px) scale(1.04);z-index:3}\n"
    u"/* the shelf's own empty slot, value for value - see #loCardPlane .loSlot.\n"
    u"   No \"+\" glyph, because the shelf's have none. */\n"
    u".fo-slot.empty{border:0.5cqw dashed rgba(214,176,96,.38);\n"
    u"  background:rgba(26,15,6,.26);font-size:0;color:transparent}",
    'P641 the deck slots spread and match the shelf')

# ══ WIN: the offer rises, the slots stay, the skip drops ═════════════════
sub(u"#end-ov.win-art-on .res-card{top:52%!important;width:80%!important}",
    u"/* P641: the offer rises 52% -> 47% per Denis, and .fo-deck takes the same\n"
    u"   distance back in padding below so the SLOTS do not move with it - two\n"
    u"   changes, because he asked for the cards up and the slots left alone. */\n"
    u"#end-ov.win-art-on .res-card{top:47%!important;width:80%!important}\n"
    u"#end-ov.win-art-on .fo-deck{padding-top:calc(6px + 5%)}",
    'P641 the offer rises, the slots hold')

sub(u"#end-ov.win-art-on .fo-deck{padding-top:2px}",
    u"",
    'P641 drop the old fo-deck padding override')

# ══ BOTH: the two screens' buttons land in the same place ════════════════
sub(u".fo-skip{display:flex;align-items:center;justify-content:center;gap:.4em;\n"
    u"  cursor:pointer;margin:8px auto 0;width:82%;min-height:2.9em;padding:.55em 1em;\n"
    u"  font-family:'JMH Beda',serif;font-size:clamp(14px,4.2vw,20px);",
    u"/* P641: LOWER AND LARGER, and anchored the same way #btnContinue is so the\n"
    u"   two screens' primary buttons land in the same place by construction rather\n"
    u"   than by tuning two different layout systems against each other. */\n"
    u".fo-skip{display:flex;align-items:center;justify-content:center;gap:.4em;\n"
    u"  cursor:pointer;margin:8px auto 0;width:82%;min-height:2.9em;padding:.55em 1em;\n"
    u"  font-family:'JMH Beda',serif;font-size:clamp(17px,5.2vw,25px);",
    'P641 the skip button grows')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('\n%d edits' % n)
