# -*- coding: utf-8 -*-
"""P754: the approved look IS the game's look.

Denis: "make it that the lab settings apply to the game."

The lab already persists every approved number to localStorage.fkLabLook
(same origin as the game), but only the lab's own applyLook ever read it
- so the look existed only while the lab was driving. The game reads the
same record at boot now, in D3X._applyLabLook, called once when the 3D
model mounts:

  sd            -> SIDEDIM_MAX
  maskAmt/Axis  -> setGrad (P752/P753's world->screen mask)
  GLOW          -> the dice halo dials (known keys only)
  CG            -> the card halo dials (new in the record)
  lights[]      -> per-light intensity ratios, scene traverse order -
                   the SAME order the lab's buildLights walks
  bounce        -> an extra fill light, named fkBounce
  vgA/vgR/vgC   -> the vignette + centre-light overlays, ported from the
                   lab's vigSet (same element ids, so the lab reuses them)
  sh            -> matchShadows brightness

Double-apply is the trap: the lab attaches to a game that has already
applied the ratios. So the game records what it multiplied in
D3X._lookLights, and the lab's buildLights divides its _lab0 baseline by
that - the sliders read the authored base again. The lab's bounceSet
adopts the game's fkBounce instead of adding a second sun, and saveLook
now also snapshots CARD_GLOW as lk.CG.
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


APPLY = r"""  /* P754: THE APPROVED LOOK IS THE GAME'S LOOK. The lab saves every
     number Denis signs off to localStorage.fkLabLook (same origin); the
     game applies the same record at boot, so standalone play looks like
     the lab session did. The lab compensates when it attaches on top -
     see _lookLights below and buildLights in the lab. */
  _applyLabLook:function(){
    if(this._lookApplied)return;this._lookApplied=1;
    var lk=null;try{lk=JSON.parse(localStorage.fkLabLook||'null');}catch(e){}
    if(!lk)return;
    var self=this;
    try{
      if(lk.sd!==null&&lk.sd!==undefined)this.SIDEDIM_MAX=+lk.sd;
      if(lk.maskAmt!==null&&lk.maskAmt!==undefined)
        this.setGrad(lk.maskAxis||this.GRAD.ax,(+lk.maskAmt)/100);
      /* known keys only: old records carry retired dials (fb*) */
      var KG=['soft','rim','rimPasses','softPasses','line','grow','clear',
              'strength','sx','sy','dy'];
      if(lk.GLOW)KG.forEach(function(k){
        if(lk.GLOW[k]!==undefined)self.GLOW[k]=lk.GLOW[k];});
      var KC=['soft','rim','strength','floor','round','line','col','softCol'];
      if(lk.CG)KC.forEach(function(k){
        if(lk.CG[k]!==undefined)self.CARD_GLOW[k]=lk.CG[k];});
      /* lights: ratios in scene traverse order - the lab's own order */
      if(lk.lights&&lk.lights.length&&this.scene){
        var Ls=[];this.scene.traverse(function(o){if(o.isLight)Ls.push(o);});
        this._lookLights=[];
        lk.lights.forEach(function(r,i){
          if(Ls[i]&&typeof r==='number'&&r>0){
            Ls[i].intensity*=r;self._lookLights[i]=r;}});
      }
      if(lk.bounce&&this.scene&&!this.scene.getObjectByName('fkBounce')){
        var b=new THREE.DirectionalLight(0xffe8c8,+lk.bounce);
        b.name='fkBounce';b.position.set(0,-1,0.6);this.scene.add(b);
      }
      this._applyLookDom(lk);
    }catch(e){try{console.warn('[D3X] look apply failed:',e);}catch(e2){}}
  },
  /* the DOM half: vignette, centre light, shadow depth - ported from the
     lab's vigSet, SAME element ids so an attached lab edits these very
     overlays instead of stacking its own */
  _applyLookDom:function(lk){
    var a=(+lk.vgA||0)/100,r=(+lk.vgR||45),cc=(+lk.vgC||0)/100;
    var msd=document.getElementById('matchShadows');
    if(msd)msd.style.filter=(lk.sh>0)?('brightness('+(1-lk.sh/100)+')'):'';
    if(!(a>0)&&!(cc>0))return;
    var cvs=document.getElementById('d3xCanvas');
    var ms=document.getElementById('screen-match');
    var host=(cvs&&cvs.parentElement)||ms;
    if(!host)return;
    if(getComputedStyle(host).position==='static')host.style.position='relative';
    var place=function(el){
      if(cvs&&cvs.parentElement===host)host.insertBefore(el,cvs);
      else host.appendChild(el);
    };
    var vg=document.getElementById('labVig');
    if(!vg){vg=document.createElement('div');vg.id='labVig';
      vg.style.cssText='position:absolute;inset:0;pointer-events:none;mix-blend-mode:multiply';
      place(vg);}
    vg.style.background='radial-gradient(ellipse at 50% 46%, rgba(16,10,4,0) '+r+'%, rgba(16,10,4,'+a.toFixed(2)+') 100%)';
    var cl=document.getElementById('labCenter');
    if(!cl){cl=document.createElement('div');cl.id='labCenter';
      cl.style.cssText='position:absolute;inset:0;pointer-events:none;mix-blend-mode:screen';
      place(cl);}
    cl.style.background='radial-gradient(ellipse at 50% 46%, rgba(255,214,150,'+cc.toFixed(2)+') 0%, rgba(255,214,150,0) '+Math.max(20,r-5)+'%)';
  },
"""

patch(os.path.join(ROOT, 'fark_proto.html'), [
    (u"  _applyLabLook", None, 'CHECK-ABSENT'),
][0:0] + [
    (u"""      self.proto=proto;self.ready=true;self.loading=false;
      var q=self._need;self._need=[];
      q.forEach(function(f){f&&f();});
      self.frame();""",
     u"""      self.proto=proto;self.ready=true;self.loading=false;
      var q=self._need;self._need=[];
      q.forEach(function(f){f&&f();});
      self.frame();
      try{self._applyLabLook();}catch(e){}/* P754: the approved look */""",
     'apply at mount'),
    (u"  _applyLabLook:PLACEHOLDER", u"x", 'never')
][0:1])

# insert the two methods before _gradHook
s = io.open(os.path.join(ROOT, 'fark_proto.html'), encoding='utf-8', newline='').read()
k = s.find("  _gradHook:function(o){")
if k < 0:
    sys.exit('_gradHook anchor lost (apply-at-mount already written!)')
# back up to the comment that precedes _gradHook
ci = s.rfind("  /* P752: the world-space mask", 0, k)
ins = ci if ci > 0 else k
s = s[:ins] + APPLY + s[ins:]
io.open(os.path.join(ROOT, 'fark_proto.html'), 'w', encoding='utf-8', newline='').write(s)
edits.append('game applyLook methods')

# ── lab: compensate, adopt, snapshot ──
patch(os.path.join(ROOT, 'fark_lab.html'), [
    (u"""  _lights.forEach(function(l,i){
    l.userData._lab0=l.userData._lab0===undefined?l.intensity:l.userData._lab0;""",
     u"""  /* P754: the game may have applied the saved ratios at boot already -
     divide them back out so _lab0 is the AUTHORED base and the sliders
     do not double-scale */
  var _gr=E('D3X._lookLights')||[];
  _lights.forEach(function(l,i){
    if(l.userData._lab0===undefined)
      l.userData._lab0=l.intensity/((typeof _gr[i]==='number'&&_gr[i]>0)?_gr[i]:1);""",
     'buildLights compensates'),

    (u"""  if(!_bounce){_bounce=new T.DirectionalLight(0xffe8c8,0);
    _bounce.position.set(0,-1,0.6);dx.scene.add(_bounce);}""",
     u"""  /* P754: adopt the game's own boot-applied fill rather than adding a
     second sun on top of it */
  if(!_bounce)_bounce=dx.scene.getObjectByName('fkBounce')||null;
  if(!_bounce){_bounce=new T.DirectionalLight(0xffe8c8,0);_bounce.name='fkBounce';
    _bounce.position.set(0,-1,0.6);dx.scene.add(_bounce);}""",
     'bounce adopted'),

    (u"""      GLOW:E('JSON.parse(JSON.stringify(D3X.GLOW))')};
    try{localStorage.fkLabLook=JSON.stringify(lk);}catch(e){}""",
     u"""      GLOW:E('JSON.parse(JSON.stringify(D3X.GLOW))'),
      CG:E('JSON.parse(JSON.stringify(D3X.CARD_GLOW))')};/* P754 */
    try{localStorage.fkLabLook=JSON.stringify(lk);}catch(e){}""",
     'saveLook snapshots CG'),

    (u"""    Object.keys(map).forEach(function(k){
      if(lk.GLOW[k]!==undefined)set(map[k][0],lk.GLOW[k]*map[k][1]);});
    E('D3X._drawGlow&&D3X._drawGlow()');}""",
     u"""    Object.keys(map).forEach(function(k){
      if(lk.GLOW[k]!==undefined)set(map[k][0],lk.GLOW[k]*map[k][1]);});
    E('D3X._drawGlow&&D3X._drawGlow()');}
  /* P754: the card halo's own dials ride the same record */
  if(lk.CG){Object.keys(lk.CG).forEach(function(k){
      E('D3X.CARD_GLOW.'+k+'='+JSON.stringify(lk.CG[k]));});
    var cmap={soft:['cgSoft',1],rim:['cgRim',1],strength:['cgStr',100],floor:['cgFloor',100]};
    Object.keys(cmap).forEach(function(k){
      if(lk.CG[k]!==undefined)set(cmap[k][0],lk.CG[k]*cmap[k][1]);});}""",
     'applyLook reads CG'),
])

print('done: %d (%s)' % (len(edits), ', '.join(edits)))
