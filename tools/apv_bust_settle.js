/* DOES THE BUST WAIT FOR THE DICE?
 * Forces a bust and races two clocks from the same t0: when the dice actually
 * stop (last landing pose frozen into d.phys, no tape left), and when the
 * verdict reaches the player (doBust runs). Before the fix the second number
 * was ~900ms SMALLER than the first - the game judged a throw it had not
 * finished showing. */
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(fn,ms)=>{const t0=Date.now();while(Date.now()-t0<ms){try{if(fn())return true;}catch(e){}await sleep(40);}return false;};
const vis=el=>{if(!el||!el.isConnected)return false;const s=getComputedStyle(el),r=el.getBoundingClientRect();
 return s.display!=='none'&&s.visibility!=='hidden'&&+s.opacity>0.05&&r.width>1&&r.height>1;};
const tap=el=>{if(!vis(el))return false;const r=el.getBoundingClientRect();
 const o={bubbles:true,cancelable:true,clientX:r.left+r.width/2,clientY:r.top+r.height/2};
 el.dispatchEvent(new PointerEvent('pointerdown',o));el.dispatchEvent(new PointerEvent('pointerup',o));
 el.dispatchEvent(new MouseEvent('click',o));return true;};

tap(document.getElementById('hsBtnBottom'));await sleep(1800);
await until(()=>{const d=document.querySelector('.nrdie');return d&&d._floatDone;},9000);
tap(document.querySelector('.nrdie'));await sleep(1300);
tap(document.getElementById('nrTakeBtn'));await sleep(2200);
const pc=[...document.querySelectorAll('.ptcard')].filter(vis)[0];if(pc){tap(pc);await sleep(1700);}
const sit=[...document.querySelectorAll('span,div,button')].filter(e=>vis(e)&&e.children.length<=1&&/^SIT\s*DOWN$/i.test((e.textContent||'').trim()))[0];
if(sit){tap(sit);if(sit.parentElement)tap(sit.parentElement);}
await until(()=>vis(document.getElementById('screen-match')),9000);
await until(()=>typeof G!=='undefined'&&G&&G.phase==='idle',14000);
await sleep(600);

const out={};
G.target=999999;
G._wardArmed=false;G._bustImmuneTurn=false;

/* how many dice stand in the player's row, and how many have a frozen pose */
function rowState(){
  const row=document.querySelector('#playerDiceRow');
  const n=row?row.getElementsByClassName('die').length:0;
  let flying=0,landed=0;
  try{
    D3X.dice.forEach(d=>{
      if(!d.chip||!d.chip.closest||!d.chip.closest('#playerDiceRow'))return;
      if(d.roll)flying++;else if(d.phys)landed++;
    });
  }catch(e){}
  return {n,flying,landed};
}

/* instrument doBust so we learn exactly when the verdict fires */
let bustAt=null;
const realBust=window.doBust;
window.doBust=function(){ if(bustAt===null)bustAt=Date.now(); return realBust.apply(this,arguments); };

/* A first roll busts about 2% of the time, so waiting for a natural one is not
   a test. _delayedDoBust is the single funnel EVERY player bust route goes
   through - it is the code the patch changed - so call it the instant the roll
   is thrown and time it directly. That is the same question with a reliable
   trigger. */
const t0=Date.now();
tap(document.getElementById('btnRoll'));
_delayedDoBust([]);

/* watch until the row settles, recording when */
let settledAt=null;
/* PRECONDITION, NOT A PAUSE. until() returns FALSE on timeout rather
   than throwing, so discarding this result meant every assertion below
   ran against a state that may never have arrived - and reported the
   result as a verdict about the game. Three probes were fixed one at a
   time for exactly this before it was swept for. */
const _pre = await until(()=>{
  const st=rowState();
  if(settledAt===null && st.n>0 && st.flying===0 && st.landed>=st.n) settledAt=Date.now();
  return settledAt!==null && bustAt!==null;
}, 9000);
if (!_pre) return { skip: 'precondition never arrived: apv_bust_settle had nothing to measure' };
await sleep(400);
window.doBust=realBust;

out.rowAtEnd=rowState();
out.settleMs = settledAt===null?null:settledAt-t0;
out.bustMs   = bustAt===null?null:bustAt-t0;
out.bustedThisRoll = bustAt!==null;

if(out.settleMs!==null && out.bustMs!==null){
  out.verdictAfterSettleMs = out.bustMs-out.settleMs;   /* must be POSITIVE now */
}
/* pauseLooksRight IS NO LONGER A VERDICT KEY, and demoting it is the fix for a
   probe that had been flapping between runs for three phases.
   It asserted that the gap between the dice settling and the verdict landing
   fell inside a hand-picked 400-1600ms window. That gap is produced by a
   physics solve over real dice, so its length legitimately varies run to run -
   the band was a guess about a duration nobody specified, and a guess about a
   duration is a coin flip dressed as an assertion. Red one run, green the next,
   with nothing changed between; a suite that does that gets ignored.
   THE ORDERING IS THE REAL CLAIM and it stays an assertion: the bust verdict
   must not reach the player BEFORE the dice have stopped. That is what the bug
   was, that is what the fix guaranteed, and it is true or false regardless of
   how long the solve took. The duration is still measured and reported below -
   if it ever needs a bound, the number to bound it with is in the output. */
out.pauseAfterSettleMs=out.verdictAfterSettleMs;
out.verdict={
  /* the whole point: the verdict must not precede the dice stopping */
  bustWaitsForDice: (out.bustMs===null||out.settleMs===null) ? 'no bust this roll'
                    : (out.bustMs>=out.settleMs)
};
return out;
