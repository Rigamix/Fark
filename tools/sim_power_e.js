/* sim_power_e.js — LENS 2, the GOLD CURVE. Can a run actually AFFORD the
 * "night-8, fully-built" loadout the power comparison is written about?
 *
 * A whole run, night 1 to night 8, driven through the shipped progression:
 *   REAL   _freshRun, _ensureNight (so every seat is a real generatePatron),
 *          _settleEndRoute (points, night fail, heart loss, boss heart heal,
 *          tier advance), _checkNightFail, _shopRollNight (the 55%-sold-out
 *          roll and the pity rule), _dicePrice / DICE_STORE / S.run.diceStock,
 *          _stTrade (a die bought into a loadout slot — and the brand in that
 *          slot destroyed with it), _gbEnchantApply (the brand purchase, with
 *          the real 1/5 face guard and the real one-Ward cap), _iconFaceRoll,
 *          tellGive, and the whole match through FSIM.
 *   MODEL  the gold AWARD itself. endMatch is an animation chain, so the two
 *          award lines are reproduced from the shipped source:
 *            patron win  = 20 + tier*12, plus the seat buy-in back  (~27570)
 *            boss win    = RUNGS[tier].gold                          (~27612)
 *            draft skip  = 5 + tier*5                                (~32126)
 *          The seat buy-in deduction is the shipped clamp (min(gold, buyIn)).
 *          Tithe's income is NOT modelled — it is the real ENCH_ICONS.tithe
 *          .fire writing into S.run.gold during the match.
 *   MODEL  the card draft: after a patron win, equip a random live, non-unique,
 *          non-active family card at tier 1 until three are held, then skip
 *          for gold. Tier upgrades and boss spoils are NOT modelled, so the
 *          card layer here is WEAKER than a real run's.
 *
 * Tail for tools/sim_run.js. fark_proto.html is NOT edited.
 */
var seed=(window.__FSIM_SEED!==undefined)?window.__FSIM_SEED:20260731;
var RUNS=(window.__FSIM_RUNS!==undefined)?window.__FSIM_RUNS:250;
var out={seed:seed,runs:RUNS};

/* ── cost of the loadout under test ───────────────────────────────────── */
var N8=FSIM.GEAR.night8;
try{
  var dcost=0;N8.dice.forEach(function(m){
    var d=DICE_STORE.find(function(x){return x.mat===m;});dcost+=d?d.price:0;});
  var ecost=0;N8.ench.forEach(function(t){if(t&&ENCH_ICONS[t])ecost+=ENCH_ICONS[t].price;});
  out.night8Cost={dice:N8.dice.slice(),diceGold:dcost,
                  ench:N8.ench.slice(),enchGold:ecost,total:dcost+ecost};
}catch(e){out.night8Cost='ERR '+e.message;}

/* the theoretical ceiling: every reward a perfect run can collect, in order */
try{
  var cum=100,sched=[{night:1,goldAtNightStart:100}];
  for(var t=0;t<8;t++){
    cum+=TIERS[t].pointsNeeded*(20+t*12);
    if(t<7)sched.push({night:t+2,goldAtNightStart:cum+RUNGS[t].gold});
    cum+=RUNGS[t].gold;
  }
  out.perfectRunIncome={byNightStart:sched,totalIfEverythingWon:cum,
    note:'patron wins + boss gold only; no losses, no draft skips, no Tithe'};
}catch(e){out.perfectRunIncome='ERR '+e.message;}

/* ── loadout is carried VERBATIM between matches ──────────────────────── */
/* FSIM.buildLoadout redraws a brand's face from _iconFaceRoll every time it is
   called. That is right for a one-off gear spec and wrong for a run, where the
   face was bought once. This override keeps the purchased ench objects; the
   normal path is untouched for any spec that does not ask for it. */
var _realBuild=FSIM.buildLoadout;
FSIM.buildLoadout=function(spec){
  if(!spec||!spec.__verbatim)return _realBuild(spec);
  _getS();
  var dice=(spec.dice||[]).slice(0,6);while(dice.length<6)dice.push('bone');
  S.run.dice=dice.slice();
  S.run.dieEnch=(spec.ench||[]).map(function(e){return e?{t:e.t,face:e.face}:null;});
  while(S.run.dieEnch.length<6)S.run.dieEnch.push(null);
  S.run.dieEnchInv=S.run.dieEnchInv||[];
  S.run._enchV=3;S.run._enchTradeV=2;
  return{dice:dice.slice(),ench:S.run.dieEnch.slice(),refused:[]};
};

var STARTERS=['amber','silver','obsidian','starstone','vagabond'];
var FAM=['amber','jade','jade2','silver','obsidian','starstone','vagabond'];

function newRunState(starter){
  _getS();
  S.run=_freshRun();
  S.run.dice=['bone','bone','bone','bone','bone','bone'];
  S.run.dice[5]=starter;/* famRunDraftPick replaces the LAST bone */
  S.run.dieEnch=[null,null,null,null,null,null];
  S.run.dieEnchInv=[];S.run.diceInv=[];
  S.run._enchV=3;S.run._enchTradeV=2;
  S.run.diceStock=_initDiceStock();
  S.run.fcards=[];S.run.finv=[];
  S.run.tells=[];S.run.sleeve=null;S.run.night=null;
  S.run._shopRoll=null;
}
function brandCount(){var n=0;(S.run.dieEnch||[]).forEach(function(e){if(e)n++;});return n;}
function famCount(){var n=0;(S.run.dice||[]).forEach(function(m){if(FAM.indexOf(m)>=0)n++;});return n;}

/* ── THE SHOP, through the shipped purchase functions ─────────────────── */
function shopVisit(plan){
  _getS();
  S.run._shopRoll=null;               /* one fresh availability roll a night */
  var roll=_shopRollNight();          /* REAL: 55% sold-out per family + pity */
  var sold=roll.sold||{};
  var guard=0;
  if(plan.buyDice)while(guard++<8){
    var worst=0;
    for(var i=1;i<6;i++)if(dieRank(S.run.dice[i])<dieRank(S.run.dice[worst]))worst=i;
    var best=null;
    FAM.forEach(function(m){
      if(sold[m])return;
      if((S.run.diceStock[m]||0)<=0)return;
      if(_dicePrice(m)>((S.run.gold||0)-(plan.reserve||0)))return;
      if(dieRank(m)<=dieRank(S.run.dice[worst]))return;
      if(!best||dieRank(m)>dieRank(best))best=m;
    });
    if(!best)break;
    _stTrade(best,worst);             /* REAL purchase into the loadout slot */
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
        lane=i;break;
      }
      if(lane<0)return;
      var face=_iconFaceRoll(S.run.dice[lane]);
      if(face==null)return;
      _gbEnchantApply(k,lane,face,null,true);   /* REAL brand purchase */
    });
  }
}

/* ── ONE MATCH, with the run's live loadout ───────────────────────────── */
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
  var goldAfter=S.run.gold||0;         /* Tithe wrote into this for real */
  _getS();
  S.run.dice=dice;S.run.dieEnch=ench;S.run.fcards=fcards;S.run.diceInv=inv;
  S.run.sleeve=sleeve;S.run.tier=tier;S.run.gold=goldAfter;
  S.run.diceStock=stock;S.run.night=night;S.run.points=pts;S.run.coins=coins;
  S.run.tells=tells;S.run.bossesBeaten=beaten;
  return m;
}

/* ── the card draft, MODELLED ─────────────────────────────────────────── */
var _draftPool=null;
function draftAfterWin(){
  _getS();
  if(!_draftPool){
    _draftPool=(typeof FAM_CARDS!=='undefined'?FAM_CARDS:[]).filter(function(d){
      if(typeof FAM_LIVE!=='undefined'&&!FAM_LIVE[d.id])return false;
      if(d.unique)return false;
      try{var def=famDef(d.id);if(def&&def.kind==='active')return false;}catch(e){}
      return true;});
  }
  S.run.fcards=S.run.fcards||[];
  if(S.run.fcards.length<3&&_draftPool.length){
    var owned={};S.run.fcards.forEach(function(c){owned[c.id]=1;});
    var pick=null,tries=0;
    while(tries++<20){
      var c=_draftPool[(Math.random()*_draftPool.length)|0];
      if(!owned[c.id]){pick=c;break;}
    }
    if(pick){S.run.fcards.push({id:pick.id,tier:1});return 'took';}
  }
  S.run.gold=(S.run.gold||0)+5+((S.run.tier||0)*5);/* draftSkip, shipped */
  return 'skipped';
}

/* ── ONE RUN ──────────────────────────────────────────────────────────── */
function playRun(policy,plan){
  newRunState(STARTERS[(Math.random()*STARTERS.length)|0]);
  var log={goldAtNightStart:[],famAtNightStart:[],brandsAtNightStart:[],
           nightsReached:0,seatWins:0,seatLosses:0,bossWins:0,bossLosses:0,
           nightFails:0,goldEarned:0,goldSpent:0,died:false,cleared:false,
           finalDice:null,finalEnch:null,everAffordedN8:false,peakGold:100,
           tithe:0};
  var guard=0;
  while(guard++<60){
    _getS();
    if(S.run._died||S.run.tier>=8)break;
    var tier=S.run.tier;
    /* SHOP — between nights */
    var before=S.run.gold||0;
    shopVisit(plan);
    log.goldSpent+=Math.max(0,before-(S.run.gold||0));
    /* wear the best badge held */
    if(plan.wear&&(S.run.tells||[]).length){
      var want=plan.wear.filter(function(id){return S.run.tells.indexOf(id)>=0;});
      S.run.sleeve=want.length?want[0]:null;
    }
    log.goldAtNightStart[tier]=S.run.gold||0;
    log.famAtNightStart[tier]=famCount();
    log.brandsAtNightStart[tier]=brandCount();
    log.nightsReached=Math.max(log.nightsReached,tier+1);
    if((S.run.gold||0)>log.peakGold)log.peakGold=S.run.gold||0;
    _ensureNight();                     /* REAL roster of real patrons */
    var need=(TIERS[tier]||TIERS[0]).pointsNeeded;
    var seatGuard=0;
    while(seatGuard++<12){
      _getS();
      if(S.run._died||S.run.tier!==tier)break;
      if((S.run.points||0)>=need)break;
      var n=S.run.night;
      if(!n||n.tier!==tier){_ensureNight();n=S.run.night;}
      var idx=-1;
      for(var i=0;i<n.roster.length;i++)if(!n.seatsPlayed[i]){idx=i;break;}
      if(idx<0)break;
      var buy=Math.min((S.run.gold||0),(NIGHT_BUYINS[tier]||0));
      S.run.gold=(S.run.gold||0)-buy;   /* shipped clamp */
      n.seatsPlayed[idx]=true;n.results[idx]='lost';
      var pat=JSON.parse(JSON.stringify(n.roster[idx]));
      var g0=S.run.gold||0;
      var m=playMatch(policy,pat,false);
      log.tithe+=Math.max(0,(S.run.gold||0)-g0);
      if(m&&m.won){
        log.seatWins++;
        S.run.gold=(S.run.gold||0)+(20+tier*12)+buy;   /* shipped award */
        log.goldEarned+=(20+tier*12)+buy;
        _settleEndRoute({win:true,isBoss:false,seatIdx:idx,pointsEarned:1});
        draftAfterWin();
      }else{
        log.seatLosses++;
        _settleEndRoute({win:false,isBoss:false,seatIdx:idx});
      }
      _getS();
      if(S.run.night===null&&!S.run._died)log.nightFails++;
      if(S.run.night===null)break;      /* night failed: roster re-rolls */
    }
    _getS();
    if(S.run._died)break;
    if(S.run.tier!==tier)continue;
    if((S.run.points||0)<need)continue; /* night failed, go round again */
    /* BOSS */
    var bm=playMatch(policy,null,true);
    if(bm&&bm.won){
      log.bossWins++;
      S.run.gold=(S.run.gold||0)+(RUNGS[tier].gold||0);
      log.goldEarned+=(RUNGS[tier].gold||0);
      try{tellGive(RUNGS[tier].tell.id);}catch(e){}   /* REAL spoils */
      _settleEndRoute({win:true,isBoss:true,bossKey:RUNGS[tier].key});
    }else{
      log.bossLosses++;
      _settleEndRoute({win:false,isBoss:true,bossKey:RUNGS[tier].key});
    }
  }
  _getS();
  log.died=!!S.run._died;
  log.cleared=(S.run.tier>=8);
  log.finalTier=S.run.tier;
  log.finalGold=S.run.gold||0;
  log.finalDice=(S.run.dice||[]).slice();
  log.finalEnch=(S.run.dieEnch||[]).map(function(e){return e?e.t:null;});
  log.finalFam=famCount();log.finalBrands=brandCount();
  log.finalCards=(S.run.fcards||[]).length;
  return log;
}

/* ── three shoppers ───────────────────────────────────────────────────── */
var PLANS={
  dice_only:{key:'DICE ONLY (never brands)',buyDice:true,maxBrands:0,
             brandList:[],reserve:0,wear:['kindred']},
  brief_maxer:{key:'THE BRIEF\'S MAXER (6 dice then brand everything)',
             buyDice:true,maxBrands:6,diceFirst:6,brandFamilyOnly:true,
             brandList:['tithe','fog','snuff','break','trade','ward','snare'],
             reserve:0,wear:['kindred']},
  two_brands:{key:'TWO BRANDS (tithe + ward, dice first)',
             buyDice:true,maxBrands:2,diceFirst:4,brandFamilyOnly:true,
             brandList:['tithe','ward'],reserve:0,wear:['kindred']}
};

try{
  FSIM.quiet();
  var t0=performance.now();
  out.plans={};
  Object.keys(PLANS).forEach(function(pk){
    FSIM.installRng(seed);
    var logs=[];
    for(var r=0;r<RUNS;r++)logs.push(playRun(FSIM.POLICIES.bea,PLANS[pk]));
    function col(f){return logs.map(f);}
    function med(a){return FSIM.median(a);}
    var nightGold=[],nightFam=[],nightBrand=[],reach=[];
    for(var t=0;t<8;t++){
      var g=[],fm=[],br=[];
      logs.forEach(function(L){
        if(L.goldAtNightStart[t]!==undefined){
          g.push(L.goldAtNightStart[t]);fm.push(L.famAtNightStart[t]);br.push(L.brandsAtNightStart[t]);}
      });
      reach.push(g.length);
      nightGold.push(g.length?{n:g.length,median:med(g),mean:+FSIM.ciMean(g).mean.toFixed(0),
        p25:med(g.slice().sort(function(a,b){return a-b;}).slice(0,Math.max(1,g.length>>1))),
        max:Math.max.apply(null,g)}:null);
      nightFam.push(fm.length?+FSIM.ciMean(fm).mean.toFixed(2):null);
      nightBrand.push(br.length?+FSIM.ciMean(br).mean.toFixed(2):null);
    }
    var cleared=0,died=0;logs.forEach(function(L){if(L.cleared)cleared++;if(L.died)died++;});
    out.plans[pk]={
      label:PLANS[pk].key,
      runWin:(function(){var c=FSIM.ci95(cleared,logs.length);
        return{pct:+(100*c.p).toFixed(1),ci:[+(100*c.lo).toFixed(1),+(100*c.hi).toFixed(1)]};})(),
      reachedNight:reach,
      goldAtNightStart:nightGold,
      familyDiceAtNightStart:nightFam,
      brandsAtNightStart:nightBrand,
      medianFinalTier:med(col(function(L){return L.finalTier;})),
      medianGoldEarned:med(col(function(L){return L.goldEarned;})),
      medianGoldSpent:med(col(function(L){return L.goldSpent;})),
      medianPeakGold:med(col(function(L){return L.peakGold;})),
      medianTitheIncome:med(col(function(L){return L.tithe;})),
      medianSeatWins:med(col(function(L){return L.seatWins;})),
      medianSeatLosses:med(col(function(L){return L.seatLosses;})),
      bossWins:col(function(L){return L.bossWins;}).reduce(function(a,b){return a+b;},0),
      bossLosses:col(function(L){return L.bossLosses;}).reduce(function(a,b){return a+b;},0),
      nightFails:col(function(L){return L.nightFails;}).reduce(function(a,b){return a+b;},0),
      medianFinalFam:med(col(function(L){return L.finalFam;})),
      medianFinalBrands:med(col(function(L){return L.finalBrands;})),
      sampleFinalLoadouts:logs.slice(0,4).map(function(L){
        return{tier:L.finalTier,dice:L.finalDice,ench:L.finalEnch,gold:L.finalGold};})
    };
  });
  out.ms=Math.round(performance.now()-t0);
  FSIM.loud();
}catch(e){try{FSIM.loud();}catch(e2){}out.plans='ERR '+e.stack;}

FSIM.buildLoadout=_realBuild;
FSIM.restoreRng();
return out;
