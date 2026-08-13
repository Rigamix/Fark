# -*- coding: utf-8 -*-
"""P702: the scoring face stays bright; the sides fall into shadow.

Denis: "keeping top face (scoring face) bright as it is but darkening sides
(non scoring) with a darkish brown so the emphasis is on the scoring faces."

Not a light-rig change: one shared scene lights shelf chips and tumbling
dice alike, ambient 0.72 floors how dark a side can go, and the 42-degree
table tilt means a down-light never aligns with the settled face. Instead
the codebase's own per-face channel: bake a copy of the die's COMPOSED atlas
with every cell multiplied by a dark warm brown EXCEPT the scoring value's,
and hard-swap it in while d.phys holds (the tray's swap-don't-fade rule -
Lambert cannot blend two maps). Orientation-agnostic, fires exactly at
settle, never mid-tumble.

The cache keys on the composed map object per value - that map already
encodes the {mat, ench} pair, so the pair travels together for free. The
bright original is stashed as userData.liveMap and restored in the air and
at every table change BEFORE the tray tint can cache a dimmed map as its
base (the two-caches-poisoning-each-other bug _airTint's comment warns
about). Derived per frame from map identity, so a reskin or rebrand
self-heals on the next frame - the spent-look lesson, no flags.

Known scopes: a resumed never-rolled die rests bright (no d.phys.v) - the
mixed look after resume is accepted for now and noted in the handover. An
enchant brand on a SIDE face keeps its emissive glow through the dim - reads
as the brand glowing in shadow, kept deliberately.
"""
import io, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'fark_proto.html')
s = io.open(P, encoding='utf-8', newline='').read()
n = 0


def sub(old, new, label):
    global s, n
    c = s.count(old)
    if c != 1:
        sys.exit('ANCHOR x%d (need 1) for %s' % (c, label))
    s = s.replace(old, new)
    n += 1
    print('  ok  %s' % label)


# 1) the baker, beside its sibling _shadeMap
sub(u"    if(!tex.userData)tex.userData={};\n"
    u"    tex.userData.trayMap=out;\n"
    u"    return out;\n"
    u"  },",
    u"    if(!tex.userData)tex.userData={};\n"
    u"    tex.userData.trayMap=out;\n"
    u"    return out;\n"
    u"  },\n"
    u"  /* P702: the sides-dimmed copy for a SETTLED die - every atlas cell\n"
    u"     multiplied by a dark warm brown except the scoring value's, so the\n"
    u"     top face keeps its painted brightness and the sides sit in the\n"
    u"     table's shadow. Cached per composed map + value; the composed map\n"
    u"     already encodes {mat, ench}, so the pair travels together. */\n"
    u"  SIDEDIM:'#5a3d24',\n"
    u"  _dimMap:function(tex,v){\n"
    u"    if(!tex||!tex.image||!v)return null;\n"
    u"    if(!tex.userData)tex.userData={};\n"
    u"    var dm=tex.userData.dimMaps||(tex.userData.dimMaps={});\n"
    u"    if(dm[v])return dm[v];\n"
    u"    var im=tex.image;\n"
    u"    var w=im.width||im.naturalWidth,h=im.height||im.naturalHeight;\n"
    u"    if(!w||!h)return null;\n"
    u"    var cv=document.createElement('canvas');cv.width=w;cv.height=h;\n"
    u"    var cx=cv.getContext('2d');\n"
    u"    cx.drawImage(im,0,0,w,h);\n"
    u"    cx.globalCompositeOperation='multiply';\n"
    u"    cx.fillStyle=this.SIDEDIM;\n"
    u"    cx.fillRect(0,0,w,h);\n"
    u"    cx.globalCompositeOperation='source-over';\n"
    u"    /* the scoring face, back at its authored brightness - same cell\n"
    u"       geometry as _brandedMap: 3x2, col (v-1)%3, row (v-1)/3 */\n"
    u"    var cw=w/3,ch=h/2,cxp=((v-1)%3)*cw,cyp=Math.floor((v-1)/3)*ch;\n"
    u"    cx.drawImage(im,cxp,cyp,cw,ch,cxp,cyp,cw,ch);\n"
    u"    var out=new THREE.CanvasTexture(cv);\n"
    u"    out.flipY=tex.flipY;out.wrapS=tex.wrapS;out.wrapT=tex.wrapT;\n"
    u"    out.encoding=tex.encoding;out.needsUpdate=true;\n"
    u"    dm[v]=out;\n"
    u"    return out;\n"
    u"  },",
    'P702 _dimMap baker')

# 2) the one place that decides what a face shows stamps the bright map
sub(u"    if(this._isWildMat(mat)&&m.map){\n"
    u"      m.map=this._wildMap(m.map);\n"
    u"      m.needsUpdate=true;\n"
    u"    }\n"
    u"  },",
    u"    if(this._isWildMat(mat)&&m.map){\n"
    u"      m.map=this._wildMap(m.map);\n"
    u"      m.needsUpdate=true;\n"
    u"    }\n"
    u"    /* P702: whatever this function decided a face shows IS the bright\n"
    u"       original the settle dim starts from - stamping it here means\n"
    u"       every build/rebrand/reskin path restamps it (P552). */\n"
    u"    m.userData.liveMap=m.map;\n"
    u"  },",
    'P702 liveMap stamp in _faceLayers')

# 3a) the throw carries its value...
sub(u"    mine.forEach(function(d,i){d.roll={sol:sol,i:i,t0:t0};d.phys=null;});",
    u"    mine.forEach(function(d,i){d.roll={sol:sol,i:i,t0:t0,val:b.vals[i]};d.phys=null;});/* P702: val rides along */",
    'P702 roll carries val')

# 3b) ...and the rest pose keeps it
sub(u"      d.phys={x:f.x,y:f.y,z:f.z,q:q.clone()};d.roll=null;",
    u"      d.phys={x:f.x,y:f.y,z:f.z,q:q.clone(),v:(d.roll&&d.roll.val)||null};d.roll=null;/* P702 */",
    'P702 phys keeps val')

# 4a) settled branch: swap to the dimmed copy, derived per frame
sub(u"          d.obj.position.set(d.phys.x,d.phys.y,d.phys.z);\n"
    u"          d.obj.quaternion.copy(d.phys.q);\n"
    u"          D3X._weightOutline(d);",
    u"          d.obj.position.set(d.phys.x,d.phys.y,d.phys.z);\n"
    u"          d.obj.quaternion.copy(d.phys.q);\n"
    u"          /* P702: scoring face bright, sides in shadow - derived from\n"
    u"             map identity every frame, so a reskin/rebrand self-heals on\n"
    u"             the next one (the spent-look lesson; no flags). */\n"
    u"          if(d.phys.v)d.obj.traverse(function(o){\n"
    u"            if(!o.isMesh||!o.material||o.userData.outline)return;\n"
    u"            var m=o.material;\n"
    u"            if(!m.userData)m.userData={};\n"
    u"            if(!m.userData.liveMap)m.userData.liveMap=m.map;\n"
    u"            var want=D3X._dimMap(m.userData.liveMap,d.phys.v)||m.userData.liveMap;\n"
    u"            if(m.map!==want){m.map=want;m.needsUpdate=true;}\n"
    u"          });\n"
    u"          D3X._weightOutline(d);",
    'P702 settled swap')

# 4b) rolling branch: the air shows the authored faces
sub(u"          D3X._airTint(d,pose.y);\n"
    u"          D3X._weightOutline(d);",
    u"          D3X._airTint(d,pose.y);\n"
    u"          /* P702 mirror: back in the air, back to the authored map */\n"
    u"          d.obj.traverse(function(o){\n"
    u"            if(!o.isMesh||!o.material||o.userData.outline)return;\n"
    u"            var m=o.material;\n"
    u"            if(m.userData&&m.userData.liveMap&&m.map!==m.userData.liveMap){m.map=m.userData.liveMap;m.needsUpdate=true;}\n"
    u"          });\n"
    u"          D3X._weightOutline(d);",
    'P702 rolling restore')

# 4c) table change: restore BEFORE the tray tint can cache a dimmed base
sub(u"          d.rk=rkNow;d.phys=null;d.roll=null;\n"
    u"          d.w0=cr.width;d.hx=undefined;d.tx=0;d.ty=0;\n"
    u"          if(d.obj.parent&&d.obj.parent!==D3X.scene)D3X.scene.add(d.obj);\n"
    u"          d.chip.style.translate='';\n"
    u"          D3X._shDirty=true;",
    u"          d.rk=rkNow;d.phys=null;d.roll=null;\n"
    u"          d.w0=cr.width;d.hx=undefined;d.tx=0;d.ty=0;\n"
    u"          if(d.obj.parent&&d.obj.parent!==D3X.scene)D3X.scene.add(d.obj);\n"
    u"          d.chip.style.translate='';\n"
    u"          /* P702: it changed tables with the sides still dimmed - put the\n"
    u"             authored map back BEFORE the tray tint stashes its baseMap,\n"
    u"             or the dim gets cached as the base (the exact two-caches\n"
    u"             poisoning _airTint's comment warns about). */\n"
    u"          try{d.obj.traverse(function(o){var m=o.isMesh&&o.material;\n"
    u"            if(m&&m.userData&&m.userData.liveMap&&m.map!==m.userData.liveMap){m.map=m.userData.liveMap;m.needsUpdate=true;}\n"
    u"          });}catch(e){}\n"
    u"          D3X._shDirty=true;",
    'P702 table-change restore')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('\n%d edits' % n)
