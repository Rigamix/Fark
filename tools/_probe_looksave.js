/* SUITE: exclude. the look persists and re-applies. */
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(fn,ms)=>{const t0=Date.now();while(Date.now()-t0<ms){try{if(fn())return true;}catch(e){}await sleep(100);}return false;};
const out={};
await setup();
if(!await until(()=>{const g=E('G');return g&&g.phase;},4000))return {err:'no match'};
await sleep(600);
document.getElementById('vgA').value=52;
document.getElementById('vgR').value=38;
document.getElementById('vgC').value=22;
vigSet();
glowDial('sy',1.45);
await sleep(700);
out.saved=(()=>{try{const lk=JSON.parse(localStorage.fkLabLook);
  return lk.vgA===52&&lk.GLOW&&lk.GLOW.sy===1.45;}catch(e){return String(e);}})();
/* simulate a fresh session: wipe the LIVE state without touching the
   setters (a setter call would save the wiped state - by design) */
document.getElementById('vgA').value=0;
document.getElementById('gSy').value=100;
E('D3X.GLOW.sy=1');
gw();var lv=W.document.getElementById('labVig');if(lv)lv.style.background='';
applyLook();
await sleep(300);
out.restoredSlider=+document.getElementById('vgA').value===52;
out.restoredGlow=E('D3X.GLOW.sy')===1.45;
gw();
out.vigOn=/0\.52/.test((W.document.getElementById('labVig')||{}).style.background||'');
out.verdict=out.saved===true&&out.restoredSlider&&out.restoredGlow&&out.vigOn;
return out;
