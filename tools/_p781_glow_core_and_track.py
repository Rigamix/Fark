# -*- coding: utf-8 -*-
"""P781: the core gets its own compositing; the halo stops drifting off
its card.

Denis (2026-08-19, third crop): "can barely see the core, still a hole
in the alpha." His crop holds the two remaining causes:

1. HIS CARD IS OVER LIGHT WOOD - and mix-blend-mode:screen vanishes on
   light backdrops by construction (screen can only brighten, and
   parchment is already bright). The hot core octave was near-white,
   so over anything pale it composited to nothing. The CORE now paints
   on its OWN canvas (dgCanvasCore, same z, appended after -> above
   the spill canvas) with NORMAL compositing and a chroma'd gold
   (#ffe08a): saturated enough to show on parchment, still hot on the
   dark table. The wide spill keeps the screen blend - that is where
   'brightening the set' lives, and it reads on the dark table where
   spill is visible at all.

2. THE HOLE BREATHES - famBob translates .fcvIn (the art) +-0.85cqw
   forever, while the stamp was painted once at the .fcv box: the art
   bobs out from under its own halo, opening a gap that moves with the
   phase. His three crops caught three phases. A LIT card now holds
   still (animation-play-state:paused on its .fcvIn) - precedent P713,
   spent cards already sit still - so the halo and the art cannot part.
   Same desync on tap-focus (scale 1.24 applied AFTER the paint):
   _cardFocusToggle/_cardFocusClose repaint the glows once the scale
   transition settles, so the halo re-fits the grown card.
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


# ── 1. a lit card holds still - the bob cannot drift the art off its halo ──
sub("""#famRowP .fcv.fcv-lit{filter:brightness(1.05)}""",
    """#famRowP .fcv.fcv-lit{filter:brightness(1.05)}
/* P781: and it HOLDS STILL - famBob translates the art inside the box
   the halo was stamped from, so a bobbing lit card breathes out from
   under its own light (the hole that moved between Denis's crops).
   animation:none, NOT paused - paused freezes the bob mid-translate
   and the hole freezes open with it; none resets the art to the box.
   Precedent: spent cards already sit still this way (P713). */
#famRowP .fcv.fcv-lit .fcvIn{animation:none}""",
    'a lit card holds still')

# ── 2. the core canvas: normal compositing, above the screened spill ──
sub("""  _glowHiCv:function(){
    var sc=document.getElementById('screen-match');
    if(!sc)return null;
    var cv=document.getElementById('dgCanvasHi');""",
    """  /* P781: the CORE's canvas - same geometry, NO blend mode, appended
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
      cv.style.cssText='position:absolute;inset:0;width:100%;height:100%;'
        +'pointer-events:none;z-index:41';
      sc.appendChild(cv);
    }
    return cv;
  },
  _glowHiCv:function(){
    var sc=document.getElementById('screen-match');
    if(!sc)return null;
    var cv=document.getElementById('dgCanvasHi');""",
    'the core canvas')

# ── 3. the draw splits octaves by canvas ──
sub("""  _drawCardGlows:function(){
    var sc0=document.getElementById('screen-match');
    var cv=document.getElementById('dgCanvasHi');
    var live=this._cardGlows&&Object.keys(this._cardGlows).length;
    if(!sc0||(!live&&!cv))return;
    cv=this._glowHiCv();if(!cv)return;
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
    """  _drawCardGlows:function(){
    var sc0=document.getElementById('screen-match');
    var cv=document.getElementById('dgCanvasHi');
    var live=this._cardGlows&&Object.keys(this._cardGlows).length;
    if(!sc0||(!live&&!cv))return;
    cv=this._glowHiCv();if(!cv)return;
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
    'both canvases sized and cleared')

sub("""      /* P779: a caller accent (the rival's red telegraph) re-tints the
         whole octave stack - same light, their colour. */
      var _oct=CG.octaves;
      if(e.col&&_oct)_oct=_oct.map(function(oc){return {r:oc.r,col:e.col,passes:oc.passes,deep:oc.deep};});
      self._paintHalo(cv,x,sc,dpr,[shape],e.col||CG.col,e.col||CG.softCol,
        CG.floor+(1-CG.floor)*Math.min(1,e.k),CG.line,
        {soft:CG.soft,rim:CG.rim,strength:CG.strength,dy:r.height*(CG.dyF||0),
         octaves:_oct,/* P779: one continuous light */
         sx:1,sy:1,/* P777: the card does not lean like a die */
         punchUnder:true,punchScaleMul:1/(CG.grow||1)});/* P777: tail-only, tucked under the card */""",
    """      /* P779: a caller accent (the rival's red telegraph) re-tints the
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
      if(_core.length&&x2)self._paintHalo(cv2,x2,sc,dpr,[shape],e.col||CG.col,e.col||CG.softCol,
        _am,CG.line,_opts(_core));""",
    'octaves split by canvas')

# ── 4. the core's colour carries chroma; marked core. r 3 -> 6: alone
#      on its canvas, r3 blurred barely past the art's own edge once the
#      punch ate the inner half - a 1px sliver hidden under the card
#      (measured: paint box ended 1 device px inside the box edge). The
#      shared-canvas look only ever showed r8's edge. ──
sub("""    octaves:[{r:3,col:'#fff7dc',passes:2},{r:8,col:'#ffd24a'},{r:24,col:'#ff9e30',deep:true}]},""",
    """    octaves:[{r:6,col:'#ffe08a',passes:2,core:true},{r:8,col:'#ffd24a'},{r:24,col:'#ff9e30',deep:true}]},""",
    'the core is chroma gold, marked')

# ── 5. focus repaints once the scale settles ──
sub("""function _cardFocusClose(){
  var t=document.getElementById('cardFocusTip');if(t)t.remove();
  if(_cardFocusEl){try{_cardFocusEl.classList.remove('focus');}catch(e){}}
  _cardFocusEl=null;
  try{var ms=document.getElementById('screen-match');if(ms)ms.classList.remove('tip-open');}catch(e){}
}""",
    """function _cardFocusClose(){
  var t=document.getElementById('cardFocusTip');if(t)t.remove();
  if(_cardFocusEl){try{_cardFocusEl.classList.remove('focus');}catch(e){}}
  _cardFocusEl=null;
  try{var ms=document.getElementById('screen-match');if(ms)ms.classList.remove('tip-open');}catch(e){}
  _cardGlowRefit();
}
/* P781: the focus scale (1.24) lands AFTER a glow was painted, so the
   halo sat stamped at the old size - the card grew out of its light.
   One refit, after the .18s scale transition settles. */
function _cardGlowRefit(){
  try{
    if(window.D3X&&D3X._cardGlows&&Object.keys(D3X._cardGlows).length){
      setTimeout(function(){try{D3X._drawCardGlows();}catch(e){}},230);
    }
  }catch(e){}
}""",
    'focus close refits')

sub("""  _cardFocusEl=el;el.classList.add('focus');""",
    """  _cardFocusEl=el;el.classList.add('focus');
  _cardGlowRefit();/* P781: the halo re-fits the grown card */""",
    'focus open refits')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d (%s)' % (len(edits), ', '.join(edits)))
