# -*- coding: utf-8 -*-
u"""P884 (FX BRIEF step 6): moment 2 - the branded face lands.

The brief calls this the best moment in the system and it did not exist. A
brand is baked into the UV (moment 1) and fires when you keep it (moment 3),
and the instant BETWEEN them - your branded face actually coming up - passed in
silence. That instant is the jolt the purchase was for.

WHERE IT HOOKS. 28781's `if(done)` is the die's OWN settle: the one place
per die per roll where physics reports it has come to rest, and the place P725
already chose as the die's own settle moment for the dim ramp. Not the tape's
end, which is the LAST die - hooking there would fire six beats at once and
turn six small jolts into one noise.

WHAT IT PLAYS. Nothing new to look at: a short glow in the brand's own ink from
ENCH_ICONS, a 6% squash, and a light high shimmer, ~200ms. Both visual halves
go through the primitives P881 and P883 just made reach a settled die - _glow
becomes an over-canvas mark and _motion's `sc` becomes a nudge on the mesh - so
this is the first thing built ON that work rather than beside it.

IT IS A METHOD, NOT A TENTH FAMILY. The nine instruments are a count this file
and its comments cite, and moment 2 is not one of the nine authored
instruments - it is a beat composed from the primitives. Adding a family would
have made every "nine instruments" comment stale to buy nothing.

TWO THINGS IT IS NARROW ABOUT, both by construction rather than by a flag:
  - PLAYER DICE ONLY. The lookup walks G.pool, which is the player's hand.
    Enchants are the player's; a rival's dice are not in that array, so there
    is nothing to exclude.
  - A REFUSED BRAND LANDS SILENTLY. _dieIsIcon is _iconLive AND NOT
    _iconRefused since P878, so a brand whose lane is already marked gets no
    jolt - which is right, because it is not going to fire, and promising the
    player a payoff the rules have already declined is the one thing this beat
    must not do.
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


# ── 1. the beat ──────────────────────────────────────────────────────
sub(u"""  play:function(id,el){""",
    u"""  /* P884: MOMENT 2 - a branded face has landed. A METHOD, not a tenth family:
     the nine instruments are a count this file's comments cite, and this is a
     beat composed from the primitives rather than another authored instrument.
     Both visual halves reach a settled match die only because P881 and P883
     routed them by owner - _glow becomes a mark on the over-canvas and
     _motion's `sc` becomes a nudge on the mesh - so this is the first thing
     built on that work. Quiet on purpose: moment 3 is the payoff, and this one
     only has to say "there it is". */
  landed:function(el,ink){
    if(!this.on||!el)return false;
    var c=ink||'#d8b054';
    try{
      this.snd('shimmer',1,1.35);
      this._glow(el,c,5,220);
      this._motion(el,[{o:0,sc:1},{o:.5,sc:1.06},{o:1,sc:1,t:200}]);
    }catch(e){return false;}
    return true;
  },
  play:function(id,el){""",
    '1 the landed beat')

# ── 2. the hook, at the die's own settle ─────────────────────────────
sub(u"""      if(!this._rolling())this._shDirty=true;/* they have landed: draw them */
    }""",
    u"""      if(!this._rolling())this._shDirty=true;/* they have landed: draw them */
      /* P884: MOMENT 2. This die - not the tape - has come to rest, which is
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
    }""",
    '2 hooked at the die own settle')

# ── post-asserts ─────────────────────────────────────────────────────
if s.count('landed:function(el,ink){') != 1:
    sys.exit('the beat is not defined exactly once (nothing written)')
if s.count('FKFX.landed(') != 1:
    sys.exit('the beat is not called exactly once (nothing written)')
# it must be inside the per-die settle, not at the tape's end
_a = s.index("d.phys={x:f.x,y:f.y,z:f.z,q:q.clone()")
_b = s.index('return {x:f.x,y:f.y,z:f.z,q:q,done:done};', _a)
if 'FKFX.landed(' not in s[_a:_b]:
    sys.exit('the hook is not inside the per-die settle branch (nothing written)')
# the predicate must be the canonical one, not a hand-rolled test
_c = s.index('P884: MOMENT 2. This die')
_d = s.index('FKFX.landed(', _c)
if '_iconLive' in s[_c:_d] or 'd.ench.face' in s[_c:_d]:
    sys.exit('the hook re-implements the predicate instead of calling it '
             '(nothing written)')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d edits (%s)' % (len(edits), ', '.join(edits)))
