/* P536 - does the Fair-Trade exit still overwrite the turn-boundary snapshot?

   _removeDieAt's main exit writes ONLY the dice fields, under a comment that
   forbids the full saveMatchState() and cites a measured exploit: a Break after
   a shatter bonus and a spent card moved the snapshot's pPts 0 -> 500 and
   recorded a card as used, so the resumed turn charged for a card use on a turn
   that never happened and re-banked points.

   Its Fair-Trade exit called saveMatchState() anyway.

   THE TEST IS THAT EXACT EXPLOIT, on the Fair-Trade path:
     put the boundary snapshot at pPts 0 (a turn that has banked nothing)
     earn points mid-turn so G.pPts is 500
     break the BORROWED die, which takes the Fair-Trade exit
     the snapshot must still say 0 - it describes the START of the turn

   AND THE OTHER HALF, or a fix that simply wrote nothing would pass: the dice
   fields MUST update, because the owner's die walking back into the lane is
   exactly what a resume needs to know.

   Both are asserted. Writing nothing is as wrong as writing everything. */
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(f,ms)=>{const t=Date.now();while(Date.now()-t<ms){try{if(f())return true;}catch(e){}await sleep(50);}return false;};
if(typeof launchBossMatch!=='function')return{error:'globals missing'};
if(typeof _removeDieAt!=='function')return{error:'_removeDieAt missing'};

_getS(); S.run=S.run||{}; S.run.tier=2;
S.run.dice=['bone','iron','flint','lead','amber','brass'];
S.settings=S.settings||{}; S.settings.reducedMotion=true;
launchBossMatch();
if(!(await until(()=>typeof G!=='undefined'&&G&&G.rung,9000)))return{error:'no match'};
await sleep(700);
try{startPTurn();}catch(e){}
await sleep(250);
try{handleRoll();}catch(e){}
if(!(await until(()=>G&&G.pool&&G.pool.length>=3,8000)))return{error:'no pool'};
await sleep(700);
if(!S.pendingMatch)return{error:'no pendingMatch - not a resumable match'};

/* the boundary snapshot as startPTurn would have left it */
G.matchDice=['bone','iron','obsidian','lead','amber','brass'];
G._enchArr=[null,null,null,null,null,null];
G.pPts=0;
try{saveMatchState();}catch(e){return{error:'baseline save threw '+e.message};}
const baseline={pPts:S.pendingMatch.pPts, md:(S.pendingMatch.matchDice||[]).slice()};

/* now the turn earns points and the loan is live */
G.pPts=500;
G._fairTrade={lane:2,was:'flint',borrowed:'obsidian'};
const dieInLoanLane=(G.pool||[]).filter(d=>d.lane===2)[0]||null;

/* break the BORROWED die - this is the Fair-Trade exit */
const ret=_removeDieAt(2);
await sleep(300);

const after={
  snapshotPPts:S.pendingMatch.pPts,
  livePPts:G.pPts,
  snapshotMd:(S.pendingMatch.matchDice||[]).slice(),
  liveMd:(G.matchDice||[]).slice(),
  snapshotFairTrade:S.pendingMatch._fairTrade,
  liveFairTrade:G._fairTrade,
  took_ft_exit: ret===true && G._fairTrade===null
};

const boundaryHeld = after.snapshotPPts===0 && after.livePPts===500;
const diceFollowed = after.snapshotMd.join(',')===after.liveMd.join(',')
                     && after.liveMd[2]==='flint';

return {
  baseline:baseline, after:after,
  boundarySnapshotHeldAt0:boundaryHeld,
  diceFieldsFollowed:diceFollowed,
  verdict:
    !after.took_ft_exit ? 'INCONCLUSIVE - the Fair-Trade exit was not taken'
    : !boundaryHeld ? 'FAIL - the snapshot took mid-turn points ('+after.snapshotPPts+'), the exploit is live'
    : !diceFollowed ? 'FAIL - the snapshot did not follow the dice: snap '+after.snapshotMd+' vs live '+after.liveMd
    : 'PASS - the boundary snapshot kept its pPts and the dice fields still updated'
};
