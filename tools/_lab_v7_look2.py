# -*- coding: utf-8 -*-
"""Lab v7: Denis's three corrections.
- Vignette, not wash: radial darkness in the dice area with the centre
  kept bright; centre light its own slider; the UI untouched.
- The REAL selection glow's dials (D3X.GLOW + P731's sx/sy/dy) - not a
  parallel shell. A 'select all' toggle lights the board for tuning.
- Die side gradient becomes a MASK ON THE SIDE-DIM (an injected _dimMap
  override): the shadow itself fades along a chosen axis, per cell, and
  the scoring face stays bright because the bake already repaints it."""
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


# 1) the studio rows: vignette trio, dim-mask gradient with axis, real glow dials
sub(u"""  h+='<br><label>room darkness <input type="range" min="0" max="70" value="0" oninput="roomSet(this.value)"> <span id="lvE">0%</span></label>';
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
    u"""  h+='<br><label>vignette <input type="range" min="0" max="80" value="0" oninput="vigSet()" id="vgA"> <span id="lvE">off</span></label>';
  h+='<label>vignette size <input type="range" min="15" max="75" value="45" oninput="vigSet()" id="vgR"></label>';
  h+='<label>centre light <input type="range" min="0" max="60" value="0" oninput="vigSet()" id="vgC"></label>';
  h+='<br><label>shadow depth <input type="range" min="0" max="70" value="0" oninput="shadowSet(this.value)"> <span id="lvSh">normal</span></label>';
  h+='<label>dice side-shadow <input type="range" min="0" max="90" value="'+Math.round((E('D3X.SIDEDIM_MAX')||0.5)*100)+'" oninput="sideSet(this.value)"> <span id="lvS"></span></label>';
  h+='<br><label>shadow mask <input type="range" min="-100" max="100" value="0" oninput="gradeDice(this.value)" id="dgAmt"> <span id="lvG">off</span></label>';
  h+='<label>mask axis <select id="dgAxis" onchange="gradeDice(document.getElementById(&quot;dgAmt&quot;).value)"><option value="y">vertical</option><option value="x">horizontal</option></select></label>';
  h+='<button onclick="lightsReset()" style="margin-left:8px">reset look</button>';
  h+='<div style="margin-top:8px;border-top:1px dashed #3a2c18;padding-top:6px">'
    +'<b style="color:#c8a45c;font-size:11px;margin-right:6px">GLOW STUDIO</b>'
    +'<span style="font-size:10px;color:#9a8a68">(the REAL selection glow - D3X.GLOW)</span> '
    +'<label><input type="checkbox" id="glSel" onchange="glowSelAll(this.checked)"> select all dice</label>'
    +'<br><label>strength <input type="range" id="gStr" min="10" max="100" value="78" oninput="glowDial(&quot;strength&quot;,this.value/100)"></label>'
    +'<label>reach <input type="range" id="gSoft" min="2" max="30" value="10" oninput="glowDial(&quot;soft&quot;,+this.value)"></label>'
    +'<label>core <input type="range" id="gRim" min="1" max="10" value="3.5" step="0.5" oninput="glowDial(&quot;rim&quot;,+this.value)"></label>'
    +'<label>line <input type="range" id="gLine" min="0" max="6" value="2.4" step="0.2" oninput="glowDial(&quot;line&quot;,+this.value)"></label>'
    +'<br><label>width <input type="range" id="gSx" min="60" max="200" value="100" oninput="glowDial(&quot;sx&quot;,this.value/100)"></label>'
    +'<label>height <input type="range" id="gSy" min="60" max="200" value="100" oninput="glowDial(&quot;sy&quot;,this.value/100)"></label>'
    +'<label>lean <input type="range" id="gDy" min="-24" max="24" value="0" oninput="glowDial(&quot;dy&quot;,+this.value)"></label>'
    +'</div>';""",
    'studio rows v7')

# 2) replace roomSet + gradeDice + glow shells with the corrected trio
sub(u"""function roomSet(v){
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
  var sp=document.getElementById('lvE');if(sp)sp.textContent=v+'%';}""",
    u"""function vigSet(){
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
  var sp=document.getElementById('lvE');if(sp)sp.textContent=a>0?Math.round(a*100)+'%':'off';}
function roomSet(v){/* superseded by vigSet - kept for old saved calls */vigSet();}""",
    'vignette replaces the wash')

sub(u"""function gradeDice(amt){
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
}""",
    u"""function gradeDice(amt){
  /* THE SHADOW MASK, not an additive layer: the side-dim itself fades
     along an axis. Implemented by overriding the frame's _dimMap with a
     parameterized copy - the multiply colour becomes a per-cell gradient
     from full shadow to none, and the scoring cell is redrawn bright
     exactly as the original does, so top faces are untouched by
     construction. Config lives on the frame; caches are busted so
     settled dice rebake on the next frame. */
  amt=+amt;
  var axis=(document.getElementById('dgAxis')||{}).value||'y';
  gw();
  if(!W.__labDimOrig){
    W.__labEval("window.__labDimOrig=D3X._dimMap.bind(D3X);"
      +"D3X._dimMap=function(tex,v,k){"
      +"var g=window.__labDimGrad;"
      +"if(!g||!g.amt)return window.__labDimOrig(tex,v,k);"
      +"if(!tex||!tex.image||!v||!k)return null;"
      +"if(!tex.userData)tex.userData={};"
      +"var dm=tex.userData.dimMaps||(tex.userData.dimMaps={});"
      +"var kq=Math.round(k*1000)/1000,key=v+'|'+kq+'|'+g.axis+g.amt;"
      +"if(dm[key])return dm[key];"
      +"var im=tex.image,w=im.width||im.naturalWidth,h=im.height||im.naturalHeight;"
      +"if(!w||!h)return null;"
      +"var hx=D3X.SIDEDIM.replace('#',''),fc=[0,1,2].map(function(i){return parseInt(hx.substr(i*2,2),16)/255;});"
      +"var col=function(kk){return 'rgb('+fc.map(function(f){return Math.round(255*(1-(1-f)*kk));}).join(',')+')';};"
      +"var cv=document.createElement('canvas');cv.width=w;cv.height=h;"
      +"var cx=cv.getContext('2d');cx.drawImage(im,0,0,w,h);"
      +"cx.globalCompositeOperation='multiply';"
      +"var cw=w/3,ch=h/2,am=Math.abs(g.amt),sgn=g.amt>0?1:-1;"
      +"for(var cy=0;cy<2;cy++)for(var cxx=0;cxx<3;cxx++){"
      +"var x0=cxx*cw,y0=cy*ch;"
      +"var gr=g.axis==='x'?cx.createLinearGradient(x0,0,x0+cw,0):cx.createLinearGradient(0,y0,0,y0+ch);"
      +"var kFull=kq,kMasked=kq*(1-am);"
      +"gr.addColorStop(sgn>0?0:1,col(kFull));gr.addColorStop(sgn>0?1:0,col(kMasked));"
      +"cx.fillStyle=gr;cx.fillRect(x0,y0,cw,ch);}"
      +"cx.globalCompositeOperation='source-over';"
      +"var cw2=w/3,ch2=h/2,cxp=((v-1)%3)*cw2,cyp=Math.floor((v-1)/3)*ch2;"
      +"cx.drawImage(im,cxp,cyp,cw2,ch2,cxp,cyp,cw2,ch2);"
      +"var out=new THREE.CanvasTexture(cv);"
      +"out.flipY=tex.flipY;out.wrapS=tex.wrapS;out.wrapT=tex.wrapT;"
      +"out.encoding=tex.encoding;out.needsUpdate=true;"
      +"dm[key]=out;return out;};");
  }
  E('window.__labDimGrad='+JSON.stringify(amt===0?null:{axis:axis,amt:amt/100}));
  /* bust the caches so settled dice rebake with the new mask */
  var dx=E('window.D3X');
  if(dx)dx.dice.forEach(function(d){
    if(!d.match||!d.obj)return;
    d.obj.traverse(function(o){
      if(!o.isMesh||!o.material||o.userData.outline)return;
      var lm=o.material.userData&&o.material.userData.liveMap;
      if(lm&&lm.userData)lm.userData.dimMaps={};
    });
  });
  var sp=document.getElementById('lvG');
  if(sp)sp.textContent=amt===0?'off':((amt>0?'+':'')+amt+' '+axis);
}""",
    'shadow mask replaces the additive bake')

sub(u"""function glowApply(){
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
    u"""function glowDial(field,v){
  /* the REAL glow: D3X.GLOW's own dials + P731's sx/sy/dy */
  E('D3X.GLOW.'+field+'='+v);
  E('D3X._drawGlow&&D3X._drawGlow()');
}
function glowSelAll(on){
  var dx=E('window.D3X');if(!dx)return;
  dx.dice.forEach(function(d){
    if(!d.match||!d.chip)return;
    d.chip.classList.toggle('selected',!!on);
  });
  E('D3X._drawGlow&&D3X._drawGlow()');
  log(on?'all dice selected - tune the glow':'selection cleared');
}""",
    'real glow dials replace the shells')

# 3) reset covers the new levers
sub(u"""function lightsReset(){
  _lights.forEach(function(l){if(l.userData._lab0!==undefined)l.intensity=l.userData._lab0;});
  if(_bounce)_bounce.intensity=0;
  roomSet(0);shadowSet(0);gradeDice(0);
  var gl=document.getElementById('glOn');if(gl){gl.checked=false;glowApply();}
  buildLights();}""",
    u"""function lightsReset(){
  _lights.forEach(function(l){if(l.userData._lab0!==undefined)l.intensity=l.userData._lab0;});
  if(_bounce)_bounce.intensity=0;
  ['vgA','vgC'].forEach(function(id){var e2=document.getElementById(id);if(e2)e2.value=0;});
  vigSet();shadowSet(0);gradeDice(0);
  ['strength',0.78,'soft',10,'rim',3.5,'line',2.4,'sx',1,'sy',1,'dy',0].forEach(function(v,i,arr){
    if(i%2===0)E('D3X.GLOW.'+arr[i]+'='+arr[i+1]);});
  glowSelAll(false);
  buildLights();}""",
    'reset covers v7')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d edits' % n)
