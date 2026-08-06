# -*- coding: utf-8 -*-
u"""P492 - candidates carry their hand SHAPE, from one derivation. Machinery only.

RULED: build the six persona keep policies. Two of them - straights and triples -
need a candidate's hand TYPE, and _legalKeeps returns only {sel,pts,icons,left}.

DO NOT WRITE A SECOND DERIVATION. famCommitBonus already computes isTriple and
isStraight from a set of dice, and its own comment says why that matters:
"two derivations of 'is this a straight' would be free to drift, which is what
five of tonight's findings turned out to be". So the derivation is EXTRACTED
into _handShape and famCommitBonus is changed to call it - there is one copy
afterwards, not two.

runLen comes out too, because the CORRECTED straights policy needs it. The
original spec assumed a partial straight was worthless until six; measured,
12345 pays 500 and 23456 pays 750 against 1500 for the full run, and
_isStraight is already `_best>=5`. So straights protects a secured five and
gambles only the sixth - which requires knowing the run length, not just a
boolean.

ALSO FIXES THE SEAT BUG I SHIPPED IN P481. _legalKeeps computed
    locked = G.kept.reduce(...)
the PLAYER's tray, for both seats. `locked` is passed to scoreSelection as the
running bank, which threshold-sensitive cards read. The rival's equivalent is
oppBank - a local in runOppTurn, not on G, which is why it has to become a
parameter rather than something _legalKeeps can look up. Unverifiable until now
because nothing called it with 'o'; the wiring in P493 is the call site that
makes it testable.

INERT BY DESIGN: nothing in the game calls _legalKeeps yet. This lands the data
and the fix; P493 lands the behaviour and its measurement.
"""
import io, os, re

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   'fark_proto.html')
with io.open(SRC, encoding='utf-8') as f:
    s = f.read()
orig = s

# ── 1. the single derivation, placed just before _legalKeeps ──
ANCH = u"function _legalKeeps(free,actor){"
assert s.count(ANCH) == 1, '_legalKeeps anchor matched %d' % s.count(ANCH)
s = s.replace(ANCH, u"""/* _handShape - what KIND of hand a set of dice is. ONE derivation.
   Lifted verbatim out of famCommitBonus rather than written again beside it:
   that function's own comment is "two derivations of 'is this a straight'
   would be free to drift, which is what five of tonight's findings turned out
   to be", and adding a second here would have been that exact mistake made
   knowingly. famCommitBonus now calls this, so there is one copy in the file.

   runLen is returned as well as the boolean, because the straights persona
   protects a SECURED five-run and gambles only the sixth die - a measured
   correction: 12345 pays 500 and 23456 pays 750 against 1500 for the full six,
   so a partial straight is not worthless and should not be thrown at. */
function _handShape(selD){
  var counts={};(selD||[]).forEach(function(d){counts[d.val]=(counts[d.val]||0)+1;});
  var isTriple=Object.keys(counts).some(function(v){return counts[v]>=3;});
  var uv=Object.keys(counts).map(Number).sort(function(a,b){return a-b;});
  var run=1,best=uv.length?1:0;
  for(var i=1;i<uv.length;i++){run=(uv[i]===uv[i-1]+1)?run+1:1;if(run>best)best=run;}
  return{counts:counts,isTriple:isTriple,runLen:best,isStraight:best>=5};
}

""" + ANCH)

# ── 2. famCommitBonus stops computing its own ──
OLD_DERIV = u"""  var _counts={};selD.forEach(function(d){_counts[d.val]=(_counts[d.val]||0)+1;});
  var _isTriple=Object.keys(_counts).some(function(v){return _counts[v]>=3;});
  var _uv=Object.keys(_counts).map(Number).sort(function(a,b){return a-b;});
  var _run=1,_best=1;for(var _i=1;_i<_uv.length;_i++){_run=(_uv[_i]===_uv[_i-1]+1)?_run+1:1;if(_run>_best)_best=_run;}
  var _isStraight=_best>=5;"""
assert s.count(OLD_DERIV) == 1, 'famCommitBonus derivation matched %d' % s.count(OLD_DERIV)
s = s.replace(OLD_DERIV, u"""  /* P492: one derivation, shared with _legalKeeps. This block used to compute
     it inline; the candidates the NPC chooses among need the same answer, and
     two copies of it is the drift this function's own comment warns about. */
  var _shape=_handShape(selD);
  var _counts=_shape.counts,_isTriple=_shape.isTriple,_isStraight=_shape.isStraight;""")

# ── 3. _legalKeeps: seat-correct `locked`, and shape on every candidate ──
OLD_LOCK = u"""function _legalKeeps(free,actor){
  var out=[];
  var n=(free||[]).length; if(!n) return out;
  var _lkO=(actor==='o');
  var locked=(G&&G.kept)?G.kept.reduce(function(a,k){return a+(k.pts||0);},0):0;"""
assert s.count(OLD_LOCK) == 1, '_legalKeeps head matched %d' % s.count(OLD_LOCK)
s = s.replace(OLD_LOCK, u"""function _legalKeeps(free,actor,locked){
  var out=[];
  var n=(free||[]).length; if(!n) return out;
  var _lkO=(actor==='o');
  /* P492 - SEAT BUG FROM P481. This read G.kept, the PLAYER's tray, for both
     seats. `locked` is handed to scoreSelection as the running bank and
     threshold-sensitive cards read it, so a rival candidate was being scored
     against the player's points. The rival's equivalent is oppBank, a LOCAL in
     runOppTurn rather than state on G - hence a parameter. Omitted, the player
     keeps its old behaviour and the rival gets 0 rather than someone else's
     bank. The P481 probe reported rivalSeatWorks:true throughout, which was
     true for its own definition - "returns candidates without throwing". */
  if(locked==null)locked=_lkO?0:((G&&G.kept)?G.kept.reduce(function(a,k){return a+(k.pts||0);},0):0);""")

OLD_PUSH = u"    out.push({sel:sel,pts:pts,icons:(sp.icons||[]).length,left:n-sel.length});"
assert s.count(OLD_PUSH) == 1, 'candidate push matched %d' % s.count(OLD_PUSH)
s = s.replace(OLD_PUSH, u"""    /* P492: shape travels with the candidate so a persona can ask what KIND of
       hand it is, not just what it scores. Same derivation famCommitBonus uses. */
    var _sh=_handShape(sel);
    out.push({sel:sel,pts:pts,icons:(sp.icons||[]).length,left:n-sel.length,
              isTriple:_sh.isTriple,isStraight:_sh.isStraight,runLen:_sh.runLen});""")

# ── gates, BEFORE the write ──
assert s != orig, 'nothing changed'
body = re.sub(r'/\*.*?\*/', '', s, flags=re.S)
assert body.count('function _handShape(') == 1, 'exactly one derivation'
assert body.count('_handShape(') == 3, 'defined once, used by famCommitBonus and _legalKeeps'
# the OLD inline derivation must be gone from famCommitBonus - that is the point
assert 'var _isStraight=_best>=5;' not in body, 'the second derivation survived'
assert body.count('function _legalKeeps(free,actor,locked)') == 1
assert body.count('runLen:_sh.runLen') == 1
# famCommitBonus still consumes the same names, so its payload is unchanged
assert body.count('isTriple:_isTriple,isStraight:_isStraight') == 1
# still inert - nothing calls it
assert body.count('_legalKeeps(') == 1, 'must still be uncalled; got %d' % body.count('_legalKeeps(')
# P489/P491 intact
assert body.count('_scoreRollBest(') == 8
assert body.count('used.splice(_fogCut,0,false)') == 1

with io.open(SRC, 'w', encoding='utf-8', newline='') as f:
    f.write(s)
print('P492 applied: one hand-shape derivation, shape on candidates, locked fixed')
