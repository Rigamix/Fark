/* P553 - does the first-night draft actually draw through D3X, and does it
   still MOVE?

   The port is only worth anything if all four of these hold at once, so the
   probe drives one run of the real screen and reads all four off it:

     1. ADOPTION   D3X holds three dice mounted on #nrStage. If sync picks a
                   different host (its selector takes chips[0]'s nearest stage,
                   and the tier screen is still underneath) the draft renders
                   nothing and every other check below is vacuous.
     2. HANDOVER   the DOM cube is hidden, its shadow is NOT, and _d3xOwned is
                   set on all three - so exactly one renderer is drawing.
     3. MOTION     the quaternion changes between two samples taken during the
                   settle, and again between two taken after it. A still die
                   would pass 1 and 2 and be the exact failure Denis ruled
                   against.
     4. THE HOLD   nothing is drawn before the animation is armed. Sampled at
                   400ms, when the chips exist and have a box but the draft has
                   not built its dice yet.

   And one control: the FACE. sync reads data-val at adoption, 950ms before the
   draft picks a die's face - so the two renderers agreeing is not automatic. */
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(f,ms)=>{const t=Date.now();while(Date.now()-t<ms){try{if(f())return true;}catch(e){}await sleep(50);}return false;};

_getS(); S.run=S.run||{}; S.run.tier=1; S.run.gold=200;
S.settings=S.settings||{};

/* D3X boots LAZILY - nothing loads three.js until a live chip asks for it - so
   a cold page never becomes ready on its own. Boot it here, before the draft,
   because the hold check below reads the very first frames of that surface and
   a four-request boot in the middle of them would measure the loader, not the
   patch. */
try{D3X.boot();}catch(e){}
if(!(await until(()=>window.D3X&&D3X.ready,25000)))return{error:'D3X never booted'};

try{startNewRun();}catch(e){}
try{famRunDraftShow();}catch(e){return{error:'draft threw '+e.message};}
if(!(await until(()=>document.getElementById('famRunDraft'),9000)))return{error:'no overlay'};

/* ---- 4. THE HOLD: before the dice are built (they land at 950ms) ------ */
await sleep(420);
const chipsEarly=[...document.querySelectorAll('#nrDice .d3chip')];
const HOLD={
  chips:chipsEarly.length,
  boxed:chipsEarly.filter(c=>c.getBoundingClientRect().width>1).length,
  adopted:(D3X.dice||[]).filter(d=>chipsEarly.indexOf(d.chip)>=0).length,
  drawn:(D3X.dice||[]).filter(d=>chipsEarly.indexOf(d.chip)>=0&&d.obj&&d.obj.visible).length,
  domDice:document.querySelectorAll('#nrDice .d3slot').length};

/* ---- 1/2. adoption and handover, once everything has settled --------- */
if(!(await until(()=>document.querySelectorAll('#nrDice .d3slot').length===3,6000)))
  return{error:'the draft never built its DOM dice',HOLD};
await sleep(2600);

const chips=[...document.querySelectorAll('#nrDice .d3chip')];
const recs=chips.map(c=>(D3X.dice||[]).find(d=>d.chip===c)||null);
const ADOPT={
  chips:chips.length,
  mount:D3X.mount&&(D3X.mount.id||D3X.mount.className),
  adopted:recs.filter(Boolean).length,
  fk3d:document.documentElement.classList.contains('fk3d'),
  canvasIn:!!(D3X.renderer&&D3X.renderer.domElement.closest&&D3X.renderer.domElement.closest('#nrStage')),
  canvasZ:D3X.renderer?getComputedStyle(D3X.renderer.domElement).zIndex:null};

const HAND=chips.map(c=>{
  const cube=c.querySelector('.d3die'),sh=c.querySelector('.d3shadow');
  return {cube:cube?getComputedStyle(cube).visibility:'none',
          shadow:sh?getComputedStyle(sh).visibility:'none',
          shadowOp:sh?+getComputedStyle(sh).opacity:null,
          owned:!!(c._d3&&c._d3._d3xOwned)};
});

/* ---- the FACE control: both renderers on the same number ------------- */
const FACE=chips.map((c,i)=>({
  attr:+c.getAttribute('data-val'),
  d3x:recs[i]?recs[i].val:null,
  dom:c._d3?c._d3.result:null,
  inFaceList:(getDie(c.getAttribute('data-mat')).faces||[]).indexOf(+c.getAttribute('data-val'))>=0}));

/* ---- 3. MOTION, after the settle: the breathe ------------------------ */
const qOf=d=>d&&d.obj?[d.obj.quaternion.x,d.obj.quaternion.y,d.obj.quaternion.z,d.obj.quaternion.w]:null;
const yOf=d=>d&&d.obj?d.obj.position.y:null;
const q1=recs.map(qOf),y1=recs.map(yOf);
await sleep(900);
const q2=recs.map(qOf),y2=recs.map(yOf);
const dq=(a,b)=>(a&&b)?Math.max(...a.map((v,i)=>Math.abs(v-b[i]))):null;
const BREATHE={
  turned:q1.map((q,i)=>dq(q,q2[i])),
  bobbed:y1.map((y,i)=>(y===null||y2[i]===null)?null:Math.abs(y-y2[i])),
  moving:q1.every((q,i)=>dq(q,q2[i])>1e-4)&&y1.some((y,i)=>Math.abs(y-y2[i])>0.1)};

const okHold =HOLD.chips===3&&HOLD.boxed===3&&HOLD.adopted===3&&HOLD.drawn===0&&HOLD.domDice===0;
const okAdopt=ADOPT.adopted===3&&ADOPT.mount==='nrStage'&&ADOPT.fk3d&&ADOPT.canvasIn;
const okHand =HAND.every(h=>h.cube==='hidden'&&h.shadow==='visible'&&h.owned);
const okFace =FACE.every(f=>f.attr===f.d3x&&f.attr===f.dom&&f.inFaceList);

return {HOLD,ADOPT,HAND,FACE,BREATHE,
  verdict:
    !okHold  ? 'FAIL - the hold: '+JSON.stringify(HOLD)+' (want 3 chips, 3 boxed, 3 adopted, 0 drawn, 0 dom dice)'
  : !okAdopt ? 'FAIL - adoption: '+JSON.stringify(ADOPT)
  : !okHand  ? 'FAIL - handover: '+JSON.stringify(HAND)
  : !okFace  ? 'FAIL - the two renderers disagree about the face: '+JSON.stringify(FACE)
  : !BREATHE.moving ? 'FAIL - the dice are STILL after settling (turn '+BREATHE.turned.join(',')+' bob '+BREATHE.bobbed.map(b=>b&&b.toFixed(2)).join(',')+')'
  : 'PASS - 3 dice on #nrStage, DOM cube hidden + shadow kept + owned, faces agree, and still breathing after the settle'};
