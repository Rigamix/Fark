/* 1b SLEIGHT, index-level: stub rollFace with a known sequence. Their
 * deal draws faces 1-6 of the sequence; the sleight reroll draws 7-12.
 * If sleight truly fires, their final values ARE draws 7-12; if it is
 * dead, they are draws 1-6. The two batches differ at every index. */
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
/* my roll: scripted so a 1 exists to keep and bank */
const Q1=[1,2,2,3,4,6];
const realE=window._enchRollM;
window._enchRollM=(m,e)=>Q1.length?Q1.shift():realE(m,e);
tap(document.getElementById('btnRoll'));
if(!await until(()=>G.phase==='choosing',15000))return {err:'no choosing'};
await sleep(500);
/* arm sleight */
G.pF=[{id:'sleight',tier:1,charges:1,state:{}}];
try{famRenderRow();}catch(e){}
famUse(0);
await sleep(200);
const armed=!!G._famSleight;
/* keep the 1 and bank */
const one=(G.pool||[]).find(d=>!d.committed&&d.val===1);
if(!one)return {err:'no 1'};
tap(one.el);
await sleep(300);
/* the counting stub goes in NOW - their deal is the next consumer */
const SEQ=[2,3,4,6,2,3, 5,1,2,3,4,6];
const draws=[];
const realF=window.rollFace;
window.rollFace=function(m){
  const v=(draws.length<SEQ.length)?SEQ[draws.length]:realF(m);
  draws.push(v);return v;
};
tap(document.getElementById('btnBank'));
if(!await until(()=>(G.oppDice||[]).length>=6,20000))return {err:'no opp deal',draws:draws.length};
await sleep(700);/* the sleight reroll happens synchronously at deal; settle */
window.rollFace=realF;
const vals=(G.oppDice||[]).slice(0,6).map(d=>({lane:d.lane,val:d.val}));
const finalVals=vals.map(v=>v.val);
const dealBatch=SEQ.slice(0,6),rerollBatch=SEQ.slice(6,12);
const eq=(a,b)=>a.length===b.length&&a.every((x,i)=>x===b[i]);
return {armed:armed,flagAfter:!!G._famSleight,draws:draws.slice(0,14),final:finalVals,
  verdicts:{
    armed:armed,
    consumed:!G._famSleight,
    twelveDraws:draws.length>=12,
    valuesAreReroll:eq(finalVals,rerollBatch),
    valuesAreNotDeal:!eq(finalVals,dealBatch)
  },
  verdict:armed&&!G._famSleight&&draws.length>=12&&eq(finalVals,rerollBatch)};
