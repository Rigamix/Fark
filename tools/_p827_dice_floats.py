# -*- coding: utf-8 -*-
"""P827: stargazer ghost dice, honeytrap's marker and pull beat,
vanguard's revived primer + end-spot hints.

All die-anchored visuals ride the P823 fog-float pattern (body-level
fixed floats at the chip rect - the one die-anchored overlay proven
visible over the 3D canvas) plus the FX spray layer.

- STARGAZER: the peek was a famLog text list. Now each free die gets a
  ghost face floating over it - starstone blue, showing that lane's
  promised value - cleared exactly where the promise is spent or
  voided (_clearRollForces, the single lifecycle point P556 built).
- HONEYTRAP: the armed pair wears honey marks (same lifecycle), and
  the pull lands ON the die - spawnPop's die-anchor (it always
  supported one; _famPop just never passed it) plus an amber spray.
- VANGUARD_F: the position-card primer at toggleDie tested the RETIRED
  card ids through effectiveCards(), which returns [] - it could never
  fire. It now tests famInst('vanguard_f') with tier-shaped ends, and
  each roll settles with brief gold end-spot hints so the player aims.
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
    hits = re.findall(pat, s)
    if len(hits) != 1:
        sys.exit('ANCHOR x%d for %s (nothing written)' % (len(hits), label))
    s = re.sub(pat, lambda m: new, s, count=1)
    edits.append(label)


# ── shared: the float helper + CSS (beside the fog float) ──
sub("""/* P823: the fog cloud - floats in the top layer over the blinded die
   (chip-level overlays are invisible under the 3D canvas). */
.fog-float{position:fixed;transform:translate(-50%,-55%);font-size:30px;color:#cdd5dc;
  text-shadow:0 2px 6px #000c,0 0 14px #a8b0b880;pointer-events:none;z-index:60;
  animation:fogFloatDrift 2.4s ease-in-out infinite}""",
    """/* P823: the fog cloud - floats in the top layer over the blinded die
   (chip-level overlays are invisible under the 3D canvas). */
.fog-float{position:fixed;transform:translate(-50%,-55%);font-size:30px;color:#cdd5dc;
  text-shadow:0 2px 6px #000c,0 0 14px #a8b0b880;pointer-events:none;z-index:60;
  animation:fogFloatDrift 2.4s ease-in-out infinite}
/* P827: die-anchored floats - stargazer's ghost faces, honeytrap's
   honey marks, vanguard's end-spot hints. Same body-level fixed
   pattern; left/top are the anchor center. */
.peek-float{position:fixed;transform:translate(-50%,-130%);pointer-events:none;z-index:60;
  font-family:monospace;font-weight:bold;font-size:17px;color:#8fa8ff;
  background:#101426cc;border:1px solid #8fa8ff88;border-radius:4px;padding:1px 6px;
  text-shadow:0 0 8px #8fa8ff;animation:peekFloatBreathe 1.6s ease-in-out infinite}
@keyframes peekFloatBreathe{0%,100%{opacity:.8;transform:translate(-50%,-130%)}
  50%{opacity:1;transform:translate(-50%,-145%)}}
.honey-float{position:fixed;transform:translate(-50%,-140%);pointer-events:none;z-index:60;
  font-size:16px;text-shadow:0 1px 4px #000c,0 0 10px #e8b04090;
  animation:peekFloatBreathe 1.8s ease-in-out infinite}
.vang-float{position:fixed;transform:translate(-50%,-135%);pointer-events:none;z-index:60;
  font-size:13px;color:#ffd870;font-family:monospace;letter-spacing:1px;
  text-shadow:0 1px 3px #000c,0 0 8px #ffd87080;opacity:.95}""",
    'float CSS trio')

# ── lifecycle: the forces clear removes the floats ──
sub("""function _clearRollForces(){
  if(!G)return;
  G._famPeekVals=null;G._famHoneyVal=null;
}""",
    """function _clearRollForces(){
  if(!G)return;
  G._famPeekVals=null;G._famHoneyVal=null;
  /* P827: the ghost faces and honey marks live exactly as long as the
     forces they mark - one lifecycle point, no second exit. */
  try{(window._pkGhosts||[]).forEach(function(g){if(g.parentNode)g.remove();});window._pkGhosts=[];}catch(e){}
  try{(window._htMarks||[]).forEach(function(g){if(g.parentNode)g.remove();});window._htMarks=[];}catch(e){}
}""",
    'forces clear removes the floats')

# ── stargazer: ghost faces over the free dice ──
sub("""    G._famPeekVals=free.map(function(d){return {lane:d.lane,val:_rollD(d)};});
    famLog('STARGAZER — NEXT ROLL: '+G._famPeekVals.map(function(p){return p.val;}).join(' · '));/* P708: only Ill Omen says OMEN */
    return true;
  }
};""",
    """    G._famPeekVals=free.map(function(d){return {lane:d.lane,val:_rollD(d)};});
    famLog('STARGAZER — NEXT ROLL: '+G._famPeekVals.map(function(p){return p.val;}).join(' · '));/* P708: only Ill Omen says OMEN */
    /* P827: GHOST DICE - each free die shows its promised face, floating
       in starstone blue over the die itself (the fog-float pattern; chip
       overlays are invisible under the canvas). Cleared with the promise
       in _clearRollForces. */
    try{
      (window._pkGhosts||[]).forEach(function(g){if(g.parentNode)g.remove();});
      window._pkGhosts=[];
      free.forEach(function(d,i){
        if(!d.el)return;
        var r=d.el.getBoundingClientRect();if(!(r.width>0))return;
        var g=document.createElement('div');
        g.className='peek-float';g.textContent=String(G._famPeekVals[i].val);
        g.style.left=(r.left+r.width/2)+'px';g.style.top=(r.top+r.height/2)+'px';
        document.body.appendChild(g);window._pkGhosts.push(g);
      });
    }catch(e){}
    return true;
  }
};""",
    'stargazer ghost faces')

# ── honeytrap: honey marks on the armed pair ──
sub("""    }else{
      G._famHoneyVal=pairVal;
      famLog('HONEYTRAP SET — THE NEXT ROLL PULLS A '+pairVal);
    }
    return true;
  }
};""",
    """    }else{
      G._famHoneyVal=pairVal;
      famLog('HONEYTRAP SET — THE NEXT ROLL PULLS A '+pairVal);
      /* P827: the pair wears the honey - marks float over the dice that
         made it (selected or kept chips both stay in G.pool). Cleared
         with the force in _clearRollForces. */
      try{
        (window._htMarks||[]).forEach(function(g){if(g.parentNode)g.remove();});
        window._htMarks=[];
        (G.pool||[]).forEach(function(d){
          if(d.val!==pairVal||!(d.sel||d.committed)||!d.el)return;
          var r=d.el.getBoundingClientRect();if(!(r.width>0))return;
          var g=document.createElement('div');
          g.className='honey-float';g.textContent='\\uD83C\\uDF6F';
          g.style.left=(r.left+r.width/2)+'px';g.style.top=(r.top+r.height/2)+'px';
          document.body.appendChild(g);window._htMarks.push(g);
        });
      }catch(e){}
    }
    return true;
  }
};""",
    'honeytrap honey marks')

# ── honeytrap: the pull lands ON the die ──
sub("""  if(G._famHoneyVal&&free.length){
    var d0=free[0];d0.val=G._famHoneyVal;try{reDrawDieFace(d0);}catch(e){}
    _famPop('HONEYTRAP → '+G._famHoneyVal);
  }""",
    """  if(G._famHoneyVal&&free.length){
    var d0=free[0];d0.val=G._famHoneyVal;try{reDrawDieFace(d0);}catch(e){}
    /* P827: the pull lands ON the pulled die - spawnPop has always taken
       an anchor (P-note at its head); _famPop just never passed one. */
    try{spawnPop('HONEYTRAP \\u2192 '+G._famHoneyVal,d0.el);}catch(e){_famPop('HONEYTRAP \\u2192 '+G._famHoneyVal);}
    try{_fxSpray(d0.el,'#e8b040',12,{speed:70,g:60,size:6,spread:2.2});}catch(e){}
  }""",
    'the pull lands on the die')

# ── vanguard: the primer tests the LIVE card ──
sub("""      var _pcCards=effectiveCards()||[];
      var _pFirst=G.pool[0],_pLast=G.pool[G.pool.length-1];
      var _pcFire=false;
      if(_pcCards.indexOf('vanguard')>=0&&d===_pFirst&&(d.val===1||d.val===5))_pcFire=true;
      else if(_pcCards.indexOf('anchor')>=0&&d===_pLast&&d.val===6)_pcFire=true;
      else if(_pcCards.indexOf('flanks')>=0&&_pFirst!==_pLast){
        if((d===_pFirst&&_pLast&&_pLast.sel)||(d===_pLast&&_pFirst&&_pFirst.sel))_pcFire=true;
      }""",
    """      /* P827: the legacy list (vanguard/anchor/flanks via effectiveCards)
         is retired and effectiveCards() returns [] - this primer could
         never fire for the live card. vanguard_f's tier shapes: I pays
         the first spot, II either end, III both ends. */
      var _vf=(typeof famInst==='function')?famInst('vanguard_f'):null;
      var _pFirst=G.pool[0],_pLast=G.pool[G.pool.length-1];
      var _pcFire=false;
      if(_vf){
        var _vt=_vf.tier||1;
        if(d===_pFirst)_pcFire=true;
        else if(_vt>=2&&d===_pLast)_pcFire=true;
      }""",
    'vanguard primer revived')

# ── vanguard: end-spot hints as each roll settles ──
sub("""  _clearRollForces();/* P556 - spent by this roll either way */
}""",
    """  _clearRollForces();/* P556 - spent by this roll either way */
  /* P827: VANGUARD AIMS - as the roll settles, the paying end spots wear
     a brief gold hint so the player knows where the card pays. Self-
     expiring; per-roll, from the one per-roll visual moment this
     function already owns. */
  try{
    var _vfh=(typeof famInst==='function')?famInst('vanguard_f'):null;
    if(_vfh&&G.pool&&G.pool.length){
      var _vt2=_vfh.tier||1;
      var _spots=[G.pool[0]];
      if(_vt2>=2&&G.pool.length>1)_spots.push(G.pool[G.pool.length-1]);
      _spots.forEach(function(sd){
        if(!sd||!sd.el)return;
        var r=sd.el.getBoundingClientRect();if(!(r.width>0))return;
        var g=document.createElement('div');
        g.className='vang-float';g.textContent='\\u25C6 PAYS';
        g.style.left=(r.left+r.width/2)+'px';g.style.top=(r.top+r.height/2)+'px';
        document.body.appendChild(g);
        setTimeout(function(){if(g.parentNode)g.remove();},2600);
      });
    }
  }catch(e){}
}""",
    'vanguard end-spot hints')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d (%s)' % (len(edits), ', '.join(edits)))
