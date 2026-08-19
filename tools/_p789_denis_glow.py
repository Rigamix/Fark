# -*- coding: utf-8 -*-
"""P789: the card glow is Denis's own prototype - CSS, verbatim.

Denis dropped card-glow-test.html ("can you use this?") - a production
spec: two solid-colour divs behind the card, masked by the card art's
alpha; the art on top hides them completely and all you ever see is
their drop-shadow, a REAL GPU gaussian that spreads outward from the
true silhouette at constant width. His authored dials ride CSS vars
(core hsl(13 100% 63%) b1.83 sharp .67, glow hsl(36 88% 56%) b.40,
halo 5, bloom 17, plus-lighter, breathe/swell, 34% candle flicker).
It answers every open complaint by construction: true gaussian (not
the mip facets), under the card, silhouette-true, and the motion he
sketched as optional.

ONE structural adaptation, forced by the game: the glow DOM lives in a
FLAT layer (#cardGlowLayer, z41, under the rows at 42) positioned per
lit card - NOT inside .fcv - because #famRowP carries a 3D transform
and WebKit clips filters inside such a context to the element's own
box (P727/P746-748, the reason the canvas painter ever existed). His
two hard rules hold: mask on the child <i>, filter on the parent span
(his CSS verbatim); and the card's dark drop-shadow is already removed
while lit (.fcv-lit, P780). The bob freeze and focus refit (P781) keep
the layer aligned exactly as they kept the canvas aligned.

cardGlow(key,el,k,col) keeps its API - the drag ramp and the rival's
armed telegraph don't change. k maps onto his state axis: state = 1 +
0.9*(floor+(1-floor)*k), so full arm = his 'selected' 1.9. An accent
(the rival's red) overrides --core and --glow together.

RETIRED: dgCanvasHi and the whole canvas card path - _paintHalo drops
the P785/788 card additions (sx/sy opts, lineBlur, hq shadowBlur) and
returns to the dice's exact pre-saga body. CARD_GLOW keeps only floor
(the arm ramp's start). The dice canvas path is byte-identical.

The prototype itself is versioned at tools/card_glow_test.html - it is
the card glow's authoring tool now; approved numbers get baked into
the game CSS the same way every lab look does.
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


# ── 1. the CSS: his prototype's production block, layer-scoped ──
sub("""#famRowP .fcv.fcv-lit .fcvIn{animation:none}""",
    """#famRowP .fcv.fcv-lit .fcvIn{animation:none}
/* P789: THE CARD GLOW IS DENIS'S PROTOTYPE (tools/card_glow_test.html),
   his production CSS verbatim: two solid-colour divs masked by the
   card art's alpha - all you see is their drop-shadow, a true GPU
   gaussian hugging the real silhouette. The layer is FLAT and sits
   under the rows (z41), because a filter inside the 3D-transformed
   rows is clipped to its own box on WebKit (P727/P746-748). Vars
   carry his authored defaults; the lab and his test page share them. */
#cardGlowLayer{position:absolute;inset:0;pointer-events:none;z-index:41;
  --core:hsl(13 100% 63%);--glow:hsl(36 88% 56%);
  --core-b:1.83;--glow-b:0.40;--core-sharp:0.67;
  --halo:5;--bloom:17;--intensity:1;--speed:1.3;--flick:1;--blend:plus-lighter}
#cardGlowLayer .cgw{position:absolute}
.cgw .spill{position:absolute;left:50%;top:50%;width:190%;height:165%;
  translate:-50% -50%;pointer-events:none;
  background:radial-gradient(closest-side,var(--glow),transparent 70%);
  opacity:calc(.22*var(--glow-b)*var(--intensity)*var(--state,1));
  mix-blend-mode:var(--blend);transition:opacity .2s ease}
.cgw .glow{position:absolute;inset:0;mix-blend-mode:var(--blend);opacity:var(--flick)}
.cgw .breathe{position:absolute;inset:0;
  animation:cgBreathe calc(3.7s/max(var(--speed),.0001)) ease-in-out infinite}
.cgw .halo,.cgw .bloom{position:absolute;inset:0;transition:opacity .2s ease;
  will-change:opacity,filter}
/* mask on the CHILD, filter on the PARENT - filters run before masking
   (Denis's rule 1, his comment verbatim) */
.cgw .halo>i,.cgw .bloom>i{position:absolute;inset:0;
  -webkit-mask:var(--card-src) center/contain no-repeat;
  mask:var(--card-src) center/contain no-repeat}
.cgw .bloom{opacity:min(1,calc(var(--glow-b)*var(--intensity)*var(--state,1)));
  filter:drop-shadow(0 0 calc(var(--bloom)*1px) var(--glow))
         drop-shadow(0 0 calc(var(--bloom)*0.5px) var(--glow))
         brightness(max(1,calc(var(--glow-b)*var(--intensity)*var(--state,1))));
  animation:cgSwell calc(5.3s/max(var(--speed),.0001)) ease-in-out infinite}
.cgw .bloom>i{background:var(--glow)}
/* sharpness redistributes the same reach: one wide pass = gaussian
   mush; four tight passes compound into a hard-edged plateau */
.cgw .halo{z-index:2;opacity:min(1,calc(var(--core-b)*var(--intensity)*var(--state,1)));
  filter:drop-shadow(0 0 calc(var(--halo)*(1 - 0.75*var(--core-sharp))*1px) var(--core))
         drop-shadow(0 0 calc(var(--halo)*0.25*var(--core-sharp)*1px) var(--core))
         drop-shadow(0 0 calc(var(--halo)*0.25*var(--core-sharp)*1px) var(--core))
         drop-shadow(0 0 calc(var(--halo)*0.25*var(--core-sharp)*1px) var(--core))
         brightness(max(1,calc(var(--core-b)*var(--intensity)*var(--state,1))))}
.cgw .halo>i{background:var(--core)}
@keyframes cgBreathe{0%,100%{opacity:.88}50%{opacity:1}}
@keyframes cgSwell{
  0%,100%{opacity:min(1,calc(var(--glow-b)*var(--intensity)*var(--state,1)*.82))}
  50%{opacity:min(1,calc(var(--glow-b)*var(--intensity)*var(--state,1)*1.25))}}
body.reduced-motion .cgw .breathe,body.reduced-motion .cgw .bloom{animation:none}""",
    "his production CSS, layer-scoped")

# ── 2. _paintHalo returns to the dice's exact body ──
sub("""    var blurOnto=function(dst,r,passes,hqCol){
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
        /* shadowBlur is sigma-ish: x2 so a dial 'reach' of r reads as
           ~r user px of visible falloff, matching the mip semantics */
        dst.shadowBlur=Math.max(1,r*dpr*2);
        dst.shadowOffsetX=S.width;
        dst.shadowOffsetY=0;
        for(var hp=0;hp<(passes||1);hp++)dst.drawImage(S,-S.width,0);
        dst.restore();
        return;
      }
      var F=Math.max(2,r*dpr);
      var n=Math.max(1,Math.min(5,Math.round(Math.log(F)/Math.LN2)));""",
    """    var blurOnto=function(dst,r,passes){
      var F=Math.max(2,r*dpr);
      var n=Math.max(1,Math.min(5,Math.round(Math.log(F)/Math.LN2)));""",
    'blurOnto restored')

sub("""    /* P785: sx/sy are caller dials like soft/rim/strength - the lean
       is proportional to the subject, and 1.24 on a card-tall shape is
       Denis's 'too tall'. Dice pass nothing and keep G's lean. */
    var SX=(opts&&opts.sx!==undefined)?opts.sx:G.sx;
    var SY=(opts&&opts.sy!==undefined)?opts.sy:G.sy;
    sel.forEach(function(sh){lay(sxc,sh,SOFT,{dy:(DY!==null)?DY:G.dy,sx:SX,sy:SY});});
    blurOnto(gx,SOFTR,G.softPasses||1,SOFT);""",
    """    sel.forEach(function(sh){lay(sxc,sh,SOFT,{dy:(DY!==null)?DY:G.dy,sx:G.sx,sy:G.sy});});
    blurOnto(gx,SOFTR,G.softPasses||1);""",
    'soft pass restored')

sub("""    sel.forEach(function(sh){lay(sxc,sh,COL,(DY!==null)?{dy:DY}:{});});
    blurOnto(gx,RIMR,G.rimPasses||1,COL);""",
    """    sel.forEach(function(sh){lay(sxc,sh,COL,(DY!==null)?{dy:DY}:{});});
    blurOnto(gx,RIMR,G.rimPasses||1);""",
    'rim pass restored')

sub("""    if(LINE>0){
      if(opts&&opts.lineBlur){
        /* P785: the hot core takes a breath of blur (Denis) - the same
           line, stroked into the scratch and mip-softened instead of
           drawn crisp. Two passes keep it hot through the blur. */
        sxc.setTransform(dpr,0,0,dpr,0,0);
        sxc.globalCompositeOperation='source-over';
        sxc.clearRect(0,0,sc.width,sc.height);
        sxc.strokeStyle=COL;sxc.lineWidth=LINE;sxc.lineJoin='round';
        sel.forEach(function(sh){
          if(sh&&sh.stamp)return;
          trace(sxc,sh&&sh.hull||sh,0);sxc.stroke();
        });
        blurOnto(gx,opts.lineBlur,2,COL);
      }else{
      gx.strokeStyle=COL;gx.lineWidth=LINE;gx.lineJoin='round';
      gx.globalAlpha=1;
      sel.forEach(function(sh){
        if(sh&&sh.stamp)return;
        trace(gx,sh&&sh.hull||sh,0);gx.stroke();
      });
      }
    }""",
    """    if(LINE>0){
      gx.strokeStyle=COL;gx.lineWidth=LINE;gx.lineJoin='round';
      gx.globalAlpha=1;
      sel.forEach(function(sh){
        if(sh&&sh.stamp)return;
        trace(gx,sh&&sh.hull||sh,0);gx.stroke();
      });
    }""",
    'line pass restored')

# ── 3. the card canvas retires; the layer takes over ──
sub("""  _glowHiCv:function(){
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
    """  /* P789: the glow layer - Denis's prototype DOM, one wrapper per lit
     card, positioned where the canvas stamp used to paint. FLAT on
     purpose: no 3D ancestor, so WebKit cannot clip the drop-shadows
     (P727/P746-748). Same z as the retired canvas (41, under rows). */
  _cardGlowLayer:function(){
    var sc=document.getElementById('screen-match');
    if(!sc)return null;
    var ly=document.getElementById('cardGlowLayer');
    if(!ly){
      ly=document.createElement('div');ly.id='cardGlowLayer';
      sc.appendChild(ly);
    }
    return ly;
  },""",
    'the layer replaces the canvas')

sub("""  _drawCardGlows:function(){
    var sc0=document.getElementById('screen-match');
    var cv=document.getElementById('dgCanvasHi');
    var live=this._cardGlows&&Object.keys(this._cardGlows).length;
    if(!sc0||(!live&&!cv))return;
    cv=this._glowHiCv();if(!cv)return;
    /* P784: the core canvas is retired - clear a stale one if this
       session predates the retirement */
    var _stale=document.getElementById('dgCanvasCore');if(_stale)_stale.remove();
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
    if(!live)return;
    var self=this,CG=this.CARD_GLOW;
    Object.keys(this._cardGlows).forEach(function(kk){
      var e=self._cardGlows[kk];
      if(!e.el||!e.el.isConnected){delete self._cardGlows[kk];return;}
      var r=e.el.getBoundingClientRect();
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
      /* P785: trim to the ART's edge - the webp carries a ~1.7%
         transparent margin per side, and a hull on the element box put
         the line and the punch outside the visible card, exposing a
         dark ring of erased halo (Denis: 'is it card thickness?'). */
      var w=e.el.offsetWidth*scl*self.GLOW.grow*(CG.trim||1),
          h=e.el.offsetHeight*scl*self.GLOW.grow*(CG.trim||1);
      var ccx=r.left-sc.left+r.width/2,ccy=r.top-sc.top+r.height/2;
      var hull=self._rectHull(ccx-w/2,ccy-h/2,w,h,Math.min(w,h)*CG.round);
      if(rot){
        var rad=rot*Math.PI/180,cr=Math.cos(rad),sr=Math.sin(rad);
        hull=hull.map(function(p){var dx=p[0]-ccx,dy=p[1]-ccy;
          return [ccx+dx*cr-dy*sr,ccy+dx*sr+dy*cr];});
      }
      var _am=CG.floor+(1-CG.floor)*Math.min(1,e.k);
      /* P788: ONE call, ALL of it under the card (Denis), gaussian-
         blurred (hq) - the breathed line included. The card's pencil
         border reads as the object's silhouette against the light. */
      self._paintHalo(cv,x,sc,dpr,[hull],e.col||self.SEL_COL,e.col||self.SEL_SOFT,
        _am,undefined,{sx:1,sy:1,lineBlur:CG.lineBlur,hq:true});
    });
  },""",
    """  _drawCardGlows:function(){
    var sc0=document.getElementById('screen-match');
    var live=this._cardGlows&&Object.keys(this._cardGlows).length;
    var ly=document.getElementById('cardGlowLayer');
    if(!sc0||(!live&&!ly))return;
    /* the canvas generation is retired - clear strays from older DOM */
    ['dgCanvasHi','dgCanvasCore','dgCanvasLine'].forEach(function(id){
      var el=document.getElementById(id);if(el)el.remove();});
    ly=this._cardGlowLayer();if(!ly)return;
    var sc=sc0.getBoundingClientRect();
    if(sc.width<10)return;
    var self=this,CG=this.CARD_GLOW,seen={};
    Object.keys(this._cardGlows).forEach(function(kk){
      var e=self._cardGlows[kk];
      if(!e.el||!e.el.isConnected){delete self._cardGlows[kk];return;}
      var r=e.el.getBoundingClientRect();
      if(r.width<4)return;
      seen[kk]=1;
      var w=ly.querySelector('[data-k="'+kk+'"]');
      if(!w){
        w=document.createElement('div');
        w.className='cgw';w.dataset.k=kk;
        /* Denis's markup verbatim, minus .face - the REAL card is the
           face, up in its row */
        w.innerHTML='<div class="spill"></div>'
          +'<div class="glow"><div class="breathe">'
          +'<span class="bloom"><i></i></span>'
          +'<span class="halo"><i></i></span>'
          +'</div></div>';
        ly.appendChild(w);
      }
      /* the mask IS the card's own art */
      var img=e.el.querySelector('.fcvIn img')||e.el.querySelector('img');
      var src=img?(img.currentSrc||img.src):'';
      if(w._src!==src){w._src=src;w.style.setProperty('--card-src','url("'+src+'")');}
      /* geometry: the untransformed box at the element's screen centre,
         rotated to the fan (an AABB of a rotated card is inflated) */
      var cs2=getComputedStyle(e.el);
      var rot=parseFloat(cs2.rotate);if(isNaN(rot))rot=0;
      var scl=parseFloat(cs2.scale);if(!(scl>0))scl=1;
      /* computed width, not offsetWidth: the row sizes cards in cqw so
         the true width is fractional, and offsetWidth's truncation put
         the mask ~2px inside the art */
      var cw=(parseFloat(cs2.width)||e.el.offsetWidth)*scl,
          ch=(parseFloat(cs2.height)||e.el.offsetHeight)*scl;
      /* the row is a 3D stage (perspective + rotateX), so the PROJECTED
         card is ~2% bigger than its CSS size. Unrotated: the rect IS
         the projected box - exact. Fanned cards keep the computed size
         (their AABB is rotation-inflated); the <=2px keystone error
         hides under 5-17px of shadow. */
      if(!rot){cw=r.width;ch=r.height;}
      w.style.left=(r.left-sc.left+r.width/2-cw/2)+'px';
      w.style.top=(r.top-sc.top+r.height/2-ch/2)+'px';
      w.style.width=cw+'px';w.style.height=ch+'px';
      w.style.rotate=rot?(rot+'deg'):'0deg';
      /* the arm ramp maps onto his state axis: full arm = 'selected' */
      var _am=CG.floor+(1-CG.floor)*Math.min(1,e.k);
      w.style.setProperty('--state',(1+0.9*_am).toFixed(3));
      /* an accent (the rival's red telegraph) re-tints the whole thing */
      if(e.col){w.style.setProperty('--core',e.col);w.style.setProperty('--glow',e.col);}
      else{w.style.removeProperty('--core');w.style.removeProperty('--glow');}
    });
    [].forEach.call(ly.querySelectorAll('.cgw'),function(w){
      if(!seen[w.dataset.k])w.remove();
    });
    this._flickSync();
  },
  /* Denis's candle flicker: three incommensurate sines, never visibly
     loops. Runs only while something is lit; one style-var write per
     frame, no repaints. */
  _flickSync:function(){
    var self=this;
    if(this._flickRAF)return;
    if(!(this._cardGlows&&Object.keys(this._cardGlows).length))return;
    var t0=performance.now();
    var step=function(now){
      if(!(self._cardGlows&&Object.keys(self._cardGlows).length)){
        self._flickRAF=null;
        var ly=document.getElementById('cardGlowLayer');
        if(ly)ly.style.setProperty('--flick','1');
        return;
      }
      var ly=document.getElementById('cardGlowLayer');
      if(ly){
        if(document.body.classList.contains('reduced-motion')){
          ly.style.setProperty('--flick','1');
        }else{
          var t=(now-t0)/1000;
          var n=Math.sin(t*5.7)*.55+Math.sin(t*11.3+1.7)*.3+Math.sin(t*2.1)*.15;
          ly.style.setProperty('--flick',(1-.34*.2*(.5+.5*n)).toFixed(4));
        }
      }
      self._flickRAF=requestAnimationFrame(step);
    };
    this._flickRAF=requestAnimationFrame(step);
  },""",
    'the layer draw + flicker')

# ── 4. CARD_GLOW keeps only the ramp floor ──
sub("""  CARD_GLOW:{round:0.075, floor:0.42, trim:0.967, lineBlur:2},""",
    """  /* P789: the card glow is CSS (Denis's prototype) - every look dial
     is a var on #cardGlowLayer. Only the arm ramp's floor stays here. */
  CARD_GLOW:{floor:0.42},""",
    'CARD_GLOW is the floor only')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d (%s)' % (len(edits), ', '.join(edits)))
