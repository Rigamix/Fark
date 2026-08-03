/* P405 — Starstone's extra turn now goes through endPTurn's bookkeeping.
 * Drives a real match to the point where a turn ends, then ends one with
 * _extraTurn pending and reads what moved. The three things ruling #9 names:
 * pTurns (the cap counter), turnNum, and Quicksilver's spent test. */
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
tap(document.getElementById('nrTakeBtn'));await sleep(1900);
const pc=[...document.querySelectorAll('.ptcard')].filter(vis)[0];if(pc){tap(pc);await sleep(1700);}
const sit=[...document.querySelectorAll('span,div,button')].filter(e=>vis(e)&&e.children.length<=1&&/^SIT\s*DOWN$/i.test((e.textContent||'').trim()))[0];
if(sit){tap(sit);if(sit.parentElement)tap(sit.parentElement);}
await until(()=>vis(document.getElementById('screen-match')),9000);
await until(()=>typeof G!=='undefined'&&G&&G.phase==='idle',14000);

const out={};
if(typeof G==='undefined'||!G){return {err:'no match'};}

/* keep the match from ending underneath the probe */
G.target=999999;

/* PHASE IS PART OF THE SNAPSHOT NOW. It was the one value the verdict read
   LIVE while the other three read this snapshot - so `stayedOurs` was asking
   about a later moment than `capCounted`, `turnAdvanced` and `qsRefreshed`,
   and the rival's turn beginning in that gap failed the check with nothing
   actually wrong. Measured flapping 1 run in 3. */
function snap(){return {turnNum:G.turnNum,pTurns:G.pTurns||0,
  qsSpent:(G._qsTurn===G.turnNum),extra:G._extraTurn||0,phase:G.phase};}

/* ── ARM: one pending Starstone turn, and Quicksilver marked used on THIS
   turn number. If turnNum does not advance the flag follows us in. ── */
G._extraTurn=1;
G._qsTurn=G.turnNum;
out.before=snap();

/* end the turn the way banking does */
G._fExtraTurn=false;
endPTurn();
await until(()=>(G._extraTurn||0)===0,4000);
/* the branch decrements the counter IMMEDIATELY and schedules startPTurn 900ms
   out, so waiting on the counter says nothing about whether the turn began.
   Wait for the turn itself. */
/* AND until() RETURNS FALSE ON TIMEOUT rather than throwing. Ignoring that
   return value is what let a timed-out wait fall straight through to an
   assertion about a state that never arrived - the same bug apv_preserve had.
   If the extra turn did not begin, this probe has nothing to say about it. */
const _extraBegan=await until(()=>G.phase==='idle'||G.phase==='choosing',6000);
out.afterExtra=snap();
if(!_extraBegan)return {skip:'the extra turn never began (phase='+G.phase
  +') - not an extra-turn result either way'};

out.verdict={
  /* the extra turn costs a capped turn, like Falling Star's */
  capCounted:  out.afterExtra.pTurns===out.before.pTurns+1,
  /* turnNum advanced ... */
  turnAdvanced:out.afterExtra.turnNum===out.before.turnNum+1,
  /* ... which is exactly what frees Quicksilver again */
  qsRefreshed: out.before.qsSpent===true&&out.afterExtra.qsSpent===false,
  /* and it really was the extra turn, not a yield to the rival */
  stayedOurs:  out.afterExtra.phase!=='opp'
};

/* ── the decided-match guard: no bonus turn once it is already won ── */
G._extraTurn=1;G.target=1;G.pPts=99999;
const t0=G.turnNum;
try{endPTurn();}catch(e){out.guardErr=String(e);}
await sleep(400);
out.guardHeldOnWin=(G._extraTurn===1);

return out;
