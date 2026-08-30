# -*- coding: utf-8 -*-
u"""P885: the owned motion path plays the AUTHORED KEYFRAMES, not a summary of them.

P881 routed a D3X-owned die's motion to the mesh, which was right, but it did
it by reducing a whole keyframe list to three numbers - the largest-magnitude
dx, the largest |sc-1| and the largest |rt| - and replaying each as one damped
sine. That reduction is where the remaining damage was.

THE REGRESSION IT CAUSED, and this one is live and mine. TRANSFORM authors

    [{o:0},{o:.5,rt:180,sc:1.08},{o:1,rt:360,sc:1,t:620,e:'cubic-bezier(.3,1.4,.4,1)'}]

which is ONE monotonic turn over 620ms. The reduction takes max|rt| = 360 and
plays rt*(1-t)*sin(t*PI*osc) with osc=6 over NUDGE.ms=260 - three full plus-
and-minus swings of up to a whole turn, in under a third of the authored time.
Measured on a real settled die, the angular deviation ran
0, 89, 44, 125, 138, 91, 176, 36, 178, 165, 70 degrees. `ench:trade` and
`ench:quicksilver` both resolve to TRANSFORM and both reach a die through the
live call site, so P882 shipped a dignified spin as a whirl.

WHAT ELSE THE REDUCTION DROPPED, all measured:
  - DURATION. Every owned effect ran at the global 260ms. SET authors 500,
    ARM 600, TRANSFORM 620, STRIKE 240, moment 2 200. Nothing said so.
  - SHAPE. ARM's two bumps (1.08, back to 1, 1.05, back to 1) became one.
  - EASING. Five authored `e:` values, including SET's overshooting
    cubic-bezier(.3,1.4,.4,1), were ignored on this path.
  - DEPTH. The (1-t)*sin(PI*t) envelope peaks near 0.5, so an authored 7%
    squash arrived as about 4%.
  - AXIS. `dy` was folded into the same scalar as `dx` and applied to
    position.x, so a vertical shake would have come out horizontal. No
    instrument authors dy today; this was a trap for the next one, of exactly
    the kind P881 clamped `op` against.

So `sc` was never the whole story. MEASURED, `sc` DOES reach the framebuffer
today - a SET keep dips the mesh to 0.960 at the shipped timing and costs 4.2%
of the die's lit pixels - so the brief's "silent no-op" does not hold. What was
true is that no probe had ever sampled d.obj.scale, so the claim was unverified
either way, and that the authored VALUE did not survive the trip.

Playing the keys directly fixes all six at once and deletes more than it adds:
NUDGE.osc has no readers left, and the whole reduction loop goes.

THE SCALE COLLISION, which is the other half. d.obj.scale had two writers in a
frame: the nudge at its old position, and then _pulsePose - which runs AFTER
it and calls setScalar unconditionally, so the pulse won. Measured: a nudge of
sc=0.5 with the pulse on peaks at 1.0574, exactly the pulse's own amplitude,
with the nudge armed throughout. That is not a corner case: _markLoneCast turns
the pulse on for _dieIsIcon dice and moment 2 fires for _dieIsIcon dice - the
same set - so moment 2's swell was erased on precisely the dice it exists for.
Fixed by giving scale ONE resolution point: the pose functions set the base,
and the nudge MULTIPLIES afterwards, so pulse and beat compose instead of
racing. Same shape as P881's fix for translate, one layer down.

NOTHING IS LEFT DISPLACED. The settled branch re-bases position, scale and
quaternion from d.phys every frame before any of this runs, so when the nudge
expires the die returns exactly to its settled pose whether or not the last
authored key came back to rest.
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


# ── 1. _motion hands the keys over whole ────────────────────────────
sub(u"""      var d=(window.D3X&&D3X.dice&&D3X._byChip)?D3X._byChip(el):null;
      if(d&&d.phys&&d.obj&&d.obj.visible){
        var mx=0,ms=0,mr=0,i,k;
        for(i=0;i<keys.length;i++){
          k=keys[i];
          if(k.dx&&Math.abs(k.dx)>Math.abs(mx))mx=k.dx;
          if(k.dy&&Math.abs(k.dy)>Math.abs(mx))mx=k.dy;
          if(k.sc!==undefined&&Math.abs(k.sc-1)>Math.abs(ms))ms=k.sc-1;
          if(k.rt&&Math.abs(k.rt)>Math.abs(mr))mr=k.rt;
        }
        if(mx||ms||mr)D3X.nudge(d,mx,ms,mr);
        return;
      }""",
    u"""      var d=(window.D3X&&D3X.dice&&D3X._byChip)?D3X._byChip(el):null;
      if(d&&d.phys&&d.obj&&d.obj.visible){
        /* P885: THE KEYS GO OVER WHOLE. This used to reduce the list to the
           largest dx, the largest |sc-1| and the largest |rt| and replay each
           as one damped sine, which lost the duration, the easing, the shape
           and the axis - and turned TRANSFORM's single 360 degree turn into
           three plus-and-minus swings of up to a whole turn in 260ms, on two
           live enchants. A keyframe list is a shape, so hand over the shape. */
        D3X.nudge(d,keys);
        return;
      }""",
    '1 _motion hands over the keys')

# ── 2. nudge stores the keys and the authored duration ──────────────
sub(u"""  NUDGE:{ms:260,osc:6},
  nudge:function(d,dxMax,scMax,rtMax){
    if(!d)return;
    d.nudge={t0:performance.now(),
             amp:(dxMax||0)/((d.w0||60)),
             sc:(scMax===undefined?0:scMax),
             /* P882: degrees in, radians stored - the instruments are written
                in degrees and the quaternion wants radians, so the conversion
                belongs here rather than in the frame loop. */
             rt:(rtMax?rtMax*Math.PI/180:0)};
    this._shDirty=true;
  },""",
    u"""  /* P885: `osc` is gone with the reduction that was its only reader. `ms` is
     now only the fallback for a key list whose last key sets no duration. */
  NUDGE:{ms:260},
  /* CSS's named easings as their bezier control points, so an instrument
     written for the DOM path reads the same on the mesh. */
  _EASE:{'linear':[0,0,1,1],'ease':[.25,.1,.25,1],'ease-in':[.42,0,1,1],
         'ease-out':[0,0,.58,1],'ease-in-out':[.42,0,.58,1]},
  /* y at x=t on a cubic bezier, by bisection on x. 18 halvings is finer than
     a pixel over any duration these effects use, and it needs no derivative,
     so an overshooting curve like cubic-bezier(.3,1.4,.4,1) - which SET and
     TRANSFORM both end on - is handled without special-casing. */
  _ease:function(spec,t){
    var e=this._EASE[spec];
    if(!e){
      var m=/cubic-bezier\\(([^)]*)\\)/.exec(spec||'');
      e=m?m[1].split(',').map(Number):this._EASE['ease-out'];
    }
    if(!e||e.length!==4||e.some(isNaN))return t;
    if(t<=0)return 0;
    if(t>=1)return 1;
    var lo=0,hi=1,u=t,mu,x;
    for(var i=0;i<18;i++){
      u=(lo+hi)/2;mu=1-u;
      x=3*mu*mu*u*e[0]+3*mu*u*u*e[2]+u*u*u;
      if(x<t)lo=u;else hi=u;
    }
    mu=1-u;
    return 3*mu*mu*u*e[1]+3*mu*u*u*e[3]+u*u*u;
  },
  /* the authored value of every property at time t (0..1), interpolated
     between the bracketing keys with the START key's easing - which is what
     `easing` means on a keyframe, in the DOM path this mirrors. */
  _nudgeAt:function(N,t){
    var K=N.keys,n=K.length,i,a,b,o0,o1,u,e;
    var off=function(j){return K[j].o===undefined?(n<2?1:j/(n-1)):K[j].o;};
    var val=function(k,p){return p==='sc'?(k.sc===undefined?1:k.sc):(k[p]||0);};
    a=K[n-1];
    for(i=0;i<n-1;i++){
      o0=off(i);o1=off(i+1);
      if(t>=o0&&t<=o1){
        a=K[i];b=K[i+1];
        u=(o1>o0)?(t-o0)/(o1-o0):1;
        e=this._ease(a.e||'ease-out',u);
        return {dx:val(a,'dx')+(val(b,'dx')-val(a,'dx'))*e,
                dy:val(a,'dy')+(val(b,'dy')-val(a,'dy'))*e,
                sc:val(a,'sc')+(val(b,'sc')-val(a,'sc'))*e,
                rt:val(a,'rt')+(val(b,'rt')-val(a,'rt'))*e};
      }
    }
    return {dx:val(a,'dx'),dy:val(a,'dy'),sc:val(a,'sc'),rt:val(a,'rt')};
  },
  nudge:function(d,keys){
    if(!d||!keys||!keys.length)return;
    var last=keys[keys.length-1];
    /* the instrument's OWN duration. SET 500 (no t, so the DOM path's
       default), ARM 600, TRANSFORM 620, STRIKE 240, moment 2 200 - all of
       which used to collapse to one global number. */
    d.nudge={t0:performance.now(),ms:(last&&last.t)||500,
             keys:keys,w:(d.w0||60),sc:1};
    this._shDirty=true;
  },""",
    '2 nudge stores keys, duration and easing')

# ── 3. the frame: position and yaw here, scale deferred ─────────────
sub(u"""          if(d.nudge){
            var _nt=(performance.now()-d.nudge.t0)/(D3X.NUDGE.ms||260);
            if(_nt>=1){d.nudge=null;D3X._shDirty=true;}
            else{
              var _nd=1-_nt;
              if(d.nudge.amp)d.obj.position.x+=d.nudge.amp*_nd*
                Math.sin(_nt*Math.PI*(D3X.NUDGE.osc||6));
              if(d.nudge.sc)d.obj.scale.setScalar(1+d.nudge.sc*_nd*
                Math.sin(_nt*Math.PI));
              /* P882: the yaw is PREmultiplied about WORLD UP, which is P821's
                 finding six lines above: a spin applied in the die's local
                 frame rolls faces 1/3/4/6 off their number, because only 2 and
                 5 have their normal on mesh Y. In the world frame about up,
                 the scoring face stays up and only the twist shows. */
              if(d.nudge.rt){
                var _nq=(D3X._nq||(D3X._nq=new THREE.Quaternion()));
                _nq.setFromAxisAngle(D3X._kup||(D3X._kup=new THREE.Vector3(0,1,0)),
                  d.nudge.rt*_nd*Math.sin(_nt*Math.PI*(D3X.NUDGE.osc||6)));
                d.obj.quaternion.premultiply(_nq);
              }
              D3X._shDirty=true;
            }
          }""",
    u"""          var _nsc=1;
          if(d.nudge){
            var _nt=(performance.now()-d.nudge.t0)/(d.nudge.ms||D3X.NUDGE.ms||260);
            if(_nt>=1){d.nudge=null;D3X._shDirty=true;}
            else{
              var _nv=D3X._nudgeAt(d.nudge,_nt);
              /* px in, die-widths out, so an instrument written against a DOM
                 chip reads the same at any table size. */
              if(_nv.dx)d.obj.position.x+=_nv.dx/d.nudge.w;
              /* P885: dy is its OWN axis now, and negated - the instruments
                 are written in screen coordinates where down is positive, and
                 table y is up. It used to be folded into the x scalar, so a
                 vertical shake came out horizontal. Nothing authors dy today;
                 this is for whoever writes the first one. */
              if(_nv.dy)d.obj.position.y-=_nv.dy/d.nudge.w;
              /* P882: the yaw is PREmultiplied about WORLD UP, which is P821's
                 finding just above: a spin applied in the die's local frame
                 rolls faces 1/3/4/6 off their number, because only 2 and 5
                 have their normal on mesh Y. In the world frame about up, the
                 scoring face stays up and only the twist shows.
                 P885: the angle is now the AUTHORED one at this instant, an
                 absolute offset from the settled pose rather than an amplitude
                 through an oscillator - so TRANSFORM's 0/180/360 is one turn
                 that ends where it started. */
              if(_nv.rt){
                var _nq=(D3X._nq||(D3X._nq=new THREE.Quaternion()));
                _nq.setFromAxisAngle(D3X._kup||(D3X._kup=new THREE.Vector3(0,1,0)),
                  _nv.rt*Math.PI/180);
                d.obj.quaternion.premultiply(_nq);
              }
              /* scale is NOT applied here - see the note at the pose block */
              _nsc=_nv.sc;
              D3X._shDirty=true;
            }
          }""",
    '3 the frame plays the keys')

# ── 4. scale gets one resolution point, after the poses ─────────────
sub(u"""          if(d.burst)D3X._burstPose(d);
          else if(d.pulseOn)D3X._pulsePose(d);
          if(e)e._d3xOwned=true;""",
    u"""          if(d.burst)D3X._burstPose(d);
          else if(d.pulseOn)D3X._pulsePose(d);
          /* P885: SCALE RESOLVES ONCE, HERE, AND THE NUDGE MULTIPLIES. It used
             to setScalar up in the nudge block, and _pulsePose - which runs
             here, after it, and setScalars unconditionally - simply won.
             Measured: a nudge of sc=0.5 with the pulse on peaked at 1.0574,
             the pulse's own amplitude, with the nudge armed the whole time.
             The overlap is not incidental: _markLoneCast turns the pulse on
             for _dieIsIcon dice and moment 2 fires for _dieIsIcon dice, so the
             beat's swell was erased on exactly the dice it exists for. Poses
             set the base, the beat scales it, and the two compose instead of
             racing - the same fix P881 made for translate, one layer down. */
          if(_nsc!==1)d.obj.scale.multiplyScalar(_nsc);
          if(e)e._d3xOwned=true;""",
    '4 scale resolves once, after the poses')

# ── post-asserts ────────────────────────────────────────────────────
_m = s.index('_motion:function(el,keys){')
_mE = s.index("/* THE FAMILIES.", _m)
if 'D3X.nudge(d,keys);' not in s[_m:_mE]:
    sys.exit('_motion does not hand over the keys (nothing written)')
for gone in ('Math.abs(k.sc-1)', 'if(k.dy&&Math.abs(k.dy)'):
    if gone in s[_m:_mE]:
        sys.exit('the reduction survives in _motion (nothing written)')
if 'osc' in s[s.index('NUDGE:{'):s.index('nudge:function(d,keys){')]:
    sys.exit('osc survives in the NUDGE block (nothing written)')
if s.count('D3X.NUDGE.osc') != 0:
    sys.exit('osc still has %d readers (nothing written)' % s.count('D3X.NUDGE.osc'))
if s.count('_nudgeAt:function(N,t){') != 1 or s.count('_ease:function(spec,t){') != 1:
    sys.exit('the evaluator is not defined exactly once (nothing written)')
# scale must be applied AFTER the pose functions, and by multiply
_f = s.index('var _nsc=1;')
_p = s.index('if(_nsc!==1)d.obj.scale.multiplyScalar(_nsc);')
_pose = s.index('else if(d.pulseOn)D3X._pulsePose(d);')
if not (_f < _pose < _p):
    sys.exit('the nudge scale is not applied after the pose block (nothing written)')
_frame = s[_f:_p]
if 'scale.setScalar' in _frame:
    sys.exit('the frame block still sets scale directly (nothing written)')
# dy must reach its own axis
if 'd.obj.position.y-=_nv.dy' not in _frame:
    sys.exit('dy does not reach the y axis (nothing written)')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d edits (%s)' % (len(edits), ', '.join(edits)))
