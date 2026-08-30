/* P876 / P878 - the lane-mark window and the card mark, on the FX harness.
 *
 * Rewritten onto tools/_fxh.js because the previous version failed three times
 * for reasons that had nothing to do with the code: the harness renders the 3D
 * layer at ~1fps, the wait for `choosing` silently expired, and the
 * clean-canvas control tested px===0 alone - which passes whenever nothing
 * ever painted. The harness separates `exists` from `px` and reports whether
 * each wait actually arrived, so a vacuous pass is not available.
 */
eval(await (await fetch('/tools/_fxh.js')).text());
const out={};

/* ══ 1. THE WINDOW: attempts, not turns lurked (brief 3.2) ═══════════
   A due mark either fires or misses and BOTH cost an attempt - so the two
   cases must come out identical, which is the point and also the thing a
   careless probe would report as a bug. */
const realG=(typeof G!=='undefined')?G:null;
G={oppTurnCount:0};
G.oppTurnCount=0;_lmArm('_probe',2,2,null);      /* Kindred: two attempts */
G.oppTurnCount=1;
out.due1=_lmDue('_probe');
_lmSpend('_probe');
out.after1={live:G._probe.live,turns:G._probe.turns};
G.oppTurnCount=2;
out.due2=_lmDue('_probe');
_lmSpend('_probe');
out.after2={live:G._probe.live,turns:G._probe.turns};
G.oppTurnCount=0;_lmArm('_probe',2,1,null);G.oppTurnCount=1;_lmSpend('_probe');
out.singleAttempt={live:G._probe.live};
out.deferIsGone=(typeof _lmDefer==='undefined');
if(realG)G=realG;

/* ══ 2. THE CARD MARK PAINTS WITH NOTHING SELECTED ═══════════════════ */
const m=await FXH.match(1);
if(!m.ok)return Object.assign(out,{err:m.why});
const r=await FXH.rollAndSettle();
out.gotToTheDice={ok:r.ok,reachedChoosing:r.reachedChoosing,tapeDrained:r.tapeDrained,freeDice:r.freeDice,why:r.why};
if(!r.ok)return Object.assign(out,{err:'never got to the dice: '+r.why});
const die=r.free[0];

/* A. exactly what Steady Hand leaves behind: marked, nothing selected */
out.markAlone=FXH.paintWith(()=>{FXH.clearMarks();die.el.classList.add('cardmark');});
/* B. control - the canvas must EXIST and be empty, not merely absent */
out.nothingAtAll=FXH.paintWith(()=>{FXH.clearMarks();});
/* C. control - a selection alone still paints, so the guard change kept it */
out.selectionAlone=FXH.paintWith(()=>{FXH.clearMarks();die.el.classList.add('selected');die.sel=true;});

out.VERDICT={
  firstAttemptSpends:      out.after1.turns===1&&out.after1.live===true,
  stillDueForTheSecond:    out.due2===true,
  secondAttemptRetires:    out.after2.live===false,
  singleAttemptDiesAtOnce: out.singleAttempt.live===false,
  deferVerbDeleted:        out.deferIsGone===true,
  probeReachedTheDice:     r.ok===true,
  markPaintsWithNothingSelected: out.markAlone.px>0,
  cleanCanvasExistsAndIsEmpty:   out.nothingAtAll.exists===true&&out.nothingAtAll.px===0,
  selectionStillPaints:          out.selectionAlone.px>0,
};
out.PASS=Object.keys(out.VERDICT).every(k=>out.VERDICT[k]===true);
return out;
