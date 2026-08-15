/* SUITE: exclude. A3: REAL context loss (WEBGL_lose_context) mid-match,
 * then the resume warm's boot() - does 3D come back with real physics? */
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(fn,ms)=>{const t0=Date.now();while(Date.now()-t0<ms){try{if(fn())return true;}catch(e){}await sleep(70);}return false;};
const vis=el=>{if(!el||!el.isConnected)return false;const s=getComputedStyle(el),r=el.getBoundingClientRect();
 return s.display!=='none'&&s.visibility!=='hidden'&&+s.opacity>0.05&&r.width>1&&r.height>1;};
const tap=el=>{if(!vis(el))return false;const r=el.getBoundingClientRect();
 const o={bubbles:true,cancelable:true,clientX:r.left+r.width/2,clientY:r.top+r.height/2};
 el.dispatchEvent(new PointerEvent('pointerdown',o));el.dispatchEvent(new PointerEvent('pointerup',o));
 el.dispatchEvent(new MouseEvent('click',o));return true;};
const out={};
tap(document.getElementById('hsBtnBottom'));await sleep(2000);
await until(()=>document.querySelector('.nrdie'),9000);await sleep(500);
tap(document.querySelector('.nrdie'));await sleep(1200);
tap(document.getElementById('nrTakeBtn'));await sleep(2400);
await until(()=>typeof launchSeat==='function'&&S&&S.run,9000);
_getS();try{G=null;}catch(e){}
window._fkDiscardOk=true;
launchSeat(0);
if(!await until(()=>typeof G!=='undefined'&&G&&G.phase==='idle',16000))return {err:'no idle'};
out.fk3dBefore=document.documentElement.classList.contains('fk3d');
/* REAL loss */
const gl=D3X.renderer.getContext();
const ext=gl.getExtension('WEBGL_lose_context');
if(!ext)return {err:'no lose_context ext'};
const rendererBefore=D3X.renderer;
ext.loseContext();
/* the suspend signal is ready flipping false - the event is async */
out.suspended=await until(()=>!D3X.ready,8000);
out.failFlag=!!D3X.fail;
/* the resume warm's revive */
D3X.boot();
out.revived=await until(()=>D3X.ready,20000);
out.freshRenderer=D3X.renderer!==rendererBefore;
await sleep(800);
/* and the physics after revival */
handleRoll();
if(!await until(()=>D3X.dice.some(d=>d.match&&d.roll),9000))return {...out,err:'no roll'};
const ds=D3X.dice.filter(d=>d.match&&d.roll&&d.roll.sol);
out.tape=ds.slice(0,2).map(d=>{
  const fr=d.roll.sol.frames,i=d.roll.i;
  let yr=[1e9,-1e9];fr.forEach(f=>{yr=[Math.min(yr[0],f[i].y),Math.max(yr[1],f[i].y)];});
  return {frames:fr.length,dy:+(yr[1]-yr[0]).toFixed(2)};
});
out.verdict=out.suspended&&!out.failFlag&&out.revived&&out.freshRenderer&&out.tape.every(t=>t.dy>0.5);
return out;
