/* P539 - does a real resume rewind THIS turn's gold and only this turn's?

   This drives resumeMatch() rather than reasoning about the snapshot's
   contents. A field being present and correct is not the claim; the claim is
   that the player's purse is back where the turn started.

   THE CONTROL IS THE SECOND ARM, AND IT IS THE ONE THAT CAN FAIL. A fix that
   simply restored some remembered gold would pass "the payout was rewound" and
   still be wrong - it would also wipe gold earned EARLIER in the same match.
   So: earn 15 in turn one, start turn two (which re-stashes), earn 15 again,
   then resume. The right answer is +15, not +0 and not +30. Only a fix that
   rewinds to the CURRENT turn's start can land on the middle number, so this
   arm separates a correct fix from two different wrong ones. */
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(f,ms)=>{const t=Date.now();while(Date.now()-t<ms){try{if(f())return true;}catch(e){}await sleep(50);}return false;};
if(typeof launchBossMatch!=='function')return{error:'globals missing'};
if(typeof resumeMatch!=='function')return{error:'resumeMatch missing'};

_getS(); S.run=S.run||{}; S.run.tier=2; S.run.gold=500; S.run._hotdNext=true;
S.run.dice=['bone','iron','flint','lead','amber','brass'];
S.settings=S.settings||{}; S.settings.reducedMotion=true;
launchBossMatch();
if(!(await until(()=>typeof G!=='undefined'&&G&&G.rung,9000)))return{error:'no match'};
await sleep(700);
try{startPTurn();}catch(e){}
await sleep(300);
try{handleRoll();}catch(e){}
if(!(await until(()=>G&&G.pool&&G.pool.length>=3,8000)))return{error:'no pool'};
await sleep(700);
if(!S.pendingMatch)return{error:'no pendingMatch'};
if(!('runGoldAtTurnStart' in S.pendingMatch))
  return{error:'P539 not applied - the snapshot has no runGoldAtTurnStart'};

/* ---- turn one: earn, and keep it by crossing a turn boundary ----------- */
const startGold=S.run.gold;
const snapT1=S.pendingMatch.runGoldAtTurnStart;
let d=G.pool[0]; d.ench={t:'tithe',face:d.val};
try{_iconFire(d,'p');}catch(e){return{error:'fire threw '+e.message};}
const afterFire1=S.run.gold;

/* a new turn: the stash must move up to include what turn one earned */
try{startPTurn();}catch(e){}
await sleep(400);
try{handleRoll();}catch(e){}
await until(()=>G&&G.pool&&G.pool.length>=3,8000);
await sleep(600);
const snapT2=S.pendingMatch.runGoldAtTurnStart;

/* ---- turn two: earn again, consume the charge, then quit --------------- */
d=G.pool[0]; d.ench={t:'tithe',face:d.val};
try{_iconFire(d,'p');}catch(e){}
S.run._hotdNext=false; try{save();}catch(e){}   /* the bank block's own line */
const beforeResume=S.run.gold, hotdBefore=S.run._hotdNext;
const snapHotd=S.pendingMatch.runHotdAtTurnStart;

/* ---- the actual resume ------------------------------------------------- */
try{resumeMatch();}catch(e){return{error:'resumeMatch threw '+e.message};}
if(!(await until(()=>typeof G!=='undefined'&&G&&G.rung&&G._resumed!==undefined||true,3000)))
  {/* fall through - the wait below is the real one */}
await sleep(2500);
const afterResume=S.run.gold, hotdAfter=S.run._hotdNext;

const expected=snapT2;                    /* the START of the turn we quit in */
return {
  startGold, snapAtTurn1:snapT1, afterFire1, snapAtTurn2:snapT2,
  beforeResume, afterResume, expected,
  hotd:{armedAtStart:snapHotd, consumed:hotdBefore, afterResume:hotdAfter},
  verdict:
    afterFire1!==startGold+15 ? 'INCONCLUSIVE - tithe did not pay 15 in turn one'
    : snapT2!==afterFire1 ? 'FAIL - the second turn boundary did not re-stash: snap '+snapT2+' vs live '+afterFire1
    : beforeResume!==snapT2+15 ? 'INCONCLUSIVE - turn two did not pay 15'
    : afterResume===beforeResume ? 'FAIL - the resume did not rewind at all ('+afterResume+')'
    : afterResume===startGold ? 'FAIL - the resume rewound TOO FAR, wiping turn one’s earnings ('+afterResume+', want '+expected+')'
    : afterResume!==expected ? 'FAIL - rewound to '+afterResume+', want '+expected
    : hotdAfter!==true ? 'PARTIAL - gold is right but the Hair of the Dog charge was not restored ('+hotdAfter+')'
    : 'PASS - resume rewound this turn only: '+beforeResume+' -> '+afterResume+' (turn start), turn one’s +15 kept, and the spent charge is back'
};
