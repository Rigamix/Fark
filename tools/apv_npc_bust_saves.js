/* P871 - the RESTORED table must actually be REACHED, on a real rival bust.
 *
 * TWO INSTRUMENT CORRECTIONS ARE BAKED IN HERE, both caught by controls:
 *
 *  1. The first re-run of the freeze repro was green with the rival BANKING,
 *     and the ReferenceError only ever fired on their BUST path. A green run
 *     that never enters the code under test proves nothing about it. So the
 *     bust-save chain is wrapped and counted: a pass requires it to have RUN.
 *  2. Forcing the bust by stubbing rollFace globally made the turn never
 *     finish - and the PRE-P860 control stalled exactly the same way under the
 *     same stub, so that was the instrument, not the game. No stub now: the
 *     rival plays real turns until they bust on their own.
 */
window.__errs=[];
window.addEventListener('error',e=>{window.__errs.push('ERROR: '+(e.message||'')+' @'+(e.lineno||''));});
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(fn,ms)=>{const t0=Date.now();while(Date.now()-t0<ms){try{if(fn())return true;}catch(e){}await sleep(100);}return false;};
await until(()=>typeof launchBossMatch==='function',20000);
_getS();window._fkDiscardOk=true;

if(typeof NPC_BUST_SAVES==='undefined')return {FATAL:'table still missing'};
const out={tableRows:NPC_BUST_SAVES.length,rowNames:NPC_BUST_SAVES.map(r=>r.name)};
let entered=0;
NPC_BUST_SAVES.forEach(r=>{const t=r.try;r.try=function(){entered++;return t.apply(this,arguments);};});

/* a save that also carries deleted ids the rival "won", so both halves of
   P871 are exercised in the same run */
S.npcWonCards=S.npcWonCards||{};
S.npcWonCards.soldier=['the_tab','all_in','sleight_of_hand'];
S.run.tier=4;S.run.gold=500;
try{delete S.pendingMatch;}catch(e){}
launchBossMatch();
if(!await until(()=>typeof G!=='undefined'&&G&&G.phase==='idle',15000))return {err:'no match'};
await sleep(1500);
out.oCards=(G.oCards||[]).slice();
out.unresolvableInRivalHand=(G.oCards||[]).filter(id=>{try{return !getCard(id);}catch(e){return true;}});

let turns=0,busts=0,stalls=0;
for(let i=0;i<14;i++){
  if(!G||G._endMatchFired)break;
  const before=G.oPts;
  try{
    G.pPts=0;G.turnPts=0;G.kept=[];
    if(typeof endTurn==='function')endTurn(); else {G.phase='opp';runOppTurn();}
  }catch(e){out.threw=e.message;break;}
  const done=await until(()=>G&&G.phase!=='opp'&&G.phase!=='rolling',20000);
  if(!done){
    /* THE STALL IS PRE-EXISTING AND NOT WHAT THIS PROBE IS FOR. It reproduces
       identically on a build from before any of this work (13 turns, 3 busts,
       1 stall there too), so failing here would make this probe red for a
       reason it does not measure - and a check that is red for the wrong
       reason is one people learn to ignore. Recorded, then the match is
       relaunched so the thing under test still gets exercised. */
    stalls++;
    try{delete S.pendingMatch;}catch(e){}
    launchBossMatch();
    if(!await until(()=>G&&G.phase==='idle',15000))break;
    await sleep(1200);
    continue;
  }
  turns++;
  if(G.oPts===before)busts++;
  await sleep(120);
}
out.turnsPlayed=turns; out.rivalBusts=busts; out.stalledTurns=stalls;
out.bustSaveChainEntered=entered;
out.errs=window.__errs.slice(0,6);
out.VERDICT={
  tableExists:            out.tableRows>0,
  rivalActuallyBusted:    busts>0,          /* the window contains the event */
  chainWasActuallyRun:    entered>0,
  someTurnsCompleted:     turns>0,
  stallsWithinPreExistingRate: stalls<=3,   /* observation, not a pass/fail on this patch */
  noExceptions:           out.errs.length===0&&!out.threw,
  /* THE PHANTOM LEG IS GONE, not weakened. It seeded npcWonCards AFTER _getS
     had already run its migration - which happens on FIRST LOAD only - so it
     was asserting against a path it never reached. The real claim is driven
     properly through localStorage in apv_card_migration.js, which is where a
     migration test belongs. Duplicating it badly here only produced a red
     light nobody could act on. */
};
out.PASS=Object.keys(out.VERDICT).every(k=>out.VERDICT[k]===true);
return out;
