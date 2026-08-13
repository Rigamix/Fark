# -*- coding: utf-8 -*-
"""P703b: the OTHER settle exit carries the same payload.

Settling has two writers: _physPose's done branch, and the overdue-tape
watchdog that snaps a die to its last frame when playback outruns its tape
(+8 frames grace). P702/P703 taught the first to carry {v, t}; the twin
kept writing a bare pose - so any die settled by the watchdog (a hitch, a
background tab, every other headless run) silently never dimmed, and the
ramp had no clock. One exit path, one payload - the standing lesson, again.
Found because the probe's 'no settle' was really 'settled without v'.
"""
import io, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'fark_proto.html')
s = io.open(P, encoding='utf-8', newline='').read()

old = (u"      d.phys={x:lf.x,y:lf.y,z:lf.z,\n"
       u"        q:rr.flat.clone().multiply(new THREE.Quaternion(lf.qx,lf.qy,lf.qz,lf.qw)).multiply(rr.fix)};\n"
       u"      d.roll=null;")
new = (u"      /* P703b: the SAME payload as _physPose's done branch - v drives the\n"
       u"         side dim, t its ramp; a bare pose here meant a watchdog-settled\n"
       u"         die silently never dimmed (two exits, one payload - the rule). */\n"
       u"      d.phys={x:lf.x,y:lf.y,z:lf.z,\n"
       u"        q:rr.flat.clone().multiply(new THREE.Quaternion(lf.qx,lf.qy,lf.qz,lf.qw)).multiply(rr.fix),\n"
       u"        v:(R&&R.val)||null,t:performance.now()};\n"
       u"      d.roll=null;")
c = s.count(old)
if c != 1:
    sys.exit('ANCHOR x%d (need 1)' % c)
io.open(P, 'w', encoding='utf-8', newline='').write(s.replace(old, new))
print('  ok  P703b watchdog exit carries {v,t}')
