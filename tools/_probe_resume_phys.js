/* SUITE: exclude. A3: does a roll AFTER the resume path produce a tape
 * with real translation and bounces, like a normal roll does? */
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(fn,ms)=>{const t0=Date.now();while(Date.now()-t0<ms){try{if(fn())return true;}catch(e){}await sleep(70);}return false;};
const vis=el=>{if(!el||!el.isConnected)return false;const s=getComputedStyle(el),r=el.getBoundingClientRect();
 return s.display!=='none'&&s.visibility!=='hidden'&&+s.opacity>0.05&&r.width>1&&r.height>1;};
const tap=el=>{if(!vis(el))return false;const r=el.getBoundingClientRect();
 const o={bubbles:true,cancelable:true,clientX:r.left+r.width/2,clientY:r.top+r.height/2};
 el.dispatchEvent(new PointerEvent('pointerdown',o));el.dispatchEvent(new PointerEvent('pointerup',o));
 el.dispatchEvent(new MouseEvent('click',o));return true;};
const tapeStats=()=>{
  const ds=D3X.dice.filter(d=>d.match&&d.roll&&d.roll.sol&&d.roll.sol.frames);
  return ds.map(d=>{
    const fr=d.roll.sol.frames,i=d.roll.i;
    let xr=[1e9,-1e9],yr=[1e9,-1e9],zr=[1e9,-1e9],bounces=0;
    let prevY=null,dir=-1;
    fr.forEach(f=>{const p=f[i];
      xr=[Math.min(xr[0],p.x),Math.max(xr[1],p.x)];
      yr=[Math.min(yr[0],p.y),Math.max(yr[1],p.y)];
      zr=[Math.min(zr[0],p.z),Math.max(zr[1],p.z)];
      if(prevY!==null){const d2=p.y-prevY;
        if(dir<0&&d2>0.02)bounces++,dir=1;else if(d2<-0.02)dir=-1;}
      prevY=p.y;});
    return {frames:fr.length,dx:+(xr[1]-xr[0]).toFixed(2),dy:+(yr[1]-yr[0]).toFixed(2),
      dz:+(zr[1]-zr[0]).toFixed(2),bounces};
  });
};
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
/* fresh-path roll */
handleRoll();
if(!await until(()=>D3X.dice.some(d=>d.match&&d.roll),9000))return {err:'no roll1'};
out.fresh=tapeStats();
await until(()=>D3X.dice.filter(d=>d.match).every(d=>!d.roll),20000);
await sleep(500);
/* save + leave + resume, the real path */
try{saveMatchState();}catch(e){out.saveErr=String(e).slice(0,90);}
out.pending=!!(S&&S.pendingMatch);
showScreen('gauntlet');await sleep(1200);
resumeMatch();
if(!await until(()=>vis(document.getElementById('screen-match'))&&G&&G.phase!=='opp',16000))
  return {...out,err:'no resume'};
await sleep(1500);
out.phaseAfterResume=G.phase;
/* the resumed roll */
const rb=document.getElementById('btnRoll');
if(rb&&!rb.classList.contains('disabled'))tap(rb);else try{handleRoll();}catch(e){out.rollErr=String(e).slice(0,90);}
if(!await until(()=>D3X.dice.some(d=>d.match&&d.roll),9000))return {...out,err:'no roll2'};
out.resumed=tapeStats();
const flat=a=>a&&a.length?{minDx:Math.min(...a.map(t=>t.dx)),minDy:Math.min(...a.map(t=>t.dy)),
  minB:Math.min(...a.map(t=>t.bounces))}:null;
out.freshSum=flat(out.fresh);out.resumedSum=flat(out.resumed);
out.verdict=!!(out.resumedSum&&out.resumedSum.minDy>0.3&&out.resumedSum.minB>=1);
return out;
