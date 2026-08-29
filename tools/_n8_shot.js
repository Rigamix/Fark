const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(fn,ms)=>{const t0=Date.now();while(Date.now()-t0<ms){try{if(fn())return true;}catch(e){}await sleep(120);}return false;};
if(!await until(()=>typeof launchBossMatch==='function',20000))return {err:'no boot'};
_getS();window._fkDiscardOk=true;
try{S.run.tier=0;launchBossMatch();await until(()=>G&&G.phase==='idle',15000);await sleep(2200);}catch(e){}
S.run.tier=7;try{delete S.pendingMatch;}catch(e){}
try{showScreen('gauntlet');}catch(e){}
launchBossMatch();
await until(()=>typeof G!=='undefined'&&G&&G.phase==='idle',15000);
await sleep(1800);
G.pPts=G.target;G.oPts=0;endMatch(true);
await until(()=>{const rc=document.querySelector('#end-ov .res-card');return rc&&/TAKE ONE/.test(rc.textContent);},20000);
await sleep(1400);
const rc=document.querySelector('#end-ov .res-card');
const tiles=[...rc.querySelectorAll('[onclick*="_gbSpoilsConfirm"]')].map(t=>{
  const r=t.getBoundingClientRect();
  return {kind:(t.getAttribute('onclick').match(/'(\w+)'/)||[])[1],x:Math.round(r.x),w:Math.round(r.width),
          clipped:r.right>innerWidth+1||r.left<-1};
});
return {boss:G.rung.name,renown:S.renown,tiles,
  text:(rc.innerText||'').replace(/\s+/g,' ').trim().slice(0,110)};
