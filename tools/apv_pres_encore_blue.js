/* P828: encore's reroll runs BLUE - catch the crr-blue class inside
 * its 400ms window and the starstone spray, plus the reroll economics
 * (faces changed, turnRollCount advanced). */
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(fn,ms)=>{const t0=Date.now();while(Date.now()-t0<ms){try{if(fn())return true;}catch(e){}await sleep(60);}return false;};
const tap=el=>{if(!el)return false;const r=el.getBoundingClientRect();
  const o={bubbles:true,cancelable:true,clientX:r.left+r.width/2,clientY:r.top+r.height/2};
  el.dispatchEvent(new PointerEvent('pointerdown',o));
  el.dispatchEvent(new PointerEvent('pointerup',o));
  el.dispatchEvent(new MouseEvent('click',o));return true;};
if(!await until(()=>typeof launchSeat==='function'&&typeof G!=='undefined',20000))return {err:'no boot'};
launchSeat(0);
if(!await until(()=>G&&G.phase==='idle',14000))return {err:'no match'};
await sleep(3000);
G.pF=[{id:'encore',tier:1,charges:1,state:{}}];
try{famRenderRow();}catch(e){}
const SPLOG=[];const _osp=window._fxSpray;
window._fxSpray=function(el,col,n,o){SPLOG.push(col);return _osp.apply(this,arguments);};
const Q=[1,2,3,4,6,2];
const realE=window._enchRollM;
window._enchRollM=(m,e)=>Q.length?Q.shift():realE(m,e);
tap(document.getElementById('btnRoll'));
if(!await until(()=>G.phase==='choosing',15000))return {err:'no roll'};
await sleep(600);
tap(G.pool.find(d=>!d.committed&&d.val===1).el);await sleep(300);
[5,2,3,4,6].forEach(v=>Q.push(v));/* the encore redraw */
const rc0=G.turnRollCount;
famUse(0);
/* catch the class INSIDE the 400ms window */
const blueSeen=await until(()=>G.pool.some(d=>d.el&&d.el.classList.contains('crr-blue')),1500);
await sleep(900);/* resolve window done */
const blueGone=!G.pool.some(d=>d.el&&d.el.classList.contains('crr-blue'));
const blueSpray=SPLOG.filter(c=>c==='#8fa8ff').length;
return {blueSeen,blueGone,blueSpray,rcDelta:G.turnRollCount-rc0,
  charges:G.pF[0].charges,phase:G.phase,
  verdicts:{
    blueDuringReroll:blueSeen,
    cleanAfter:blueGone,
    starstoneMotes:blueSpray>=4,
    rollCounted:G.turnRollCount===rc0+1,
    chargeSpent:G.pF[0].charges===0},
  verdict:blueSeen&&blueGone&&blueSpray>=4&&G.turnRollCount===rc0+1&&G.pF[0].charges===0};
