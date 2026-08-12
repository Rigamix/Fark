# -*- coding: utf-8 -*-
"""P654: the shadow really darkens the table now, and the tracking opens up.

── WHY THE MULTIPLY DID NOTHING ──
Denis: "shadow is not dark nor multiplied." He is right, and the reason is
structural rather than a wrong colour.

mix-blend-mode blends an element with its BACKDROP, and the backdrop stops at
the nearest stacking context. Walked from the shadow path outward
(tools/apv_bubble_shadow.js), there are two before the table:
    svg.dlg-bubble        position:absolute + z-index:0
    div#dlgBox            position:fixed + z-index:90
So the shadow could only ever see what was painted inside the SVG below it -
which is nothing, because it is the first child. Multiply against an empty
backdrop returns the source colour untouched, so it rendered as flat #7a5a3c: a
mid-brown that is LIGHTER than the table in places. Exactly "not dark nor
multiplied".

AND IT IS NOT FIXABLE BY MOVING THE ISOLATION. #dlgBox has to paint above the
table, which needs z-index on a positioned element, which IS a stacking context.
Any element that sits above the table is cut off from blending with it.

── WHAT REACHES THROUGH INSTEAD ──
backdrop-filter. It filters the pixels actually behind the element rather than
compositing a colour onto them, and it is NOT stopped by stacking contexts - it
stops only at a backdrop root (a filter, an opacity below 1, a mask), and there
is none between here and the table.

So the shadow becomes a plain div clipped to the bubble's own outline with
clip-path:path() - the same path string the SVG is already built from, in the
same coordinate space, so there is no second shape to keep in sync - offset, and
darkening what is under it. That is what multiply was supposed to look like, by
a route that works from inside a stacking context.

ONE HONEST LIMIT: .dlg-box fades in on opacity, and an opacity below 1 IS a
backdrop root. So for the half second of the fade the shadow darkens only what
is inside the box - which is nothing - and it lands properly once the fade
settles. Visible as the shadow arriving a beat after the bubble.

── TRACKING ──
Denis: "More space between letters please." Measured over the FULL corpus, all
1075 lines, at the shipped 3.8cqw and 356px:
    0.2px   worst 3 lines,  0 of 1075 over three
    0.4px   worst 4 lines,  1 of 1075 over three
    0.6px   worst 4 lines,  1 of 1075
    0.8px   worst 4 lines,  1 of 1075
The cost does not grow between 0.4 and 0.8 - it is the same single outlier line
throughout - so the generous end of that range is free relative to the cheap
end. 0.6px, three times what P652 shipped, for one line in a thousand.
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


# ── 1. tracking ──────────────────────────────────────────────────────────
sub(u"  line-height:1.3;letter-spacing:.2px;word-spacing:0}",
    u"  /* P654: .2px -> .6px. Measured over all 1075 lines: 0.2 costs nothing,\n"
    u"     and 0.4, 0.6 and 0.8 all cost the SAME single line - so the top of that\n"
    u"     range is free relative to the bottom of it. Word-spacing stays at 0. */\n"
    u"  line-height:1.3;letter-spacing:.6px;word-spacing:0}",
    'P654 more tracking')

# ── 2. the shadow stops pretending to multiply ───────────────────────────
sub(u"  /* P652: THE CAST SHADOW, and it MULTIPLIES. It was a flat\n"
    u"     drop-shadow(2px 4px 0 rgba(38,22,12,.85)) - a near-black wash sitting ON\n"
    u"     the table rather than darkening it, identical over bare wood, a coin or a\n"
    u"     card. A filter cannot blend, so this is a third copy of the path, offset\n"
    u"     and multiplied. Mid-brown on purpose: multiply already darkens, so a dark\n"
    u"     colour here goes to near-black and loses the wood grain underneath. */\n"
    u"  shadowColor: '#7a5a3c', shadowDX: 2, shadowDY: 4",
    u"  /* P654: THE CAST SHADOW DARKENS WHAT IS UNDER IT, which is what P652's\n"
    u"     multiply was trying to do and could not. mix-blend-mode stops at the\n"
    u"     nearest stacking context, and there are two between this and the table\n"
    u"     (the SVG's own z-index, and #dlgBox's) - so multiply saw an empty\n"
    u"     backdrop and returned its own colour, rendering as a flat mid-brown.\n"
    u"     backdrop-filter reads through instead: it filters the pixels actually\n"
    u"     behind the element and is stopped only by a backdrop root. shadowDarken\n"
    u"     is the brightness multiplier applied to the table beneath the shape. */\n"
    u"  shadowDarken: 0.52, shadowSat: 1.15, shadowDX: 3, shadowDY: 5",
    'P654 the shadow knobs become a darkening')

sub(u"    /* THE CAST SHADOW FIRST, and OUTSIDE the isolation group below - it has to\n"
    u"       multiply against the table, not against the paper. */\n"
    u"    + '<path d=\"' + pathD + '\" fill=\"' + o.shadowColor + '\" stroke=\"none\"'\n"
    u"      + ' transform=\"translate(' + o.shadowDX + ',' + o.shadowDY + ')\"'\n"
    u"      + ' style=\"mix-blend-mode:multiply\" filter=\"url(#gr-' + uid + ')\"/>'\n",
    u"",
    'P654 drop the multiply path')

sub(u"  var old = scrollEl.querySelector('svg.dlg-bubble');\n"
    u"  if (old) old.remove();\n"
    u"  scrollEl.insertAdjacentHTML('afterbegin', svg);",
    u"  /* THE CAST SHADOW, as a plain div clipped to the bubble's own outline.\n"
    u"     clip-path takes the SAME path string the SVG is built from, in the same\n"
    u"     coordinate space, so there is no second shape to keep in sync - move the\n"
    u"     bubble and the shadow moves with it by construction.\n"
    u"     It is a div and not another SVG path because what it does is\n"
    u"     backdrop-filter: darkening the table's real pixels rather than laying a\n"
    u"     colour over them. See the note in DLG_BUBBLE for why blending could not. */\n"
    u"  var shadow = '<div class=\"dlg-bubble-shadow\" aria-hidden=\"true\" style=\"'\n"
    u"    + 'left:' + (-offX + o.shadowDX).toFixed(1) + 'px;top:' + (-offY + o.shadowDY).toFixed(1) + 'px;'\n"
    u"    + 'width:' + svgW.toFixed(1) + 'px;height:' + svgH.toFixed(1) + 'px;'\n"
    u"    + 'clip-path:path(\\'' + pathD + '\\');-webkit-clip-path:path(\\'' + pathD + '\\')\"></div>';\n"
    u"  var old = scrollEl.querySelector('svg.dlg-bubble');\n"
    u"  if (old) old.remove();\n"
    u"  var oldSh = scrollEl.querySelector('.dlg-bubble-shadow');\n"
    u"  if (oldSh) oldSh.remove();\n"
    u"  scrollEl.insertAdjacentHTML('afterbegin', svg);\n"
    u"  scrollEl.insertAdjacentHTML('afterbegin', shadow);",
    'P654 emit the darkening shadow')

sub(u"/* the flat drop-shadow the multiply layer replaces. Scoped off here rather\n"
    u"   than deleted from .dlg-scroll, which #resDlg and the shop bubble share. */\n"
    u"#screen-match .dlg-scroll{filter:none}",
    u"/* the flat drop-shadow the darkening layer replaces. Scoped off here rather\n"
    u"   than deleted from .dlg-scroll, which #resDlg and the shop bubble share.\n"
    u"   IT ALSO HAS TO GO FOR THE SHADOW TO WORK AT ALL: a filter on an ancestor\n"
    u"   is a backdrop root, and backdrop-filter cannot see past one. */\n"
    u"#screen-match .dlg-scroll{filter:none}\n"
    u"/* P654: THE CAST SHADOW. Not a colour laid over the table - a darkening OF\n"
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
    'P654 the shadow CSS')

# the darkening knobs reach the CSS through variables on the element
sub(u"  var shadow = '<div class=\"dlg-bubble-shadow\" aria-hidden=\"true\" style=\"'\n",
    u"  var shadow = '<div class=\"dlg-bubble-shadow\" aria-hidden=\"true\" style=\"'\n"
    u"    + '--sh-dark:' + o.shadowDarken + ';--sh-sat:' + o.shadowSat + ';'\n",
    'P654 pass the knobs through')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('\n%d edits' % n)
