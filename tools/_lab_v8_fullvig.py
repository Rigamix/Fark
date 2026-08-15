# -*- coding: utf-8 -*-
"""Lab v8: Denis's follow-ups on the approved look.
- The vignette covers the WHOLE screen, under the UI: both layers now
  insert into #screen-match right after #matchShadows in DOM order - the
  room art and shadows sit below, the dice canvas / rows / HUD / buttons
  all come later in the DOM and paint above. No z guessing.
- Die targets finally MOVE: the sliders wrote CSS onto the chip slot,
  which settled 3D dice ignore (their homes are measured, cached). A tiny
  injected frame hook applies per-die lab offsets to the MESH after the
  game's own frame: position (px converted through the parent scale),
  scale multiplier, z-rotation, material opacity. Cards keep DOM styles.
- Die dresser: works off the picked die target with clear logging, and
  the reskin is verified.
- 'copy look numbers': dumps every look dial + D3X.GLOW into the export
  box so Denis can paste his approved numbers straight into chat."""
import io, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'fark_lab.html')
s = io.open(P, encoding='utf-8', newline='').read()
n = 0


def sub(old, new, label):
    global s, n
    c = s.count(old)
    if c != 1:
        sys.exit('ANCHOR x%d for %s' % (c, label))
    s = s.replace(old, new)
    n += 1
    print('  ok  ' + label)


# 1) full-screen vignette via DOM order
sub(u"""function vigSet(){
  /* VIGNETTE, not a wash: radial darkness with the centre kept bright,
     living in the DICE AREA so the HUD and buttons never darken. The
     centre pool is its own screen-blend layer with its own slider. */
  gw();
  var host=W.document.querySelector('#screen-match .dice-area')
        ||W.document.getElementById('screen-match');
  if(!host)return;
  var a=(+document.getElementById('vgA').value)/100;
  var r=+document.getElementById('vgR').value;
  var c=(+document.getElementById('vgC').value)/100;
  var cvs=W.document.getElementById('d3xCanvas');
  var z=cvs?(parseInt(getComputedStyle(cvs).zIndex)||0):0;
  var vg=W.document.getElementById('labVig');
  if(!vg){vg=W.document.createElement('div');vg.id='labVig';
    vg.style.cssText='position:absolute;inset:0;pointer-events:none;mix-blend-mode:multiply;z-index:'+(z-1);
    host.style.position=host.style.position||'relative';host.appendChild(vg);}
  vg.style.background='radial-gradient(ellipse at 50% 46%, rgba(16,10,4,0) '+r+'%, rgba(16,10,4,'+a.toFixed(2)+') 100%)';
  var cl=W.document.getElementById('labCenter');
  if(!cl){cl=W.document.createElement('div');cl.id='labCenter';
    cl.style.cssText='position:absolute;inset:0;pointer-events:none;mix-blend-mode:screen;z-index:'+(z-1);
    host.appendChild(cl);}
  cl.style.background='radial-gradient(ellipse at 50% 46%, rgba(255,214,150,'+c.toFixed(2)+') 0%, rgba(255,214,150,0) '+Math.max(20,r-5)+'%)';
  var sp=document.getElementById('lvE');if(sp)sp.textContent=a>0?Math.round(a*100)+'%':'off';}""",
    u"""function vigSet(){
  /* VIGNETTE, full screen, UNDER the UI: both layers insert right after
     #matchShadows in DOM ORDER - room art and shadows sit below them,
     the dice canvas / rows / HUD / buttons come later in the DOM and
     paint above. Denis: 'full screen, just under the UI elements'. */
  gw();
  var ms=W.document.getElementById('screen-match');if(!ms)return;
  var after=W.document.getElementById('matchShadows');
  var a=(+document.getElementById('vgA').value)/100;
  var r=+document.getElementById('vgR').value;
  var c=(+document.getElementById('vgC').value)/100;
  var place=function(el){
    if(after&&after.parentNode===ms)ms.insertBefore(el,after.nextSibling);
    else ms.insertBefore(el,ms.firstChild?ms.firstChild.nextSibling:null);
  };
  var vg=W.document.getElementById('labVig');
  if(!vg){vg=W.document.createElement('div');vg.id='labVig';
    vg.style.cssText='position:absolute;inset:0;pointer-events:none;mix-blend-mode:multiply';
    ms.style.position=ms.style.position||'relative';place(vg);}
  vg.style.background='radial-gradient(ellipse at 50% 46%, rgba(16,10,4,0) '+r+'%, rgba(16,10,4,'+a.toFixed(2)+') 100%)';
  var cl=W.document.getElementById('labCenter');
  if(!cl){cl=W.document.createElement('div');cl.id='labCenter';
    cl.style.cssText='position:absolute;inset:0;pointer-events:none;mix-blend-mode:screen';
    place(cl);}
  cl.style.background='radial-gradient(ellipse at 50% 46%, rgba(255,214,150,'+c.toFixed(2)+') 0%, rgba(255,214,150,0) '+Math.max(20,r-5)+'%)';
  var sp=document.getElementById('lvE');if(sp)sp.textContent=a>0?Math.round(a*100)+'%':'off';}""",
    'full-screen vignette under the UI')

# 2) die targets drive the mesh through a frame hook
sub(u"""function applyProps(){var el=tEl();if(el)setProps(el,props());}""",
    u"""function _dieHook(){
  /* settled 3D dice ignore CSS on their chip slot (homes are measured
     and cached) - so die offsets apply to the MESH, after the game's
     own frame, through one injected wrapper. */
  gw();
  if(W.__labEval('window.__labFrameHook'))return;
  W.__labEval("window.__labFrameHook=1;window.__labDieFx={};"
    +"var _lf=D3X.frame.bind(D3X);"
    +"D3X.frame=function(){_lf();"
    +"var L=window.__labDieFx;"
    +"var ds=D3X.dice.filter(function(x){return x.match&&x.chip;});"
    +"Object.keys(L).forEach(function(i){var o=L[i],d=ds[+i];if(!d||!o)return;"
    +"var ps=(d.obj.parent&&d.obj.parent.scale.x)||1;"
    +"if(o.dx)d.obj.position.x+=o.dx/ps;"
    +"if(o.dy)d.obj.position.y-=o.dy/ps;"
    +"if(o.sc!==1)d.obj.scale.multiplyScalar(o.sc);"
    +"if(o.rt)d.obj.rotateZ(o.rt);"
    +"d.obj.traverse(function(m){if(!m.isMesh||!m.material)return;"
    +"if(o.op<1){m.material.transparent=true;m.material.opacity=o.op;m.userData._labOp=1;}"
    +"else if(m.userData._labOp){m.material.opacity=1;delete m.userData._labOp;}});"
    +"});};");
}
function applyProps(){
  var p=props();
  if(target&&target.k==='die'){
    _dieHook();
    var cfg={dx:p.dx,dy:p.dy,sc:p.sc/100,op:p.op/100,rt:p.rt*Math.PI/180};
    E('window.__labDieFx['+target.i+']='+JSON.stringify(cfg));
    return;
  }
  var el=tEl();if(el)setProps(el,p);
}""",
    'die targets drive the mesh')

sub(u"""function resetProps(){var el=tEl();if(!el)return;
  ['pDx','pDy','pRt'].forEach(function(id){document.getElementById(id).value=0;});
  document.getElementById('pSc').value=100;document.getElementById('pOp').value=100;
  el.style.translate='';el.style.scale='';el.style.opacity='';el.style.rotate='';}""",
    u"""function resetProps(){
  ['pDx','pDy','pRt'].forEach(function(id){document.getElementById(id).value=0;});
  document.getElementById('pSc').value=100;document.getElementById('pOp').value=100;
  if(target&&target.k==='die'){
    E('window.__labDieFx&&delete window.__labDieFx['+target.i+']');
    E('window.__labDieFx&&Object.keys(window.__labDieFx).length===0&&D3X.dice.forEach(function(d){d.obj&&d.obj.traverse(function(m){if(m.isMesh&&m.material&&m.userData._labOp){m.material.opacity=1;delete m.userData._labOp;}});})');
    return;
  }
  var el=tEl();if(!el)return;
  el.style.translate='';el.style.scale='';el.style.opacity='';el.style.rotate='';}""",
    'reset clears mesh offsets')

# 3) the keyframe player routes through applyProps-style logic for dice
sub(u"""function playRecipe(){
  var el=tEl();if(!el&&rec.keys.length)return log('pick a target first');""",
    u"""function _setTargetProps(p){
  if(target&&target.k==='die'){
    _dieHook();
    E('window.__labDieFx['+target.i+']='+JSON.stringify(
      {dx:p.dx,dy:p.dy,sc:p.sc/100,op:p.op/100,rt:p.rt*Math.PI/180}));
    return true;
  }
  var el=tEl();if(el){setProps(el,p);return true;}
  return false;
}
function playRecipe(){
  var el=tEl();if(!el&&rec.keys.length&&!(target&&target.k==='die'))return log('pick a target first');""",
    'shared prop router')

sub(u"""  var step=function(now){
    var t=now-t0;
    if(el){var p=lerpAt(t);if(p)setProps(el,p);}""",
    u"""  var step=function(now){
    var t=now-t0;
    var p=lerpAt(t);if(p)_setTargetProps(p);""",
    'player routes dice to the mesh')

sub(u"""function scrubTo(t){stopRecipe();
  document.getElementById('scrubT').textContent=t+'ms';
  var el=tEl();if(!el)return;
  var p=lerpAt(t);if(p)setProps(el,p);}""",
    u"""function scrubTo(t){stopRecipe();
  document.getElementById('scrubT').textContent=t+'ms';
  var p=lerpAt(t);if(p)_setTargetProps(p);}""",
    'scrub routes too')

# 4) copy-look button + dresser logging
sub(u"""  h+='<button onclick="lightsReset()" style="margin-left:8px">reset look</button>';""",
    u"""  h+='<button onclick="lightsReset()" style="margin-left:8px">reset look</button>';
  h+='<button onclick="copyLook()">copy look numbers \\u2193</button>';""",
    'copy look button')

sub(u"""function lightsReset(){""",
    u"""function copyLook(){
  var v=function(id){var e2=document.getElementById(id);return e2?+e2.value:null;};
  var lookNums={
    vignette:v('vgA'),vignetteSize:v('vgR'),centreLight:v('vgC'),
    shadowDepth:(document.getElementById('lvSh')||{}).textContent,
    sideShadowMax:E('D3X.SIDEDIM_MAX'),
    shadowMask:E('window.__labDimGrad'),
    lights:_lights.map(function(l){return {type:l.type,intensity:+l.intensity.toFixed(3)};}),
    bounce:_bounce?+_bounce.intensity.toFixed(3):0,
    GLOW:E('JSON.parse(JSON.stringify(D3X.GLOW))')
  };
  document.getElementById('exportBox').value=JSON.stringify(lookNums,null,1);
  showTab(2);
  log('look numbers in the export box (Advanced tab) - copy them into chat');
}
function lightsReset(){""",
    'copyLook dumps the dials')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d edits' % n)
