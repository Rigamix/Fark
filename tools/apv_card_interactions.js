/* P844: the card-interaction rule enforced - a promise or arm is
 * voided by any effect that mutates the free pool outside the roll
 * path; visuals die with it; cosmetic changes and flag-only cards
 * leave it alone.
 *  A: stargazer -> sacrifice: ghosts+promise void, STARS BLUR told
 *  C: stargazer alone: promise still LANDS on the right dice (base
 *     mechanic unregressed - the void is not on the roll path)
 *  D: honeytrap -> double_or_nothing (flag-only): promise SURVIVES
 *  E: transmute armed -> sacrifice: arm + rings + hijack all swept */
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(fn,ms)=>{const t0=Date.now();while(Date.now()-t0<ms){try{if(fn())return true;}catch(e){}await sleep(120);}return false;};
const tap=el=>{if(!el)return false;const r=el.getBoundingClientRect();
  const o={bubbles:true,cancelable:true,clientX:r.left+r.width/2,clientY:r.top+r.height/2};
  el.dispatchEvent(new PointerEvent('pointerdown',o));
  el.dispatchEvent(new PointerEvent('pointerup',o));
  el.dispatchEvent(new MouseEvent('click',o));return true;};
if(!await until(()=>typeof launchSeat==='function'&&typeof S!=='undefined',20000))return {err:'no boot'};
if(typeof _getS==='function')_getS();
window._fkDiscardOk=true;
const logs=[];const _rfl=window.famLog;window.famLog=t=>{logs.push(String(t));try{_rfl(t);}catch(e){}};
const gz=()=>(window._pkGhosts||[]).filter(g=>g.isConnected).length;
const Q=[];
const realE=window._enchRollM;
window._enchRollM=(m,e)=>Q.length?Q.shift():realE(m,e);
const freshTurn=async q=>{
  /* relaunch with retries - a mid-match relaunch can swallow one
     launch (the ladder instrument's measured stall-start) */
  let ok=false;
  for(let a=0;a<3&&!ok;a++){
    try{delete S.pendingMatch;}catch(e){}
    /* un-spend the seat - launchSeat silently refuses a played seat */
    try{if(S.run&&S.run.night){S.run.night.seatsPlayed[0]=false;S.run.night.results[0]=null;}}catch(e){}
    window._fkDiscardOk=true;
    try{launchSeat(0);}catch(e){}
    ok=await until(()=>typeof G!=='undefined'&&G&&G.phase==='idle'
      &&(G.pool||[]).length===0&&(G.pTurns||0)===0,9000);
    if(!ok)await sleep(1500);
  }
  if(!ok)return false;
  await sleep(2200);
  Q.length=0;q.forEach(v=>Q.push(v));
  tap(document.getElementById('btnRoll'));
  if(!await until(()=>G.phase==='choosing',15000))return false;
  await sleep(500);return true;};
const R={};

/* ── A: stargazer then sacrifice ── */
if(!await freshTurn([1,1,5,2,3,4]))return {err:'no turn A'};
const sgA={id:'stargazer',fam:'starstone',kind:'active',tier:3,charges:3,state:{}};
const scA={id:'sacrifice',fam:'obsidian',kind:'active',tier:2,charges:3,state:{}};
G.pF=[sgA,scA];
CFX.stargazer.use(sgA,'p');await sleep(250);
const armedA={ghosts:gz(),peekLen:(G._famPeekVals||[]).length};
logs.length=0;
CFX.sacrifice.use(scA,'p');await sleep(1300);
R.legA={armed:armedA,afterSac:{ghosts:gz(),peek:G._famPeekVals,honey:G._famHoneyVal},
  blurTold:logs.some(t=>/STARS BLUR/.test(t))};

/* ── C: stargazer alone - the promise still lands ── */
if(!await freshTurn([1,1,5,2,3,4]))return {err:'no turn C',R};
const sgC={id:'stargazer',fam:'starstone',kind:'active',tier:3,charges:3,state:{}};
G.pF=[sgC];
CFX.stargazer.use(sgC,'p');await sleep(250);
const promisedC={};(G._famPeekVals||[]).forEach(p=>{promisedC[p.lane]=p.val;});
/* keep a scorer so the next roll is legal */
const oneC=(G.pool||[]).find(d=>!d.committed&&d.val===1);
if(oneC)tap(oneC.el);await sleep(350);
const keptLane=oneC?oneC.lane:null;
tap(document.getElementById('btnRoll'));
await until(()=>G.phase==='choosing'||G.phase==='idle',15000);
await sleep(600);
const landedC=(G.pool||[]).filter(d=>!d.committed).map(d=>({lane:d.lane,val:d.val}));
const holdsC=landedC.every(d=>promisedC[d.lane]===undefined||promisedC[d.lane]===d.val);
R.legC={promised:promisedC,keptLane,landed:landedC,promiseHolds:holdsC,
  ghostsAfterRoll:gz(),peekCleared:!G._famPeekVals};

/* ── D: honeytrap then a flag-only card - the promise survives ── */
if(!await freshTurn([2,2,1,3,4,6]))return {err:'no turn D',R};
const htD={id:'honeytrap',fam:'amber',kind:'active',tier:2,charges:3,state:{}};
const dnD={id:'double_or_nothing',fam:'flint',kind:'active',tier:1,charges:3,state:{}};
G.pF=[htD,dnD];
/* select the pair of 2s so honeytrap sees a pair on the table */
const twos=(G.pool||[]).filter(d=>!d.committed&&d.val===2).slice(0,2);
twos.forEach(d=>tap(d.el));await sleep(400);
const canH=CFX.honeytrap.canUse?CFX.honeytrap.canUse(htD,'p'):true;
const usedH=canH?CFX.honeytrap.use(htD,'p'):false;
await sleep(250);
const honeyArmed=G._famHoneyVal;
const usedDn=CFX.double_or_nothing.use?CFX.double_or_nothing.use(dnD,'p'):null;
await sleep(300);
R.legD={canH,usedH,honeyArmed,usedDn,honeySurvives:G._famHoneyVal===honeyArmed&&honeyArmed!=null,
  marks:(window._htMarks||[]).filter(g=>g.isConnected).length};

/* ── E: transmute armed then sacrifice - arm and rings swept ── */
if(!await freshTurn([1,1,5,2,3,4]))return {err:'no turn E',R};
const tmE={id:'transmute',fam:'jade',kind:'active',tier:2,charges:3,state:{}};
const scE={id:'sacrifice',fam:'obsidian',kind:'active',tier:2,charges:3,state:{}};
G.pF=[tmE,scE];
CFX.transmute.use(tmE,'p');await sleep(250);
const ringsArmed=document.querySelectorAll('#playerDiceRow .break-target').length;
const armedE=G._transArmed;
CFX.sacrifice.use(scE,'p');await sleep(1300);
R.legE={armedE,ringsArmed,afterSac:{transArmed:!!G._transArmed,
  rings:document.querySelectorAll('#playerDiceRow .break-target').length}};

return {R,verdicts:{
  A_ghostsVoid:R.legA.afterSac.ghosts===0&&!R.legA.afterSac.peek,
  A_playerTold:R.legA.blurTold,
  C_promiseStillLands:R.legC.promiseHolds&&R.legC.peekCleared&&R.legC.ghostsAfterRoll===0,
  D_flagOnlySurvives:R.legD.honeySurvives,
  E_armSwept:R.legE.armedE===true&&!R.legE.afterSac.transArmed&&R.legE.afterSac.rings===0},
  verdict:R.legA.afterSac.ghosts===0&&!R.legA.afterSac.peek&&R.legA.blurTold
    &&R.legC.promiseHolds&&R.legC.peekCleared
    &&R.legD.honeySurvives
    &&!R.legE.afterSac.transArmed&&R.legE.afterSac.rings===0};
