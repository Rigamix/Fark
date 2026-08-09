/* PR4 and PR9 - both are startPTurn against the snapshot it takes at its end.

   PR9  playerTurnCount is incremented at 24746, BEFORE the snapshot at 24893.
        Its sibling turnNum is incremented inside runOppTurn, AFTER the
        snapshot. So a restore re-enters startPTurn and increments
        playerTurnCount a second time for the same turn, while turnNum is
        immune. Consumer: periodic_drain fires on playerTurnCount % interval.

        THE TEST: does the snapshot already contain the increment for the turn
        it describes? If yes for playerTurnCount and no for turnNum, the two
        counters of one fact disagree and the resume double-counts.

   PR4  Preserve pays out at the top of startPTurn - G.kept and G.turnPts - and
        sets G._famPreserve=null before the snapshot. The snapshot carries
        famPreserve (guaranteed null by then) and does NOT carry kept/turnPts.
        So a resume loses the payout AND cannot re-pay it.

        THE TEST: what does the snapshot actually hold after a preserve turn?

   Measured off the real snapshot object rather than reasoned from field lists,
   because the doc's line numbers are from a pinned copy and the file has moved. */
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(f,ms)=>{const t=Date.now();while(Date.now()-t<ms){try{if(f())return true;}catch(e){}await sleep(50);}return false;};
if(typeof launchBossMatch!=='function')return{error:'globals missing'};

_getS(); S.run=S.run||{}; S.run.tier=2;
S.run.dice=['bone','iron','flint','lead','amber','brass'];
S.settings=S.settings||{}; S.settings.reducedMotion=true;
launchBossMatch();
if(!(await until(()=>typeof G!=='undefined'&&G&&G.rung,9000)))return{error:'no match'};
await sleep(750);
/* the snapshot does not exist until a turn has run - startPTurn's last line is
   what creates it. The first version checked before priming and reported "not
   a resumable match", which was the probe's ordering, not the game's. */
try{startPTurn();}catch(e){}
await sleep(500);
if(!S.pendingMatch)return{error:'no pendingMatch even after a turn - not resumable here'};

/* ---------- PR9: the two counters of one fact ------------------------- */
G.npcCardState=G.npcCardState||{};
G.npcCardState.playerTurnCount=5;
G.turnNum=5;
try{startPTurn();}catch(e){return{error:'startPTurn threw '+e.message};}
await sleep(400);
const snap=S.pendingMatch||{};
const PR9={
  livePlayerTurnCount:(G.npcCardState||{}).playerTurnCount,
  snapPlayerTurnCount:((snap.npcCardState)||{}).playerTurnCount,
  liveTurnNum:G.turnNum,
  snapTurnNum:snap.turnNum,
};
/* a restore then a replay: does playerTurnCount move twice for one turn? */
if(snap.npcCardState) G.npcCardState=JSON.parse(JSON.stringify(snap.npcCardState));
if(typeof snap.turnNum==='number') G.turnNum=snap.turnNum;
try{startPTurn();}catch(e){}
await sleep(400);
PR9.afterReplay_playerTurnCount=(G.npcCardState||{}).playerTurnCount;
PR9.afterReplay_turnNum=G.turnNum;
PR9.playerTurnCountDoubleCounts = PR9.afterReplay_playerTurnCount > PR9.livePlayerTurnCount;
PR9.turnNumImmune = PR9.afterReplay_turnNum === PR9.liveTurnNum;

/* ---------- PR4: the preserve payout across a boundary ----------------- */
G._famPreserve={val:1,mat:'amber',pts:100,crack:0};
const beforeKept=(G.kept||[]).length;
try{startPTurn();}catch(e){}
await sleep(500);
const snap2=S.pendingMatch||{};
const PR4={
  paidOut_kept:(G.kept||[]).length, paidOut_turnPts:G.turnPts,
  liveFamPreserveAfter:G._famPreserve,
  snapshotHasKept:Object.prototype.hasOwnProperty.call(snap2,'kept'),
  snapshotKept:snap2.kept,
  snapshotHasTurnPts:Object.prototype.hasOwnProperty.call(snap2,'turnPts'),
  snapshotTurnPts:snap2.turnPts,
  /* IT IS NESTED. famPreserve lives inside famState, not at the top of the
     snapshot - the first run of this probe read snap.famPreserve, got undefined
     and reported the payout lost when the field was simply somewhere else.
     Read both, and say which one carried it. */
  snapshotFamPreserve_top:snap2.famPreserve===undefined?'(absent)':snap2.famPreserve,
  snapshotFamPreserve_famState:(snap2.famState&&snap2.famState.famPreserve!==undefined)
      ?snap2.famState.famPreserve:'(absent)',
  snapshotHasFamState:!!snap2.famState,
};
const _fpSnap=(snap2.famState&&snap2.famState.famPreserve)||snap2.famPreserve||null;
PR4.payoutSurvivesResume = (PR4.snapshotHasKept && (PR4.snapshotKept||[]).length>0)
                        || (_fpSnap!=null);

return {
  PR9:PR9, PR4:PR4,
  verdict:
    (PR9.playerTurnCountDoubleCounts && !PR4.payoutSurvivesResume)
      ? 'BOTH CONFIRMED - the counter double-counts on replay, and the preserve payout is on no snapshot'
    : PR9.playerTurnCountDoubleCounts
      ? 'PR9 STILL BROKEN, PR4 fixed'
    : !PR4.payoutSurvivesResume
      ? 'PR4 STILL BROKEN, PR9 fixed'
    : !PR9.turnNumImmune
      ? 'REGRESSION - turnNum is no longer immune, the fix moved the wrong thing'
      : 'BOTH FIXED - the snapshot records turn-START values and turnNum is still immune'
};
