window.__errs=[];
window.addEventListener('error',e=>{window.__errs.push('ERR: '+(e.message||'')+' @'+(e.lineno||''));});
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(fn,ms)=>{const t0=Date.now();while(Date.now()-t0<ms){try{if(fn())return true;}catch(e){}await sleep(100);}return false;};
await until(()=>typeof launchBossMatch==='function',20000);
_getS();window._fkDiscardOk=true;
S.run.tier=4;S.run.gold=500;
try{delete S.pendingMatch;}catch(e){}
launchBossMatch();
await until(()=>G&&G.phase==='idle',15000);
await sleep(1400);
const log=[];
for(let i=0;i<14;i++){
  const b=G.oPts;
  G.pPts=0;G.turnPts=0;G.kept=[];
  try{ if(typeof endTurn==='function')endTurn(); else {G.phase='opp';runOppTurn();} }catch(e){log.push({i,threw:e.message});break;}
  const done=await until(()=>G&&G.phase!=='opp'&&G.phase!=='rolling',12000);
  log.push({i,done,phase:G&&G.phase,oPts:G&&G.oPts,busted:G&&G.oPts===b,
            endFired:!!(G&&G._endMatchFired),oppTurnCount:G&&G.npcCardState&&G.npcCardState.oppTurnCount,
            endReason:G&&G._endReason});
  if(!done)break;
  await sleep(100);
}
return {log,errs:window.__errs.slice(0,5)};
