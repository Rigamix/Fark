/* HONEYTRAP: keep a pair of 5s, arm AFTER the commit roll fully
 * settles (the roll path ends in _clearRollForces - "spent by this
 * roll either way" - so arming mid-animation is eaten by the roll in
 * flight; first probe draft hit exactly that), then the NEXT real
 * roll must pull a free die to 5 through famApplyRollForces. */
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
G.pF=[{id:'honeytrap',tier:1,charges:1,state:{}}];
try{famRenderRow();}catch(e){}
const Q=[5,5,2,3,4,6];
const realE=window._enchRollM;
window._enchRollM=(m,e)=>Q.length?Q.shift():realE(m,e);
tap(document.getElementById('btnRoll'));
if(!await until(()=>G.phase==='choosing'&&(G.turnRollCount||0)===1,15000))return {err:'no choosing'};
await sleep(400);
const fives=G.pool.filter(d=>!d.committed&&d.val===5);
if(fives.length<2)return {err:'no pair',vals:G.pool.map(d=>d.val)};
tap(fives[0].el);await sleep(150);tap(fives[1].el);await sleep(250);
/* commit the pair by rolling; queue a 1 to keep next + dead rest */
[1,2,3,4].forEach(v=>Q.push(v));
tap(document.getElementById('btnRoll'));
/* wait for the ROLL ITSELF to settle - turnRollCount===2 AND choosing
   again - not for kept.length, which goes true at commit time while
   the dice are still in the air */
if(!await until(()=>G.phase==='choosing'&&(G.turnRollCount||0)===2,20000))return {err:'no settle 2'};
await sleep(600);
if(G._famHoneyVal)return {err:'pre-armed?'};
famUse(0);
await sleep(250);
const armedVal=G._famHoneyVal;
if(!armedVal)return {err:'arm failed',pairs:_tablePairs(),kept:(G.kept||[]).map(k=>k.vals),charges:G.pF[0].charges};
/* the next REAL roll: select the 1, roll the remaining 3 */
const one=G.pool.find(d=>!d.committed&&d.val===1);
if(!one)return {err:'no 1',armedVal};
tap(one.el);await sleep(250);
[2,3,4].forEach(v=>Q.push(v));
tap(document.getElementById('btnRoll'));
if(!await until(()=>G.phase==='choosing'&&(G.turnRollCount||0)===3||G.phase==='opp',20000))return {err:'no roll 3',armedVal};
await sleep(600);
const free=G.pool.filter(d=>!d.committed&&!d._frozen);
const pulled=free[0];
return {armedVal:armedVal,cleared:!G._famHoneyVal,charges:G.pF[0].charges,
  pulledVal:pulled?pulled.val:null,freeVals:free.map(d=>d.val),
  verdicts:{
    armedWithPairValue:armedVal===5,
    forceFiredOnRealRoll:!!pulled&&pulled.val===5,
    consumed:!G._famHoneyVal,
    spent:G.pF[0].charges===0},
  verdict:armedVal===5&&!!pulled&&pulled.val===5&&!G._famHoneyVal&&G.pF[0].charges===0};
