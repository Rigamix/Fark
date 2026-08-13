# -*- coding: utf-8 -*-
"""P674: every dialogue speaks Raritas, from one declaration.

Denis: "use the raritas font (semi bold italic) I've added to the font folder.
Do this for all dialogues across the whole game (ideally it all points to one
font and ripples out efficiently)"

The folder (Art/Assets/Fonts/) holds Regular, Medium, Semi-Bold and Bold - no
italic file - so the face is Semi-Bold with font-style:italic, which the
browser synthesizes as an oblique. If a true italic arrives later, one src line
changes and every dialogue follows.

ONE VARIABLE, TWO CONSUMERS. --font-dlg sits beside --font-ui, and the two
surfaces that print SPOKEN lines point at it: the match bubble
(#screen-match .dlg-text, was JMH Beda) and the end-screen patron line
(.res-dlg .dlg-text, was IM Fell English - two different faces for the same
voice, which is exactly the drift Denis is closing). Card text, status lines
and UI stay JMH Beda: they are the game's hand, not a speaker's voice.

Also: the bubble example Denis sent sat on three lines where two fit. The
fitter already minimises lines - the cap was the box: .dlg-scroll's max-width
94% inside an inner box that reserves 100px for the portrait. The reserve is
real (the portrait is the speaker), so the win comes from the face change
itself - Raritas Semi-Bold sets narrower than JMH Beda at the same size -
plus a nudge of the cap. Measured after, not assumed.
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


# ── the face and the variable ───────────────────────────────────────────
sub(u"@font-face{font-family:'JMH Beda';src:url('assets/_mockups/new_main/JMH Beda.ttf') format('truetype')}",
    u"@font-face{font-family:'JMH Beda';src:url('assets/_mockups/new_main/JMH Beda.ttf') format('truetype')}\n"
    u"/* P674: the dialogue voice. Semi-Bold is the only weight Denis pointed at\n"
    u"   (no italic file exists in the folder), so italic is synthesized by the\n"
    u"   browser. Loaded from Art/Assets/Fonts/ where he put it. */\n"
    u"@font-face{font-family:'Raritas';src:url('Art/Assets/Fonts/fonnts.com-Raritas-Semi-Bold.otf') format('opentype');\n"
    u"  font-weight:600;font-display:swap}",
    'P674 the font face')

sub(u"  --font-ui:'JMH Beda',serif;",
    u"  --font-ui:'JMH Beda',serif;\n"
    u"  /* P674: ONE voice for every spoken line - the match bubble and the\n"
    u"     end-screen patron line both point here, so a future face change is one\n"
    u"     edit. Semi-bold italic per Denis. */\n"
    u"  --font-dlg:'Raritas','JMH Beda',serif;",
    'P674 the variable')

# ── the two spoken surfaces ─────────────────────────────────────────────
sub(u"#screen-match .dlg-text{font-family:'JMH Beda',serif;font-size:3.8cqw;",
    u"#screen-match .dlg-text{font-family:var(--font-dlg);font-style:italic;font-weight:600;font-size:3.8cqw;",
    'P674 the match bubble speaks it')

sub(u".res-dlg .dlg-text{position:relative;z-index:1;font-family:'IM Fell English',serif;",
    u"/* P674: same voice as the match bubble - it was IM Fell English, a second\n"
    u"   face for the same speaker */\n"
    u".res-dlg .dlg-text{position:relative;z-index:1;font-family:var(--font-dlg);font-style:italic;font-weight:600;",
    'P674 the end-screen line speaks it')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('\n%d edits' % n)
