const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(fn,ms)=>{const t0=Date.now();while(Date.now()-t0<ms){try{if(fn())return true;}catch(e){}await sleep(120);}return false;};
if(!await until(()=>typeof launchBossMatch==='function',20000))return {err:'no boot'};
_getS();window._fkDiscardOk=true;
S.run.tier=0;S.run.gold=500;
try{delete S.pendingMatch;}catch(e){}
launchBossMatch();
if(!await until(()=>typeof G!=='undefined'&&G&&G.phase==='idle',15000))return {err:'no match'};
await sleep(1800);
G.pPts=G.target;G.oPts=0;
endMatch(true);
const got=await until(()=>{const rc=document.querySelector('#end-ov .res-card');
  return rc&&/SPOILS/.test(rc.textContent);},20000);
await sleep(1500);
const rc=document.querySelector('#end-ov .res-card');
const tiles=[...rc.querySelectorAll('[onclick*="_gbSpoilsConfirm"]')].map(t=>{
  const r=t.getBoundingClientRect();
  return {kind:(t.getAttribute('onclick').match(/'(\w+)'/)||[])[1],
          text:t.textContent.replace(/\s+/g,' ').trim().slice(0,70),
          x:Math.round(r.x),w:Math.round(r.width),h:Math.round(r.height),
          clippedRight:r.right>innerWidth+1,clippedBottom:r.bottom>innerHeight+1};
});
return {reachedSpoils:got,viewport:{w:innerWidth,h:innerHeight},tiles,
  trophiesAfterWin:(S.trophies||[]).slice(),
  spoils:window._spoils?{card:window._spoils.card,cardName:window._spoils.cardName,tell:window._spoils.tell,purse:window._spoils.purse}:null};
