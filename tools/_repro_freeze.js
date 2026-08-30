/* Reproduce Denis's freeze: a save whose npcWonCards holds ids P862 deleted. */
window.__errs=[];
window.addEventListener('error',e=>{window.__errs.push('ERROR: '+(e.message||'')+' @'+(e.lineno||''));});
const _ce=console.error;console.error=function(){window.__errs.push('cerr: '+[...arguments].map(String).join(' ').slice(0,220));return _ce.apply(console,arguments);};
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(fn,ms)=>{const t0=Date.now();while(Date.now()-t0<ms){try{if(fn())return true;}catch(e){}await sleep(120);}return false;};
const tap=el=>{if(!el)return false;const r=el.getBoundingClientRect();
  const o={bubbles:true,cancelable:true,clientX:r.left+r.width/2,clientY:r.top+r.height/2};
  el.dispatchEvent(new PointerEvent('pointerdown',o));el.dispatchEvent(new PointerEvent('pointerup',o));
  el.dispatchEvent(new MouseEvent('click',o));return true;};
await until(()=>typeof launchBossMatch==='function',20000);
_getS();window._fkDiscardOk=true;

/* the state a returning player has: cards the rival won off them, some of
   which P862 deleted from the catalog */
S.npcWonCards=S.npcWonCards||{};
S.npcWonCards.soldier=['the_tab','all_in','sleight_of_hand'];
S.run.tier=4;S.run.gold=500;
try{delete S.pendingMatch;}catch(e){}
launchBossMatch();
if(!await until(()=>typeof G!=='undefined'&&G&&G.phase==='idle',15000))return {err:'no match',errs:window.__errs};
await sleep(1800);

const out={oCards:(G.oCards||[]).slice(),
  unresolvable:(G.oCards||[]).filter(id=>{try{return !getCard(id);}catch(e){return true;}})};

/* hand the turn over and watch whether the rival ever finishes it */
const before={oPts:G.oPts,phase:G.phase};
try{
  G.pPts=0;G.turnPts=0;
  if(typeof endTurn==='function')endTurn();
  else if(typeof yieldTurn==='function')yieldTurn();
  else { G.phase='opp'; runOppTurn(); }
}catch(e){out.handoverThrew=e.message;}
const finished=await until(()=>G&&G.phase!=='opp'&&G.phase!=='rolling',25000);
out.oppTurnFinished=finished;
out.phaseAfter=G&&G.phase;
out.oPtsAfter=G&&G.oPts;
out.errs=window.__errs.slice(0,10);
return out;
