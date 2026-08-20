/* BOSS-HELD RETORT DOUBLE-PAY suspect: CFX.retort.bust pays for the
 * 'o' owner off the symmetric bust seam AND the bespoke NPC block at
 * ~35556 still deducts (the comment above it says pickpocket/slow_cook
 * left that block FOR this exact reason). Boss busts holding retort
 * t1: text says the player loses 400 - measure what actually leaves. */
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(fn,ms)=>{const t0=Date.now();while(Date.now()-t0<ms){try{if(fn())return true;}catch(e){}await sleep(120);}return false;};
const tap=el=>{if(!el)return false;const r=el.getBoundingClientRect();
  const o={bubbles:true,cancelable:true,clientX:r.left+r.width/2,clientY:r.top+r.height/2};
  el.dispatchEvent(new PointerEvent('pointerdown',o));
  el.dispatchEvent(new PointerEvent('pointerup',o));
  el.dispatchEvent(new MouseEvent('click',o));return true;};
if(!await until(()=>typeof launchBossMatch==='function'&&typeof G!=='undefined',20000))return {err:'no boot'};
window._fkDiscardOk=true;
launchBossMatch();
if(!await until(()=>G&&G.phase==='idle',20000))return {err:'no match'};
await sleep(3000);
G.oF=[{id:'retort',tier:1,charges:0,state:{}}];
G.pF=[];
try{famRenderRow();}catch(e){}
G.pPts=1000;try{updHUD();}catch(e){}
/* player takes a quick turn: keep the 1, bank 100 */
const Q=[1,2,3,4,6,2];
const realE=window._enchRollM;
window._enchRollM=(m,e)=>Q.length?Q.shift():realE(m,e);
/* the RIVAL deals through rollFace: all-dead first roll -> bust */
const realRF=window.rollFace;
const RQ=[2,2,3,3,4,6];
window.rollFace=m=>RQ.length?RQ.shift():realRF(m);
const HB=[];const _ohb=window.handleBank;window.handleBank=function(){HB.push({ph:G.phase,lk:!!G._rollLocked,sel:G.pool.filter(d=>d.sel&&!d.committed).length});return _ohb.apply(this,arguments);};
const PT=[];setInterval(()=>{try{const last=PT[PT.length-1];if(!last||last.p!==G.pPts||last.ph!==G.phase)PT.push({p:G.pPts,ph:G.phase,t:performance.now()|0});}catch(e){}},80);
tap(document.getElementById('btnRoll'));
if(!await until(()=>G.phase==='choosing',15000))return {err:'no roll'};
await sleep(500);
const one=G.pool.find(d=>!d.committed&&d.val===1);
tap(one.el);await sleep(300);
const p0=G.pPts;
tap(document.getElementById('btnBank'));
if(!await until(()=>G.pPts>p0,15000))return {err:'no bank',phase:G.phase,pPts:G.pPts,target:G.target,locked:!!G._rollLocked,emf:!!G._endMatchFired,HB:HB,PT:PT.slice(-16),rqLeft:RQ.length};
const pAfterBank=G.pPts;/* 1100 expected */
/* track the player's purse MINIMUM through the rival's bust */
let minP=pAfterBank;
const tPoll=setInterval(()=>{try{if(G.pPts<minP)minP=G.pPts;}catch(e){}},50);
if(!await until(()=>G.phase==='idle'&&(G.turnNum||0)>=2,90000)){clearInterval(tPoll);return {err:'no turn 2',minP:minP};}
await sleep(1500);
clearInterval(tPoll);
const lost=pAfterBank-minP;
return {pAfterBank:pAfterBank,minP:minP,lost:lost,HB:HB,PT:PT.slice(-16),
  oF:(G.oF||[]).map(c=>c.id),rqLeft:RQ.length,
  verdicts:{
    textSays400:lost===400,
    doublePaid800:lost===800,
    neverFired:lost===0},
  verdict:lost===400};
