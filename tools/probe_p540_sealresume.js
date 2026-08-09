/* P540 - does the sealed seat survive a force-close and resume?

   G._sealRule was in no snapshot field and resumeMatch never passed it, so
   `G._sealRule=params.sealRule||null` landed null on every resume. That is not
   only scoring: _ruleActive is `if(G._sealRule===id)return true;`, so the
   seat's RULE went with it, and pointsEarned then collapsed 3 -> 1 because
   isHandicap is `!!G._handicap||!!G._sealRule`.

   THE VALUE MUST ROUND-TRIP, NOT JUST THE TRUTHINESS. _ruleActive compares
   G._sealRule === id, so a snapshot that stored `true` instead of 'steeped'
   would restore something truthy, satisfy a naive check, and still leave every
   rule comparison false. So this asserts the exact string, and then asks
   _ruleActive itself rather than trusting the field.

   CONTROL, both directions: an UNSEALED match must come back null. A fix that
   restored some default would pass the sealed arm and silently seal every
   ordinary seat, which is the more damaging failure of the two. */
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(f,ms)=>{const t=Date.now();while(Date.now()-t<ms){try{if(f())return true;}catch(e){}await sleep(50);}return false;};
if(typeof launchBossMatch!=='function')return{error:'globals missing'};
if(typeof resumeMatch!=='function')return{error:'resumeMatch missing'};
if(typeof _ruleActive!=='function')return{error:'_ruleActive missing'};

async function run(seal){
  _getS(); S.run=S.run||{}; S.run.tier=2; S.run.gold=300;
  S.run.dice=['bone','iron','flint','lead','amber','brass'];
  S.settings=S.settings||{}; S.settings.reducedMotion=true;
  delete S.pendingMatch;
  launchBossMatch();
  if(!(await until(()=>typeof G!=='undefined'&&G&&G.rung,9000)))return{error:'no match'};
  await sleep(650);
  G._sealRule=seal;                      /* as launchSeat would have set it */
  try{startPTurn();}catch(e){}           /* the boundary snapshot happens here */
  await sleep(500);
  if(!S.pendingMatch)return{error:'no pendingMatch'};
  const inSnap=S.pendingMatch.sealRule;
  const liveBefore=G._sealRule;
  const ruleBefore=seal?_ruleActive(seal,'p'):null;
  try{resumeMatch();}catch(e){return{error:'resumeMatch threw '+e.message};}
  await sleep(2600);
  return {inSnapshot:inSnap, liveBefore:liveBefore, liveAfter:G._sealRule,
          ruleActiveBefore:ruleBefore,
          ruleActiveAfter:seal?_ruleActive(seal,'p'):null,
          isHandicapAfter:!!G._handicap||!!G._sealRule};
}

const sealed=await run('steeped');
if(sealed.error)return{error:'sealed arm: '+sealed.error};
const plain=await run(null);
if(plain.error)return{error:'control arm: '+plain.error};

return {
  sealed, plain,
  verdict:
    sealed.inSnapshot!=='steeped' ? 'FAIL - the snapshot did not carry the seal (got '+JSON.stringify(sealed.inSnapshot)+')'
    : sealed.liveAfter!=='steeped' ? 'FAIL - the resume lost the seal: '+JSON.stringify(sealed.liveAfter)
    : sealed.ruleActiveAfter!==true ? 'FAIL - the field came back but _ruleActive is still false, so the rule is dead'
    : sealed.isHandicapAfter!==true ? 'FAIL - isHandicap is false after resume, so pointsEarned still collapses'
    : plain.liveAfter!==null ? 'FAIL - an UNSEALED match resumed sealed ('+JSON.stringify(plain.liveAfter)+') - worse than the bug'
    : 'PASS - the seal round-trips as its exact id, _ruleActive agrees, isHandicap holds, and an unsealed seat stays unsealed'
};
