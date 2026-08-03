/* sim_power_f.js — LENS 2, part F: what the run ACTUALLY reaches, and what the
 * power delta looks like against that instead of against a spec.
 *
 *  F1. Re-runs the run loop with brand-level instrumentation: how many brands
 *      a shopper who is TRYING to build the briefed loadout actually holds at
 *      the start of night 8, how many brands get destroyed by a later die
 *      purchase (_stTrade nulls the slot's enchant, no refund), what Tithe
 *      really pays, and whether jade2 (1800g) is ever bought at all.
 *  F2. The power delta measured against the loadout a run REALLY arrives at,
 *      not the spec: night-1 gear vs the median reached night-8 build.
 *
 * Tail for tools/sim_run.js. fark_proto.html is NOT edited.
 */
var seed=(window.__FSIM_SEED!==undefined)?window.__FSIM_SEED:20260731;
var RUNS=(window.__FSIM_RUNS!==undefined)?window.__FSIM_RUNS:250;
var out={seed:seed,runs:RUNS};

var FAM=['amber','jade','jade2','silver','obsidian','starstone','vagabond'];
var STARTERS=['amber','silver','obsidian','starstone','vagabond'];

/* Carry the run's PURCHASED brands into the match untouched.
   FSIM.buildLoadout redraws every brand's face from _iconFaceRoll, which is
   right for a one-off gear spec and wrong for a run, where the face was bought
   once. Detection is by SHAPE, not by a flag: FSIM.setupMatch rebuilds its own
   options object before calling buildLoadout, so any private flag on the gear
   is dropped on the way through — a real ench object ({t:'tithe',face:5}) is
   the only reliable signal. Getting this wrong the first time made every brand
   in the run loop inert (mkEnch wrapped the object as {t:{...}} and _isIcon
   then said no), which is why titheLive below is asserted in the output. */
var _realBuild=FSIM.buildLoadout;
FSIM.buildLoadout=function(spec){
  var e0=((spec&&spec.ench)||[]).filter(Boolean)[0];
  if(!(e0&&typeof e0==='object'&&typeof e0.t==='string'))return _realBuild(spec);
  _getS();
  var dice=(spec.dice||[]).slice(0,6);while(dice.length<6)dice.push('bone');
  S.run.dice=dice.slice();
  S.run.dieEnch=(spec.ench||[]).map(function(e){return e?{t:e.t,face:e.face}:null;});
  while(S.run.dieEnch.length<6)S.run.dieEnch.push(null);
  S.run.dieEnchInv=S.run.dieEnchInv||[];
  S.run._enchV=3;S.run._enchTradeV=2;
  return{dice:dice.slice(),ench:S.run.dieEnch.slice(),refused:[]};
};

/* count brands destroyed by a die purchase, by watching the REAL _stTrade */
var brandsBurned=0,goldOnBrands=0,tradeCount=0;
var _realTrade=window._stTrade;
window._stTrade=function(mat,slot){
  _getS();
  var had=!!(S.run.dieEnch&&S.run.dieEnch[slot]);
  var before=S.run.gold||0;
  var r=_realTrade.apply(null,arguments);
  if((S.run.gold||0)<before){tradeCount++;if(had)brandsBurned++;}
  return r;
};
var _realApply=window._gbEnchantApply;
window._gbEnchantApply=function(k,i,a,b,q){
  _getS();var before=S.run.gold||0;
  var r=_realApply.apply(null,arguments);
  goldOnBrands+=Math.max(0,before-(S.run.gold||0));
  return r;
};

function newRunState(starter){
  _getS();
  S.run=_freshRun();
  S.run.dice=['bone','bone','bone','bone','bone','bone'];S.run.dice[5]=starter;
  S.run.dieEnch=[null,null,null,null,null,null];
  S.run.dieEnchInv=[];S.run.diceInv=[];
  S.run._enchV=3;S.run._enchTradeV=2;
  S.run.diceStock=_initDiceStock();
  S.run.fcards=[];S.run.finv=[];
  S.run.tells=[];S.run.sleeve=null;S.run.night=null;S.run._shopRoll=null;
}
function brandCount(){var n=0;(S.run.dieEnch||[]).forEach(function(e){if(e)n++;});return n;}
function famCount(){var n=0;(S.run.dice||[]).forEach(function(m){if(FAM.indexOf(m)>=0)n++;});return n;}

function shopVisit(plan){
  _getS();
  S.run._shopRoll=null;
  var sold=(_shopRollNight()||{}).sold||{};
  var guard=0;
  if(plan.buyDice)while(guard++<8){
    var worst=0;
    for(var i=1;i<6;i++)if(dieRank(S.run.dice[i])<dieRank(S.run.dice[worst]))worst=i;
    var best=null;
    FAM.forEach(function(m){
      if(sold[m])return;
      if((S.run.diceStock[m]||0)<=0)return;
      if(_dicePrice(m)>(S.run.gold||0))return;
      if(dieRank(m)<=dieRank(S.run.dice[worst]))return;
      if(!best||dieRank(m)>dieRank(best))best=m;
    });
    if(!best)break;
    _stTrade(best,worst);
  }
  if(plan.maxBrands>0){
    plan.brandList.forEach(function(k){
      if(brandCount()>=plan.maxBrands)return;
      if(plan.diceFirst&&famCount()<plan.diceFirst)return;
      var e=ENCH_ICONS[k];if(!e)return;
      if((S.run.gold||0)<e.price)return;
      var lane=-1;
      for(var i=0;i<6;i++){
        if(S.run.dieEnch[i])continue;
        if(plan.brandFamilyOnly&&FAM.indexOf(S.run.dice[i])<0)continue;
        lane=i;break;}
      if(lane<0)return;
      var face=_iconFaceRoll(S.run.dice[lane]);if(face==null)return;
      _gbEnchantApply(k,lane,face,null,true);
    });
  }
}
function playMatch(policy,rung,boss){
  _getS();
  var dice=S.run.dice.slice(),ench=S.run.dieEnch.slice(),
      fcards=(S.run.fcards||[]).slice(),inv=(S.run.diceInv||[]).slice(),
      sleeve=S.run.sleeve,tier=S.run.tier,gold=S.run.gold||0,
      stock=S.run.diceStock,night=S.run.night,pts=S.run.points,
      coins=S.run.coins,tells=(S.run.tells||[]).slice(),
      beaten=(S.run.bossesBeaten||[]).slice();
  var m=FSIM.simMatch(policy,{tier:tier,boss:!!boss,
    gear:{__verbatim:true,dice:dice,ench:ench,badge:sleeve,fcards:fcards},
    badge:sleeve,fcards:fcards,diceInv:inv,gold:gold,
    rung:boss?null:rung,playerFirst:(FSIM.aux()<0.5)});
  var goldAfter=S.run.gold||0;
  _getS();
  S.run.dice=dice;S.run.dieEnch=ench;S.run.fcards=fcards;S.run.diceInv=inv;
  S.run.sleeve=sleeve;S.run.tier=tier;S.run.gold=goldAfter;
  S.run.diceStock=stock;S.run.night=night;S.run.points=pts;S.run.coins=coins;
  S.run.tells=tells;S.run.bossesBeaten=beaten;
  return m;
}
var _pool=null;
function draftAfterWin(){
  _getS();
  if(!_pool){_pool=(typeof FAM_CARDS!=='undefined'?FAM_CARDS:[]).filter(function(d){
    if(typeof FAM_LIVE!=='undefined'&&!FAM_LIVE[d.id])return false;
    if(d.unique)return false;
    try{var def=famDef(d.id);if(def&&def.kind==='active')return false;}catch(e){}
    return true;});}
  S.run.fcards=S.run.fcards||[];
  if(S.run.fcards.length<3&&_pool.length){
    var owned={};S.run.fcards.forEach(function(c){owned[c.id]=1;});
    for(var t=0;t<20;t++){
      var c=_pool[(Math.random()*_pool.length)|0];
      if(!owned[c.id]){S.run.fcards.push({id:c.id,tier:1});return;}
    }
  }
  S.run.gold=(S.run.gold||0)+5+((S.run.tier||0)*5);
}

function playRun(policy,plan){
  newRunState(STARTERS[(Math.random()*STARTERS.length)|0]);
  var L={gold8:null,brands8:null,fam8:null,dice8:null,ench8:null,
         tithe:0,cleared:false,died:false,ownedJade2:false,
         shopGoldWhenDiceDone:[],brandsMax:0,finalTier:0};
  var guard=0;
  while(guard++<60){
    _getS();
    if(S.run._died||S.run.tier>=8)break;
    var tier=S.run.tier;
    shopVisit(plan);
    if(plan.wear&&(S.run.tells||[]).length){
      var wnt=plan.wear.filter(function(id){return S.run.tells.indexOf(id)>=0;});
      S.run.sleeve=wnt.length?wnt[0]:null;
    }
    if(famCount()>=6)L.shopGoldWhenDiceDone.push(S.run.gold||0);
    if((S.run.dice||[]).indexOf('jade2')>=0)L.ownedJade2=true;
    if(brandCount()>L.brandsMax)L.brandsMax=brandCount();
    if(tier===7){L.gold8=S.run.gold||0;L.brands8=brandCount();L.fam8=famCount();
      L.dice8=(S.run.dice||[]).slice();
      L.ench8=(S.run.dieEnch||[]).map(function(e){return e?e.t:null;});}
    _ensureNight();
    var need=(TIERS[tier]||TIERS[0]).pointsNeeded,sg=0;
    while(sg++<12){
      _getS();
      if(S.run._died||S.run.tier!==tier)break;
      if((S.run.points||0)>=need)break;
      var n=S.run.night;if(!n||n.tier!==tier){_ensureNight();n=S.run.night;}
      var idx=-1;for(var i=0;i<n.roster.length;i++)if(!n.seatsPlayed[i]){idx=i;break;}
      if(idx<0)break;
      var buy=Math.min((S.run.gold||0),(NIGHT_BUYINS[tier]||0));
      S.run.gold=(S.run.gold||0)-buy;
      n.seatsPlayed[idx]=true;n.results[idx]='lost';
      var pat=JSON.parse(JSON.stringify(n.roster[idx]));
      var g0=S.run.gold||0;
      var m=playMatch(policy,pat,false);
      L.tithe+=Math.max(0,(S.run.gold||0)-g0);
      if(m&&m.won){S.run.gold=(S.run.gold||0)+(20+tier*12)+buy;
        _settleEndRoute({win:true,isBoss:false,seatIdx:idx,pointsEarned:1});draftAfterWin();}
      else _settleEndRoute({win:false,isBoss:false,seatIdx:idx});
      _getS();if(S.run.night===null)break;
    }
    _getS();
    if(S.run._died)break;
    if(S.run.tier!==tier)continue;
    if((S.run.points||0)<need)continue;
    var g1=S.run.gold||0;
    var bm=playMatch(policy,null,true);
    L.tithe+=Math.max(0,(S.run.gold||0)-g1);
    if(bm&&bm.won){S.run.gold=(S.run.gold||0)+(RUNGS[tier].gold||0);
      try{tellGive(RUNGS[tier].tell.id);}catch(e){}
      _settleEndRoute({win:true,isBoss:true,bossKey:RUNGS[tier].key});}
    else _settleEndRoute({win:false,isBoss:true,bossKey:RUNGS[tier].key});
  }
  _getS();
  L.died=!!S.run._died;L.cleared=(S.run.tier>=8);L.finalTier=S.run.tier;
  return L;
}

var MAXER={key:'maxer',buyDice:true,maxBrands:6,diceFirst:6,brandFamilyOnly:true,
  brandList:['tithe','fog','snuff','break','trade','ward','snare'],wear:['kindred']};
var EARLY={key:'early brander',buyDice:true,maxBrands:6,diceFirst:0,brandFamilyOnly:true,
  brandList:['tithe','fog','snuff','break','trade','ward','snare'],wear:['kindred']};

/* LIVENESS ASSERT: a tithe-branded loadout, carried through the verbatim path,
   must actually pay gold. If this is 0 the brands are inert and every number
   below it is measuring an unbranded build. */
try{
  FSIM.quiet();FSIM.installRng(seed);
  var probe=FSIM.simMatch(FSIM.POLICIES.bea,{tier:5,
    gear:{dice:['amber','amber','amber','amber','amber','amber'],
          ench:[{t:'tithe',face:1},{t:'tithe',face:5},null,null,null,null],
          badge:null,fcards:[]},gold:0});
  out.titheLive={goldGained:probe.goldGained,icons:probe.icons,
    verdict:probe.goldGained>0?'BRANDS LIVE':'BRANDS INERT — numbers below are void'};
  FSIM.loud();
}catch(e){out.titheLive='ERR '+e.message;}

try{
  FSIM.quiet();
  var t0=performance.now();
  out.plans={};
  [['maxer_dice_first',MAXER],['early_brander',EARLY]].forEach(function(pp){
    brandsBurned=0;goldOnBrands=0;tradeCount=0;
    FSIM.installRng(seed);
    var logs=[];for(var r=0;r<RUNS;r++)logs.push(playRun(FSIM.POLICIES.bea,pp[1]));
    var at8=logs.filter(function(L){return L.brands8!==null;});
    var hist={};at8.forEach(function(L){hist[L.brands8]=(hist[L.brands8]||0)+1;});
    var shopGold=[];logs.forEach(function(L){L.shopGoldWhenDiceDone.forEach(function(g){shopGold.push(g);});});
    var full=at8.filter(function(L){return L.brands8>=6&&L.fam8>=6;}).length;
    var jade2=logs.filter(function(L){return L.ownedJade2;}).length;
    out.plans[pp[0]]={
      reachedNight8:at8.length,ofRuns:logs.length,
      goldAtNight8:{median:FSIM.median(at8.map(function(L){return L.gold8;})),
        mean:+FSIM.ciMean(at8.map(function(L){return L.gold8;})).mean.toFixed(0),
        max:at8.length?Math.max.apply(null,at8.map(function(L){return L.gold8;})):0},
      brandsAtNight8:{mean:+FSIM.ciMean(at8.map(function(L){return L.brands8;})).mean.toFixed(2),
        ci:(function(){var m=FSIM.ciMean(at8.map(function(L){return L.brands8;}));return [m.lo,m.hi];})(),
        median:FSIM.median(at8.map(function(L){return L.brands8;})),histogram:hist},
      famDiceAtNight8:+FSIM.ciMean(at8.map(function(L){return L.fam8;})).mean.toFixed(2),
      reachedFullSpec:full,reachedFullSpecPct:+(100*full/Math.max(1,at8.length)).toFixed(1),
      everOwnedJade2:jade2,everOwnedJade2Pct:+(100*jade2/logs.length).toFixed(1),
      brandsDestroyedByDiePurchase:brandsBurned,dicePurchases:tradeCount,
      goldSpentOnBrands:goldOnBrands,
      titheIncomePerRun:{mean:+FSIM.ciMean(logs.map(function(L){return L.tithe;})).mean.toFixed(0),
        median:FSIM.median(logs.map(function(L){return L.tithe;}))},
      goldInPurseAtShopVisitsAfterDiceComplete:{n:shopGold.length,
        median:FSIM.median(shopGold),
        mean:shopGold.length?+FSIM.ciMean(shopGold).mean.toFixed(0):0},
      clearedPct:+(100*logs.filter(function(L){return L.cleared;}).length/logs.length).toFixed(1),
      sampleNight8Loadouts:at8.slice(0,6).map(function(L){
        return{dice:L.dice8,ench:L.ench8,gold:L.gold8};})
    };
  });
  out.msRuns=Math.round(performance.now()-t0);
  FSIM.loud();
}catch(e){try{FSIM.loud();}catch(e2){}out.plans='ERR '+e.stack;}

window._stTrade=_realTrade;window._gbEnchantApply=_realApply;
FSIM.buildLoadout=_realBuild;

/* ── F2. the delta against the build a run actually arrives at ────────── */
try{
  FSIM.quiet();
  var TIER=5,NM=600;
  function pairedCI(b,c,n){
    var d=(b-c)/n,v=(b+c-(b-c)*(b-c)/n)/(n*n),se=Math.sqrt(Math.max(v,0));
    return{d:+(100*d).toFixed(1),lo:+(100*(d-1.959963985*se)).toFixed(1),
           hi:+(100*(d+1.959963985*se)).toFixed(1),discordant:b+c};
  }
  var CARDS=FSIM.GEAR.night8.fcards.slice();
  var gears=[
    {key:'night1_real',dice:['silver','bone','bone','bone','bone','bone'],
     ench:[null,null,null,null,null,null],badge:null,fcards:[]},
    /* the shape the run loop actually produces: six family dice, starstone /
       obsidian heavy because jade2 at 1800g is never affordable in one visit */
    {key:'night8_REACHED_0brands',dice:['starstone','starstone','jade','vagabond','silver','amber'],
     ench:[null,null,null,null,null,null],badge:'kindred',fcards:CARDS},
    {key:'night8_REACHED_2brands',dice:['starstone','starstone','jade','vagabond','silver','amber'],
     ench:['tithe','ward',null,null,null,null],badge:'kindred',fcards:CARDS},
    {key:'night8_SPEC_6brands',dice:FSIM.GEAR.night8.dice.slice(),
     ench:FSIM.GEAR.night8.ench.slice(),badge:'kindred',fcards:CARDS}
  ];
  var wins=gears.map(function(){return [];}),bank=gears.map(function(){return [];});
  for(var i=0;i<NM;i++){
    var s=(seed+i*7919)|0,first=(i%2===0);
    for(var g=0;g<gears.length;g++){
      FSIM.installRng(s);
      var rung=generatePatron(TIER);
      var m=null;
      try{m=FSIM.simMatch(FSIM.POLICIES.bea,{tier:TIER,gear:gears[g],
        badge:gears[g].badge,fcards:gears[g].fcards,rung:rung,playerFirst:first});}catch(e){}
      wins[g].push(m?(m.won?1:0):null);bank[g].push(m?m.playerBank:null);
    }
  }
  function rate(g){var k=0,n=0;wins[g].forEach(function(x){if(x!=null){n++;if(x)k++;}});
    var c=FSIM.ci95(k,n);return{win:+(100*c.p).toFixed(1),ci:[+(100*c.lo).toFixed(1),+(100*c.hi).toFixed(1)],n:n};}
  function vs(a,b){var x=0,y=0,n=0;
    for(var i=0;i<NM;i++){var p=wins[a][i],q=wins[b][i];if(p==null||q==null)continue;
      n++;if(p&&!q)x++;if(!p&&q)y++;}
    return pairedCI(x,y,Math.max(1,n));}
  out.realisedPower={tier:TIER,n:NM,
    rows:gears.map(function(g,i){return{key:g.key,rate:rate(i)};}),
    reached0_vs_night1:vs(1,0),reached2_vs_night1:vs(2,0),spec_vs_night1:vs(3,0),
    reached0_vs_spec:vs(1,3)};
  FSIM.loud();
}catch(e){try{FSIM.loud();}catch(e2){}out.realisedPower='ERR '+e.stack;}

FSIM.restoreRng();
return out;
