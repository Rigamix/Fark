/* P553 - is the draft's contact shadow actually SEEN, or only present?

   The port keeps `.d3shadow` alive and drives it with D3's own formula, and
   that is easy to confirm from the DOM. It is not the question. The canvas is
   painted ABOVE #nrDice, so the ellipse only reaches a player where the die's
   own silhouette does not already cover it - and the ellipse is centred just
   16*s px below the die's centre, well inside a cube that spans about 1.2 edge
   lengths. "The shadow survives the port" and "the shadow is visible" are two
   different claims and only the first is cheap.

   So this measures the die's REAL silhouette rather than its box: the eight
   cube corners projected through D3X's own camera, lowest point taken, against
   the shadow element's own rect. Reported at the bottom of the breathe (the die
   is lowest, the shadow most covered) and at its peak.

   This is a MEASUREMENT, not an assertion about the patch - the geometry is
   the same as it was before the port, so whatever it says is a pre-existing
   property of this surface, not something P553 changed. SUITE: exclude */
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(f,ms)=>{const t=Date.now();while(Date.now()-t<ms){try{if(f())return true;}catch(e){}await sleep(60);}return false;};
_getS(); S.run=S.run||{}; S.run.tier=1;
try{D3X.boot();}catch(e){}
if(!(await until(()=>D3X.ready,25000)))return{error:'D3X never booted'};
try{startNewRun();}catch(e){}
_starterOffer=['silver','obsidian','vagabond'];
try{famRunDraftShow();}catch(e){}
if(!(await until(()=>document.querySelectorAll('#nrDice .d3slot').length===3,9000)))return{error:'no dice'};
await sleep(3000);

const mr=D3X.mount.getBoundingClientRect();
/* the lowest screen pixel the die can occupy: its eight corners through the
   very camera that drew it, not the chip's box */
function dieLow(d){
  const g=d.obj; g.updateMatrixWorld(true);
  let lo=-1e9;
  for(let i=0;i<8;i++){
    const v=new THREE.Vector3((i&1?0.5:-0.5),(i&2?0.5:-0.5),(i&4?0.5:-0.5));
    g.localToWorld(v); v.project(D3X.cam);
    lo=Math.max(lo,(-v.y*0.5+0.5)*mr.height+mr.top);
  }
  return lo;
}
function sample(){
  return (D3X.dice||[]).filter(d=>d.chip.closest('#nrDice')).map(d=>{
    const sh=d._dom&&d._dom.shadow; if(!sh)return null;
    const r=sh.getBoundingClientRect();
    return {below:+(r.bottom-dieLow(d)).toFixed(1),
            shH:+r.height.toFixed(1),
            op:+getComputedStyle(sh).opacity,
            lift:+(d.anim?(d.anim.hT0?1:0):0)};
  });
}
/* three seconds of the breathe, keeping the extremes */
let best=null,worst=null;
for(let n=0;n<40;n++){
  const s=sample();
  const m=Math.max(...s.filter(Boolean).map(x=>x.below));
  if(best===null||m>best.m)best={m:+m.toFixed(1),s};
  if(worst===null||m<worst.m)worst={m:+m.toFixed(1),s};
  await sleep(75);
}
return {
  peak:best, trough:worst,
  note:'below = px of shadow reaching past the die silhouette. <=0 means the '
      +'die covers it entirely and the ellipse never reaches a player.',
  reading: best.m<=0 ? 'NEVER SEEN - fully behind the die through the whole breathe'
         : worst.m>0 ? 'ALWAYS SEEN - '+worst.m+' to '+best.m+'px clear of the die'
         : 'SEEN ONLY AT THE TOP OF THE BREATHE - up to '+best.m+'px'};
