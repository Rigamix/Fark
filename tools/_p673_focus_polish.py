# -*- coding: utf-8 -*-
"""P673: the card focus per Denis's notes, and the tier badge back on top.

Denis: "make the title smaller (and don't write the level number next to it, as
I said before we already have the badge on the card to tell us that), try to
narrow the text box a bit (like, justified both sides) and space out letters a
bit. Don't add text shadow, just ensure the colors contrast with the table
color enough. Don't write 'drag past the line to play'"
And: "the level badge appears to be under the card and not above (which I guess
happens because of the scale effect), fix that"

THE BADGE IS NOT THE SCALE'S FAULT - it is P670's. The cover-face fix gave
.fcvIn img z-index:1 so art paints over the CARD_BG cover; .fcvTier and
.fcvBadge are absolute with NO z-index, and a stacked z-index:1 beats their
auto - so the art started painting over the tier pip on every card, focus or
not. The pip and badge get z-index:2, above the art they were always meant to
sit on.

THE TITLE: down a step, numeral gone (the card's own pip carries the tier -
Denis has now said this twice, so the numeral dies at both call sites).

THE TEXT: narrower and justified both sides with a touch of tracking. The last
line centres rather than stretching - a justified final line of two words is a
chasm. No text-shadow anywhere in the tip; contrast comes from the colours:
body cream on the dark wood, title the family accent LIFTED toward cream -
lifted, not darkened, because the ground here is the near-black table and it is
contrast against THAT which Denis asked for. (The darker-than-accent rule
serves reading text against light grounds; on this ground the mix direction
inverts or the title vanishes.)
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


# ── the badge back on top ───────────────────────────────────────────────
sub(u".fcv .fcvTier{position:absolute;right:-2%;top:-1.5%;min-width:13%;box-sizing:border-box;text-align:center;",
    u"/* P673: z-index 2 because P670 gave .fcvIn img z-index:1 (art over the\n"
    u"   CARD_BG cover) - which silently put the art over this pip too. */\n"
    u".fcv .fcvTier{position:absolute;right:-2%;top:-1.5%;min-width:13%;box-sizing:border-box;text-align:center;z-index:2;",
    'P673 tier pip above the art')

sub(u".fcv .fcvBadge{position:absolute;left:5%;top:3.5%;font-size:min(1.6cqh,10px);letter-spacing:.08em;",
    u".fcv .fcvBadge{position:absolute;left:5%;top:3.5%;font-size:min(1.6cqh,10px);letter-spacing:.08em;z-index:2;",
    'P673 badge above the art')

# ── the title: smaller, no numeral ──────────────────────────────────────
sub(u"  _cardFocusToggle(document.querySelectorAll('#famRowP .fcv')[i],{\n"
    u"    title:d.name.toUpperCase()+(inst.tier>1?' '+['','II','III'][inst.tier-1]:''),\n"
    u"    sub:sub,body:d.text[inst.tier-1],col:col});",
    u"  _cardFocusToggle(document.querySelectorAll('#famRowP .fcv')[i],{\n"
    u"    title:d.name.toUpperCase(),/* P673: the card's own pip carries the tier */\n"
    u"    sub:sub,body:d.text[inst.tier-1],col:col});",
    'P673 player title plain')

sub(u"  _cardFocusToggle(document.querySelectorAll('#famRowO .fcv')[i],{\n"
    u"    title:d.name.toUpperCase()+(inst.tier>1?' '+['','II','III'][inst.tier-1]:''),",
    u"  _cardFocusToggle(document.querySelectorAll('#famRowO .fcv')[i],{\n"
    u"    title:d.name.toUpperCase(),/* P673: no numeral - the pip says it */",
    'P673 rival title plain')

# ── the teaching line goes ──────────────────────────────────────────────
sub(u"  var sub=(d.kind==='active'?(inst.charges>0?'uses left: '+inst.charges+' — drag past the line to play'\n"
    u"                                            :'spent for this match'):'passive — always on');",
    u"  /* P673: no 'drag past the line' teach-line, per Denis */\n"
    u"  var sub=(d.kind==='active'?(inst.charges>0?'uses left: '+inst.charges\n"
    u"                                            :'spent for this match'):'passive — always on');",
    'P673 drop the teach-line')

# ── the tip: smaller title, narrow justified body, no shadow ────────────
sub(u"#cardFocusTip{position:absolute;z-index:9001;pointer-events:none;\n"
    u"  max-width:74cqw;text-align:center}\n"
    u"#cardFocusTip .cft-name{font-family:'JMH Beda',serif;font-size:5cqw;\n"
    u"  letter-spacing:.04em;\n"
    u"  /* the title prints two steps darker than the family accent it is handed -\n"
    u"     never AT the accent (the standing rule) */\n"
    u"  color:color-mix(in srgb,var(--cft-a,#f0c860) 80%,#140c04)}\n"
    u"#cardFocusTip .cft-sub{font-family:'JMH Beda',serif;font-size:2.9cqw;\n"
    u"  color:#c9b490;opacity:.9;margin-top:0.4cqw}\n"
    u"#cardFocusTip .cft-body{font-family:'JMH Beda',serif;font-size:3.7cqw;\n"
    u"  color:#efe2c4;line-height:1.35;margin-top:1.2cqw}\n"
    u"#cardFocusTip .cft-name,#cardFocusTip .cft-sub,#cardFocusTip .cft-body{\n"
    u"  text-shadow:0 1px 0 rgba(20,12,4,.85),0 0 6px rgba(20,12,4,.7)}",
    u"#cardFocusTip{position:absolute;z-index:9001;pointer-events:none;\n"
    u"  /* P673: narrower, per Denis - the body justifies inside it */\n"
    u"  max-width:60cqw;width:60cqw;text-align:center}\n"
    u"#cardFocusTip .cft-name{font-family:'JMH Beda',serif;font-size:3.9cqw;\n"
    u"  letter-spacing:.09em;\n"
    u"  /* P673: LIFTED toward cream, not darkened - the ground is the near-black\n"
    u"     table and Denis asked for contrast against THAT, with no text-shadow\n"
    u"     doing the work. (Darker-than-accent serves light grounds; here the mix\n"
    u"     direction inverts or a dark family's title vanishes into the wood.) */\n"
    u"  color:color-mix(in srgb,var(--cft-a,#f0c860) 55%,#f7ecd2)}\n"
    u"#cardFocusTip .cft-sub{font-family:'JMH Beda',serif;font-size:2.7cqw;\n"
    u"  color:#c9b490;opacity:.9;margin-top:0.4cqw;letter-spacing:.06em}\n"
    u"/* P673: justified both sides with a touch of tracking; the LAST line\n"
    u"   centres because a justified final line of two words is a chasm */\n"
    u"#cardFocusTip .cft-body{font-family:'JMH Beda',serif;font-size:3.5cqw;\n"
    u"  color:#f2e6c8;line-height:1.4;margin-top:1.1cqw;letter-spacing:.05em;\n"
    u"  text-align:justify;text-align-last:center}",
    'P673 the tip restyle')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('\n%d edits' % n)
