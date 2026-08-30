/* P876 - the three fixes, driven.
 *
 * THE PAINT LEG USES A FORCED DRAW, and that is the harness pattern Denis
 * asked for rather than a shortcut. _drawGlow only runs from D3X's frame pass,
 * the headless harness renders the 3D layer at ~1 fps, and the pass refuses to
 * run at all while D3X._rolling() is true - which takes ~19s to clear here
 * against ~700ms real. So: poll the STATE until the tape has drained, then
 * call the painter directly and read the canvas. Nothing about the painter is
 * stubbed; only the clock is waited out.
 */
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(fn,ms)=>{const t0=Date.now();while(Date.now()-t0<ms){try{if(fn())return true;}catch(e){}await sleep(150);}return false;};
await until(()=>typeof launchBossMatch==='function',20000);
_getS();window._fkDiscardOk=true;
const out={};

/* ══ 1. THE WINDOW LOGIC, on the primitives themselves ═══════════════
   These are pure functions of G, so they can be exercised exactly without a
   match - and the bug was never about the match, it was about which branch
   the spend sat in. */
function lmCase(label,fire){
  G=G||{};
  G.oppTurnCount=0;
  _lmArm('_probe',2,2,null);              /* a Kindred-doubled mark: two turns */
  const armed={live:G._probe.live,turns:G._probe.turns,turn:G._probe.turn};
  G.oppTurnCount=1;                       /* their turn arrives */
  const due1=_lmDue('_probe');
  if(fire)_lmSpend('_probe'); else _lmDefer('_probe');
  const after1={live:G._probe.live,turns:G._probe.turns,turn:G._probe.turn};
  G.oppTurnCount=2;                       /* and the next one */
  const due2=_lmDue('_probe');
  return {label,armed,due1,after1,due2};
}
const realG=(typeof G!=='undefined')?G:null;
G={oppTurnCount:0};
out.fired  = lmCase('it acted',   true);
out.noop   = lmCase('it could not act', false);
/* and a second spend must retire it */
G.oppTurnCount=0;_lmArm('_probe',2,1,null);G.oppTurnCount=1;_lmSpend('_probe');
out.singleTurnRetires={live:G._probe.live};
if(realG)G=realG;

/* ══ 2. THE CARD MARK ACTUALLY PAINTS ════════════════════════════════ */
S.run.tier=1;S.run.gold=500;
try{delete S.pendingMatch;}catch(e){}
launchBossMatch();
if(!await until(()=>typeof G!=='undefined'&&G&&G.phase==='idle',20000))return Object.assign(out,{err:'no match'});
await sleep(1500);
const Q=[];for(let i=0;i<12;i++)Q.push(i%2?5:1);
const realE=window._enchRollM;window._enchRollM=(m,e)=>Q.length?Q.shift():realE(m,e);
const tap=el=>{const r=el.getBoundingClientRect();const o={bubbles:true,cancelable:true,clientX:r.left+r.width/2,clientY:r.top+r.height/2};
  el.dispatchEvent(new PointerEvent('pointerdown',o));el.dispatchEvent(new PointerEvent('pointerup',o));el.dispatchEvent(new MouseEvent('click',o));};
tap(document.getElementById('btnRoll'));
await until(()=>G.phase==='choosing',20000);
/* THE STATE, not the clock: wait for the physics tape to drain */
out.tapeDrained=await until(()=>!D3X._rolling(),40000);
await sleep(400);

function ink(){
  const cv=document.getElementById('dgCanvas');
  if(!cv||!cv.width)return {exists:!!cv,px:0};
  const x=cv.getContext('2d'),d=x.getImageData(0,0,cv.width,cv.height).data;
  let n=0;for(let i=3;i<d.length;i+=4)if(d[i]>8)n++;
  return {exists:true,px:n};
}
const free=(G.pool||[]).filter(d=>!d.committed);
const mark=free[0];

/* A. THE REAL SITUATION: a mark, and nothing selected. This is exactly what
      Steady Hand leaves behind - it clears `selected`, then marks. */
(G.pool||[]).forEach(d=>{if(d.el){d.el.classList.remove('selected','cardmark');d.sel=false;}});
if(mark&&mark.el)mark.el.classList.add('cardmark');
try{D3X._drawGlow();}catch(e){out.drawThrew=e.message;}
await sleep(150);
out.markAlone=ink();

/* B. CONTROL - nothing marked, nothing selected. The canvas must go clean,
      or a non-zero in A proves nothing. */
if(mark&&mark.el)mark.el.classList.remove('cardmark');
try{D3X._drawGlow();}catch(e){}
await sleep(150);
out.nothingAtAll=ink();

/* C. CONTROL - a selection alone still paints, so the guard change did not
      break what already worked. */
if(mark&&mark.el){mark.el.classList.add('selected');mark.sel=true;}
try{D3X._drawGlow();}catch(e){}
await sleep(150);
out.selectionAlone=ink();

out.VERDICT={
  /* the window logic */
  aFiredMarkSpendsATurn:      out.fired.after1.turns===1&&out.fired.after1.live===true,
  aFiredMarkIsDueAgain:       out.fired.due2===true,
  aNoOpMarkKeepsItsTurns:     out.noop.after1.turns===2&&out.noop.after1.live===true,
  aNoOpMarkIsStillDueNextTurn:out.noop.due2===true,
  lastTurnRetires:            out.singleTurnRetires.live===false,
  /* the paint */
  tapeActuallyDrained:        out.tapeDrained===true,
  markPaintsWithNothingSelected: out.markAlone.px>0,
  canvasGoesCleanWithNoMark:  out.nothingAtAll.px===0,
  selectionStillPaints:       out.selectionAlone.px>0,
};
out.PASS=Object.keys(out.VERDICT).every(k=>out.VERDICT[k]===true);
return out;
