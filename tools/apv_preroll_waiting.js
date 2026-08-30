/* P875 - the two triggers, driven.
 *
 * The claim P874 could not make: that the preroll and waiting rows are
 * REACHABLE. So this does not inspect tables - it plays, and records what the
 * dialogue layer actually asks for.
 *
 * THE CLOCK IS SHORTENED, NOT FAKED. DLG_IDLE_MS is read at arm time, so the
 * probe drops it to 600ms to keep the run short - that exercises the whole
 * mechanism (arm, re-arm, latch, guards) and only shortens the wait. The
 * SHIPPED value is asserted separately, because a probe that passes on a
 * constant it rewrote has proved nothing about what players get.
 */
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(fn,ms)=>{const t0=Date.now();while(Date.now()-t0<ms){try{if(fn())return true;}catch(e){}await sleep(80);}return false;};
await until(()=>typeof launchBossMatch==='function'&&typeof DLG!=='undefined',20000);
_getS();window._fkDiscardOk=true;
const out={shippedIdleMs:(typeof DLG_IDLE_MS!=='undefined')?DLG_IDLE_MS:null};

/* record every category the dialogue layer is asked for, and what resolved */
const asked=[];
const _origTrigger=DLG.trigger.bind(DLG);
DLG.trigger=function(cat){
  let line=null;
  try{const m=_DLG_MOMENT[cat];if(m)line=_dlgEvent(m);}catch(e){}
  asked.push({cat,line});
  return _origTrigger(cat);
};

/* ── leg 1: PREROLL at the head of the rival's turn ───────────────── */
S.run.tier=1;S.run.gold=500;
try{delete S.pendingMatch;}catch(e){}
launchBossMatch();
await until(()=>typeof G!=='undefined'&&G&&G.phase==='idle',15000);
await sleep(1500);
/* a patron seat is what gives preroll a pool to draw from */
window._lastSeatArt='Nell';window._lastSeatTrait='steady';
asked.length=0;
G.pPts=0;G.turnPts=0;G.kept=[];
try{if(typeof endTurn==='function')endTurn();else{G.phase='opp';runOppTurn();}}catch(e){out.leg1Threw=e.message;}
await sleep(2500);
out.preroll={
  triggered:asked.some(a=>a.cat==='OPP_TURN_START'),
  resolvedToALine:asked.filter(a=>a.cat==='OPP_TURN_START').map(a=>a.line),
};

/* ── leg 2: WAITING after idle on the player's turn ───────────────── */
DLG_IDLE_MS=600;                       /* mechanism, not the constant */
await until(()=>G&&(G.phase==='idle'||G.phase==='choosing'),20000);
window._lastSeatArt='Nell';window._lastSeatTrait='steady';
asked.length=0;
try{_dlgIdleFired=false;_dlgIdleArm();}catch(e){out.leg2Threw=e.message;}
await sleep(1600);
out.waiting={
  triggered:asked.some(a=>a.cat==='PLAYER_IDLE'),
  resolvedToALine:asked.filter(a=>a.cat==='PLAYER_IDLE').map(a=>a.line),
  firedCount:asked.filter(a=>a.cat==='PLAYER_IDLE').length,
};

/* ── leg 3: ONCE per turn - a second wait must stay silent ─────────── */
asked.length=0;
try{_dlgIdleArm();}catch(e){}
await sleep(1400);
out.waitingSecondTime=asked.filter(a=>a.cat==='PLAYER_IDLE').length;

/* ── leg 4: player INPUT re-arms it, so an active player is never nagged ── */
asked.length=0;
try{_dlgIdleFired=false;_dlgIdleArm();}catch(e){}
for(let i=0;i<6;i++){                  /* keep tapping inside the window */
  await sleep(200);
  document.dispatchEvent(new PointerEvent('pointerdown',{bubbles:true}));
}
out.nagWhileActive=asked.filter(a=>a.cat==='PLAYER_IDLE').length;
await sleep(900);                      /* then stop, and it should land */
out.nagAfterStopping=asked.filter(a=>a.cat==='PLAYER_IDLE').length;

/* ── leg 5: it must NOT fire into the rival's turn ─────────────────── */
asked.length=0;
try{_dlgIdleFired=false;_dlgIdleArm();}catch(e){}
G.phase='opp';                         /* turn passes while the clock runs */
await sleep(1400);
out.firedDuringOppTurn=asked.filter(a=>a.cat==='PLAYER_IDLE').length;
G.phase='idle';

/* ── leg 6: nothing in the tables is stranded any more ─────────────── */
const moments=new Set();
PATRON_LINES.forEach(r=>{const m=/^patron:[a-z]+:([a-zA-Z]+)$/.exec(r.p);if(m)moments.add(m[1]);});
const fireable=new Set(Object.keys(_DLG_MOMENT).map(k=>_DLG_MOMENT[k]).concat(['win','loss','recog']));
out.stillStranded=[...moments].filter(m=>!fireable.has(m)).sort();

DLG.trigger=_origTrigger;
out.VERDICT={
  shippedClockIsNineSeconds: out.shippedIdleMs===9000,
  prerollFires:              out.preroll.triggered===true,
  prerollFindsAPatronLine:   out.preroll.resolvedToALine.some(Boolean),
  waitingFires:              out.waiting.triggered===true,
  waitingFindsAPatronLine:   out.waiting.resolvedToALine.some(Boolean),
  waitingOncePerTurn:        out.waitingSecondTime===0,
  activePlayerNeverNagged:   out.nagWhileActive===0,
  butNaggedOnceTheyStop:     out.nagAfterStopping===1,
  silentDuringRivalTurn:     out.firedDuringOppTurn===0,
  nothingStrandedAnyMore:    out.stillStranded.length===0,
};
out.PASS=Object.keys(out.VERDICT).every(k=>out.VERDICT[k]===true);
return out;
