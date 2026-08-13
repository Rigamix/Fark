# -*- coding: utf-8 -*-
"""P677: four tunings from Denis's screenshots.

1. FOCUS TIP - "less space between words, a bit more space between letters.
   Narrow the text box so it's not as wide. Saturate the title."
   The word gaps ARE the justification stretch: a 60cqw box leaves the lines
   short, so justify pads the spaces wide. Narrowing to 50cqw closes the gaps
   at the source; tracking rises a step; the title's mix drops most of its
   cream (55% accent -> 82%) toward a warm gold instead of a pale one, which
   is what washed the saturation out.

2. DIALOGUE - text a couple of pixels lower, more side margin, and the
   UPRIGHT Raritas to try ("just to see if it works better"). Padding moves
   top-heavy (25/19) to sink the text; sides 20 -> 26. The width the sides
   eat comes back at the cap (96% -> 99%) so the two-line fit survives -
   re-measured after, in the upright font, not assumed.

3. PAUSE - smaller (9.5 -> 8cqw) and on Denis's red line. The line, scaled
   off his crop against the ROLL plaque's known edge (21.1px, full-bleed art,
   measured alpha bbox), sits at ~33px = 7.7cqw.

4. TURN 1/10 - the word up (.72em -> .92em), the number down (1.34em ->
   1.14em), so the two read as one label rather than a caption under a score.
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


# ── 1. the focus tip ────────────────────────────────────────────────────
sub(u"#cardFocusTip{position:absolute;z-index:9001;pointer-events:none;\n"
    u"  /* P673: narrower, per Denis - the body justifies inside it */\n"
    u"  max-width:60cqw;width:60cqw;text-align:center}",
    u"#cardFocusTip{position:absolute;z-index:9001;pointer-events:none;\n"
    u"  /* P677: 60 -> 50cqw. The wide word gaps WERE this box: justify pads the\n"
    u"     spaces to fill whatever width it is given, so the narrower box closes\n"
    u"     the gaps at the source. */\n"
    u"  max-width:50cqw;width:50cqw;text-align:center}",
    'P677 narrower tip box')

sub(u"  color:color-mix(in srgb,var(--cft-a,#f0c860) 55%,#f7ecd2)}",
    u"  /* P677: saturate - 55% accent was a pale wash; 82% toward a warm gold\n"
    u"     keeps the chroma while still lifting off the dark wood */\n"
    u"  color:color-mix(in srgb,var(--cft-a,#f0c860) 82%,#ffdf9e)}",
    'P677 saturate the title')

sub(u"#cardFocusTip .cft-body{font-family:'JMH Beda',serif;font-size:3.5cqw;\n"
    u"  color:#f2e6c8;line-height:1.4;margin-top:1.1cqw;letter-spacing:.05em;\n"
    u"  text-align:justify;text-align-last:center}",
    u"#cardFocusTip .cft-body{font-family:'JMH Beda',serif;font-size:3.5cqw;\n"
    u"  color:#f2e6c8;line-height:1.4;margin-top:1.1cqw;letter-spacing:.075em;\n"
    u"  text-align:justify;text-align-last:center}",
    'P677 more tracking')

# ── 2. the dialogue ─────────────────────────────────────────────────────
sub(u"#screen-match .dlg-text{font-family:var(--font-dlg);font-style:italic;font-weight:600;font-size:3.8cqw;",
    u"/* P677: upright, to try - Denis: \"use the non italic version ... just to\n"
    u"   see if it works better\". One property back if it does not. */\n"
    u"#screen-match .dlg-text{font-family:var(--font-dlg);font-style:normal;font-weight:600;font-size:3.8cqw;",
    'P677 upright in the bubble')

sub(u".res-dlg .dlg-text{position:relative;z-index:1;font-family:var(--font-dlg);font-style:italic;font-weight:600;",
    u".res-dlg .dlg-text{position:relative;z-index:1;font-family:var(--font-dlg);font-style:normal;font-weight:600;",
    'P677 upright on the end screen')

sub(u"  box-shadow:none;padding:22px 20px;max-width:96%;margin:0 0 0 3cqw;flex:0 1 auto;",
    u"  /* P677: the text sinks a couple of pixels (25/19 top-heavy padding), the\n"
    u"     sides breathe (20 -> 26), and the width the sides eat comes back at the\n"
    u"     cap (96 -> 99%) so the two-line fit survives - re-measured upright. */\n"
    u"  box-shadow:none;padding:25px 26px 19px;max-width:99%;margin:0 0 0 3cqw;flex:0 1 auto;",
    'P677 bubble padding and cap')

# ── 3. the pause ────────────────────────────────────────────────────────
sub(u"  /* P675: the NEW icon's own ratio (92x94, full-bleed) - the old 129/150 box\n"
    u"     letterboxed a near-square image, which read as misalignment */\n"
    u"  width:9.5cqw;height:auto;aspect-ratio:92/94;z-index:21;cursor:pointer;transition:transform .1s}",
    u"  /* P675: the NEW icon's own ratio (92x94, full-bleed) - the old 129/150 box\n"
    u"     letterboxed a near-square image, which read as misalignment */\n"
    u"  /* P677: smaller, and on Denis's red line - scaled off his crop against the\n"
    u"     ROLL plaque's measured edge, the line sits at ~7.7cqw */\n"
    u"  width:8cqw;height:auto;aspect-ratio:92/94;z-index:21;cursor:pointer;transition:transform .1s}",
    'P677 pause smaller')

sub(u"#matchPause{position:absolute;left:4.92%;bottom:calc(32.5cqw + env(safe-area-inset-bottom,0px));top:auto;right:auto;",
    u"#matchPause{position:absolute;left:7.7cqw;bottom:calc(32.5cqw + env(safe-area-inset-bottom,0px));top:auto;right:auto;",
    'P677 pause on the line')

# ── 4. the turn label ───────────────────────────────────────────────────
sub(u"#screen-match #turnNum .tn-w{font-size:.72em;letter-spacing:.11em;color:#a89070;/* P589 *//* P579: bigger */",
    u"/* P677: word up, number down - the two read as one label now */\n"
    u"#screen-match #turnNum .tn-w{font-size:.92em;letter-spacing:.11em;color:#a89070;/* P589 *//* P579: bigger */",
    'P677 TURN bigger')

sub(u"#screen-match #turnNum .tn-n{font-size:1.34em;letter-spacing:.02em;",
    u"#screen-match #turnNum .tn-n{font-size:1.14em;letter-spacing:.02em;",
    'P677 number smaller')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('\n%d edits' % n)
