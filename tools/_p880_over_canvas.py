# -*- coding: utf-8 -*-
u"""P880 (FX BRIEF step 4): the over-canvas.

A twin of _glowCv with its own id, z-index 42 and its own draw pass. It exists
because the glow canvas cannot carry states: dgCanvas is z-index 3, UNDER the
dice at 41, and _drawGlow refuses to run in two situations a state has to
survive.

THE TWO GUARDS IT MUST NOT INHERIT, and why each would be fatal here:
  - the selection wake condition. _drawGlow paints only while some die carries
    the keep class or a card mark. A state is a property of a die nobody is
    touching - a frozen die, a fogged spot - so a state layer with that guard
    paints exactly when there is no state to paint.
  - the _rolling() skip. It is the whole of the harness constraint: the pass is
    abandoned while the physics tape plays, which headless is ~19s. A state has
    to survive a roll, because surviving the roll is what makes it a state
    rather than a flourish.

WHAT IT KEEPS. One per-frame test: does any die actually carry a registered
state class. That is the same SHAPE of guard as the one it drops, but it is
keyed on the registry rather than on selection, so a state wakes it and the
absence of any state is the only thing that lets it sleep. Under P879's ruling
the cost bound is per-frame - a few thin hulls on an empty surface - and holds
however long the state lives, which is what makes it safe to keep painting for
a state that never ends.

THE SURFACE HAS AN OWNER. The pass clears the whole canvas each frame, so
anything painting to it from outside the pass is erased on the next one. Step
5's primitives must therefore REGISTER a form rather than paint behind the
pass's back. Recording that here because it is the kind of collision that is
obvious while writing the owner and invisible three patches later.

Forms are step 7; RIM is built because the pass needs one painter to be
testable, and it delegates to _paintHalo so a ported state cannot drift from
the selection glow it is supposed to look like.
"""
import io, os, sys, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'fark_proto.html')
s = io.open(P, encoding='utf-8', newline='').read()
edits = []


def sub(old, new, label):
    global s
    if s.count(old) == 1:
        s = s.replace(old, new); edits.append(label); return
    pat = re.escape(old).replace('\\\n', '\n').replace('\n', '\\r?\n')
    ms = list(re.finditer(pat, s))
    if len(ms) != 1:
        sys.exit('ANCHOR x%d for %s (nothing written)' % (len(ms), label))
    m = ms[0]
    rep = new.replace('\n', '\r\n') if '\r\n' in m.group(0) else new
    s = s[:m.start()] + rep + s[m.end():]
    edits.append(label)


ANCHOR = u"""  /* the die's 8 corners projected to screen space, gift-wrapped */
  _hullOf:function(d,sc,grow){"""

NEW = u"""  /* P880: THE OVER-CANVAS. dgCanvas is z-index 3, UNDER the dice at 41, which
     is right for a glow bleeding out from behind a die and wrong for a state
     that has to sit ON it. 42 is above the dice canvas at 41 and below the
     player's card row, which the base rule also puts at 42 but the match
     screen lifts to 45 - so on this screen, and only on this screen, 42 is
     free. */
  _stateCv:function(){
    var sc=document.getElementById('screen-match');
    if(!sc)return null;
    var cv=document.getElementById('dsCanvas');
    if(!cv){
      cv=document.createElement('canvas');cv.id='dsCanvas';
      cv.style.cssText='position:absolute;inset:0;width:100%;height:100%;'
        +'pointer-events:none;z-index:42';
      sc.appendChild(cv);
    }
    return cv;
  },
  /* Registered state forms. Empty here on purpose - the forms are step 7 and
     the ports come with their own patch. An entry is
     {cls:'die-frozen', ink:'#9ab0d0', form:'rim'}; `ink` is the state's
     EXISTING colour from ENCH_ICONS or FKFX.meta, never a new one. */
  STATE_FORMS:[],
  /* THE STATE PASS. Deliberately not _drawGlow: it must not inherit either of
     that painter's guards. _drawGlow skips whenever no die is being kept or
     card-marked (a state belongs to a die nobody is touching) and whenever
     _rolling() is true (a state has to survive the roll - that is what makes
     it a state). What stays is one test keyed on the REGISTRY: if no die
     carries a registered class there is nothing to draw, which is the only
     thing that may put this pass to sleep.
     THE PASS OWNS THE SURFACE. It clears its canvas every frame, so anything
     painting here from outside is erased on the next one - register a form,
     do not paint behind it. */
  _drawStates:function(){
    this._statePasses=(this._statePasses||0)+1;
    var cv=document.getElementById('dsCanvas'),i,d;
    var forms=this.STATE_FORMS||[],want=[];
    for(i=0;i<this.dice.length;i++){
      d=this.dice[i];
      if(!d.match||!d.obj.visible||!d.chip)continue;
      for(var f=0;f<forms.length;f++){
        if(d.chip.classList.contains(forms[f].cls))want.push({d:d,form:forms[f]});
      }
    }
    if(!want.length){
      if(cv&&this._stateInk){
        var c0=cv.getContext('2d');
        c0.setTransform(1,0,0,1,0,0);c0.clearRect(0,0,cv.width,cv.height);
        this._stateInk=false;
      }
      return;
    }
    cv=this._stateCv();if(!cv)return;
    var scEl=document.getElementById('screen-match');
    if(!scEl)return;
    var sc=scEl.getBoundingClientRect();
    if(sc.width<10)return;
    /* same raster argument as the glow (P739): these are thin crisp rims, so
       they are painted at the display's resolution, not capped at 2x. */
    var dpr=Math.min(devicePixelRatio||1,this.GLOW_DPR_MAX||3);
    if(cv.width!==Math.round(sc.width*dpr)||cv.height!==Math.round(sc.height*dpr)){
      cv.width=Math.round(sc.width*dpr);cv.height=Math.round(sc.height*dpr);
    }
    var x=cv.getContext('2d');
    x.setTransform(dpr,0,0,dpr,0,0);
    x.clearRect(0,0,sc.width,sc.height);
    this._stateInk=true;
    var self=this,G=this.GLOW,byInk={};
    want.forEach(function(w){
      var h=self._hullOf(w.d,sc,G.grow);
      if(!h)return;
      var k=(w.form.form||'rim')+'|'+w.form.ink;
      (byInk[k]=byInk[k]||[]).push(h);
    });
    /* RIM is the only form built here; VEIL, CRUST and DIM arrive with the
       ports at step 7. It delegates to _paintHalo so a state that is supposed
       to look like the keep glow cannot drift away from it. */
    for(var k in byInk){
      var ink=k.split('|')[1];
      this._paintHalo(cv,x,sc,dpr,byInk[k],ink,ink,1);
    }
  },
  /* the die's 8 corners projected to screen space, gift-wrapped */
  _hullOf:function(d,sc,grow){"""

sub(ANCHOR, NEW, '1 the over-canvas and its pass')

sub(u"""    try{this._drawGlow();}catch(e){}
  },""",
    u"""    try{this._drawGlow();}catch(e){}
    /* P880: the state pass runs after the glow and never instead of it - they
       own different surfaces (3 under the dice, 42 over them) and neither
       clears the other's. */
    try{this._drawStates();}catch(e){}
  },""",
    '2 wired into the frame hook')

# ── post-asserts: the two forbidden guards must be absent from the new pass ──
_a = s.index('_drawStates:function(){')
_b = s.index('_hullOf:function(d,sc,grow){', _a)
body = s[_a:_b]
if '_rolling()' in body:
    sys.exit('the state pass inherited the _rolling skip (nothing written)')
for bad in ("'selected'", 'cardmark'):
    if bad in body:
        sys.exit('the state pass inherited the selection wake condition '
                 '(nothing written)')
# scoped to the inline style this patch writes: a bare z-index:42 also
# matches the card row's base rule at 1253, which is a different element.
if s.count("cv.id='dsCanvas'") != 1:
    sys.exit('the canvas id is not written exactly once (nothing written)')
if s.count("+'pointer-events:none;z-index:42';") != 1:
    sys.exit('the canvas layer is not set exactly once (nothing written)')
if s.count('this._drawStates();') != 1:
    sys.exit('the pass is not called exactly once (nothing written)')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d edits (%s)' % (len(edits), ', '.join(edits)))
