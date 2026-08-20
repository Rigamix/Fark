/* THE LADDER, REBUILT AGAINST THE REAL RIVAL (Denis's §1 ruling).
 *
 * Instrument A of the design sketch: tap-driven full-real matches -
 * the engine owns ALL sequencing on both seats (launchBossMatch,
 * handleRoll/handleBank via real taps, runOppTurn scheduled by the
 * engine itself), so every seam ships: caps, final-answer turns, boss
 * cards, tells, falling-star extras. Nothing is modelled.
 *
 * The player's DECISIONS come from the sim harness's own policy
 * objects (F.POLICIES.carl / rita - the same pair as the old table)
 * over F.legalKeeps, so no third keep implementation exists; only the
 * EFFECTING is taps. Gear convention, stated: the measured modal
 * loadout per night (probe_oppturn_ladder's table), no family cards,
 * no enchants - the same bare convention as probe_oppturn_real.
 *
 * Cell config via URL hash: #lad=<tier>,<policy>,<n>
 * Emits one console line per match: LADDER;tier;policy;i;win;pPts;oPts;secs
 * and a final LADDER-CELL summary the collector greps.
 */
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(fn,ms)=>{const t0=Date.now();while(Date.now()-t0<ms){try{if(fn())return true;}catch(e){}await sleep(100);}return false;};
const tap=el=>{if(!el)return false;const r=el.getBoundingClientRect();
  const o={bubbles:true,cancelable:true,clientX:r.left+r.width/2,clientY:r.top+r.height/2};
  el.dispatchEvent(new PointerEvent('pointerdown',o));
  el.dispatchEvent(new PointerEvent('pointerup',o));
  el.dispatchEvent(new MouseEvent('click',o));return true;};
const H=(location.hash.match(/#lad=([^&]+)/)||[])[1]||'';
const [TIER,POL,NRAW]=H.split(',');
const tier=+TIER||0, polName=POL||'carl', N=+NRAW||10;
if(!await until(()=>typeof launchBossMatch==='function'&&typeof S!=='undefined',30000))return {err:'no boot'};
/* the sim harness supplies the policies + legalKeeps - the REAL pair */
try{
  const src=await (await fetch('tools/sim_harness.js')).text();
  (0,eval)(src);
}catch(e){return {err:'harness load: '+e.message};}
if(!window.FSIM||!FSIM.POLICIES[polName])return {err:'no policy '+polName};
const policy=FSIM.POLICIES[polName];
const LOADOUTS=[
  ['bone','bone','bone','bone','bone','bone'],
  ['silver','bone','bone','bone','bone','bone'],
  ['silver','jade','bone','bone','bone','bone'],
  ['silver','jade','jade','bone','bone','bone'],
  ['silver','jade','jade','jade','bone','bone'],
  ['silver','jade','jade','starstone','jade2','bone'],
  ['amber','jade','jade','jade2','starstone','jade2'],
  ['amber','jade','jade','jade2','starstone','jade2']];
if(typeof _getS==='function')_getS();
S.settings=S.settings||{};S.settings.fastRival=true;
S.run._bossSeen={drunkard:1,peasant:1,commoner:1,merchant:1,soldier:1,knight:1,noble:1,bishop:1};
/* rival pacing: the engine resets _ffMult at runOppTurn entry - keep
   pressing it low while their turn runs */
setInterval(()=>{try{if(typeof G!=='undefined'&&G&&(G.phase==='opp'||G._oppTurnActive))G._ffMult=0.05;}catch(e){}},150);
let wins=0,done=0,stalls=0;const LOG=[];const say=t=>{LOG.push(t);try{console.log(t);}catch(e){}};
for(let m=0;m<N;m++){
  const t0=Date.now();
  /* relaunch with retries - a post-loss screen transition can swallow
     one launch (measured: 1 stall-start in 3) */
  let okStart=false;
  for(let _a=0;_a<3&&!okStart;_a++){
    try{delete S.pendingMatch;}catch(e){}
    window._fkDiscardOk=true;
    S.run.tier=tier;
    S.run.dice=LOADOUTS[tier].slice();
    launchBossMatch();
    okStart=await until(()=>typeof G!=='undefined'&&G&&G.phase==='idle'&&!G._endMatchFired&&(G.pTurns||0)===0,15000);
    if(!okStart)await sleep(1800);
  }
  if(!okStart){stalls++;say('LADDER;'+tier+';'+polName+';'+m+';stall-start');continue;}
  await sleep(400);
  G.pF=[];/* bare gear convention, stated */
  const state={};
  let guard=Date.now()+240000, dead=false;
  while(!G._endMatchFired){
    if(Date.now()>guard){dead=true;break;}
    /* the turn STARTS at idle - tap ROLL to begin it (the first draft
       waited for 'choosing' that could never come) */
    if(G.phase==='idle'&&!G._oppTurnActive){tap(document.getElementById('btnRoll'));await sleep(300);}
    /* wait for a decision point or the match end */
    const got=await until(()=>G._endMatchFired||(G.phase==='choosing'&&(G.pool||[]).some(d=>!d.committed&&d.el&&d.el.onclick)),12000);
    if(G._endMatchFired)break;
    if(!got){/* engine mid-beat (rival turn, yields) - keep waiting */
      if(Date.now()>guard){dead=true;break;}
      continue;}
    await sleep(120);
    const free=G.pool.filter(d=>!d.committed&&!d._frozen);
    const keeps=FSIM.legalKeeps(free);
    if(!keeps.length){await sleep(400);continue;}/* the engine will bust it */
    let sel=null;
    try{sel=policy.keep(free,{keeps:keeps,G:G,state:state,rolls:G.turnRollCount||0});}catch(e){}
    if(!sel||!sel.length)sel=keeps[keeps.length-1].sel;
    for(const d of sel){if(d.el&&!d.sel)tap(d.el);await sleep(60);}
    await sleep(180);
    state.oppTotal=G.oPts;state.lastTurn=(G.turnNum||1)>=(G.turnCap||10);
    let bank=false;
    try{bank=policy.bankAt({turnPts:G.turnPts||0,diceLeft:free.length-sel.length,
      rolls:G.turnRollCount||0,state:state,G:G});}catch(e){bank=(G.turnPts||0)>=300;}
    tap(document.getElementById(bank?'btnBank':'btnRoll'));
    await sleep(250);
  }
  if(dead){stalls++;
    try{say('LADDER-STALL;'+tier+';'+polName+';'+m+';phase='+G.phase+';turn='+G.turnNum+';rc='+G.turnRollCount+';pool='+(G.pool||[]).map(d=>d.val+(d.committed?'c':'')).join('.')+';pPts='+G.pPts+';oPts='+G.oPts+';oppActive='+!!G._oppTurnActive+';locked='+!!G._rollLocked+';ge='+(G.phase==='gamblers_eye'));}catch(e){}
    continue;}
  const win=G.pPts>G.oPts?1:0;
  wins+=win;done++;
  say('LADDER;'+tier+';'+polName+';'+m+';'+(win?'win':'loss')+';'+G.pPts+';'+G.oPts+';'+Math.round((Date.now()-t0)/1000));
  await until(()=>!G||!G._oppTurnActive,8000);
  await sleep(2500);/* the post-match screen settles before the relaunch */
}
const rate=done?(wins/done):0;
/* Wilson 95% halfwidth */
const z=1.96,ph=done?((rate+z*z/(2*done))/(1+z*z/done)):0;
const hw=done?(z*Math.sqrt(rate*(1-rate)/done+z*z/(4*done*done))/(1+z*z/done)):0;
say('LADDER-CELL;'+tier+';'+polName+';n='+done+';wins='+wins+';rate='+(rate*100).toFixed(1)+';wilson='+(ph*100).toFixed(1)+'±'+(hw*100).toFixed(1)+';stalls='+stalls);
return {tier,policy:polName,n:done,wins,rate:+(rate*100).toFixed(1),stalls,log:LOG};
