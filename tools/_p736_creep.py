# -*- coding: utf-8 -*-
"""P736: a die that is done STOPS - no more slow drag into place.

Denis, twice: 'dice take a looong while to finish, they hang and then
slooowly land like they are in jelly / sliding against an invisible
wall'. Measured on three throws: the tape runs 1.2-1.85s and 183-650ms
of that is the TAIL - frames after the die's last clearly-moving frame,
with up to 56 consecutive crawl frames. That tail is what he is watching.

Two causes, both in the solve loop:
- THE LANE PULL SKIPPED ONLY THE FULLY STOPPED. Its gate is
  velocity > stopV (0.09) - a die oozing at 0.3 is above that, so the
  spring keeps drawing it toward its lane centre at walking pace. A
  correction applied to a die that has visibly finished is exactly the
  magnetism this file removed everywhere else, surviving in slow motion.
- NOTHING ENDED THE OOZE. Damping (0.55) and friction (0.42) shrink the
  speed asymptotically; the still-frame test needs 14 frames under
  0.006 of displacement, so a die creeping just above it keeps the tape
  running frame after frame.

THE REST SNAP: a die that has been under the creep band for six
consecutive frames, low enough to be on the table, has its velocity and
spin zeroed - it stops, the still-counter fires immediately, and the
tape cut trims the rest. The band is well above stopV so it engages
while the die is still oozing, and the six-frame wait means a die that
is genuinely still moving is never caught mid-slide.
"""
import io, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'fark_proto.html')
s = io.open(P, encoding='utf-8', newline='').read()
n = 0


def sub(old, new, label, count=1):
    global s, n
    c = s.count(old)
    if c != count and '\n' in old:
        old2 = old.replace('\n', '\r\n')
        if s.count(old2) == count:
            old, c = old2, count
            new = new.replace('\n', '\r\n')
    if c != count:
        sys.exit('ANCHOR x%d (need %d) for %s' % (c, count, label))
    s = s.replace(old, new)
    n += 1
    print('  ok  %s' % label)


sub(u"    on:true, gravity:-50, dt:1/60, cap:700, stopV:.09, stopW:.14,",
    u"    on:true, gravity:-50, dt:1/60, cap:700, stopV:.09, stopW:.14,\n"
    u"    /* P736: THE CREEP BAND. A die under both of these for creepFrames\n"
    u"       consecutive frames, resting low, is finished - its velocity is\n"
    u"       zeroed rather than left to ooze toward zero. Measured: the tail\n"
    u"       (frames after the last clearly-moving one) ran 183-650ms per\n"
    u"       throw before this. Well above stopV on purpose: it has to catch\n"
    u"       the ooze, not the stop. */\n"
    u"    creepV:.5, creepW:.85, creepFrames:6, creepY:1.25,",
    'creep constants')

sub(u"      if(P.lanePull>0){\n"
    u"        var _K=P.lanePull,_C=2*Math.sqrt(_K);\n"
    u"        for(var kp=0;kp<N;kp++){\n"
    u"          var bp=bodies[kp];\n"
    u"          if(bp.velocity.norm()<=P.stopV&&bp.angularVelocity.norm()<=P.stopW)continue;",
    u"      if(P.lanePull>0){\n"
    u"        var _K=P.lanePull,_C=2*Math.sqrt(_K);\n"
    u"        for(var kp=0;kp<N;kp++){\n"
    u"          var bp=bodies[kp];\n"
    u"          /* P736: and nothing pulls a die that is merely OOZING either -\n"
    u"             the old gate was stopV (0.09), so a die creeping at 0.3 was\n"
    u"             still being drawn toward its lane at walking pace, which is\n"
    u"             the slow drag Denis reported twice. */\n"
    u"          if(bp.velocity.norm()<=P.creepV&&bp.angularVelocity.norm()<=P.creepW)continue;",
    'lane pull stops dragging the finished')

sub(u"      world.step(P.dt);\n"
    u"      var fr=[];",
    u"      world.step(P.dt);\n"
    u"      /* P736: THE REST SNAP. Damping and friction only approach zero;\n"
    u"         a die can ooze for half a second under the still-frame test's\n"
    u"         nose. Six consecutive frames inside the creep band, low enough\n"
    u"         to be on the table, means finished - so end it, and let the\n"
    u"         still counter and the tape cut do the rest. */\n"
    u"      for(var ks=0;ks<N;ks++){\n"
    u"        var bs=bodies[ks];\n"
    u"        if(bs.velocity.norm()<P.creepV&&bs.angularVelocity.norm()<P.creepW\n"
    u"          &&bs.position.y<P.creepY){\n"
    u"          bs._creep=(bs._creep||0)+1;\n"
    u"          if(bs._creep>=P.creepFrames){\n"
    u"            bs.velocity.set(0,0,0);bs.angularVelocity.set(0,0,0);\n"
    u"          }\n"
    u"        }else bs._creep=0;\n"
    u"      }\n"
    u"      var fr=[];",
    'the rest snap')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d edits' % n)
