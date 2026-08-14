# -*- coding: utf-8 -*-
"""P725: the dim survives the rolling-to-settled handoff.

Denis: "Shadow appears then off then back on, as if other dice was still
influencing it when they do their settle." Exactly right: the flight ramp
(P724) dims each die at its OWN moment, but d.phys only exists once the
WHOLE tape ends - and the settled branch's catch-up ramp keyed on
phys.t = that shared tape-end stamp. An early settler was fully dim, then
at the last die's settle its k snapped to 0 (bright) and re-ramped. The
fix: phys.t is backdated to the die's PERSONAL settle moment (the same
R._setF the flight ramp uses), so at handoff the settled ramp computes
k=1, wants the same map, and the identity check swaps nothing. Both
settle writers stamp it the same way - one payload, as always.
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


sub(u"      d.phys={x:f.x,y:f.y,z:f.z,q:q.clone(),v:(d.roll&&d.roll.val)||null,t:performance.now()};d.roll=null;/* P702/P703 */",
    u"      /* P725: t is the die's OWN settle moment (the flight ramp's _setF),\n"
    u"         not the tape's end - or an early settler's dim snapped bright at\n"
    u"         the LAST die's settle and re-ramped (Denis's flicker). */\n"
    u"      d.phys={x:f.x,y:f.y,z:f.z,q:q.clone(),v:(d.roll&&d.roll.val)||null,\n"
    u"        t:(d.roll&&d.roll.sol&&d.roll.sol.frames)\n"
    u"          ?d.roll.t0+((d.roll._setF!==undefined?d.roll._setF:d.roll.sol.frames.length))*(this.PHYS.dt*1000)\n"
    u"          :performance.now()};d.roll=null;/* P702/P703/P725 */",
    'P725 physPose stamps the personal moment')

sub(u"      d.phys={x:lf.x,y:lf.y,z:lf.z,\n"
    u"        q:rr.flat.clone().multiply(new THREE.Quaternion(lf.qx,lf.qy,lf.qz,lf.qw)).multiply(rr.fix),\n"
    u"        v:(R&&R.val)||null,t:performance.now()};\n"
    u"      d.roll=null;",
    u"      d.phys={x:lf.x,y:lf.y,z:lf.z,\n"
    u"        q:rr.flat.clone().multiply(new THREE.Quaternion(lf.qx,lf.qy,lf.qz,lf.qw)).multiply(rr.fix),\n"
    u"        v:(R&&R.val)||null,\n"
    u"        t:(R&&R.sol&&R.sol.frames)?R.t0+((R._setF!==undefined?R._setF:R.sol.frames.length))*(D3X.PHYS.dt*1000):performance.now()};/* P725 */\n"
    u"      d.roll=null;",
    'P725 watchdog stamps the same way')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d edits' % n)
