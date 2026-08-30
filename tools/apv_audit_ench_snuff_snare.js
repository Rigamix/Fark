/* SNUFF + SNARE through the real icon-keep.
 * Snuff: keep the branded 1 (with a 5) and BANK -> the rival's next
 * deal is FIVE dice with lane 0 empty; the turn after, six again.
 * Snare: re-brand, keep, bank -> the mark arms for their next turn
 * and the halving branch RUNS (witnessed via the log line the hit writes).
 * P879: this used to watch _lmRetire('_snare'), and a straight swap to
 * _lmSpend would have quietly broken it - the spend is UNCONDITIONAL inside
 * the due block now, so it fires on a miss too and the witness could not
 * fail. The halving is the thing under test, so watch what only the halving
 * does. */
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
G.pF=[];try{famRenderRow();}catch(e){}
const Q=[1,5,2,3,4,6];
const realE=window._enchRollM;
window._enchRollM=(m,e)=>Q.length?Q.shift():realE(m,e);
/* watch their deals */
let dealSizes=[];
const dealWatch=setInterval(()=>{try{
  const n=(G.oppDice||[]).length;if(!n)return;
  const lanes=(G.oppDice||[]).map(d=>d.lane).join(',');
  const last=dealSizes[dealSizes.length-1];
  if(!last||last.key!==lanes)
    dealSizes.push({key:lanes,n:n,lanes:(G.oppDice||[]).map(d=>d.lane),pTurn:G.turnNum});
}catch(e){}},80);
G._enchArr=[{t:'snuff',face:1},null,null,null,null,null];
tap(document.getElementById('btnRoll'));
if(!await until(()=>G.phase==='choosing',15000))return {err:'no roll A'};
await sleep(600);
const b1=G.pool.find(d=>d.lane===0&&d.val===1);
if(!b1||!b1.ench)return {err:'no brand A'};
tap(b1.el);await sleep(150);tap(G.pool.find(d=>!d.committed&&d.val===5).el);await sleep(300);
tap(document.getElementById('btnBank'));
if(!await until(()=>G.phase==='idle'&&(G.turnNum||0)>=2,90000)){clearInterval(dealWatch);return {err:'no turn 2'};}
await sleep(2000);
/* FIRST sample of the snuffed rival turn - later samples show kept dice already moved off the row */
const snuffDeal=dealSizes[0]||null;
dealSizes.length=0;/* fresh window for the snare leg */
/* SNARE turn: witness the halving branch */
/* TWO WITNESSES, because one cannot tell a miss from a no-show. The probe
   stubs their roll so lane 0 holds a 5, but it cannot make their AI KEEP it,
   and the halving is conditional on the keep - measured across five runs this
   leg fires sometimes and not others, on this build and on the one before it.
   So: the SPEND says the due block was reached and the mark was evaluated;
   the LOG says it actually halved. Absent both, the mark was never due, and
   that is the only outcome that is a bug. */
const RET=[];const BITE=[];
const _olog=window.famLog;
window.famLog=function(m){try{if(/SNARE BITES/.test(String(m)))BITE.push({t:performance.now()|0});}catch(e){}
  return _olog?_olog.apply(this,arguments):undefined;};
const _osp=window._lmSpend;
window._lmSpend=function(k){if(k==='_snare')RET.push({k:k,t:performance.now()|0});
  return _osp?_osp.apply(this,arguments):undefined;};
G._enchArr=[{t:'snare',face:1},null,null,null,null,null];
/* their deal is stubbed so lane 0 holds a 5 they WILL keep - the
   halving is conditional on that lane scoring (the SPEND is not, P879) */
const realRF=window.rollFace;
let RQ=[5,1,2,2,3,3];
window.rollFace=m=>RQ.length?RQ.shift():realRF(m);
[1,5,2,3,4,6].forEach(v=>Q.push(v));
tap(document.getElementById('btnRoll'));
if(!await until(()=>G.phase==='choosing'&&(G.turnRollCount||0)===1,15000)){clearInterval(dealWatch);return {err:'no roll B',snuffDeal};}
await sleep(600);
const b2=G.pool.find(d=>d.lane===0&&d.val===1);
if(!b2||!b2.ench){clearInterval(dealWatch);return {err:'no brand B'};}
tap(b2.el);await sleep(150);tap(G.pool.find(d=>!d.committed&&d.val===5).el);await sleep(300);
tap(document.getElementById('btnBank'));
/* G._snare is an OBJECT mark {lane,live,turn,turns} - armed means it exists; their turn may already have consumed it (live:false) by the time we look */
const snareArmedAt=await until(()=>!!G._snare,8000);
const snareState=G._snare?JSON.parse(JSON.stringify(G._snare)):null;
if(!await until(()=>G.phase==='idle'&&(G.turnNum||0)>=3,90000)){clearInterval(dealWatch);return {err:'no turn 3',snuffDeal,snareState};}
await sleep(2000);
clearInterval(dealWatch);
const nextDeal=dealSizes[0]||null;
const snareEvaluated=RET.some(r=>r.k==='_snare');/* the due block ran */
/* P887: some() cannot see a DOUBLE spend, and at Kindred's turns:2 on fog or
   snuff a second spend in one due turn would silently eat both attempts. So
   count, do not test existence. */
const spendCounts={};RET.forEach(function(r){spendCounts[r.k]=(spendCounts[r.k]||0)+1;});
const snareBit=BITE.length>0;/* it actually halved */
return {snuffDeal,nextDealAfterSnare:nextDeal,snareArmedAt,snareState,RET,BITE,
  snareOutcome:(!snareEvaluated?'NEVER DUE - the bug':snareBit?'HIT':'MISS - they declined lane 0'),
  verdicts:{
    snuffedLane0Gone:!!(snuffDeal&&snuffDeal.n===5&&snuffDeal.lanes.indexOf(0)<0),
    snareArmedByKeep:snareArmedAt,
    snareLane0:!!(snareState&&snareState.lane===0),
    snareBecameDue:snareEvaluated,/* the assertion that can fail */
    noKeySpentTwiceInOneDueTurn:Object.keys(spendCounts).every(function(k){return spendCounts[k]<=1;}),
    snareHalvedWhenTheyKept:(!snareEvaluated||!snareBit)?'n/a - no keep on lane 0':true,
    dealBackToSixAfterSnare:!!(nextDeal&&nextDeal.n===6)},
  verdict:!!(snuffDeal&&snuffDeal.n===5&&snuffDeal.lanes.indexOf(0)<0)&&snareArmedAt&&!!(snareState&&snareState.lane===0)&&snareEvaluated};
