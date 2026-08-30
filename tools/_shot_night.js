const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(fn,ms)=>{const t0=Date.now();while(Date.now()-t0<ms){try{if(fn())return true;}catch(e){}await sleep(120);}return false;};
window.__errs=[];
window.addEventListener('error',e=>{window.__errs.push('ERROR: '+(e.message||'')+' @'+(e.lineno||''));});
const _ce=console.error;console.error=function(){window.__errs.push('cerr: '+[...arguments].map(String).join(' ').slice(0,200));return _ce.apply(console,arguments);};
await until(()=>typeof showScreen==='function'&&typeof _getS==='function',20000);
_getS();
S.run.tier=3;S.run.gold=500;S.run.points=0;S.run.night=null;
try{_ensureNight();}catch(e){window.__errs.push('ensureNight: '+e.message);}
showScreen('gauntlet');
await sleep(3000);
const seats=[...document.querySelectorAll('.pt-seat,[class*="ptSeat"],#ptRoom > *')].slice(0,8)
  .map(e=>({cls:String(e.className).slice(0,40),txt:(e.innerText||'').replace(/\s+/g,' ').trim().slice(0,60)}));
return {
  artNames:(S.run.night.roster||[]).map(r=>r._art),
  goldNow:S.run.gold,
  buyInForTier:(typeof NIGHT_BUYINS!=='undefined')?NIGHT_BUYINS[S.run.tier]:null,
  seatSample:seats,
  screenText:(document.getElementById('screen-gauntlet')||document.body).innerText.replace(/\s+/g,' ').trim().slice(0,260),
  errs:window.__errs.slice(0,8),
};
