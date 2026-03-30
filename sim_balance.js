// ============ GAMBIT BALANCE SIMULATOR v2 ============
// Includes all original + Batch 1 (20) + Batch 2 (19) cards = 65 total
// Runs 1000 games per card per rung to estimate win rates.

const DICE_TYPES=[
  {id:'bone',faces:[1,2,3,4,5,6],effect:null},
  {id:'iron',faces:[1,2,4,5,5,6],effect:null},
  {id:'flint',faces:[1,3,4,4,5,6],effect:null},
  {id:'lead',faces:[1,1,2,3,4,5],effect:null},
  {id:'amber',faces:[1,2,3,4,5,6],effect:{mechanic:'triple_bonus',amount:100}},
  {id:'jade',faces:[1,2,3,4,5,6],effect:{mechanic:'wild_triple'}},
  {id:'brass',faces:[1,1,5,5,3,4],effect:{mechanic:'reckless',penalty:200}},
  {id:'silver',faces:[1,2,3,4,5,6],effect:{mechanic:'shield'}},
  {id:'crystal',faces:[1,1,2,3,5,5],effect:{mechanic:'single1_bonus',amount:50}},
];

const RUNGS=[
  {id:0,name:'GROG',target:1500,gold:30,buyIn:10,agg:.22,minBank:0,diceStop:3,chaotic:true,adaptive:false,
    boss:null,dice:['bone','bone','bone','bone','bone','bone']},
  {id:1,name:'MABEL',target:2000,gold:45,buyIn:20,agg:.30,minBank:150,diceStop:4,chaotic:false,adaptive:false,
    boss:null,dice:['bone','bone','bone','bone','bone','iron']},
  {id:2,name:'FINNICK',target:2500,gold:60,buyIn:30,agg:.40,minBank:200,diceStop:3,chaotic:false,adaptive:true,
    boss:'STICKY_FINGERS',dice:['bone','bone','bone','iron','iron','flint']},
  {id:3,name:'CORVUS',target:3000,gold:80,buyIn:45,agg:.50,minBank:350,diceStop:3,chaotic:false,adaptive:false,
    boss:'MERCHANTS_TAX',dice:['bone','iron','iron','flint','lead','lead']},
  {id:4,name:'BRUTUS',target:3500,gold:110,buyIn:60,agg:.55,minBank:250,diceStop:2,chaotic:false,adaptive:false,
    boss:'SHIELD_BASH',dice:['iron','iron','flint','lead','amber','amber']},
  {id:5,name:'ALDRIC',target:4000,gold:150,buyIn:80,agg:.58,minBank:300,diceStop:2,chaotic:false,adaptive:false,
    boss:'KNIGHTS_CHALLENGE',dice:['iron','flint','lead','amber','jade','jade']},
  {id:6,name:'WHISPER',target:4500,gold:220,buyIn:120,agg:.58,minBank:300,diceStop:2,chaotic:false,adaptive:true,
    boss:'ROYAL_DECREE',dice:['flint','lead','amber','jade','brass','brass']},
  {id:7,name:'AMBROSE',target:5000,gold:350,buyIn:160,agg:.62,minBank:200,diceStop:2,chaotic:false,adaptive:true,
    boss:'DIVINE_TITHE',dice:['lead','amber','jade','brass','silver','crystal']},
];

// All non-NPC cards (original + batch1 + batch2)
const CARDS=[
  // ── ORIGINAL (26) ──
  {id:'flintlock',rarity:'silver'},
  {id:'copper_pincher',rarity:'tin'},
  {id:'half_measure',rarity:'tin'},
  {id:'the_hearth',rarity:'tin'},
  {id:'slow_burn',rarity:'tin'},
  {id:'fools_gold',rarity:'tin'},
  {id:'cracked_bell',rarity:'tin'},
  {id:'jesters_mask',rarity:'tin'},
  {id:'millers_toll',rarity:'silver'},
  {id:'scavenger',rarity:'silver'},
  {id:'last_stand',rarity:'silver'},
  {id:'rusty_spur',rarity:'silver'},
  {id:'martyr',rarity:'silver'},
  {id:'blood_debt',rarity:'silver'},
  {id:'serpents_whisper',rarity:'silver'},
  {id:'cowards_bell',rarity:'silver'},
  {id:'leaky_cup',rarity:'gold'},
  {id:'crows_luck',rarity:'gold'},
  {id:'taxing_breath',rarity:'gold'},
  {id:'thieves_luck',rarity:'gold'},
  {id:'plague_wind',rarity:'gold'},
  {id:'kings_ransom',rarity:'gold'},
  {id:'sooty_table',rarity:'gold'},
  {id:'thrifty_gambler',rarity:'gold'},
  {id:'iron_crown',rarity:'gold'},
  {id:'tyrants_gaze',rarity:'gold'},
  // ── WAVE 1.5 (5) ──
  {id:'beggars_bowl',rarity:'tin'},
  {id:'loose_thread',rarity:'tin'},
  {id:'the_whetstone',rarity:'silver'},
  {id:'snake_oil',rarity:'silver'},
  {id:'fortunes_wheel',rarity:'gold'},
  // ── BATCH 1 (20) ──
  {id:'loaded_die',rarity:'silver'},
  {id:'gamblers_ghost',rarity:'tin'},
  {id:'greedy_hands',rarity:'tin'},
  {id:'the_grudge',rarity:'silver'},
  {id:'lucky_seven',rarity:'tin'},
  {id:'the_hare',rarity:'silver'},
  {id:'cold_shoulder',rarity:'tin'},
  {id:'warm_hands',rarity:'silver'},
  {id:'gamblers_thumb',rarity:'silver'},
  {id:'chain_lightning',rarity:'silver'},
  {id:'hot_streak',rarity:'silver'},
  {id:'underdog',rarity:'silver'},
  {id:'twin_dice',rarity:'silver'},
  {id:'sawdust',rarity:'silver'},
  {id:'short_pour',rarity:'silver'},
  {id:'the_collector',rarity:'gold'},
  {id:'tavern_cheer',rarity:'gold'},
  {id:'last_call',rarity:'gold'},
  {id:'old_bones',rarity:'gold'},   // active — sim as one-shot
  {id:'phoenix_ash',rarity:'gold'},  // active — sim as one-shot
  // ── BATCH 2 (19) ──
  {id:'drunkards_prayer',rarity:'tin'},
  {id:'the_jinx',rarity:'tin'},
  {id:'thick_skin',rarity:'tin'},
  {id:'blood_tithe',rarity:'tin'},
  {id:'the_echo',rarity:'silver'},
  {id:'frozen_die',rarity:'silver'},  // active — sim as passive
  {id:'double_down',rarity:'silver'}, // active — skip in sim
  {id:'slippery_table',rarity:'silver'},
  {id:'high_roller',rarity:'silver'},
  {id:'the_fence',rarity:'silver'},
  {id:'the_alchemist',rarity:'silver'},
  {id:'twin_flames',rarity:'silver'},
  {id:'broken_lantern',rarity:'gold'}, // active — no gameplay effect in sim
  {id:'wild_die',rarity:'gold'},       // active — sim as one-shot
  {id:'second_wind',rarity:'gold'},    // active — sim as one-shot
  {id:'the_brewer',rarity:'gold'},
  {id:'dead_mans_hand',rarity:'gold'},
  {id:'the_pyre',rarity:'gold'},       // active — skip (sacrifice)
  {id:'all_in',rarity:'gold'},         // active — sim as one-shot
];

function getDie(mat){return DICE_TYPES.find(d=>d.id===mat)||DICE_TYPES[0];}
function rollFace(mat){
  const dt=getDie(mat);
  const faces=dt.faces||[1,2,3,4,5,6];
  return faces[Math.floor(Math.random()*faces.length)];
}

// ---- SCORING ----
function scoreRoll(vals,cards,locked,context,dieMats){
  cards=cards||[];locked=locked||0;context=context||{};dieMats=dieMats||null;
  const n=vals.length,used=new Array(n).fill(false);let pts=0;
  const copperPincher=cards.includes('copper_pincher'),millersToll=cards.includes('millers_toll'),scavenger=cards.includes('scavenger');
  const bloodTithe=cards.includes('blood_tithe');
  const dieEff=i=>{if(!dieMats||!dieMats[i])return null;const dt=getDie(dieMats[i]);return dt&&dt.effect?dt.effect:null;};

  /* Jade wild_triple prep: 6s on jade dice become -1 (wildcard) */
  const eVals=[...vals];
  const wildIdx=[];
  for(let i=0;i<n;i++){const eff=dieEff(i);if(eff&&eff.mechanic==='wild_triple'&&vals[i]===6){wildIdx.push(i);eVals[i]=-1;}}

  const cnt=f=>{let c=0;for(let i=0;i<n;i++)if(!used[i]&&eVals[i]===f)c++;return c;};
  const cntWild=()=>{let c=0;for(let i=0;i<n;i++)if(!used[i]&&eVals[i]===-1)c++;return c;};
  const mark=(f,k)=>{let l=k;for(let i=0;i<n&&l>0;i++)if(!used[i]&&eVals[i]===f){used[i]=true;l--;}};
  const markWild=(k)=>{let l=k;for(let i=0;i<n&&l>0;i++)if(!used[i]&&eVals[i]===-1){used[i]=true;l--;}};
  const hasSet=faces=>{const pool=eVals.filter((_,i)=>!used[i]);let wilds=pool.filter(v=>v===-1).length;const nonWild=pool.filter(v=>v!==-1);return faces.every(f=>{const j=nonWild.indexOf(f);if(j>=0){nonWild.splice(j,1);return true;}if(wilds>0){wilds--;return true;}return false;});};
  const markSet=faces=>{const todo=[...faces];for(let i=0;i<n&&todo.length;i++)if(!used[i]){const j=todo.indexOf(eVals[i]);if(j>=0){used[i]=true;todo.splice(j,1);}else if(eVals[i]===-1&&todo.length){used[i]=true;todo.splice(0,1);}}};

  let scavengerFired=false;
  if(scavenger&&!context._scavengerBlocked){
    const ones=vals.filter(v=>v===1).length,fives=vals.filter(v=>v===5).length;
    if(ones===1&&fives===1){pts+=300;mark(1,1);mark(5,1);scavengerFired=true;}
  }
  if(!copperPincher&&!scavengerFired){
    if(n>=6&&hasSet([1,2,3,4,5,6])){
      let straightBase=1500;
      if(cards.includes('tavern_cheer'))straightBase+=750;
      pts+=straightBase;used.fill(true);
      return{total:pts,used,context,triplesFired:[]};
    }
    if(hasSet([2,3,4,5,6])){pts+=750;markSet([2,3,4,5,6]);}
    else if(hasSet([1,2,3,4,5])){pts+=500;markSet([1,2,3,4,5]);}
  }
  const triplesFired=[];
  for(let f=1;f<=6;f++){
    const realC=cnt(f);const wc=cntWild();const totalC=realC+wc;
    if(totalC>=3){
      const wildsNeeded=Math.max(0,3-realC);
      let base=f===1?1000:f*100;
      for(let x=0;x<(realC+wildsNeeded)-3;x++)base*=2;
      if(millersToll&&f>=2&&f<=4)base+=150;
      /* Amber triple_bonus: +amount for each amber die in this set */
      if(dieMats){
        let amberBonus=0;
        for(let i=0;i<n;i++){
          if(!used[i]&&(eVals[i]===f||eVals[i]===-1)){
            const e=dieEff(i);
            if(e&&e.mechanic==='triple_bonus')amberBonus+=(e.amount||100);
          }
        }
        if(amberBonus>0)base+=amberBonus;
      }
      pts+=base;mark(f,realC);if(wildsNeeded>0)markWild(wildsNeeded);
      triplesFired.push(f);
    }
  }
  // Singles
  let single1Count=0;
  for(let i=0;i<n;i++){if(used[i])continue;const v=eVals[i];
    if(v===1){single1Count++;
      let s1=millersToll?75:(bloodTithe?150:(copperPincher?125:100));
      /* Crystal single1_bonus */
      const e=dieEff(i);if(e&&e.mechanic==='single1_bonus')s1+=(e.amount||50);
      pts+=s1;used[i]=true;}
    else if(v===5){pts+=copperPincher?75:50;used[i]=true;}}
  // Twin Dice: pair of singles 1s = +100
  if(cards.includes('twin_dice')&&single1Count>=2)pts+=100;
  // Lucky Seven: non-scoring dice total 7 → +200
  if(cards.includes('lucky_seven')){
    let nss=0;for(let i=0;i<n;i++){if(!used[i])nss+=vals[i];}
    if(nss===7)pts+=200;
  }
  return{total:pts,used,context,triplesFired};
}

function anyScoring(vals,cards,dieMats){return scoreRoll(vals,cards||[],0,{},dieMats).total>0;}

function playerSelectDice(vals,cards,dieMats){
  const{total,used,triplesFired}=scoreRoll(vals,cards,0,{},dieMats);
  if(total<=0)return{pts:0,kept:0,bust:true};
  return{pts:total,kept:used.filter(u=>u).length,bust:false,triplesFired};
}

function playerShouldBank(bankSoFar,diceLeft,myTotal,oppTotal,target,skill,cards,turnRolls,safeTurnStreak){
  if((myTotal+bankSoFar)>=target)return true;
  if(skill===1){
    if(diceLeft<=1&&bankSoFar>=200)return true;
    if(diceLeft<=2&&bankSoFar>=350)return true;
    if(diceLeft<=3&&bankSoFar>=500)return true;
    if(bankSoFar>=700)return true;
    if(diceLeft===0)return false;
    return false;
  }
  return bankSoFar>=400;
}

function oppShouldBank(rung,oppBank,diceLeft,oppTotal,playerTotal,target,cardMods){
  if((oppTotal+oppBank)>=target)return true;
  let agg=rung.agg;
  if(rung.chaotic)agg=Math.random()*0.8+0.1;
  if(rung.adaptive&&!(cardMods&&cardMods.tyrantsGaze)){
    const gap=playerTotal-oppTotal;const gapRatio=gap/target;
    if(gapRatio>0.2)agg=Math.min(0.95,agg+0.2);
    else if(gapRatio<-0.2)agg=Math.max(0.1,agg-0.15);
  }
  if(cardMods&&cardMods.plagueWind)agg=Math.max(0.05,agg*0.75);
  const effMinBank=rung.minBank+(cardMods&&cardMods.serpentsWhisper?200:0);
  const effDiceStop=rung.diceStop+(cardMods&&cardMods.cowardsBell?1:0);
  if(oppBank<effMinBank&&diceLeft>=2)return false;
  if(diceLeft<=effDiceStop&&oppBank>=effMinBank){if(Math.random()>agg*0.6)return true;}
  if(Math.random()>agg&&oppBank>230)return true;
  return false;
}

// ---- SIMULATE ONE MATCH ----
function simMatch(rung,playerCards,playerDice,skill){
  let pPts=0,oPts=0;
  let turnNum=0;
  let safeTurnStreak=0;
  let flintlockUsedThisTurn=false;
  let martyrUsed=false;
  let crackedBellUsed=false;
  let thickSkinUsed=false;
  let ghostDieNext=false;
  let hotStreakReady=false;
  let chainCount=0;
  let grudgeStack=0;
  let consecutiveBusts=0;
  let beggarsBowlUsed=false;
  let snakeOilUsed=false;
  let snakeOilActive=false;
  let bankCount=0;
  let phoenixUsed=false;
  let secondWindUsed=false;
  let allInUsed=false;
  let wildDieUsed=false;
  let lanternUsed=false;
  let bossState={stickyFingersUsed:false,shieldBashCount:0,challengeUsed:false,challengeActive:false,royalDecreeCount:0};
  let pNumDice=6;
  let maxTurns=200;

  const has=id=>playerCards.includes(id);
  const fenceActive=has('the_fence');
  const alchemistActive=has('the_alchemist')&&playerCards.filter(cid=>{const c=CARDS.find(x=>x.id===cid);return c&&c.rarity==='tin';}).length>=3;

  const cardMods={
    plagueWind:has('plague_wind'),
    serpentsWhisper:has('serpents_whisper'),
    cowardsBell:has('cowards_bell'),
    tyrantsGaze:has('tyrants_gaze'),
    leakyCup:has('leaky_cup'),
    jestersMask:has('jesters_mask'),
  };

  if(has('blood_debt'))pPts=-200;
  if(has('blood_tithe'))pPts-=0;// cost applied per turn in bank

  /* Silver shield: count shield dice for bust protection */
  let playerShields=0;
  playerDice.forEach(m=>{const dt=getDie(m);if(dt.effect&&dt.effect.mechanic==='shield')playerShields++;});
  let shieldUsed=false;

  /* Brass reckless: count brass dice for bust penalty */
  let brassPenalty=0;
  playerDice.forEach(m=>{const dt=getDie(m);if(dt.effect&&dt.effect.mechanic==='reckless')brassPenalty+=(dt.effect.penalty||200);});

  for(let t=0;t<maxTurns;t++){
    turnNum++;
    flintlockUsedThisTurn=false;
    let numDice=pNumDice;
    let turnBank=0;
    let turnRolls=0;
    let busted=false;
    let echoArmed=false;
    let echoReady=false;
    let turnTriples={};
    let turnScoringTypes={};

    // Cold Shoulder: delays boss once-cards by 2 turns
    const csDelay=has('cold_shoulder')?2:0;

    // Knight's Challenge trigger
    if(rung.boss==='KNIGHTS_CHALLENGE'&&!bossState.challengeUsed&&turnNum>=(3+csDelay)&&pPts>=500&&Math.random()<0.4){
      bossState.challengeUsed=true;bossState.challengeActive=true;
    }

    while(true){
      turnRolls++;
      const vals=[];const mats=[];
      for(let i=0;i<numDice;i++){
        const mat=playerDice[i%playerDice.length]||'bone';
        vals.push(rollFace(mat));mats.push(mat);
      }

      // Loaded Die: 40% first roll, force one die to 1
      const warmLimit=has('warm_hands')?3:1;
      if(has('loaded_die')&&turnRolls===1&&Math.random()<0.4){
        const non1=[];vals.forEach((v,i)=>{if(v!==1)non1.push(i);});
        if(non1.length>0)vals[non1[Math.floor(Math.random()*non1.length)]]=1;
      }
      // Gambler's Ghost: post-bust, one die=1
      if(ghostDieNext){
        ghostDieNext=false;
        const non1=[];vals.forEach((v,i)=>{if(v!==1)non1.push(i);});
        if(non1.length>0)vals[non1[Math.floor(Math.random()*non1.length)]]=1;
      }
      // Gambler's Thumb: first roll only, 75% chance, flip one blank to 5
      if(has('gamblers_thumb')&&turnRolls<=1&&Math.random()<0.75){
        const blanks=[];vals.forEach((v,i)=>{if(v!==1&&v!==5)blanks.push(i);});
        if(blanks.length>0)vals[blanks[Math.floor(Math.random()*blanks.length)]]=5;
      }
      // Hot Streak: ready → force one die to 1
      if(hotStreakReady){
        hotStreakReady=false;
        const non1=[];vals.forEach((v,i)=>{if(v!==1)non1.push(i);});
        if(non1.length>0)vals[non1[Math.floor(Math.random()*non1.length)]]=1;
      }
      // Wild Die: one-shot, sim as force one non-scoring die to 1
      if(has('wild_die')&&!wildDieUsed&&turnRolls===1&&numDice>=4){
        wildDieUsed=true;
        const ns=[];vals.forEach((v,i)=>{if(v!==1&&v!==5)ns.push(i);});
        if(ns.length>0)vals[ns[Math.floor(Math.random()*ns.length)]]=1;
      }

      // Flintlock
      if(!flintlockUsedThisTurn&&has('flintlock')&&vals.includes(1)){
        flintlockUsedThisTurn=true;pPts+=100;
      }

      // Boss attacks on roll
      if(rung.boss==='ROYAL_DECREE'&&bossState.royalDecreeCount<2&&turnNum>=(2+csDelay)){
        const oneIdx=[];vals.forEach((v,i)=>{if(v===1)oneIdx.push(i);});
        if(oneIdx.length>0){bossState.royalDecreeCount++;oneIdx.forEach(i=>{vals[i]=3;});}
      }
      if(rung.boss==='SHIELD_BASH'&&bossState.shieldBashCount<2&&numDice>1&&turnNum>=(2+csDelay)){
        const si=[];vals.forEach((v,i)=>{if(v===1||v===5)si.push(i);});
        if(si.length>0){bossState.shieldBashCount++;const vi=si[Math.floor(Math.random()*si.length)];let nv=rollFace(playerDice[vi%playerDice.length]||'bone');while(nv===1||nv===5)nv=rollFace(playerDice[vi%playerDice.length]||'bone');vals[vi]=nv;}
      }

      if(!anyScoring(vals,playerCards,mats)){
        // Silver shield: save from one bust per match
        if(!shieldUsed&&playerShields>0){shieldUsed=true;continue;/* reroll same dice count */}
        // Martyr
        if(!martyrUsed&&has('martyr')){martyrUsed=true;continue;/* reroll same dice count */}
        // Cracked Bell
        if(!crackedBellUsed&&has('cracked_bell')){crackedBellUsed=true;busted=true;break;}
        busted=true;break;
      }

      // Last stand
      if(has('last_stand')&&numDice===1&&(vals[0]===1||vals[0]===5)){turnBank+=600;numDice=0;break;}

      // Score + keep
      const sel=playerSelectDice(vals,playerCards,mats);
      let rollPts=sel.pts;

      // Echo: +25% if previous roll scored
      if(has('the_echo')&&echoReady){rollPts=Math.floor(rollPts*1.35);}
      echoReady=echoArmed;echoArmed=true;

      // Chain Lightning: track
      if(has('chain_lightning'))chainCount++;

      // Track triples for twin_flames
      if(sel.triplesFired)sel.triplesFired.forEach(f=>{turnTriples[f]=true;});

      // Track scoring types for collector
      if(sel.pts>0){
        if(vals.some(v=>v===1))turnScoringTypes.single1=true;
        if(vals.some(v=>v===5))turnScoringTypes.single5=true;
        if(sel.triplesFired&&sel.triplesFired.length>0)turnScoringTypes.triple=true;
      }

      turnBank+=rollPts;
      numDice-=sel.kept;
      if(numDice<=0)numDice=6;

      if(playerShouldBank(turnBank,numDice,pPts,oPts,rung.target,skill,playerCards,turnRolls,safeTurnStreak))break;
    }

    if(busted){
      // Second Wind: bust → mini-turn with 3 dice
      if(!secondWindUsed&&has('second_wind')){
        secondWindUsed=true;
        const swVals=[];for(let i=0;i<3;i++)swVals.push(rollFace(playerDice[i%playerDice.length]||'bone'));
        const swScore=scoreRoll(swVals,playerCards).total;
        if(swScore>0){pPts+=swScore;/* rescued */}
        busted=true;// still counts as bust for streaks
      }
      // Thick Skin: first bust, bank half
      if(!thickSkinUsed&&has('thick_skin')&&turnBank>0){
        thickSkinUsed=true;
        pPts+=Math.floor(turnBank/2);
        safeTurnStreak=0;consecutiveBusts++;chainCount=0;
        if(has('gamblers_ghost'))ghostDieNext=true;
        if(pPts>=rung.target)return{win:true,turns:turnNum,pPts,oPts};
      }
      // Drunkard's Prayer: 30% bust → +100
      else if(has('drunkards_prayer')&&Math.random()<0.30){
        let bonus=100;if(alchemistActive)bonus*=2;
        pPts+=bonus;
      }
      // Phoenix Ash: bust → bank turn pts
      else if(!phoenixUsed&&has('phoenix_ash')&&turnBank>0){
        phoenixUsed=true;pPts+=turnBank;
      }

      safeTurnStreak=0;
      consecutiveBusts++;
      chainCount=0;
      if(has('gamblers_ghost'))ghostDieNext=true;
      // Brass reckless penalty: lose points on bust
      if(brassPenalty>0)pPts=Math.max(0,pPts-brassPenalty);

      // Loose Thread: 2 consecutive busts → +400
      if(has('loose_thread')&&consecutiveBusts>=2){
        let bonus=400;if(alchemistActive)bonus*=2;
        pPts+=bonus;consecutiveBusts=0;
      }

      // Boss challenge bust
      if(rung.boss==='KNIGHTS_CHALLENGE'&&bossState.challengeActive){
        bossState.challengeActive=false;pPts=Math.max(0,pPts-500);
      }
    }else{
      // ==== BANK ====
      let bankAmt=turnBank;
      consecutiveBusts=0;
      bankCount++;

      if(has('the_hearth')&&turnRolls===1)bankAmt+=100;
      if(has('the_hare')&&turnRolls===1)bankAmt+=100;
      if(has('thrifty_gambler')&&bankAmt>=400&&bankAmt<=600)bankAmt+=150;
      if(has('beggars_bowl')&&!beggarsBowlUsed){beggarsBowlUsed=true;bankAmt+=150;}
      safeTurnStreak++;
      if(has('slow_burn')&&safeTurnStreak%3===0)bankAmt+=300;
      if(has('fools_gold')&&bankAmt>0&&bankAmt%500===0)bankAmt+=300;
      if(has('greedy_hands')&&bankAmt<250){let mult=2;if(alchemistActive)mult=4;bankAmt*=mult;}
      if(has('underdog')&&(oPts-pPts)>=1000)bankAmt+=200;
      if(has('chain_lightning')&&chainCount>0){bankAmt+=(chainCount-1)*50;}
      if(has('the_collector')){
        const tc=Object.keys(turnScoringTypes).length;
        if(tc>=3)bankAmt+=100;
      }
      if(has('high_roller')&&bankAmt>=800)bankAmt+=200;
      if(has('blood_tithe')){let cost=50;if(alchemistActive)cost*=2;bankAmt-=cost;}
      if(has('twin_flames')&&Object.keys(turnTriples).length>=2)bankAmt+=750;
      if(has('the_grudge')&&grudgeStack>0){bankAmt+=grudgeStack;grudgeStack=0;}
      if(has('the_whetstone')){bankAmt+=Math.min(turnRolls,3)*50;}
      if(has('fortunes_wheel')&&bankCount%5===0)bankAmt*=2;
      if(has('last_call')&&(pPts+bankAmt)>=rung.target){bankAmt=Math.floor(bankAmt*1.5);}
      if(has('hot_streak')&&safeTurnStreak>=3)hotStreakReady=true;
      if(has('kings_ransom')&&(pPts+bankAmt-oPts)>=3000)bankAmt+=1000;
      if(has('iron_crown')&&turnRolls>1&&numDice===6)bankAmt+=500;// hot dice approx

      // All In: one-shot, sim as double bank mid-game if behind
      if(!allInUsed&&has('all_in')&&oPts>pPts&&bankAmt>=400){
        allInUsed=true;
        bankAmt*=2;
        if((pPts+bankAmt)<rung.target)bankAmt-=500;
      }

      // Boss attacks on bank
      if(rung.boss==='STICKY_FINGERS'&&!bossState.stickyFingersUsed&&bankAmt<300){
        bossState.stickyFingersUsed=true;oPts+=bankAmt;bankAmt=0;
      }
      if(rung.boss==='MERCHANTS_TAX'){const tax=Math.ceil(bankAmt*0.1);bankAmt-=tax;oPts+=tax;}
      if(rung.boss==='DIVINE_TITHE'){const tithe=Math.ceil(bankAmt*0.1);bankAmt-=tithe;oPts+=tithe;}
      if(rung.boss==='KNIGHTS_CHALLENGE'&&bossState.challengeActive){
        bossState.challengeActive=false;if(bankAmt<500)pPts=Math.max(0,pPts-500);
      }

      chainCount=0;
      pPts+=bankAmt;
      if(pPts>=rung.target)return{win:true,turns:turnNum,pPts,oPts};
    }

    // ==== OPPONENT TURN ====
    let oppBank=0;
    let oppDiceLeft=6;
    let oppRolls=0;
    let sootyActive=false;
    // Broken Lantern: once per match, opp plays blind → sim as 30% score reduction + early bank
    let lanternThisTurn=false;
    if(!lanternUsed&&has('broken_lantern')&&turnNum>=3){lanternUsed=true;lanternThisTurn=true;}

    if(cardMods.leakyCup&&turnNum%4===0&&turnNum>0)oppDiceLeft=5;
    if(has('the_jinx')&&turnNum%3===0){let red=1;if(fenceActive)red=1;oppDiceLeft=Math.max(3,oppDiceLeft-red);}

    while(true){
      oppRolls++;
      const vals=[];const oppMats=[];
      for(let i=0;i<oppDiceLeft;i++){
        const mat=rung.dice[i%rung.dice.length]||'bone';
        let v=rollFace(mat);
        if(sootyActive){while(v===1)v=rollFace(mat);}
        // Sawdust: first roll, dampen 2 dice (fence: 3)
        if(has('sawdust')&&oppRolls===1&&i<(fenceActive?3:2)){
          while(v===1||v===5)v=rollFace(mat);
        }
        vals.push(v);oppMats.push(mat);
      }
      sootyActive=false;

      let{total,used}=scoreRoll(vals,[],oppBank,{},oppMats);
      // Snake Oil: once per match, opp triple → next roll=half
      if(snakeOilActive){snakeOilActive=false;total=Math.floor(total/2);}
      // Broken Lantern: blind play → 30% worse scoring + force early bank
      if(lanternThisTurn){total=Math.floor(total*0.7);}
      if(total===0){
        if(has('blood_debt'))pPts+=250;
        if(has('thieves_luck')&&oppBank>0&&oppBank<200)pPts+=oppBank;
        oppBank=0;break;
      }

      // Sooty table
      if(has('sooty_table')){for(let f=2;f<=6;f++){if(vals.filter(v=>v===f).length>=3){sootyActive=true;break;}}}
      // Snake Oil trigger
      if(has('snake_oil')&&!snakeOilUsed){for(let f=1;f<=6;f++){if(vals.filter(v=>v===f).length>=3){snakeOilUsed=true;snakeOilActive=true;break;}}}
      // Slippery Table: 15% chance unkeep one die (fence: 18.75%)
      if(has('slippery_table')&&Math.random()<(fenceActive?0.1875:0.15)){
        const keptIdx=[];used.forEach((u,i)=>{if(u)keptIdx.push(i);});
        if(keptIdx.length>0){
          const slip=keptIdx[Math.floor(Math.random()*keptIdx.length)];
          used[slip]=false;
          // Recalculate total
          const remaining=vals.filter((_,i)=>!used[i]);
          const newScore=scoreRoll(remaining,[]).total;
          total=newScore;
        }
      }

      oppBank+=total;
      const keptCount=used.filter(u=>u).length;
      oppDiceLeft-=keptCount;
      if(oppDiceLeft<=0)oppDiceLeft=6;

      const effRung=cardMods.jestersMask?{...rung,chaotic:true}:rung;
      // Lantern: blind play forces early banking (50% chance to bank early)
      if(lanternThisTurn&&oppBank>100&&Math.random()<0.5){
        if(has('short_pour')){const pct=fenceActive?0.125:0.10;oppBank-=Math.ceil(oppBank*pct);}
        if(has('the_grudge'))grudgeStack=Math.min(grudgeStack+50,250);
        if(has('taxing_breath')&&oppBank>=50){oppBank-=50;pPts+=50;}
        if(has('thieves_luck')&&oppBank>0&&oppBank<200){pPts+=oppBank;oppBank=0;}
        else{oPts+=oppBank;}
        break;
      }
      if(oppShouldBank(effRung,oppBank,oppDiceLeft,oPts,pPts,rung.target,cardMods)){
        // Short Pour: -10% (fence: -12.5%)
        if(has('short_pour')){const pct=fenceActive?0.125:0.10;oppBank-=Math.ceil(oppBank*pct);}
        // Grudge: +50 per opp bank
        if(has('the_grudge'))grudgeStack=Math.min(grudgeStack+50,250);
        if(has('taxing_breath')&&oppBank>=50){oppBank-=50;pPts+=50;}
        if(has('thieves_luck')&&oppBank>0&&oppBank<200){pPts+=oppBank;oppBank=0;}
        else{oPts+=oppBank;}
        break;
      }
    }

    if(oPts>=rung.target)return{win:false,turns:turnNum,pPts,oPts};
    if(pPts>=rung.target)return{win:true,turns:turnNum,pPts,oPts};
  }
  return{win:false,turns:maxTurns,pPts,oPts};
}

// ════════════════════════════════════════════════
//  RUN SIMULATIONS — Focus on new cards
// ════════════════════════════════════════════════

const N=1000;
const boneDice=['bone','bone','bone','bone','bone','bone'];
/* Tier-appropriate player dice: player dice come from the tier reward BEFORE the rung */
const tierDice={
  0:['bone','bone','bone','bone','bone','bone'],      // vs Grog: starter
  1:['bone','bone','bone','bone','bone','iron'],       // vs Mabel: tier 0→1 reward
  2:['bone','bone','bone','iron','iron','flint'],      // vs Finnick: tier 1→2 reward
  3:['bone','bone','iron','iron','flint','lead'],      // vs Corvus: tier 2→3 reward
  4:['iron','iron','lead','lead','amber','flint'],     // vs Brutus: tier 3→4 reward
  5:['lead','lead','amber','amber','jade','flint'],    // vs Aldric: tier 4→5 reward
  6:['amber','amber','jade','jade','brass','silver'],  // vs Whisper: tier 5→6 reward
  7:['jade','jade','brass','brass','silver','crystal'], // vs Ambrose: tier 6→7 reward
};
const testRungs=[RUNGS[1],RUNGS[3],RUNGS[5]]; // Mabel, Corvus, Aldric

console.log('══════════════════════════════════════════════════════════════');
console.log('  GAMBIT BALANCE v2 — '+N+' games/card/rung  ('+CARDS.length+' cards)');
console.log('══════════════════════════════════════════════════════════════\n');

// ── SECTION 1: INDIVIDUAL CARD IMPACT ──
console.log('╔═══════════════════════════════════════════════════════════╗');
console.log('║  SOLO CARD IMPACT (avg skill, tier dice)                 ║');
console.log('╚═══════════════════════════════════════════════════════════╝\n');

for(const rung of testRungs){
  const pDice=tierDice[rung.id]||boneDice;
  let bWins=0;
  for(let i=0;i<N;i++){if(simMatch(rung,[],pDice,1).win)bWins++;}
  const baseWR=bWins/N*100;
  console.log(`--- vs ${rung.name} (target: ${rung.target}, dice: ${pDice.join(',')}) baseline: ${baseWR.toFixed(1)}% ---`);

  const results=[];
  for(const card of CARDS){
    let wins=0;
    for(let i=0;i<N;i++){if(simMatch(rung,[card.id],pDice,1).win)wins++;}
    const wr=wins/N*100;
    const delta=wr-baseWR;
    results.push({id:card.id,rarity:card.rarity,wr,delta});
  }
  results.sort((a,b)=>b.delta-a.delta);
  for(const r of results){
    const sign=r.delta>=0?'+':'';
    const flag=r.delta>15?' ⚠️OP':r.delta>10?' ⚡':r.delta<-2?' ❄️':'';
    console.log(`  ${r.id.padEnd(24)} [${r.rarity.padEnd(6)}] win: ${r.wr.toFixed(1).padStart(5)}%  (${sign}${r.delta.toFixed(1).padStart(5)})${flag}`);
  }
  console.log();
}

// ── SECTION 2: TOP COMBOS ──
console.log('╔═══════════════════════════════════════════════════════════╗');
console.log('║  CARD COMBOS (3 cards, avg skill)                       ║');
console.log('╚═══════════════════════════════════════════════════════════╝\n');

const combos=[
  {name:'Dice Manip',cards:['loaded_die','gamblers_thumb','warm_hands']},
  {name:'Opp Disrupt',cards:['the_jinx','sawdust','short_pour']},
  {name:'Opp Disrupt+Fence',cards:['the_jinx','short_pour','the_fence']},
  {name:'Bust Protect',cards:['thick_skin','drunkards_prayer','phoenix_ash']},
  {name:'Bust Protect v2',cards:['cracked_bell','second_wind','gamblers_ghost']},
  {name:'Score Boost',cards:['the_echo','chain_lightning','high_roller']},
  {name:'Tin Alchemist',cards:['the_alchemist','drunkards_prayer','blood_tithe','the_jinx']},
  {name:'Banking',cards:['the_hare','the_hearth','greedy_hands']},
  {name:'Grudge+Pour',cards:['the_grudge','short_pour','taxing_breath']},
  {name:'Streak Build',cards:['slow_burn','hot_streak','chain_lightning']},
  {name:'Risk/Reward',cards:['blood_tithe','twin_dice','twin_flames']},
  {name:'Meta: Brewer',cards:['the_brewer','phoenix_ash','old_bones']},
  {name:'Meta: DeadMan',cards:['dead_mans_hand','phoenix_ash','second_wind']},
  {name:'All In Risk',cards:['all_in','last_call','underdog']},
  {name:'Classic Aggro',cards:['flintlock','copper_pincher','scavenger']},
  {name:'Classic Safe',cards:['slow_burn','the_hearth','cracked_bell']},
  {name:'Classic Control',cards:['plague_wind','leaky_cup','taxing_breath']},
];

for(const rung of [RUNGS[3],RUNGS[5]]){
  const pDice=tierDice[rung.id]||boneDice;
  let bWins=0;
  for(let i=0;i<N;i++){if(simMatch(rung,[],pDice,1).win)bWins++;}
  const baseWR=bWins/N*100;
  console.log(`--- vs ${rung.name} (target: ${rung.target}, dice: ${pDice.join(',')}) baseline: ${baseWR.toFixed(1)}% ---`);

  const results=[];
  for(const combo of combos){
    let wins=0;
    for(let i=0;i<N;i++){if(simMatch(rung,combo.cards,pDice,1).win)wins++;}
    const wr=wins/N*100;
    const delta=wr-baseWR;
    results.push({name:combo.name,cards:combo.cards,wr,delta});
  }
  results.sort((a,b)=>b.delta-a.delta);
  for(const r of results){
    const sign=r.delta>=0?'+':'';
    const flag=r.delta>25?' ⚠️OP':r.delta>20?' ⚡':'';
    console.log(`  ${r.name.padEnd(22)} win: ${r.wr.toFixed(1).padStart(5)}%  (${sign}${r.delta.toFixed(1).padStart(5)})${flag}  [${r.cards.join(', ')}]`);
  }
  console.log();
}

// ── SECTION 3: RARITY BALANCE CHECK ──
console.log('╔═══════════════════════════════════════════════════════════╗');
console.log('║  RARITY BALANCE — avg delta per rarity                   ║');
console.log('╚═══════════════════════════════════════════════════════════╝\n');

const rung=RUNGS[3];// Corvus
const rungDice=tierDice[rung.id]||boneDice;
let bWins=0;
for(let i=0;i<N;i++){if(simMatch(rung,[],rungDice,1).win)bWins++;}
const baseWR=bWins/N*100;

const rarityData={tin:[],silver:[],gold:[]};
for(const card of CARDS){
  let wins=0;
  for(let i=0;i<N;i++){if(simMatch(rung,[card.id],rungDice,1).win)wins++;}
  const delta=wins/N*100-baseWR;
  if(rarityData[card.rarity])rarityData[card.rarity].push({id:card.id,delta});
}

for(const rar of ['tin','silver','gold']){
  const arr=rarityData[rar];
  arr.sort((a,b)=>b.delta-a.delta);
  const avg=arr.reduce((s,x)=>s+x.delta,0)/arr.length;
  const min=arr[arr.length-1];
  const max=arr[0];
  console.log(`${rar.toUpperCase()} (${arr.length} cards)  avg: ${avg>=0?'+':''}${avg.toFixed(1)}%  range: ${min.delta.toFixed(1)}% to +${max.delta.toFixed(1)}%`);
  console.log(`  Best: ${max.id} (+${max.delta.toFixed(1)})  Worst: ${min.id} (${min.delta.toFixed(1)})`);
  // Flag outliers
  const target={tin:{lo:0,hi:8},silver:{lo:2,hi:15},gold:{lo:-3,hi:18}};
  const t=target[rar];
  const outliers=arr.filter(x=>x.delta>t.hi||x.delta<t.lo);
  if(outliers.length>0){
    console.log(`  ⚠️ Outliers: ${outliers.map(x=>x.id+'('+x.delta.toFixed(1)+')').join(', ')}`);
  }
  console.log();
}

console.log('══════════════════════════════════════════════════════════════');
console.log('  SIMULATION COMPLETE');
console.log('══════════════════════════════════════════════════════════════');
