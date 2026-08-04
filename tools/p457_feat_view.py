# -*- coding: utf-8 -*-
"""P457 - Phase 5: feats get a view they cannot write through.

MEASURED FIRST (feat_purity.py, feat_reads.py):
  * no feat writes game state today - the rule has held on discipline alone
  * the 23 checks read 19 G fields, one S field (S.run), one module global
    (TIERS, read-only data) and no mutating helpers

So this is not a repair. It makes an invariant that is currently true hard to
break later.

THE SHAPE, and why a facade rather than a freeze or a bare proxy. Object.freeze
is SHALLOW - G.matchDice would stay mutable and the guarantee would quietly not
hold for the one field most worth protecting. A proxy over the real G stops
writes but leaves the whole object nameable, so the next feat reaches for
anything. A narrow facade means a check cannot even NAME what it was not given,
which is the guarantee that survives someone writing a new feat without reading
this comment.

Both, in fact: a facade holding exactly the measured fields, behind a proxy
whose set() THROWS. Narrow vocabulary and a loud failure, rather than a silent
no-op that a sloppy-mode assignment would produce.

WHAT THIS DOES NOT CLOSE, and it is 7 of the 23 feats. `S` is a module global,
so a check can reach S.run directly without it being passed - and seven do.
A facade over the ARGUMENT cannot stop that; only moving the checks into a
scope without S would, which is a restructure this phase is not. So `run` is
included in the view as a frozen copy for the feats that want it, and the hole
is named here and asserted against by apv_feat_view rather than left implied.

That gap is exactly what feat_purity said it could not see. It is smaller now -
a direct S.run write is the only route left, where before any helper would do -
but "smaller" is not "closed" and the docs say so.
"""
import io, os

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   'fark_proto.html')
with io.open(SRC, encoding='utf-8') as f:
    s = f.read()
orig = s

ANCHOR = u"const FEATS=["
assert s.count(ANCHOR) == 1, 'FEATS anchor matched %d' % s.count(ANCHOR)
s = s.replace(ANCHOR,
u"""/* == THE FEAT VIEW (Phase 5) ==========================================
   Feats OBSERVE. They must never grant power - and until now that was a rule
   someone had to remember, not one the code enforced. Measured before
   building: across all 23 checks, not one writes game state, so this makes a
   true invariant hard to break rather than repairing a broken one.

   WHAT A CHECK GETS is exactly the fields the 23 were measured to read, behind
   a proxy that THROWS on assignment. Two properties, both deliberate:
     - narrow VOCABULARY: a check cannot name what it was not given, so a new
       feat reaching for G.pPts fails at authoring time, not review time
     - LOUD on write: a sloppy-mode `view.x = 1` would silently no-op against a
       frozen object; this throws, so a violation cannot pass quietly

   NOT Object.freeze(G): freeze is shallow, so G.matchDice - an array, and the
   one field most worth protecting - would stay mutable.

   THE HOLE, NAMED: `S` is a module global. Seven checks read S.run directly
   rather than through their argument, and a facade over the argument cannot
   stop that. `run` is provided here as a frozen copy for them, but a check
   CAN still reach the real S.run and write it. Closing that needs the checks
   moved to a scope without S, which is a restructure, not this patch.
   apv_feat_view asserts the gap is exactly this size and no larger. */
function _featView(G){
  if(!G)return G;
  var v={};
  ['_isBoss','_famBankCount','_famMinBank','_featBloom','_featBusts',
   '_featJade','_featMaxBank','_featMaxDeficit','_featMaxRolls','_featOmenTrue',
   '_featShatterBanked','_featStarChain','_featSticky','_featWardSaves',
   '_forKeeps','_handicap','_sleeve','matchDice','rung'].forEach(function(k){
     var x=G[k];
     /* arrays and objects are copied AND frozen - handing the live one over
        would make the proxy decorative */
     if(Array.isArray(x))x=Object.freeze(x.slice());
     else if(x&&typeof x==='object')x=Object.freeze(Object.assign({},x));
     v[k]=x;
   });
  try{
    v.run=(typeof S!=='undefined'&&S&&S.run)?Object.freeze(Object.assign({},S.run)):null;
  }catch(e){v.run=null;}
  if(typeof Proxy!=='function')return Object.freeze(v);
  return new Proxy(v,{
    set:function(t,k){throw new Error('a feat tried to write '+String(k)+
      ' - feats observe, they do not grant power');},
    deleteProperty:function(t,k){throw new Error('a feat tried to delete '+String(k));}
  });
}
const FEATS=[""")

# the one caller: whatever evaluates check()
OLD_CALL = u"f.check(G)"
n = s.count(OLD_CALL)
assert n >= 1, 'check call site matched %d' % n
s = s.replace(OLD_CALL, u"f.check(_featView(G))")

assert s != orig, 'nothing changed'
assert s.count('function _featView(') == 1
assert s.count('f.check(_featView(G))') == n
print('P457 applied: feat view + proxy; %d check call site(s) routed' % n)
with io.open(SRC, 'w', encoding='utf-8', newline='') as f:
    f.write(s)
