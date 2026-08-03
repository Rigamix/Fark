# -*- coding: utf-8 -*-
"""P445 - the `commit` hook: the eighth seam, and the one four cards needed.

WHY A NEW HOOK RATHER THAN A MIGRATION. Reading the nine unexplained sites by
hand produced a category no classifier had a bucket for: three cards have halves
living off the bus not because anyone forgot, but because THE BUS HAS NO HOOK
FOR THE MOMENT THEY FIRE. short_fuse doubles at commit; fools_gold_f rerolls on
a dead roll; ill_omen resolves on the rival's turn. None of the seven hooks
reaches those.

`commit` is the first of the three, and it is worth doing first because it
unblocks FOUR cards at once: short_fuse's x2 plus bloom, cultivate and
vanguard_f - three of the five group-2 cards waiting to be migrated, all three
of which already live in famCommitBonus.

ORDER IS THE WHOLE DESIGN PROBLEM, and it is not hypothetical. Today the
function multiplies for short_fuse FIRST and then adds bloom, cultivate and
vanguard: (pts*2)+adds. famFire iterates equipped cards in EQUIP ORDER and
offers only ev.add(), so a naive migration computes ((pts+bloom)*2) whenever
short_fuse happens to sit later in the loadout. Same cards, same tiers, a
different score depending on draft order, and no error anywhere.

So famFire gains ev.mul() beside ev.add(), and the commit caller applies
`pts*mul + add`. That reproduces today's arithmetic EXACTLY.

CORRECTION, TESTED RATHER THAN ASSUMED: an earlier draft of this docstring said
the migration REMOVES an order dependence latent in the hand-written version.
That is false, and measuring it is what showed it. The old function called
famInst('short_fuse'), famInst('bloom'), ... in a FIXED WRITTEN ORDER - the
order lived in the function body, not in the loadout - so it was already
order-independent by construction. Both files score [short_fuse,bloom] and
[bloom,short_fuse] at 2300.

The accurate claim is narrower and still worth the work: the order dependence
would have been INTRODUCED by migrating onto an add-only bus, because famFire
iterates G.pF in equip order. ev.mul prevents a regression; it does not fix an
existing bug. Overstating that would have been the Ward mistake again - naming
a defect in code that was already correct.

WHAT STAYS IN famCommitBonus, deliberately: the relic effects (finnicks_palm,
whispers_fang). They are dice MATERIALS, not equipped family cards; famFire
walks G.pF and would never see them. Moving them would need a second mechanism
and they are not what this hook is for.

VERIFIED BY FIXTURE, not by reading. apv_commit_hook drives 96 cases - every
subset of the four cards, three roll shapes, two roll counts - and the digest
must be identical before and after. Baseline before this patch: 300798530.
"""
import io, os, re

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   'fark_proto.html')
with io.open(SRC, encoding='utf-8') as f:
    s = f.read()
orig = s

# ── 1. famFire learns to multiply ──
OLD_FIRE = u"  ev=ev||{};ev._delta=0;ev.add=function(n){ev._delta+=n;};"
assert s.count(OLD_FIRE) == 1, 'famFire header matched %d' % s.count(OLD_FIRE)
s = s.replace(OLD_FIRE,
  u"""  /* ADD AND MUL ARE SEPARATE ACCUMULATORS because they do not commute, and
     the loop order is EQUIP order - which is draft order, which is arbitrary.
     A hook that could only add forced every caller to fold multiplication into
     the iteration, making the result depend on where a card sat in the
     loadout. Collect both, let the caller apply `base*mul + delta`, and the
     answer stops caring about order. _mul starts at 1 so every existing hook
     is unaffected: nothing calls mul() yet. */
  ev=ev||{};ev._delta=0;ev._mul=1;
  ev.add=function(n){ev._delta+=n;};
  ev.mul=function(n){ev._mul*=n;};""")

# ── 2. the four card bodies become CFX commit hooks ──
ANCHOR = u"CFX.short_fuse={\n  turnStart:function(ev){if(ev.owner==='p')ev.me.state.lit=false;},"
assert s.count(ANCHOR) == 1, 'short_fuse CFX anchor matched %d' % s.count(ANCHOR)
s = s.replace(ANCHOR,
  u"""/* == THE `commit` HOOK ================================================
   Fires when dice are COMMITTED - after a roll is kept, before it is banked.
   The eighth hook, and the first that needed ordering: ev.mul() multiplies,
   ev.add() adds, and famCommitBonus applies pts*mul + add so the result does
   not depend on which order the cards were drafted in.

   ev carries what the commit moment knows and a card cannot recompute:
     ev.sel        the dice being committed
     ev.isTriple   three or more of a kind among them
     ev.isStraight five in a run
     ev.jade       the jade dice among them (jade cards all gate on this)
     ev.hitFirst   the row's first die is in the selection
     ev.hitLast    the row's last die is in the selection

   NOT here: the relic commit effects (finnicks_palm, whispers_fang). Those are
   dice MATERIALS, not equipped cards - famFire walks G.pF and would never see
   them. They stay in famCommitBonus. */
CFX.short_fuse={
  /* THE ONLY MULTIPLIER IN THE GAME so far, and the reason ev.mul exists. */
  commit:function(ev){if(!_fxMine(ev)||(G.turnRollCount||0)<3)return;
    ev.mul(2);ev.me.state.lit=true;_famPop('x2 SHORT FUSE');},
  turnStart:function(ev){if(ev.owner==='p')ev.me.state.lit=false;},""")

# short_fuse's old body
OLD_SF = u"""  if((inst=famInst('short_fuse'))&&(G.turnRollCount||0)>=3){
    pts*=2;inst.state.lit=true;_famPop('x2 SHORT FUSE');
  }
"""
assert s.count(OLD_SF) == 1, 'short_fuse body matched %d' % s.count(OLD_SF)
s = s.replace(OLD_SF, u"")

OLD_BLOOM = u"""  if((inst=famInst('bloom'))&&(_isTriple||_isStraight)&&_jadeDice.length){
    var P=famDef('bloom').p[inst.tier-1];pts+=P;_famPop('+'+P+' BLOOM');
    G._featBloom=(G._featBloom||0)+1;/* FULL BLOOM */
  }
"""
assert s.count(OLD_BLOOM) == 1, 'bloom body matched %d' % s.count(OLD_BLOOM)
s = s.replace(OLD_BLOOM, u"")

OLD_CULT = u"""  if((inst=famInst('cultivate'))&&(_isTriple||_isStraight)&&_jadeDice.length){
    /* the jade wild fired: those dice grow, and their growth pays now */
    var grown=0;
    _jadeDice.forEach(function(d){grown+=(d._cult||0);d._cult=(d._cult||0)+50;});
    if(grown>0){pts+=grown;_famPop('+'+grown+' CULTIVATE');}
    else _famPop('CULTIVATE GROWS');
  }
"""
assert s.count(OLD_CULT) == 1, 'cultivate body matched %d' % s.count(OLD_CULT)
s = s.replace(OLD_CULT, u"")

OLD_VAN = u"""  if((inst=famInst('vanguard_f'))){
    /* collapsed positional card: I first spot; II both ends; III adds
       the full-bookends payoff when both ends score */
    var vb=0,t=inst.tier;
    if(t===1){if(hitFirst)vb=200;}
    else if(t===2){if(hitFirst)vb+=350;if(hitLast)vb+=350;}
    else{if(hitFirst&&hitLast)vb=1200;else if(hitFirst||hitLast)vb=350;}
    if(vb>0){pts+=vb;_famPop('+'+vb+' VANGUARD');}
  }
"""
assert s.count(OLD_VAN) == 1, 'vanguard body matched %d' % s.count(OLD_VAN)
s = s.replace(OLD_VAN, u"")

# the three adders, as CFX entries, appended after short_fuse's block
SF_END = u"""  turnStart:function(ev){if(ev.owner==='p')ev.me.state.lit=false;},"""
assert s.count(SF_END) == 1
s = s.replace(SF_END, SF_END + u"""
  /* the three jade/positional adders that used to sit in famCommitBonus.
     Each keeps its own gate verbatim - they are NOT one condition. */""")

# insert the three entries just before CFX.transmute
TRANS = u"CFX.transmute={"
assert s.count(TRANS) == 1
s = s.replace(TRANS,
  u"""CFX.bloom={
  commit:function(ev){if(!_fxMine(ev)||!(ev.isTriple||ev.isStraight)||!ev.jade.length)return;
    ev.add(ev.P);_famPop('+'+ev.P+' BLOOM');
    G._featBloom=(G._featBloom||0)+1;/* FULL BLOOM */}
};
CFX.cultivate={
  /* the jade wild fired: those dice grow, and their growth pays now. The
     mutation of d._cult is why this cannot be a pure scoring function. */
  commit:function(ev){if(!_fxMine(ev)||!(ev.isTriple||ev.isStraight)||!ev.jade.length)return;
    var grown=0;
    ev.jade.forEach(function(d){grown+=(d._cult||0);d._cult=(d._cult||0)+50;});
    if(grown>0){ev.add(grown);_famPop('+'+grown+' CULTIVATE');}
    else _famPop('CULTIVATE GROWS');}
};
CFX.vanguard_f={
  /* collapsed positional card: I first spot; II both ends; III adds
     the full-bookends payoff when both ends score. Tier-shaped rather than
     ev.P-shaped, so it reads ev.me.tier directly. */
  commit:function(ev){if(!_fxMine(ev))return;
    var vb=0,t=ev.me.tier;
    if(t===1){if(ev.hitFirst)vb=200;}
    else if(t===2){if(ev.hitFirst)vb+=350;if(ev.hitLast)vb+=350;}
    else{if(ev.hitFirst&&ev.hitLast)vb=1200;else if(ev.hitFirst||ev.hitLast)vb=350;}
    if(vb>0){ev.add(vb);_famPop('+'+vb+' VANGUARD');}}
};
CFX.transmute={""")

# ── 3. famCommitBonus fires the hook instead ──
OLD_TAIL = u"""  var first=G.pool[0],last=G.pool[G.pool.length-1];
  var hitFirst=first&&selD.indexOf(first)>=0,hitLast=last&&selD.indexOf(last)>=0;
"""
assert s.count(OLD_TAIL) == 1, 'pool-ends block matched %d' % s.count(OLD_TAIL)
s = s.replace(OLD_TAIL,
  u"""  var first=G.pool[0],last=G.pool[G.pool.length-1];
  var hitFirst=first&&selD.indexOf(first)>=0,hitLast=last&&selD.indexOf(last)>=0;
  /* THE COMMIT HOOK. pts*mul + delta, in that order, which is what the four
     hand-written blocks above used to compute - short_fuse doubled before the
     others added. Applying it here instead of inside the loop is what makes
     the result independent of equip order. */
  var _cev={actor:'p',sel:selD,isTriple:_isTriple,isStraight:_isStraight,
            jade:_jadeDice,hitFirst:hitFirst,hitLast:hitLast};
  var _cadd=famFire('commit',_cev);
  pts=Math.round(pts*(_cev._mul||1))+_cadd;
""")

assert s != orig, 'nothing changed'
# the four bodies must be GONE and the four hooks present
for gone in ("famInst('short_fuse')", "famInst('bloom')",
             "famInst('cultivate')", "famInst('vanguard_f')"):
    assert gone not in s, 'old body survives: %s' % gone
assert s.count('commit:function(ev)') == 4, \
    'commit hooks: %d (want 4)' % s.count('commit:function(ev)')
assert s.count("famFire('commit'") == 1
with io.open(SRC, 'w', encoding='utf-8', newline='') as f:
    f.write(s)
print('P445 applied: commit hook + ev.mul, four cards migrated')
