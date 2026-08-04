/* SUITE: exclude - superseded by apv_bust_settle.js, which asserts the same
 * thing against the shipped funnel. Kept because it measures the SECOND roll
 * specifically, which is where the rival gate failed, and that is worth being
 * able to re-run by hand. It measures; it does not claim. */
/* MEASURE (v2): first roll is left natural so the physics batch is definitely
 * live, then a die is committed and the SECOND roll is forced into a
 * non-scoring pattern. Timestamps the bust word against the dice tape. */
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(fn,ms)=>{const t0=Date.now();while(Date.now()-t0<ms){try{if(fn())return true;}catch(e){}await sleep(60);}return false;};
const vis=el=>{if(!el||!el.isConnected)return false;const s=getComputedStyle(el),r=el.getBoundingClientRect();
 return s.display!=='none'&&s.visibility!=='hidden'&&+s.opacity>0.05&&r.width>1&&r.height>1;};
const tap=el=>{if(!vis(el))return false;const r=el.getBoundingClientRect();
 const o={bubbles:true,cancelable:true,clientX:r.left+r.width/2,clientY:r.top+r.height/2};
 el.dispatchEvent(new PointerEvent('pointerdown',o));el.dispatchEvent(new PointerEvent('pointerup',o));
 el.dispatchEvent(new MouseEvent('click',o));return true;};

tap(document.getElementById('hsBtnBottom'));await sleep(1800);
await until(()=>{const d=document.querySelector('.nrdie');return d&&d._floatDone;},9000);
tap(document.querySelector('.nrdie'));await sleep(1300);
tap(document.getElementById('nrTakeBtn'));await sleep(2200);
const pc=[...document.querySelectorAll('.ptcard')].filter(vis)[0];if(pc){tap(pc);await sleep(1700);}
const sit=[...document.querySelectorAll('span,div,button')].filter(e=>vis(e)&&e.children.length<=1&&/^SIT\s*DOWN$/i.test((e.textContent||'').trim()))[0];
if(sit){tap(sit);if(sit.parentElement)tap(sit.parentElement);}
await until(()=>vis(document.getElementById('screen-match')),9000);
/* PRECONDITION, NOT A PAUSE. until() returns FALSE on timeout rather
   than throwing, so discarding this result meant every assertion below
   ran against a state that may never have arrived - and reported the
   result as a verdict about the game. Three probes were fixed one at a
   time for exactly this before it was swept for. */
const _pre = await until(()=>typeof G!=='undefined'&&G&&G.phase==='idle',14000);
if (!_pre) return { skip: 'precondition never arrived: apv_bust_settle_p2 had nothing to measure' };
await sleep(500);

const out={BUST_PAUSE_MS:(typeof BUST_PAUSE_MS!=='undefined'?BUST_PAUSE_MS:null)};
const bov=document.getElementById('bust-ov');

/* ── helper: watch one roll and report tape-vs-flash ── */
async function watch(label,ms){
  let tFirst=null,tLast=null,maxTape=0,peak=0,flashAt=null;
  const t0=performance.now();
  const mo=new MutationObserver(()=>{if(flashAt===null&&bov.classList.contains('flash'))flashAt=performance.now();});
  mo.observe(bov,{attributes:true,attributeFilter:['class']});
  const trace=[];
  for(let i=0;i*16<ms;i++){
    const now=performance.now();let moving=0;
    try{if(window.D3X&&D3X.dice)D3X.dice.forEach(function(d){
      if(!d.roll||!d.chip||!d.chip.closest)return;
      if(!d.chip.closest('#playerDiceRow'))return;
      moving++;const len=d.roll.sol&&d.roll.sol.frames?d.roll.sol.frames.length:0;
      if(len>maxTape)maxTape=len;});}catch(e){}
    if(moving>0){if(tFirst===null)tFirst=now;tLast=now;if(moving>peak)peak=moving;}
    if(i%8===0)trace.push({t:Math.round(now-t0),mv:moving,fl:bov.classList.contains('flash')});
    await sleep(16);
  }
  mo.disconnect();
  return {label:label,tapeFirstMs:tFirst===null?null:Math.round(tFirst-t0),
    tapeLastMs:tLast===null?null:Math.round(tLast-t0),
    tapeFrames:maxTape,tapeSolvedMs:maxTape?Math.round(maxTape*D3X.PHYS.dt*1000):null,
    peakDiceMoving:peak,flashMs:flashAt===null?null:Math.round(flashAt-t0),trace:trace};
}

/* ── roll 1: natural ── */
tap(document.getElementById('btnRoll'));
out.roll1=await watch('natural roll 1',3400);
out.phaseAfter1=G.phase;

/* commit one scoring die so a second roll is legal */
if(G.phase==='choosing'){
  const free=G.pool.filter(d=>!d.committed);
  const one=free.filter(d=>d.val===1)[0]||free.filter(d=>d.val===5)[0];
  if(one){toggleDie(one);await sleep(400);}
  out.keptAfterPick=G.kept.length;
}

/* ── roll 2: forced bust ── */
const CAND=[[2,2,3,4,6,6],[2,3,4,6,6],[2,3,4,6],[2,3,6],[3,4,6],[2,3],[2,6],[3],[2]];
const _mats=(G.matchDice||[]).slice();
let bi=0,PAT=null;
const freeN=G.pool.filter(d=>!d.committed).length;
for(const p of CAND){
  if(p.length!==freeN)continue;
  let s=true;try{s=anyScoring(p,effectiveCards(),_mats.slice(0,p.length),null);}catch(e){s=true;}
  if(s===false){PAT=p;break;}
}
out.freeBeforeRoll2=freeN;out.bustPattern=PAT?PAT.join(''):null;
if(!PAT)return Object.assign(out,{err:'no non-scoring pattern for '+freeN+' dice'});
window._enchRollM=function(){return PAT[(bi++)%PAT.length];};
window.rollFace=function(){return PAT[(bi++)%PAT.length];};
window.rollFaceSpur=function(){return PAT[(bi++)%PAT.length];};

let tDoBust=null;const realDoBust=window.doBust;
const rT0={v:0};
window.doBust=function(){tDoBust=performance.now();return realDoBust.apply(this,arguments);};

const t0b=performance.now();
tap(document.getElementById('btnRoll'));
out.roll2=await watch('forced bust roll 2',4200);
out.doBustMs=tDoBust===null?null:Math.round(tDoBust-t0b);
out.verdict={
  bustWordAtMs: out.roll2.flashMs,
  diceStillMovingUntilMs: out.roll2.tapeLastMs,
  bustShownBeforeSettleBy: (out.roll2.flashMs!==null&&out.roll2.tapeLastMs!==null)
      ? (out.roll2.tapeLastMs-out.roll2.flashMs) : null
};
return out;
