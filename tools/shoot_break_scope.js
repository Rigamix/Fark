/* BREAK IS MATCH-SCOPED: the die leaves THIS match and comes back next one.
 * Ruling (AUDIT_RESOLUTIONS.md): "the destroyed die returns fully restored at
 * the start of the player's NEXT match, not gone for the rest of the run." */
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
const p=[...document.querySelectorAll('.ptcard')].filter(vis)[0];if(p){tap(p);await sleep(1700);}
const sit=[...document.querySelectorAll('span,div,button')].filter(e=>vis(e)&&e.children.length<=1&&/^SIT\s*DOWN$/i.test((e.textContent||'').trim()))[0];
if(sit){tap(sit);if(sit.parentElement)tap(sit.parentElement);}
await until(()=>vis(document.getElementById('screen-match')),9000);
await until(()=>typeof G!=='undefined'&&G&&G.phase==='idle',14000);
_getS();
const before={runDice:(S.run.dice||[]).slice(), runEnch:JSON.stringify(S.run.dieEnch||[]),
  matchDice:(G.matchDice||[]).slice(), numDice:G.numDice};
tap(document.getElementById('btnRoll'));
await until(()=>G.phase==='choosing'||G.phase==='idle',14000);
await until(()=>!(D3X.dice||[]).some(d=>d.roll),12000);
await sleep(500);
/* break the die in seat 2 through the real path */
const victim=(G.pool||[]).filter(d=>!d.committed)[0];
if(!victim)return{skipped:'no free die'};
const victimLane=victim.lane, victimMat=G.matchDice[victimLane];
G._breakArmed=true;
let broke=false; try{broke=_breakDie(victim)!==false;}catch(e){return{err:String(e)};}
await sleep(400);
_getS();
const after={runDice:(S.run.dice||[]).slice(), runEnch:JSON.stringify(S.run.dieEnch||[]),
  matchDice:(G.matchDice||[]).slice(), numDice:G.numDice,
  pendingMatchDice:(S.pendingMatch&&S.pendingMatch.matchDice||[]).slice(),
  pendingHasEnchArr:!!(S.pendingMatch&&S.pendingMatch._enchArr)};
return {victimLane, victimMat, broke,
  RUN_ARRAY_UNTOUCHED: before.runDice.length===after.runDice.length && before.runEnch===after.runEnch,
  runDiceBefore:before.runDice.length, runDiceAfter:after.runDice.length,
  GONE_FROM_THIS_MATCH: after.matchDice.length===before.matchDice.length-1,
  matchDiceBefore:before.matchDice.length, matchDiceAfter:after.matchDice.length,
  SNAPSHOT_AGREES_WITH_LIVE: after.pendingMatchDice.length===after.matchDice.length,
  pendingLen:after.pendingMatchDice.length, pendingHasEnchArr:after.pendingHasEnchArr};
