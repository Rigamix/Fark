# -*- coding: utf-8 -*-
"""P837: the four patron-leveling rulings (Denis, 2026-08-20 batch).

1. RIVAL OBSIDIAN SHATTERS - "the material can't mean something
   different for each side." Same denominator as the player's sweep
   (each free obsidian, each roll, its own chance), same payout shape
   (straight to the score, bust-proof), and the die leaves the MATCH
   through _oRemoveOppDieAt - the first permanent rival-die removal in
   the game, so it gets the _removeDieAt-style lane repairs: markers
   (snuff/fog/snare), the trade ledger's oLane, held-die lanes, the
   published snuff seat, and the alsoOpp snapshot (resume is a
   standing risk area; without it a reload resurrects the die).
2. TIER LOCKS - "no raw tier-III for patrons either. The point of
   parity is matching rules, not giving NPCs a shortcut." The
   night>=6 20% raw-III roll goes; II from night 3 stays (matches the
   player's raw-II odds).
3. THE NAME IS THE CHARACTER - art names are chosen BEFORE generation
   and their persona rides S.run._artPersona, so 'Krox' is
   mechanically the same patron every night. The room's assignment
   IIFE stays as the legacy fallback and now records first-seen
   personas into the same registry.
4. THE RECOGNITION BEAT - first meeting since the patron's band
   changed (bands: nights 1-3 / 4-6 / 7+), once, ahead of the
   ordinary open, drawn from the patron:<art>:recog pools P833 wired.
   Band state per art name on S.run (the identity register the
   dialogue stages already use).
"""
import io, os, sys, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'fark_proto.html')
s = io.open(P, encoding='utf-8', newline='').read()
edits = []


def sub(old, new, label):
    global s
    if s.count(old) == 1:
        s = s.replace(old, new)
        edits.append(label)
        return
    pat = re.escape(old).replace('\\\n', '\n').replace('\n', '\\r?\n')
    ms = list(re.finditer(pat, s))
    if len(ms) != 1:
        sys.exit('ANCHOR x%d for %s (nothing written)' % (len(ms), label))
    m = ms[0]
    rep = new.replace('\n', '\r\n') if '\r\n' in m.group(0) else new
    s = s[:m.start()] + rep + s[m.end():]
    edits.append(label)


# ── 2) tier locks ──
sub("""    var t=1;
    if(night>=3&&Math.random()<0.30)t=2;
    if(night>=6&&Math.random()<0.20)t=3;
    fc.push({id:pick.id,tier:t});""",
    """    var t=1;
    if(night>=3&&Math.random()<0.30)t=2;
    /* P837 (Denis, ruling 2): NO raw tier-III for patrons - the player's
       III is upgrade-only, and parity means matching rules, not an NPC
       shortcut. The night>=6 20% roll is deleted. Bosses keep their own
       schedule (a different table by design). */
    fc.push({id:pick.id,tier:t});""",
    'no raw tier-III')

# ── 3) persona rides the name: threading ──
sub("""function _generatePatronInner(tierIndex){""",
    """function _generatePatronInner(tierIndex,forcePersona){""",
    'inner takes a forced persona')

sub("""  var _personaKey=(tierIndex<=1)
    ? ['ones','hoard','aggro'][Math.floor(Math.random()*3)]
    : _PERSONA_KEYS[Math.floor(Math.random()*_PERSONA_KEYS.length)];""",
    """  var _personaKey=(forcePersona&&PERSONAS[forcePersona])?forcePersona
    :((tierIndex<=1)
    ? ['ones','hoard','aggro'][Math.floor(Math.random()*3)]
    : _PERSONA_KEYS[Math.floor(Math.random()*_PERSONA_KEYS.length)]);/* P837: the registry wins */""",
    'the registry wins the roll')

sub("""function generatePatron(tierIndex){
  var _gp=_generatePatronInner(tierIndex);""",
    """function generatePatron(tierIndex,forcePersona){
  var _gp=_generatePatronInner(tierIndex,forcePersona);""",
    'generatePatron threads it')

# ── 3) the roster binds names first ──
sub("""  var n=_nightSeats(),roster=[];
  for(var i=0;i<n;i++)roster.push(generatePatron(S.run.tier));""",
    """  var n=_nightSeats(),roster=[];
  /* P837 (Denis, ruling 3): THE NAME IS THE CHARACTER. The art name is
     chosen BEFORE generation and its persona rides S.run._artPersona,
     so the same name is mechanically the same patron every night - the
     approved growth dialogue has a stable identity under it. */
  S.run._artPersona=S.run._artPersona||{};
  var _apUsed={};
  for(var i=0;i<n;i++){
    var _apFree=PT_ART_POOL.filter(function(a){return !_apUsed[a];});
    var _apPool=_apFree.length?_apFree:PT_ART_POOL;
    var _apName=_apPool[Math.floor(Math.random()*_apPool.length)];
    _apUsed[_apName]=1;
    var _apP=generatePatron(S.run.tier,S.run._artPersona[_apName]||null);
    _apP._art=_apName;
    S.run._artPersona[_apName]=_apP.persona;
    roster.push(_apP);
  }""",
    'the roster binds names first')

# ── 3) the legacy room fallback records into the registry ──
sub("""      p2._art=pool[Math.floor(Math.random()*pool.length)];
      used[p2._art]=1;dirty=true;""",
    """      p2._art=pool[Math.floor(Math.random()*pool.length)];
      used[p2._art]=1;dirty=true;
      /* P837: the legacy fallback records first-seen personas into the
         same registry the roster build consults. */
      try{S.run._artPersona=S.run._artPersona||{};
        if(!S.run._artPersona[p2._art])S.run._artPersona[p2._art]=p2.persona;}catch(e){}""",
    'the fallback records too')

# ── 4) the recognition beat, ahead of the ordinary open ──
sub("""        else if(typeof _DLG_PERSONAL!=='undefined'&&_DLG_PERSONAL[cat]){
          var pl=_dlgSay(window._lastSeatArt);if(pl)return pl;
        }""",
    """        else if(typeof _DLG_PERSONAL!=='undefined'&&_DLG_PERSONAL[cat]){
          /* P837 (Denis's brief, piece 2): THE RECOGNITION BEAT - the
             first meeting since this patron's band changed, once, ahead
             of the ordinary open. Bands: nights 1-3 / 4-6 / 7+. State
             per art name on S.run, the same identity register the
             dialogue stages use. A first-ever meeting records the band
             silently; only a CHANGE speaks. */
          try{
            var _ra=window._lastSeatArt;
            if(_ra&&(cat==='MATCH_START'||cat==='REMATCH_START')){
              _getS();S.run._artBand=S.run._artBand||{};
              var _rk=String(_ra).toLowerCase();
              var _nightNow=((S.run.tier||0)+1);
              var _nowB=(_nightNow>=7)?2:((_nightNow>=4)?1:0);
              var _prevB=S.run._artBand[_rk];
              if(_prevB===undefined){S.run._artBand[_rk]=_nowB;try{save();}catch(e){}}
              else if(_nowB>_prevB){
                S.run._artBand[_rk]=_nowB;try{save();}catch(e){}
                var _rr=_dlgPick('patron:'+_rk+':recog',0,null);
                if(_rr)return _rr.t;
              }
            }
          }catch(e){}
          var pl=_dlgSay(window._lastSeatArt);if(pl)return pl;
        }""",
    'the recognition beat')

# ── 1) the rival-side removal path ──
sub("""function _lmArm(key,lane,turns,extra){""",
    """/* P837: THE RIVAL-SIDE REMOVAL PATH - the mirror of _removeDieAt's
   lane repairs, built for the first permanent rival-die removal (the
   obsidian shatter). matchOppDice shrinks (the deal reads its length,
   so the next turn deals one fewer by itself); every stored rival-lane
   index above L shifts down; a marker sitting ON L dies with the die;
   the trade ledger's oLane is repaired (NEVER lane - that indexes the
   player's board, the exact error P531 caught); and the change is
   re-snapshotted with alsoOpp so a reload cannot resurrect the die. */
function _oRemoveOppDieAt(L){
  if(!G||!G.matchOppDice||typeof L!=='number'||L<0||L>=G.matchOppDice.length)return null;
  if(G.matchOppDice.length<=1)return null;/* the one-die floor, both sides */
  var gone=G.matchOppDice.splice(L,1)[0];
  ['_snuff','_fog','_snare'].forEach(function(k){
    var m=G[k];if(!m||typeof m.lane!=='number')return;
    if(m.lane===L)m.live=false;
    else if(m.lane>L)m.lane--;
  });
  (G._tradeSwaps||[]).forEach(function(t){
    if(!t||typeof t.oLane!=='number')return;
    if(t.oLane===L)t.oLane=-1;
    else if(t.oLane>L)t.oLane--;
  });
  (G._oppHeld||[]).forEach(function(d){
    if(typeof d.lane==='number'&&d.lane>L)d.lane--;
  });
  if(typeof G._oSnuffLane==='number'){
    if(G._oSnuffLane===L)G._oSnuffLane=-1;
    else if(G._oSnuffLane>L)G._oSnuffLane--;
  }
  (G.oppDice||[]).forEach(function(d){
    if(typeof d.lane==='number'&&d.lane>L)d.lane--;
  });
  try{_snapDiceOnly(true);}catch(e){}
  return gone;
}
function _lmArm(key,lane,turns,extra){""",
    'the rival removal path')

# ── 1) the shatter sweep, before the reckoning reads the row ──
sub("""      _npcRunArms('roll',{oppBank:oppBank});
      const _oFree=G.oppDice.filter(d=>!d.kept);""",
    """      _npcRunArms('roll',{oppBank:oppBank});
      /* P837 (Denis, ruling 1): RIVAL OBSIDIAN SHATTERS TOO - the
         material cannot mean something different per side. Same
         denominator as the player's sweep (each free obsidian, each
         roll, its own chance via _dieEffect - hushable the same way),
         same payout shape (straight to the score, bust-proof), die gone
         for the match through the one removal path. Runs BEFORE the
         reckoning builds its view, so a shattered die never scores. */
      try{
        for(var _obI=G.oppDice.length-1;_obI>=0;_obI--){
          var _obD=G.oppDice[_obI];
          if(_obD.kept)continue;
          var _obFx=(typeof _dieEffect==='function')?_dieEffect(_obD):null;
          if(!_obFx||_obFx.mechanic!=='shatter_bonus')continue;
          if(Math.random()>=(_obFx.chance||0.06))continue;
          var _obAmt=_obFx.amount||1000;
          var _obL=(typeof _obD.lane==='number')?_obD.lane:-1;
          if(_oRemoveOppDieAt(_obL)===null)continue;/* the floor said no */
          G.oPts+=_obAmt;
          G.oppDice.splice(_obI,1);
          if(_obD.el){
            try{if(window.D3X&&D3X.shatter)D3X.shatter(_obD.el);}catch(e){}
            try{spawnObsidianBurst(_obD.el);}catch(e){}
            try{_obD.el.classList.add('die-shatter');}catch(e){}
            (function(_e){setTimeout(function(){try{_e.remove();}catch(e2){}},420);})(_obD.el);
          }
          try{SFX.coinExplode&&SFX.coinExplode();}catch(e){}
          triggerCard('obsidian',(G.rung&&G.rung.name||'RIVAL')+' SHATTERED +'+_obAmt,false);
          setStatusMsg((G.rung&&G.rung.name||'RIVAL')+' — OBSIDIAN SHATTERS +'+_obAmt,'red');
          try{updHUD();}catch(e){}
        }
      }catch(e){}
      const _oFree=G.oppDice.filter(d=>!d.kept);""",
    'the rival shatter sweep')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d (%s)' % (len(edits), ', '.join(edits)))
