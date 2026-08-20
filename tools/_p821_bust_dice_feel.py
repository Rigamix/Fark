# -*- coding: utf-8 -*-
"""P821: busted dice settle FLAT, and the scatter gets wider + faster.

Denis (playthrough notes): "busted dice must settle on a face" and
"scatter more/faster".

(a) THE FLATNESS BUG, measured before touching it: after a bust, dice
showing 2 stayed perfectly flat (up-dot 1.000) while 1/3/4/6 tipped to
0.71-0.97 - two baseline runs, 8 of 10 non-2 dice cocked. Cause: the
kick's yaw quaternion is composed with multiply(), which applies it in
the die's LOCAL frame - the mesh Y axis only points up for faces 2 and
5 (FACE table), so for every other face the 'tabletop spin' is a roll
about a horizontal axis. The comment above the line states the intent
('spinning about the die's own up axis so the scoring face stays up');
premultiply() applies the same spin about WORLD up and preserves any
flat pose exactly.

(b) The dials, per the note: KICK.ms 620->460 (faster slide),
KICK.dist 0.85->1.15 (wider kick; P743's 1.5 was ruled too strong,
this splits the difference), stagger 70->55 ms/die-width (the wave
crosses the row quicker).

(c) Spacing: the sim's die-die collider (proxy 1.06 die-widths) is
narrower than the painted mid-row die (drawnMid 1.25), so two settled
neighbours can legally overlap on screen - the recon confirmed the
old 'fights the pen' warning is obsolete (the slot pen is dead code).
proxy 1.06->1.22: separation happens DURING the roll, no post-hoc
sliding, painted faces can no longer interpenetrate at rest.
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


# (a) world-frame yaw - flat stays flat
sub("""            _kq2.setFromAxisAngle(D3X._kup||(D3X._kup=new THREE.Vector3(0,1,0)),d.kick.sp*_ke2*0.3);
            d.obj.quaternion.multiply(_kq2);""",
    """            _kq2.setFromAxisAngle(D3X._kup||(D3X._kup=new THREE.Vector3(0,1,0)),d.kick.sp*_ke2*0.3);
            /* P821: PREmultiply - world-frame yaw about world up. multiply()
               applied the spin in the die's LOCAL frame, whose Y axis lies
               HORIZONTAL for faces 1/3/4/6 (only 2 and 5 have their normal
               on mesh Y), so those dice rolled over and settled cocked -
               measured: 8 of 10 non-2 dice off-face across two baselines,
               every 2 perfectly flat. The comment above always said 'the
               scoring face stays up'; now the math agrees. */
            d.obj.quaternion.premultiply(_kq2);""",
    'kick yaw in world frame')

# (b) wider + faster
sub("""  KICK:{ms:620,dist:0.85,spin:4.5,edge:2.6},""",
    """  /* P821: ms 620->460, dist 0.85->1.15 (Denis: 'scatter more/faster';
     P743's 1.5 was too strong, this splits the difference). spin is a
     dead dial - the per-die value at the launch site is what spins. */
  KICK:{ms:460,dist:1.15,spin:4.5,edge:2.6},""",
    'kick faster and wider')

sub("""      d.kick={t0:t0+L*70,vx:vx,vz:vz,""",
    """      d.kick={t0:t0+L*55,vx:vx,vz:vz,/* P821: the wave crosses quicker (was 70ms/die-width) */""",
    'stagger quickened')

# (c) the collider matches the painted die
sub("""  proxy:1.06, tall:0.96,""",
    """  proxy:1.22, tall:0.96,/* P821: was 1.06 - narrower than the painted
     mid-row die (drawnMid 1.25), so neighbours could legally overlap on
     screen. The 'fights the pen' fear is obsolete: the slot pen is dead
     code (recon-verified), separation now happens during the roll. */""",
    'collider matches the paint')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d (%s)' % (len(edits), ', '.join(edits)))
