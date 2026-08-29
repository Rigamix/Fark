/* P867 - night 8 pays, and Ambrose keeps his tiles.
 *
 * The branch this replaces gated on G.rung.key==='ambrose' against a rung key
 * of 'bishop', so it had never fired. "It pays now" therefore has to be shown
 * against a BEFORE, not asserted from the code - and the before is a renown
 * total that does not move, which is also what a broken probe produces. So
 * the run is done twice over: Ambrose (must pay, once) and a non-Ambrose boss
 * (must NOT pay, but must still take a trophy). Neither leg means anything
 * without the other.
 */
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(fn,ms)=>{const t0=Date.now();while(Date.now()-t0<ms){try{if(fn())return true;}catch(e){}await sleep(120);}return false;};
if(!await until(()=>typeof launchBossMatch==='function',20000))return {err:'no boot'};
_getS();window._fkDiscardOk=true;
const out={};

async function beat(tier,label){
  S.run.tier=tier;S.run.gold=500;
  try{delete S.pendingMatch;}catch(e){}
  try{showScreen('gauntlet');}catch(e){}
  launchBossMatch();
  if(!await until(()=>typeof G!=='undefined'&&G&&G.phase==='idle',15000))return {label,err:'no match'};
  await sleep(1600);
  const boss=G.rung&&G.rung.name, key=G.rung&&G.rung.key;
  const renownBefore=S.renown||0, trophiesBefore=(S.trophies||[]).slice();
  G.pPts=G.target;G.oPts=0;
  endMatch(true);
  const reached=await until(()=>{const rc=document.querySelector('#end-ov .res-card');
    return rc&&/TAKE ONE/.test(rc.textContent);},20000);
  await sleep(900);
  const rc=document.querySelector('#end-ov .res-card');
  const txt=rc?(rc.innerText||rc.textContent||'').replace(/\s+/g,' ').trim():'';
  const tiles=rc?rc.querySelectorAll('[onclick*="_gbSpoilsConfirm"]').length:0;
  return {label,boss,rungKey:key,
    reachedSpoils:reached,tileCount:tiles,
    headerShown:/THE HOUSE REMEMBERS YOUR NAME/.test(txt),
    headerAboveTiles: txt.indexOf('THE HOUSE REMEMBERS')>=0
      ? txt.indexOf('THE HOUSE REMEMBERS')<txt.indexOf('SPOILS') : null,
    renownBefore,renownAfter:S.renown||0,renownDelta:(S.renown||0)-renownBefore,
    trophyGained:(S.trophies||[]).filter(t=>trophiesBefore.indexOf(t)<0),
    n8Paid:!!(S.run&&S.run._n8Paid)};
}

/* warm-up: the first match after a cold boot is jittery reaching the spoils DOM */
try{S.run.tier=0;launchBossMatch();await until(()=>G&&G.phase==='idle',15000);await sleep(2200);}catch(e){}

out.ambrose      = await beat(7,'ambrose-first-win');
out.ambroseAgain = await beat(7,'ambrose-second-win');   /* must NOT pay twice */
out.brutus       = await beat(4,'brutus-control');       /* must NOT pay renown */

/* a FRESH run must pay again - _n8Paid is run-scoped, not account-scoped */
try{
  S.run._n8Paid=false;
  out.freshRun = await beat(7,'ambrose-after-run-reset');
}catch(e){out.freshRun={err:String(e).slice(0,90)};}

out.VERDICT={
  /* NOT ===150 on the first win. A boss win pays other renown too (feats
     claimed on the same win), and the measured first-win delta is 255 - so an
     exact-equality assert here fails on a CORRECT payout and would have sent
     me to change working code. The +150 is isolated instead by the pair below:
     with the latch already set the delta is 0, and with the latch cleared it
     is exactly 150. That difference is the night-8 payout and nothing else. */
  ambroseFirstWinPaysAtLeast150: out.ambrose.renownDelta>=150,
  ambroseLatchSet:               out.ambrose.n8Paid===true,
  ambroseGotHisTrophy:       out.ambrose.trophyGained.indexOf('ambrose_weight')>=0,
  ambroseKeptHisThreeTiles:  out.ambrose.tileCount===3,
  hisLineIsAHeaderNotAScreen:out.ambrose.headerShown===true&&out.ambrose.headerAboveTiles===true,
  paysOncePerRun:            out.ambroseAgain.renownDelta===0,
  controlBossPaysNoRenown:   out.brutus.renownDelta===0,
  controlBossStillTakesATrophy: out.brutus.trophyGained.length===1,
  controlBossHasNoHeader:    out.brutus.headerShown===false,
  runScopedNotAccountScoped: out.freshRun&&out.freshRun.renownDelta===150,
};
out.PASS=Object.keys(out.VERDICT).every(k=>out.VERDICT[k]===true);
return out;
