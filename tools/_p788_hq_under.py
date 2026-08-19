# -*- coding: utf-8 -*-
"""P788: a true gaussian for the card, and ALL of it back under the card.

Denis (2026-08-19): "the glow is incredibly low res, even in the lab...
and it all goes over the card rather than under."

LOW RES: the painter's blur is a mip chain - halvings down, bilinear
back up. For a subject the card's size the working mip is ~40px across
a full-screen canvas, and those bilinear facets are the blockiness.
The card path now blurs with canvas shadowBlur - a TRUE gaussian, core
canvas2d on every engine (no ctx.filter gate): each pass's shape is
drawn fully off-canvas and only its blurred shadow lands, in the
pass's own colour. opts.hq, cards only - the dice keep the mip look
their dials were tuned on, byte-identical.

OVER vs UNDER: P786 put the line pass on an over-card canvas to light
the art's pencil ink. Denis rules it the other way: the whole glow
lives UNDER the card again (dgCanvasHi, z41) - line included, still
breathed (lineBlur). The card's dark pencil border now reads as the
object's silhouette against the light, which is what a thing in front
of a glow looks like. dgCanvasLine is retired; opts.lineOnly with it.
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


# ── 1. blurOnto grows the hq gaussian branch ──
sub("""    var blurOnto=function(dst,r,passes){
      var F=Math.max(2,r*dpr);
      var n=Math.max(1,Math.min(5,Math.round(Math.log(F)/Math.LN2)));""",
    """    var blurOnto=function(dst,r,passes,hqCol){
      /* P788: opts.hq = a TRUE gaussian via canvas shadowBlur (core
         canvas2d, every engine - no ctx.filter gate). The pass's shape
         is drawn fully off-canvas and only its shadow lands, in the
         pass's colour. For subjects the card's size the mip chain's
         bilinear facets read as 'incredibly low res' (Denis); the dice
         pass no hq and keep the mip look their dials were tuned on.
         Identity transform: the _sos shadow-offset quirk needs none. */
      if(hqCol&&opts&&opts.hq){
        dst.save();
        dst.setTransform(1,0,0,1,0,0);
        dst.shadowColor=hqCol;
        dst.shadowBlur=Math.max(1,r*dpr);
        dst.shadowOffsetX=S.width;
        dst.shadowOffsetY=0;
        for(var hp=0;hp<(passes||1);hp++)dst.drawImage(S,-S.width,0);
        dst.restore();
        return;
      }
      var F=Math.max(2,r*dpr);
      var n=Math.max(1,Math.min(5,Math.round(Math.log(F)/Math.LN2)));""",
    'the hq gaussian branch')

# ── 2. lineOnly retires; every blur names its colour for hq ──
sub("""    /* P786: lineOnly skips the body - the card's line pass paints on
       its own over-card canvas, where it can light the art's pencil
       ink. Everything else about the call is unchanged. */
    if(!(opts&&opts.lineOnly)){
    sel.forEach(function(sh){lay(sxc,sh,SOFT,{dy:(DY!==null)?DY:G.dy,sx:SX,sy:SY});});
    blurOnto(gx,SOFTR,G.softPasses||1);
    /* then the bright rim, stacked - the punch-out below throws away the
       inner half of every blur, so a single pass never reads as strong */
    sxc.setTransform(dpr,0,0,dpr,0,0);
    sxc.clearRect(0,0,sc.width,sc.height);
    sel.forEach(function(sh){lay(sxc,sh,COL,(DY!==null)?{dy:DY}:{});});
    blurOnto(gx,RIMR,G.rimPasses||1);
    }""",
    """    sel.forEach(function(sh){lay(sxc,sh,SOFT,{dy:(DY!==null)?DY:G.dy,sx:SX,sy:SY});});
    blurOnto(gx,SOFTR,G.softPasses||1,SOFT);
    /* then the bright rim, stacked - the punch-out below throws away the
       inner half of every blur, so a single pass never reads as strong */
    sxc.setTransform(dpr,0,0,dpr,0,0);
    sxc.clearRect(0,0,sc.width,sc.height);
    sel.forEach(function(sh){lay(sxc,sh,COL,(DY!==null)?{dy:DY}:{});});
    blurOnto(gx,RIMR,G.rimPasses||1,COL);""",
    'lineOnly retires from the body')

sub("""    if(!(opts&&opts.noPunch)&&!(opts&&opts.lineOnly)){""",
    """    if(!(opts&&opts.noPunch)){""",
    'lineOnly retires from the punch')

sub("""        blurOnto(gx,opts.lineBlur,2);
      }else{""",
    """        blurOnto(gx,opts.lineBlur,2,COL);
      }else{""",
    'the breathed line names its colour')

# ── 3. the over-card line canvas retires ──
sub("""  /* P786: the card line's canvas - ABOVE the card layer (rows 42,
     dragged card 9500), because the card's edge is opaque pencil ink
     and light from underneath can never brighten ink. Holds ONLY the
     blurred line pass. */
  _glowLineCv:function(){
    var sc=document.getElementById('screen-match');
    if(!sc)return null;
    var cv=document.getElementById('dgCanvasLine');
    if(!cv){
      this._glowHiCv();
      cv=document.createElement('canvas');cv.id='dgCanvasLine';
      cv.style.cssText='position:absolute;inset:0;width:100%;height:100%;'
        +'pointer-events:none;z-index:9600';
      sc.appendChild(cv);
    }
    return cv;
  },
  _glowHiCv:function(){""",
    """  _glowHiCv:function(){""",
    'the line canvas retires')

sub("""    var _stale=document.getElementById('dgCanvasCore');if(_stale)_stale.remove();
    var cvL=this._glowLineCv();
    var sc=sc0.getBoundingClientRect();
    if(sc.width<10)return;
    var dpr=Math.min(devicePixelRatio||1,this.GLOW_DPR_MAX||3);
    if(cv.width!==Math.round(sc.width*dpr)||cv.height!==Math.round(sc.height*dpr)){
      cv.width=Math.round(sc.width*dpr);cv.height=Math.round(sc.height*dpr);
    }
    if(cvL&&(cvL.width!==cv.width||cvL.height!==cv.height)){cvL.width=cv.width;cvL.height=cv.height;}
    var x=cv.getContext('2d');
    x.setTransform(dpr,0,0,dpr,0,0);
    x.clearRect(0,0,sc.width,sc.height);
    var xL=cvL?cvL.getContext('2d'):null;
    if(xL){xL.setTransform(dpr,0,0,dpr,0,0);xL.clearRect(0,0,sc.width,sc.height);}
    if(!live)return;""",
    """    var _stale=document.getElementById('dgCanvasCore');if(_stale)_stale.remove();
    var _staleL=document.getElementById('dgCanvasLine');if(_staleL)_staleL.remove();/* P788 */
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
    'one canvas prepared')

# ── 4. one call, under the card, hq ──
sub("""      var _am=CG.floor+(1-CG.floor)*Math.min(1,e.k);
      /* P786: the body glows from UNDER the card (line suppressed)... */
      self._paintHalo(cv,x,sc,dpr,[hull],e.col||self.SEL_COL,e.col||self.SEL_SOFT,
        _am,0,{sx:1,sy:1});
      /* ...and the breathed line rides ABOVE it, lighting the art's
         pencil ink the way a die's ivory edge never needed. */
      if(xL)self._paintHalo(cvL,xL,sc,dpr,[hull],e.col||self.SEL_COL,e.col||self.SEL_SOFT,
        _am,undefined,{lineOnly:true,lineBlur:CG.lineBlur});""",
    """      var _am=CG.floor+(1-CG.floor)*Math.min(1,e.k);
      /* P788: ONE call, ALL of it under the card (Denis), gaussian-
         blurred (hq) - the breathed line included. The card's pencil
         border reads as the object's silhouette against the light. */
      self._paintHalo(cv,x,sc,dpr,[hull],e.col||self.SEL_COL,e.col||self.SEL_SOFT,
        _am,undefined,{sx:1,sy:1,lineBlur:CG.lineBlur,hq:true});""",
    'one call, under, hq')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d (%s)' % (len(edits), ', '.join(edits)))
