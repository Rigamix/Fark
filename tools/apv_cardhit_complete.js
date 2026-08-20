/* P836: the completed cardHit rule, driven. The rival holds the_skim
 * (30% of every bank) and the player holds retort t1. One real bank:
 * the skim takes 300 of 1000 -> the seam fires -> retort answers with
 * 400 off their score. Dead seam: oPts ends 1300; live: 900. */
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
G.oCards=['the_skim'];
G.pF=[{id:'retort',tier:1,charges:0,state:{}}];
try{famRenderRow();}catch(e){}
G.oPts=1000;try{updHUD();}catch(e){}
const ERRS=[];window.addEventListener('error',e=>ERRS.push(String(e.message)+' @'+e.lineno));
const HITS=[];const _off=window.famFire;
window.famFire=function(seam,ev){if(seam==='cardHit')HITS.push({actor:ev&&ev.actor,src:ev&&ev.src});return _off.apply(this,arguments);};
/* FOUR 1s: the skim cuts 30% and Grog's LAST CALL refuses sub-800 - a 1000 bank became 700 and was VOIDED (found live by the first draft). 2000 -> skim 600 -> 1400 clears it. */
const Q=[1,1,1,1,2,3];
const realE=window._enchRollM;
window._enchRollM=(m,e)=>Q.length?Q.shift():realE(m,e);
tap(document.getElementById('btnRoll'));
if(!await until(()=>G.phase==='choosing',15000))return {err:'no roll'};
await sleep(600);
const ones=G.pool.filter(d=>!d.committed&&d.val===1);
tap(ones[0].el);await sleep(120);tap(ones[1].el);await sleep(120);tap(ones[2].el);await sleep(120);tap(ones[3].el);await sleep(300);
const p0=G.pPts;
tap(document.getElementById('btnBank'));
if(!await until(()=>G.pPts>p0,15000))return {err:'no bank',HITS,ERRS,phase:G.phase,turnPts:G.turnPts,pPts:G.pPts,oPts:G.oPts,status:(document.getElementById('statusBot')||{}).textContent};
await sleep(250);/* read BEFORE the rival banks */
const pGain=G.pPts-p0;      /* 2000 - 600 skim = 1400 */
const oNow=G.oPts;          /* 1000 + 600 skim - 400 retort = 1200 */
return {pGain,oNow,HITS,
  verdicts:{
    skimTook600:pGain===1400,
    seamFired:HITS.some(h=>h.actor==='p'&&h.src==='steal_pct'),
    retortAnswered400:oNow===1200},
  verdict:pGain===1400&&oNow===1200&&HITS.some(h=>h.src==='steal_pct')};
