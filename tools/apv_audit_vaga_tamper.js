/* TAMPER: give the rival [slow_cook t1, retort t2]. Use t3 tamper ->
 * the HIGHEST tier (retort t2) breaks, charges 0, and the t3 steal
 * lifts 300. THEN the sharp question: force the rival's bust with the
 * broken retort - the famFire bus has NO broken filter, so if 400
 * still leaves the player's purse, breaking a PASSIVE is cosmetic. */
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
G.pF=[{id:'tamper',tier:3,charges:1,state:{}}];
G.oF=[{id:'slow_cook',tier:1,charges:0,state:{}},{id:'retort',tier:2,charges:0,state:{}}];
try{famRenderRow();}catch(e){}
G.oPts=1000;G.pPts=500;try{updHUD();}catch(e){}
const p0=G.pPts,o0=G.oPts;
famUse(0);
await sleep(400);
const retortInst=G.oF.find(c=>c.id==='retort');
const brokeHighest=!!(retortInst&&retortInst.broken);
const slowIntact=!G.oF.find(c=>c.id==='slow_cook').broken;
const stole300=(G.pPts-p0===300)&&(o0-G.oPts===300);
/* now the rival busts holding the BROKEN retort (t2 P=700) */
const Q=[1,2,3,4,6,2];
const realE=window._enchRollM;
window._enchRollM=(m,e)=>Q.length?Q.shift():realE(m,e);
const realRF=window.rollFace;
let RQ=[2,2,3,3,4,6];
window.rollFace=m=>RQ.length?RQ.shift():realRF(m);
tap(document.getElementById('btnRoll'));
if(!await until(()=>G.phase==='choosing',15000))return {err:'no roll',brokeHighest};
await sleep(500);
tap(G.pool.find(d=>!d.committed&&d.val===1).el);await sleep(300);
const p1=G.pPts;
tap(document.getElementById('btnBank'));
if(!await until(()=>G.pPts>p1,15000))return {err:'no bank',brokeHighest};
const pAfterBank=G.pPts;
let minP=pAfterBank;
const tPoll=setInterval(()=>{try{if(G.pPts<minP)minP=G.pPts;}catch(e){}},50);
if(!await until(()=>G.phase==='idle'&&(G.turnNum||0)>=2,90000)){clearInterval(tPoll);return {err:'no turn 2'};}
await sleep(1200);
clearInterval(tPoll);
const lostToBrokenRetort=pAfterBank-minP;
return {brokeHighest,slowIntact,stole300,rqLeft:RQ.length,
  lostToBrokenRetort:lostToBrokenRetort,charges:G.pF[0].charges,
  verdicts:{
    brokeHighestTier:brokeHighest,
    lowerCardUntouched:slowIntact,
    t3Stole300:stole300,
    rivalBusted:RQ.length===0,
    brokenPassiveStaysDead:lostToBrokenRetort===0,
    chargeSpent:G.pF[0].charges===0},
  verdict:brokeHighest&&slowIntact&&stole300&&lostToBrokenRetort===0&&G.pF[0].charges===0};
