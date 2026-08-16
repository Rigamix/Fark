# -*- coding: utf-8 -*-
"""P759: the lab tells the truth about the baked look.

Denis asked whether the lab carries the glow changes - auditing that
question found three places where it lies since P757 made his numbers
the game's authored defaults:

1. The mask slider booted at 'off' while the shipped mask is +30
   horizontal - and the vignette sliders at 0/45 while the room ships at
   72/48, so touching one STOMPED the baked room back to zero. The game
   now stashes what it applied (D3X._lookRec) and buildLights initialises
   every slider from the live values.
2. 'reset look' restored PRE-P757 numbers (glow strength 0.78, soft 10,
   mask off...) - the button meant "back to the approved look" and
   delivered a stale one, right after I told Denis to press it. It now
   restores the authored P757 look exactly: glow 0.91/11/3/3.2 +
   1.14/1.24/0, card halo 6/2.5/0.91/floor .42/drop 0, side dim 0.86,
   mask +30 x, vignette 72/48, and the adopted fkBounce back to its
   authored intensity instead of zero.
"""
import io, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
edits = []


def patch(path, pairs):
    s = io.open(path, encoding='utf-8', newline='').read()
    for old, new, label in pairs:
        c = s.count(old)
        if c != 1:
            o2 = old.replace('\n', '\r\n')
            if s.count(o2) == 1:
                old, new = o2, new.replace('\n', '\r\n')
            else:
                sys.exit('ANCHOR x%d for %s (nothing written)' % (c, label))
        s = s.replace(old, new)
        edits.append(label)
    io.open(path, 'w', encoding='utf-8', newline='').write(s)


# game: remember what was applied, so the lab can read it
patch(os.path.join(ROOT, 'fark_proto.html'), [
    (u"""    if(!lk)lk={vgA:72,vgR:48,vgC:0,sh:0};
    var self=this;""",
     u"""    if(!lk)lk={vgA:72,vgR:48,vgC:0,sh:0};
    this._lookRec=lk;/* P759: the lab initialises its sliders from this */
    var self=this;""",
     'game stashes the record'),
])

L = os.path.join(ROOT, 'fark_lab.html')
patch(L, [
    # sliders boot from the LIVE look, not hardcoded zeros
    (u"""  h+='<br><label>vignette <input type="range" min="0" max="80" value="0" oninput="vigSet()" id="vgA"> <span id="lvE">off</span></label>';
  h+='<label>vignette size <input type="range" min="15" max="75" value="45" oninput="vigSet()" id="vgR"></label>';
  h+='<label>centre light <input type="range" min="0" max="60" value="0" oninput="vigSet()" id="vgC"></label>';
  h+='<br><label>shadow depth <input type="range" min="0" max="70" value="0" oninput="shadowSet(this.value)"> <span id="lvSh">normal</span></label>';""",
     u"""  /* P759: the game BOOTS with the baked look applied (P757) - these
     sliders must open at the live values or the first touch stomps the
     room back to zero. D3X._lookRec is what the game actually applied. */
  var _rec=E('D3X._lookRec')||{};
  h+='<br><label>vignette <input type="range" min="0" max="80" value="'+(+_rec.vgA||0)+'" oninput="vigSet()" id="vgA"> <span id="lvE">'+(_rec.vgA>0?_rec.vgA+'%':'off')+'</span></label>';
  h+='<label>vignette size <input type="range" min="15" max="75" value="'+(+_rec.vgR||45)+'" oninput="vigSet()" id="vgR"></label>';
  h+='<label>centre light <input type="range" min="0" max="60" value="'+(+_rec.vgC||0)+'" oninput="vigSet()" id="vgC"></label>';
  h+='<br><label>shadow depth <input type="range" min="0" max="70" value="'+(+_rec.sh||0)+'" oninput="shadowSet(this.value)"> <span id="lvSh">'+(_rec.sh>0?('-'+_rec.sh+'%'):'normal')+'</span></label>';""",
     'sliders open at the live room'),

    (u"""  h+='<br><label>shadow mask <input type="range" min="-100" max="100" value="0" oninput="gradeDice(this.value)" id="dgAmt"> <span id="lvG">off</span></label>';
  h+='<label>mask axis <select id="dgAxis" onchange="gradeDice(document.getElementById(&quot;dgAmt&quot;).value)"><option value="y">vertical</option><option value="x">horizontal</option></select></label>';""",
     u"""  /* P759: the mask ships baked (SIDEDIM_MASK) - open at its live value */
  var _mk=E('D3X.SIDEDIM_MASK')||{axis:'y',amt:0};
  var _mkV=Math.round((_mk.amt||0)*100);
  h+='<br><label>shadow mask <input type="range" min="-100" max="100" value="'+_mkV+'" oninput="gradeDice(this.value)" id="dgAmt"> <span id="lvG">'+(_mkV?((_mkV>0?'+':'')+_mkV+' '+_mk.axis):'off')+'</span></label>';
  h+='<label>mask axis <select id="dgAxis" onchange="gradeDice(document.getElementById(&quot;dgAmt&quot;).value)"><option value="y"'+(_mk.axis!=='x'?' selected':'')+'>vertical</option><option value="x"'+(_mk.axis==='x'?' selected':'')+'>horizontal</option></select></label>';""",
     'mask slider opens live'),

    # the adopted bounce remembers its authored intensity
    (u"""  if(!_bounce)_bounce=dx.scene.getObjectByName('fkBounce')||null;
  if(!_bounce){_bounce=new T.DirectionalLight(0xffe8c8,0);_bounce.name='fkBounce';
    _bounce.position.set(0,-1,0.6);dx.scene.add(_bounce);}""",
     u"""  if(!_bounce){_bounce=dx.scene.getObjectByName('fkBounce')||null;
    if(_bounce&&_bounce.userData._lab0===undefined)
      _bounce.userData._lab0=_bounce.intensity;/* P759: authored base */}
  if(!_bounce){_bounce=new T.DirectionalLight(0xffe8c8,0);_bounce.name='fkBounce';
    _bounce.userData._lab0=0;
    _bounce.position.set(0,-1,0.6);dx.scene.add(_bounce);}""",
     'bounce keeps its authored base'),

    # reset restores the AUTHORED look, not a stale one
    (u"""function lightsReset(){
  try{delete localStorage.fkLabLook;}catch(e){}
  _lights.forEach(function(l){if(l.userData._lab0!==undefined)l.intensity=l.userData._lab0;});
  if(_bounce)_bounce.intensity=0;
  ['vgA','vgC'].forEach(function(id){var e2=document.getElementById(id);if(e2)e2.value=0;});
  vigSet();shadowSet(0);gradeDice(0);
  ['strength',0.78,'soft',10,'rim',3.5,'line',2.4,'sx',1,'sy',1,'dy',0].forEach(function(v,i,arr){
    if(i%2===0)E('D3X.GLOW.'+arr[i]+'='+arr[i+1]);});
  glowSelAll(false);
  buildLights();}""",
     u"""function lightsReset(){
  /* P759: reset means THE AUTHORED LOOK (P757 baked Denis's numbers as
     the game's defaults) - the old body restored pre-P757 values and
     zeroed the mask, so the reset button un-approved the approved look. */
  try{delete localStorage.fkLabLook;}catch(e){}
  _lights.forEach(function(l){if(l.userData._lab0!==undefined)l.intensity=l.userData._lab0;});
  if(_bounce)_bounce.intensity=_bounce.userData._lab0||0;
  var set=function(id,v){var e2=document.getElementById(id);if(e2)e2.value=v;};
  set('vgA',72);set('vgR',48);set('vgC',0);
  vigSet();shadowSet(0);
  E('D3X.SIDEDIM_MAX=0.86');
  var spS=document.getElementById('lvS');if(spS)spS.textContent='0.86';
  set('dgAmt',30);var ax=document.getElementById('dgAxis');if(ax)ax.value='x';
  gradeDice(30);
  [['strength',0.91],['soft',11],['rim',3],['rimPasses',5],['softPasses',1],
   ['line',3.2],['grow',1.004],['clear',0.7],['sx',1.14],['sy',1.24],['dy',0]]
    .forEach(function(p){E('D3X.GLOW.'+p[0]+'='+p[1]);});
  [['soft',6],['rim',2.5],['strength',0.91],['floor',0.42],['dyF',0],
   ['grow',1.05],['round',0.075],['line',0]]
    .forEach(function(p){E('D3X.CARD_GLOW.'+p[0]+'='+p[1]);});
  set('gStr',91);set('gSoft',11);set('gRim',3);set('gLine',3.2);
  set('gSx',114);set('gSy',124);set('gDy',0);
  set('cgSoft',6);set('cgRim',2.5);set('cgStr',91);set('cgFloor',42);set('cgDy',0);
  E('D3X._drawGlow&&D3X._drawGlow()');E('D3X._drawCardGlows&&D3X._drawCardGlows()');
  glowSelAll(false);
  buildLights();
  log('reset to the AUTHORED look - the baked P757 numbers');}""",
     'reset restores the authored look'),
])

print('done: %d (%s)' % (len(edits), ', '.join(edits)))
