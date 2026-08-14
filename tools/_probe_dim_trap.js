/* P725c hunt: a SETTER TRAP on every die material's map - logs EVERY
 * assignment with the writer's stack line, so a one-frame flash cannot
 * slip between samples. Real sequence: roll -> settle -> choose -> reroll.
 * SUITE: exclude */
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
const t0=Date.now();
const recs=[];
const trap=(d,idx)=>{d.obj.traverse(o=>{
 if(!o.isMesh||!o.material||o.userData.outline)return;
 const m=o.material;if(m.__dimTrap)return;m.__dimTrap=1;
 let cur=m.map;
 const rec={idx,m,d,log:[]};recs.push(rec);
 Object.defineProperty(m,'map',{configurable:true,
  get:()=>cur,
  set:v=>{
   const live=m.userData&&m.userData.liveMap;
   const toBright=!!(live&&v===live);
   const fromDim=!!(live&&cur&&cur!==live);
   /* the stack line IS the writer: F:line:col inside fark_proto.html */
   const st=((new Error().stack)||'').split('\n').slice(2,5)
     .map(x=>x.replace(/^\s*at /,'').replace(/https?:\/\/\S*?fark_proto\.html/g,'F'))
     .join(' | ');
   if(rec.log.length<80)rec.log.push({t:Date.now()-t0,
    toBright,fromDim,settled:!!(d.phys&&d.phys.v),rolling:!!d.roll,st});
   cur=v;}});
 });};
handleRoll();
ok=await until(()=>D3X.dice.some(d=>d.match&&d.roll),9000);
if(!ok)return {err:'no roll'};
D3X.dice.filter(d=>d.match&&d.roll).forEach((d,i)=>trap(d,i));
/* first settle + tail */
await until(()=>D3X.dice.filter(d=>d.match).every(d=>!d.roll),20000);
await sleep(1200);
const phase1=G&&G.phase;
/* choose a scoring die, then reroll the rest */
let chose=false,rerolled=false;
if(G&&G.phase==='choosing'){
  const mine=D3X.dice.filter(d=>d.match&&d.chip&&d.chip.closest&&d.chip.closest('#playerDiceRow'));
  const scored=mine.filter(d=>d.chip._trueVal===1||d.chip._trueVal===5);
  for(const d of (scored.length?scored:mine)){
    tap(d.chip.querySelector('.die-hit')||d.chip);
    await sleep(350);
    if(d.chip.classList.contains('selected')){chose=true;break;}
  }
  await sleep(600);
  const rb=document.getElementById('btnRoll');
  if(rb&&!rb.classList.contains('disabled')){tap(rb);rerolled=true;}
  await sleep(400);
  if(rerolled){
    await until(()=>D3X.dice.filter(d=>d.match).every(d=>!d.roll),20000);
    await sleep(1200);
  }
}
/* verdict material: bright writes that hit a DIMMED die outside early
   flight of a fresh throw - those are flicker writers */
const bad=[],census={};
recs.forEach(r=>r.log.forEach(e=>{
  const key=(e.toBright?'BRIGHT ':'dim ')+e.st.slice(0,110);
  census[key]=(census[key]||0)+1;
  if(e.toBright&&e.fromDim&&e.settled)bad.push({die:r.idx,t:e.t,st:e.st.slice(0,160)});
}));
return {phase1,chose,rerolled,phase2:G&&G.phase,
 badCount:bad.length,bad:bad.slice(0,10),
 census,
 verdict:bad.length===0};
