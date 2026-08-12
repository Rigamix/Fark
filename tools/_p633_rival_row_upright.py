# -*- coding: utf-8 -*-
"""P633: the rival's cards are the right way up, and the dead degradation goes.

Denis, from play: "UI issue with the boss cards? Looks like my card mirrored on
top of theirs. Also remove the degradation effect from boss cards (the destroyed
outline, etc. Should be like regular cards. Not needed I'll do something for it
later myself"

BOTH ARE MY P591, and they are the same edit's two consequences.

THE MIRRORING. #famRowO carried rotate(180deg). That was written when the row
held .mcBack - a flat CSS rectangle with a rim and a centred diamond - and the
comment on it said so outright: "It reverses their order too, which is
meaningless for identical backs." P591 then swapped .mcBack for famCardArt, so
the row started holding PAINTED FACES, and nothing counter-rotated them.
Photographed (tools/shoot_opp_cards.js): the row's computed matrix is a=-1,
d=-0.966, and the rival's two cards render upside down above the player's.
Which from the player's side of the table reads exactly as a mirrored copy of
their own hand - Denis's words.

The 180 comes off rather than being cancelled per-card. Cancelling it needed a
counter-rotation on .fcv AND left the drop-shadows pointing up the screen, since
a filter is applied before the element's own transform; taking it off the row
makes the rival's construction identical to the player's - translateX(-50%)
perspective(900px) rotateX(N) - which is one shape to reason about instead of
two. The far edge still leans away, because that is what a positive rotateX does
in the player's row too. The fan angles keep their signs and now read the same
direction as the player's, which is what "like regular cards" means.

THE DEGRADATION WAS ALREADY INVISIBLE, and that is worth saying plainly rather
than quietly deleting. The grey-out and the crossed-out overlay only ever
existed as `.mcBack.broken` / `.mcBack.broken::before`. P591 removed the last
thing that emitted a .mcBack element, so since then `inst.broken` has put a
`broken` class on a .fcv that no rule matches. Measured, not assumed: no
stylesheet in the built page carries a .broken selector that is not a .mcBack
one. So the whole .mcBack block is dead CSS, and this deletes it - which is what
Denis asked for, and also removes the trap where a future .mcBack quietly
inherits a crossed-out card. THE STATE STAYS: inst.broken still zeroes charges
and the card sheet still says "BROKEN - Tampered for the night". Only the
picture is gone, which is the half Denis said he wants to do himself.

AND A THIRD THING, WHICH DENIS DID NOT ASK FOR AND SHOULD SEE. The same
orphaning took the rival's ARMED telegraph with it. The brief's section 6 says
an armed rival active "rises with a red glow one roll ahead"; that was
.mcBack.armed, so today a rival card arms with nothing on screen at all -
famRenderRow still adds the class, and only #famRowP styles it. The player is
being denied a tell the design gives them. Fixed by widening the existing
#famRowP .fcv.armed rule to both rows rather than writing a second one, so
there is one armed look and it cannot drift. Revert is deleting one selector.
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


# ── 1. the row stands upright ────────────────────────────────────────────
sub(u"/* P579: MIRRORS THE PLAYER'S ROW - centred, upside down, and smaller for\n"
    u"   perspective. It sits below the turn plate (whose top is 9.4cqw and which is\n"
    u"   6.75cqw tall at 26cqw wide), so 17cqw clears it.\n"
    u"   THE ROTATION IS ON THE ROW, NOT THE CARDS. .mcBack.armed animates its own\n"
    u"   transform as the telegraph that a rival card is about to fire, and a per-card\n"
    u"   rotate would be deleted the moment one armed. One transform on the parent\n"
    u"   leaves every child's free. It reverses their order too, which is meaningless\n"
    u"   for identical backs. */\n"
    u"#famRowO{position:absolute;left:50%;top:calc(env(safe-area-inset-top,0px) + 8px + var(--bar-top) + 23cqw);/* P580: down, off the turn plate */\n"
    u"  /* P591: TILTED INTO THE TABLE. The row is the plane, not each card: the cards'\n"
    u"     own `rotate` is already carrying the fan, and one element cannot hold two\n"
    u"     rotations. Tilting the row is also what perspective actually means here -\n"
    u"     a hand lying on a surface, not four independently skewed cards.\n"
    u"     The 180deg comes first, so the rotateX after it leans the far edge away\n"
    u"     from the viewer exactly as the near row's does. */\n"
    u"  transform:translateX(-50%) rotate(180deg) perspective(900px) rotateX(15deg);\n"
    u"  display:flex;gap:0.6cqw;z-index:40}",
    u"/* P579: MIRRORS THE PLAYER'S ROW - centred, smaller for perspective, and sat\n"
    u"   below the turn plate (whose top is 9.4cqw and which is 6.75cqw tall at 26cqw\n"
    u"   wide), so 17cqw clears it.\n"
    u"   P633: THE 180deg IS GONE. It was written for .mcBack - a flat rectangle with\n"
    u"   a rim and a diamond - and its own note said reversing their order was\n"
    u"   \"meaningless for identical backs\". P591 put PAINTED FACES in this row and\n"
    u"   nothing counter-rotated them, so the rival's hand rendered upside down\n"
    u"   (measured: the row's matrix was a=-1, d=-0.966). Denis, from play: \"Looks\n"
    u"   like my card mirrored on top of theirs.\"\n"
    u"   Taken off the row rather than cancelled per card: a counter-rotation on .fcv\n"
    u"   would still leave the drop-shadows pointing up the screen, because a filter\n"
    u"   is applied before the element's own transform. Without it this row is built\n"
    u"   exactly like #famRowP, which is one shape to reason about instead of two. */\n"
    u"#famRowO{position:absolute;left:50%;top:calc(env(safe-area-inset-top,0px) + 8px + var(--bar-top) + 23cqw);/* P580: down, off the turn plate */\n"
    u"  /* P591: TILTED INTO THE TABLE. The row is the plane, not each card: the cards'\n"
    u"     own `rotate` is already carrying the fan, and one element cannot hold two\n"
    u"     rotations. Tilting the row is also what perspective actually means here -\n"
    u"     a hand lying on a surface, not four independently skewed cards.\n"
    u"     A positive rotateX leans the far edge away, the same way the near row's\n"
    u"     13deg does - which is now the whole of it. */\n"
    u"  transform:translateX(-50%) perspective(900px) rotateX(15deg);\n"
    u"  display:flex;gap:0.6cqw;z-index:40}",
    'P633 rival row upright')

# ── 2. the stale note on the row's sizing rule ───────────────────────────
sub(u"/* P580: THE FAN, ON `rotate` RATHER THAN `transform`, and that is the point.\n"
    u"   The row's own 180deg and .mcBack.armed's translateY telegraph both live on\n"
    u"   `transform`; the standalone `rotate` property composes with it instead of\n"
    u"   replacing it, so a fan angle costs neither of them anything and nothing has to\n"
    u"   restate anyone else's values inside a keyframe. */",
    u"/* P580: THE FAN, ON `rotate` RATHER THAN `transform`, and that is the point.\n"
    u"   The row's own plane lives on `transform`; the standalone `rotate` property\n"
    u"   composes with it instead of replacing it, so a fan angle costs it nothing and\n"
    u"   nothing has to restate anyone else's values inside a keyframe.\n"
    u"   P633: these angles now read the same direction as the player's fan, because\n"
    u"   the row no longer flips them. */",
    'P633 fix the fan note')

sub(u"/* P579: 14cqw -> 11cqw. The player's are 20cqw, so the rival's now read as\n"
    u"   further away rather than merely smaller, and the extra shadow sits them\n"
    u"   deeper in the candlelight Denis is lighting the table with. */\n",
    u"/* P579: 14cqw -> 11cqw. The player's are 20cqw, so the rival's now read as\n"
    u"   further away rather than merely smaller, and the extra shadow sits them\n"
    u"   deeper in the candlelight Denis is lighting the table with.\n"
    u"   P633: the shadows fall DOWN the screen now. Under the old 180deg they were\n"
    u"   cast upward - a dark halo above each card, with the light source below it -\n"
    u"   which is the other half of what read as a damaged card. */\n",
    'P633 note the shadow direction')

# ── 3. the rival's armed telegraph gets a look again ─────────────────────
sub(u"#famRowP .fcv.armed{filter:drop-shadow(0 0 1.1cqw rgba(255,217,138,.85))\n"
    u"  drop-shadow(0 0.9cqw 1.3cqw rgba(10,6,2,.5))}/* P576: third of the three */",
    u"/* P633: BOTH ROWS. The rival's armed telegraph was .mcBack.armed, and P591\n"
    u"   deleted the element that carried it - so since then famRenderRow has been\n"
    u"   adding `armed` to a .fcv that only #famRowP styled, and a rival card arming\n"
    u"   showed nothing at all. The brief's section 6 gives the player that tell.\n"
    u"   Widened rather than duplicated: one armed look, and it cannot drift. */\n"
    u"#famRowP .fcv.armed,#screen-match #famRowO .fcv.armed{\n"
    u"  filter:drop-shadow(0 0 1.1cqw rgba(255,217,138,.85))\n"
    u"  drop-shadow(0 0.9cqw 1.3cqw rgba(10,6,2,.5))}/* P576: third of the three */",
    'P633 rival armed telegraph')

# ── 4. the dead .mcBack block, degradation and all ───────────────────────
sub(u"/* FLAT family colour, standing in for painted backs. The border is the\n"
    u"   family (brief section 2: \"family = border colour, full stop\") and the face\n"
    u"   is a darker wash of the same so the card reads as an object rather than as\n"
    u"   a swatch. */\n"
    u".mcBack{width:8cqw;aspect-ratio:911/1298;border-radius:8%;position:relative;cursor:pointer;\n"
    u"  /* FLAT family colour as the cover, standing in until painted backs exist -\n"
    u"     the face IS the family, with a dark rim so the card reads as an object\n"
    u"     against the table rather than as a swatch. */\n"
    u"  background:var(--fc,#666);border:0.5cqw solid #1d1309;\n"
    u"  box-shadow:inset 0 0 0 0.35cqw rgba(255,255,255,.16),\n"
    u"             inset 0 -0.9cqw 1.2cqw rgba(0,0,0,.28),\n"
    u"             1px 2px 0 rgba(15,9,4,.45);\n"
    u"  transition:transform .2s,box-shadow .2s,filter .2s}\n"
    u"/* a single centred diamond, in the dark rim colour, so the flat face has one\n"
    u"   thing on it and the cards do not read as blank chips */\n"
    u".mcBack::after{content:'';position:absolute;inset:34%;border:0.34cqw solid rgba(20,12,6,.5);\n"
    u"  transform:rotate(45deg)}\n"
    u".mcBack.armed{transform:translateY(-1.5cqw);\n"
    u"  box-shadow:0 0 9px 2px rgba(224,70,45,.6),inset 0 0 0 1px rgba(0,0,0,.5)}\n"
    u".mcBack.broken{filter:grayscale(.85) brightness(.5)}\n"
    u".mcBack.broken::before{content:'\\2715';position:absolute;inset:0;display:flex;align-items:center;\n"
    u"  justify-content:center;color:#c96a5a;font-size:4cqw;z-index:1}\n",
    u"/* P633: THE WHOLE .mcBack BLOCK IS GONE. P591 removed the last thing that\n"
    u"   emitted one - famRenderRow builds the rival's row with famCardArt now - so\n"
    u"   these rules had had nothing to match for a while. Two of them mattered:\n"
    u"     .mcBack.broken  greyed the card and stamped a crossed-out mark over it.\n"
    u"                     That is the degradation Denis asked to have removed, and\n"
    u"                     it had already stopped painting; `inst.broken` has been\n"
    u"                     landing on a .fcv no rule matched. THE STATE IS UNTOUCHED -\n"
    u"                     broken still zeroes charges and the sheet still reads\n"
    u"                     \"BROKEN - Tampered for the night\". Only the picture is\n"
    u"                     gone, which is the half Denis is doing himself.\n"
    u"     .mcBack.armed   the rival's about-to-fire telegraph, moved to .fcv above.\n"
    u"   Deleted rather than left: a dead rule keyed to a class name is a trap for\n"
    u"   whoever writes the next element called .mcBack. */\n",
    'P633 delete the dead .mcBack block')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('\n%d edits' % n)
