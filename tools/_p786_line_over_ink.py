# -*- coding: utf-8 -*-
"""P786: the card's core line paints OVER the pencil ink.

The scanline after P785 still holds the near-black pair (18,13) between
the glow and the green border: THE CARD ART'S OWN PENCIL OUTLINE. The
dice recipe shows no such gap because a die's edge is bright ivory; the
card's edge is opaque black ink, and ink cannot be brightened by any
canvas UNDER the card - which is where the whole recipe lives. So the
same recipe only LOOKS the same if the card's line pass is drawn from
above.

Minimal split, no new optics: the under-card canvas keeps soft+rim+punch
with the line suppressed (lineW 0); the line alone - already blurred per
Denis's note - paints on a thin over-card canvas (dgCanvasLine, z9600),
straddling the art edge so its inner half lights the ink and its outer
half meets the falloff. opts.lineOnly skips soft/rim/punch so the second
call is just the stroke through the same mip blur. Dice: untouched, one
canvas, crisp line, as ever.
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


# ── 1. lineOnly: just the stroke, none of the body ──
sub("""    /* P785: sx/sy are caller dials like soft/rim/strength - the lean
       is proportional to the subject, and 1.24 on a card-tall shape is
       Denis's 'too tall'. Dice pass nothing and keep G's lean. */
    var SX=(opts&&opts.sx!==undefined)?opts.sx:G.sx;
    var SY=(opts&&opts.sy!==undefined)?opts.sy:G.sy;
    sel.forEach(function(sh){lay(sxc,sh,SOFT,{dy:(DY!==null)?DY:G.dy,sx:SX,sy:SY});});
    blurOnto(gx,SOFTR,G.softPasses||1);
    /* then the bright rim, stacked - the punch-out below throws away the
       inner half of every blur, so a single pass never reads as strong */
    sxc.setTransform(dpr,0,0,dpr,0,0);
    sxc.clearRect(0,0,sc.width,sc.height);
    sel.forEach(function(sh){lay(sxc,sh,COL,(DY!==null)?{dy:DY}:{});});
    blurOnto(gx,RIMR,G.rimPasses||1);""",
    """    /* P785: sx/sy are caller dials like soft/rim/strength - the lean
       is proportional to the subject, and 1.24 on a card-tall shape is
       Denis's 'too tall'. Dice pass nothing and keep G's lean. */
    var SX=(opts&&opts.sx!==undefined)?opts.sx:G.sx;
    var SY=(opts&&opts.sy!==undefined)?opts.sy:G.sy;
    /* P786: lineOnly skips the body - the card's line pass paints on
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
    'lineOnly skips the body')

sub("""    if(!(opts&&opts.noPunch)){
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
    """    if(!(opts&&opts.noPunch)&&!(opts&&opts.lineOnly)){
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
    'lineOnly skips the punch')

# ── 2. the over-card line canvas ──
sub("""  _glowHiCv:function(){
    var sc=document.getElementById('screen-match');
    if(!sc)return null;
    var cv=document.getElementById('dgCanvasHi');""",
    """  /* P786: the card line's canvas - ABOVE the card layer (rows 42,
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
  _glowHiCv:function(){
    var sc=document.getElementById('screen-match');
    if(!sc)return null;
    var cv=document.getElementById('dgCanvasHi');""",
    'the line canvas')

# ── 3. the draw: body under, line over ──
sub("""    cv=this._glowHiCv();if(!cv)return;
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
    """    cv=this._glowHiCv();if(!cv)return;
    /* P784: the core canvas is retired - clear a stale one if this
       session predates the retirement */
    var _stale=document.getElementById('dgCanvasCore');if(_stale)_stale.remove();
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
    'both canvases prepared')

sub("""      self._paintHalo(cv,x,sc,dpr,[hull],e.col||self.SEL_COL,e.col||self.SEL_SOFT,
        CG.floor+(1-CG.floor)*Math.min(1,e.k),undefined,
        {sx:1,sy:1,lineBlur:CG.lineBlur});/* P785: no lean, breathed core */""",
    """      var _am=CG.floor+(1-CG.floor)*Math.min(1,e.k);
      /* P786: the body glows from UNDER the card (line suppressed)... */
      self._paintHalo(cv,x,sc,dpr,[hull],e.col||self.SEL_COL,e.col||self.SEL_SOFT,
        _am,0,{sx:1,sy:1});
      /* ...and the breathed line rides ABOVE it, lighting the art's
         pencil ink the way a die's ivory edge never needed. */
      if(xL)self._paintHalo(cvL,xL,sc,dpr,[hull],e.col||self.SEL_COL,e.col||self.SEL_SOFT,
        _am,undefined,{lineOnly:true,lineBlur:CG.lineBlur});""",
    'body under, line over')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d (%s)' % (len(edits), ', '.join(edits)))
