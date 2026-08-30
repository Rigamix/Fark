# -*- coding: utf-8 -*-
u"""P882: `rt` is drivable after all - P881 dropped it on a wrong reason.

P881 said a settled die's rotation IS the face it shows, so spinning it would
change the number. That is true of an ARBITRARY axis and false of the one this
file already uses. P821 solved exactly this for the bust kick: premultiply
about WORLD UP, in the world frame, and the scoring face stays up - its comment
records that multiply() applied the spin in the die's LOCAL frame, whose Y axis
lies horizontal for faces 1/3/4/6, and measured 8 of 10 non-2 dice settling
cocked. So the mechanism for "turn a settled die without changing its number"
was sitting six lines above the code P881 was editing.

Dropping rt was defensible; the reason given for it was not, and it contradicted
a comment already read. So `rt` joins dx/dy and sc: a small damped yaw about
world up, on the same premultiply the kick uses. SET's authored -2/+2 degrees
becomes a settle twist that keeps its face.

This makes the brief's step 5 line true as written - sc AND rt driven into D3X,
with nothing left in the instrument definitions that silently does nothing.
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


# ── 1. nudge carries a yaw ───────────────────────────────────────────
sub(u"""  NUDGE:{ms:260,osc:6},
  nudge:function(d,dxMax,scMax){
    if(!d)return;
    d.nudge={t0:performance.now(),
             amp:(dxMax||0)/((d.w0||60)),
             sc:(scMax===undefined?0:scMax)};
    this._shDirty=true;
  },""",
    u"""  NUDGE:{ms:260,osc:6},
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
    '1 nudge takes a yaw')

# ── 2. applied on the kick's axis, for the kick's reason ─────────────
sub(u"""              if(d.nudge.sc)d.obj.scale.setScalar(1+d.nudge.sc*_nd*
                Math.sin(_nt*Math.PI));
              D3X._shDirty=true;""",
    u"""              if(d.nudge.sc)d.obj.scale.setScalar(1+d.nudge.sc*_nd*
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
              D3X._shDirty=true;""",
    '2 the yaw applied about world up')

# ── 3. _motion collects rt and stops calling it undrivable ───────────
sub(u"""     damped shake and `sc` becomes the squash SET has always described and
     never shown. `rt` is dropped on purpose - D3X owns the quaternion and a
     settled die's rotation IS the face it is showing, so spinning it would
     change the number. */""",
    u"""     damped shake, `sc` becomes the squash SET has always described and never
     shown, and `rt` becomes a twist.
     P882: rt was dropped here on a wrong reason - that spinning a settled die
     would change its number. True of an arbitrary axis, false of the one this
     file already uses: the bust kick premultiplies about WORLD UP for exactly
     this reason (P821, in the settled branch), and the scoring face stays up.
     Nothing an instrument can write is silently discarded now. */""",
    '3 the comment corrected')

sub(u"""        var mx=0,ms=0,i,k;
        for(i=0;i<keys.length;i++){
          k=keys[i];
          if(k.dx&&Math.abs(k.dx)>Math.abs(mx))mx=k.dx;
          if(k.dy&&Math.abs(k.dy)>Math.abs(mx))mx=k.dy;
          if(k.sc!==undefined&&Math.abs(k.sc-1)>Math.abs(ms))ms=k.sc-1;
        }
        if(mx||ms)D3X.nudge(d,mx,ms);
        return;""",
    u"""        var mx=0,ms=0,mr=0,i,k;
        for(i=0;i<keys.length;i++){
          k=keys[i];
          if(k.dx&&Math.abs(k.dx)>Math.abs(mx))mx=k.dx;
          if(k.dy&&Math.abs(k.dy)>Math.abs(mx))mx=k.dy;
          if(k.sc!==undefined&&Math.abs(k.sc-1)>Math.abs(ms))ms=k.sc-1;
          if(k.rt&&Math.abs(k.rt)>Math.abs(mr))mr=k.rt;
        }
        if(mx||ms||mr)D3X.nudge(d,mx,ms,mr);
        return;""",
    '4 rt collected and passed')

# ── post-asserts ─────────────────────────────────────────────────────
_a = s.index('_motion:function(el,keys){')
_b = s.index('/* THE FAMILIES.', _a)
if 'D3X.nudge(d,mx,ms,mr)' not in s[_a:_b]:
    sys.exit('rt does not reach nudge (nothing written)')
_c = s.index('if(d.nudge){')
_d = s.index('/* P702: scoring face bright', _c)
frame = s[_c:_d]
if 'premultiply' not in frame:
    sys.exit('the yaw is not premultiplied (nothing written)')
if 'setFromAxisAngle' not in frame or '_kup' not in frame:
    sys.exit('the yaw is not on the world-up axis the kick uses (nothing written)')
if s.count('rt:(rtMax?rtMax*Math.PI/180:0)') != 1:
    sys.exit('the degree conversion is not in nudge exactly once (nothing written)')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d edits (%s)' % (len(edits), ', '.join(edits)))
