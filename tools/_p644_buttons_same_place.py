# -*- coding: utf-8 -*-
"""P644: the win and loss buttons land in the same place, structurally.

Denis: "those buttons should match position on the win, loss screens ideally".

P643 tried `position:fixed` on the win's SKIP and it did not work, for a reason
worth writing down: `#end-ov .res-card` carries `transform:translateX(-50%)`, and
A TRANSFORMED ANCESTOR BECOMES THE CONTAINING BLOCK FOR `position:fixed`
DESCENDANTS. So "28px off the bottom of the screen" quietly meant "28px off the
bottom of the offer card", and the button measured at 77.3% against the loss
button's 91.1%. Fixed inside a transform is not fixed.

SO THE BUTTON LEAVES THE CARD. After the offer renders, the .fo-skip node is
moved to be a direct child of #end-ov and positioned with the same anchor
#end-btns already uses - `bottom:calc(28px + env(safe-area-inset-bottom,0px))`.
Both screens' primary buttons now share one anchor and one width, so they match
by construction rather than by two numbers tuned against each other.

REMOVED AT ONE PLACE, and that is why this is safe. A node hoisted out of
.res-card no longer disappears when .res-card's innerHTML is replaced - which is
what every draft outcome does - so it would have outlived the offer and sat over
the next screen. _famEndReady is the single convergence point for all four
outcomes (pick, upgrade, replace, decline) and already exists to reveal
#end-btns; the skip is torn down there, next to the thing that replaces it.

The selector is #end-ov-qualified because `#end-ov>*{position:relative}` further
down this sheet catches every direct child and would beat a bare .fo-skip - the
same trap already recorded above .win-art and .loss-art.

And #end-btns gets a width: it is a flex row sized by its content, so
`#btnContinue{width:82%}` was 82% of nothing in particular and the loss button
measured 49.2% against the win's 65.6%.
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


# ── 1. the skip stops pretending to be fixed ─────────────────────────────
sub(u".fo-skip{display:flex;align-items:center;justify-content:center;gap:.4em;\n"
    u"  cursor:pointer;width:82%;min-height:2.9em;padding:.55em 1em;\n"
    u"  position:fixed;left:50%;transform:translateX(-50%);\n"
    u"  bottom:calc(28px + env(safe-area-inset-bottom,0px));z-index:6;",
    u".fo-skip{display:flex;align-items:center;justify-content:center;gap:.4em;\n"
    u"  cursor:pointer;width:82%;min-height:2.9em;padding:.55em 1em;",
    'P644 drop the broken fixed positioning')

sub(u".fo-skip:active{transform:translateX(-50%) translateY(1px)}",
    u"/* P644: HOISTED OUT OF .res-card by the offer builder, because that element\n"
    u"   carries a transform and a transformed ancestor becomes the containing block\n"
    u"   for position:fixed - so \"28px off the screen\" meant \"28px off the card\",\n"
    u"   and the button sat at 77.3% against the loss button's 91.1%.\n"
    u"   Same anchor as #end-btns now, so the two screens agree by construction.\n"
    u"   #end-ov-qualified because `#end-ov>*{position:relative}` below catches\n"
    u"   every direct child and beats a bare class. */\n"
    u"#end-ov>.fo-skip{position:absolute;left:50%;transform:translateX(-50%);\n"
    u"  bottom:calc(28px + env(safe-area-inset-bottom,0px));z-index:6;margin:0}\n"
    u"#end-ov>.fo-skip:active{transform:translateX(-50%) translateY(1px)}\n"
    u".fo-skip:active{transform:translateY(1px)}",
    'P644 anchor the hoisted skip')

# ── 2. the loss button gets a real width and the same type size ──────────
sub(u"  position:absolute!important;bottom:calc(28px + env(safe-area-inset-bottom,0px));left:50%;transform:translateX(-50%);\n"
    u"  display:flex;align-items:center;\n"
    u"}",
    u"  position:absolute!important;bottom:calc(28px + env(safe-area-inset-bottom,0px));left:50%;transform:translateX(-50%);\n"
    u"  /* P644: A WIDTH. This is a flex row sized by its content, so the 82% on\n"
    u"     #btnContinue resolved against nothing meaningful and the loss button came\n"
    u"     out 49.2% wide against the win's 65.6%. */\n"
    u"  display:flex;align-items:center;justify-content:center;width:82%;\n"
    u"}",
    'P644 give the loss button row a width')

sub(u"  padding:.55em 1em;width:82%;justify-content:center;white-space:nowrap;\n"
    u"  overflow:visible;border-radius:6px;",
    u"  /* P644: fills its row, which is the 82% above - and the same type scale as\n"
    u"     the win's SKIP, so the two plates carry the same weight of text. */\n"
    u"  padding:.55em 1em;width:100%;justify-content:center;white-space:nowrap;\n"
    u"  font-size:clamp(17px,5.2vw,25px);letter-spacing:.04em;\n"
    u"  overflow:visible;border-radius:6px;",
    'P644 the loss button fills its row')

# ── 3. hoist on render, tear down on the one exit ────────────────────────
sub(u"    if(resCard){resCard.innerHTML=famOfferHtml(_famOffer,'famDraftPick',_dg);resCard.classList.add('show');}",
    u"    if(resCard){resCard.innerHTML=famOfferHtml(_famOffer,'famDraftPick',_dg);resCard.classList.add('show');}\n"
    u"    /* P644: the SKIP moves out of .res-card. It cannot be anchored to the\n"
    u"       screen from inside an element that carries a transform, and it has to\n"
    u"       sit where the loss screen's button sits. Torn down in _famEndReady,\n"
    u"       which every draft outcome passes through - once out here it no longer\n"
    u"       vanishes with .res-card's innerHTML. */\n"
    u"    try{\n"
    u"      var _ovSk=document.getElementById('end-ov');\n"
    u"      _ovSk.querySelectorAll(':scope>.fo-skip').forEach(function(e){e.remove();});\n"
    u"      var _sk=resCard&&resCard.querySelector('.fo-skip');\n"
    u"      if(_sk&&_ovSk)_ovSk.appendChild(_sk);\n"
    u"    }catch(e){}",
    'P644 hoist the skip on render')

sub(u"function _famEndReady(){\n"
    u"  try{var eb=document.getElementById('end-btns');if(eb)eb.style.display='';}catch(e){}",
    u"function _famEndReady(){\n"
    u"  /* P644: the hoisted SKIP goes here, beside the button that replaces it.\n"
    u"     It lives outside .res-card now, so replacing that element's innerHTML no\n"
    u"     longer disposes of it and it would otherwise outlive the offer. This is\n"
    u"     the one place all four outcomes converge. */\n"
    u"  try{document.querySelectorAll('#end-ov>.fo-skip').forEach(function(e){e.remove();});}catch(e){}\n"
    u"  try{var eb=document.getElementById('end-btns');if(eb)eb.style.display='';}catch(e){}",
    'P644 tear it down at the one exit')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('\n%d edits' % n)
