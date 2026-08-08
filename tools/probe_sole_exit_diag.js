/* Two P519 arms disagreed with the code as written. Measure, do not reason.
   Every read here is SYNCHRONOUS and immediately adjacent to the call, so
   nothing that happens later in the turn can be mistaken for what the call did.
   The previous arms sampled after a 300ms sleep, which is how a bust toll or a
   turn boundary gets read as the sacrifice's own effect. */
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
  try{if(typeof handleRoll==='function')handleRoll();}catch(e){}
  await until(()=>G&&G.pool&&G.pool.length>0,6000);
  await sleep(500);
  return G.pool.length>0;
}
const snap=t=>({at:t,md:G.matchDice.length,nd:G.numDice,pool:G.pool.length,
                lanes:(G.pool||[]).map(d=>d.lane),
                committed:(G.pool||[]).map(d=>!!d.committed),
                phase:G.phase});

/* ---- Q1: does numDice drop with matchDice, measured AT the call? ------- */
async function q1(){
  if(!(await fresh()))return{error:'no pool'};
  const before=snap('before');
  const ret=CFX.sacrifice.use({tier:1});
  const immediately=snap('immediately after use() returned');
  await sleep(300);
  const later=snap('after 300ms');
  await sleep(1200);
  const muchLater=snap('after 1.5s');
  return {ret:ret, before:before, immediately:immediately, later:later, muchLater:muchLater,
          droppedAtTheCall:(before.md-immediately.md)===1&&(before.nd-immediately.nd)===1,
          somethingRestoredItLater:immediately.nd!==later.nd};
}

/* ---- Q2: why did the loan lane not get excluded? ---------------------- */
async function q2(){
  if(!(await fresh()))return{error:'no pool'};
  const pool=G.pool.map(d=>({lane:d.lane,committed:!!d.committed,shattered:!!d._shattered}));
  const top=G.pool[G.pool.length-1];
  G._fairTrade={lane:top.lane,was:G.matchDice[top.lane],borrowed:'obsidian'};
  const ftLaneSeen=(G._fairTrade&&typeof G._fairTrade.lane==='number')?G._fairTrade.lane:-1;
  const targets=CFX.sacrifice._targets().map(d=>d.lane);
  /* and what the card would actually pick */
  const t=CFX.sacrifice._targets();
  const wouldPick=t.length?t[t.length-1].lane:null;
  return {poolAsSeen:pool, topElementLane:top.lane, ftLaneInsideTargets:ftLaneSeen,
          targets:targets, wouldPick:wouldPick,
          loanExcluded:targets.indexOf(top.lane)===-1,
          poolIsLaneOrdered:pool.every((p,n)=>n===0||p.lane>=pool[n-1].lane)};
}

const Q1=await q1(); await sleep(500);
const Q2=await q2();
return {Q1_numDice:Q1, Q2_loanBan:Q2};
