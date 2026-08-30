/* catch anything the page throws, then walk the two broken paths */
window.__errs=[];
window.addEventListener('error',e=>{window.__errs.push('ERROR: '+(e.message||'')+' @'+(e.filename||'')+':'+(e.lineno||''));});
window.addEventListener('unhandledrejection',e=>{window.__errs.push('REJECT: '+String(e.reason).slice(0,200));});
const _ce=console.error; console.error=function(){window.__errs.push('console.error: '+[...arguments].map(String).join(' ').slice(0,240));return _ce.apply(console,arguments);};
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(fn,ms)=>{const t0=Date.now();while(Date.now()-t0<ms){try{if(fn())return true;}catch(e){}await sleep(120);}return false;};
await until(()=>typeof _getS==='function',20000);
_getS();
const out={};

/* 1. does generateOppCards throw for a PATRON? */
try{
  const tier=TIERS[3];
  out.patronCall='ok';
  const p={key:'patron',cardPool:['quick_hands','the_skim'],cardCount:2};
  out.patronDraw=generateOppCards(p);
}catch(e){out.patronCall='THREW: '+e.message;}

/* 2. does it throw for a BOSS? */
try{ out.bossDraw=generateOppCards(TIERS[3].boss,3); }catch(e){out.bossDraw='THREW: '+e.message;}

/* 3. the night screen - where the patron frames live */
try{
  S.run.tier=3;S.run.night=null;
  if(typeof _ensureNight==='function')_ensureNight();
  out.nightBuilt=!!(S.run.night&&S.run.night.roster);
  out.roster=(S.run.night&&S.run.night.roster||[]).map(n=>({name:n.name,buyIn:n.buyIn,gone:n.gone}));
}catch(e){out.nightBuilt='THREW: '+e.message;}

out.errs=window.__errs.slice(0,10);
return out;
