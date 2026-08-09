/* P535 - does a bust get judged against the table as it IS?

   The arrangement that separates the two answers: make the CAPTURED pool score
   and the LIVE pool not, by removing the only scoring die during the window.

     stale capture  -> sees the removed die, declares no bust, turn continues
                       over a table with nothing playable
     re-derived     -> sees the live table, busts (or offers a bust save)

   ARM A  Powder Keg: capture, 500ms timer, no phase guard - removers legal.
   ARM B  Steady Hand: capture at USE, judged when the player taps. Unbounded.
   ARM C  control: same cards, nothing removed. Behaviour must be unchanged, or
          a "fix" that simply busts more often would pass A and B.

   Bust is detected by watching G.phase and the kept tray rather than by
   trusting a return value - _delayedDoBust runs on its own timer. */
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(f,ms)=>{const t=Date.now();while(Date.now()-t<ms){try{if(f())return true;}catch(e){}await sleep(50);}return false;};
if(typeof launchBossMatch!=='function')return{error:'globals missing'};
if(!(window.CFX&&CFX.powder_keg&&CFX.steady_hand))return{error:'cards missing'};

async function fresh(){
  _getS(); S.run=S.run||{}; S.run.tier=2;
  S.run.dice=['bone','iron','flint','lead','amber','brass'];
  S.settings=S.settings||{}; S.settings.reducedMotion=true;
  launchBossMatch();
  if(!(await until(()=>typeof G!=='undefined'&&G&&G.rung,9000)))return false;
  await sleep(650);
  try{startPTurn();}catch(e){}
  await sleep(200);
  try{handleRoll();}catch(e){}
  if(!(await until(()=>G&&G.pool&&G.pool.length>=4,8000)))return false;
  await sleep(700);
  return G.pool.length>=4;
}

/* ONE scorer and junk that does NOT score on its own. The first version used
   five 3s as the junk - which is a TRIPLE, worth 300, so the table still had a
   legal keep and not busting was correct. The probe was wrong, not the fix.
   [2,3,4,2,3] is the classic dead hand: no 1, no 5, no three of a kind. */
const JUNK=[2,3,4,2,3];
function seedOneScorer(){
  G.pool.forEach(function(d,i){d.committed=false;d.sel=false;d._frozen=false;d.ench=null;
    d.val=(i===0)?1:JUNK[(i-1)%JUNK.length];});
  try{G.pool.forEach(function(d){reDrawDieFace(d);});}catch(e){}
  return G.pool[0];
}
/* prove the arrangement really is dead before drawing any conclusion from it */
function tableScores(){
  const f=(G.pool||[]).filter(function(d){return !d.committed;});
  try{return anyScoring(f.map(function(d){return d.val;}),effectiveCards(),
                        f.map(function(d){return d.mat;}),f);}catch(e){return null;}
}

async function armKeg(removeIt){
  if(!(await fresh()))return{skip:'no pool'};
  const scorer=seedOneScorer();
  G.phase='choosing';
  /* the keg rerolls everything, so force its result: freeze the faces after
     its reroll by re-seeding inside the window, then optionally remove */
  let removed=false;
  try{CFX.powder_keg.use({tier:1});}catch(e){return{skip:'keg threw '+e.message};}
  /* inside the 500ms window: make the table one-scorer, then take the scorer */
  await sleep(120);
  G.pool.forEach(function(d,i){d.val=(i===0)?1:JUNK[(i-1)%JUNK.length];});
  try{G.pool.forEach(function(d){reDrawDieFace(d);});}catch(e){}
  const liveBefore=G.pool.map(d=>d.val);
  if(removeIt&&G.pool.length){
    const L=G.pool[0].lane;
    if(typeof L==='number')_removeDieAt(L);
    removed=!G.pool.some(d=>d.val===1);
  }
  const liveAfter=G.pool.map(d=>d.val);
  const deadNow=(tableScores()===false);
  await sleep(1200);
  return {liveBefore:liveBefore, liveAfter:liveAfter, scorerRemoved:removed,
          tableGenuinelyDead:deadNow,
          phase:G.phase, poolLen:G.pool.length,
          busted:(G.phase==='idle'||G.phase==='opp')||G.pool.length===0};
}

async function armSteady(removeIt){
  if(!(await fresh()))return{skip:'no pool'};
  seedOneScorer();
  G.phase='choosing';
  try{CFX.steady_hand.use({tier:1});}catch(e){return{skip:'steady threw '+e.message};}
  await sleep(150);
  /* the card rebinds each die's onclick; removing a die now makes the captured
     list stale before the player ever taps */
  let removed=false;
  if(removeIt&&G.pool.length){
    const one=G.pool.filter(d=>d.val===1)[0];
    if(one&&typeof one.lane==='number'){_removeDieAt(one.lane);removed=!G.pool.some(d=>d.val===1);}
  }
  const liveAtTap=G.pool.map(d=>d.val);
  const deadNow=(tableScores()===false);
  /* the tap: fire the handler the card installed on a surviving die */
  const tapTarget=G.pool.filter(d=>!d.committed)[0];
  if(tapTarget&&tapTarget.el&&tapTarget.el.onclick){try{tapTarget.el.onclick();}catch(e){}}
  await sleep(1100);
  return {liveAtTap:liveAtTap, scorerRemoved:removed, tableGenuinelyDead:deadNow, phase:G.phase,
          poolLen:G.pool.length,
          busted:(G.phase==='idle'||G.phase==='opp')||G.pool.length===0};
}

const KEG_REMOVED = await armKeg(true);   await sleep(400);
const KEG_CONTROL = await armKeg(false);  await sleep(400);
const STEADY_REMOVED = await armSteady(true);

const ok = x => x && !x.skip;
return {
  A_keg_scorerRemoved:KEG_REMOVED,
  C_keg_control:KEG_CONTROL,
  B_steady_scorerRemoved:STEADY_REMOVED,
  verdict:
    !ok(KEG_REMOVED) ? 'INCONCLUSIVE - keg arm: '+(KEG_REMOVED&&KEG_REMOVED.skip)
    : !KEG_REMOVED.scorerRemoved ? 'INCONCLUSIVE - the scorer was never actually removed'
    : !KEG_REMOVED.tableGenuinelyDead ? 'INCONCLUSIVE - the junk still scores, so not busting is correct'
    : !KEG_REMOVED.busted ? 'FAIL - the keg still judged against the stale capture'
    : (ok(KEG_CONTROL)&&KEG_CONTROL.busted) ? 'SUSPECT - the control busted too; the fix may just bust more'
    : (ok(STEADY_REMOVED)&&STEADY_REMOVED.scorerRemoved&&!STEADY_REMOVED.busted)
        ? 'PARTIAL - keg fixed, Steady Hand still judged a removed die'
    : 'PASS - the bust is judged against the live table, and the control is unchanged'
};
