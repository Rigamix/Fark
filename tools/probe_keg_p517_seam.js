/* THE SEAM THE SWEEP NEVER DROVE.
   The cross-reference reported that P517 turned a dormant Powder Keg write into
   a live penalty, but stated plainly that both halves were measured separately
   and the JOIN was never driven. This drives the join.

   The claim under test:
     _removeDieAt's Fair-Trade break branch removes a die from G.pool for THIS
     ROLL ONLY and deliberately leaves G.numDice alone, so numDice 6 / pool 5 is
     a legitimate state. Powder Keg then does G.numDice=G.pool.length, writing a
     stale 5. Post-P517 hot dice computes Math.min(6,5)=5 and the player is a
     lane short for the rest of the turn. Pre-P517 it recomputed to 6.

   Three arms, so the carrier is isolated rather than assumed:
     A  mismatch + keg   the accused path
     B  mismatch, NO keg the mismatch alone must be harmless
     C  keg, NO mismatch the keg alone must be harmless

   Pre-P517 needs no arm: that line was an unconditional
   G.numDice=G.matchDice.length, so its answer is the loadout by definition. */
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(f,ms)=>{const t=Date.now();while(Date.now()-t<ms){try{if(f())return true;}catch(e){}await sleep(50);}return false;};
if(typeof launchBossMatch!=='function')return{error:'globals missing'};

async function run(label,doMismatch,doKeg){
  try{
    _getS(); S.run=S.run||{}; S.run.tier=2;
    S.run.dice=['bone','iron','flint','lead','amber','brass'];
    S.run.cards=S.run.cards||[]; S.settings=S.settings||{}; S.settings.reducedMotion=true;
    launchBossMatch();
  }catch(e){return{label:label,error:'launch '+e.message};}
  if(!(await until(()=>typeof G!=='undefined'&&G&&G.rung,9000)))return{label:label,error:'no match'};
  await sleep(600);
  try{if(typeof startPTurn==='function')startPTurn();}catch(e){}
  await sleep(250);
  const loadout=(G.matchDice||[]).length;
  /* THE DENOMINATOR. "Short" must be measured against what the player had at
     the START OF THIS TURN, not against the loadout. The rival arms dice
     penalties on its own schedule, so an arm that happens to draw one begins at
     five of six lanes - and scoring that against the loadout reports P517 doing
     exactly its job as a defect. It did, once, before this line existed. */
  const atTurnStart=G.numDice;
  try{if(typeof handleRoll==='function')handleRoll();}catch(e){}
  if(!(await until(()=>G&&G.pool&&G.pool.length>0,9000)))return{label:label,error:'no pool'};
  await sleep(600);
  const rolled=G.pool.length, ndRolled=G.numDice;

  /* --- make the legitimate numDice/pool disagreement, via the REAL branch --- */
  let mismatch=null;
  if(doMismatch){
    const lane=2;
    G._fairTrade={lane:lane,was:G.matchDice[lane],borrowed:'obsidian'};
    G.matchDice[lane]='obsidian';
    try{_removeDieAt(lane);}catch(e){return{label:label,error:'removeDieAt '+e.message};}
    await sleep(200);
    mismatch={numDice:G.numDice,pool:G.pool.length,
              lanes:(G.pool||[]).map(d=>d.lane),
              ftCleared:G._fairTrade===null};
  }

  /* --- the keg --- */
  let afterKeg=null;
  if(doKeg){
    G.phase='choosing';
    try{CFX.powder_keg.use({});}catch(e){return{label:label,error:'keg '+e.message};}
    await sleep(900);
    afterKeg={numDice:G.numDice,pool:G.pool.length};
  }

  /* --- sweep the table so handleRoll takes the hot-dice branch ---
     The dice must actually BE there. A busted reroll empties the pool and the
     arm then passes without ever entering the branch - which is exactly how
     the first P517 verification produced a meaningless green. */
  if(!G.pool||!G.pool.length)return{label:label,skip:'pool empty before the sweep - retry'};
  G.phase='choosing';
  G._lastHotDice=false;
  const sweptCount=G.pool.length;
  G.pool.forEach(function(d){d.committed=true;});

  /* Sample AT the reset, not a second later. Reading numDice after a sleep
     reads whatever the NEXT roll did to it - a bust toll takes a die, and that
     lands as a phantom "short by 1" that has nothing to do with hot dice.
     Poll tight and latch the value the instant the branch sets its flag. */
  let atReset=null;
  const spin=setInterval(function(){
    if(atReset===null&&G&&G._lastHotDice===true)atReset=G.numDice;
  },10);
  try{if(typeof handleRoll==='function')handleRoll();}catch(e){}
  await until(()=>atReset!==null,3000);
  await sleep(900);
  clearInterval(spin);

  return {label:label, loadout:loadout, rolled:rolled, numDiceWhenRolled:ndRolled,
          afterMismatch:mismatch, afterKeg:afterKeg,
          diceSwept:sweptCount,
          hotDiceBranchFired:atReset!==null,
          numDiceAtReset:atReset,
          numDiceASecondLater:G.numDice,
          bustToolATollAfterwards:(atReset!==null&&G.numDice<atReset),
          numDiceAtTurnStart:atTurnStart,
          rivalPenaltyThisTurn:atTurnStart<loadout,
          preP517WouldHaveBeen:(G.matchDice||[]).length,
          shortBy:(atReset===null)?null:(atTurnStart-atReset)};
}

/* retry an arm until it actually exercises the branch, rather than reporting a
   green that came from an empty table */
async function arm(label,mm,keg){
  for(let a=0;a<4;a++){
    const r=await run(label+(a?' (retry '+a+')':''),mm,keg);
    /* An arm only counts if it built the state it claims to test. A mismatch
       arm whose _removeDieAt took the NORMAL path decremented numDice legally,
       and scoring that as a lost lane reports _dropLanes doing its job as a
       bug - which is what the first run of this probe did. */
    const windowFormed=!mm||(r.afterMismatch
        && r.afterMismatch.numDice===r.numDiceAtTurnStart
        && r.afterMismatch.pool<r.afterMismatch.numDice);
    if(!r.skip&&!r.error&&r.hotDiceBranchFired&&windowFormed)return r;
    if(r.afterMismatch&&!windowFormed)r.armInvalid='the roll-only window never formed - _removeDieAt took the normal path';
    await sleep(700);
    if(a===3)return Object.assign(r,{WARNING:'never exercised the hot-dice branch in 4 tries'});
  }
}

const A=await arm('A mismatch+keg',true,true);
const B=await arm('B mismatch only',true,false);
const C=await arm('C keg only',false,true);

const bad=x=>x&&!x.error&&x.shortBy>0;
return {
  A_MISMATCH_AND_KEG:A, B_MISMATCH_ONLY:B, C_KEG_ONLY:C,
  allArmsExercisedTheBranch:[A,B,C].every(x=>x&&x.hotDiceBranchFired===true),
  verdict:
    ![A,B,C].every(x=>x&&x.hotDiceBranchFired===true)
      ? 'INCONCLUSIVE - an arm never entered the hot-dice branch, so its green means nothing'
    : bad(A)&&!bad(B)&&!bad(C)
      ? 'DEFECT PRESENT - only mismatch+keg strands the player, and P517 is what makes it stick'
    : (!bad(A)&&!bad(B)&&!bad(C))
      ? 'FIXED - every arm holds its full lane count, all three having entered the branch'
      : 'UNEXPECTED - more than one arm moved, the carrier is not what was claimed'
};
