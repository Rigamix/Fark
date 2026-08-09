/* PR10 / P538 - does a Vagabond reorder survive a quit now, and does trade
   still persist the rival's board?

   ARM A  the reorder. It permutes matchDice, _enchArr and the lanes inside
          _fairTrade and _tradeSwaps, and persisted NONE of it - a quit after a
          drag lost the whole rearrangement. The snapshot must now match live.

   ARM B  the control that stops this being a one-way fix. _tradeSnap used to
          write matchOppDice and now delegates to the shared writer; if the
          alsoOpp flag were wrong, trades would silently stop persisting the
          rival's board. So: change matchOppDice, call _tradeSnap, check it
          landed - and separately check the REORDER does NOT write it, because
          a reorder has no business touching the rival's side. */
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(f,ms)=>{const t=Date.now();while(Date.now()-t<ms){try{if(f())return true;}catch(e){}await sleep(50);}return false;};
if(typeof launchBossMatch!=='function')return{error:'globals missing'};
if(typeof _snapDiceOnly!=='function')return{error:'_snapDiceOnly missing - P538 not applied'};

_getS(); S.run=S.run||{}; S.run.tier=2;
S.run.dice=['bone','iron','flint','lead','amber','brass'];
S.settings=S.settings||{}; S.settings.reducedMotion=true;
launchBossMatch();
if(!(await until(()=>typeof G!=='undefined'&&G&&G.rung,9000)))return{error:'no match'};
await sleep(700);
try{startPTurn();}catch(e){}
await sleep(350);
try{handleRoll();}catch(e){}
if(!(await until(()=>G&&G.pool&&G.pool.length>=4,8000)))return{error:'no pool'};
await sleep(750);
if(!S.pendingMatch)return{error:'no pendingMatch'};

/* ---- ARM A: the reorder ------------------------------------------------ */
G.matchDice=['bone','iron','flint','lead','amber','brass'];
G._enchArr=[{t:'tithe',face:1},null,null,null,null,null];
G.matchOppDice=['bone','bone','bone','bone','bone','bone'];
G.numDice=6;
const mover=(G.pool||[]).filter(d=>d.lane===0)[0]||G.pool[0];
if(mover)mover.mat='bone';
G._fairTrade={lane:0,was:'flint',borrowed:'bone'};
G._tradeSwaps=[{lane:0,oLane:0,mine:'jade',theirs:'bone',myEn:null,cnt:1}];
try{_snapDiceOnly();}catch(e){}                    /* a clean baseline */
const baseline={md:(S.pendingMatch.matchDice||[]).slice(),
                ftLane:(S.pendingMatch._fairTrade||{}).lane,
                tsLane:((S.pendingMatch._tradeSwaps||[])[0]||{}).lane};

const meshes=(G.pool||[]).map((d,i)=>({chip:d.el,phys:{x:i*10,y:0},hx:undefined,tx:0,ty:0,match:true}));
if(meshes.length>=4){
  _vgDragState={die:meshes[0].chip,me:meshes[0],order:meshes.slice(),
    homes:meshes.map(m=>m.phys.x),target:meshes.map(m=>m.phys.x),
    from:0,to:3,raf:0,y0:0,onMove:function(){},info:{mount:null,mid:0,sz:1}};
  try{_commitVagabondDrag();}catch(e){return{error:'commit threw '+e.message};}
}
await sleep(500);
const A={
  moverLane:mover?mover.lane:null,
  liveMd:(G.matchDice||[]).slice(), snapMd:(S.pendingMatch.matchDice||[]).slice(),
  liveFtLane:(G._fairTrade||{}).lane, snapFtLane:(S.pendingMatch._fairTrade||{}).lane,
  liveTsLane:((G._tradeSwaps||[])[0]||{}).lane,
  snapTsLane:((S.pendingMatch._tradeSwaps||[])[0]||{}).lane,
  baselineMd:baseline.md
};
A.reorderHappened = A.liveMd.join(',')!==baseline.md.join(',');
A.snapshotFollowed = A.snapMd.join(',')===A.liveMd.join(',');
A.lanesFollowed = A.snapFtLane===A.liveFtLane && A.snapTsLane===A.liveTsLane;

/* ---- ARM B: the rival board, both directions -------------------------- */
S.pendingMatch.matchOppDice=['x','x','x','x','x','x'];
G.matchOppDice=['jade','bone','bone','bone','bone','bone'];
try{_snapDiceOnly();}catch(e){}                    /* reorder-style: must NOT write it */
const oppAfterPlain=(S.pendingMatch.matchOppDice||[]).slice();
try{_tradeSnap();}catch(e){}                       /* trade-style: MUST write it */
const oppAfterTrade=(S.pendingMatch.matchOppDice||[]).slice();
const B={oppAfterPlain:oppAfterPlain, oppAfterTrade:oppAfterTrade,
         plainLeftItAlone:oppAfterPlain.join(',')==='x,x,x,x,x,x',
         tradeWroteIt:oppAfterTrade.join(',')===G.matchOppDice.join(',')};

return {
  A_reorder:A, B_rivalBoard:B,
  verdict:
    !A.reorderHappened ? 'INCONCLUSIVE - the reorder did not change matchDice'
    : !A.snapshotFollowed ? 'FAIL - the reorder is still not persisted: snap '+A.snapMd+' vs live '+A.liveMd
    : !A.lanesFollowed ? 'FAIL - the lane carries did not reach the snapshot'
    : !B.plainLeftItAlone ? 'FAIL - a plain snapshot wrote the rival board, which it must not'
    : !B.tradeWroteIt ? 'FAIL - trade stopped persisting the rival board'
    : 'PASS - the reorder persists, the lanes travel, and only trade writes the rival board'
};
