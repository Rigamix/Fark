/* P553 - the two ways the ported draft can lose its 3D die, and what a player
   sees in each. The screen is the FIRST thing a new run shows, so neither may
   end in an empty palm.

   ARM A - NO WEBGL. The device never gets a renderer. D3X must give up, drop
   html.fk3d, hand the dice back to D3, and the DRAFT MUST STILL ANIMATE - that
   is the whole reason the D3.roll call was kept alongside the D3X one instead
   of being deleted as dead weight. Measured as movement, not as a flag.

   ARM B - THE HOLD NEVER ENDS. `data-anim` holds a die off screen until
   chipAnim arms it, and adoption is also when fk3d hides the DOM cube - so an
   arming call that never arrives means nothing draws the die at all. chipAnim
   is stubbed to a no-op here to reproduce exactly that. The deadline must let
   the die through: STILL, having lost its intro, but on screen.

   Arm B is the one worth having. Arm A is a path P551 already built and this
   only confirms the draft did not break it; arm B is a failure mode this patch
   INTRODUCED, and the probe exists because reasoning about it - not seeing it -
   is what found it. */
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(f,ms)=>{const t=Date.now();while(Date.now()-t<ms){try{if(f())return true;}catch(e){}await sleep(60);}return false;};
const openDraft=async()=>{
  try{document.getElementById('famRunDraft').remove();}catch(e){}
  _starterOffer=['silver','obsidian','vagabond'];
  try{famRunDraftShow();}catch(e){return 'threw '+e.message;}
  return await until(()=>document.querySelectorAll('#nrDice .d3slot').length===3,9000)?null:'no dice built';
};
_getS(); S.run=S.run||{}; S.run.tier=1; S.run.gold=200;
if(!(await until(()=>window.D3X,8000)))return{error:'no D3X'};
try{startNewRun();}catch(e){}

/* ── ARM B first: 3D is UP, but the animation is never handed over ────── */
try{D3X.boot();}catch(e){}
if(!(await until(()=>D3X.ready,25000)))return{error:'D3X never booted'};
const realAnim=D3X.chipAnim;
D3X.chipAnim=function(){};                 /* the arming call that never comes */
let err=await openDraft(); if(err)return{error:'arm B: '+err};
await sleep(1500);
const early=(D3X.dice||[]).filter(d=>d.chip.closest('#nrDice'));
const B_early={held:early.length?early.filter(d=>!d.obj.visible).length:null,of:early.length};
await sleep(2200);                          /* past the 2500ms deadline */
const late=(D3X.dice||[]).filter(d=>d.chip.closest('#nrDice'));
const qA=late.map(d=>d.obj.quaternion.y);
await sleep(700);
const B={adopted:late.length,
  drawn:late.filter(d=>d.obj.visible).length,
  fk3d:document.documentElement.classList.contains('fk3d'),
  domHidden:[...document.querySelectorAll('#nrDice .d3die')].filter(e=>getComputedStyle(e).visibility==='hidden').length,
  /* it has lost its intro, so it must be STILL - a moving die here would mean
     the deadline let a half-armed animation through */
  still:late.every((d,i)=>Math.abs(d.obj.quaternion.y-qA[i])<1e-6)};
D3X.chipAnim=realAnim;
try{document.getElementById('famRunDraft').remove();}catch(e){}

/* ── ARM A: no WebGL at all ───────────────────────────────────────────── */
await sleep(300);
const _gc=HTMLCanvasElement.prototype.getContext;
HTMLCanvasElement.prototype.getContext=function(t){
  if(/webgl/i.test(String(t)))return null;
  return _gc.apply(this,arguments);
};
D3X.ready=false;D3X.loading=false;D3X.fail=false;D3X._need=[];
try{D3X.detach&&D3X.detach();}catch(e){}
document.documentElement.classList.remove('fk3d');
err=await openDraft(); if(err)return{error:'arm A: '+err,B};
try{D3X.boot();}catch(e){}
await sleep(1400);
const slots=[...document.querySelectorAll('#nrDice .d3slot')];
const pose=()=>slots.map(sl=>sl.querySelector('.d3die').style.transform+'|'
  +[...sl.querySelectorAll('.d3f')].map(f=>f.style.transform).join(''));
const p1=pose();
await sleep(700);
const p2=pose();
const A={fail:!!D3X.fail,ready:!!D3X.ready,fk3d:document.documentElement.classList.contains('fk3d'),
  cubes:slots.length,
  visible:[...document.querySelectorAll('#nrDice .d3die')].filter(e=>getComputedStyle(e).visibility==='visible').length,
  owned:[...document.querySelectorAll('#nrDice .d3chip')].filter(c=>c._d3&&c._d3._d3xOwned).length,
  /* P554: THE SHADOW MUST BE OFF HERE TOO, and this is the arm that says so.
     The whole reason the rule went in CSS rather than in D3X is that D3X
     drawing no shadow would still leave the DOM die's ellipse showing on a
     device with no WebGL - which is this device. Asserting it only on the 3D
     path would have proved the easy half. */
  shadows:[...document.querySelectorAll('#nrDice .d3shadow')].filter(e=>getComputedStyle(e).display!=='none').length,
  moving:p1.filter((p,i)=>p!==p2[i]).length};

const okB=B.adopted===3&&B.drawn===3&&B.still&&B_early.held===3;
const okA=A.fail&&!A.fk3d&&A.cubes===3&&A.visible===3&&A.owned===0&&A.moving===3&&A.shadows===0;
return {B_holdDeadline:{...B_early,...B},A_noWebGL:A,
  verdict:
    B_early.of!==3 ? 'INCONCLUSIVE - arm B adopted '+B_early.of+' dice, so the hold was never exercised'
  : B_early.held!==3 ? 'FAIL - the hold did not hold: '+B_early.held+'/3 hidden at 1.5s, so the deadline test below proves nothing'
  : !okB ? 'FAIL - an unarmed chip never reached the screen: '+JSON.stringify(B)
  : !okA ? 'FAIL - no-WebGL draft: '+JSON.stringify(A)+' (want fail, no fk3d, 3 visible cubes, 0 owned, 3 moving, 0 shadows)'
  : 'PASS - unarmed chips fall through to a still die after 2.5s, and a WebGL-less device still gets three animating DOM dice with no shadow under them'};
