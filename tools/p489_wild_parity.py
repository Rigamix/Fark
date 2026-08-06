# -*- coding: utf-8 -*-
u"""P489 - the rival scores wilds the way the player does. Law 6.

RULED (OPEN.md 11): yes, give the rival wild-as-option scoring matching the
player exactly, as its own measured change, before the keep wiring.

THE GAP. The player's keeps go through scoreSelection, which scores a wild both
ways and keeps the better - its own comment: "a Jade 6 could only ever be spent
as a wild and never as a 6... a 1-2-3-4-5-6 straight could not complete because
its 6 had been replaced". The rival calls scoreRoll directly, one pass. The fix
landed on the player's path and never reached the rival.

Measured over all 462 rolls containing a jade 6: 308 where jade vs bone changes
the score, worst case 23456 - rival takes 50, the same dice are worth 750.

WHY A NEW FUNCTION RATHER THAN CALLING scoreSelection. The rival needs `used`,
not just a point total - `used` is what decides which dice it keeps.
scoreSelection returns a number, and it gates on VALIDITY (every selected die
must be used) because a SELECTION must be fully scoring. A ROLL's `used` is
partial by nature. So the rival's version takes whichever pass scores higher
together with THAT PASS'S `used` array, and applies no validity gate.

SAFE TO SCORE TWICE: scoreRoll writes no globals and fires no cards or effects
(it returns an `effects` list for the caller to act on), and scoreSelection
already runs it up to three times. Verified by inspection before relying on it.

SEVEN CALL SITES IN THE GAME, ALL OF THEM. Converting some would leave the
rival's wild worth different amounts depending on which disruption card had
fired - worse than the bug. And the SIM's F.oppTurn too: it has its own
scoreRoll call, so leaving it would make the before/after measurement blind to
the very change being measured.
"""
import io, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'fark_proto.html')
HARNESS = os.path.join(ROOT, 'tools', 'sim_harness.js')

with io.open(SRC, encoding='utf-8') as f:
    s = f.read()
orig = s

# ── 1. the helper, placed just before scoreSelection ──
ANCH = u"function scoreSelection(selVals,cards,locked,context,dieMats,dieEnchs){"
assert s.count(ANCH) == 1, 'scoreSelection anchor matched %d' % s.count(ANCH)
s = s.replace(ANCH, u"""/* _scoreRollBest - scoreRoll, but a wild is an OPTION rather than a
   replacement. LAW 6: whatever the player can do, an NPC can do.

   scoreRoll substitutes a wild unconditionally, so a Jade 6 can only ever be
   spent as a wild and never as a 6. The player has never had that problem
   because every player keep goes through scoreSelection, which scores both
   ways and keeps the better. The rival calls scoreRoll directly and so was
   stuck with the substitution - measured, 23456 with a jade 6 scored 50 for
   the rival and 750 for the player off identical dice.

   Returns the WHOLE result of whichever pass scored higher, not just its
   total: `used` decides which dice the rival keeps, so it has to come from
   the pass that won. No validity gate here - scoreSelection needs one because
   a SELECTION must be entirely scoring dice, but a ROLL's `used` is partial by
   nature and that is the point of it. */
function _scoreRollBest(vals,cards,locked,context,dieMats,dieEnchs){
  var r=scoreRoll(vals,cards,locked,context,dieMats,dieEnchs);
  var _hasWild=false;
  try{
    (dieMats||[]).forEach(function(m){
      var dt=getDie(m);
      if(dt&&dt.effect&&/^wild_/.test(dt.effect.mechanic||''))_hasWild=true;
    });
  }catch(e){}
  if(!_hasWild)return r;/* control arm: with no wild this is scoreRoll exactly */
  var _ctxN=Object.assign({},context||{},{_noWild:true});
  var _rN=scoreRoll(vals,cards,locked,_ctxN,dieMats,dieEnchs);
  return (_rN&&_rN.total>r.total)?_rN:r;
}

""" + ANCH)

# ── 2. all seven rival call sites ──
SITES = [
    (u"var{total,used,context:newCtx}=scoreRoll(_fogV,G.oCards,oppBank,crowsCtx,_fogM);",
     u"var{total,used,context:newCtx}=_scoreRollBest(_fogV,G.oCards,oppBank,crowsCtx,_fogM);"),
    (u"var _encRs=scoreRoll(_encV,G.oCards,oppBank,crowsCtx,_encM);",
     u"var _encRs=_scoreRollBest(_encV,G.oCards,oppBank,crowsCtx,_encM);"),
    (u"var _resR=scoreRoll(_resFV,G.oCards,oppBank,crowsCtx,_resFM);",
     u"var _resR=_scoreRollBest(_resFV,G.oCards,oppBank,crowsCtx,_resFM);"),
    (u"var _swR=scoreRoll(_swRoll,G.oCards,0,{crowsLuck:false,crowsLuckRemaining:0},_swMats);",
     u"var _swR=_scoreRollBest(_swRoll,G.oCards,0,{crowsLuck:false,crowsLuckRemaining:0},_swMats);"),
    (u"var _qhR=scoreRoll(_qhFV,G.oCards,oppBank,crowsCtx,_qhFM);",
     u"var _qhR=_scoreRollBest(_qhFV,G.oCards,oppBank,crowsCtx,_qhFM);"),
    (u"var _gbR=scoreRoll(_gbFV,G.oCards,oppBank,crowsCtx,_gbFM);",
     u"var _gbR=_scoreRollBest(_gbFV,G.oCards,oppBank,crowsCtx,_gbFM);"),
    (u"var _stR=scoreRoll(_stFV,G.oCards,oppBank,crowsCtx,_stFM);",
     u"var _stR=_scoreRollBest(_stFV,G.oCards,oppBank,crowsCtx,_stFM);"),
]
for old, new in SITES:
    assert s.count(old) == 1, 'site matched %d: %s' % (s.count(old), old[:52])
    s = s.replace(old, new)

# ── gates on the game file, BEFORE the write ──
assert s != orig, 'nothing changed'
body = re.sub(r'/\*.*?\*/', '', s, flags=re.S)
assert body.count('function _scoreRollBest(') == 1
assert body.count('_scoreRollBest(') == 8, 'definition + 7 sites, got %d' % body.count('_scoreRollBest(')
# NOT ONE rival scoring call may still go through raw scoreRoll
leftover = [m for m in re.findall(r'scoreRoll\([^;]{0,90}', body) if 'G.oCards' in m and '_scoreRollBest' not in m]
assert not leftover, 'rival call sites still on raw scoreRoll: %r' % leftover[:3]
# the player's path is untouched - scoreSelection still does its own wild pass
assert body.count('function scoreSelection(') == 1
assert body.count('_noWild:true') == 2, 'scoreSelection keeps its own, plus the new one'
# and the rest of the file is where it was
assert body.count("famCommitBonus(_oSel,total,'o')") == 1
assert body.count('function _legalKeeps(') == 1
assert body.count('G._enchArr.splice(') == 4

with io.open(SRC, 'w', encoding='utf-8', newline='') as f:
    f.write(s)

# ── 3. the SIM, or the before/after cannot see the change ──
with io.open(HARNESS, encoding='utf-8') as f:
    h = f.read()
horig = h
HOLD = u"var r=scoreRoll(fV,G.oCards||[],bank,G.crowsLuckCtx||{},fM);"
assert h.count(HOLD) == 1, 'sim rival site matched %d' % h.count(HOLD)
h = h.replace(HOLD, u"""/* P489: the SIM has its own copy of the rival's scoring, so leaving it on
       raw scoreRoll would make this harness blind to the very change it is
       being used to measure. */
    var r=(typeof _scoreRollBest==='function'?_scoreRollBest:scoreRoll)(fV,G.oCards||[],bank,G.crowsLuckCtx||{},fM);""")
assert h != horig
assert h.count('_scoreRollBest') == 2
with io.open(HARNESS, 'w', encoding='utf-8', newline='') as f:
    f.write(h)

print('P489 applied: 7 game sites + the sim now score the rival wild as an option')
