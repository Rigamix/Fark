/* P877 - the per-spot refusal, driven on the predicates and the split.
 *
 * The claim has two halves and BOTH need a control: an occupying enchant on a
 * taken spot must be refused, and everything else must NOT be. A refusal that
 * fires on everything would pass a one-sided test.
 */
if(typeof _splitIcons!=='function'||typeof _iconRefused!=='function')return {err:'P877 not present'};
_getS();
const realG=(typeof G!=='undefined')?G:null;
G={oppTurnCount:0,pool:[]};

/* a die carrying a live brand on its landed face, at a given lane */
function die(t,lane,face){
  return {lane:lane,val:face,ench:{t:t,face:face},el:null,committed:false};
}
const out={};

/* nothing armed: nothing is refused */
out.cleanTable={
  fog:_iconRefused(die('fog',2,1)),
  snuff:_iconRefused(die('snuff',2,5)),
  tithe:_iconRefused(die('tithe',2,1)),
};

/* arm a FOG on lane 2 the way the game does */
_lmArm('_fog',2,1,null);
out.afterFogOnLane2={
  snuffSameLane:_iconRefused(die('snuff',2,5)),   /* the ruling: refused */
  snareSameLane:_iconRefused(die('snare',2,1)),   /* refused */
  snuffOtherLane:_iconRefused(die('snuff',4,5)),  /* free spot: allowed */
  titheSameLane:_iconRefused(die('tithe',2,1)),   /* non-occupying: never refused */
  wardSameLane:_iconRefused(die('ward',2,1)),
  tradeSameLane:_iconRefused(die('trade',2,5)),
  breakSameLane:_iconRefused(die('break',2,1)),
};

/* once the mark has affected the opponent, the spot frees up. P879: that is
   _lmSpend now - the fog above is armed with a single attempt, so spending it
   is what ends it, and _lmRetire no longer exists. */
_lmSpend('_fog');
out.afterRetire={snuffSameLane:_iconRefused(die('snuff',2,5))};

/* THE SPLIT: a refused brand must leave `icons` and join `rest`, so it scores */
_lmArm('_fog',2,1,null);
const okDie=die('snuff',4,5), noDie=die('snuff',2,5);
/* _dieIsIcon needs the brand live and unspent; G._castEnch drives _brandSpent */
G._castEnch=[];
const sp=_splitIcons([okDie,noDie]);
out.split={
  icons:sp.icons.length,
  rest:sp.rest.length,
  refused:sp.refused.length,
  refusedIsTheTakenLane:sp.refused.length===1&&sp.refused[0]===noDie,
  refusedAlsoInRest:sp.rest.indexOf(noDie)>=0,
  allowedStayedAnIcon:sp.icons.indexOf(okDie)>=0,
};
/* and the handler refuses it too, without firing anything */
let fired=0;
const realFire=window.ENCH_ICONS&&ENCH_ICONS.snuff&&ENCH_ICONS.snuff.fire;
if(realFire)ENCH_ICONS.snuff.fire=function(){fired++;};
try{_iconFire(noDie,'p');}catch(e){out.fireThrew=e.message;}
try{_iconFire(okDie,'p');}catch(e){}
if(realFire)ENCH_ICONS.snuff.fire=realFire;
out.handler={firesForAllowedOnly:fired===1};

/* P878 (brief 3.6): THE RULE IS IN THE CANONICAL PREDICATE NOW, so every one
   of _dieIsIcon's twelve readers gets it. The named divergence: _markLoneCast
   built its list from _dieIsIcon and would mark a refused brand "will cast" on
   a die that then scored 100 - a visual promising an effect that cannot
   happen. Asserted directly on the predicate rather than on the marker, since
   the marker is what reads it. */
/* FRESH DICE. The first version reused okDie/noDie - but the probe has by
   then called _iconFire on them, which pushes their brand into G._castEnch
   and makes _brandSpent true, so `allowedIsBoth` was false for a completely
   correct reason. The assertion was measuring after a change it had caused. */
const pFree=die('snuff',4,5), pTaken=die('snuff',2,5);
out.predicate={
  refusedIsLiveButNotAnIcon: _iconLive(pTaken)===true&&_dieIsIcon(pTaken)===false,
  allowedIsBoth:             _iconLive(pFree)===true&&_dieIsIcon(pFree)===true,
};
if(realG)G=realG;
out.VERDICT={
  refusalLivesInTheCanonicalPredicate: out.predicate.refusedIsLiveButNotAnIcon===true
                                       &&out.predicate.allowedIsBoth===true,
  nothingRefusedOnACleanTable: !out.cleanTable.fog&&!out.cleanTable.snuff&&!out.cleanTable.tithe,
  occupyingRefusedOnATakenSpot: out.afterFogOnLane2.snuffSameLane===true&&out.afterFogOnLane2.snareSameLane===true,
  occupyingAllowedElsewhere:    out.afterFogOnLane2.snuffOtherLane===false,
  nonOccupyingNeverRefused:     !out.afterFogOnLane2.titheSameLane&&!out.afterFogOnLane2.wardSameLane
                                &&!out.afterFogOnLane2.tradeSameLane&&!out.afterFogOnLane2.breakSameLane,
  spotFreesOnceItHasFired:      out.afterRetire.snuffSameLane===false,
  refusedBrandScoresInstead:    out.split.refusedAlsoInRest===true&&out.split.refusedIsTheTakenLane===true,
  allowedBrandStillWithheld:    out.split.allowedStayedAnIcon===true,
  handlerFiresOnlyTheAllowed:   out.handler.firesForAllowedOnly===true,
};
out.PASS=Object.keys(out.VERDICT).every(k=>out.VERDICT[k]===true);
return out;
