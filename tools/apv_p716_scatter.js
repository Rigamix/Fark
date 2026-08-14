/* P716: the kick displaces settled dice and holds; the shield ring mounts
 * and leaves; the full impact wires both. P717 text check. SUITE: exclude */
window.__errs=window.__errs||[];window.addEventListener('error',e=>{window.__errs.push((e.message||'')+' @L'+e.lineno+' | '+String(e.error&&e.error.stack||'').slice(0,500));});
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(fn,ms)=>{const t0=Date.now();while(Date.now()-t0<ms){try{if(fn())return true;}catch(e){}await sleep(60);}return false;};
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
ok=await until(()=>window.D3X&&D3X.dice.filter(d=>d.match&&d.phys).length>=3,12000);
if(!ok)return {err:'no settle'};
await sleep(600);
const md=()=>D3X.dice.filter(d=>d.match&&d.phys);
const posOf=d=>({x:+d.obj.position.x.toFixed(2),z:+d.obj.position.z.toFixed(2)});
const before=md().map(posOf);
const out={settled:before.length};

/* the full impact (class + kick) */
_bustImpact();
out.kicked=md().filter(d=>d.kick).length;
await sleep(900);/* past KICK.ms */
const after=md().map(posOf);
out.moved=after.filter((p,i)=>Math.abs(p.x-before[i].x)+Math.abs(p.z-before[i].z)>0.3).length;
out.scatterClass=document.querySelectorAll('#playerDiceRow .die.scatter').length;
await sleep(300);
const after2=md().map(posOf);
out.holds=after.every((p,i)=>Math.abs(p.x-after2[i].x)<0.05);

/* the shield */
_bustShieldFX('#9ab0d0');
await sleep(200);
const sh=document.querySelector('.bust-shield-row');
out.shield={mounted:!!sh,visible:vis(sh)};
await sleep(1400);
out.shield.gone=!document.querySelector('.bust-shield-row');

/* P717 -> P718: the card is RETIRED now; the old .text read was this
 * probe's own crash ("reading 'text' of null" - the instrument, not the
 * game). */
out.ftGone=!famDef('fair_trade');

out.errs=window.__errs.slice(0,3);
out.verdict=out.kicked>=3&&out.moved>=3&&out.holds&&out.scatterClass>0
 &&out.shield.mounted&&out.shield.visible&&out.shield.gone&&out.ftGone;
return out;
