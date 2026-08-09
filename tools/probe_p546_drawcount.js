/* P546 part 2: D3 must stop repainting dice that D3X has adopted.
   Counted, not reasoned: wrap D3.draw, open the loadout, count over ~120
   frames. Before the patch this was roughly one call per die per frame.
   CONTROL: the wrap must still fire for dice D3X has NOT adopted, or a
   "0" would just mean the counter never armed. */
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(f,ms)=>{const t=Date.now();while(Date.now()-t<ms){try{if(f())return true;}catch(e){}await sleep(60);}return false;};
_getS(); S.run=S.run||{}; S.run.tier=2; S.run.gold=500;
S.run.dice=['bone','iron','flint','amber','jade','starstone'];
S.settings=S.settings||{}; S.settings.reducedMotion=true;
let drawn=0, armed=0;
const orig=D3.draw;
D3.draw=function(d){ armed++; if(d&&d._d3xOwned===true){} else drawn++; return orig.apply(this,arguments); };
try{famLoadoutShow();}catch(e){return{error:'famLoadoutShow threw '+e.message};}
if(!(await until(()=>document.querySelectorAll('.d3chip').length>0,9000)))return{error:'no chips'};
/* WAIT for D3X rather than sampling and hoping - the first run opened the
   shelf before boot finished and reported a meaningless zero. */
if(!(await until(()=>window.D3X&&D3X.ready,20000)))
  return{error:'D3X never became ready in 20s - the count would be meaningless'};
const d3x=window.D3X;
await sleep(1500);
/* now measure a clean window, after adoption has settled */
armed=0; drawn=0;
await sleep(2200);
const chips=[...document.querySelectorAll('.d3chip')];
/* the probe made the SAME accessor mistake as the patch: _d3 is on the die
   div, not the placeholder. Reading the wrong property reported 0 flagged
   while the draw count had already gone 3174 -> 0. */
const dobj=c=>c._d3||((c.querySelector&&c.querySelector('.die'))||{})._d3;
const owned=chips.filter(c=>{const o=dobj(c);return o&&o._d3xOwned===true;}).length;
return {chips:chips.length, adoptedFlagged:owned,
  d3xDice:(d3x.dice||[]).length,
  drawCallsTotal:armed, drawCallsOnUnownedDice:drawn,
  verdict: !d3x.ready ? 'INCONCLUSIVE'
    : owned!==chips.length ? 'FAIL - only '+owned+' of '+chips.length+' chips were flagged as owned'
    : armed===0 ? 'INCONCLUSIVE - D3.draw never fired at all, so the counter proves nothing'
    : drawn===0 ? 'PASS - D3.draw ran '+armed+' times in the window and every call was an owned die bailing out; zero unowned repaints'
    : 'PARTIAL - '+drawn+' repaints of unowned dice in the window'};
