# -*- coding: utf-8 -*-
"""P660: the bubble grows from the speaker's side, sits left, sizes consistently,
and loses its shadow.

Denis: "make the text bubble scale up from the side of the patron portrait rather
than a fade. Ensure it's always lined up to the left which is patron portrait
side, so that the tail always points at it since they're the ones speaking.
There is inconsistency in the parchment box sizing: sometimes the same amount of
text sits in a wide box with lots of side paddings, sometimes it narrower which
is more correct. Remove the dialogue box shadow altogether"

── IT GROWS OUT OF THE CORNER THE TAIL IS ON ──
The box faded in on opacity alone. It now scales from transform-origin at its
top-left, which is where tailPos 0.99 puts the tail - so the bubble appears to
come out of the speaker rather than materialise over the table. The opacity fade
stays underneath it; what changed is that something moves.

── AND IT SITS LEFT ──
#screen-match .dlg-scroll carried margin:0 auto, so a narrow bubble centred over
the table and its tail pointed at nothing. The patron's portrait is the HUD's
top-left avatar - the match screen hides .dlg-portrait, so that IS the speaker's
side - and the box now starts there. .dlg-inner was already
justify-content:flex-start; only the auto margin was fighting it.

── THE WIDTH WOBBLE HAS A CAUSE ──
"sometimes the same amount of text sits in a wide box with lots of side padding,
sometimes it narrower which is more correct." The narrow one is the search
working. The wide one is the search being unable to reach: it started at
lo = max(60, maxW * 0.3), which at the shipped 349px cap is 105px - so any
message whose tightest honest width is under 105px stopped there and kept the
slack as padding. Short two-line lines are exactly that case. lo drops to 12%.

── NO SHADOW ──
The backdrop-filter darkening P654 built goes. Denis asked for a multiply
instead of a flat wash, got one, and has now decided the bubble is better with
nothing under it at all - so the element, its CSS and its knobs are removed
rather than left switched off.
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


# ── 1. left, and growing from the tail's corner ──────────────────────────
sub(u"  box-shadow:none;padding:22px 24px;max-width:94%;margin:0 auto;flex:0 1 auto}",
    u"  /* P660: LEFT, not centred. margin:0 auto put a narrow bubble in the middle\n"
    u"     of the table with its tail pointing at nothing. The speaker's portrait is\n"
    u"     the HUD's top-left avatar - this screen hides .dlg-portrait, so that IS\n"
    u"     their side - and tailPos 0.99 puts the tail on the top-left corner, so\n"
    u"     the box starts there and the tail points at them. .dlg-inner was already\n"
    u"     justify-content:flex-start; the auto margin was fighting it. */\n"
    u"  box-shadow:none;padding:22px 24px;max-width:94%;margin:0 0 0 3cqw;flex:0 1 auto;\n"
    u"  /* and it GROWS from that corner rather than fading in place */\n"
    u"  transform-origin:0% 0%}",
    'P660 left-aligned, origin on the tail')

sub(u".dlg-box.show{opacity:1}",
    u"/* P660: SCALES UP FROM THE SPEAKER'S SIDE. Denis: \"scale up from the side of\n"
    u"   the patron portrait rather than a fade\". The origin is the bubble's own\n"
    u"   top-left - the corner the tail is on - so it reads as coming out of them.\n"
    u"   The opacity fade stays underneath; what changed is that something moves. */\n"
    u"#screen-match .dlg-scroll{scale:.72;transition:scale .34s cubic-bezier(.2,1.3,.35,1),opacity .3s ease}\n"
    u"#screen-match .dlg-box.show .dlg-scroll{scale:1}\n"
    u".dlg-box.show{opacity:1}",
    'P660 scale in')

# ── 2. the search can reach a narrow box ─────────────────────────────────
sub(u"  var lo = Math.max(60, maxW * 0.3), hi = maxW;",
    u"  /* P660: 0.3 -> 0.12. The floor was the width wobble Denis is describing: at\n"
    u"     the shipped 349px cap, lo started at 105px, so any line whose tightest\n"
    u"     honest width was under that stopped at the floor and kept the slack as\n"
    u"     side padding. Short two-line messages are exactly that case. */\n"
    u"  var lo = Math.max(60, maxW * 0.12), hi = maxW;",
    'P660 let the search reach narrow')

# ── 3. the shadow goes ───────────────────────────────────────────────────
sub(u"  /* P654: THE CAST SHADOW DARKENS WHAT IS UNDER IT, which is what P652's\n"
    u"     multiply was trying to do and could not. mix-blend-mode stops at the\n"
    u"     nearest stacking context, and there are two between this and the table\n"
    u"     (the SVG's own z-index, and #dlgBox's) - so multiply saw an empty\n"
    u"     backdrop and returned its own colour, rendering as a flat mid-brown.\n"
    u"     backdrop-filter reads through instead: it filters the pixels actually\n"
    u"     behind the element and is stopped only by a backdrop root. shadowDarken\n"
    u"     is the brightness multiplier applied to the table beneath the shape. */\n"
    u"  shadowDarken: 0.52, shadowSat: 1.15, shadowDX: 3, shadowDY: 5\n"
    u"};",
    u"  /* P660: no cast shadow. P652 tried multiply and it could not reach the table\n"
    u"     through two stacking contexts; P654 got there with backdrop-filter; Denis\n"
    u"     then decided the bubble reads better with nothing under it. The knobs are\n"
    u"     removed rather than zeroed - a switched-off feature is a thing the next\n"
    u"     reader has to work out the state of. */\n"
    u"  _noShadow: true\n"
    u"};",
    'P660 drop the shadow knobs')

sub(u"  /* THE CAST SHADOW, as a plain div clipped to the bubble's own outline.\n"
    u"     clip-path takes the SAME path string the SVG is built from, in the same\n"
    u"     coordinate space, so there is no second shape to keep in sync - move the\n"
    u"     bubble and the shadow moves with it by construction.\n"
    u"     It is a div and not another SVG path because what it does is\n"
    u"     backdrop-filter: darkening the table's real pixels rather than laying a\n"
    u"     colour over them. See the note in DLG_BUBBLE for why blending could not. */\n"
    u"  var shadow = '<div class=\"dlg-bubble-shadow\" aria-hidden=\"true\" style=\"'\n"
    u"    + '--sh-dark:' + o.shadowDarken + ';--sh-sat:' + o.shadowSat + ';'\n"
    u"    + 'left:' + (-offX + o.shadowDX).toFixed(1) + 'px;top:' + (-offY + o.shadowDY).toFixed(1) + 'px;'\n"
    u"    + 'width:' + svgW.toFixed(1) + 'px;height:' + svgH.toFixed(1) + 'px;'\n"
    u"    + 'clip-path:path(\\'' + pathD + '\\');-webkit-clip-path:path(\\'' + pathD + '\\')\"></div>';\n"
    u"  var old = scrollEl.querySelector('svg.dlg-bubble');\n"
    u"  if (old) old.remove();\n"
    u"  var oldSh = scrollEl.querySelector('.dlg-bubble-shadow');\n"
    u"  if (oldSh) oldSh.remove();\n"
    u"  scrollEl.insertAdjacentHTML('afterbegin', svg);\n"
    u"  scrollEl.insertAdjacentHTML('afterbegin', shadow);",
    u"  var old = scrollEl.querySelector('svg.dlg-bubble');\n"
    u"  if (old) old.remove();\n"
    u"  /* P660: and any shadow left over from a build that had one */\n"
    u"  var oldSh = scrollEl.querySelector('.dlg-bubble-shadow');\n"
    u"  if (oldSh) oldSh.remove();\n"
    u"  scrollEl.insertAdjacentHTML('afterbegin', svg);",
    'P660 stop emitting the shadow')

sub(u"/* P654: THE CAST SHADOW. Not a colour laid over the table - a darkening OF\n"
    u"   the table, clipped to the bubble's outline, which is what Denis's \"multiply\n"
    u"   rather than half transparent brown\" describes. mix-blend-mode could not do\n"
    u"   it from in here: it stops at the nearest stacking context and #dlgBox is\n"
    u"   one. backdrop-filter reads through them.\n"
    u"   ONE LIMIT WORTH KNOWING: .dlg-box fades in on opacity, and an opacity below\n"
    u"   1 IS a backdrop root - so for the half second of the fade this darkens\n"
    u"   nothing, and lands as the fade settles. */\n"
    u"#screen-match .dlg-scroll .dlg-bubble-shadow{position:absolute;pointer-events:none;\n"
    u"  -webkit-backdrop-filter:brightness(var(--sh-dark,.52)) saturate(var(--sh-sat,1.15));\n"
    u"  backdrop-filter:brightness(var(--sh-dark,.52)) saturate(var(--sh-sat,1.15))}",
    u"/* P660: the cast shadow is gone entirely - see the note in DLG_BUBBLE. */",
    'P660 drop the shadow CSS')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('\n%d edits' % n)
