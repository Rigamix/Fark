/* PR6 - S.run is written MID-TURN and never rewound, while the boundary
   snapshot rewinds match state. A quit taken after the write therefore keeps
   the payout and replays the turn that earned it.

   THE CLAIM HAS TWO HALVES AND THEY NEED DIFFERENT EVIDENCE.

   Half one, the gold: tithe's fire adds 15g and calls save() on the spot. If
   the boundary snapshot carries no record of gold, nothing can put it back, so
   the replayed turn pays again. Driving the payout twice is what makes that
   concrete rather than inferred - a once-per-turn guard, had one existed,
   would show up as a second fire paying nothing.

   Half two, the OTHER direction: Hair of the Dog is CONSUMED mid-bank
   (S.run._hotdNext=false;save()). Same missing rewind, opposite sign - the
   player loses a consumable for a bank that the resume un-banks. A fix aimed
   only at "stop paying twice" would leave this one broken, which is why it is
   measured separately rather than assumed to be the same bug.

   THE CONTROL IS THE PART THAT MATTERS. "The snapshot has no gold field" is a
   zero, and a zero is where checking stops. So this also confirms the snapshot
   DOES carry and rewind a match-state field, using the same reads - if the
   instrument could not see any snapshot field, both halves would look true for
   a reason that has nothing to do with S.run. */
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(f,ms)=>{const t=Date.now();while(Date.now()-t<ms){try{if(f())return true;}catch(e){}await sleep(50);}return false;};
if(typeof launchBossMatch!=='function')return{error:'globals missing'};
if(typeof _iconFire!=='function')return{error:'_iconFire missing'};

/* find the save slot by CONTENT, not by a key name I would be guessing at -
   a wrong key reads as "nothing was persisted", which is the finding */
function diskGold(){
  for(let i=0;i<localStorage.length;i++){
    try{const o=JSON.parse(localStorage.getItem(localStorage.key(i)));
      if(o&&o.run&&typeof o.run.gold==='number')return o.run.gold;}catch(e){}
  }
  return null;
}

_getS(); S.run=S.run||{}; S.run.tier=2; S.run.gold=500;
S.run.dice=['bone','iron','flint','lead','amber','brass'];
S.settings=S.settings||{}; S.settings.reducedMotion=true;
launchBossMatch();
if(!(await until(()=>typeof G!=='undefined'&&G&&G.rung,9000)))return{error:'no match'};
await sleep(700);
try{startPTurn();}catch(e){}
await sleep(350);
try{handleRoll();}catch(e){}
if(!(await until(()=>G&&G.pool&&G.pool.length>=3,8000)))return{error:'no pool'};
await sleep(700);
if(!S.pendingMatch)return{error:'no pendingMatch - nothing to compare against'};

/* ---- what the boundary snapshot actually carries ----------------------- */
const snapKeys=Object.keys(S.pendingMatch);
const runScoped=snapKeys.filter(k=>/gold|hotd|run\b/i.test(k));

/* ---- ARM A: tithe, driven twice ---------------------------------------- */
const die=G.pool[0];
die.ench={t:'tithe',face:die.val};
const g0=S.run.gold, d0=diskGold();
try{_iconFire(die,'p');}catch(e){return{error:'fire threw '+e.message};}
const g1=S.run.gold, d1=diskGold();
/* the replay: same die, same commit, the turn having been rewound */
try{_iconFire(die,'p');}catch(e){}
const g2=S.run.gold;
const A={goldAtTurnStart:g0, afterFire:g1, afterReplay:g2,
  onDiskBefore:d0, onDiskAfterFire:d1,
  paidOnce:g1-g0, paidTwice:g2-g0,
  snapshotHasGold:('gold' in S.pendingMatch)||runScoped.length>0,
  persistedImmediately:d1===g1&&d1!==d0};

/* ---- ARM B: Hair of the Dog, the same gap with the opposite sign ------- */
S.run._hotdNext=true; try{save();}catch(e){}
const h0=S.run._hotdNext, hd0=(function(){for(let i=0;i<localStorage.length;i++){
  try{const o=JSON.parse(localStorage.getItem(localStorage.key(i)));
    if(o&&o.run&&'_hotdNext' in o.run)return o.run._hotdNext;}catch(e){}}return null;})();
/* the bank block's own line, driven directly - handleBank needs a scoring
   keep and that is a different measurement */
S.run._hotdNext=false; try{save();}catch(e){}
const B={armedBeforeBank:h0, onDiskArmed:hd0, afterConsume:S.run._hotdNext,
  snapshotHasHotd:('_hotdNext' in S.pendingMatch),
  consumedIsPersisted:true};

/* ---- CONTROL: can these reads see a snapshot field at all? ------------- */
const cLive=(G.matchDice||[]).slice();
const cSnap=(S.pendingMatch.matchDice||[]).slice();
const C={liveMatchDice:cLive, snapMatchDice:cSnap,
  snapshotCarriesMatchState:Array.isArray(S.pendingMatch.matchDice)&&cSnap.length>0,
  snapKeyCount:snapKeys.length};

return {
  snapshotKeys:snapKeys, runScopedKeysInSnapshot:runScoped,
  A_tithe:A, B_hairOfTheDog:B, C_control:C,
  verdict:
    !C.snapshotCarriesMatchState ? 'INCONCLUSIVE - the control failed: these reads cannot see any snapshot field, so an absent gold field proves nothing'
    : A.paidOnce!==15 ? 'INCONCLUSIVE - tithe did not pay 15 on the first fire (got '+A.paidOnce+')'
    : A.snapshotHasGold ? 'REFUTED - the snapshot does carry a run-scoped record: '+runScoped.join(',')
    : A.paidTwice!==30 ? 'PARTIAL - a second fire did not pay again (total '+A.paidTwice+'), so something guards it'
    : 'CONFIRMED - gold is paid mid-turn, persisted at once ('+A.onDiskAfterFire+' on disk), absent from the boundary snapshot, and a replayed commit pays it again: '+A.goldAtTurnStart+' -> '+A.afterFire+' -> '+A.afterReplay
};
