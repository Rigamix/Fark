/* P553 - the interactive half of the draft, which is the half that matters:
   you tap a die to read it and take it.

   Four things, in the order a player does them:
     FOCUS    the tapped die is the only one drawn, it is bigger, and it turns
              (the focus idle spin owns the pose while it is held)
     LAYERS   the canvas comes up WITH the dice - #nrScrim is z5 and the read-out
              panel z8, so a canvas left at its default z2 would render the
              focused die under the scrim it is meant to stand out against
     RETURN   letting go eases the die back. The ease targets a pose; if it
              targets the WRONG pose the die arrives and then jumps, because the
              settle leaves a small permanent in-plane roll the rest pose has no
              idea about
     TAKE     the overlay goes and nothing is left holding a detached chip

   RETURN is the reason this probe exists. It is a one-frame jump at the end of
   a 450ms ease and no screenshot would ever catch it. */
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(f,ms)=>{const t=Date.now();while(Date.now()-t<ms){try{if(f())return true;}catch(e){}await sleep(60);}return false;};
const qv=d=>d&&d.obj?[d.obj.quaternion.x,d.obj.quaternion.y,d.obj.quaternion.z,d.obj.quaternion.w]:null;
const dq=(a,b)=>(a&&b)?Math.max(...a.map((v,i)=>Math.abs(v-b[i]))):null;

_getS(); S.run=S.run||{}; S.run.tier=1; S.run.gold=200;
try{D3X.boot();}catch(e){}
if(!(await until(()=>D3X.ready,25000)))return{error:'D3X never booted'};
try{startNewRun();}catch(e){}
_starterOffer=['silver','obsidian','vagabond'];
try{famRunDraftShow();}catch(e){}
if(!(await until(()=>document.querySelectorAll('#nrDice .d3slot').length===3,9000)))return{error:'no dice'};
if(!(await until(()=>[...document.querySelectorAll('.nrdie')].every(n=>n._floatDone),9000)))
  return{error:'the tiles never finished floating, so the die cannot be tapped'};
await sleep(400);

const mine=()=>(D3X.dice||[]).filter(d=>d.chip.closest('#nrDice'));
const rest=mine();
const sz0=rest.map(d=>d.obj.scale.x);

/* ── FOCUS ─────────────────────────────────────────────────────────── */
_nrFocus(1);
await sleep(900);
const foc=mine();
const zi=foc.findIndex(d=>d.chip.closest('.zoom'));
const q1=qv(foc[zi]);
await sleep(700);
const q2=qv(foc[zi]);
const FOCUS={zoomed:zi,
  drawn:foc.filter(d=>d.obj.visible).length,
  grew:zi>=0?+(foc[zi].obj.scale.x/sz0[zi]).toFixed(3):null,
  turning:dq(q1,q2)};
const LAYERS={canvasZ:+getComputedStyle(D3X.renderer.domElement).zIndex,
  scrimZ:+getComputedStyle(document.getElementById('nrScrim')).zIndex,
  panelZ:+getComputedStyle(document.getElementById('nrFocusPanel')).zIndex,
  diceZ:+getComputedStyle(document.getElementById('nrDice')).zIndex};

/* ── RETURN: sample right through the end of the 450ms ease ────────── */
/* SAMPLE THE STEPS, and judge them AFTER the ease has finished. The ease is a
   450ms cubic that starts fast and covers whatever angle the focus spin racked
   up, so a big step early in it proves nothing - the first version of this
   probe called that a failure and it was reading the ease doing its job.
   The ease's own speed is zero by the time it ends, so ANY large step after
   450ms is the die being posed by something else. */
_nrUnfocus();
const t0=performance.now();
const trail=[],ts=[];
for(let n=0;n<26;n++){trail.push(qv(mine()[zi]));ts.push(performance.now()-t0);await sleep(40);}
const steps=[];
for(let n=1;n<trail.length;n++)steps.push({t:Math.round(ts[n]),d:+dq(trail[n-1],trail[n]).toFixed(4)});
const after=steps.filter(s=>s.t>500);
const worstAfter=after.reduce((a,b)=>b.d>a.d?b:a,{t:0,d:0});
const RETURN={steps,settledMax:worstAfter,
  /* the breathe alone moves about 1e-3 per 40ms */
  smooth:worstAfter.d<0.01};

/* ── TAKE ──────────────────────────────────────────────────────────────
   `stillHeld` is REPORTED, NOT ASSERTED, and the reason is measured rather
   than assumed: closing the loadout - a surface this patch never touched -
   leaves 6 of 6 records behind in exactly the same way (see the run recorded
   in NEXT_SESSION). D3X only prunes on the next sync, because tick's
   no-live-chips branch falls into syncMatch, which returns without detaching
   when _matchOn is already false. That is a lifecycle gap in D3X, not a draft
   one, and failing this probe on it would blame the port for it. */
try{famRunDraftPick(1);}catch(e){return{error:'pick threw '+e.message,FOCUS,LAYERS,RETURN};}
await sleep(900);
const TAKE={overlay:!!document.getElementById('famRunDraft'),
  stillHeld:mine().length,
  note:'stillHeld matches the loadout - pre-existing, pruned on the next sync'};

const okF=FOCUS.zoomed>=0&&FOCUS.drawn===1&&FOCUS.grew>1.5&&FOCUS.turning>1e-4;
const okL=LAYERS.canvasZ>=LAYERS.scrimZ&&LAYERS.canvasZ>=LAYERS.diceZ&&LAYERS.panelZ>LAYERS.canvasZ;
return {FOCUS,LAYERS,RETURN,TAKE,
  verdict:
    !okF ? 'FAIL - focus: '+JSON.stringify(FOCUS)+' (want 1 drawn, >1.5x, turning)'
  : !okL ? 'FAIL - the canvas does not come up with the dice: '+JSON.stringify(LAYERS)
  : !RETURN.smooth ? "FAIL - the die JUMPS after the return ease has finished (step "+RETURN.settledMax.d+" at "+RETURN.settledMax.t+"ms) - the ease is targeting the wrong pose"
  : TAKE.overlay ? 'FAIL - taking the die left the overlay up'
  : 'PASS - focus draws one die '+FOCUS.grew+'x and turns it, the canvas rides above the scrim, the return is smooth, and taking it closes the screen'};
