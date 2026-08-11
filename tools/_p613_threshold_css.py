# -*- coding: utf-8 -*-
"""P613: the look of the threshold - arm glow, fire beat, and the zone stops painting.

THE GLOW IS THE ONLY SIGN THE LINE EXISTS, so it has to read instantly and it
has to read as CARD-ARMED and not as anything else on this table. Ward's armed
die and the enchant faces already pulse; those are DICE and they breathe slowly.
This is a card, it is a hard gold rim plus bloom, and it does NOT pulse - it
snaps on at the crossing and holds. A steady state for "you are above the line",
a moving one for "this die is enchanted": different element, different behaviour,
so the two cannot be read for each other.

--card-arm-lift is a TUNING KNOB and is deliberately one number in one place.
The brief is explicit that the distance wants real hands: too close and cards
fire by accident, too far and the gesture feels dead. 16cqw is a starting value
measured against the row, not a guess at a pixel count - at the 430px design
width it puts the line ~69px above the card row's top, which is about three
quarters of a card height of deliberate travel.
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


# 1. the knob, beside the other match-layout constants
sub(u"  --dice-min-clearance: 36px;",
    u"  /* P613: how far above the player's card row the invisible activation\n"
    u"     threshold sits. THE ONE KNOB for the whole gesture - see _cardThresholdY.\n"
    u"     cqw so it scales with the row it is measured from. The brief asks for\n"
    u"     this to be tuned by hand: raise it if cards fire by accident, lower it\n"
    u"     if the drag feels unresponsive. */\n"
    u"  --card-arm-lift: 16cqw;\n"
    u"  --dice-min-clearance: 36px;",
    'P613 --card-arm-lift')

# 2. the zone stops being drawn and stops being a target
# anchored with its surrounding newlines: ".activate-zone{" alone matches three
# times (a #screen-match override and a media query carry the same substring).
sub(u"\n.activate-zone{\n",
    u"/* P613: RETIRED. The threshold replaced it - there is no drop target to aim\n"
    u"   at any more, and nothing adds .dragging-active. Its RESERVED SPACE is a\n"
    u"   different matter and is deliberately kept: --activate-zone-h and\n"
    u"   --dice-reserve-gap now set where the dice block sits, which Denis tuned to\n"
    u"   his mark in P610, and reclaiming the 76px here would drop the dice ~56px\n"
    u"   and undo it. The rules below are inert; the display:none is what matters. */\n"
    u"\n.activate-zone{display:none!important}\n"
    u".activate-zone_retired{\n",
    'P613 zone retired')

# 3. armed / fired / spent-cut
sub(u"/* Yield — matches activate-zone exactly */",
    u"/* ═══ P613: THE THRESHOLD'S ONLY VISIBLE SIGN ═══\n"
    u"   Snaps on when the card crosses the line and holds while it is above it.\n"
    u"   Deliberately NOT a pulse: the dice already use slow breathing glows for\n"
    u"   Ward and the enchant faces, and a player should never have to work out\n"
    u"   whether a moving light means \"this die is warded\" or \"this card will\n"
    u"   fire\". Steady = a state you are holding; moving = a property of a die. */\n"
    u".mcard.armed{\n"
    u"  filter:drop-shadow(0 0 0.9cqw rgba(255,214,120,.95))\n"
    u"         drop-shadow(0 0 2.6cqw rgba(255,180,60,.55))\n"
    u"         brightness(1.14) saturate(1.12);\n"
    u"  transition:filter .12s ease-out}\n"
    u".mcard.armed .gcard{outline:0.22cqw solid rgba(255,226,150,.92);outline-offset:-0.22cqw}\n"
    u"/* the release beat: one bright flash, then it is gone */\n"
    u"@keyframes cardFired{\n"
    u"  0%{filter:drop-shadow(0 0 1.4cqw rgba(255,240,200,1)) brightness(1.6) saturate(1.2)}\n"
    u"  100%{filter:none}}\n"
    u".mcard.card-fired{animation:cardFired .42s ease-out}\n"
    u"/* the spent card does not fly home, it IS home - this only softens the cut\n"
    u"   so the change of state is legible rather than a pop */\n"
    u"@keyframes cardSpentCut{0%{opacity:.25;filter:brightness(1.35)}100%{opacity:1;filter:none}}\n"
    u".mcard.card-spent-cut{animation:cardSpentCut .3s ease-out}\n"
    u"/* Yield — matches activate-zone exactly */",
    'P613 armed/fired/cut')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('\n%d edits applied' % n)
