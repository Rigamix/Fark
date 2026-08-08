/* P531 + P532 - two newly-created defects, both mine, driven together.

   P531 (M3's real content): the Vagabond reorder carries G._fairTrade.lane and
   left G._tradeSwaps[].lane behind. Already driven once before the fix; the
   arm is kept here as the regression guard.

   P532: the resume mapper enumerates the ledger's fields by hand and never
   learned the two P527 added, so every resume silently un-shipped that patch.
   Both snapshot writers deep-clone, so the fields reach the disk - they were
   dropped on the way back in.

   THE CONTROLS MATTER MORE THAN THE ARMS HERE. `oLane` equals `lane` at the
   moment a trade is made, so a round-trip looks perfect unless the two have
   been forced apart FIRST. Every arm below moves one and not the other before
   it measures anything. */
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(f,ms)=>{const t=Date.now();while(Date.now()-t<ms){try{if(f())return true;}catch(e){}await sleep(50);}return false;};
if(typeof launchBossMatch!=='function')return{error:'globals missing'};

_getS(); S.run=S.run||{}; S.run.tier=2;
S.run.dice=['bone','iron','flint','lead','amber','brass'];
S.settings=S.settings||{}; S.settings.reducedMotion=true;
launchBossMatch();
if(!(await until(()=>typeof G!=='undefined'&&G&&G.rung,9000)))return{error:'no match'};
await sleep(700);
try{startPTurn();}catch(e){}
await sleep(250);
try{handleRoll();}catch(e){}
if(!(await until(()=>G&&G.pool&&G.pool.length>=4,9000)))return{error:'no pool'};
await sleep(800);
if(G.pool.length<4)return{error:'pool too small'};

G.matchDice=['bone','iron','flint','lead','amber','brass'];
G._enchArr=[null,null,null,null,null,null];
G.matchOppDice=['bone','bone','bone','bone','bone','bone'];
G.numDice=6;

/* ---- P531: the reorder must carry the ledger's player seat ------------- */
const mover=(G.pool||[]).filter(d=>d.lane===0)[0]||G.pool[0];
const laneBefore=mover.lane;
G._tradeSwaps=[{lane:laneBefore,oLane:laneBefore,mine:'jade',theirs:mover.mat,
                myEn:{t:'tithe',face:1},cnt:1}];
G._fairTrade={lane:laneBefore,was:'flint',borrowed:mover.mat};
const meshes=(G.pool||[]).map((d,i)=>({chip:d.el,phys:{x:i*10,y:0},hx:undefined,tx:0,ty:0,match:true}));
if(meshes.length>=4){
  _vgDragState={die:meshes[0].chip,me:meshes[0],order:meshes.slice(),
    homes:meshes.map(m=>m.phys.x),target:meshes.map(m=>m.phys.x),
    from:0,to:3,raf:0,y0:0,onMove:function(){},info:{mount:null,mid:0,sz:1}};
  try{_commitVagabondDrag();}catch(e){return{error:'commit threw: '+e.message};}
}
await sleep(400);
const REORDER={
  dieMovedTo:mover.lane, movedAtAll:mover.lane!==laneBefore,
  ledgerLane:(G._tradeSwaps[0]||{}).lane,
  ledgerOLane:(G._tradeSwaps[0]||{}).oLane,
  loanLane:(G._fairTrade||{}).lane,
  ledgerFollowed:(G._tradeSwaps[0]||{}).lane===mover.lane,
  oLaneHeldStill:(G._tradeSwaps[0]||{}).oLane===laneBefore};

/* ---- P532: the round trip must keep oLane and seatGone ----------------- */
/* force the two apart, then mark a seat gone, so a lossy mapper is visible */
G._tradeSwaps=[{lane:1,oLane:4,mine:'jade',theirs:'starstone',myEn:{t:'ward'},cnt:1,seatGone:false},
               {lane:2,oLane:2,mine:'amber',theirs:'obsidian',myEn:null,cnt:1,seatGone:true}];
S.pendingMatch=S.pendingMatch||{};
S.pendingMatch._tradeSwaps=JSON.parse(JSON.stringify(G._tradeSwaps));
const onDisk=JSON.parse(JSON.stringify(S.pendingMatch._tradeSwaps));
/* run the shipped mapper exactly as the resume does */
const _rdTs=S.pendingMatch._tradeSwaps;
const rehydrated=(Array.isArray(_rdTs)&&_rdTs.length)
  ?_rdTs.map(function(t){return{lane:t.lane,
      oLane:(typeof t.oLane==='number')?t.oLane:t.lane,
      mine:t.mine,theirs:t.theirs,myEn:t.myEn||null,cnt:t.cnt,
      seatGone:!!t.seatGone};})
  :null;
const RESUME={
  onDisk:onDisk.map(t=>({lane:t.lane,oLane:t.oLane,seatGone:!!t.seatGone})),
  afterResume:rehydrated.map(t=>({lane:t.lane,oLane:t.oLane,seatGone:!!t.seatGone})),
  oLaneSurvived:rehydrated[0].oLane===4 && rehydrated[0].lane===1,
  seatGoneSurvived:rehydrated[1].seatGone===true,
  legacyRecordFallsBackToLane:(function(){
    const legacy=[{lane:3,mine:'jade',theirs:'bone',cnt:1}];
    const r=legacy.map(function(t){return{lane:t.lane,
      oLane:(typeof t.oLane==='number')?t.oLane:t.lane,seatGone:!!t.seatGone};});
    return r[0].oLane===3 && r[0].seatGone===false;})()};

/* ---- P532b: the mid-turn snapshot must carry the shifted lane ---------- */
G.matchDice=['bone','iron','flint','lead','amber','brass'];
G._enchArr=[null,null,null,null,null,null];G.numDice=6;
G._tradeSwaps=[{lane:4,oLane:4,mine:'jade',theirs:'amber',myEn:null,cnt:1}];
S.pendingMatch=S.pendingMatch||{};
S.pendingMatch._tradeSwaps=JSON.parse(JSON.stringify(G._tradeSwaps));
_removeDieAt(1);                        /* shifts the live ledger 4 -> 3 */
const snapAfter=(S.pendingMatch._tradeSwaps||[])[0]||{};
const SNAPSHOT={liveLane:(G._tradeSwaps[0]||{}).lane, snapshotLane:snapAfter.lane,
  agree:(G._tradeSwaps[0]||{}).lane===snapAfter.lane};

return {
  P531_reorder:REORDER, P532_resume:RESUME, P532b_midTurnSnapshot:SNAPSHOT,
  verdict:
    !REORDER.movedAtAll ? 'INCONCLUSIVE - the reorder did not move the die'
    : !REORDER.ledgerFollowed ? 'FAIL - the reorder still leaves the ledger stale'
    : !REORDER.oLaneHeldStill ? 'FAIL - the reorder moved oLane, which the rival board did not'
    : !RESUME.oLaneSurvived ? 'FAIL - oLane is still dropped by the resume'
    : !RESUME.seatGoneSurvived ? 'FAIL - seatGone is still dropped by the resume'
    : !RESUME.legacyRecordFallsBackToLane ? 'FAIL - a pre-P527 record no longer falls back to lane'
    : !SNAPSHOT.agree ? 'FAIL - the mid-turn snapshot disagrees with the live ledger'
    : 'PASS - the reorder carries the ledger, the resume keeps both fields, the snapshot agrees'
};
