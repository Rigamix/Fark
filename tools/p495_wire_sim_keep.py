# -*- coding: utf-8 -*-
u"""P495 - the SIM's rival chooses too, or the measurement is blind.

F.oppTurn has its own keep step - it always has. That is the finding the very
first sizing turned up: wiring the game alone and then measuring difficulty
through this harness would run the harness's own maximal-keep copy and report a
ZERO DELTA, which reads as "the personas do not matter" and actually means "the
instrument never executed the change".

Placed between the bust check and `bank+=total`, because the sim banks the total
before it builds keptIdx - choosing after the bank would credit the maximal
points and keep the chosen dice.

FOG: `_vis` is `live` minus fogIdx, in order, which is exactly how fV was built,
so a mask over _vis is already fV-indexed and the existing fi/fogIdx walk below
needs no change. The rival chooses from the seats it can SEE, same as the game.

`bank` is the running total, which is the harness's equivalent of the game's
oppBank, so it is what goes to _legalKeeps as `locked`.

Guarded on typeof so an older fark_proto.html still runs this harness.
"""
import io, os

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   'tools', 'sim_harness.js')
with io.open(SRC, encoding='utf-8') as f:
    s = f.read()
orig = s

OLD = u"""    if(!total||total<=0){out.busted=true;out.rolls=rolls;bank=0;break;}
    bank+=total;
    var keptIdx={};"""
assert s.count(OLD) == 1, 'sim keep step matched %d' % s.count(OLD)

s = s.replace(OLD, u"""    if(!total||total<=0){out.busted=true;out.rolls=rolls;bank=0;break;}
    /* P495 - THE PERSONA CHOOSES, in the sim as well as the game. This harness
       has its own keep step, so leaving it on the maximal keep would make every
       persona measurement a guaranteed zero - the instrument reporting that the
       change does nothing because it never ran it.
       Before bank+=total: the sim banks first and builds keptIdx after, so
       choosing later would bank the maximal points while keeping the chosen
       dice. _vis is `live` minus the fogged seat IN ORDER, which is how fV was
       built, so this mask is already fV-indexed and the fi/fogIdx walk below is
       untouched. */
    if(typeof _oppChooseFrom==='function'){
      var _vis=[];
      for(var _vq=0;_vq<live.length;_vq++)if(_vq!==fogIdx)_vis.push(live[_vq]);
      var _vpick=_oppChooseFrom(_vis,total,bank);
      if(_vpick){
        total=_vpick.pts;
        used=_vis.map(function(d){return _vpick.sel.indexOf(d)>=0;});
      }
    }
    bank+=total;
    var keptIdx={};""")

# ── gates, BEFORE the write ──
assert s != orig, 'nothing changed'
assert s.count('_oppChooseFrom(_vis,total,bank)') == 1
assert s.count("typeof _oppChooseFrom==='function'") == 1
# the choice must precede the bank, never follow it
assert s.index('_oppChooseFrom(_vis') < s.index('bank+=total;\n    var keptIdx'), \
    'the choice runs after the bank'
# the existing fog walk is untouched - the mask is deliberately fV-indexed
assert s.count('if(w===fogIdx){nextLive.push(live[w]);continue;}') == 1
assert s.count('for(var q=0;q<fV.length;q++)if(used&&used[q])keptIdx[q]=1;') == 1
# P489's scoring swap survives
assert s.count('_scoreRollBest') == 2

with io.open(SRC, 'w', encoding='utf-8', newline='') as f:
    f.write(s)
print('P495 applied: the sim rival chooses, so the measurement can see it')
