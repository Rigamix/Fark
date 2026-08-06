# -*- coding: utf-8 -*-
u"""P481 - _legalKeeps in the game, seat-aware. Machinery only, no behaviour change.

RULED: build real NPC decision-making. The sizing found the rival already makes
a real SELECTION - it takes the scorer's single maximal answer - and what it
cannot do is CHOOSE between options. Choosing needs options to choose from.

THE REFERENCE IMPLEMENTATION ALREADY EXISTS, in tools/sim_harness.js:
`legalKeeps(free)` walks every subset (1<<n, so 63 at six dice), scores each
with scoreSelection, and returns {sel,pts,icons,left} per legal keep. simTurn
then hands those to `policy.keep` - candidate enumeration and a policy that
chooses among them. That is exactly the architecture the game's NPC lacks, and
it is harness code calling game functions, so it can live in the game.

SEAT-AWARE FROM THE START, because two of its six helpers are player-bound:
`effectiveCards` reads G.pCards and `_bookendsEligible` reads G.pool. The other
four - scoreSelection, _splitIcons, _pCrowsForScore, _dieIsIcon - are pure.
Same shape famCommitBonus needed, and building it seat-blind now would mean
finding that out later.

THIS PATCH DELIBERATELY CHANGES NO BEHAVIOUR. The NPC still ends up with the
maximal keep - the new code picks the candidate with the highest points, which
is what taking the scorer's `used[]` already produced. That is the point: the
machinery lands verifiably inert, and the CHOICE becomes a separate change with
its own before/after. OPEN.md 6 exists because three difficulty changes landed
in one session without being separable; this one will not add a fourth by
accident.
"""
import io, os, re

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   'fark_proto.html')
with io.open(SRC, encoding='utf-8') as f:
    s = f.read()
orig = s

ANCH = u"function famCommitBonus(selD,pts,actor){"
assert s.count(ANCH) == 1, 'anchor matched %d' % s.count(ANCH)

s = s.replace(ANCH, u"""/* _legalKeeps - every legal keep from a set of free dice, scored.
   Ported from tools/sim_harness.js legalKeeps, which has been enumerating
   candidates for the sim's policies all along while the game's NPC took the
   scorer's single maximal answer. 1<<n subsets, so 63 at six dice - cheap.

   SEAT-AWARE: `effectiveCards` reads G.pCards and `_bookendsEligible` reads
   G.pool, so both are resolved from the actor rather than assumed. The other
   helpers it uses are pure.

   Returns [{sel,pts,icons,left}] sorted by points, highest first, so a caller
   that just wants "the best" takes [0] and a caller that wants to CHOOSE has
   the alternatives in hand. */
function _legalKeeps(free,actor){
  var out=[];
  var n=(free||[]).length; if(!n) return out;
  var _lkO=(actor==='o');
  var locked=(G&&G.kept)?G.kept.reduce(function(a,k){return a+(k.pts||0);},0):0;
  var cards=_lkO?(G.oCards||[]):(typeof effectiveCards==='function'?effectiveCards():(G.pCards||[]));
  var row=(_lkO?(G.oppDice||[]):(G.pool||[]));
  for(var m=1;m<(1<<n);m++){
    var sel=[];
    for(var i=0;i<n;i++) if(m&(1<<i)) sel.push(free[i]);
    var sp=(typeof _splitIcons==='function')?_splitIcons(sel):{rest:sel,icons:[]};
    var rest=sp.rest||sel;
    var ctx={};
    try{ ctx=(!_lkO&&typeof _pCrowsForScore==='function')?(_pCrowsForScore()||{}):{}; }catch(e){ ctx={}; }
    try{ if(!_lkO&&typeof _bookendsEligible==='function') ctx._bookendsEligible=_bookendsEligible(sel); }catch(e){}
    var pts=0;
    if(rest.length){
      try{ pts=scoreSelection(rest.map(function(d){return d.val;}),cards,locked,ctx,
             rest.map(function(d){return d.mat;}),
             rest.map(function(d){return d.ench||null;})); }catch(e){ pts=0; }
    }
    if(rest.length===0&&(sp.icons||[]).length) pts=0;
    if(pts<0||(pts===0&&!(sp.icons||[]).length)) continue;
    out.push({sel:sel,pts:pts,icons:(sp.icons||[]).length,left:n-sel.length});
  }
  out.sort(function(a,b){return b.pts-a.pts;});
  return out;
}

""" + ANCH)

assert s != orig
body = re.sub(r'/\*.*?\*/', '', s, flags=re.S)
assert body.count('function _legalKeeps(') == 1
assert 'row=' in body  # seat-aware row resolved
# the helpers it leans on must all still exist
for fn in ['scoreSelection', '_splitIcons', '_bookendsEligible', '_pCrowsForScore']:
    assert ('function ' + fn) in body, '%s missing' % fn
# nothing else touched - this patch adds a function and changes no call site
assert body.count("famCommitBonus(_oSel,total,'o')") == 1
assert body.count('BANK_FX.') == 8 and body.count('_useCap(') == 19
assert body.count('G._enchArr.splice(') == 4

with io.open(SRC, 'w', encoding='utf-8', newline='') as f:
    f.write(s)
print('P481 applied: _legalKeeps added, seat-aware, no call sites changed yet')
