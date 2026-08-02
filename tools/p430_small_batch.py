# -*- coding: utf-8 -*-
"""P430 - four confirmed items from OPEN.md, each small and independent.

  #15  the victory headline
  #14  audio on by default
  #8   the Settings icon swaps to the current art tree
  #21  the backdrop stretch (see the note - it does not paint)
"""
import io, os

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   'fark_proto.html')
with io.open(SRC, encoding='utf-8') as f:
    s = f.read()
orig = s

def sub_once(hay, old, new, what):
    n = hay.count(old)
    assert n == 1, 'anchor %s matched %d times (want 1)' % (what, n)
    return hay.replace(old, new)

# ── #15. THE VICTORY HEADLINE ─────────────────────────────────────────
# Ruled in AUDIT_RESOLUTIONS.md #4: "THE HOUSE IS YOURS." The Ambrose-reuse
# option ("THE HOUSE REMEMBERS YOUR NAME") was rejected outright - the same
# line twice in a row reads as copy-paste on the biggest moment in the game.
#
# LAST ORDERS RUNG is the NIGHT-END beat, not the run-end one, and the code
# already knows: _showLastOrders' own comment says it must be impossible to
# misread as a win. It was on both screens.
#
# The sub-line goes too, and that is a separate ruling: master brief section 8
# deletes the renown counter and states "There is NO trophy shelf - the feats
# wall is the only meta surface". This box was promising a trophy to a shelf
# that does not exist and printing a counter that does not either.
s = sub_once(s,
  u"    h+='<div class=\"gbx-box\" style=\"width:230px;height:64px\">LAST ORDERS RUNG<br><span class=\"gbx-label\">you own the night</span></div>'\n"
  u"      +'<div class=\"gbx-box sub\" style=\"width:230px;height:64px;font-size:12px\">trophy → shelf · '+playerTitle()+' · renown '+(S.renown||0)+'</div>';",
  u"    /* RULED (AUDIT_RESOLUTIONS #4). \"LAST ORDERS RUNG\" is the NIGHT-END beat -\n"
  u"       _showLastOrders' own comment says that screen must be impossible to\n"
  u"       misread as a win - and it was being used for the run-END one too, so the\n"
  u"       single biggest moment in the game shared its headline with a night you\n"
  u"       failed. The Ambrose-reuse alternative was rejected outright: the same\n"
  u"       line twice running reads as copy-paste, not callback.\n"
  u"       THE SUB-LINE GOES FOR A DIFFERENT REASON. Master brief section 8 deletes\n"
  u"       the renown counter and states there is NO trophy shelf - the feats wall\n"
  u"       is the only meta surface. This box promised a trophy to a shelf that does\n"
  u"       not exist and printed a counter that does not either. What replaces it is\n"
  u"       what the brief actually asks 3.11 to show: the run, and the wall. */\n"
  u"    h+='<div class=\"gbx-box\" style=\"width:230px;height:64px\">THE HOUSE IS YOURS<br><span class=\"gbx-label\">you own the night</span></div>'\n"
  u"      +'<div class=\"gbx-box sub\" style=\"width:230px;height:64px;font-size:12px\">'\n"
  u"      +((S.run&&S.run._featsThisRun)||0)+' feats this run · '+((S.run&&S.run.gold)||0)+'g in the purse</div>';",
  'victory headline')

# ── #14. AUDIO ON BY DEFAULT ──────────────────────────────────────────
# The flag forced all three channels off on first touch and then latched, so
# every feel assessment of this build - mine included - has been of a silent
# game. Removing the block is not enough on its own: saves that already took
# the mute have music/sfx/ambience false PERSISTED, so they would stay silent
# forever. One migration flag turns them back on exactly once, and a player who
# then chooses to mute keeps that choice, because _protoUnmuted latches too.
s = sub_once(s,
  u"    if(!S.settings._protoMuted){/* proto build: audio off by default (Denis) */\n"
  u"      S.settings._protoMuted=true;\n"
  u"      S.settings.music=false;S.settings.ambience=false;S.settings.sfx=false;\n"
  u"    }\n",
  u"    /* AUDIO ON BY DEFAULT. This used to force all three channels off on first\n"
  u"       touch and latch the fact, so every feel assessment of this build has been\n"
  u"       of a silent game - which is a bad way to judge a game about a tavern.\n"
  u"       DELETING THE BLOCK IS NOT ENOUGH BY ITSELF: any save that already took\n"
  u"       the mute has music/ambience/sfx PERSISTED false, and would stay silent\n"
  u"       forever. The one-shot below turns them back on exactly once. It latches\n"
  u"       on its own flag, so a player who then mutes deliberately keeps that\n"
  u"       choice - the un-mute never fights the user. */\n"
  u"    if(!S.settings._protoUnmuted){\n"
  u"      S.settings._protoUnmuted=true;\n"
  u"      if(S.settings._protoMuted){\n"
  u"        S.settings.music=true;S.settings.ambience=true;S.settings.sfx=true;\n"
  u"        delete S.settings._protoMuted;\n"
  u"      }\n"
  u"    }\n",
  'audio default')

# ── #8. THE SETTINGS ICON ─────────────────────────────────────────────
# The one legacy art path with a real, usable replacement in the current tree.
# (gameover.png is deliberately NOT swapped: its only current-tree twin is a
# .psd - a source file, not an asset - so there is nothing to point at until
# someone exports it. That is a blocked swap, not a deferred one.)
s = sub_once(s,
  u'src="assets/Menu_Art/Settings.png"',
  u'src="Art/Assets/Panels/Settings/settings.png"',
  'settings icon')

# ── #21. THE BACKDROP STRETCH ─────────────────────────────────────────
# MEASURED FIRST, AND THE PREMISE DID NOT HOLD: `body::before` computes to
# display:none - line ~4561 kills both pseudo-elements outright because every
# screen paints its own plate now. So the stretch is real in the source and
# reaches no pixel. Fixed anyway, because a wrong rule sitting in a file is a
# trap for whoever re-enables it, and `cover` is what the match rule below
# already uses. Cost: nothing. Effect today: nothing, stated plainly rather
# than reported as a fix.
s = sub_once(s,
  u"     STILL STRETCHES, and that is a known fault left alone on purpose: `100%\n"
  u"     100%` scales both axes independently, which is the exact thing the match",
  u"     STRETCH FIXED, AND IT CHANGES NOTHING TODAY - measured before touching it:\n"
  u"     this pseudo-element computes to display:none, because every screen paints\n"
  u"     its own plate now (see the body::before,body::after kill rule further\n"
  u"     down). The old `100%\n"
  u"     100%` scales both axes independently, which is the exact thing the match",
  'backdrop comment')

assert s != orig, 'nothing changed'
assert u'LAST ORDERS RUNG<br>' not in s, 'old headline survives'
assert u'assets/Menu_Art/Settings.png' not in s, 'old settings path survives'
with io.open(SRC, 'w', encoding='utf-8', newline='') as f:
    f.write(s)
print('P430 applied: headline, audio, settings icon, backdrop comment')
