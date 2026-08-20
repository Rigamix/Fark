/* PRESERVE, full round trip to the BANK: trap a kept 1, bank, survive
 * the rival's whole turn, and on return assert the die is genuinely
 * KEPT-AND-SCORED (G.kept entry, turnPts 100, a lane paid) - then bank
 * it immediately: pPts must rise by exactly 100. A visually-returned
 * but unscored die fails three of these. */
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(fn,ms)=>{const t0=Date.now();while(Date.now()-t0<ms){try{if(fn())return true;}catch(e){}await sleep(120);}return false;};
const tap=el=>{if(!el)return false;const r=el.getBoundingClientRect();
  const o={bubbles:true,cancelable:true,clientX:r.left+r.width/2,clientY:r.top+r.height/2};
  el.dispatchEvent(new PointerEvent('pointerdown',o));
  el.dispatchEvent(new PointerEvent('pointerup',o));
  el.dispatchEvent(new MouseEvent('click',o));return true;};
if(!await until(()=>typeof launchSeat==='function'&&typeof G!=='undefined',20000))return {err:'no boot'};
launchSeat(0);
if(!await until(()=>G&&G.phase==='idle',14000))return {err:'no match'};
await sleep(3000);
G.pF=[{id:'preserve',tier:1,charges:1,state:{}}];
try{famRenderRow();}catch(e){}
const Q=[1,2,3,4,6,2];
const realE=window._enchRollM;
window._enchRollM=(m,e)=>Q.length?Q.shift():realE(m,e);
tap(document.getElementById('btnRoll'));
if(!await until(()=>G.phase==='choosing',15000))return {err:'no choosing'};
await sleep(400);
const one=G.pool.find(d=>!d.committed&&d.val===1);
tap(one.el);
await sleep(300);
[5,2,3,4,6].forEach(v=>Q.push(v));
tap(document.getElementById('btnRoll'));
if(!await until(()=>(G.kept||[]).length>0,15000))return {err:'no commit'};
await sleep(400);
famUse(0);
await sleep(300);
const cap=G._famPreserve?JSON.parse(JSON.stringify(G._famPreserve)):null;
if(!cap)return {err:'no capture'};
const pPts0=G.pPts;
tap(document.getElementById('btnBank'));
if(!await until(()=>G.phase==='opp'||G.pPts>pPts0,15000))return {err:'no bank'};
const bankDelta=G.pPts-pPts0;
/* the whole rival turn passes */
if(!await until(()=>G.phase==='idle'&&(G.turnNum||0)>=2,90000))return {err:'no turn 2',bankDelta};
await sleep(2500);/* the amber return animation settles */
const kept=(G.kept||[]).map(k=>({pts:k.pts,vals:k.vals}));
const keptPts=(G.kept||[]).reduce((a,k)=>a+(k.pts||0),0);
const numDiceAtReturn=G.numDice;
/* the turn-end exits, on record with timestamps - the flaky failure
   ends the return turn paying ZERO and no driveable path does that */
const W=[];const mark=(n,x)=>W.push(Object.assign({n:n,ph:G&&G.phase,tp:G&&G.turnPts,t:performance.now()|0},x||{}));
['doBust','handleBank','handleYield','endPTurn','handleRoll'].forEach(fn=>{
  const orig=window[fn];window[fn]=function(){
    let stk='';try{stk=(new Error()).stack.split('\n').slice(2,4).join('|');}catch(e){}
    mark(fn,{stk:stk});return orig.apply(this,arguments);};});
/* the die is dealt ON THE ROLL (P744: _pvDie consumed by the deal
   walk, minted committed at its held lane) - so ROLL, then look */
[1,2,3,4].forEach(v=>Q.push(v));
mark('probe:rollTap');
tap(document.getElementById('btnRoll'));
if(!await until(()=>G.phase==='choosing'&&G.pool.some(d=>d._preserved),20000))return {err:'no return roll',kept};
await sleep(700);
const pv=G.pool.find(d=>d._preserved);
const elLive=!!(pv&&pv.el&&pv.el.isConnected&&pv.el.offsetParent!==null);
const pvCommitted=!!(pv&&pv.committed);
/* the LANE PAYMENT, player-visible: a preserved turn deals LOADOUT-1
   fresh dice (numDice write-trap showed startPTurn 6 -> _dropLanes 5;
   seat 0 runs six dice) - the deal itself is the fact */
const loadout=(G.matchDice||[]).length||6;
const freeCount=G.pool.filter(d=>!d.committed).length;
/* the economic close: keep the fresh 1 and bank - preserved 100 + new
   100 must both pay */
const fresh1=G.pool.find(d=>!d.committed&&d.val===1);
if(!fresh1)return {err:'no fresh 1',freeVals:G.pool.filter(d=>!d.committed).map(d=>d.val)};
mark('probe:dieTap',{conn:!!(fresh1.el&&fresh1.el.isConnected),onclick:!!(fresh1.el&&fresh1.el.onclick)});
tap(fresh1.el);await sleep(300);
const pPts1=G.pPts;
mark('probe:bankTap',{sel:G.pool.filter(d=>d.sel&&!d.committed).length,locked:!!G._rollLocked});
tap(document.getElementById('btnBank'));
if(!await until(()=>G.pPts>pPts1,15000))return {err:'no return bank',kept,
  turnPts:G.turnPts,phase:G.phase,pPts:G.pPts,pPts1:pPts1,freeCount:freeCount,
  sel:G.pool.filter(d=>d.sel&&!d.committed).map(d=>d.val),
  poolNow:G.pool.map(d=>({v:d.val,c:!!d.committed,s:!!d.sel})),
  turnNum:G.turnNum,W:W};
const returnBank=G.pPts-pPts1;
return {captured:cap,bankDelta:bankDelta,kept:kept,turnPtsAtReturn:keptPts,
  numDice:numDiceAtReturn,loadout:loadout,freeCount:freeCount,elLive:elLive,
  pvCommitted:pvCommitted,pvVal:pv?pv.val:null,returnBank:returnBank,
  verdicts:{
    capturedTheOne:cap.val===1&&cap.pts===100,
    trappingTurnBanked:bankDelta===100,
    returnedKept:kept.length===1&&kept[0].pts===100,
    lanePaid:freeCount===loadout-1,
    dieMintedOnRoll:elLive&&pvCommitted&&pv.val===1,
    returnBanks200:returnBank===200},
  verdict:cap.val===1&&bankDelta===100&&kept.length===1&&kept[0].pts===100
    &&freeCount===loadout-1&&elLive&&pvCommitted&&returnBank===200};
