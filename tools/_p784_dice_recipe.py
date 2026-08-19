# -*- coding: utf-8 -*-
"""P784: the card glow IS the dice glow.

Denis (2026-08-19): "I don't understand what you're doing... should be
the same effect as on the dice. It looks weirder and weirder."

He is right. P778-P783 built a bespoke optical system - octaves, a
second canvas, two blend modes, rim bloom - and every layer of it
manufactured a new seam the dice recipe never had. The dice glow is
one painter call with one set of dials, and he likes it. The card now
makes THE SAME CALL:

  _paintHalo(cv, x, sc, dpr, [hull], SEL_COL, SEL_SOFT, armRamp)

Same GLOW dials (soft 11, rim 3 x5, line 3.2, lean, standard punch),
same SEL gold, no opts. The only difference is the silhouette: the
card's rounded box - built from the UNTRANSFORMED element size (the
AABB of a rotated card is inflated) and rotated to match the fan - in
place of a die's projected hull. The stroked line rides the hull
exactly as it rides a die's, and it straddles the card's edge so the
punch's clear-ring can never read as a gap.

RETIRED in this patch: the octave path, punchUnder/punchClear, the
blurOnto mip-cap override, the core canvas (_glowCoreCv/dgCanvasCore),
the screen blend on dgCanvasHi, and CARD_GLOW's private colour/radius
dials. _paintHalo returns to its pre-P777 body. KEPT from the saga,
because they fix geometry/compositing truths independent of any
recipe: .fcv-lit (a lit card drops the dark contact shadows that
painted over the halo - P780), the bob freeze and focus refit (the
halo cannot track an animating card - P781).

CARD_GLOW keeps only what is genuinely the card's own: the hull's
corner radius and the drag ramp's floor.
"""
import io, os, sys, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'fark_proto.html')
s = io.open(P, encoding='utf-8', newline='').read()
edits = []


def sub(old, new, label):
    global s
    if s.count(old) == 1:
        s = s.replace(old, new)
        edits.append(label)
        return
    pat = re.escape(old).replace('\\\n', '\n').replace('\n', '\\r?\n')
    hits = re.findall(pat, s)
    if len(hits) != 1:
        sys.exit('ANCHOR x%d for %s (nothing written)' % (len(hits), label))
    s = re.sub(pat, lambda m: new, s, count=1)
    edits.append(label)


# ── A. blurOnto: the mip-cap override goes ──
sub("""    var blurOnto=function(dst,r,passes,maxN){
      var F=Math.max(2,r*dpr);
      /* P779: the default cap of 5 tops the radius out at 32/dpr user px
         - ~10.7 on a dpr-3 phone. A wide octave passes 6. */
      var n=Math.max(1,Math.min(maxN||5,Math.round(Math.log(F)/Math.LN2)));""",
    """    var blurOnto=function(dst,r,passes){
      var F=Math.max(2,r*dpr);
      var n=Math.max(1,Math.min(5,Math.round(Math.log(F)/Math.LN2)));""",
    'blurOnto restored')

# ── B. the octave path goes; soft+rim exactly as the dice run it ──
sub("""    var SX=(opts&&opts.sx!==undefined)?opts.sx:G.sx;
    var SY=(opts&&opts.sy!==undefined)?opts.sy:G.sy;
    if(opts&&opts.octaves){
      /* P779: ONE CONTINUOUS LIGHT. The same silhouette, blurred at a
         few radii in a few colours and SUMMED - a smooth curve with no
         rim band and no boundary between layers (Denis: "I can see the
         two layers"). Each octave: {r, col, passes, deep}. */
      opts.octaves.forEach(function(oc){
        sxc.setTransform(dpr,0,0,dpr,0,0);
        sxc.globalCompositeOperation='source-over';
        sxc.clearRect(0,0,sc.width,sc.height);
        sel.forEach(function(sh){lay(sxc,sh,oc.col,{dy:(DY!==null)?DY:0,sx:SX,sy:SY});});
        blurOnto(gx,oc.r,oc.passes||1,oc.deep?6:undefined);
      });
    }else{
    sel.forEach(function(sh){lay(sxc,sh,SOFT,{dy:(DY!==null)?DY:G.dy,sx:SX,sy:SY});});
    blurOnto(gx,SOFTR,(opts&&opts.softPasses)||G.softPasses||1);/* P778b: caller's count */
    /* then the bright rim, stacked - the punch-out below throws away the
       inner half of every blur, so a single pass never reads as strong */
    sxc.setTransform(dpr,0,0,dpr,0,0);
    sxc.clearRect(0,0,sc.width,sc.height);
    sel.forEach(function(sh){lay(sxc,sh,COL,(DY!==null)?{dy:DY}:{});});
    blurOnto(gx,RIMR,G.rimPasses||1);
    }""",
    """    sel.forEach(function(sh){lay(sxc,sh,SOFT,{dy:(DY!==null)?DY:G.dy,sx:G.sx,sy:G.sy});});
    blurOnto(gx,SOFTR,G.softPasses||1);
    /* then the bright rim, stacked - the punch-out below throws away the
       inner half of every blur, so a single pass never reads as strong */
    sxc.setTransform(dpr,0,0,dpr,0,0);
    sxc.clearRect(0,0,sc.width,sc.height);
    sel.forEach(function(sh){lay(sxc,sh,COL,(DY!==null)?{dy:DY}:{});});
    blurOnto(gx,RIMR,G.rimPasses||1);""",
    'one soft+rim recipe again')

# ── C. the punch: one grammar, the dice's ──
sub("""    if(opts&&opts.punchUnder){
      /* P782: the inset is the caller's - the rim-bloom core cuts ~3px
         deep so its inner ring washes OVER the card's own dark outline
         (its canvas sits above the card layer); the spill keeps the
         default hair-inside cut. */
      var PCL=(opts.punchClear!==undefined)?opts.punchClear:G.clear;
      gx.globalCompositeOperation='destination-out';
      gx.globalAlpha=1;
      sel.forEach(function(sh){
        if(sh&&sh.stamp){
          lay(gx,sh,null,{scaleMul:(opts.punchScaleMul||1)
            *(1-(2*PCL)/Math.max(8,Math.min(sh.stamp.w,sh.stamp.h)))});
        }else{
          lay(gx,sh,null,{shrink:PCL});
        }
      });
      gx.globalCompositeOperation='source-over';
    }else if(!(opts&&opts.noPunch)){""",
    """    if(!(opts&&opts.noPunch)){""",
    'one punch grammar')

# ── D. the core canvas goes ──
sub("""  /* P781: the CORE's canvas - same geometry, NO blend mode, appended
     after the spill canvas so it paints above it. Screen blending
     vanishes over light backdrops (it can only brighten), so the hot
     edge lives here where it is visible on parchment and table alike. */
  _glowCoreCv:function(){
    var sc=document.getElementById('screen-match');
    if(!sc)return null;
    var cv=document.getElementById('dgCanvasCore');
    if(!cv){
      this._glowHiCv();/* the spill canvas first, so core lands above it */
      cv=document.createElement('canvas');cv.id='dgCanvasCore';
      /* P782: ABOVE the card layer (rows 42, dragged card 9500) - rim
         light BLOOMS over an object's edge. The card art carries an
         opaque black pencil outline, and a light from underneath can
         never brighten ink; from above, the border catches the gold. */
      cv.style.cssText='position:absolute;inset:0;width:100%;height:100%;'
        +'pointer-events:none;z-index:9600';
      sc.appendChild(cv);
    }
    return cv;
  },
  _glowHiCv:function(){""",
    """  _glowHiCv:function(){""",
    'the core canvas goes')

# ── E. the screen blend goes ──
sub("""      /* P778: SCREEN-BLENDED - the halo brightens the table under it
         (grain showing through) instead of painting over it. This is
         the additive read Denis asked for; the ctx-level 'lighter' in
         _paintHalo only ever blended the glow with its own cleared
         canvas. Cards only: the dice canvas is separate and liked. */
      cv.style.cssText='position:absolute;inset:0;width:100%;height:100%;'
        +'pointer-events:none;z-index:41;mix-blend-mode:screen';
      sc.appendChild(cv);""",
    """      cv.style.cssText='position:absolute;inset:0;width:100%;height:100%;'
        +'pointer-events:none;z-index:41';
      sc.appendChild(cv);""",
    'the screen blend goes')

# ── F1. the draw's head: one canvas again ──
sub("""    cv=this._glowHiCv();if(!cv)return;
    var cv2=this._glowCoreCv();
    var sc=sc0.getBoundingClientRect();
    if(sc.width<10)return;
    var dpr=Math.min(devicePixelRatio||1,this.GLOW_DPR_MAX||3);
    if(cv.width!==Math.round(sc.width*dpr)||cv.height!==Math.round(sc.height*dpr)){
      cv.width=Math.round(sc.width*dpr);cv.height=Math.round(sc.height*dpr);
    }
    if(cv2&&(cv2.width!==cv.width||cv2.height!==cv.height)){cv2.width=cv.width;cv2.height=cv.height;}
    var x=cv.getContext('2d');
    x.setTransform(dpr,0,0,dpr,0,0);
    x.clearRect(0,0,sc.width,sc.height);
    var x2=cv2?cv2.getContext('2d'):null;
    if(x2){x2.setTransform(dpr,0,0,dpr,0,0);x2.clearRect(0,0,sc.width,sc.height);}
    if(!live)return;""",
    """    cv=this._glowHiCv();if(!cv)return;
    /* P784: the core canvas is retired - clear a stale one if this
       session predates the retirement */
    var _stale=document.getElementById('dgCanvasCore');if(_stale)_stale.remove();
    var sc=sc0.getBoundingClientRect();
    if(sc.width<10)return;
    var dpr=Math.min(devicePixelRatio||1,this.GLOW_DPR_MAX||3);
    if(cv.width!==Math.round(sc.width*dpr)||cv.height!==Math.round(sc.height*dpr)){
      cv.width=Math.round(sc.width*dpr);cv.height=Math.round(sc.height*dpr);
    }
    var x=cv.getContext('2d');
    x.setTransform(dpr,0,0,dpr,0,0);
    x.clearRect(0,0,sc.width,sc.height);
    if(!live)return;""",
    'one canvas again')

# ── F2. the per-entry body: the dice call on the card's hull ──
sub("""      var r=e.el.getBoundingClientRect();
      if(r.width<4)return;
      /* P751: THE CARD'S OWN SILHOUETTE. The halo is derived from the
         card art's alpha, at the element's on-screen rotation and scale
         (Denis: "derived from the card alpha at all times so it never
         risks not matching its shape"). The bounding rect's centre is
         the transformed centre; rotate and scale are the standalone CSS
         properties the fan and the drag use. A face-down or imageless
         card falls back to the rounded box. */
      var shape=null;
      var img=e.el.querySelector('.fcvIn img')||e.el.querySelector('img');
      if(img&&img.complete&&img.naturalWidth>0){
        var cs2=getComputedStyle(e.el);
        var rot=parseFloat(cs2.rotate);if(isNaN(rot))rot=0;
        var scl=parseFloat(cs2.scale);if(!(scl>0))scl=1;
        shape={stamp:{img:img,
          cx:r.left-sc.left+r.width/2,cy:r.top-sc.top+r.height/2,
          w:e.el.offsetWidth*scl*(CG.grow||1),h:e.el.offsetHeight*scl*(CG.grow||1),
          rot:rot*Math.PI/180}};
      }else{
        shape={hull:self._rectHull(r.left-sc.left,r.top-sc.top,r.width,r.height,
          Math.min(r.width,r.height)*CG.round)};
      }
      /* P779: a caller accent (the rival's red telegraph) re-tints the
         whole octave stack - same light, their colour. */
      var _oct=CG.octaves;
      if(e.col&&_oct)_oct=_oct.map(function(oc){return {r:oc.r,col:e.col,passes:oc.passes,deep:oc.deep,core:oc.core};});
      /* P781: core octaves paint on the NORMAL canvas (visible on any
         backdrop), the rest on the screened spill canvas. */
      var _spill=_oct.filter(function(oc){return !oc.core;});
      var _core=_oct.filter(function(oc){return oc.core;});
      var _opts=function(list){return {soft:CG.soft,rim:CG.rim,strength:CG.strength,
        dy:r.height*(CG.dyF||0),octaves:list,sx:1,sy:1,
        punchUnder:true,punchScaleMul:1/(CG.grow||1)};};
      var _am=CG.floor+(1-CG.floor)*Math.min(1,e.k);
      if(_spill.length)self._paintHalo(cv,x,sc,dpr,[shape],e.col||CG.col,e.col||CG.softCol,
        _am,CG.line,_opts(_spill));
      if(_core.length&&x2){
        var _co=_opts(_core);
        _co.punchClear=(CG.bloomPx!==undefined)?CG.bloomPx:3;/* P782: the rim-bloom depth */
        self._paintHalo(cv2,x2,sc,dpr,[shape],e.col||CG.col,e.col||CG.softCol,
          _am,CG.line,_co);
      }""",
    """      var r=e.el.getBoundingClientRect();
      if(r.width<4)return;
      /* P784 (Denis: "should be the same effect as on the dice"): the
         card halo is the DICE's halo - the same painter call with the
         same GLOW dials and SEL colours, no opts. The only difference
         is the silhouette: the card's rounded box, built from the
         UNTRANSFORMED element size (the AABB of a rotated card is
         inflated) and rotated to match the fan. The stroked line rides
         the hull exactly as it rides a die's, straddling the card's
         edge, so the punch's clear-ring can never read as a gap. */
      var cs2=getComputedStyle(e.el);
      var rot=parseFloat(cs2.rotate);if(isNaN(rot))rot=0;
      var scl=parseFloat(cs2.scale);if(!(scl>0))scl=1;
      var w=e.el.offsetWidth*scl*self.GLOW.grow,h=e.el.offsetHeight*scl*self.GLOW.grow;
      var ccx=r.left-sc.left+r.width/2,ccy=r.top-sc.top+r.height/2;
      var hull=self._rectHull(ccx-w/2,ccy-h/2,w,h,Math.min(w,h)*CG.round);
      if(rot){
        var rad=rot*Math.PI/180,cr=Math.cos(rad),sr=Math.sin(rad);
        hull=hull.map(function(p){var dx=p[0]-ccx,dy=p[1]-ccy;
          return [ccx+dx*cr-dy*sr,ccy+dx*sr+dy*cr];});
      }
      self._paintHalo(cv,x,sc,dpr,[hull],e.col||self.SEL_COL,e.col||self.SEL_SOFT,
        CG.floor+(1-CG.floor)*Math.min(1,e.k));""",
    'the dice call on the card hull')

# ── G. CARD_GLOW keeps only the card's own geometry ──
sub("""  /* P779 (Denis: "a magical golden glow"): the card halo is summed
     octaves - hot near-white core, golden body, faint warm spill. grow
     1.0: nothing solid survives the punch, every visible pixel is
     blur. col stays as the tint the drag/armed callers fall back to
     for their own accents. */
  CARD_GLOW:{col:'#ffd84e', softCol:'#ffae1f', soft:11, rim:2.5, strength:0.91,
    grow:1.0, dyF:0, round:0.075, line:0, floor:0.42,
    octaves:[{r:6,col:'#ffe08a',passes:2,core:true},{r:12,col:'#ffd24a',core:true},{r:24,col:'#ff9e30',deep:true}]},""",
    """  /* P784 (Denis: "should be the same effect as on the dice"): the
     card borrows the dice's GLOW dials and SEL colours wholesale - one
     look, two subjects. Only the card's own geometry lives here: its
     hull's corner radius and the drag ramp's floor. */
  CARD_GLOW:{round:0.075, floor:0.42},""",
    'CARD_GLOW is geometry only')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d (%s)' % (len(edits), ', '.join(edits)))
