# -*- coding: utf-8 -*-
"""P799: the bust is an impact, not a parting.

Denis: "the bust dice anim still is broken, they split into two stacks
left and right it doesn't look natural at all, try something else."

P733 diagnosed this exact disease ('the row PARTED and bunched') and
then kept its cause: the kick's base angle is still built from
sign(phys.x) - dice left of centre kick left, right of centre kick
right, and 42 degrees of jitter cannot break a binary. Two lobes of
similar magnitude = two stacks.

Something else: ONE SLAM POINT. The bust lands somewhere over the row
(never dead centre, always off the dice line in depth) and every die
is thrown RADIALLY away from it - direction is continuous in the die's
position, so no left/right binary can exist; closer dice are hit
harder (magnitude falls off with distance, replacing the old 'two
unlucky ones' lottery); spin scales with the hit; and the wave reaches
far dice a beat later (t0 staggered by distance - the consumer gains
the t<t0 clamp so a pending kick simply hasn't started). Depth motion
is guaranteed because the slam point is off the dice line, so dice
tumble toward/away from the player too, not just along the row.

The P743 rules stand: same KICK.dist scale, wall-bounce at the row's
edges, dice never leave the screen.
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


# ── 1. the kick consumer honours a staggered start ──
sub("""          if(d.kick){
            var _kt2=(performance.now()-d.kick.t0)/D3X.KICK.ms;
            if(_kt2>1)_kt2=1;""",
    """          if(d.kick){
            var _kt2=(performance.now()-d.kick.t0)/D3X.KICK.ms;
            if(_kt2>1)_kt2=1;
            if(_kt2<0)_kt2=0;/* P799: the wave has not reached this die yet */""",
    'the consumer clamps below')

# ── 2. the impact scatter ──
sub("""    /* P733: CHAOS IS VARIANCE. The old kick read its direction off the
       die's SIGN - left of centre went left, right went right, with a
       whisker of jitter - so the row PARTED and bunched, which is what
       Denis saw. Each die now gets its own angle (outward bias, wide
       spread), its own magnitude, and two of them are picked for a hard
       hit. Same one impulse, applied unevenly. */
    var hit=[];
    this.dice.forEach(function(d){
      if(!d.match||!d.phys||d.burst||d.kick)return;
      if(!d.chip||!d.chip.closest||!d.chip.closest(sel))return;
      hit.push(d);
    });
    if(!hit.length)return 0;
    /* the two unlucky ones */
    var hard={},picks=Math.min(2,hit.length);
    while(Object.keys(hard).length<picks)hard[Math.floor(Math.random()*hit.length)]=1;
    hit.forEach(function(d,i){
      /* outward from the row's middle, then thrown off by up to 42 degrees */
      var base=Math.atan2((Math.random()-0.5)*0.6,(d.phys.x>=0?1:-1));
      var ang=base+(Math.random()-0.5)*1.47;
      var mag=(hard[i]?1.5+Math.random()*0.6:0.65+Math.random()*0.8)*self.KICK.dist;
      var vx=Math.cos(ang)*mag,vz=Math.sin(ang)*mag*0.7-0.1*self.KICK.dist;
      /* P743: THE TABLE HAS EDGES. The kick was unbounded, so a hard hit
         carried a die off screen. Anything that would end past the edge
         bounces off it - the sign flips and the overshoot is what is
         left of the travel, which is what a wall does. */
      var edge=self.KICK.edge||2.6,endX=d.phys.x+vx;
      if(endX>edge)vx=(edge-d.phys.x)-(endX-edge)*0.45;
      else if(endX<-edge)vx=(-edge-d.phys.x)-(endX+edge)*0.45;
      if(Math.abs(vz)>edge*0.5)vz=(vz>0?1:-1)*edge*0.5;
      d.kick={t0:t0,vx:vx,vz:vz,
        sp:(Math.random()<0.5?-1:1)*(hard[i]?4+Math.random()*3:1.5+Math.random()*3)};
    });
    this._shDirty=true;
    return hit.length;""",
    """    /* P799: AN IMPACT, NOT A PARTING. P733 named the disease ('the row
       PARTED and bunched') and kept its cause - the base angle was still
       sign(phys.x), and 42 degrees of jitter cannot break a binary
       (Denis: 'they split into two stacks left and right'). ONE SLAM
       POINT now, never dead centre and always off the dice line in
       depth: every die is thrown RADIALLY away from it, so direction is
       continuous in position and no two-lobe pattern can form; closer
       dice are hit harder (falloff replaces the old hard-hit lottery);
       spin scales with the hit; the wave reaches far dice a beat later. */
    var hit=[];
    this.dice.forEach(function(d){
      if(!d.match||!d.phys||d.burst||d.kick)return;
      if(!d.chip||!d.chip.closest||!d.chip.closest(sel))return;
      hit.push(d);
    });
    if(!hit.length)return 0;
    var ix=(Math.random()-0.5)*1.6;
    var iz=(Math.random()<0.5?-1:1)*(0.35+Math.random()*0.55);
    this._lastImpact={x:ix,z:iz};/* the probe reads this */
    /* P799b: the wall sits just past the OUTERMOST die - the fixed 2.6
       sat INSIDE the row (dice rest out to ~4.8), so the clamp yanked
       outer dice toward the centre, inverting their kicks (it was
       doing the same to the old scatter). Self-calibrating: the row
       tells us where its edge is. */
    var edge=this.KICK.edge||2.6;
    hit.forEach(function(d){var ax=Math.abs(d.phys.x);if(ax+0.45>edge)edge=ax+0.45;});/* P799c: the outermost die was clipping the screen at +0.9 */
    hit.forEach(function(d){
      var dx=d.phys.x-ix,dz=(d.phys.z||0)-iz;
      var L=Math.sqrt(dx*dx+dz*dz)||0.001;
      var ang=Math.atan2(dz,dx)+(Math.random()-0.5)*0.55;
      var mag=self.KICK.dist*(0.55+Math.random()*0.35)*(1.75/(0.6+L));
      var vx=Math.cos(ang)*mag,vz=Math.sin(ang)*mag*0.8;
      /* P743: THE TABLE HAS EDGES - bounce off them, never leave */
      var endX=d.phys.x+vx;
      if(endX>edge)vx=(edge-d.phys.x)-(endX-edge)*0.45;
      else if(endX<-edge)vx=(-edge-d.phys.x)-(endX+edge)*0.45;
      if(Math.abs(vz)>edge*0.5)vz=(vz>0?1:-1)*edge*0.5;
      d.kick={t0:t0+L*70,vx:vx,vz:vz,
        sp:(Math.random()<0.5?-1:1)*(1.5+mag*3.2+Math.random()*1.6)};
    });
    this._shDirty=true;
    return hit.length;""",
    'the impact scatter')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d (%s)' % (len(edits), ', '.join(edits)))
