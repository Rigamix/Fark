window.__errs=[];
window.addEventListener('error',e=>{window.__errs.push('ERR: '+(e.message||'')+' @'+(e.lineno||''))});
const _ce=console.error;console.error=function(){window.__errs.push('cerr: '+[...arguments].map(String).join(' ').slice(0,200));return _ce.apply(console,arguments);};
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(fn,ms)=>{const t0=Date.now();while(Date.now()-t0<ms){try{if(fn())return true;}catch(e){}await sleep(150);}return false;};
await until(()=>typeof launchBossMatch==='function',20000);
_getS();window._fkDiscardOk=true;
S.run.tier=1;S.run.gold=500;
try{delete S.pendingMatch;}catch(e){}
launchBossMatch();
await until(()=>typeof G!=='undefined'&&G&&G.phase==='idle',20000);
await sleep(1500);
const Q=[];for(let i=0;i<12;i++)Q.push(i%2?5:1);
const realE=window._enchRollM;window._enchRollM=(m,e)=>Q.length?Q.shift():realE(m,e);
const tap=el=>{const r=el.getBoundingClientRect();const o={bubbles:true,cancelable:true,clientX:r.left+r.width/2,clientY:r.top+r.height/2};
  el.dispatchEvent(new PointerEvent('pointerdown',o));el.dispatchEvent(new PointerEvent('pointerup',o));el.dispatchEvent(new MouseEvent('click',o));};
const before=G.phase;
tap(document.getElementById('btnRoll'));
const reached=await until(()=>G.phase==='choosing',30000);
return {
  phaseBefore:before,phaseAfter:G&&G.phase,reachedChoosing:reached,
  poolLen:(G.pool||[]).length,
  turnRollCount:G&&G.turnRollCount,
  rolling:D3X._rolling(),
  predicateSane:(function(){try{
    return {iconLive:typeof _iconLive,dieIsIcon:typeof _dieIsIcon,refused:typeof _iconRefused,
            callOk:_dieIsIcon({val:1,ench:{t:'fog',face:1},lane:0})};
  }catch(e){return 'THREW: '+e.message;}})(),
  errs:window.__errs.slice(0,8),
};
