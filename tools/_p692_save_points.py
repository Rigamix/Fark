# -*- coding: utf-8 -*-
"""P692: the save audit's three fixes - a bank can never be lost, resume is
visible, and the game never discards a saved match silently.

Denis: "more save points, especially in matches so that if I leave the game it
doesn't consider that match lost... If it makes the game heavier do let me
know before implementing."

THE AUDIT MEASURED IT FIRST (agent report, tools/apv_save_cost*.js): the whole
save file is ~5.3KB and a full saveMatchState costs 0.03ms (max 0.4) - saving
is free, no gate to raise. But it also found the matches were never being lost
for LACK of saves. Three real causes:
  1. the only snapshot writer fires at startPTurn, so the loss window is a
     full ROUND - bank 800, quit during the rival's animation, and the bank
     replays away;
  2. resume exists ONLY as a button buried in Settings - the on-screen banner
     was removed (its refresher is a cleanup no-op);
  3. starting any other match silently deletes the pending one (and charges
     the heart if it was a boss) with no confirmation anywhere.

THE FIXES, per the audit's own recommended shape:
  1. a SECOND boundary write at the top of endPTurn, after the turn's results
     are locked and the per-turn state resets - with the four turn-start
     anchors re-stashed first so the snapshot's replay contract holds
     ("turn start" simply becomes "post-bank"; the rival's replayed turn is
     automated). A bank now survives any exit.
  2. _refreshResumeBanners gets its body back: a parchment chip on the room
     when a match is pending, tapping it resumes. Same class name the no-op
     already clears, so cached older builds stay clean.
  3. launchSeat/launchBossMatch ask before burning a pending match, through
     the game's own modal - the initMatchScreen block stays as the single
     enforcement site for the heart charge.
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


# ── 1. the post-bank boundary ───────────────────────────────────────────
sub(u"  var _pTurnPts=(G.turnPts||0);\n"
    u"  G._pTurnPts=_pTurnPts;\n"
    u"  G.phase='opp';G.turnPts=0;G.kept=[];G.numDice=6;G.turnNum++;",
    u"  var _pTurnPts=(G.turnPts||0);\n"
    u"  G._pTurnPts=_pTurnPts;\n"
    u"  G.phase='opp';G.turnPts=0;G.kept=[];G.numDice=6;G.turnNum++;\n"
    u"  /* P692: THE POST-BANK BOUNDARY. The only snapshot used to be the next\n"
    u"     startPTurn - a full round away - so a banked turn evaporated on any\n"
    u"     exit during the rival's animation. The four turn-start anchors are\n"
    u"     re-stashed first, so the snapshot's replay contract holds: 'turn\n"
    u"     start' is simply 'the moment after the bank'. Cost measured at 0.03ms\n"
    u"     on a 5KB payload - free. */\n"
    u"  try{\n"
    u"    G._goldAtTurnStart=(S&&S.run&&typeof S.run.gold==='number')?S.run.gold:null;\n"
    u"    G._hotdAtTurnStart=!!(S&&S.run&&S.run._hotdNext);\n"
    u"    if(G.npcCardState)G._ptcAtTurnStart=G.npcCardState.playerTurnCount;\n"
    u"    G._famPreserveAtTurnStart=G._famPreserve||null;\n"
    u"    saveMatchState();\n"
    u"  }catch(e){}",
    'P692 the post-bank boundary')

# ── 2. resume gets a face ───────────────────────────────────────────────
sub(u"function _refreshResumeBanners(){\n"
    u"  /* The on-screen resume banner is gone — resume now lives ONLY as a button in\n"
    u"     Settings (see #settingsResume / initSettingsUI). This stays as a cleanup\n"
    u"     no-op so any banner left in a cached older build gets cleared, and existing\n"
    u"     callers (abandonMatch, initTierScreen, initMenuScreen) keep working. */\n"
    u"  document.querySelectorAll('.resume-banner').forEach(function(b){b.remove();});\n"
    u"}",
    u"function _refreshResumeBanners(){\n"
    u"  /* P692: the banner is BACK - the save audit found resume buried in\n"
    u"     Settings was most of why leaving read as losing the match. Same class\n"
    u"     the old no-op cleared, so cached builds stay clean. Lives on the room\n"
    u"     screen, where the next match would be chosen. */\n"
    u"  document.querySelectorAll('.resume-banner').forEach(function(b){b.remove();});\n"
    u"  try{\n"
    u"    _getS();\n"
    u"    if(!S||!S.pendingMatch)return;\n"
    u"    var host=document.getElementById('gbRoom');\n"
    u"    if(!host)return;\n"
    u"    var b=document.createElement('div');\n"
    u"    b.className='resume-banner';\n"
    u"    b.style.cssText='position:absolute;left:50%;top:9%;transform:translateX(-50%);'\n"
    u"      +'z-index:80;background:#e7d6ac;color:#2a1808;border:2px solid #a58a3c;'\n"
    u"      +'border-radius:10px;padding:8px 18px;font-family:'+\"'JMH Beda'\"+',serif;'\n"
    u"      +'font-size:14px;cursor:pointer;box-shadow:0 4px 14px rgba(10,6,2,.5)';\n"
    u"    b.textContent='\\u25B6 RESUME \\u2014 '+((S.pendingMatch.rung&&S.pendingMatch.rung.name)||'THE MATCH');\n"
    u"    b.onclick=function(){try{SFX.nav();}catch(e){}resumeMatch();};\n"
    u"    host.appendChild(b);\n"
    u"  }catch(e){}\n"
    u"}",
    'P692 the banner returns')

# ── 3. no silent discard ────────────────────────────────────────────────
sub(u"function launchSeat(seatIdx){",
    u"/* P692: NEVER BURN A SAVED MATCH SILENTLY. The heart charge itself stays in\n"
    u"   initMatchScreen (single enforcement site); this only makes sure it is a\n"
    u"   choice. The flag is consumed by the relaunch. */\n"
    u"function _confirmDiscardPending(onYes){\n"
    u"  var pm=S&&S.pendingMatch;\n"
    u"  var nm=(pm&&pm.rung&&pm.rung.name)||'a match';\n"
    u"  var boss=!!(pm&&pm.isBoss);\n"
    u"  _gbModalOpen('<div style=\"font-size:15px;text-align:center\">A game against '+nm+' is waiting.</div>'\n"
    u"    +'<div style=\"font-size:12px;text-align:center;opacity:.85\">Starting another one abandons it'\n"
    u"    +(boss?' \\u2014 and walking from a boss costs a heart.':'.')+'</div>'\n"
    u"    +'<div class=\"gbx-btn primary\" style=\"height:46px\" id=\"pdResume\">RESUME IT</div>'\n"
    u"    +'<div class=\"gbx-btn\" style=\"height:42px\" id=\"pdDiscard\">PLAY THIS ONE INSTEAD</div>');\n"
    u"  var r=document.getElementById('pdResume'),d=document.getElementById('pdDiscard');\n"
    u"  if(r)r.onclick=function(){_gbModalClose();try{SFX.nav();}catch(e){}resumeMatch();};\n"
    u"  if(d)d.onclick=function(){_gbModalClose();try{SFX.nav();}catch(e){}onYes();};\n"
    u"}\n"
    u"function launchSeat(seatIdx){\n"
    u"  if(S&&S.pendingMatch&&!window._fkDiscardOk){\n"
    u"    _confirmDiscardPending(function(){window._fkDiscardOk=true;try{launchSeat(seatIdx);}finally{window._fkDiscardOk=false;}});\n"
    u"    return;\n"
    u"  }",
    'P692 seat launch asks')

sub(u"function launchBossMatch(){\n"
    u"  _getS();\n"
    u"  /* P682: the stale-seat hygiene half of the same fix */",
    u"function launchBossMatch(){\n"
    u"  _getS();\n"
    u"  if(S&&S.pendingMatch&&!window._fkDiscardOk){\n"
    u"    _confirmDiscardPending(function(){window._fkDiscardOk=true;try{launchBossMatch();}finally{window._fkDiscardOk=false;}});\n"
    u"    return;\n"
    u"  }\n"
    u"  /* P682: the stale-seat hygiene half of the same fix */",
    'P692 boss launch asks')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('\n%d edits' % n)
