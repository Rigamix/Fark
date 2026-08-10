/* P547, both directions.

   ARM A is the hazard: force html.fk3d ON and open the draft. Before this
   patch the draft's dice were hidden by CSS with nothing drawing them - three
   empty sockets on the first screen of a new run. They must stay visible.

   ARM B is the control that a too-wide fix would fail: a real .d3chip surface
   must STILL hide its DOM die under fk3d. If it does not, the CSS cube and the
   WebGL cube both draw and every 3D surface double-renders. Scoping too far is
   the easy mistake here and it is invisible on the draft. */
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(f,ms)=>{const t=Date.now();while(Date.now()-t<ms){try{if(f())return true;}catch(e){}await sleep(60);}return false;};
_getS(); S.run=S.run||{}; S.run.tier=2; S.run.gold=500;
S.run.dice=['bone','iron','flint','amber','jade','starstone'];
S.settings=S.settings||{}; S.settings.reducedMotion=true;

/* ---- ARM A: the draft, with fk3d forced on --------------------------- */
try{startNewRun();}catch(e){}
try{famRunDraftShow();}catch(e){return{error:'draft threw '+e.message};}
if(!(await until(()=>document.getElementById('famRunDraft'),9000)))return{error:'no overlay'};
document.documentElement.classList.add('fk3d');   /* the condition that used to bite */
await sleep(3000);
const hosts=[...document.querySelectorAll('.nrdie .d3host')];
const draftVis=hosts.map(h=>{const d=h.querySelector('.die')||h.querySelector('.d3slot');
  return d?getComputedStyle(d).visibility:'no-die';});
const A={hosts:hosts.length, vis:draftVis, forcedFk3d:document.documentElement.classList.contains('fk3d'),
  allVisible:hosts.length>0&&draftVis.every(v=>v==='visible')};
try{document.getElementById('famRunDraft').remove();}catch(e){}
document.documentElement.classList.remove('fk3d');

/* ---- ARM B: a chip surface must still hide its DOM die --------------- */
await sleep(400);
try{famLoadoutShow();}catch(e){return{error:'loadout threw '+e.message};}
if(!(await until(()=>document.querySelectorAll('.d3chip').length>0,9000)))return{error:'no chips'};
if(!(await until(()=>window.D3X&&D3X.ready,20000)))return{error:'D3X never ready'};
await sleep(2200);
const chips=[...document.querySelectorAll('.d3chip')];
const chipVis=chips.map(c=>{const d=c.querySelector('.die');return d?getComputedStyle(d).visibility:'no-die';});
const B={chips:chips.length, vis:chipVis,
  fk3d:document.documentElement.classList.contains('fk3d'),
  d3xDice:(window.D3X&&D3X.dice)?D3X.dice.length:null,
  allHidden:chips.length>0&&chipVis.every(v=>v==='hidden')};

return {A_draft:A, B_chips:B,
  verdict:
    !A.hosts ? 'INCONCLUSIVE - the draft built no dice'
    : !A.forcedFk3d ? 'INCONCLUSIVE - fk3d did not stay on, so the hazard was never reproduced'
    : !A.allVisible ? 'FAIL - draft dice still hidden under fk3d: '+A.vis.join(',')
    : !B.chips ? 'INCONCLUSIVE - no chip surface to control against'
    : !B.fk3d ? 'INCONCLUSIVE - fk3d off on the chip surface, so its hiding was never tested'
    : !B.allHidden ? 'FAIL - a chip surface stopped hiding its DOM die ('+B.vis.join(',')+') - every 3D surface would double-draw'
    : 'PASS - the draft survives fk3d ('+A.hosts+' dice visible) and chip surfaces still hide theirs ('+B.chips+' hidden, '+B.d3xDice+' meshes)'};
