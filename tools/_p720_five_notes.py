# -*- coding: utf-8 -*-
"""P720: five notes from Denis's latest pass.

1 GRUDGE SPEAKS, NOT A CAPTION. The 'its owner will remember' line comes
  off the seat screen; instead, a patron whose archetype you robbed opens
  the REMATCH with a grudge bark - a real _DLG_MOMENT ('grudge') with two
  lines per trait, fired 2s into a match against a grudge-carrying patron,
  through DLG.trigger like every other beat.

2 THE FIRST-NIGHT DRAFT: dice spread out (gap 6% -> 10%), the name labels
  drop lower (margin 10% -> 24%) and FADE IN AT FINAL POSITION once their
  die has landed, instead of scaling up inside the entrance animation.

3 THE SIDE-SHADOW LANDS WITH THE DIE. The landing value rides the tape
  (d.roll.val) and the tape's end is a known time, so the dim ramp now
  finishes exactly at touchdown - during the roll, not after a post-settle
  delay - and runs twice as fast (350ms). The settled branch keeps the same
  ramp as a catch-up for watchdog-settled dice.

4 THE JELLY EDGE. Two causes, both in the solver: a cocked die's topple
  kick waited for the WHOLE pile to settle (the tape faithfully recorded
  the wait - 'they hang on their edge for a second or two'), and the
  settle-phase damping (.5 angular) made the eventual tip wade through
  treacle. Per-die: ten still-and-cocked frames earn the tip immediately,
  and a cocked die is exempt from the heavy settle damping while it falls.

5 RESUME WARMS THE ENGINE. resumeMatch boots the 3D stack and pulls cannon
  before the match screen opens, so the resumed turn's first roll does not
  pay script-load + first-solve while the player is trying to tap.
"""
import io, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'fark_proto.html')
s = io.open(P, encoding='utf-8', newline='').read()
n = 0


def sub(old, new, label, count=1):
    global s, n
    c = s.count(old)
    if c != count and '\n' in old:
        old2 = old.replace('\n', '\r\n')
        if s.count(old2) == count:
            old, c = old2, count
            new = new.replace('\n', '\r\n')
    if c != count:
        sys.exit('ANCHOR x%d (need %d) for %s' % (c, count, label))
    s = s.replace(old, new)
    n += 1
    print('  ok  %s' % label)


# ══ 1: the caption goes; the beat arrives ══
sub(u"    +(outE?'<div style=\"font-size:11px;color:#8a4a18;margin-top:6px\">its brand goes with it</div>':'')\n"
    u"    +(t.persona?'<div style=\"font-size:11px;color:#6a5238;margin-top:6px\">its owner will remember</div>':'')+'</div>';",
    u"    +(outE?'<div style=\"font-size:11px;color:#8a4a18;margin-top:6px\">its brand goes with it</div>':'')+'</div>';\n"
    u"  /* P720: no caption about remembering - the patron SAYS so at the\n"
    u"     rematch (the grudge moment below). */",
    'grudge caption out')

sub(u"var _DLG_MOMENT={OPP_BUST:'bust',PLAYER_BUST:'yourBust',\n"
    u"                 OPP_BIG_BANK:'bank',BIG_BANK:'yourBank',\n"
    u"                 OPP_HESITATE_PUSH:'push',OPP_HESITATE_BANK:'banksafe'};",
    u"var _DLG_MOMENT={OPP_BUST:'bust',PLAYER_BUST:'yourBust',\n"
    u"                 OPP_BIG_BANK:'bank',BIG_BANK:'yourBank',\n"
    u"                 OPP_HESITATE_PUSH:'push',OPP_HESITATE_BANK:'banksafe',\n"
    u"                 GRUDGE_TAKEN:'grudge'/* P720: you kept a die of theirs */};",
    'GRUDGE_TAKEN moment')

sub(u"prob:{MATCH_START:1,REMATCH_START:1,CARD_EFFECT:.8,",
    u"prob:{MATCH_START:1,REMATCH_START:1,GRUDGE_TAKEN:1,CARD_EFFECT:.8,",
    'GRUDGE_TAKEN prob')

sub(u"  {p:'trait:steady:bust',s:0,g:'v0',t:\"Ah, well.\"},",
    u"  /* P720: the grudge barks - a patron of an archetype you took a die\n"
    u"     from opens the rematch with it. Two voices per trait; Denis may\n"
    u"     reword in his own pass. */\n"
    u"  {p:'trait:steady:grudge',s:0,g:'v0',t:\"That die in your hand was ours.\"},\n"
    u"  {p:'trait:steady:grudge',s:0,g:'v1',t:\"We remember what you took.\"},\n"
    u"  {p:'trait:strong:grudge',s:0,g:'v0',t:\"My die. Your hand. We settle that tonight.\"},\n"
    u"  {p:'trait:strong:grudge',s:0,g:'v1',t:\"You took from us. Sit down.\"},\n"
    u"  {p:'trait:orderly:grudge',s:0,g:'v0',t:\"One die short since you last sat here. Noted.\"},\n"
    u"  {p:'trait:orderly:grudge',s:0,g:'v1',t:\"The ledger says you owe us a die.\"},\n"
    u"  {p:'trait:reckless:grudge',s:0,g:'v0',t:\"Ha! The die thief returns!\"},\n"
    u"  {p:'trait:reckless:grudge',s:0,g:'v1',t:\"Roll it. The one you stole. I dare you.\"},\n"
    u"  {p:'trait:greedy:grudge',s:0,g:'v0',t:\"You cost us a die. Tonight it comes back with interest.\"},\n"
    u"  {p:'trait:greedy:grudge',s:0,g:'v1',t:\"That was a GOOD die you walked off with.\"},\n"
    u"  {p:'trait:cunning:grudge',s:0,g:'v0',t:\"I remember what left with you last time.\"},\n"
    u"  {p:'trait:cunning:grudge',s:0,g:'v1',t:\"Still carrying it? Thought so.\"},\n"
    u"  {p:'trait:steady:bust',s:0,g:'v0',t:\"Ah, well.\"},",
    'grudge lines x12')

sub(u"    DLG.trigger('MATCH_START');\n"
    u"    /* NPC rivalry dialogue based on streak history */",
    u"    DLG.trigger('MATCH_START');\n"
    u"    /* P720: the archetype you robbed says so at the rematch */\n"
    u"    if(G.rung&&G.rung.grudge){setTimeout(function(){if(window.DLG)DLG.trigger('GRUDGE_TAKEN');},2000);}\n"
    u"    /* NPC rivalry dialogue based on streak history */",
    'grudge fires at rematch')

# ══ 2: the draft spreads out; labels fade in place ══
sub(u"#nrDice{position:absolute;left:0;right:0;top:47%;z-index:3;display:flex;gap:6%;\n"
    u"  justify-content:center}",
    u"#nrDice{position:absolute;left:0;right:0;top:47%;z-index:3;display:flex;gap:10%;/* P720: spread out, per Denis */\n"
    u"  justify-content:center}",
    'draft dice spread')

sub(u"#nrDice .nrdie .sub{margin-top:10%;text-shadow:0 2px 4px rgba(0,0,0,.7)}",
    u"/* P720: the name does not ride the entrance scale - it FADES IN at its\n"
    u"   final position once its die has landed, and sits lower off the die. */\n"
    u"#nrDice .nrdie .sub{margin-top:24%;text-shadow:0 2px 4px rgba(0,0,0,.7);\n"
    u"  opacity:0;animation:nrSubIn .45s ease-out forwards}\n"
    u"#nrDice .nrdie:nth-child(1) .sub{animation-delay:1.5s}\n"
    u"#nrDice .nrdie:nth-child(2) .sub{animation-delay:1.7s}\n"
    u"#nrDice .nrdie:nth-child(3) .sub{animation-delay:1.9s}\n"
    u"@keyframes nrSubIn{from{opacity:0}to{opacity:1}}",
    'draft labels fade in place')

# ══ 3: the dim lands with the die ══
sub(u"  SIDEDIM_RAMP:{delay:150,dur:700,steps:8},",
    u"  SIDEDIM_RAMP:{delay:0,dur:350,steps:8},/* P720: twice as fast, lands WITH the die */",
    'ramp twice as fast')

sub(u"          D3X._airTint(d,pose.y);\n"
    u"          /* P702 mirror: back in the air, back to the authored map */\n"
    u"          d.obj.traverse(function(o){\n"
    u"            if(!o.isMesh||!o.material||o.userData.outline)return;\n"
    u"            var m=o.material;\n"
    u"            if(m.userData&&m.userData.liveMap&&m.map!==m.userData.liveMap){m.map=m.userData.liveMap;m.needsUpdate=true;}\n"
    u"          });",
    u"          D3X._airTint(d,pose.y);\n"
    u"          /* P702 mirror / P720: the sides fall into shadow AS THE DIE\n"
    u"             LANDS - the landing value rides the tape (d.roll.val) and the\n"
    u"             tape's end is a known moment, so the ramp finishes exactly at\n"
    u"             touchdown. Early flight restores the authored map, which is\n"
    u"             also what un-dims a rerolled die. */\n"
    u"          (function(){\n"
    u"            var R2=d.roll,_lt=(R2&&R2.sol&&R2.sol.frames)?R2.t0+R2.sol.frames.length*(D3X.PHYS.dt*1000):0;\n"
    u"            var _kL=_lt?(performance.now()-(_lt-D3X.SIDEDIM_RAMP.dur))/D3X.SIDEDIM_RAMP.dur:0;\n"
    u"            if(_kL<0)_kL=0;if(_kL>1)_kL=1;\n"
    u"            _kL=_kL*_kL*(3-2*_kL);\n"
    u"            var _kkL=(Math.round(_kL*D3X.SIDEDIM_RAMP.steps)/D3X.SIDEDIM_RAMP.steps)*D3X.SIDEDIM_MAX;\n"
    u"            d.obj.traverse(function(o){\n"
    u"              if(!o.isMesh||!o.material||o.userData.outline)return;\n"
    u"              var m=o.material;\n"
    u"              if(!m.userData)m.userData={};\n"
    u"              if(!m.userData.liveMap)m.userData.liveMap=m.map;\n"
    u"              var want=(_kkL>0&&R2&&R2.val?D3X._dimMap(m.userData.liveMap,R2.val,_kkL):null)||m.userData.liveMap;\n"
    u"              if(m.map!==want){m.map=want;m.needsUpdate=true;}\n"
    u"            });\n"
    u"          })();",
    'dim ramps in during the roll')

# ══ 4: the jelly edge ══
sub(u"    var frames=[],it=0,over=0,boostFrom=-1,still=0;",
    u"    var frames=[],it=0,over=0,boostFrom=-1,still=0,_cockedFor=[];/* P720 */",
    'per-die cocked counters')

sub(u"        b2.linearDamping=hot?.55:.02;b2.angularDamping=hot?.5:.06;",
    u"        b2.linearDamping=hot?.55:.02;\n"
    u"        /* P720: a die mid-TIP is exempt from the settle damping - the\n"
    u"           heavy value is for skating, and it turned every topple into\n"
    u"           slow-motion jelly. */\n"
    u"        b2.angularDamping=(hot&&!this._cocked(b2.quaternion))?.5:.06;",
    'tip exempt from settle damping')

sub(u"      if(settled()){\n"
    u"        var anyCocked=false;",
    u"      /* P720: a die balanced on its edge earns its tip after ten still\n"
    u"         frames of ITS OWN - the old gate waited for the whole pile, and\n"
    u"         the tape faithfully recorded the wait as a die hanging on its\n"
    u"         edge for seconds. */\n"
    u"      for(var kc=0;kc<N;kc++){\n"
    u"        var bkc=bodies[kc];\n"
    u"        if(bkc.velocity.norm()<=P.stopV&&bkc.angularVelocity.norm()<=P.stopW&&this._cocked(bkc.quaternion)){\n"
    u"          _cockedFor[kc]=(_cockedFor[kc]||0)+1;\n"
    u"          if(_cockedFor[kc]>=10){\n"
    u"            _cockedFor[kc]=0;\n"
    u"            bkc.angularVelocity.set((Math.random()*2-1)*2.6,0,(Math.random()*2-1)*2.6);\n"
    u"          }\n"
    u"        }else _cockedFor[kc]=0;\n"
    u"      }\n"
    u"      if(settled()){\n"
    u"        var anyCocked=false;",
    'per-die tip without the pile gate')

# ══ 5: resume warms the engine ══
sub(u"  /* P700: restamp the identity the launcher never got to write - the\n"
    u"     snapshot's rung IS the deep-cloned patron, art and persona included.\n"
    u"     Boot, Settings, banner and both launch redirects all pass here. */",
    u"  /* P720: warm the 3D stack NOW - a resumed turn rolls almost on arrival,\n"
    u"     and the first roll used to pay script-load + first-solve right while\n"
    u"     the player was trying to tap (Denis: \"couldn't click anything\"). */\n"
    u"  try{if(window.D3X){D3X.boot&&D3X.boot();D3X._warmCannon&&D3X._warmCannon();}}catch(e){}\n"
    u"  /* P700: restamp the identity the launcher never got to write - the\n"
    u"     snapshot's rung IS the deep-cloned patron, art and persona included.\n"
    u"     Boot, Settings, banner and both launch redirects all pass here. */",
    'resume warms the engine')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d edits' % n)
