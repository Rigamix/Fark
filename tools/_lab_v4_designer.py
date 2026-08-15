# -*- coding: utf-8 -*-
"""Lab v4: the designer's second pass (VFX_LANGUAGE.md section 10).

Amber becomes a MATERIAL: Phong specular hot-spot, nested rim shells
(cheap Fresnel depth), a ghost pass of the die's own textured mesh
(refraction blur), drifting inclusion bubbles, viscous drip particles,
and a trap-snap jitter - each with a slider in the Shell studio. Plus
the family-wide upgrades: STRIKE and BREAK get the hit-frame flash and
hanging dust/smoke, PAY sparks hang with a light column at power 2+,
FATE gets beam + twinkles, TRANSFORM gets the afterimage ghost."""
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


# 1) Shell studio sliders
sub(u"""    <label>shell corner% <input type="range" id="pCr" min="0" max="30" value="12"></label>
    <button onclick="resetProps()">reset target</button>""",
    u"""    <button onclick="resetProps()">reset target</button>
  </div>
  <div class="row" style="border:1px dashed #3a2c18;border-radius:4px;padding:4px 8px">
    <b style="color:#c8a45c;font-size:11px;margin-right:6px">SHELL STUDIO</b>
    <label>corner% <input type="range" id="pCr" min="0" max="30" value="12"></label>
    <label>opacity <input type="range" id="shOp" min="10" max="90" value="42"></label>
    <label>specular <input type="range" id="shSpec" min="0" max="120" value="45"></label>
    <label>rims <select id="shRims"><option>1</option><option selected>2</option><option>3</option></select></label>
    <label>bubbles <input type="range" id="shBub" min="0" max="8" value="4"></label>
    <label>ghost blur% <input type="range" id="shGhost" min="0" max="60" value="25"></label>""",
    'shell studio sliders')

# 2) FX palette gains flash / beam / ghost
sub(u"var FXDEFS=['spray','glow','amberShell','clearShell','break','shield','candle','beat-gain','beat-hit','beat-churn','beat-steal'];",
    u"var FXDEFS=['spray','glow','flash','beam','ghost','amberShell','clearShell','break','shield','candle','beat-gain','beat-hit','beat-churn','beat-steal'];",
    'FXDEFS extended')

# 3) fire() learns flash / beam / ghost
sub(u"""    else if(fx==='amberShell'){amberShell(p.col);}""",
    u"""    else if(fx==='flash'){if(!el)return log('no target');
      var fl=W.document.createElement('div');
      fl.style.cssText='position:absolute;inset:-4%;border-radius:18%;background:#fff;opacity:.85;pointer-events:none;z-index:8;transition:opacity 90ms ease-out';
      el.style.position=el.style.position||'relative';el.appendChild(fl);
      requestAnimationFrame(function(){fl.style.opacity='0';});
      setTimeout(function(){fl.remove();},140);}
    else if(fx==='beam'){if(!el)return log('no target');
      var bm=W.document.createElement('div');
      bm.style.cssText='position:absolute;left:20%;width:60%;bottom:55%;height:230%;pointer-events:none;z-index:4;'
        +'background:linear-gradient(to top,'+p.col+'55,transparent);mix-blend-mode:screen;'
        +'opacity:0;transition:opacity '+(p.ms/3)+'ms ease-out';
      el.style.position=el.style.position||'relative';el.appendChild(bm);
      requestAnimationFrame(function(){bm.style.opacity='1';});
      setTimeout(function(){bm.style.opacity='0';},p.ms*0.55);
      setTimeout(function(){bm.remove();},p.ms+200);}
    else if(fx==='ghost'){
      var d3=d3die();if(!d3||!d3.obj)return log('ghost needs a DIE target');
      var T2=W.__labEval('THREE');var bd=null;
      d3.obj.traverse(function(o){if(!bd&&o.isMesh&&!o.userData.outline)bd=o;});
      if(!bd)return;
      var gm2=new T2.Mesh(bd.geometry,new T2.MeshBasicMaterial({map:bd.material.map||null,
        color:new T2.Color(p.col),transparent:true,opacity:0.4,depthWrite:false}));
      gm2.userData.outline=true;gm2.scale.setScalar(1.05);
      d3.obj.add(gm2);
      var t0g=performance.now();
      (function fade(){var k=(performance.now()-t0g)/(p.ms||400);
        if(k>=1){d3.obj.remove(gm2);gm2.material.dispose();return;}
        gm2.material.opacity=0.4*(1-k);gm2.scale.setScalar(1.05+k*0.1);
        requestAnimationFrame(fade);})();}
    else if(fx==='amberShell'){amberShell(p.col);}""",
    'flash + beam + ghost FX')

# 4) amberShell v2 - the material pass
sub(u"""function amberShell(col){
  var d=d3die();if(!d||!d.obj)return log('amberShell needs a DIE target');
  if(d.obj.getObjectByName('labShell'))return log('shell already on');
  var T=W.__labEval('THREE');
  var body=null;
  d.obj.traverse(function(o){if(!body&&o.isMesh&&!o.userData.outline)body=o;});
  if(!body)return log('no body mesh');
  var c=new T.Color(col);
  body.geometry.computeBoundingBox();
  var bb=body.geometry.boundingBox,sz=(bb.max.x-bb.min.x)*1.16;
  var rPct=+((document.getElementById('pCr')||{}).value||12);
  var sh=new T.Mesh(roundedBoxGeo(T,sz,rPct,4),new T.MeshBasicMaterial({
    color:c,transparent:true,opacity:0.5,depthWrite:false}));
  sh.name='labShell';sh.userData.outline=true;/* every die pass skips it */
  d.obj.add(sh);
  /* the faces take the amber light: lerp material colour toward it */
  d.obj.traverse(function(o){
    if(!o.isMesh||!o.material||o.userData.outline)return;
    if(!o.userData._labCol)o.userData._labCol=o.material.color.clone();
    var b=o.userData._labCol;
    o.material.color.setRGB(b.r*0.3+c.r*0.7,b.g*0.3+c.g*0.7,b.b*0.3+c.b*0.7);
  });
  log('amber shell ON (die '+target.i+')');}""",
    u"""function shellOpts(){var v=function(id,dflt){var e2=document.getElementById(id);return e2?+e2.value:dflt;};
  return {corner:v('pCr',12),op:v('shOp',42)/100,spec:v('shSpec',45),
    rims:v('shRims',2),bub:v('shBub',4),ghost:v('shGhost',25)/100};}
function amberShell(col){
  /* VFX_LANGUAGE.md section 10 - amber as a MATERIAL:
     Phong specular (glossy) + nested rims (cheap Fresnel depth) +
     ghost pass of the die's own textured mesh (refraction blur) +
     drifting inclusion bubbles. Every knob is a Shell studio slider. */
  var d=d3die();if(!d||!d.obj)return log('amberShell needs a DIE target');
  if(d.obj.getObjectByName('labShell'))return log('shell already on');
  var T=W.__labEval('THREE');
  var body=null;
  d.obj.traverse(function(o){if(!body&&o.isMesh&&!o.userData.outline)body=o;});
  if(!body)return log('no body mesh');
  var c=new T.Color(col),os=shellOpts();
  body.geometry.computeBoundingBox();
  var bb=body.geometry.boundingBox,sz=(bb.max.x-bb.min.x);
  var grp=new T.Group();grp.name='labShell';grp.userData.outline=true;
  for(var i=0;i<os.rims;i++){
    var mesh=new T.Mesh(roundedBoxGeo(T,sz*(1.10+i*0.06),os.corner,4),
      new T.MeshPhongMaterial({color:c,transparent:true,
        opacity:os.op*(i===0?1:0.4),depthWrite:false,
        specular:new T.Color(0xfff6e0),shininess:os.spec}));
    mesh.userData.outline=true;grp.add(mesh);
  }
  if(os.ghost>0){
    var gh=new T.Mesh(body.geometry,new T.MeshBasicMaterial({
      map:body.material.map||null,color:c,transparent:true,
      opacity:os.ghost,depthWrite:false}));
    gh.scale.setScalar(1.035);gh.userData.outline=true;grp.add(gh);
  }
  grp.userData.bubbles=[];grp.userData.lim=sz*0.32;
  for(var b=0;b<os.bub;b++){
    var bmesh=new T.Mesh(new T.SphereGeometry(sz*(0.025+Math.random()*0.02),6,6),
      new T.MeshPhongMaterial({color:0xffe8c0,transparent:true,opacity:0.5,
        specular:0xffffff,shininess:60,depthWrite:false}));
    bmesh.userData.outline=true;
    bmesh.position.set((Math.random()-0.5)*sz*0.5,(Math.random()-0.5)*sz*0.5,(Math.random()-0.5)*sz*0.5);
    bmesh.userData.ph=Math.random()*6.28;bmesh.userData.sp=0.6+Math.random()*0.8;
    grp.add(bmesh);grp.userData.bubbles.push(bmesh);
  }
  d.obj.add(grp);
  /* the faces take the amber light - lighter than v1: the rims and ghost
     carry the depth now, the tint only warms */
  d.obj.traverse(function(o){
    if(!o.isMesh||!o.material||o.userData.outline)return;
    if(!o.userData._labCol)o.userData._labCol=o.material.color.clone();
    var b2=o.userData._labCol;
    o.material.color.setRGB(b2.r*0.45+c.r*0.55,b2.g*0.45+c.g*0.55,b2.b*0.45+c.b*0.55);
  });
  _driftOn();
  log('amber shell ON (die '+target.i+') - rims '+os.rims+', bubbles '+os.bub);}
var _drift=null;
function _driftOn(){
  if(_drift)return;
  var step=function(){
    var any=false;
    try{
      var dx=E('window.D3X');
      dx&&dx.dice.forEach(function(dd){
        var g=dd.obj&&dd.obj.getObjectByName&&dd.obj.getObjectByName('labShell');
        if(!g||!g.userData.bubbles||!g.userData.bubbles.length)return;
        any=true;
        var t=performance.now()/1000,lim=g.userData.lim||0.3;
        g.userData.bubbles.forEach(function(b){
          b.position.y+=lim*0.004*b.userData.sp;
          b.position.x+=Math.sin(t*2+b.userData.ph)*lim*0.002;
          if(b.position.y>lim)b.position.y=-lim;
        });
      });
    }catch(e){}
    if(any)_drift=requestAnimationFrame(step);else _drift=null;
  };
  _drift=requestAnimationFrame(step);
}""",
    'amberShell v2 - the material')

# 5) clearShell handles the group
sub(u"""function clearShell(){
  var d=d3die();if(!d||!d.obj)return log('clearShell needs a DIE target');
  var sh=d.obj.getObjectByName('labShell');
  if(sh){d.obj.remove(sh);sh.material.dispose();}""",
    u"""function clearShell(){
  var d=d3die();if(!d||!d.obj)return log('clearShell needs a DIE target');
  var sh=d.obj.getObjectByName('labShell');
  if(sh){d.obj.remove(sh);
    sh.traverse&&sh.traverse(function(o){if(o.material&&o.material.dispose)o.material.dispose();});
    if(sh.material&&sh.material.dispose)sh.material.dispose();}""",
    'clearShell disposes the group')

# 6) family templates - the second pass
sub(u"""var FAM_T={
  SET:function(c,P){return {keys:[K(0,{}),K(160,{sc:93},'ease-out'),K(340,{sc:100},'back-out')],
    fx:[SN(0,'set',P),F(60,'amberShell',{col:c}),F(90,'spray',{col:c,count:8+4*P,speed:65,g:110,size:6,spread:1.8})]};},
  PAY:function(c,P){return {keys:[],
    fx:[SN(0,'chime',P),F(0,'spray',{col:c,count:10+5*P,speed:60,g:-40,size:7,spread:1.2}),
        F(0,'glow',{col:c,size:6+2*P,ms:500})]};},
  COIN:function(c,P){return {keys:[],
    fx:[SN(0,'coin',P),F(0,'spray',{col:c,count:6+3*P,speed:90,g:60,size:6,spread:0.9})]};},
  STRIKE:function(c,P){return {keys:[K(0,{}),K(60,{dx:-7},'ease-in'),K(120,{dx:7}),K(180,{dx:-3}),K(240,{dx:0},'back-out')],
    fx:[SN(0,'thud',P),F(20,'spray',{col:c,count:10+4*P,speed:70,g:220,size:6,spread:2.6})]};},
  TRANSFORM:function(c,P){return {keys:[K(0,{}),K(300,{rt:180,sc:108},'ease-out'),K(620,{rt:360,sc:100},'back-out')],
    fx:[SN(0,'shimmer',P),F(150,'spray',{col:c,count:12+4*P,speed:55,g:-10,size:6,spread:3})]};},
  FATE:function(c,P){return {keys:[K(0,{}),K(450,{op:78},'ease-out'),K(900,{op:100},'ease-out')],
    fx:[SN(0,'bell',P),F(0,'glow',{col:c,size:8+2*P,ms:900})]};},
  BREAK:function(c,P){return {keys:[],
    fx:[SN(0,'crack',P),F(40,'break',{col:c,count:22+6*P,speed:110,g:180,size:6,ms:520})]};},
  ARM:function(c,P){return {keys:[K(0,{}),K(140,{sc:108},'back-out'),K(300,{sc:100}),K(440,{sc:105},'back-out'),K(600,{sc:100})],
    fx:[SN(0,'drum',P),F(120,'glow',{col:c,size:5+2*P,ms:400})]};},
  LEDGER:function(c,P){return {keys:[],
    fx:[SN(0,'scratch',P),F(0,'announce',{text:'THE LEDGER NOTES IT',annCol:'gold'})]};}
};""",
    u"""var FAM_T={
  /* section 10: each family interrogated as a MATERIAL/physical event.
     SET snaps shut (jitter) and DRIPS (viscous: few, large, slow, heavy). */
  SET:function(c,P){return {keys:[K(0,{}),K(60,{sc:95,rt:-2},'ease-in'),K(120,{sc:93,rt:2}),K(200,{sc:93,rt:-1}),K(340,{sc:100,rt:0},'back-out')],
    fx:[SN(0,'set',P),F(60,'amberShell',{col:c}),
        F(140,'spray',{col:c,count:5+2*P,speed:28,g:170,size:10,spread:0.6})]};},
  /* PAY hangs: sparks decelerate and linger; power 2+ lifts a light column */
  PAY:function(c,P){var fx=[SN(0,'chime',P),
      F(0,'spray',{col:c,count:10+5*P,speed:50,g:-16,size:7,spread:1.2}),
      F(0,'glow',{col:c,size:6+2*P,ms:500})];
    if(P>=2)fx.push(F(60,'beam',{col:c,ms:700}));
    return {keys:[],fx:fx};},
  COIN:function(c,P){return {keys:[],
    fx:[SN(0,'coin',P),F(0,'spray',{col:c,count:6+3*P,speed:90,g:60,size:6,spread:0.9})]};},
  /* STRIKE: the hit-frame flash FIRST, then shake, then dust drifting UP */
  STRIKE:function(c,P){return {keys:[K(0,{}),K(60,{dx:-7},'ease-in'),K(120,{dx:7}),K(180,{dx:-3}),K(240,{dx:0},'back-out')],
    fx:[F(0,'flash',{ms:90}),SN(0,'thud',P),
        F(20,'spray',{col:c,count:10+4*P,speed:70,g:220,size:6,spread:2.6}),
        F(80,'spray',{col:'#7a6a55',count:6+2*P,speed:20,g:-8,size:12,spread:2.8})]};},
  /* TRANSFORM: the afterimage ghost lags the spin; swap hides at the peak */
  TRANSFORM:function(c,P){return {keys:[K(0,{}),K(300,{rt:180,sc:108},'ease-out'),K(620,{rt:360,sc:100},'back-out')],
    fx:[SN(0,'shimmer',P),F(150,'spray',{col:c,count:12+4*P,speed:55,g:-10,size:6,spread:3}),
        F(300,'ghost',{col:c,ms:420})]};},
  /* FATE is SLOW: beam + two delayed twinkles - speed is what separates
     it from PAY */
  FATE:function(c,P){return {keys:[K(0,{}),K(450,{op:78},'ease-out'),K(900,{op:100},'ease-out')],
    fx:[SN(0,'bell',P),F(0,'glow',{col:c,size:8+2*P,ms:900}),
        F(0,'beam',{col:c,ms:1000}),
        F(250,'glow',{col:'#ffffff',size:4,ms:300}),F(500,'glow',{col:c,size:3,ms:300})]};},
  /* BREAK has an ORDER: flash, crack, shards OUT, smoke HANGING */
  BREAK:function(c,P){return {keys:[],
    fx:[F(0,'flash',{ms:90}),SN(0,'crack',P),
        F(40,'break',{col:c,count:22+6*P,speed:110,g:180,size:6,ms:520}),
        F(90,'spray',{col:'#5a5248',count:8+2*P,speed:16,g:-6,size:13,spread:3})]};},
  ARM:function(c,P){return {keys:[K(0,{}),K(140,{sc:108},'back-out'),K(300,{sc:100}),K(440,{sc:105},'back-out'),K(600,{sc:100})],
    fx:[SN(0,'drum',P),F(120,'glow',{col:c,size:5+2*P,ms:400})]};},
  LEDGER:function(c,P){return {keys:[],
    fx:[SN(0,'scratch',P),F(0,'announce',{text:'THE LEDGER NOTES IT',annCol:'gold'})]};}
};""",
    'family templates: the second pass')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d edits' % n)
