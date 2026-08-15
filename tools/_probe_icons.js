/* SUITE: exclude. v5b: every chip and step wears a glyph. */
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(fn,ms)=>{const t0=Date.now();while(Date.now()-t0<ms){try{if(fn())return true;}catch(e){}await sleep(100);}return false;};
const out={};
await setup();
if(!await until(()=>{const g=E('G');return g&&g.phase==='idle';},4000))return {err:'no match'};
openStudio('preserve');await sleep(500);
showTab(1);
out.palChips=document.querySelectorAll('#seqPal .chip').length;
out.palIcons=document.querySelectorAll('#seqPal .chip svg').length;
out.stepIcons=document.querySelectorAll('#seqLane .step svg').length;
out.steps=document.querySelectorAll('#seqLane .step').length;
out.verdict=out.palChips>25&&out.palIcons===out.palChips&&out.stepIcons===out.steps&&out.steps>0;
return out;
