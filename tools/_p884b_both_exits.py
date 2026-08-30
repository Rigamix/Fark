# -*- coding: utf-8 -*-
u"""P884b: moment 2 was hooked to one of the two settle exits.

P884 put the beat in _physPose's `done` branch. A die also settles through the
WATCHDOG (29296), which retires a tape that has plainly finished for a die
_physPose never ran on - because _physPose only runs for a die the frame
decided to DRAW. The watchdog's own comment is the warning I walked into:

    "the SAME payload as _physPose's done branch - v drives the side dim, t
     its ramp; a bare pose here meant a watchdog-settled die silently never
     dimmed (two exits, one payload - the rule)."

So this file had already been bitten by this exact hole, had written down the
rule, and I added a behaviour to one exit anyway.

HOW IT SURFACED, because it is the more useful half. The probe measured zero
beats on a hand with a live icon in it. Headless renders the 3D layer at ~1fps,
so most dice are never drawn while their tape plays and the WATCHDOG becomes
the common exit - it retired all six. A stack trace on the predicate settled it
in one run: all six consultations came from _markLoneCast, none from the hook,
so the hook had not run at all rather than run and been refused. On a 60fps
browser the beat would have fired and looked correct, and the hole would have
been a die that occasionally lands with no jolt for no visible reason.

THE FIX IS ONE FUNCTION, TWO CALLERS, not the same block written twice. The
watchdog's rule says the payload must match at both exits; the way to keep two
things matching is to have one of them. _landed(d) holds the lookup, the
predicate and the beat, and both exits call it.
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


HOOK = u"""      /* P884: MOMENT 2. This die - not the tape - has come to rest, which is
         why the hook is here and not at the roll's end: the tape ends on the
         LAST die, and six jolts fired together are one noise. G.pool is the
         player's hand, so rival dice are excluded by construction rather than
         by a test, and _dieIsIcon has excluded a refused brand since P878, so
         a brand whose lane is taken lands silently instead of promising a
         payoff the rules have already declined. */
      if(d.match&&d.chip&&window.FKFX&&typeof _dieIsIcon==='function'){
        try{
          var _lp=(window.G&&G.pool)||[],_lg=null;
          for(var _li=0;_li<_lp.length;_li++){
            if(_lp[_li].el===d.chip){_lg=_lp[_li];break;}
          }
          if(_lg&&_dieIsIcon(_lg)){
            var _lk=(window.ENCH_ICONS&&_lg.ench&&ENCH_ICONS[_lg.ench.t])||null;
            FKFX.landed(d.chip,_lk&&_lk.ink);
          }
        }catch(e){}
      }
"""

# ── 1. the inline hook becomes a call ────────────────────────────────
sub(HOOK, u"""      this._landed(d);/* P884b: one of TWO settle exits - see _landed */
""", '1 the physPose exit calls it')

# ── 2. the function, beside the pose it belongs to ───────────────────
sub(u"""  _physPose:function(d){""",
    u"""  /* P884 / P884b: MOMENT 2 - a branded face has landed.
     ONE FUNCTION, TWO CALLERS. A die settles either in _physPose's `done`
     branch or in the WATCHDOG, which retires a tape that has plainly finished
     for a die _physPose never ran on - and _physPose only runs for a die the
     frame decided to DRAW. The watchdog already carries the note for exactly
     this hazard ("two exits, one payload - the rule"), earned when a
     watchdog-settled die silently never dimmed. P884 hooked one exit anyway,
     and headless - where ~1fps makes the watchdog the COMMON exit - measured
     zero beats on a hand that had a live icon in it.
     It is hooked at the DIE's own settle rather than the tape's end because
     the tape ends on the last die, and six jolts fired together are one noise.
     G.pool is the player's hand, so rival dice are out by construction rather
     than by a test; and _dieIsIcon has excluded a refused brand since P878, so
     a brand whose lane is taken lands silently instead of promising a payoff
     the rules have already declined. */
  _landed:function(d){
    if(!d||!d.match||!d.chip)return false;
    if(!window.FKFX||typeof _dieIsIcon!=='function')return false;
    try{
      var p=(window.G&&G.pool)||[],g=null;
      for(var i=0;i<p.length;i++){if(p[i].el===d.chip){g=p[i];break;}}
      if(!g||!_dieIsIcon(g))return false;
      var k=(window.ENCH_ICONS&&g.ench&&ENCH_ICONS[g.ench.t])||null;
      return FKFX.landed(d.chip,k&&k.ink);
    }catch(e){return false;}
  },
  _physPose:function(d){""",
    '2 the function')

# ── 3. the watchdog exit calls it too ────────────────────────────────
sub(u"""        t:(R&&R.sol&&R.sol.frames)?R.t0+((R._setF!==undefined?R._setF:R.sol.frames.length))*(D3X.PHYS.dt*1000):performance.now()};/* P725 */
      d.roll=null;
    });""",
    u"""        t:(R&&R.sol&&R.sol.frames)?R.t0+((R._setF!==undefined?R._setF:R.sol.frames.length))*(D3X.PHYS.dt*1000):performance.now()};/* P725 */
      d.roll=null;
      D3X._landed(d);/* P884b: the OTHER settle exit - the rule above applies
                        to the beat exactly as it applies to the payload */
    });""",
    '3 the watchdog exit calls it')

# ── post-asserts ─────────────────────────────────────────────────────
if s.count('_landed:function(d){') != 1:
    sys.exit('the beat helper is not defined exactly once (nothing written)')
n = s.count('_landed(d);')
if n != 2:
    sys.exit('the beat is called from %d exits, expected 2 (nothing written)' % n)
if 'FKFX.landed(' not in s or s.count('FKFX.landed(') != 1:
    sys.exit('the beat itself must be reached from exactly one place '
             '(nothing written)')
# both settle exits must be covered - assert by position, not by counting
_pp = s.index("d.phys={x:f.x,y:f.y,z:f.z,q:q.clone()")
_wd = s.index('d.phys={x:lf.x,y:lf.y,z:lf.z,')
_end_pp = s.index('return {x:f.x,y:f.y,z:f.z,q:q,done:done};', _pp)
_end_wd = s.index('SYNC BEFORE STARTING A DEFERRED THROW', _wd)
if '_landed(d);' not in s[_pp:_end_pp]:
    sys.exit('the _physPose exit lost its call (nothing written)')
if '_landed(d);' not in s[_wd:_end_wd]:
    sys.exit('the watchdog exit has no call (nothing written)')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d edits (%s)' % (len(edits), ', '.join(edits)))
