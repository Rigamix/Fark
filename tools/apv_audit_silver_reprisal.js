/* REPRISAL: trailing by >=1000, a bank STEALS amt*P from the rival.
 * Leg A: oPts preset 2000, bank 100 -> steal 25 (tier1 P=0.25):
 * pPts 125, oPts 1975. Leg B (control): oPts dropped to 0 before the
 * next bank -> not trailing is irrelevant here (0-125<1000): bank
 * pays plain, oPts untouched. Dead wire: leg A pays plain 100. */
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
G.pF=[{id:'reprisal',tier:1,charges:0,state:{}}];
try{famRenderRow();}catch(e){}
G.oPts=2000;try{updHUD();}catch(e){}
const Q=[1,2,3,4,6,2];
const realE=window._enchRollM;
window._enchRollM=(m,e)=>Q.length?Q.shift():realE(m,e);
tap(document.getElementById('btnRoll'));
if(!await until(()=>G.phase==='choosing',15000))return {err:'no roll A'};
await sleep(500);
const one=G.pool.find(d=>!d.committed&&d.val===1);
tap(one.el);await sleep(300);
const p0=G.pPts,oA0=G.oPts;
tap(document.getElementById('btnBank'));
if(!await until(()=>G.pPts>p0,15000))return {err:'no bank A'};
const pGainA=G.pPts-p0,oLossA=oA0-G.oPts;
/* LEG B: next turn, rival purse emptied - control */
if(!await until(()=>G.phase==='idle'&&(G.turnNum||0)>=2,90000))return {err:'no turn 2'};
await sleep(2000);
G.oPts=0;try{updHUD();}catch(e){}
[1,2,3,4,6,2].forEach(v=>Q.push(v));
tap(document.getElementById('btnRoll'));
if(!await until(()=>G.phase==='choosing'&&(G.turnRollCount||0)===1,15000))return {err:'no roll B'};
await sleep(500);
const oneB=G.pool.find(d=>!d.committed&&d.val===1);
tap(oneB.el);await sleep(300);
const p1=G.pPts,oB0=G.oPts;
tap(document.getElementById('btnBank'));
if(!await until(()=>G.pPts>p1,15000))return {err:'no bank B'};
const pGainB=G.pPts-p1,oLossB=oB0-G.oPts;
return {pGainA:pGainA,oLossA:oLossA,pGainB:pGainB,oLossB:oLossB,
  verdicts:{
    trailingBankSteals:pGainA===125&&oLossA===25,
    controlPaysPlain:pGainB===100&&oLossB===0},
  verdict:pGainA===125&&oLossA===25&&pGainB===100&&oLossB===0};
