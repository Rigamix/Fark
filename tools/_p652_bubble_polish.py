# -*- coding: utf-8 -*-
"""P652: a touch of tracking back, text darker than its accent, shadow in multiply.

── TRACKING, AND IT IS A BUDGET ──
Denis: "give a touch more spacing between letters."

P651 spent the tracking to buy the font step, so putting it back costs line
count. Measured at the shipped 3.8cqw across the 40 longest of 1075 lines:
    0px     worst 3 lines, 0 over
    0.2px   worst 3 lines, 0 over
    0.35px  worst 4 lines, 1 over
    0.5px   worst 4 lines, 1 over
0.2px is the whole budget, and it is what ships.

── TEXT DARKER THAN ITS ACCENT ──
Denis, as a standing rule: "When you pick a color for text, always make it a bit
darker than the color accent you chose."

The bubble prints in var(--patCol), the speaker's accent, AT that accent. It is
now that accent mixed 78/22 with a near-black brown, so it stays recognisably
the patron's colour while sitting a step below it - which is also what makes it
legible against parchment rather than glowing on it.

color-mix does this without knowing what --patCol holds, which matters because
it is a different value per patron and there is nowhere to hand-darken 29 of
them. The plain declaration is left above it as the fallback: anything that does
not understand color-mix keeps exactly today's colour rather than losing the
rule entirely.

── THE SHADOW MULTIPLIES ──
Denis: "The bubble's shadow should be in multiply mode rather than just half
transparent brown."

It was `filter:drop-shadow(2px 4px 0 rgba(38,22,12,.85))` on .dlg-scroll - a flat
near-black wash that sits ON the table rather than darkening it, so it reads the
same over bare wood as over a coin or a card.

A filter cannot blend, so the shadow becomes a third copy of the bubble path,
offset, solid-filled and mix-blend-mode:multiply.

AND THE ISOLATION HAD TO MOVE FOR IT TO WORK, which is the part worth writing
down. P649 put isolation:isolate on the SVG so the light layer would tint the
parchment underneath instead of the page. That same group would have trapped the
shadow, which needs to multiply against the TABLE. So the isolation moves off
the root and onto an inner <g> holding just the parchment and the light: the
shadow is a sibling outside it and blends with the room, the light is inside it
and blends with the paper. Two blend targets, two scopes.
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


# ── 1. the tracking budget, and the darker ink ───────────────────────────
sub(u"#screen-match .dlg-text{font-family:'JMH Beda',serif;font-size:3.8cqw;\n"
    u"  color:var(--patCol,#3a2812);line-height:1.3;letter-spacing:0;word-spacing:0}",
    u"/* P652: 0.2px of tracking back, and that is the WHOLE budget - measured at\n"
    u"   3.8cqw across the 40 longest of 1075 lines, 0.2 holds three lines and 0.35\n"
    u"   tips one to four. Word-spacing stays at 0; it was the expensive one.\n"
    u"   AND THE INK IS A STEP BELOW THE ACCENT, per Denis's standing rule that text\n"
    u"   should always be a little darker than the accent it is drawn from. This\n"
    u"   prints in the speaker's own --patCol, so it is that colour mixed 78/22 with\n"
    u"   a near-black brown: still recognisably theirs, but sitting under the accent\n"
    u"   rather than glowing at it on parchment. color-mix because --patCol is a\n"
    u"   different value per patron and there is nowhere to hand-darken 29 of them.\n"
    u"   The plain declaration stays above as the fallback, so anything that does\n"
    u"   not understand color-mix keeps today's colour rather than losing the rule. */\n"
    u"#screen-match .dlg-text{font-family:'JMH Beda',serif;font-size:3.8cqw;\n"
    u"  color:var(--patCol,#3a2812);\n"
    u"  color:color-mix(in srgb, var(--patCol,#3a2812) 78%, #14100a);\n"
    u"  line-height:1.3;letter-spacing:.2px;word-spacing:0}",
    'P652 tracking + darker ink')

# ── 2. the isolation moves off the root so a shadow can multiply ─────────
sub(u"/* behind the text, and allowed out of the box: the tail lives out here.\n"
    u"   isolation:isolate because the light layer is mix-blend-mode:overlay - the\n"
    u"   brief wants it tinting the PARCHMENT PATH under it, and without an\n"
    u"   isolation group it blends against whatever is behind the whole SVG. */\n"
    u"#screen-match .dlg-scroll svg.dlg-bubble{position:absolute;z-index:0;\n"
    u"  pointer-events:none;overflow:visible;isolation:isolate}",
    u"/* behind the text, and allowed out of the box: the tail lives out here.\n"
    u"   P652: THE ISOLATION IS NOT HERE ANY MORE. P649 put it on the root so the\n"
    u"   light layer would tint the parchment rather than the page - correct then,\n"
    u"   and it would trap the drop shadow now, which has to multiply against the\n"
    u"   TABLE. It lives on an inner <g> holding the parchment and the light; the\n"
    u"   shadow is a sibling outside it. Two blend targets, two scopes. */\n"
    u"#screen-match .dlg-scroll svg.dlg-bubble{position:absolute;z-index:0;\n"
    u"  pointer-events:none;overflow:visible}\n"
    u"/* the flat drop-shadow the multiply layer replaces. Scoped off here rather\n"
    u"   than deleted from .dlg-scroll, which #resDlg and the shop bubble share. */\n"
    u"#screen-match .dlg-scroll{filter:none}",
    'P652 move the isolation off the root')

# ── 3. the shadow itself ─────────────────────────────────────────────────
sub(u"  /* the brief's corrected stops - beige and dark brown, NOT white and black */\n"
    u"  lightStop: '#d9bd90', shadowStop: '#4a2f18', ink: '#1c140c'\n"
    u"};",
    u"  /* the brief's corrected stops - beige and dark brown, NOT white and black */\n"
    u"  lightStop: '#d9bd90', shadowStop: '#4a2f18', ink: '#1c140c',\n"
    u"  /* P652: THE CAST SHADOW, and it MULTIPLIES. It was a flat\n"
    u"     drop-shadow(2px 4px 0 rgba(38,22,12,.85)) - a near-black wash sitting ON\n"
    u"     the table rather than darkening it, identical over bare wood, a coin or a\n"
    u"     card. A filter cannot blend, so this is a third copy of the path, offset\n"
    u"     and multiplied. Mid-brown on purpose: multiply already darkens, so a dark\n"
    u"     colour here goes to near-black and loses the wood grain underneath. */\n"
    u"  shadowColor: '#7a5a3c', shadowDX: 2, shadowDY: 4\n"
    u"};",
    'P652 the shadow knobs')

sub(u"    + '</defs>'\n"
    u"    /* the parchment, then a SECOND copy of the same path carrying the light as\n"
    u"       a blended tint - the brief is specific that the lighting is a layer over\n"
    u"       the real texture, not baked into it */\n"
    u"    + '<path d=\"' + pathD + '\" fill=\"url(#par-' + uid + ')\" stroke=\"' + o.ink + '\" stroke-width=\"' + o.strokeW + '\" stroke-linejoin=\"round\" stroke-linecap=\"round\" filter=\"url(#gr-' + uid + ')\"/>'\n"
    u"    + '<path d=\"' + pathD + '\" fill=\"url(#li-' + uid + ')\" stroke=\"none\" style=\"mix-blend-mode:' + o.lightBlend + '\" filter=\"url(#gr-' + uid + ')\"/>'\n"
    u"    + '</svg>';",
    u"    + '</defs>'\n"
    u"    /* THE CAST SHADOW FIRST, and OUTSIDE the isolation group below - it has to\n"
    u"       multiply against the table, not against the paper. */\n"
    u"    + '<path d=\"' + pathD + '\" fill=\"' + o.shadowColor + '\" stroke=\"none\"'\n"
    u"      + ' transform=\"translate(' + o.shadowDX + ',' + o.shadowDY + ')\"'\n"
    u"      + ' style=\"mix-blend-mode:multiply\" filter=\"url(#gr-' + uid + ')\"/>'\n"
    u"    /* the parchment, then a SECOND copy of the same path carrying the light as\n"
    u"       a blended tint - the brief is specific that the lighting is a layer over\n"
    u"       the real texture, not baked into it. ISOLATED TOGETHER so the overlay\n"
    u"       tints the paper and nothing further back. */\n"
    u"    + '<g style=\"isolation:isolate\">'\n"
    u"    + '<path d=\"' + pathD + '\" fill=\"url(#par-' + uid + ')\" stroke=\"' + o.ink + '\" stroke-width=\"' + o.strokeW + '\" stroke-linejoin=\"round\" stroke-linecap=\"round\" filter=\"url(#gr-' + uid + ')\"/>'\n"
    u"    + '<path d=\"' + pathD + '\" fill=\"url(#li-' + uid + ')\" stroke=\"none\" style=\"mix-blend-mode:' + o.lightBlend + '\" filter=\"url(#gr-' + uid + ')\"/>'\n"
    u"    + '</g>'\n"
    u"    + '</svg>';",
    'P652 the multiply shadow path')

# the SVG box has to hold the offset shadow, or it clips
sub(u"  var margin = o.strokeW + 4;",
    u"  /* P652: the offset shadow has to fit inside the box too, or it clips at the\n"
    u"     bottom-right exactly where it is most visible. */\n"
    u"  var margin = o.strokeW + 4 + Math.max(o.shadowDX, o.shadowDY);",
    'P652 room for the shadow')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('\n%d edits' % n)
