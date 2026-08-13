# -*- coding: utf-8 -*-
"""P691: three defects from the re-derivation pass - D25, D10(b), D6(a).

Nine investigators re-derived the open dice-lane list against the current
build. Five entries were already closed (D3/P557, D7/P556, D11, D15/P561,
D23b/P343-4), D19's ruling was made and implemented long ago (P520), and
three things remained real. This patch closes them.

── D25: the player's Blessed Confiscation still pushed a seventh seat ──
The rival's side was fixed by P522 ("A SWAP, NOT A SEVENTH SEAT"); the
player's copy kept the exact removed shape - matchDice.push(stolen) - and the
re-derivation DROVE it: matchDice 6->7 while _enchArr stayed 6 (the parallel-
array desync), numDice 7 next turn. The entry's "unreachable" mitigation is
stale since P615 revived the player hand; safety rested on nothing granting
the card. Now it is P522's own swap, mirrored: the stolen die replaces the
player's WORST seat, and only if it is actually an upgrade - and the
displaced die's brand leaves with it, because {mat,ench} travel together and
the stolen die arrives bare.

── D10(b): _ftDead retires dice by MATERIAL string ──
Driven: stash ['jade','jade'], ONE dead jade -> Fair Trade refuses both.
The loan record has carried invIdx since P569; both death sites now push an
{i,m} record and the picker filters by INDEX. Legacy material-string entries
(from a pre-fix save) still match by material - the filter tolerates both
shapes, because a resume must not invalidate an old snapshot. The famLog
lines read the loan record's own fields and are untouched. The mid-run
stash splices the picker's comment warns about cannot interleave: _ftDead is
match-scoped, the splices are shop-scoped.

── D6(a): Preserve benches the wrong SEAT ──
The amber holds a die but not its lane, so the restore turn deals a fresh die
into the preserved die's own seat and the lane budget runs out on the highest
lane instead - the wrong die sits out. Now: the keep record carries each
die's lane (it already carries val/mat/ench - the identity that travels),
Preserve captures the found die's lane, _removeDieAt maintains it exactly the
way it maintains G._fairTrade.lane one block above, and the restore stashes
it as G._pvLane so the deal walk marks that seat occupied. The stash rides
the same famState snapshot the preserve record rides.
"""
import io, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'fark_proto.html')
s = io.open(P, encoding='utf-8', newline='').read()
n = 0


def sub(old, new, label):
    global s, n
    c = s.count(old)
    if c != 1:
        sys.exit('ANCHOR x%d (need 1) for %s:\n  %r' % (c, label, old[:130]))
    s = s.replace(old, new)
    n += 1
    print('  ok  %s' % label)


# ── D25 ─────────────────────────────────────────────────────────────────
sub(u"  var stolen=G.matchOppDice[oBestIdx];\n"
    u"  G.matchOppDice.splice(oBestIdx,1);\n"
    u"  G.matchDice.push(stolen);\n"
    u"  setStatusMsg('BLESSED CONFISCATION: TOOK '+stolen.toUpperCase(),'gold');",
    u"  var stolen=G.matchOppDice[oBestIdx];\n"
    u"  G.matchOppDice.splice(oBestIdx,1);\n"
    u"  /* P691 (D25): A SWAP, NOT A SEVENTH SEAT - P522's fix, mirrored to the\n"
    u"     player's copy it never reached. The push made matchDice seven long\n"
    u"     while _enchArr stayed six (driven: enchDesynced true), and the seventh\n"
    u"     seat is never dealt. The stolen die replaces the player's WORST seat,\n"
    u"     and only if it is actually an upgrade - the player already gained by\n"
    u"     stripping the rival either way. The displaced die's brand leaves with\n"
    u"     it: {mat,ench} travel together, and the stolen die arrives bare. */\n"
    u"  var _bcW=0;G.matchDice.forEach(function(m,i){if(dieRank(m)<dieRank(G.matchDice[_bcW]))_bcW=i;});\n"
    u"  if(dieRank(stolen)>dieRank(G.matchDice[_bcW])){\n"
    u"    G.matchDice[_bcW]=stolen;\n"
    u"    if(G._enchArr)G._enchArr[_bcW]=null;\n"
    u"    setStatusMsg('BLESSED CONFISCATION: '+stolen.toUpperCase()+' REPLACES YOUR WORST','gold');\n"
    u"  }else{\n"
    u"    setStatusMsg('BLESSED CONFISCATION: TOOK THEIR '+stolen.toUpperCase(),'gold');\n"
    u"  }",
    'P691 D25 the swap')

# ── D10(b) ──────────────────────────────────────────────────────────────
sub(u"      G._ftDead=(G._ftDead||[]).concat([_ftB.borrowed]);",
    u"      /* P691 (D10b): an {i,m} record, not a material string - one dead jade\n"
    u"         used to retire every jade in the stash (driven). m stays for the\n"
    u"         log and for legacy-shape tolerance. */\n"
    u"      G._ftDead=(G._ftDead||[]).concat([(typeof _ftB.invIdx==='number')?{i:_ftB.invIdx,m:_ftB.borrowed}:_ftB.borrowed]);",
    'P691 D10b break-path record')

sub(u"      G._ftDead=(G._ftDead||[]).concat([_ft.borrowed]);",
    u"      G._ftDead=(G._ftDead||[]).concat([(typeof _ft.invIdx==='number')?{i:_ft.invIdx,m:_ft.borrowed}:_ft.borrowed]);/* P691 (D10b) */",
    'P691 D10b expiry-path record')

sub(u"    var _ftIdx=[];\n"
    u"    (S.run.diceInv||[]).forEach(function(_d,_i){\n"
    u"      if((G._ftDead||[]).indexOf(_d)<0)_ftIdx.push(_i);});",
    u"    var _ftIdx=[];\n"
    u"    /* P691 (D10b): dead by INDEX. A pre-fix snapshot can still hold bare\n"
    u"       material strings - those keep the old (conservative) material match\n"
    u"       rather than being invalidated by a resume. */\n"
    u"    (S.run.diceInv||[]).forEach(function(_d,_i){\n"
    u"      var _dead=(G._ftDead||[]).some(function(_r){\n"
    u"        return (_r&&typeof _r==='object')?(_r.i===_i):(_r===_d);\n"
    u"      });\n"
    u"      if(!_dead)_ftIdx.push(_i);});",
    'P691 D10b the index filter')

# ── D6(a) ───────────────────────────────────────────────────────────────
sub(u"dice:selDice.map(function(dd){return{val:dd.val,mat:dd.mat,ench:dd.ench||null};})",
    u"dice:selDice.map(function(dd){return{val:dd.val,mat:dd.mat,ench:dd.ench||null,lane:(typeof dd.lane==='number')?dd.lane:null};})/* P691 (D6a): the lane is part of the identity */",
    'P691 D6a keep records the lane')

sub(u"    G._famPreserve={val:found,mat:foundMat,ench:foundEnch||null,pts:found===1?100:50,crack:(inst.tier===3?100:0)};/* P559 */",
    u"    G._famPreserve={val:found,mat:foundMat,ench:foundEnch||null,lane:(typeof foundLane==='number')?foundLane:null,pts:found===1?100:50,crack:(inst.tier===3?100:0)};/* P559 + P691 (D6a): the SEAT is preserved too */",
    'P691 D6a preserve records the lane')

sub(u"  try{\n"
    u"    var ft=G._fairTrade;\n"
    u"    if(ft){\n"
    u"      /* the ft.lane===lane case is handled above, where the lane is kept */\n"
    u"      if(ft.lane>lane)ft.lane--;\n"
    u"    }\n"
    u"  }catch(e){}",
    u"  try{\n"
    u"    var ft=G._fairTrade;\n"
    u"    if(ft){\n"
    u"      /* the ft.lane===lane case is handled above, where the lane is kept */\n"
    u"      if(ft.lane>lane)ft.lane--;\n"
    u"    }\n"
    u"    /* P691 (D6a): the preserved seat is a lane record in the same sense.\n"
    u"       Above the removed lane it slides down; AT the removed lane the seat\n"
    u"       itself died, so the claim is void and the restore falls back to the\n"
    u"       old free-lane behaviour rather than pointing at a moved seat. */\n"
    u"    var pv=G._famPreserve;\n"
    u"    if(pv&&typeof pv.lane==='number'){\n"
    u"      if(pv.lane===lane)pv.lane=null;\n"
    u"      else if(pv.lane>lane)pv.lane--;\n"
    u"    }\n"
    u"    if(typeof G._pvLane==='number'){\n"
    u"      if(G._pvLane===lane)G._pvLane=null;\n"
    u"      else if(G._pvLane>lane)G._pvLane--;\n"
    u"    }\n"
    u"  }catch(e){}",
    'P691 D6a lane maintenance')

sub(u"    G.kept=[{vals:[_fp.val],mat:_fp.mat||'bone',pts:_fp.pts+(_fp.crack||0),\n"
    u"             dice:[{val:_fp.val,mat:_fp.mat||'bone',ench:_fp.ench||null}]}];",
    u"    /* P691 (D6a): stash the preserved SEAT for this turn's deal - the record\n"
    u"       itself is consumed below, and the deal walk runs later in handleRoll. */\n"
    u"    G._pvLane=(typeof _fp.lane==='number')?_fp.lane:null;\n"
    u"    G.kept=[{vals:[_fp.val],mat:_fp.mat||'bone',pts:_fp.pts+(_fp.crack||0),\n"
    u"             dice:[{val:_fp.val,mat:_fp.mat||'bone',ench:_fp.ench||null,lane:(typeof _fp.lane==='number')?_fp.lane:null}]}];",
    'P691 D6a restore stashes the seat')

sub(u"      var _occLane={};(G.pool||[]).forEach(function(_d){_occLane[_d.lane]=1;});",
    u"      var _occLane={};(G.pool||[]).forEach(function(_d){_occLane[_d.lane]=1;});\n"
    u"      /* P691 (D6a): the preserved die's own seat is occupied by the die in\n"
    u"         amber - without this the deal put a fresh die into that seat and\n"
    u"         the lane budget ran out on the HIGHEST lane instead, so the wrong\n"
    u"         die (a warded one, in the recorded repro) sat out the turn. */\n"
    u"      if(typeof G._pvLane==='number')_occLane[G._pvLane]=1;",
    'P691 D6a the deal honours the seat')

sub(u"  if(typeof famFire==='function'&&G){famFire('turnStart',{actor:'p'});try{famRenderRow();}catch(e){}}",
    u"  if(typeof famFire==='function'&&G){famFire('turnStart',{actor:'p'});try{famRenderRow();}catch(e){}}\n"
    u"  G._pvLane=null;/* P691 (D6a): the seat stash is one turn's fact - the NEXT\n"
    u"     turn's preserve (if any) writes its own on restore, after this clear */",
    'P691 D6a the stash is turn-scoped')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('\n%d edits' % n)
