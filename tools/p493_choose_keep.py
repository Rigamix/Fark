# -*- coding: utf-8 -*-
u"""P493 - the six persona keep policies. Pure function, not wired yet.

RULED: build the six, with straights corrected.

Every policy answers one question, because the shape of the candidate set makes
it the only question: the maximal keep is always the full set of scoring dice
and it is unique (measured, 852 bone rolls), so choosing is always choosing to
SCORE LESS NOW in exchange for more dice left live. There is no free variation.

  hoard      takes the maximal. What used[] already did.
  aggro      leaves the MOST dice live; points break the tie.
  straights  CORRECTED - protects a secured five, pushes only the remainder.
  triples    leaves dice live when that preserves a triple, not in general.
  ones       maximal, but never empties the hand.
  combo      NOT GUESSED - takes the maximal until its number is measured.

THE STRAIGHTS CORRECTION, and it changed the policy rather than its reasoning.
The spec said "a partial straight is worth exactly nothing until it's
six-for-six... so gamble hardest for completion". Measured: 12345 pays 500,
23456 pays 750, against 1500 for the full six - and _isStraight was already
`_best>=5`. So there IS substantial partial credit and the premise was false.
Ruled: bank at five MORE readily, gamble the last die only when the five is
already secured. Protect what is worth something, push only the remainder -
closer to triples than to blind aggression.

COMBO IS DELIBERATELY LEFT ALONE. It is meant to weigh points against an
estimated value per die left live, and that number has not been measured.
Reasoning it into a placeholder now would mean re-deriving it properly later,
so it takes the maximal keep and is flagged, not faked.

NO FALLBACK TO aggro WHEN A SHAPE IS ABSENT. If a straights persona has no
five-run available, or a triples persona no triple, they take the MAXIMAL keep
rather than the most-dice-live one - "protect what is already worth something"
is the rule, and blanket risk-taking is aggro's identity, not theirs.

NOT WIRED. `total` currently comes from scoreRoll and is then modified by snare
and the disruption cards before the keep loop reads `used`; routing the keep
through a chosen candidate has to reconcile with that, and doing it in the same
patch as six new policies would make any difficulty delta unattributable. This
lands the policies testable and inert; the wiring is its own change.
"""
import io, os, re

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   'fark_proto.html')
with io.open(SRC, encoding='utf-8') as f:
    s = f.read()
orig = s

ANCH = u"function _legalKeeps(free,actor,locked){"
assert s.count(ANCH) == 1, 'anchor matched %d' % s.count(ANCH)

s = s.replace(ANCH, u"""/* _npcChooseKeep - which legal keep does this persona take?
   `keeps` arrives from _legalKeeps sorted by points, highest first, so the
   maximal keep is always keeps[0].

   Every policy is an answer to one question, because the candidate set makes it
   the only question: the maximal keep is always the full set of scoring dice
   and it is unique, so choosing is always choosing to SCORE LESS NOW for more
   dice left live. Nothing here can pick a worthless keep - scoreSelection
   rejects any selection holding a non-scoring die, so every candidate scores. */
function _npcChooseKeep(keeps,rung){
  if(!keeps||!keeps.length)return null;
  var key=(typeof _npcPersonaKey==='function')
    ? _npcPersonaKey(rung||(typeof G!=='undefined'&&G?G.rung:null)) : 'ones';
  var c=keeps.slice(),pick;

  if(key==='aggro'){
    /* minimise what is locked in, maximise reroll volume. Points break ties. */
    pick=c.sort(function(a,b){return (b.left-a.left)||(b.pts-a.pts);})[0];

  }else if(key==='straights'){
    /* CORRECTED. A five-run is NOT worthless - 12345 pays 500, 23456 pays 750
       against 1500 for the full six. So secure the run first, take points
       second, and push only the remainder. When no five-run is available this
       takes the MAXIMAL keep rather than aggro's: protecting what is already
       worth something is the rule, and blanket risk is aggro's identity. */
    var _fiveish=c.filter(function(k){return k.runLen>=5;});
    pick=_fiveish.length
      ? _fiveish.sort(function(a,b){return (b.pts-a.pts)||(b.left-a.left);})[0]
      : c[0];

  }else if(key==='triples'){
    /* leaves dice live specifically where that keeps a triple alive, rather
       than in general. No triple available - take the maximal. */
    var _trip=c.filter(function(k){return k.isTriple;});
    pick=_trip.length
      ? _trip.sort(function(a,b){return (b.left-a.left)||(b.pts-a.pts);})[0]
      : c[0];

  }else if(key==='ones'){
    /* reliable, but never all-in: if the maximal keep empties the hand, drop to
       the best keep that still leaves a die to roll. */
    pick=c[0];
    if(pick&&pick.left===0){
      var _live=c.filter(function(k){return k.left>=1;});
      if(_live.length)pick=_live[0];/* already points-sorted */
    }

  }else{
    /* hoard takes everything scoring and protects it - which is what used[]
       already did.
       combo lands here TOO, deliberately: it is meant to weigh points against
       an estimated value per die left live, and that number has not been
       measured. A placeholder would only have to be re-derived properly later,
       so it holds at maximal until the measurement exists. */
    pick=c[0];
  }
  return pick||keeps[0];
}

""" + ANCH)

# ── gates, BEFORE the write ──
assert s != orig, 'nothing changed'
body = re.sub(r'/\*.*?\*/', '', s, flags=re.S)
assert body.count('function _npcChooseKeep(') == 1
# every persona the table defines must be reachable in the code, not just named
for k in ['aggro', 'straights', 'triples', 'ones']:
    assert ("key==='" + k + "'") in body, '%s has no branch' % k
# combo and hoard share the maximal branch on purpose - assert neither got its
# own invented rule
assert "key==='combo'" not in body, 'combo must not have been given a rule'
assert "key==='hoard'" not in body, 'hoard is the default maximal branch'
assert body.count('_npcPersonaKey(') >= 2  # its own definition, existing callers, plus mine
# straights must key off runLen, which is what P492 added - not a boolean
assert 'k.runLen>=5' in body, 'the corrected straights rule is not using runLen'
# NOT WIRED
assert body.count('_npcChooseKeep(') == 1, 'must be uncalled; got %d' % body.count('_npcChooseKeep(')
assert body.count('_legalKeeps(') == 1, 'still uncalled'
# earlier work intact
assert body.count('function _handShape(') == 1
assert body.count('_scoreRollBest(') == 8
assert body.count('used.splice(_fogCut,0,false)') == 1

with io.open(SRC, 'w', encoding='utf-8', newline='') as f:
    f.write(s)
print('P493 applied: six policies, combo left unguessed, nothing wired')
