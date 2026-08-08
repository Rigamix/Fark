/* M3, taken seriously before the adversarial pass returns, as ruled.

   TWO SEPARATE QUESTIONS, which the nomination runs together:

   Q1. Does the player's reorder leave G._tradeSwaps stale? The reorder carries
       G._fairTrade (added in P530) and does NOT mention _tradeSwaps. P527 gave
       that ledger a player-side `lane` precisely so it could be maintained
       across seat changes - and then a reorder was never taught to maintain it.
       If so this is MINE: P520 made the reorder real, P527 built the ledger,
       P530 carried the loan and left the sibling behind.

   Q2. Does a reorder change which RIVAL seat a snuff/fog/snare hits?
       _lmArm('_snuff', c.lane, ...) stores _laneOf(d) - a PLAYER lane - and
       _snuffLane is then consumed against the rival's seats. The marker itself
       is not mutated by a reorder, so the question is whether the lane recorded
       AT COMMIT now depends on how the player arranged their dice. If it does,
       P520 did not create the conflation but it made it player-CONTROLLABLE,
       which is a design consequence rather than a straightforward defect. */
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

/* ---- Q1: a trade ledger entry on the seat we are about to move --------- */
const mover=(G.pool||[]).filter(d=>d.lane===0)[0]||G.pool[0];
const moverLaneBefore=mover.lane;
G._tradeSwaps=[{lane:moverLaneBefore,oLane:moverLaneBefore,mine:'jade',
                theirs:mover.mat,myEn:{t:'tithe',face:1},cnt:1}];
/* and a loan on the same seat, which P530 DOES carry - the control that proves
   the reorder is capable of maintaining a record at all */
G._fairTrade={lane:moverLaneBefore,was:'flint',borrowed:mover.mat};

/* ---- Q2: what lane would an icon report at commit time? ---------------- */
const laneAtCommitBefore = (typeof _laneOf==='function') ? _laneOf(mover) : null;

/* perform the reorder: move the first die to slot 3 */
const meshes=(G.pool||[]).map((d,i)=>({chip:d.el,phys:{x:i*10,y:0},hx:undefined,tx:0,ty:0,match:true}));
if(meshes.length>=4){
  _vgDragState={die:meshes[0].chip,me:meshes[0],order:meshes.slice(),
    homes:meshes.map(m=>m.phys.x),target:meshes.map(m=>m.phys.x),
    from:0,to:3,raf:0,y0:0,onMove:function(){},info:{mount:null,mid:0,sz:1}};
  try{_commitVagabondDrag();}catch(e){return{error:'commit threw: '+e.message};}
}
await sleep(400);

const moverLaneAfter=mover.lane;
const laneAtCommitAfter=(typeof _laneOf==='function')?_laneOf(mover):null;
const ledgerLane=(G._tradeSwaps&&G._tradeSwaps[0])?G._tradeSwaps[0].lane:null;
const ledgerOLane=(G._tradeSwaps&&G._tradeSwaps[0])?G._tradeSwaps[0].oLane:null;
const loanLane=(G._fairTrade||{}).lane;

return {
  moverLane:{before:moverLaneBefore, after:moverLaneAfter, moved:moverLaneBefore!==moverLaneAfter},

  Q1_tradeLedger:{
    laneRecorded:ledgerLane, oLaneRecorded:ledgerOLane,
    followedTheDie: ledgerLane===moverLaneAfter,
    STALE: ledgerLane===moverLaneBefore && moverLaneBefore!==moverLaneAfter},

  CONTROL_loan:{ laneRecorded:loanLane, followedTheDie: loanLane===moverLaneAfter },

  Q2_iconLaneAtCommit:{
    before:laneAtCommitBefore, after:laneAtCommitAfter,
    reorderChangesTheTarget: laneAtCommitBefore!==laneAtCommitAfter},

  verdict:
    !(moverLaneBefore!==moverLaneAfter) ? 'INCONCLUSIVE - the reorder did not move the die, nothing was tested'
    : (ledgerLane===moverLaneBefore)
        ? 'Q1 CONFIRMED - the reorder carries the loan but leaves the trade ledger stale'
    : (ledgerLane===moverLaneAfter)
        ? 'Q1 CLEAN - the trade ledger followed the die'
        : 'Q1 UNEXPECTED - ledger lane is neither the old nor the new seat'
};
