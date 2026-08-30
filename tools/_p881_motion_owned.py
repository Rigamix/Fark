# -*- coding: utf-8 -*-
u"""P881 (FX BRIEF step 5, the motion half): _motion stops fighting D3X for the
chip, and starts moving the thing the player can actually see.

WHAT _motion DOES TO A SETTLED MATCH DIE TODAY. It animates `translate`,
`scale`, `rotate` and `opacity` on d.chip. For a match die that chip is under
#d3xCanvas and paints nothing, so every one of those is invisible - and two of
them are not harmless:

  - `translate` is the property _slaveHost writes inline EVERY FRAME (26317),
    and its own comment says it chose translate precisely because a running
    animation outranks inline style. _motion is a running animation on that
    property, so for the length of the effect the inline write loses and the
    chip - the hit box - snaps back to its flex slot while the die stays where
    physics left it. STRIKE shakes the hit box off the die for 240ms.
    _slaveHost is called from the `if(d.phys)` settled branch (29620), which is
    exactly the die STRIKE fires on, so this is not a shop-only path.
  - `opacity` is read by D3X as a VISIBILITY SIGNAL: 29629 hides any die whose
    computed chip opacity is <= .02. An instrument that fades through zero
    removes the die from the board. NO INSTRUMENT AUTHORS `op` TODAY - this is
    a trap for the next author, not a bug that is firing - which is why it gets
    a clamp rather than a rewrite.

SO THE FIX IS NOT TO PICK A SAFER PROPERTY. There is nothing to win on the
chip: it is invisible. The motion belongs to the mesh, and D3X already has the
mechanism - `d.kick` (29594) displaces a settled die over time from inside the
settled branch, in table units, marking shadows dirty as it goes. `nudge` is
its sibling for an oscillation rather than a one-way push, and it composes with
kick by adding to the position kick already set.

WHAT IS AND IS NOT CARRIED OVER:
  dx/dy -> a damped shake on the mesh, amplitude in die-widths so an
           instrument written in px keeps its intent at any table size.
  sc    -> the mesh's scale, which is the squash SET was written to have and
           has never once been seen.
  rt    -> DROPPED, and deliberately: D3X owns the quaternion, and a settled
           die's rotation IS its face. Spinning it would show a different
           number. This is the one that stays unreachable, so it is documented
           at the instrument rather than left to be rediscovered.
  op    -> clamped on the DOM path that remains, for a chip _byChip misses.

The DOM path is untouched for everything that is not a D3X-owned die - cards,
shop rows, the loadout - where the chip is the visible thing and translate is
nobody else's property.
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


# ── 1. the lookup and the mechanism, beside _slaveHost ───────────────
sub(u"""  /* one-line health check for a browser that is showing the wrong dice */
  diag:function(){""",
    u"""  /* P881: which die is this chip? FKFX is handed a DOM element and has to
     know whether D3X owns it, because what is safe to animate depends
     entirely on that. Linear over at most a couple of dozen dice, and only
     on an effect, never per frame. */
  _byChip:function(el){
    if(!el)return null;
    for(var i=0;i<this.dice.length;i++)if(this.dice[i].chip===el)return this.dice[i];
    return null;
  },
  /* P881: NUDGE - kick's sibling. kick (29594) is a one-way displacement with
     a spin; nudge is a damped oscillation with none, because a settled die's
     rotation is the number it is showing. Amplitude arrives in px, from an
     instrument that was written against a DOM chip, and is stored in
     DIE-WIDTHS so the same instrument reads the same at any table size.
     Applied from inside the settled branch, on top of whatever kick did. */
  NUDGE:{ms:260,osc:6},
  nudge:function(d,dxMax,scMax){
    if(!d)return;
    d.nudge={t0:performance.now(),
             amp:(dxMax||0)/((d.w0||60)),
             sc:(scMax===undefined?0:scMax)};
    this._shDirty=true;
  },
  /* one-line health check for a browser that is showing the wrong dice */
  diag:function(){""",
    '1 _byChip and nudge')

# ── 2. applied per frame, beside kick ────────────────────────────────
sub(u"""            d.obj.quaternion.premultiply(_kq2);
            if(_kt2<1)D3X._shDirty=true;
          }
          /* P702: scoring face bright, sides in shadow - derived from""",
    u"""            d.obj.quaternion.premultiply(_kq2);
            if(_kt2<1)D3X._shDirty=true;
          }
          /* P881: the nudge rides on top of the kick, same as the kick rides
             on the frozen pose. Damped sine so it returns to exactly where it
             started - an effect must not leave a settled die displaced, since
             the position is what the hit box and the shadow are read from. */
          if(d.nudge){
            var _nt=(performance.now()-d.nudge.t0)/(D3X.NUDGE.ms||260);
            if(_nt>=1){d.nudge=null;D3X._shDirty=true;}
            else{
              var _nd=1-_nt;
              if(d.nudge.amp)d.obj.position.x+=d.nudge.amp*_nd*
                Math.sin(_nt*Math.PI*(D3X.NUDGE.osc||6));
              if(d.nudge.sc)d.obj.scale.setScalar(1+d.nudge.sc*_nd*
                Math.sin(_nt*Math.PI));
              D3X._shDirty=true;
            }
          }
          /* P702: scoring face bright, sides in shadow - derived from""",
    '2 the nudge applied in the settled branch')

# ── 3. _motion routes by owner ───────────────────────────────────────
sub(u"""  /* motion: standalone props, so the row's own transforms survive */
  _motion:function(el,keys){
    if(!el||!el.animate||!keys||!keys.length)return;
    try{
      el.animate(keys.map(function(k){
        return {offset:k.o,translate:(k.dx||0)+'px '+(k.dy||0)+'px',
          scale:String(k.sc===undefined?1:k.sc),rotate:(k.rt||0)+'deg',
          opacity:k.op===undefined?1:k.op,easing:k.e||'ease-out'};
      }),{duration:keys[keys.length-1].t||500});
    }catch(e){}
  },""",
    u"""  /* motion: standalone props, so the row's own transforms survive.
     P881: WHO OWNS THE ELEMENT DECIDES WHAT MAY BE ANIMATED. On a settled
     match die the chip is under #d3xCanvas and shows nothing, so the DOM
     animation below is invisible - while `translate` is the property
     _slaveHost writes inline every frame (and a running animation outranks
     inline style, which is the whole reason it picked translate), and
     `opacity` is read by D3X at 29629 as "hide this die". Invisible, and two
     ways harmful. So a D3X-owned die takes the mesh instead: dx/dy become a
     damped shake and `sc` becomes the squash SET has always described and
     never shown. `rt` is dropped on purpose - D3X owns the quaternion and a
     settled die's rotation IS the face it is showing, so spinning it would
     change the number. */
  _motion:function(el,keys){
    if(!el||!keys||!keys.length)return;
    try{
      var d=(window.D3X&&D3X.dice&&D3X._byChip)?D3X._byChip(el):null;
      if(d&&d.phys&&d.obj&&d.obj.visible){
        var mx=0,ms=0,i,k;
        for(i=0;i<keys.length;i++){
          k=keys[i];
          if(k.dx&&Math.abs(k.dx)>Math.abs(mx))mx=k.dx;
          if(k.dy&&Math.abs(k.dy)>Math.abs(mx))mx=k.dy;
          if(k.sc!==undefined&&Math.abs(k.sc-1)>Math.abs(ms))ms=k.sc-1;
        }
        if(mx||ms)D3X.nudge(d,mx,ms);
        return;
      }
      if(!el.animate)return;
      el.animate(keys.map(function(k){
        /* P881: the clamp is for a chip _byChip missed. D3X hides a die whose
           computed opacity is <= .02, so an instrument that fades through
           zero would delete it. No instrument authors `op` today; this keeps
           it that way by construction rather than by nobody having tried. */
        var op=k.op===undefined?1:Math.max(k.op,0.05);
        return {offset:k.o,translate:(k.dx||0)+'px '+(k.dy||0)+'px',
          scale:String(k.sc===undefined?1:k.sc),rotate:(k.rt||0)+'deg',
          opacity:op,easing:k.e||'ease-out'};
      }),{duration:keys[keys.length-1].t||500});
    }catch(e){}
  },""",
    '3 _motion routes by owner')

# ── post-asserts ─────────────────────────────────────────────────────
_a = s.index('_motion:function(el,keys){')
_b = s.index('/* THE FAMILIES.', _a)
body = s[_a:_b]
if 'D3X.nudge(d,mx,ms)' not in body:
    sys.exit('the owned path does not reach nudge (nothing written)')
if 'Math.max(k.op,0.05)' not in body:
    sys.exit('the opacity clamp is missing (nothing written)')
if s.count('_byChip:function(el){') != 1 or s.count('nudge:function(d,dxMax,scMax){') != 1:
    sys.exit('the new D3X members are not defined exactly once (nothing written)')
if s.count('if(d.nudge){') != 1:
    sys.exit('the nudge is not applied exactly once (nothing written)')
# it must sit in the settled branch, after the kick it composes with
if s.index('if(d.nudge){') < s.index('if(d.kick){'):
    sys.exit('the nudge is applied before the kick it rides on (nothing written)')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d edits (%s)' % (len(edits), ', '.join(edits)))
