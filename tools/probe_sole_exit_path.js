/* P519 - is the unwinnable match still reachable, and did the routing hold?

   Five arms. The first is the one that matters: walk the loadout down to a
   single die and try every way to remove it. If any of them succeeds,
   matchDice empties, the refill mints a lane:NaN die that nothing can remove,
   and the match is unwinnable while still looking live.

   The control arms exist because a floor that refuses EVERYTHING would also
   pass arm 1. Sacrifice must still work normally at six dice, or the fix has
   simply broken the card. */
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(f,ms)=>{const t=Date.now();while(Date.now()-t<ms){try{if(f())return true;}catch(e){}await sleep(50);}return false;};
if(typeof launchBossMatch!=='function')return{error:'globals missing'};

async function fresh(){
  _getS(); S.run=S.run||{}; S.run.tier=2;
  S.run.dice=['bone','iron','flint','lead','amber','brass'];
  S.run.cards=S.run.cards||[]; S.settings=S.settings||{}; S.settings.reducedMotion=true;
  launchBossMatch();
  if(!(await until(()=>typeof G!=='undefined'&&G&&G.rung,9000)))return false;
  await sleep(600);
  try{if(typeof startPTurn==='function')startPTurn();}catch(e){}
  await sleep(250);
  return true;
}
async function rollOut(){
  try{if(typeof handleRoll==='function')handleRoll();}catch(e){}
  await until(()=>G&&G.pool&&G.pool.length>0,6000);
  await sleep(500);
}
const lanesOf=()=>(G.pool||[]).map(d=>d.lane);
const nonFinite=()=>(G.pool||[]).filter(d=>typeof d.lane!=='number'||!isFinite(d.lane)).length;

/* ---- arm 1: the unwinnable match ------------------------------------- */
async function armEmpty(){
  if(!(await fresh()))return{error:'no match'};
  /* walk six down to one through the shipped remover */
  let guard=0;
  while(G.matchDice.length>1&&guard++<20){ _removeDieAt(G.matchDice.length-1); }
  const atOne={mdLen:G.matchDice.length,numDice:G.numDice};
  /* now try EVERY route to take the last one */
  const removeRefused = _removeDieAt(0)===false;
  const mdAfterRemove = G.matchDice.length;
  const sacOffered = !!(CFX.sacrifice.canUse&&CFX.sacrifice.canUse());
  let sacForced=null;
  try{ sacForced = CFX.sacrifice.use({tier:1}); }catch(e){ sacForced='threw: '+e.message; }
  const mdAfterSac = G.matchDice.length;
  /* and prove the NaN die cannot be minted even so */
  await rollOut();
  return {atOne:atOne, removeRefusedLastDie:removeRefused, mdAfterRemove:mdAfterRemove,
          sacrificeOffered:sacOffered, sacrificeForcedReturned:sacForced,
          mdAfterSacrifice:mdAfterSac,
          poolLanes:lanesOf(), nonFiniteLanes:nonFinite(),
          UNWINNABLE: mdAfterSac===0||nonFinite()>0};
}

/* ---- arm 2: sacrifice must still work normally ------------------------ */
async function armNormal(){
  if(!(await fresh()))return{error:'no match'};
  await rollOut();
  const before={md:G.matchDice.length,nd:G.numDice,pool:G.pool.length};
  const offered=!!CFX.sacrifice.canUse();
  const used=CFX.sacrifice.use({tier:1});
  /* SAMPLE AT THE CALL. Reading after a sleep reads the next turn: the first
     run of this arm caught a turn boundary and scored startPTurn's numDice as
     the sacrifice's effect. */
  const after={md:G.matchDice.length,nd:G.numDice,pool:G.pool.length};
  const lanesNow=lanesOf(), nfNow=nonFinite();
  await sleep(300);
  return {before:before, offered:offered, used:used, after:after,
          afterASleep:{md:G.matchDice.length,nd:G.numDice,pool:G.pool.length},
          lanes:lanesNow, nonFiniteLanes:nfNow,
          droppedExactlyOne:(before.md-after.md)===1&&(before.nd-after.nd)===1};
}

/* ---- arm 3: D9, the loan lane must shift ------------------------------ */
async function armLoanShift(){
  if(!(await fresh()))return{error:'no match'};
  await rollOut();
  if(!G.pool.length)return{skip:'no pool'};
  /* put a loan on a LOW lane, sacrifice a HIGHER one; ft.lane must not move.
     then sacrifice a lane BELOW it and it must come down by one. */
  G._fairTrade={lane:1,was:G.matchDice[1],borrowed:'obsidian'};
  G.matchDice[1]='obsidian';
  const start=G._fairTrade.lane;
  CFX.sacrifice.use({tier:1});          // takes the highest free die
  await sleep(250);
  const afterHigh=G._fairTrade?G._fairTrade.lane:null;
  /* now force a removal below the loan */
  _removeDieAt(0);
  const afterBelow=G._fairTrade?G._fairTrade.lane:null;
  return {start:start, afterSacrificingAbove:afterHigh, afterRemovingBelow:afterBelow,
          heldWhenAbove:afterHigh===start, shiftedWhenBelow:afterBelow===start-1};
}

/* ---- arm 4: a borrowed die is not a legal target ---------------------- */
async function armLoanBan(){
  if(!(await fresh()))return{error:'no match'};
  await rollOut();
  if(!G.pool.length)return{skip:'no pool'};
  const top=G.pool[G.pool.length-1];
  G._fairTrade={lane:top.lane,was:G.matchDice[top.lane],borrowed:'obsidian'};
  G.matchDice[top.lane]='obsidian';
  /* CAPTURE THE LANE BEFORE THE CALL. _removeDieAt relanes the survivors, so
     reading top.lane afterwards reads a number the removal already shifted -
     which is how the first run of this arm scored a working ban as a failure. */
  const loanLaneBefore=top.lane;
  const targets=CFX.sacrifice._targets().map(d=>d.lane);
  const excluded=targets.indexOf(loanLaneBefore)===-1;
  CFX.sacrifice.use({tier:1});
  await sleep(250);
  return {loanLane:loanLaneBefore, targetsOfferred:targets,
          loanLaneAfterRelane:top.lane,
          loanExcluded:excluded,
          loanSurvived:!!G._fairTrade};
}

/* ---- arm 5: D14, the mid-turn snapshot must follow -------------------- */
async function armSnapshot(){
  if(!(await fresh()))return{error:'no match'};
  await rollOut();
  if(!G.pool.length)return{skip:'no pool'};
  const snapBefore=(S.pendingMatch&&S.pendingMatch.matchDice)?S.pendingMatch.matchDice.length:null;
  const liveBefore=G.matchDice.length;
  CFX.sacrifice.use({tier:1});
  await sleep(300);
  const snapAfter=(S.pendingMatch&&S.pendingMatch.matchDice)?S.pendingMatch.matchDice.length:null;
  return {snapBefore:snapBefore, liveBefore:liveBefore,
          snapAfter:snapAfter, liveAfter:G.matchDice.length,
          snapshotFollowed:(snapAfter!==null&&snapAfter===G.matchDice.length)};
}

const A=await armEmpty();     await sleep(500);
const B=await armNormal();    await sleep(500);
const C=await armLoanShift(); await sleep(500);
const D=await armLoanBan();   await sleep(500);
const E=await armSnapshot();

return {
  ARM1_unwinnable:A, ARM2_normal:B, ARM3_loanShift:C, ARM4_loanBan:D, ARM5_snapshot:E,
  verdict:
    (A.UNWINNABLE===true) ? 'FAIL - the unwinnable match is STILL reachable'
    : (!B.droppedExactlyOne) ? 'FAIL - the floor broke ordinary sacrifice'
    : (D.loanExcluded===false) ? 'FAIL - a borrowed die is still a legal sacrifice target'
    : (C.heldWhenAbove!==true||C.shiftedWhenBelow!==true) ? 'FAIL - the loan lane does not track removals'
    : (E.snapshotFollowed!==true) ? 'FAIL - the mid-turn snapshot did not follow'
    : 'PASS - last die protected, sacrifice still works, routing held'
};
