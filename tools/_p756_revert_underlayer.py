# -*- coding: utf-8 -*-
"""P756: the dice mask goes back to exactly what it was; the card halo
moves UNDER the card layer - no cutout, no gap, badge on top for free.

Denis: "For the dice, just go back to before you changed it, it's fine
as it was." Full revert of the P752/753/755 mask experiment - the P732
per-cell UV bake returns byte-for-byte from git (SIDEDIM_GRAD:0.14, the
gradient loop in _dimMap), the shader hook, GRAD/setGrad and every uK
write are deleted, and the lab's mask slider goes back to its original
_dimMap override. The P753 dim LEAD (earlier shadow) stays - that was a
separate, approved ask.

And his card suggestion is simply better architecture than mine: "why
not have no cutout and put it under the card layer?" The halo canvas
drops from z 9400 (above the hand, where it must be punched and can
cover the badge) to z 41 - under the rows at 42 and the dragged card at
9500. The card body hides the halo's middle by simply being on top, the
badge sits over the glow for free, the punch-out and the drop offset are
retired, and there is no gap because there is nothing to cut.
"""
import io, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'fark_proto.html')
s = io.open(P, encoding='utf-8', newline='').read()
edits = []


def sub(old, new, label, count=1):
    global s
    c = s.count(old)
    if c != count:
        o2 = old.replace('\n', '\r\n')
        if s.count(o2) == count:
            old, new = o2, new.replace('\n', '\r\n')
        else:
            sys.exit('ANCHOR x%d (want %d) for %s (nothing written)' % (c, count, label))
    s = s.replace(old, new)
    edits.append(label)


def cut(startmark, endmark, label):
    """delete [startmark, endmark) - endmark stays"""
    global s
    i = s.find(startmark)
    j = s.find(endmark)
    if i < 0 or j < 0 or j <= i:
        sys.exit('cut markers bad for %s (nothing written)' % label)
    s = s[:i] + s[j:]
    edits.append(label)


# ── 1. GRAD/setGrad/_syncGrad go; SIDEDIM_GRAD returns ──
cut("  /* P752: the mask is WORLD-SPACE now.",
    "  /* P754: THE APPROVED LOOK IS THE GAME'S LOOK.",
    'GRAD block deleted')
sub("  /* P754: THE APPROVED LOOK IS THE GAME'S LOOK.",
    """  /* P732: the dim is STRONGER but fades ACROSS each face - Denis's final
     numbers went horizontal and subtler. GRAD is the fraction of the dim
     masked away at the right edge of each cell (all dice). */
  SIDEDIM_GRAD:0.14,
  /* P754: THE APPROVED LOOK IS THE GAME'S LOOK.""",
    'SIDEDIM_GRAD restored')

# ── 2. the shader hook goes ──
cut("  /* P752: the world-space mask, injected into the die's Lambert.",
    "  _dimMap:function(tex,v,k){",
    'gradHook deleted')

# ── 3. the bake gradient returns, byte-true from git ──
sub("""    /* P752: FLAT again. P732's per-cell gradient was the mask baked into
       the die's own UV space, which rotates with the die - the world-space
       version lives in _gradHook's shader term now, so the bake carries
       only the strength and the caches never depend on the mask. */
    cx.fillStyle=col;cx.fillRect(0,0,w,h);""",
    """    /* P732: the dim fades toward each face's BASE (SIDEDIM_GRAD masks
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
    'bake gradient restored')

# ── 4. every P752 touchpoint out ──
sub("""        self._gradHook(o);/* P752: the world-space shadow mask */
""", "", 'hook call removed')
sub("""      if(m.userData.fkG)m.userData.fkG.uK.value=_kk;/* P752 */
""", "", 'uK settle write removed')
sub("""              if(m.userData.fkG)m.userData.fkG.uK.value=_kkL;/* P752 */
""", "", 'uK resume write removed')
sub("""            if(m&&m.userData&&m.userData.fkG)m.userData.fkG.uK.value=0;/* P752 */
""", "", 'uK clear removed')
sub("""      if(lk.maskAmt!==null&&lk.maskAmt!==undefined)
        this.setGrad(lk.maskAxis||this.GRAD.ax,(+lk.maskAmt)/100);
""",
    """      /* P756: the mask went back to the lab's own _dimMap override -
         nothing to apply here */
""",
    'applyLook mask line removed')
sub("  SIDEDIM_MAX:0.82,/* P732: 0.5 -> 0.82, relit along GRAD's axis (P752) */",
    "  SIDEDIM_MAX:0.82,/* P732: 0.5 -> 0.82, masked by SIDEDIM_GRAD */",
    'SIDEDIM_MAX comment restored')

# ── 5. the card halo moves under the card layer ──
sub("""  _glowHiCv:function(){
    var sc=document.getElementById('screen-match');
    if(!sc)return null;
    var cv=document.getElementById('dgCanvasHi');
    if(!cv){
      cv=document.createElement('canvas');cv.id='dgCanvasHi';
      cv.style.cssText='position:absolute;inset:0;width:100%;height:100%;'
        +'pointer-events:none;z-index:9400';
      sc.appendChild(cv);
    }
    return cv;
  },""",
    """  _glowHiCv:function(){
    var sc=document.getElementById('screen-match');
    if(!sc)return null;
    var cv=document.getElementById('dgCanvasHi');
    if(!cv){
      cv=document.createElement('canvas');cv.id='dgCanvasHi';
      /* P756: UNDER the card layer (Denis's call, and the better
         architecture): rows sit at 42 and a dragged card at 9500, so at
         41 the card body hides the halo's middle by being on top, the
         badge sits over the glow for free, and no punch-out is needed -
         which is what removed the visible gap the cut used to make.
         Appended after the dice canvas, so the same z paints above it. */
      cv.style.cssText='position:absolute;inset:0;width:100%;height:100%;'
        +'pointer-events:none;z-index:41';
      sc.appendChild(cv);
    }
    return cv;
  },""",
    'canvas under the cards')

sub("""    gx.globalCompositeOperation='destination-out';
    gx.globalAlpha=1;
    sel.forEach(function(sh){
      if(sh&&sh.stamp){
        var _pm={scaleMul:1+(2*G.clear)/Math.max(8,Math.min(sh.stamp.w,sh.stamp.h))};
        lay(gx,sh,null,_pm);
        /* P755b: a DROPPED halo needs a SWEPT punch - cutting only the
           true position left a detached band below the card with the
           punch's own hard edge across it. The cut walks the drop. */
        if(DY){
          lay(gx,sh,null,{scaleMul:_pm.scaleMul,dy:DY/2});
          lay(gx,sh,null,{scaleMul:_pm.scaleMul,dy:DY});
        }
      }else{
        lay(gx,sh,null,{shrink:-G.clear});
      }
    });
    gx.globalCompositeOperation='source-over';""",
    """    /* P756: no punch when the subject itself covers the middle - the
       card halo paints UNDER the card layer now, so cutting it out only
       manufactured a visible gap. The dice keep their punch: their glow
       canvas sits above the painted table and must not wash the die. */
    if(!(opts&&opts.noPunch)){
      gx.globalCompositeOperation='destination-out';
      gx.globalAlpha=1;
      sel.forEach(function(sh){
        if(sh&&sh.stamp){
          lay(gx,sh,null,{scaleMul:1+(2*G.clear)/Math.max(8,Math.min(sh.stamp.w,sh.stamp.h))});
        }else{
          lay(gx,sh,null,{shrink:-G.clear});
        }
      });
      gx.globalCompositeOperation='source-over';
    }""",
    'punch is optional')

sub("""        {soft:CG.soft,rim:CG.rim,strength:CG.strength,dy:r.height*(CG.dyF||0)});""",
    """        {soft:CG.soft,rim:CG.rim,strength:CG.strength,dy:r.height*(CG.dyF||0),
         noPunch:true});/* P756: the card body covers the middle */""",
    'cards skip the punch')

sub("""  CARD_GLOW:{col:'#ffe6a4', softCol:'#ffa93a', soft:6, rim:2.5, strength:0.91,
    dyF:0.10, round:0.075, line:0, floor:0.42},""",
    """  CARD_GLOW:{col:'#ffe6a4', softCol:'#ffa93a', soft:6, rim:2.5, strength:0.91,
    dyF:0, round:0.075, line:0, floor:0.42},/* P756: hugging, not dropped */""",
    'no drop by default')

io.open(P, 'w', encoding='utf-8', newline='').write(s)

# ── lab: the original gradeDice returns; drop slider defaults to 0 ──
L = os.path.join(ROOT, 'fark_lab.html')
sl = io.open(L, encoding='utf-8', newline='').read()
gi = sl.find('function gradeDice(amt){')
ge = sl.find('\nfunction ', gi + 10)
if gi < 0 or ge < 0:
    sys.exit('lab gradeDice not found (game written, lab NOT)')
OLDLAB = '''function gradeDice(amt){
  /* P756: back to the ORIGINAL override - Denis: the dice were fine as
     they were. The side-dim itself fades along an axis, baked per cell;
     caches are busted so settled dice rebake on the next frame. */
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
  saveLook();
}'''
sl = sl[:gi] + OLDLAB + sl[ge:]
edits.append('lab gradeDice restored')

old = "id=\"cgDy\" min=\"0\" max=\"25\" value=\"10\""
new = "id=\"cgDy\" min=\"0\" max=\"25\" value=\"0\""
if sl.count(old) != 1:
    sys.exit('cgDy anchor missing (lab partial!)')
sl = sl.replace(old, new)
edits.append('drop defaults 0')
io.open(L, 'w', encoding='utf-8', newline='').write(sl)

print('done: %d (%s)' % (len(edits), ', '.join(edits)))
