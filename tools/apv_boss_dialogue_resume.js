/* P818 resume leg: a boss match snapshot re-entered through
 * resumeMatch must RESTAMP the boss trait (the 5th-arg path with
 * snap.rung). Null the trait first to prove the restamp did it. */
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
/* bank once so a real boundary snapshot exists */
const Q=[1,1,1,2,3,4];/* LAST CALL voids sub-800 banks - bank a 1000 triple */
const realE=window._enchRollM;
window._enchRollM=(m,e)=>Q.length?Q.shift():realE(m,e);
tap(document.getElementById('btnRoll'));
if(!await until(()=>G.phase==='choosing',15000))return {err:'no roll'};
await sleep(500);
const ones=G.pool.filter(d=>!d.committed&&d.val===1);
tap(ones[0].el);await sleep(120);tap(ones[1].el);await sleep(120);tap(ones[2].el);await sleep(300);
tap(document.getElementById('btnBank'));
if(!await until(()=>G.pPts>0,15000))return {err:'no bank'};
if(!await until(()=>S&&S.pendingMatch,10000))return {err:'no snapshot'};
const snapIsBoss=!!S.pendingMatch.isBoss;
/* stale the identity, then resume the real snapshot */
window._lastSeatTrait=null;
window._fkDiscardOk=false;
resumeMatch();
const restamped=await until(()=>window._lastSeatTrait==='reckless',15000);
return {snapIsBoss,restamped,trait:window._lastSeatTrait,art:window._lastSeatArt,
  verdicts:{snapshotIsBoss:snapIsBoss,resumeRestampsTrait:restamped,artStaysNull:window._lastSeatArt===null},
  verdict:snapIsBoss&&restamped&&window._lastSeatArt===null};
