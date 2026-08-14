/* P725: once a die's dim is on, it NEVER flips back to the bright map -
 * sampled across the rolling->settled handoff. SUITE: exclude */
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(fn,ms)=>{const t0=Date.now();while(Date.now()-t0<ms){try{if(fn())return true;}catch(e){}await sleep(40);}return false;};
const vis=el=>{if(!el||!el.isConnected)return false;const s=getComputedStyle(el),r=el.getBoundingClientRect();
 return s.display!=='none'&&s.visibility!=='hidden'&&+s.opacity>0.05&&r.width>1&&r.height>1;};
const tap=el=>{if(!vis(el))return false;const r=el.getBoundingClientRect();
 const o={bubbles:true,cancelable:true,clientX:r.left+r.width/2,clientY:r.top+r.height/2};
 el.dispatchEvent(new PointerEvent('pointerdown',o));el.dispatchEvent(new PointerEvent('pointerup',o));
 el.dispatchEvent(new MouseEvent('click',o));return true;};
await until(()=>window.D3X&&D3X.frame,9000);
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
handleRoll();
ok=await until(()=>window.D3X&&D3X.dice.some(d=>d.match&&d.roll),9000);
if(!ok)return {err:'no roll'};
/* watch every rolling die's material across the whole settle window:
   record dim-state transitions; a dim->bright flip after first dim = flap */
const watch=D3X.dice.filter(d=>d.match&&d.roll).map(d=>{
 let m=null;d.obj.traverse(o=>{if(!m&&o.isMesh&&o.material&&!o.userData.outline)m=o.material;});
 return {d,m,everDim:false,flaps:0,wasDim:false,log:[]};});
const t0=Date.now();let settledAt=0;
const calls={rebrand:[],reskin:[]};
const _rb=D3X._rebrand.bind(D3X);D3X._rebrand=function(x){calls.rebrand.push(Date.now()-t0);return _rb(x);};
const _rs=D3X._reskin.bind(D3X);D3X._reskin=function(){calls.reskin.push(Date.now()-t0);return _rs();};
while(Date.now()-t0<20000){
 if(!settledAt&&watch.every(w=>w.d.phys))settledAt=Date.now();
 if(settledAt&&Date.now()-settledAt>900)break;
 watch.forEach(w=>{
  const live=w.m.userData&&w.m.userData.liveMap;
  const dim=!!(live&&w.m.map!==live);
  if(dim!==w.wasDim&&w.log.length<14){
   if(!w.ids)w.ids={};
   const mu=w.m.map&&w.m.map.uuid,lu=live&&live.uuid;
   const tag=u=>{if(!u)return null;if(!(u in w.ids))w.ids[u]='T'+Object.keys(w.ids).length;return w.ids[u];};
   w.log.push({
   ms:Date.now()-t0,dim,roll:!!w.d.roll,phys:!!w.d.phys,
   v:w.d.phys&&w.d.phys.v,map:tag(mu),live:tag(lu),
   physAge:w.d.phys?Math.round(performance.now()-w.d.phys.t):null});}
  if(dim&&!w.wasDim&&w.everDim)w.flaps++;      /* re-dim after a bright gap */
  if(!dim&&w.wasDim)w.flaps++;                  /* dim -> bright flip */
  if(dim)w.everDim=true;
  w.wasDim=dim;});
 await sleep(50);}
const allSettled=watch.every(w=>w.d.phys);
/* force the rebuild paths mid-dim: P725b must re-dim SYNCHRONOUSLY */
const dimNow=()=>watch.map(w=>!!(w.m.userData.liveMap&&w.m.map!==w.m.userData.liveMap));
const before=dimNow();
_rs();               /* full reskin: every die rebuilt */
const afterReskin=dimNow();
_rb(watch[0].d);     /* single-die rebrand */
const afterRebrand=dimNow();
return {dice:watch.length,allSettled,calls,before,afterReskin,afterRebrand,
 rebuildHeld:before.every(Boolean)&&afterReskin.every(Boolean)&&afterRebrand.every(Boolean),
 logs:watch.map(w=>w.log),
 everDim:watch.filter(w=>w.everDim).length,
 flaps:watch.map(w=>w.flaps),
 verdict:watch.length>=3&&allSettled&&watch.every(w=>w.everDim&&w.flaps===0)
  &&before.every(Boolean)&&afterReskin.every(Boolean)&&afterRebrand.every(Boolean)};
