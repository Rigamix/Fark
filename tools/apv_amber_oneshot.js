/* AMBER EATS ONE BUST, THEN IT IS GONE.
 * The ruling: "saves the turn from the NEXT bust only - one bust, not the rest
 * of the turn". The old code never spent the flag on the path where it saved,
 * so 98.5% of measured turns never ended naturally. This drives doBust TWICE in
 * one turn with the flag armed once, and reads what happened each time.
 * The second call is the whole test: before the fix it was identical to the
 * first. */
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
await until(()=>typeof G!=='undefined'&&G&&G.phase==='idle',14000);

/* get into a live turn with dice on the table */
tap(document.getElementById('btnRoll'));
await until(()=>G.phase==='choosing',12000);
await sleep(500);

const out={};
G.target=999999;                 /* do not let the match end mid-probe */
G._wardArmed=false;              /* Ward would swallow the bust before Amber */

/* watch the bust EVENT, which is what pays Retort/Reprisal/slow_cook */
const seen=[],realFire=window.famFire;
window.famFire=function(ev){seen.push(ev);return realFire.apply(this,arguments);};

function snap(){return {flag:!!G._bustImmuneTurn,phase:G.phase,
  kept:(G.kept||[]).length,turnPts:G.turnPts||0,bustEvent:seen.indexOf('bust')>=0};}

/* arm it once, the way BREAK_TRIGGERS.amber does */
G.kept=[{vals:[1],mat:'bone',pts:100,dice:[]}];G.turnPts=100;
G._bustImmuneTurn=true;
out.armed=snap();

seen.length=0;
try{doBust();}catch(e){out.err1=String(e);}
await sleep(1500);
out.firstBust=snap();            /* expect: saved, flag now false, no bust event */

seen.length=0;
try{doBust();}catch(e){out.err2=String(e);}
await sleep(1800);
out.secondBust=snap();           /* expect: NOT saved - a real bust */

window.famFire=realFire;

out.verdict={
  firstSaved:      out.firstBust.bustEvent===false,
  flagSpent:       out.firstBust.flag===false,
  secondLanded:    out.secondBust.bustEvent===true,
  turnEnded:       out.secondBust.phase!=='choosing'||out.secondBust.kept===0
};
/* the wording has to say it is spent, not that the turn is immune */
out.copy={trigger:(typeof BREAK_TRIGGERS!=='undefined')?BREAK_TRIGGERS.amber.msg:null};
return out;
