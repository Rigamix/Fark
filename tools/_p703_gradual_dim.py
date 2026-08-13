# -*- coding: utf-8 -*-
"""P703: the side-face shadow arrives like a shadow, not a switch.

Denis: "Side face darkness is 50% too strong but more importantly it appears
in one frame after the dice settle so it's jarring. Should be very gradual
and unnoticeable."

Strength: SIDEDIM_MAX 0.5 halves the multiply toward the same warm brown.

Gradualness inside the Lambert two-map rule (no crossfade without a
shader): bake QUANTIZED steps of the same dim and walk through them on a
smoothstepped ramp - 8 steps over 700ms after a 150ms hold is ~4% per swap,
below noticing. Each step is cached per composed map + value + step, so a
given die pays the bake cost once ever; the identity-check swap idiom is
unchanged, the settled branch just derives WHICH step from the settle
timestamp now riding d.phys.t.
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


# 1) the baker learns strength; the tunables move to one block
sub(u"  SIDEDIM:'#5a3d24',\n"
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
    u"  SIDEDIM:'#5a3d24',\n"
    u"  /* P703, both from Denis on device: half the strength, and the arrival\n"
    u"     must be 'very gradual and unnoticeable'. Lambert still cannot blend\n"
    u"     two maps, so gradual = QUANTIZED BAKES: steps of ~4%% walked on a\n"
    u"     smoothstepped ramp, each cached per composed map + value + step. */\n"
    u"  SIDEDIM_MAX:0.5,\n"
    u"  SIDEDIM_RAMP:{delay:150,dur:700,steps:8},\n"
    u"  _dimMap:function(tex,v,k){\n"
    u"    if(!tex||!tex.image||!v||!k)return null;\n"
    u"    if(!tex.userData)tex.userData={};\n"
    u"    var dm=tex.userData.dimMaps||(tex.userData.dimMaps={});\n"
    u"    var kq=Math.round(k*1000)/1000,key=v+'|'+kq;\n"
    u"    if(dm[key])return dm[key];\n"
    u"    var im=tex.image;\n"
    u"    var w=im.width||im.naturalWidth,h=im.height||im.naturalHeight;\n"
    u"    if(!w||!h)return null;\n"
    u"    /* the multiply colour at strength k: each channel walks from 255\n"
    u"       toward SIDEDIM's, so k=0 is the authored sheet and k=1 the full\n"
    u"       shadow - one hex stays the only colour opinion */\n"
    u"    var hx=this.SIDEDIM.replace('#',''),fc=[0,1,2].map(function(i){\n"
    u"      return parseInt(hx.substr(i*2,2),16)/255;});\n"
    u"    var col='rgb('+fc.map(function(f){\n"
    u"      return Math.round(255*(1-(1-f)*kq));}).join(',')+')';\n"
    u"    var cv=document.createElement('canvas');cv.width=w;cv.height=h;\n"
    u"    var cx=cv.getContext('2d');\n"
    u"    cx.drawImage(im,0,0,w,h);\n"
    u"    cx.globalCompositeOperation='multiply';\n"
    u"    cx.fillStyle=col;\n"
    u"    cx.fillRect(0,0,w,h);\n"
    u"    cx.globalCompositeOperation='source-over';\n"
    u"    /* the scoring face, back at its authored brightness - same cell\n"
    u"       geometry as _brandedMap: 3x2, col (v-1)%3, row (v-1)/3 */\n"
    u"    var cw=w/3,ch=h/2,cxp=((v-1)%3)*cw,cyp=Math.floor((v-1)/3)*ch;\n"
    u"    cx.drawImage(im,cxp,cyp,cw,ch,cxp,cyp,cw,ch);\n"
    u"    var out=new THREE.CanvasTexture(cv);\n"
    u"    out.flipY=tex.flipY;out.wrapS=tex.wrapS;out.wrapT=tex.wrapT;\n"
    u"    out.encoding=tex.encoding;out.needsUpdate=true;\n"
    u"    dm[key]=out;\n"
    u"    return out;\n"
    u"  },",
    'P703 stepped baker')

# 2) settle stamps its moment
sub(u"      d.phys={x:f.x,y:f.y,z:f.z,q:q.clone(),v:(d.roll&&d.roll.val)||null};d.roll=null;/* P702 */",
    u"      d.phys={x:f.x,y:f.y,z:f.z,q:q.clone(),v:(d.roll&&d.roll.val)||null,t:performance.now()};d.roll=null;/* P702/P703 */",
    'P703 settle timestamp')

# 3) the settled branch derives the step from the clock
sub(u"          /* P702: scoring face bright, sides in shadow - derived from\n"
    u"             map identity every frame, so a reskin/rebrand self-heals on\n"
    u"             the next one (the spent-look lesson; no flags). */\n"
    u"          if(d.phys.v)d.obj.traverse(function(o){\n"
    u"            if(!o.isMesh||!o.material||o.userData.outline)return;\n"
    u"            var m=o.material;\n"
    u"            if(!m.userData)m.userData={};\n"
    u"            if(!m.userData.liveMap)m.userData.liveMap=m.map;\n"
    u"            var want=D3X._dimMap(m.userData.liveMap,d.phys.v)||m.userData.liveMap;\n"
    u"            if(m.map!==want){m.map=want;m.needsUpdate=true;}\n"
    u"          });",
    u"          /* P702: scoring face bright, sides in shadow - derived from\n"
    u"             map identity every frame, so a reskin/rebrand self-heals on\n"
    u"             the next one (the spent-look lesson; no flags). P703: the\n"
    u"             shadow ARRIVES on a smoothstepped ramp in quantized baked\n"
    u"             steps - ~4%% a swap, below noticing, per Denis. */\n"
    u"          if(d.phys.v){\n"
    u"            var _R=D3X.SIDEDIM_RAMP;\n"
    u"            var _k=(performance.now()-(d.phys.t||0)-_R.delay)/_R.dur;\n"
    u"            _k=_k<0?0:(_k>1?1:_k);\n"
    u"            _k=_k*_k*(3-2*_k);/* smoothstep: no visible start, no visible stop */\n"
    u"            var _kk=(Math.round(_k*_R.steps)/_R.steps)*D3X.SIDEDIM_MAX;\n"
    u"            d.obj.traverse(function(o){\n"
    u"              if(!o.isMesh||!o.material||o.userData.outline)return;\n"
    u"              var m=o.material;\n"
    u"              if(!m.userData)m.userData={};\n"
    u"              if(!m.userData.liveMap)m.userData.liveMap=m.map;\n"
    u"              var want=(_kk>0?D3X._dimMap(m.userData.liveMap,d.phys.v,_kk):null)||m.userData.liveMap;\n"
    u"              if(m.map!==want){m.map=want;m.needsUpdate=true;}\n"
    u"            });\n"
    u"          }",
    'P703 ramped settled swap')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('\n%d edits' % n)
