# -*- coding: utf-8 -*-
"""P793: the ink ring - the card's painted rim catches the core's light.

Denis: "you STILL have a darkish outline between the card png and the
glow. Check the layers you have?" The layer check, in paint order:
table -> dice canvas (z3) -> #cardGlowLayer (z41: spill, bloom, halo,
ALL under) -> rows (z42: the card img, whose outermost ~1px is painted
BLACK PENCIL INK - measured at (18,10,4) opaque in the webp, P782) ->
dragged card (9500). The constant across every build: no light exists
ABOVE the ink. Under-light stops dead beneath the card, so its own
painted rim reads as a dark outline against the glow beside it.

The fix keeps his prototype's grammar: a RING layer above the cards
(#cardGlowRim, z9600) holding, per lit card, the card mask MINUS a
slightly-inset copy of itself (mask-composite: subtract; the standard
property, with the -webkit- legacy spelling beside it) - a ~1.5px
silhouette ring, filled var(--core), blurred through his own
filter-on-parent / mask-on-child pattern, plus-lighter. Additive over
black ink = the core colour exactly where the ink is: the outline is
LIT, not covered, and no other pixel of the art is touched. This is
NOT the over-card wash he rejected - it is a hairline, the width of
the ink itself.

Geometry rides the same loop as the under-wrappers (same box, same
--cgs/--state/accent); the flicker var feeds both layers.
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


# ── 1. the ring's CSS ──
sub("""@keyframes cgBreathe{0%,100%{opacity:.88}50%{opacity:1}}""",
    """/* P793: THE INK RING - the card's painted black rim (the webp's own
   outermost ~1px of pencil ink) can never be brightened by the under-
   layer, so it gets its OWN light: the card mask minus an inset copy
   of itself = a hairline silhouette ring, core-coloured, blurred via
   the filter-on-parent/mask-on-child pattern, plus-lighter above the
   card. Additive over black ink = lit ink. Nothing else is covered. */
#cardGlowRim{position:absolute;inset:0;pointer-events:none;z-index:9600;
  mix-blend-mode:var(--blend,plus-lighter);
  --core:hsl(13 100% 63%);--core-b:1.83;--intensity:1;--flick:1}
#cardGlowRim .cgr{position:absolute}
.cgr .rim{position:absolute;inset:0;
  opacity:calc(min(1,var(--core-b)*var(--intensity)*var(--state,1))*var(--flick,1));
  filter:blur(calc(1.2px*var(--cgs,1))) brightness(max(1,calc(var(--core-b)*var(--intensity)*var(--state,1))))}
.cgr .rim>i{position:absolute;inset:0;background:var(--core);
  mask-image:var(--card-src),var(--card-src);
  -webkit-mask-image:var(--card-src),var(--card-src);
  mask-repeat:no-repeat;-webkit-mask-repeat:no-repeat;
  mask-position:center,center;-webkit-mask-position:center,center;
  mask-size:100% 100%,calc(100% - var(--inkw,3px)) calc(100% - var(--inkh,3px));
  -webkit-mask-size:100% 100%,calc(100% - var(--inkw,3px)) calc(100% - var(--inkh,3px));
  mask-composite:subtract;
  -webkit-mask-composite:source-out}
@keyframes cgBreathe{0%,100%{opacity:.88}50%{opacity:1}}""",
    "the ring's CSS")

# ── 2. the rim layer builder ──
sub("""  _cardGlowLayer:function(){
    var sc=document.getElementById('screen-match');
    if(!sc)return null;
    var ly=document.getElementById('cardGlowLayer');
    if(!ly){
      ly=document.createElement('div');ly.id='cardGlowLayer';
      sc.appendChild(ly);
    }
    return ly;
  },""",
    """  _cardGlowLayer:function(){
    var sc=document.getElementById('screen-match');
    if(!sc)return null;
    var ly=document.getElementById('cardGlowLayer');
    if(!ly){
      ly=document.createElement('div');ly.id='cardGlowLayer';
      sc.appendChild(ly);
    }
    return ly;
  },
  /* P793: the ink ring's layer - ABOVE the rows (and the dragged card),
     because the card's painted rim can only be lit from above. */
  _cardGlowRimLayer:function(){
    var sc=document.getElementById('screen-match');
    if(!sc)return null;
    var ly=document.getElementById('cardGlowRim');
    if(!ly){
      ly=document.createElement('div');ly.id='cardGlowRim';
      sc.appendChild(ly);
    }
    return ly;
  },""",
    'the rim layer builder')

# ── 3. the draw loop feeds both layers ──
sub("""    ly=this._cardGlowLayer();if(!ly)return;
    var sc=sc0.getBoundingClientRect();
    if(sc.width<10)return;
    var self=this,CG=this.CARD_GLOW,seen={};""",
    """    ly=this._cardGlowLayer();if(!ly)return;
    var lyR=this._cardGlowRimLayer();
    var sc=sc0.getBoundingClientRect();
    if(sc.width<10)return;
    var self=this,CG=this.CARD_GLOW,seen={};""",
    'both layers prepared')

sub("""      /* the arm ramp maps onto his state axis: full arm = 'selected' */
      var _am=CG.floor+(1-CG.floor)*Math.min(1,e.k);
      w.style.setProperty('--state',(1+0.9*_am).toFixed(3));
      /* an accent (the rival's red telegraph) re-tints the whole thing */
      if(e.col){w.style.setProperty('--core',e.col);w.style.setProperty('--glow',e.col);}
      else{w.style.removeProperty('--core');w.style.removeProperty('--glow');}
    });
    [].forEach.call(ly.querySelectorAll('.cgw'),function(w){
      if(!seen[w.dataset.k])w.remove();
    });""",
    """      /* the arm ramp maps onto his state axis: full arm = 'selected' */
      var _am=CG.floor+(1-CG.floor)*Math.min(1,e.k);
      w.style.setProperty('--state',(1+0.9*_am).toFixed(3));
      /* an accent (the rival's red telegraph) re-tints the whole thing */
      if(e.col){w.style.setProperty('--core',e.col);w.style.setProperty('--glow',e.col);}
      else{w.style.removeProperty('--core');w.style.removeProperty('--glow');}
      /* P793: the ink ring above the card - same box, same state; the
         ring's inset tracks the webp's ~5-natural-px ink plus its AA
         (7/456 of the width per side, both axes as px of this box). */
      if(lyR){
        var w2=lyR.querySelector('[data-k="'+kk+'"]');
        if(!w2){
          w2=document.createElement('div');
          w2.className='cgr';w2.dataset.k=kk;
          w2.innerHTML='<span class="rim"><i></i></span>';
          lyR.appendChild(w2);
        }
        if(w2._src!==src){w2._src=src;w2.style.setProperty('--card-src','url("'+src+'")');}
        /* the ring sits at the FULL projected size - the under-glow's
           0.99 inset half-missed the ink (measured: a 2px unlit notch
           at the very edge). The ring's job IS the edge. */
        /* x1.02: the ring's outer edge clears the visible edge by ~0.5px
           everywhere - overflow lands on the glow where plus-lighter makes
           core-on-glow invisible; undershoot leaves ink dark (measured x2) */
        var ch2=ch*1.02,cw2=ch2*_nat;
        w2.style.left=(r.left-sc.left+r.width/2-cw2/2)+'px';
        w2.style.top=(r.top-sc.top+r.height/2-ch2/2)+'px';
        w2.style.width=cw2+'px';w2.style.height=ch2+'px';
        w2.style.rotate=w.style.rotate;
        w2.style.setProperty('--cgs',(cw/200).toFixed(4));
        w2.style.setProperty('--inkw',(cw2*2*10/456).toFixed(2)+'px');
        w2.style.setProperty('--inkh',(ch2*2*10/650).toFixed(2)+'px');
        w2.style.setProperty('--state',(1+0.9*_am).toFixed(3));
        if(e.col)w2.style.setProperty('--core',e.col);
        else w2.style.removeProperty('--core');
      }
    });
    [].forEach.call(ly.querySelectorAll('.cgw'),function(w){
      if(!seen[w.dataset.k])w.remove();
    });
    if(lyR)[].forEach.call(lyR.querySelectorAll('.cgr'),function(w){
      if(!seen[w.dataset.k])w.remove();
    });""",
    'the ring rides the loop')

# ── 4. the flicker feeds both layers ──
sub("""      var ly=document.getElementById('cardGlowLayer');
      if(ly){
        if(document.body.classList.contains('reduced-motion')){
          ly.style.setProperty('--flick','1');
        }else{
          var t=(now-t0)/1000;
          var n=Math.sin(t*5.7)*.55+Math.sin(t*11.3+1.7)*.3+Math.sin(t*2.1)*.15;
          ly.style.setProperty('--flick',(1-.34*.2*(.5+.5*n)).toFixed(4));
        }
      }""",
    """      var _lys=[document.getElementById('cardGlowLayer'),
        document.getElementById('cardGlowRim')];
      var _fv='1';
      if(!document.body.classList.contains('reduced-motion')){
        var t=(now-t0)/1000;
        var n=Math.sin(t*5.7)*.55+Math.sin(t*11.3+1.7)*.3+Math.sin(t*2.1)*.15;
        _fv=(1-.34*.2*(.5+.5*n)).toFixed(4);
      }
      _lys.forEach(function(l){if(l)l.style.setProperty('--flick',_fv);});""",
    'the flicker feeds both')

sub("""        self._flickRAF=null;
        var ly=document.getElementById('cardGlowLayer');
        if(ly)ly.style.setProperty('--flick','1');
        return;""",
    """        self._flickRAF=null;
        [document.getElementById('cardGlowLayer'),
         document.getElementById('cardGlowRim')].forEach(function(l){
          if(l)l.style.setProperty('--flick','1');});
        return;""",
    'the flicker rests both')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d (%s)' % (len(edits), ', '.join(edits)))
