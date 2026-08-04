/* MEASURE: when does the BUST verdict appear, vs when do the player's dice
 * actually stop moving? Forces a guaranteed bust on the first roll by
 * overriding the face roller, then timestamps:
 *   tRoll      - the ROLL tap
 *   tFlash     - #bust-ov gains .flash (the word BUST on screen)
 *   tFirstTape - first frame any player die carries a physics tape (d.roll)
 *   tLastTape  - last frame any player die still carried one (settle)
 *   tapeMs     - the solved tape's own length, frames * PHYS.dt
 */
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
if (!_pre) return { skip: 'precondition never arrived: apv_bust_settle_player had nothing to measure' };
await sleep(600);

const out={D3_MATCH:window.D3_MATCH,phys:(window.D3X&&D3X.PHYS)?{on:D3X.PHYS.on,dt:D3X.PHYS.dt,cap:D3X.PHYS.cap}:null,
           d3xReady:!!(window.D3X&&D3X.ready),d3xFail:!!(window.D3X&&D3X.fail),
           BUST_PAUSE_MS:(typeof BUST_PAUSE_MS!=='undefined'?BUST_PAUSE_MS:null)};

/* guaranteed bust: pick a 6-face pattern anyScoring itself rejects (three
   pairs and two pairs both score in some loadouts, so ASK rather than assume) */
const CAND=[[2,3,4,2,3,4],[2,2,3,4,6,6],[2,3,4,6,6,4],[2,2,3,3,4,6],[3,4,6,2,3,6],[2,3,6,4,2,4]];
const _mats=(G.matchDice||['bone','bone','bone','bone','bone','bone']).slice(0,6);
let BUSTPAT=null;
out.candScan=CAND.map(function(p){
  let s=true;try{s=anyScoring(p,effectiveCards(),_mats,null);}catch(e){s='err:'+e;}
  if(s===false&&!BUSTPAT)BUSTPAT=p;
  return {p:p.join(''),scores:s};
});
if(!BUSTPAT)return Object.assign(out,{err:'no non-scoring pattern found'});
out.bustPattern=BUSTPAT.join('');
let bi=0;
window._enchRollM=function(){return BUSTPAT[(bi++)%BUSTPAT.length];};
window.rollFace=function(){return BUSTPAT[(bi++)%BUSTPAT.length];};
window.rollFaceSpur=function(){return BUSTPAT[(bi++)%BUSTPAT.length];};

const bov=document.getElementById('bust-ov');
let tFlash=null,tDoBust=null;
const realDoBust=window.doBust;
window.doBust=function(){tDoBust=performance.now();return realDoBust.apply(this,arguments);};
const mo=new MutationObserver(()=>{if(tFlash===null&&bov.classList.contains('flash'))tFlash=performance.now();});
mo.observe(bov,{attributes:true,attributeFilter:['class']});

let tFirstTape=null,tLastTape=null,tapeMs=null,maxTape=0,seenTapeIds=0;
const t0=performance.now();
tap(document.getElementById('btnRoll'));

const samples=[];
for(let i=0;i<420;i++){          /* ~7s at 16ms */
  const now=performance.now();
  let moving=0;
  try{
    if(window.D3X&&D3X.dice){
      D3X.dice.forEach(function(d){
        if(!d.roll||!d.chip||!d.chip.closest)return;
        if(!d.chip.closest('#playerDiceRow'))return;
        moving++;
        const len=d.roll.sol&&d.roll.sol.frames?d.roll.sol.frames.length:0;
        if(len>maxTape){maxTape=len;tapeMs=Math.round(len*D3X.PHYS.dt*1000);}
      });
    }
  }catch(e){}
  if(moving>0){if(tFirstTape===null)tFirstTape=now;tLastTape=now;seenTapeIds=Math.max(seenTapeIds,moving);}
  if(i%6===0){
    let nd=0,np=0,rowN=0;
    try{if(window.D3X&&D3X.dice){nd=D3X.dice.length;D3X.dice.forEach(function(d){if(d.phys)np++;});}}catch(e){}
    try{rowN=document.querySelectorAll('#playerDiceRow .die').length;}catch(e){}
    samples.push({t:Math.round(now-t0),moving:moving,flash:bov.classList.contains('flash'),
      nd:nd,phys:np,row:rowN,wq:(window.D3X&&D3X._waitQ)?D3X._waitQ.length:0,
      cannon:!!window.CANNON});
  }
  await sleep(16);
}
mo.disconnect();

out.tRollTapAt=0;
out.tFirstTapeMs = tFirstTape===null?null:Math.round(tFirstTape-t0);
out.tLastTapeMs  = tLastTape===null?null:Math.round(tLastTape-t0);
out.tDoBustMs    = tDoBust===null?null:Math.round(tDoBust-t0);
out.tFlashMs     = tFlash===null?null:Math.round(tFlash-t0);
out.tapeFrames   = maxTape;
out.tapeSolvedMs = tapeMs;
out.diceInTape   = seenTapeIds;
out.bustBeforeSettleMs = (out.tFlashMs!==null&&out.tLastTapeMs!==null)?(out.tLastTapeMs-out.tFlashMs):null;
out.trace=samples.filter(s=>s.t<3200);
return out;
