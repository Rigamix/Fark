/* P703: the dim walks in over ~850ms in several steps, not one frame.
 * Samples one die's map identity from the moment it settles. SUITE: exclude */
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(fn,ms)=>{const t0=Date.now();while(Date.now()-t0<ms){try{if(fn())return true;}catch(e){}await sleep(40);}return false;};
const vis=el=>{if(!el||!el.isConnected)return false;const s=getComputedStyle(el),r=el.getBoundingClientRect();
 return s.display!=='none'&&s.visibility!=='hidden'&&+s.opacity>0.05&&r.width>1&&r.height>1;};
const tap=el=>{if(!vis(el))return false;const r=el.getBoundingClientRect();
 const o={bubbles:true,cancelable:true,clientX:r.left+r.width/2,clientY:r.top+r.height/2};
 el.dispatchEvent(new PointerEvent('pointerdown',o));el.dispatchEvent(new PointerEvent('pointerup',o));
 el.dispatchEvent(new MouseEvent('click',o));return true;};
/* the boot must finish before the first tap - probes that tap before D3X
 * exists hit a run where the playback never advances (headless quirk); the
 * instrumented diag that waits here settles every time */
await until(()=>window.D3X&&D3X.frame&&D3X._physPose,9000);
let fc=0,pc=0,fe=null,pe=null;
{const oF=D3X.frame;D3X.frame=function(){fc++;try{return oF.apply(this,arguments);}catch(e){if(!fe)fe=String(e&&e.stack||e).slice(0,300);throw e;}};
 const oP=D3X._physPose;D3X._physPose=function(){pc++;try{return oP.apply(this,arguments);}catch(e){if(!pe)pe=String(e&&e.stack||e).slice(0,300);throw e;}};}
let solveVals=null,rollVals=null;
{const oS=D3X._physSolve;D3X._physSolve=function(slots,vals){solveVals=(vals||[]).slice();
 const r=oS.apply(this,arguments);
 setTimeout(()=>{rollVals=(D3X.dice||[]).filter(d=>d.match&&d.roll).map(d=>d.roll.val);},120);
 return r;};}
for(let a=0;a<3;a++){tap(document.getElementById('hsBtnBottom'));await sleep(2000);
 await until(()=>document.querySelector('.nrdie'),9000);await sleep(500);
 tap(document.querySelector('.nrdie'));await sleep(1200);
 tap(document.getElementById('nrTakeBtn'));await sleep(2400);
 if(await until(()=>typeof launchSeat==='function'&&S&&S.run,9000))break;}
_getS();try{G=null;}catch(e){}
window._fkDiscardOk=true;
launchSeat(0);
let ok=await until(()=>typeof G!=='undefined'&&G&&G.phase==='idle',16000);
if(!ok){try{G=null;}catch(e){}launchSeat(0);
 ok=await until(()=>typeof G!=='undefined'&&G&&G.phase==='idle',16000);}
if(!ok)return {err:'no idle'};
const fcPre=fc;
handleRoll();
ok=await until(()=>window.D3X&&D3X.dice.some(d=>d.match&&d.phys&&d.phys.v),12000);
if(!ok)return {err:'no settle',fc,fcPre,pc,fe,pe,solveVals,rollVals,
 rollState:(D3X.dice||[]).filter(d=>d.match).slice(0,3).map(d=>({roll:!!d.roll,phys:!!d.phys,
  v:d.phys?d.phys.v:undefined,vType:d.phys?typeof d.phys.v:undefined}))};
const d=D3X.dice.find(x=>x.match&&x.phys&&x.phys.v);
let m=null;d.obj.traverse(o=>{if(!m&&o.isMesh&&o.material&&!o.userData.outline)m=o.material;});
const t0=d.phys.t||performance.now();
/* sample every 70ms for 1.4s */
const seen=[],ids=new Map();let nid=0;
const idOf=x=>{if(!ids.has(x))ids.set(x,nid++);return ids.get(x);};
for(let i=0;i<20;i++){
 seen.push({t:Math.round(performance.now()-t0),map:idOf(m.map),
  isLive:m.map===(m.userData&&m.userData.liveMap)});
 await sleep(70);}
const distinct=new Set(seen.map(x=>x.map)).size;
const early=seen.filter(x=>x.t<120);
const late=seen.filter(x=>x.t>1000);
return {v:d.phys.v,samples:seen,distinctMaps:distinct,
 earlyStillLive:early.length===0||early.every(x=>x.isLive),
 lateStable:late.length>1&&new Set(late.map(x=>x.map)).size===1,
 lateDimmed:late.length>0&&late.every(x=>!x.isLive),
 /* >=3 distinct maps = live + at least one INTERMEDIATE step + final: the
 * one-frame pop this guards against would read exactly 2. Headless frames
 * are too sparse to render all 8 steps; devices at 60fps show every one. */
verdict:distinct>=3&&(early.length===0||early.every(x=>x.isLive))
 &&late.length>0&&late.every(x=>!x.isLive)&&new Set(late.map(x=>x.map)).size===1};
