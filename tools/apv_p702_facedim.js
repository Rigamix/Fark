/* P702: settled dice swap to the sides-dimmed map; the value rides phys.
 * SUITE: exclude */
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(fn,ms)=>{const t0=Date.now();while(Date.now()-t0<ms){try{if(fn())return true;}catch(e){}await sleep(60);}return false;};
const vis=el=>{if(!el||!el.isConnected)return false;const s=getComputedStyle(el),r=el.getBoundingClientRect();
 return s.display!=='none'&&s.visibility!=='hidden'&&+s.opacity>0.05&&r.width>1&&r.height>1;};
const tap=el=>{if(!vis(el))return false;const r=el.getBoundingClientRect();
 const o={bubbles:true,cancelable:true,clientX:r.left+r.width/2,clientY:r.top+r.height/2};
 el.dispatchEvent(new PointerEvent('pointerdown',o));el.dispatchEvent(new PointerEvent('pointerup',o));
 el.dispatchEvent(new MouseEvent('click',o));return true;};
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
await until(()=>G.pool&&G.pool.length>=3,9000);
/* wait for the physics rest, not just game state */
await until(()=>window.D3X&&D3X.dice.some(d=>d.match&&d.phys),9000);
await sleep(1800);
const md=D3X.dice.filter(d=>d.match&&d.phys);
const out={settled:md.length,adopted:!!(D3X._tbl&&D3X.dice.some(d=>d.match))};
out.dice=md.slice(0,6).map(d=>{
 let m=null;d.obj.traverse(o=>{if(!m&&o.isMesh&&o.material&&!o.userData.outline)m=o.material;});
 const live=m&&m.userData&&m.userData.liveMap;
 return {v:d.phys.v,hasLive:!!live,dimmed:!!(m&&live&&m.map!==live),
  gameVal:(d.chip&&d.chip._trueVal)||null,
  cacheKeyed:!!(live&&live.userData&&live.userData.dimMaps&&live.userData.dimMaps[d.phys.v])};
});
out.allDimmed=out.dice.length>0&&out.dice.every(x=>x.dimmed&&x.v);
out.valsMatch=out.dice.every(x=>!x.gameVal||x.v===x.gameVal);
out.verdict=out.adopted&&out.allDimmed&&out.valsMatch;
return out;
