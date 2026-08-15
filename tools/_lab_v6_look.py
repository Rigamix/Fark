# -*- coding: utf-8 -*-
"""Lab v6: the LOOK STUDIO - real levers for the accidental look.

- Room darkness: a warm multiply overlay slotted UNDER the dice canvas
  (the room is a lit/unlit canvas composite, so the old CSS filter on
  imgs glitched and changed nothing).
- Shadow depth: brightness filter on #matchShadows - the painted die and
  prop shadows deepen with the room.
- Die side gradient: bakes a per-cell vertical gradient into each die's
  own atlas (darker at the base, or lighter = bounce), the 'individual
  gradients on the dice' from Denis's reference shot.
- Selection glow studio: back-face silhouette shells in 3D - the same
  mechanism the legacy engine's clone glow used (crisp rim + soft halo
  hugging the cube), with rim/halo/alpha/colour sliders."""
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


# 1) buildLights: the full look studio
sub(u"""  h+='<label>bounce fill <input type="range" min="0" max="120" value="0" oninput="bounceSet(this.value)"> <span id="lvB">off</span></label>';
  h+='<br><label>env art brightness <input type="range" min="40" max="110" value="100" oninput="envSet(this.value)"> <span id="lvE">100%</span></label>';
  h+='<label>dice side-shadow <input type="range" min="0" max="90" value="'+Math.round((E('D3X.SIDEDIM_MAX')||0.5)*100)+'" oninput="sideSet(this.value)"> <span id="lvS"></span></label>';
  h+='<button onclick="lightsReset()" style="margin-left:8px">reset lights</button>';""",
    u"""  h+='<label>bounce fill <input type="range" min="0" max="120" value="0" oninput="bounceSet(this.value)"> <span id="lvB">off</span></label>';
  h+='<br><label>room darkness <input type="range" min="0" max="70" value="0" oninput="roomSet(this.value)"> <span id="lvE">0%</span></label>';
  h+='<label>shadow depth <input type="range" min="0" max="70" value="0" oninput="shadowSet(this.value)"> <span id="lvSh">normal</span></label>';
  h+='<label>dice side-shadow <input type="range" min="0" max="90" value="'+Math.round((E('D3X.SIDEDIM_MAX')||0.5)*100)+'" oninput="sideSet(this.value)"> <span id="lvS"></span></label>';
  h+='<br><label>die side gradient <input type="range" min="-100" max="100" value="0" oninput="gradeDice(this.value)"> <span id="lvG">off</span></label>';
  h+='<button onclick="lightsReset()" style="margin-left:8px">reset look</button>';
  h+='<div style="margin-top:8px;border-top:1px dashed #3a2c18;padding-top:6px">'
    +'<b style="color:#c8a45c;font-size:11px;margin-right:6px">GLOW STUDIO</b>'
    +'<label><input type="checkbox" id="glOn" onchange="glowApply()"> on (all dice)</label>'
    +'<label>rim <input type="range" id="glRim" min="101" max="115" value="105" oninput="glowApply()"></label>'
    +'<label>halo <input type="range" id="glHalo" min="105" max="140" value="118" oninput="glowApply()"></label>'
    +'<label>strength <input type="range" id="glA" min="5" max="90" value="45" oninput="glowApply()"></label>'
    +'<label>colour <input type="color" id="glCol" value="#ffd98a" oninput="glowApply()"></label>'
    +'</div>';""",
    'look studio sliders')

# 2) replace envSet with the overlay + add the new functions
sub(u"""function envSet(v){
  /* the ART dims; dice (canvas) and rows stay untouched - this is what
     'darker room' should have been */
  gw();var ms=W.document.getElementById('screen-match');if(!ms)return;
  ms.querySelectorAll('img').forEach(function(im){
    if(im.closest('#playerDiceRow,#oppDiceRow,#keptRow,#famRowP,#famRowO'))return;
    im.style.filter=v>=100?'':'brightness('+(v/100)+')';
  });
  var sp=document.getElementById('lvE');if(sp)sp.textContent=v+'%';}""",
    u"""function roomSet(v){
  /* the room is a CANVAS COMPOSITE (lit/unlit table + painted shadows) -
     a CSS filter on imgs glitched and changed nothing. This is a warm
     multiply overlay slotted just UNDER the dice canvas: the whole
     painting darkens, the dice stay in their own light. */
  gw();var ms=W.document.getElementById('screen-match');if(!ms)return;
  var ov=W.document.getElementById('labDark');
  if(!ov){ov=W.document.createElement('div');ov.id='labDark';
    var cvs=W.document.getElementById('d3xCanvas');
    var z=cvs?(parseInt(getComputedStyle(cvs).zIndex)||0):0;
    ov.style.cssText='position:absolute;inset:0;pointer-events:none;'
      +'background:#100a04;mix-blend-mode:multiply;opacity:0;z-index:'+(z-1);
    ms.appendChild(ov);}
  ov.style.opacity=String(v/100);
  var sp=document.getElementById('lvE');if(sp)sp.textContent=v+'%';}
function shadowSet(v){
  gw();var msd=W.document.getElementById('matchShadows');
  if(msd)msd.style.filter=v>0?'brightness('+(1-v/100)+')':'';
  var sp=document.getElementById('lvSh');if(sp)sp.textContent=v>0?('-'+v+'%'):'normal';}
function gradeDice(amt){
  /* bake a vertical gradient into each die's own atlas cells: negative =
     darker toward each face's base (grounded), positive = lighter (bounce).
     The 'individual gradients on the dice' in the reference shot. */
  amt=+amt;
  var dx=E('window.D3X');if(!dx)return;
  var T=W.__labEval('THREE');
  dx.dice.forEach(function(d){
    if(!d.match||!d.obj)return;
    d.obj.traverse(function(o){
      if(!o.isMesh||!o.material||o.userData.outline)return;
      var m=o.material;
      if(!m.userData)m.userData={};
      if(!m.userData._gradeBase)m.userData._gradeBase=m.userData.liveMap||m.map;
      var base=m.userData._gradeBase;
      if(!base||!base.image)return;
      if(amt===0){m.map=base;m.userData.liveMap=base;m.needsUpdate=true;return;}
      var im=base.image,wd=im.width||im.naturalWidth,ht=im.height||im.naturalHeight;
      if(!wd)return;
      var cv=W.document.createElement('canvas');cv.width=wd;cv.height=ht;
      var x=cv.getContext('2d');x.drawImage(im,0,0,wd,ht);
      var a=Math.abs(amt)/100;
      var cw=wd/3,ch=ht/2;
      for(var cyc=0;cyc<2;cyc++)for(var cxc=0;cxc<3;cxc++){
        var gx=x.createLinearGradient(0,cyc*ch,0,cyc*ch+ch);
        if(amt<0){gx.addColorStop(0,'rgba(16,8,2,0)');gx.addColorStop(1,'rgba(16,8,2,'+(a*0.6)+')');
          x.globalCompositeOperation='source-atop';}
        else{gx.addColorStop(0,'rgba(255,232,200,0)');gx.addColorStop(1,'rgba(255,232,200,'+(a*0.4)+')');
          x.globalCompositeOperation='source-atop';}
        x.fillStyle=gx;x.fillRect(cxc*cw,cyc*ch,cw,ch);
      }
      var out=new T.CanvasTexture(cv);
      out.flipY=base.flipY;out.wrapS=base.wrapS;out.wrapT=base.wrapT;
      out.encoding=base.encoding;out.needsUpdate=true;
      m.map=out;m.userData.liveMap=out;m.needsUpdate=true;
    });
  });
  var sp=document.getElementById('lvG');if(sp)sp.textContent=amt===0?'off':(amt>0?'+':'')+amt;
}
function glowApply(){
  /* the legacy engine's glow was a silhouette CLONE - crisp rim + soft
     halo hugging the cube. In 3D that is two BACK-FACE shells: only the
     outer silhouette renders, so the glow is thin where the cube is
     tight and tall where it is tall, exactly the reference look. */
  var on=document.getElementById('glOn').checked;
  var rim=(+document.getElementById('glRim').value)/100;
  var halo=(+document.getElementById('glHalo').value)/100;
  var a=(+document.getElementById('glA').value)/100;
  var col=document.getElementById('glCol').value;
  var dx=E('window.D3X');if(!dx)return;
  var T=W.__labEval('THREE');
  dx.dice.forEach(function(d){
    if(!d.match||!d.obj)return;
    var g=d.obj.getObjectByName('labGlow');
    if(!on){if(g){d.obj.remove(g);
      g.traverse(function(o){if(o.material&&o.material.dispose)o.material.dispose();});}
      return;}
    var body=null;
    d.obj.traverse(function(o){if(!body&&o.isMesh&&!o.userData.outline)body=o;});
    if(!body)return;
    if(!g){
      g=new T.Group();g.name='labGlow';g.userData.outline=true;
      var mk=function(){var mesh=new T.Mesh(body.geometry,new T.MeshBasicMaterial({
        color:new T.Color(col),transparent:true,opacity:0.3,
        side:T.BackSide,depthWrite:false}));
        mesh.userData.outline=true;g.add(mesh);return mesh;};
      g.userData.rim=mk();g.userData.halo=mk();
      d.obj.add(g);
    }
    g.userData.rim.scale.setScalar(rim);
    g.userData.rim.material.opacity=a;
    g.userData.rim.material.color.set(col);
    g.userData.halo.scale.setScalar(halo);
    g.userData.halo.material.opacity=a*0.35;
    g.userData.halo.material.color.set(col);
  });
}""",
    'roomSet + shadowSet + gradeDice + glow studio')

# 3) lightsReset covers the new levers
sub(u"""function lightsReset(){
  _lights.forEach(function(l){if(l.userData._lab0!==undefined)l.intensity=l.userData._lab0;});
  if(_bounce)_bounce.intensity=0;
  envSet(100);buildLights();}""",
    u"""function lightsReset(){
  _lights.forEach(function(l){if(l.userData._lab0!==undefined)l.intensity=l.userData._lab0;});
  if(_bounce)_bounce.intensity=0;
  roomSet(0);shadowSet(0);gradeDice(0);
  var gl=document.getElementById('glOn');if(gl){gl.checked=false;glowApply();}
  buildLights();}""",
    'reset covers the look levers')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d edits' % n)
