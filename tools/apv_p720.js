/* P720: draft layout + label fade, grudge bark plumbing, resume engine warm.
 * SUITE: exclude */
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(fn,ms)=>{const t0=Date.now();while(Date.now()-t0<ms){try{if(fn())return true;}catch(e){}await sleep(60);}return false;};
const vis=el=>{if(!el||!el.isConnected)return false;const s=getComputedStyle(el),r=el.getBoundingClientRect();
 return s.display!=='none'&&s.visibility!=='hidden'&&+s.opacity>0.05&&r.width>1&&r.height>1;};
const tap=el=>{if(!vis(el))return false;const r=el.getBoundingClientRect();
 const o={bubbles:true,cancelable:true,clientX:r.left+r.width/2,clientY:r.top+r.height/2};
 el.dispatchEvent(new PointerEvent('pointerdown',o));el.dispatchEvent(new PointerEvent('pointerup',o));
 el.dispatchEvent(new MouseEvent('click',o));return true;};
await until(()=>window.D3X&&D3X.frame,9000);
const out={};
tap(document.getElementById('hsBtnBottom'));await sleep(2000);
await until(()=>document.querySelector('.nrdie'),9000);
/* draft: labels invisible early, visible after their delay, spread + low */
const dice=[...document.querySelectorAll('#nrDice .nrdie')];
out.draft={count:dice.length,
 gap:getComputedStyle(document.getElementById('nrDice')).gap};
const sub0=dice[0]&&dice[0].querySelector('.sub');
out.draft.subEarly=sub0?+getComputedStyle(sub0).opacity:null;
await sleep(2600);
out.draft.subLate=sub0?+getComputedStyle(sub0).opacity:null;
if(dice[0]&&sub0){
 const dr=dice[0].querySelector('.d3host').getBoundingClientRect();
 const sr=sub0.getBoundingClientRect();
 out.draft.labelGapPx=+(sr.top-dr.bottom).toFixed(0);}
tap(document.querySelector('.nrdie'));await sleep(1200);
tap(document.getElementById('nrTakeBtn'));await sleep(2400);
await until(()=>typeof launchSeat==='function'&&S&&S.run,9000);
_getS();try{G=null;}catch(e){}
window._fkDiscardOk=true;
launchSeat(0);
let ok=await until(()=>typeof G!=='undefined'&&G&&G.phase==='idle',16000);
if(!ok){try{G=null;}catch(e){}launchSeat(0);
 ok=await until(()=>typeof G!=='undefined'&&G&&G.phase==='idle',16000);}
if(!ok)return {...out,err:'no idle'};

/* grudge bark: plumbing end to end via the front door */
G.rung.grudge=true;
DLG.trigger('GRUDGE_TAKEN');
await sleep(900);
const dt=document.getElementById('dlgText');
out.grudge={line:(dt&&dt.textContent||'').slice(0,60),
 hit:/die|remember|thief|ledger|stole|interest|carrying|took|settle/i.test(dt&&dt.textContent||'')};

/* resume warm: save a snapshot, resume, cannon must arrive */
try{saveMatchState();}catch(e){}
out.pending=!!S.pendingMatch;
window._fkDiscardOk=false;
try{G=null;}catch(e){}
delete window.CANNON;
resumeMatch();
ok=await until(()=>!!window.CANNON,6000);
out.cannonWarm=ok;
out.verdict=out.draft.count===3&&out.draft.subEarly===0&&out.draft.subLate>0.9
 &&out.draft.labelGapPx>10&&out.grudge.hit&&out.pending&&out.cannonWarm;
return out;
