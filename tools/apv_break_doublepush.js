/* BANKING A BREAK WITH NOTHING LEFT TO BREAK MUST COUNT THE KEEP ONCE.
 * Drives handleBank's _breakPending block down the fall-through path - a Break
 * armed on the bank press with no legal target - and counts the rows the one
 * selection produces. */
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
tap(document.getElementById('btnRoll'));
/* PRECONDITION, NOT A PAUSE. until() returns FALSE on timeout rather
   than throwing, so discarding this result meant every assertion below
   ran against a state that may never have arrived - and reported the
   result as a verdict about the game. Three probes were fixed one at a
   time for exactly this before it was swept for. */
const _pre = await until(()=>G.phase==='choosing',12000);
if (!_pre) return { skip: 'precondition never arrived: apv_break_doublepush had nothing to measure' };
await sleep(500);
G.target=999999;
const out={};
/* force a scoring selection: make every free die a 1, select them all, then
   arm a Break whose target list will be EMPTY because every other die is in
   the selection and therefore committed by the time _breakBegin runs. */
const free=G.pool.filter(d=>!d.committed);
free.forEach(d=>{d.val=1;d.sel=true;});
out.selected=free.length;
G._breakPending={src:free[0]};
G.kept=[];G.turnPts=0;
/* handleBank CLEARS G.kept when the bank lands, so reading it afterwards
   always says 0 - the pushes have to be captured as they happen. */
const pushes=[];
const realPush=G.kept.push.bind(G.kept);
G.kept.push=function(x){try{pushes.push({vals:(x&&x.vals||[]).slice(),pts:x&&x.pts});}catch(e){}return realPush(x);};
try{handleBank();}catch(e){out.err=String(e);}
await sleep(1000);
out.pushes=pushes;
out.pushCount=pushes.length;
out.banked=G._lastBankAmount;
/* the defect signature: the SAME selection pushed twice */
const keys=pushes.map(k=>JSON.stringify(k.vals)+'/'+k.pts);
out.duplicatePush=keys.length!==new Set(keys).size;
out.verdict={countedOnce:out.duplicatePush===false};
return out;
