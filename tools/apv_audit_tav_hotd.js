/* HAIR OF THE DOG, toll + prize in one match. Armed flag, bust before
 * any bank -> _hotdToll rubs a circle and clears the flag. Re-arm,
 * first bank -> DOUBLED (100->200). Next bank -> plain. (The real
 * loss-path arm is proven in _tav_loss.) */
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(fn,ms)=>{const t0=Date.now();while(Date.now()-t0<ms){try{if(fn())return true;}catch(e){}await sleep(120);}return false;};
const tap=el=>{if(!el)return false;const r=el.getBoundingClientRect();
  const o={bubbles:true,cancelable:true,clientX:r.left+r.width/2,clientY:r.top+r.height/2};
  el.dispatchEvent(new PointerEvent('pointerdown',o));
  el.dispatchEvent(new PointerEvent('pointerup',o));
  el.dispatchEvent(new MouseEvent('click',o));return true;};
if(!await until(()=>typeof launchSeat==='function'&&typeof S!=='undefined',20000))return {err:'no boot'};
if(typeof _getS==='function')_getS();
S.run.fcards=[{id:'hair_of_the_dog',tier:1,charges:0}];
S.run.points=5;S.run._hotdNext=true;
try{save();}catch(e){}
launchSeat(0);
if(!await until(()=>typeof G!=='undefined'&&G&&G.phase==='idle',14000))return {err:'no match'};
await sleep(3000);
const Q=[1,2,3,4,6,6];
const realE=window._enchRollM;
window._enchRollM=(m,e)=>Q.length?Q.shift():realE(m,e);
/* TURN 1: bust before any bank - keep the 1, roll the rest dead */
tap(document.getElementById('btnRoll'));
if(!await until(()=>G.phase==='choosing',15000))return {err:'no roll 1'};
await sleep(500);
tap(G.pool.find(d=>!d.committed&&d.val===1).el);await sleep(300);
[2,2,3,3,4].forEach(v=>Q.push(v));
const pts0=S.run.points;
tap(document.getElementById('btnRoll'));
if(!await until(()=>G.phase==='opp'||(G.turnNum||0)>=2,25000))return {err:'no bust'};
await sleep(800);
const tollCircle=pts0-(S.run.points||0);
const flagAfterToll=!!S.run._hotdNext;
/* re-arm for the prize half */
S.run._hotdNext=true;try{save();}catch(e){}
if(!await until(()=>G.phase==='idle'&&(G.turnNum||0)>=2,90000))return {err:'no turn 2',tollCircle};
await sleep(2000);
[1,2,3,4,6,2].forEach(v=>Q.push(v));
tap(document.getElementById('btnRoll'));
if(!await until(()=>G.phase==='choosing'&&(G.turnRollCount||0)===1,15000))return {err:'no roll 2'};
await sleep(500);
tap(G.pool.find(d=>!d.committed&&d.val===1).el);await sleep(300);
const p0=G.pPts;
tap(document.getElementById('btnBank'));
if(!await until(()=>G.pPts>p0,15000))return {err:'no bank 1',tollCircle};
const firstBank=G.pPts-p0;
const flagAfterPrize=!!S.run._hotdNext;
/* TURN 3: plain bank */
if(!await until(()=>G.phase==='idle'&&(G.turnNum||0)>=3,90000))return {err:'no turn 3',firstBank};
await sleep(2000);
[1,2,3,4,6,2].forEach(v=>Q.push(v));
tap(document.getElementById('btnRoll'));
if(!await until(()=>G.phase==='choosing'&&(G.turnRollCount||0)===1,15000))return {err:'no roll 3'};
await sleep(500);
tap(G.pool.find(d=>!d.committed&&d.val===1).el);await sleep(300);
const p1=G.pPts;
tap(document.getElementById('btnBank'));
if(!await until(()=>G.pPts>p1,15000))return {err:'no bank 2',firstBank};
const secondBank=G.pPts-p1;
return {tollCircle,flagAfterToll,firstBank,flagAfterPrize,secondBank,
  verdicts:{
    bustBeforeBankRubsCircle:tollCircle===1,
    tollClearsFlag:!flagAfterToll,
    firstBankDoubled:firstBank===200,
    prizeClearsFlag:!flagAfterPrize,
    secondBankPlain:secondBank===100},
  verdict:tollCircle===1&&!flagAfterToll&&firstBank===200&&!flagAfterPrize&&secondBank===100};
