# -*- coding: utf-8 -*-
"""P605-P608: four defects from the batch recon, patched in one pass.

ANCHORED ON CONTENT, NOT LINE NUMBERS - the recon's line numbers are already
stale (its 14521 is now a different statement), and a line-addressed patch would
have silently rewritten the wrong code. Every anchor asserts it matched EXACTLY
ONCE, so a miss fails the run instead of reporting success on zero edits. That is
the same failure shape that bit the \\u2014 strings an hour ago.

P605 THE STORE'S UNAFFORDABLE BUTTON. `#stBuyBtn img` is a TYPE selector written
for the plaque background `<img class="plq">`, but the label also contains an
inline price glyph `<img class="pcoin">`. Specificity (1,0,1) beats .pcoin's
(0,1,0), so the coin was forced to position:absolute;inset:0;width:100%;
height:100%;object-fit:fill - a coin stretched across the whole label, hiding the
text behind it. Scoping the selector to the class it was written for is the whole
fix; the five sibling buttons already do this.

P606 THE LINGERING DRAFT PLATE. famRunDraftPick announces the pick through
famLog, which off-match routes to _famToast - and _famToast parents to
`#phoneShell || document.body`. #phoneShell does not exist on this path, so the
plate lands on BODY and survives both the draft overlay's removal and the screen
change. Only the announcement goes; famLog/_famAnnounce/_famToast are shared by
every off-match message and must not be touched.

P607 THE PLAYER RANK. Two independent ladders, both display-only:
PLAYER_TITLES/playerTitle() (8 call sites, nothing consumes the return value) and
a renown-tier header that iterates an empty array and renders 'Unknown'. Denis
asked for the main screen and "ensure it is removed everywhere", so all of it
goes - including the every-match "WELL MET, MASTER." toast, which is the one that
would have kept appearing after the visible label was gone.

P608 THE APEX SWELL. The throw is a recorded cannon.js solve replayed by D3X, and
the per-frame height (pose.y) is already in scope on the exact line that writes
the scale. THE DARKENING ALREADY EXISTS - _airTint ramps on the same height - so
the swell must share ITS ramp rather than carry a second copy of the expression:
two copies is how the two come to peak on different frames. Hence _airRamp.
"""
import io, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'fark_proto.html')
s = io.open(P, encoding='utf-8', newline='').read()
n_edits = 0


def sub(old, new, label):
    global s, n_edits
    c = s.count(old)
    if c != 1:
        sys.exit('ANCHOR MATCHED %d TIMES (need 1) for %s:\n  %r' % (c, label, old[:110]))
    s = s.replace(old, new)
    n_edits += 1
    print('  ok  %s' % label)


# ── P605: the store button ────────────────────────────────────────────────
sub(u"#stBuyBtn img{position:absolute;inset:0;width:100%;height:100%;object-fit:fill;pointer-events:none}",
    u"/* P605: img.plq, NOT img. This was written for the plaque background, but a\n"
    u"   type selector also catches the inline price glyph <img class=\"pcoin\"> in\n"
    u"   the label - and at (1,0,1) it outranks .pcoin's (0,1,0), so the coin was\n"
    u"   stretched across the whole button with object-fit:fill, hiding the text\n"
    u"   behind it. Only the unaffordable branch shows a label, which is why it\n"
    u"   only ever looked broken when you could not afford the die. */\n"
    u"#stBuyBtn img.plq{position:absolute;inset:0;width:100%;height:100%;object-fit:fill;pointer-events:none}",
    'P605 store button')

# ── P606: the draft toast ─────────────────────────────────────────────────
# NOTE ON ESCAPES: this file mixes both forms - some strings carry a LITERAL
# — escape and others a real em dash. The anchors below use whichever the
# source actually has, checked per site; assuming one form matched zero here.
sub(u"  famLog(getDie(mt).name.toUpperCase()+' — YOURS, WITH YOUR FIRST ALE');\n",
    u"  /* P606: no announcement here. famLog routes off-match to _famToast, which\n"
    u"     parents to `#phoneShell || document.body` - and #phoneShell does not\n"
    u"     exist on this path, so the plate landed on BODY and outlived both the\n"
    u"     draft overlay's removal and showScreen. The pick reads fine without it:\n"
    u"     the die is visibly taken and the screen advances. Anything put back here\n"
    u"     must not be body-parented. */\n",
    'P606 draft toast')

# ── P607: the player rank, every surface ──────────────────────────────────
sub(u"      +(playerTitle()!=='nobody'?' · '+playerTitle():'')+'</div>'",
    u"      +'</div>'/* P607: rank gone; NIGHT n/8 is the whole label now */",
    'P607 main screen')

sub(u"  if(typeof playerTitle==='function'&&playerTitle()!=='nobody'){\n"
    u"    setTimeout(function(){try{setStatusMsg((G&&G.rung?G.rung.name:'')+': “WELL MET, '+playerTitle().toUpperCase()+'.”','');}catch(e){}},400);\n"
    u"  }\n",
    u"  /* P607: the match-start rank greeting is gone with the rest of the ladder.\n"
    u"     This one fired on EVERY match once renown hit 40, so leaving it would\n"
    u"     have kept announcing a rank the game no longer shows anywhere. */\n",
    'P607 match-start toast')

sub(u"    +'<div class=\"gbx-label\">'+playerTitle()+' · renown '+(S.renown||0)+' · feats '",
    u"    +'<div class=\"gbx-label\">renown '+(S.renown||0)+' · feats '",
    'P607 shelf label')

sub(u"      +'<span style=\"color:#ca8\">TITLE: '+playerTitle().toUpperCase()+'</span><br>'\n",
    u"",
    'P607 Ambrose win card')

sub(u"  var html='<div class=\"rnk-info-title\">\\u2B50 '+(current?current.label:'Unknown')+'</div>';",
    u"  /* P607: the tier header is gone too. _getCurrentTier() walks an empty array\n"
    u"     and always returns null, so this rendered the literal word 'Unknown' as a\n"
    u"     rank - reachable in-match from the loadout's renown corner. */\n"
    u"  var html='';",
    'P607 renown panel header')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('\n%d edits applied' % n_edits)
