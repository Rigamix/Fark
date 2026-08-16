# -*- coding: utf-8 -*-
"""P752: the shadow mask lives in WORLD space, not on the die's skin.

Denis: "mask axis slider doesn't work because each die has a different
axis when settled. It needs to be global, left to right or top to bottom
for all dice independent from their rotation."

ROOT. The mask was baked into the texture atlas - a gradient across each
face's CELL, which is the die's own UV space. The dice are glTF models;
where a cell's UV axes point on a settled die depends entirely on which
way the die landed, so the axis slider was choosing a direction in a
space that rotates with every die. No slider value could fix that.

Now the bake goes back to FLAT dim (one colour per strength, exactly the
pre-P732 map - caches, ramps and liveMap identity all untouched), and the
gradient is a world-space term injected into the die's own Lambert
material: per-pixel position along a WORLD axis, relightened toward the
mask's bright end, masked off the top face by world normal. 'x' is the
table's left-to-right, 'y' is top-to-bottom (world Z, screen vertical),
for every die, whatever way it rolled.

  D3X.GRAD={ax,amt}       the config (baked from Denis's approved look)
  D3X.setGrad(ax,amt)     live control - uniforms only, no rebake, which
                          also makes the lab slider instant

The lab's gradeDice stops overriding _dimMap (that override was the same
UV-space bake) and drives setGrad instead.
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
    return s


P = os.path.join(ROOT, 'fark_proto.html')

GAME = [
    # ── 1. config: GRAD replaces SIDEDIM_GRAD ──
    (u"""  /* P732: the dim is STRONGER but fades ACROSS each face - Denis's final
     numbers went horizontal and subtler. GRAD is the fraction of the dim
     masked away at the right edge of each cell (all dice). */
  SIDEDIM_GRAD:0.14,""",
     u"""  /* P752: the mask is WORLD-SPACE now. P732 baked it into each face's
     atlas cell - the die's own UV space, which rotates with the die, so
     the axis slider chose directions in a space no two settled dice
     share. ax 'x' = the table's left-to-right, 'y' = top-to-bottom
     (world Z); amt is the fraction of the dim relit at the bright end,
     signed to flip ends. Applied in the material as a per-pixel term -
     see _gradHook - so setGrad is uniforms only, no rebake. */
  GRAD:{ax:'x', amt:0.14},
  setGrad:function(ax,amt){
    this.GRAD.ax=ax||this.GRAD.ax;
    if(amt!==undefined)this.GRAD.amt=+amt;
    var self=this;
    this.dice.forEach(function(d){
      if(!d.obj)return;
      d.obj.traverse(function(o){
        if(o.isMesh&&o.material&&o.material.userData.fkG)
          self._syncGrad(o.material.userData.fkG);
      });
    });
  },
  _syncGrad:function(u){
    var g=this.GRAD;
    u.uAmt.value=g.amt||0;
    if(g.ax==='y')u.uAx.value.set(0,0,1);
    else u.uAx.value.set(1,0,0);
  },
  /* P752: the world-space mask, injected into the die's Lambert. The
     bake dims every side face FLAT at strength k; this term relights
     each pixel toward the mask's bright end along a WORLD axis, and the
     top face is excluded by world normal exactly as the bake excludes
     the scoring cell. uK rides the same settle ramp the bake steps
     through, written wherever _dimMap is applied. */
  _gradHook:function(o){
    var m=o.material;
    if(!m||m.userData.fkG)return;
    var u={uK:{value:0},uAmt:{value:0},uAx:{value:new THREE.Vector3(1,0,0)},
           uSpan:{value:1},uDim:{value:new THREE.Color(this.SIDEDIM)}};
    m.userData.fkG=u;
    try{
      if(!o.geometry.boundingBox)o.geometry.computeBoundingBox();
      var bb=o.geometry.boundingBox;
      u.uSpan.value=Math.max(0.2,bb.max.x-bb.min.x);
    }catch(e){}
    this._syncGrad(u);
    m.onBeforeCompile=function(sh){
      sh.uniforms.fkK=u.uK;sh.uniforms.fkAmt=u.uAmt;sh.uniforms.fkAx=u.uAx;
      sh.uniforms.fkSpan=u.uSpan;sh.uniforms.fkDim=u.uDim;
      sh.vertexShader=sh.vertexShader
        .replace('#include <common>',
          '#include <common>\nvarying vec3 vFkW;varying vec3 vFkC;varying vec3 vFkN;')
        .replace('#include <worldpos_vertex>',
          '#include <worldpos_vertex>\n'
          +'vFkW=(modelMatrix*vec4(position,1.0)).xyz;\n'
          +'vFkC=(modelMatrix*vec4(0.0,0.0,0.0,1.0)).xyz;\n'
          +'vFkN=normalize(mat3(modelMatrix[0].xyz,modelMatrix[1].xyz,modelMatrix[2].xyz)*normal);');
      sh.fragmentShader=sh.fragmentShader
        .replace('#include <common>',
          '#include <common>\nvarying vec3 vFkW;varying vec3 vFkC;varying vec3 vFkN;\n'
          +'uniform float fkK;uniform float fkAmt;uniform vec3 fkAx;'
          +'uniform float fkSpan;uniform vec3 fkDim;')
        .replace('#include <map_fragment>',
          '#include <map_fragment>\n'
          +'if(fkK>0.001&&abs(fkAmt)>0.0001){\n'
          +'  float fkT=clamp(0.5+dot(vFkW-vFkC,fkAx)/fkSpan,0.0,1.0);\n'
          +'  float fkM=1.0-smoothstep(0.55,0.85,dot(normalize(vFkN),vec3(0.0,1.0,0.0)));\n'
          +'  float fkKt=fkK*(1.0-abs(fkAmt)*(fkAmt>0.0?fkT:(1.0-fkT)));\n'
          +'  vec3 fkA=vec3(1.0)-(vec3(1.0)-fkDim)*fkKt;\n'
          +'  vec3 fkF=vec3(1.0)-(vec3(1.0)-fkDim)*fkK;\n'
          +'  diffuseColor.rgb*=mix(vec3(1.0),fkA/max(fkF,vec3(0.02)),fkM);\n'
          +'}');
    };
    m.needsUpdate=true;
  },""",
     'GRAD config + world-space hook'),

    # ── 2. the bake goes back to flat ──
    (u"""    /* P732: the dim fades toward each face's BASE (SIDEDIM_GRAD masks
       that fraction of it) - a per-cell vertical gradient of the multiply
       colour rather than one flat fill. The scoring cell is repainted
       bright below exactly as before, so top faces are untouched. */
    var _gd=this.SIDEDIM_GRAD||0;
    var _colAt=function(kk){return 'rgb('+fc.map(function(f){
      return Math.round(255*(1-(1-f)*kk));}).join(',')+')';};
    var _cw=w/3,_ch=h/2;
    for(var _cy=0;_cy<2;_cy++)for(var _cx2=0;_cx2<3;_cx2++){
      var _x0=_cx2*_cw,_y0=_cy*_ch;
      var _gr=cx.createLinearGradient(0,_y0,0,_y0+_ch);
      _gr.addColorStop(0,_colAt(kq));
      _gr.addColorStop(1,_colAt(kq*(1-_gd)));
      cx.fillStyle=_gr;cx.fillRect(_x0,_y0,_cw,_ch);
    }""",
     u"""    /* P752: FLAT again. P732's per-cell gradient was the mask baked into
       the die's own UV space, which rotates with the die - the world-space
       version lives in _gradHook's shader term now, so the bake carries
       only the strength and the caches never depend on the mask. */
    cx.fillStyle=col;cx.fillRect(0,0,w,h);""",
     'bake back to flat'),

    # ── 3. hook attached where the die material is born ──
    (u"""        o.material.userData.baseMap=_pipTex;
        self._dress(o.material,mat,sk);
        self._faceLayers(o.material,mat,ench,col);/* P552 */""",
     u"""        o.material.userData.baseMap=_pipTex;
        self._dress(o.material,mat,sk);
        self._faceLayers(o.material,mat,ench,col);/* P552 */
        self._gradHook(o);/* P752: the world-space shadow mask */""",
     'hook at material birth'),

    # ── 4. uK rides the settle ramp at both bake sites ──
    (u"""      var want=(_kk>0?self._dimMap(m.userData.liveMap,d.phys.v,_kk):null)||m.userData.liveMap;
      if(m.map!==want){m.map=want;m.needsUpdate=true;}""",
     u"""      var want=(_kk>0?self._dimMap(m.userData.liveMap,d.phys.v,_kk):null)||m.userData.liveMap;
      if(m.map!==want){m.map=want;m.needsUpdate=true;}
      if(m.userData.fkG)m.userData.fkG.uK.value=_kk;/* P752 */""",
     'uK at settle dim'),

    (u"""              var want=(_kkL>0&&R2&&R2.val?D3X._dimMap(m.userData.liveMap,R2.val,_kkL):null)||m.userData.liveMap;
              if(m.map!==want){m.map=want;m.needsUpdate=true;}""",
     u"""              var want=(_kkL>0&&R2&&R2.val?D3X._dimMap(m.userData.liveMap,R2.val,_kkL):null)||m.userData.liveMap;
              if(m.map!==want){m.map=want;m.needsUpdate=true;}
              if(m.userData.fkG)m.userData.fkG.uK.value=_kkL;/* P752 */""",
     'uK at resume dim'),

    # ── 5. and clears where the bright map is restored ──
    (u"""          try{d.obj.traverse(function(o){var m=o.isMesh&&o.material;
            if(m&&m.userData&&m.userData.liveMap&&m.map!==m.userData.liveMap){m.map=m.userData.liveMap;m.needsUpdate=true;}
          });}catch(e){}""",
     u"""          try{d.obj.traverse(function(o){var m=o.isMesh&&o.material;
            if(m&&m.userData&&m.userData.liveMap&&m.map!==m.userData.liveMap){m.map=m.userData.liveMap;m.needsUpdate=true;}
            if(m&&m.userData&&m.userData.fkG)m.userData.fkG.uK.value=0;/* P752 */
          });}catch(e){}""",
     'uK cleared with the bright map'),
]
patch(P, GAME)

# ── 6. the lab drives the base, not an override ──
L = os.path.join(ROOT, 'fark_lab.html')
sl = io.open(L, encoding='utf-8', newline='').read()
# replace the whole gradeDice body: from its function line to the next
# function definition
gi = sl.find('function gradeDice(amt){')
if gi < 0:
    sys.exit('gradeDice not found (nothing written)')
ge = sl.find('\nfunction ', gi + 10)
if ge < 0:
    sys.exit('gradeDice end not found (nothing written)')
NEWLAB = '''function gradeDice(amt){
  /* P752: the mask is the GAME's own world-space term now (D3X.setGrad) -
     the old _dimMap override baked it into the die's UV space, which is
     why the axis slider pointed a different way on every settled die. */
  amt=+amt;
  var axis=(document.getElementById('dgAxis')||{}).value||'y';
  gw();
  E('D3X.setGrad&&D3X.setGrad("'+axis+'",'+(amt/100)+')');
  var sp=document.getElementById('lvG');
  if(sp)sp.textContent=amt?(amt+'% '+(axis==='x'?'horizontal':'vertical')):'off';
  saveLook();
}'''
sl = sl[:gi] + NEWLAB + sl[ge:]
io.open(L, 'w', encoding='utf-8', newline='').write(sl)
edits.append('lab drives setGrad')

print('done: %d (%s)' % (len(edits), ', '.join(edits)))
