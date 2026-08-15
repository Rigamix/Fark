# -*- coding: utf-8 -*-
"""P740: REVERT P736 whole. It failed both tests - the seeded A/B and Denis.

P736 tried to shorten the settle drag two ways: release the lane pull
once a die is inside its lane radius, and zero a die that spends six
frames inside a creep band.

- BY EYE: releasing the pull inside 0.54 of the pitch means dice are
  never actually centred, so they bundle. Denis: 'you broke the dice
  roll, they don't stay in their lane now, they bundle too much' - with
  a screenshot of four dice clumped left and a gap right.
- BY MEASUREMENT: a seeded A/B (the same eight throws, identical values
  and impulses, fix on vs off) put the drag WORSE with the change -
  573ms of crawl against 498ms, and a longer tape (1779ms vs 1696ms).

So it goes, entirely: the constants, the release and the snap. The
settle drag is a real complaint and stays OPEN - but the base returns to
the behaviour that at least lays the dice out correctly, which is the
more important of the two.
"""
import io, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'fark_proto.html')
s = io.open(P, encoding='utf-8', newline='').read()
n = 0


def sub(old, new, label):
    global s, n
    c = s.count(old)
    if c != 1:
        old2 = old.replace('\n', '\r\n')
        if s.count(old2) == 1:
            old, new = old2, new.replace('\n', '\r\n')
        else:
            sys.exit('ANCHOR x%d for %s' % (c, label))
    s = s.replace(old, new)
    n += 1
    print('  ok  ' + label)


sub(u"""    /* P736: THE CREEP BAND. A die under both of these for creepFrames
       consecutive frames, resting low, is finished - its velocity is
       zeroed rather than left to ooze toward zero. Measured: the tail
       (frames after the last clearly-moving one) ran 183-650ms per
       throw before this. Well above stopV on purpose: it has to catch
       the ooze, not the stop. */
    creepV:.5, creepW:.85, creepFrames:6, creepY:1.25,
""", u"", 'creep constants removed')

sub(u"""        /* P736b: THE PULL IS SELF-SUSTAINING, and that is the drag. A
           critically damped spring approaches its target asymptotically:
           at K=37 a die 0.3 off-centre settles into a terminal creep of
           K*dx/C ~ 0.9 units/s - ABOVE any speed gate, so the gate never
           fires and the die is walked into its lane over half a second.
           That is Denis's 'sliding against an invisible wall'. The lane
           is an AREA (laneRadius), so once the die is inside it, stop
           pulling: it is already where it belongs. */
        var _pitch=(N>1&&slotC.length>1)?Math.abs(slotC[1]-slotC[0]):1.6;
        var _laneR=_pitch*(P.laneRadius||0.54);
        for(var kp=0;kp<N;kp++){
          var bp=bodies[kp];
          if(Math.abs(slotC[kp]-bp.position.x)<_laneR
            &&Math.abs(bp.position.z)<_laneR*0.6)continue;
          /* P736: and nothing pulls a die that is merely OOZING either -
             the old gate was stopV (0.09), so a die creeping at 0.3 was
             still being drawn toward its lane at walking pace, which is
             the slow drag Denis reported twice. */
          if(bp.velocity.norm()<=P.creepV&&bp.angularVelocity.norm()<=P.creepW)continue;""",
    u"""        /* P736 REVERTED (P740): releasing the pull inside the lane
           radius meant the dice were never centred - they bundled, which
           is exactly what Denis saw - and the seeded A/B put the drag
           WORSE with it (573ms vs 498ms over the same eight throws). The
           pull runs to rest again, as it always did. */
        for(var kp=0;kp<N;kp++){
          var bp=bodies[kp];
          if(bp.velocity.norm()<=P.stopV&&bp.angularVelocity.norm()<=P.stopW)continue;""",
    'lane pull restored')

sub(u"""      /* P736: THE REST SNAP. Damping and friction only approach zero;
         a die can ooze for half a second under the still-frame test's
         nose. Six consecutive frames inside the creep band, low enough
         to be on the table, means finished - so end it, and let the
         still counter and the tape cut do the rest. */
      for(var ks=0;ks<N;ks++){
        var bs=bodies[ks];
        if(bs.velocity.norm()<P.creepV&&bs.angularVelocity.norm()<P.creepW
          &&bs.position.y<P.creepY){
          bs._creep=(bs._creep||0)+1;
          if(bs._creep>=P.creepFrames){
            bs.velocity.set(0,0,0);bs.angularVelocity.set(0,0,0);
          }
        }else bs._creep=0;
      }
      var fr=[];""",
    u"      var fr=[];",
    'rest snap removed')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d edits' % n)
