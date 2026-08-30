# -*- coding: utf-8 -*-
u"""P883 (FX BRIEF step 5, the rest): _glow, _flash and _beam reach a match die.

All three build or animate DOM on the chip, and on a settled match die that
chip is under #d3xCanvas, so all three have been invisible there since the 3D
layer shipped:
  _glow  - a drop-shadow filter on an element with no opaque pixels. Nothing
           to cast a shadow from.
  _flash - appends a white div at z-index 8, under a canvas at 41.
  _beam  - appends a gradient column at z-index 4, likewise.
That is PAY's glow and beam, and STRIKE's flash: three of the nine instruments
playing as sound and spray with their light dropped.

They route by owner, exactly as _motion does since P881: a die D3X owns takes
the over-canvas, and everything else keeps the DOM path untouched.

TIMED MARKS, NOT DIRECT PAINTS, because the pass owns the surface - it clears
every frame, so a one-shot paint from outside would be erased by the next
frame. That constraint was written into P880's comment before there was
anything to test it, and this is the thing it was written for. A mark carries
its own t0 and duration; the pass paints it from its own clock and drops it
when it expires, which also means a beat cannot outlive its die: an entry whose
die has gone invisible is filtered out on the next pass rather than painting
over an empty seat.

The three painters:
  glow  - _paintHalo, the same painter as the keep glow and the card halo, with
          alpha on a sine so it swells and leaves. No new drawing code.
  flash - the hull filled flat, decaying linearly. Short by construction.
  beam  - a column rising from the die's own hull box, gradient to nothing,
          keeping the proportions the DOM version used (22% in, 56% wide) so
          it reads as the same effect it always was.

_traceHull is a small sibling of the tracer inside _paintHalo rather than a
refactor of it: _paintHalo's closure does shrink, lean and stretch for the halo
and the stamp path, and pulling it apart to share thirty lines would put the
selection glow at risk for no gain here.
"""
import io, os, sys, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'fark_proto.html')
s = io.open(P, encoding='utf-8', newline='').read()
edits = []


def sub(old, new, label):
    global s
    if s.count(old) == 1:
        s = s.replace(old, new); edits.append(label); return
    pat = re.escape(old).replace('\\\n', '\n').replace('\n', '\\r?\n')
    ms = list(re.finditer(pat, s))
    if len(ms) != 1:
        sys.exit('ANCHOR x%d for %s (nothing written)' % (len(ms), label))
    m = ms[0]
    rep = new.replace('\n', '\r\n') if '\r\n' in m.group(0) else new
    s = s[:m.start()] + rep + s[m.end():]
    edits.append(label)


# ── 1. the mark list, the tracer, and the way in ─────────────────────
sub(u"""  STATE_FORMS:[],""",
    u"""  STATE_FORMS:[],
  /* P883: TRANSIENT BEATS on the same surface. A state is a class that is
     either there or not; a beat has a clock. Both are painted by the pass
     because the pass clears the canvas every frame, so a one-shot paint from
     outside would live exactly one frame. An entry is
     {d, kind:'glow'|'flash'|'beam', ink, t0, ms}. */
  FX_MARKS:[],
  _fxMark:function(d,kind,ink,ms){
    if(!d||!d.obj)return false;
    (this.FX_MARKS||(this.FX_MARKS=[])).push(
      {d:d,kind:kind,ink:ink||'#ffffff',t0:performance.now(),ms:ms||500});
    return true;
  },
  /* the hull as a path. A small sibling of the tracer inside _paintHalo, not
     a refactor of it: that one also does shrink, lean, stretch and the stamp
     branch for the card halo, and taking it apart to share this much would
     put the selection glow at risk for nothing. */
  _traceHull:function(ctx,hull){
    if(!hull||!hull.length)return;
    ctx.beginPath();
    for(var i=0;i<hull.length;i++){
      if(i)ctx.lineTo(hull[i][0],hull[i][1]);
      else ctx.moveTo(hull[i][0],hull[i][1]);
    }
    ctx.closePath();
  },""",
    '1 the mark list and the tracer')

# ── 2. the pass wakes for beats too ──────────────────────────────────
sub(u"""  _drawStates:function(){
    this._statePasses=(this._statePasses||0)+1;
    var cv=document.getElementById('stCanvas'),i,d;
    var forms=this.STATE_FORMS||[],want=[];""",
    u"""  _drawStates:function(){
    this._statePasses=(this._statePasses||0)+1;
    var cv=document.getElementById('stCanvas'),i,d;
    /* P883: expire first, and drop any beat whose die has gone - a mark that
       outlived its die would paint over an empty seat. */
    var _now=performance.now();
    var beats=this.FX_MARKS=(this.FX_MARKS||[]).filter(function(mk){
      return mk.d&&mk.d.obj&&mk.d.obj.visible&&(_now-mk.t0)<mk.ms;
    });
    var forms=this.STATE_FORMS||[],want=[];""",
    '2 beats expire at the top of the pass')

sub(u"""    if(!want.length){
      if(cv&&this._stateInk){
        var c0=cv.getContext('2d');
        c0.setTransform(1,0,0,1,0,0);c0.clearRect(0,0,cv.width,cv.height);
        this._stateInk=false;
      }
      return;
    }""",
    u"""    if(!want.length&&!beats.length){
      if(cv&&this._stateInk){
        var c0=cv.getContext('2d');
        c0.setTransform(1,0,0,1,0,0);c0.clearRect(0,0,cv.width,cv.height);
        this._stateInk=false;
      }
      return;
    }""",
    '3 a beat alone keeps the pass awake')

# ── 3. paint the beats after the states ──────────────────────────────
sub(u"""    for(var k in byInk){
      var ink=k.split('|')[1];
      this._paintHalo(cv,x,sc,dpr,byInk[k],ink,ink,1);
    }
  },""",
    u"""    for(var k in byInk){
      var ink=k.split('|')[1];
      this._paintHalo(cv,x,sc,dpr,byInk[k],ink,ink,1);
    }
    /* P883: beats last, so a transient reads ON TOP of the state it belongs
       to rather than under it. */
    for(i=0;i<beats.length;i++){
      var mk=beats[i],hb=this._hullOf(mk.d,sc,G.grow);
      if(!hb)continue;
      var tt=(_now-mk.t0)/mk.ms;
      if(tt<0)tt=0;if(tt>1)tt=1;
      if(mk.kind==='glow'){
        /* the keep glow's own painter, alpha on a sine: it swells and leaves */
        this._paintHalo(cv,x,sc,dpr,[hb],mk.ink,mk.ink,Math.sin(tt*Math.PI));
      }else if(mk.kind==='flash'){
        x.save();
        x.globalAlpha=Math.max(0,1-tt)*0.8;
        x.fillStyle=mk.ink;
        this._traceHull(x,hb);
        x.fill();
        x.restore();
      }else if(mk.kind==='beam'){
        /* a column out of the die's own box, in the proportions the DOM
           version used, so it reads as the effect it has always been */
        var bx0=1e9,bx1=-1e9,by0=1e9,by1=-1e9;
        for(var bi=0;bi<hb.length;bi++){
          if(hb[bi][0]<bx0)bx0=hb[bi][0];
          if(hb[bi][0]>bx1)bx1=hb[bi][0];
          if(hb[bi][1]<by0)by0=hb[bi][1];
          if(hb[bi][1]>by1)by1=hb[bi][1];
        }
        var bw=bx1-bx0,bh=by1-by0;
        var cx2=bx0+bw*0.22,cw=bw*0.56;
        var top=by0+bh*0.48-bh*2,bot=by0+bh*0.48;
        var gr=x.createLinearGradient(0,bot,0,top);
        gr.addColorStop(0,mk.ink);
        gr.addColorStop(1,'rgba(0,0,0,0)');
        x.save();
        /* screen, like the DOM gradient's blend - a beam adds light */
        x.globalCompositeOperation='lighter';
        x.globalAlpha=Math.sin(tt*Math.PI)*0.55;
        x.fillStyle=gr;
        x.fillRect(cx2,top,cw,bot-top);
        x.restore();
      }
    }
  },""",
    '4 the three beat painters')

# ── 4. FKFX routes each primitive by owner ───────────────────────────
sub(u"""  _glow:function(el,col,size,ms){
    if(!el||!el.animate)return;""",
    u"""  _glow:function(el,col,size,ms){
    /* P883: a drop-shadow on an element with no opaque pixels casts nothing,
       and a match die's chip has none - the die is drawn on the canvas above
       it. Owned dice take the over-canvas, where the shape is real. */
    var _d=(window.D3X&&D3X.dice&&D3X._byChip)?D3X._byChip(el):null;
    if(_d&&_d.phys&&_d.obj&&_d.obj.visible){D3X._fxMark(_d,'glow',col,ms||500);return;}
    if(!el||!el.animate)return;""",
    '5 _glow routes by owner')

sub(u"""  _flash:function(el){
    if(!el)return;""",
    u"""  _flash:function(el){
    /* P883: this appends a white div at z-index 8, and on the match screen the
       dice canvas is 41. Owned dice get the hull filled on the over-canvas. */
    var _d=(window.D3X&&D3X.dice&&D3X._byChip)?D3X._byChip(el):null;
    if(_d&&_d.phys&&_d.obj&&_d.obj.visible){D3X._fxMark(_d,'flash','#ffffff',150);return;}
    if(!el)return;""",
    '6 _flash routes by owner')

sub(u"""  _beam:function(el,col,ms){
    if(!el)return;""",
    u"""  _beam:function(el,col,ms){
    /* P883: z-index 4, under the dice canvas at 41 - same story as _flash. */
    var _d=(window.D3X&&D3X.dice&&D3X._byChip)?D3X._byChip(el):null;
    if(_d&&_d.phys&&_d.obj&&_d.obj.visible){D3X._fxMark(_d,'beam',col,ms||600);return;}
    if(!el)return;""",
    '7 _beam routes by owner')

# ── post-asserts ─────────────────────────────────────────────────────
if s.count("_fxMark(_d,'glow'") != 1 or s.count("_fxMark(_d,'flash'") != 1 \
        or s.count("_fxMark(_d,'beam'") != 1:
    sys.exit('the three primitives do not each route exactly once (nothing written)')
_a = s.index('_drawStates:function(){')
_b = s.index('_hullOf:function(d,sc,grow){', _a)
body = s[_a:_b]
for need in ("mk.kind==='glow'", "mk.kind==='flash'", "mk.kind==='beam'"):
    if need not in body:
        sys.exit('%s is not painted (nothing written)' % need)
if '!want.length&&!beats.length' not in body:
    sys.exit('a beat alone does not keep the pass awake (nothing written)')
if '_now-mk.t0)<mk.ms' not in body:
    sys.exit('beats never expire (nothing written)')
# the guards P880 refused must still be absent
if '_rolling()' in body:
    sys.exit('the state pass gained the _rolling skip (nothing written)')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d edits (%s)' % (len(edits), ', '.join(edits)))
