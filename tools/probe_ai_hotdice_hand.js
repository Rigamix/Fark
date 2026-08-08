/* P525 - does the AI now price hot dice off the hand the rival will really get?

   Two parts, because the unit answer is worthless if the value it reads is
   never actually published on the live path.
     A  the helper's arithmetic, against constructed state
     B  G._oSnuffLane is genuinely set by a REAL snuffed rival turn - the thing
        the helper depends on. Prove the publish happens, do not assume it. */
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(f,ms)=>{const t=Date.now();while(Date.now()-t<ms){try{if(f())return true;}catch(e){}await sleep(50);}return false;};
if(typeof launchBossMatch!=='function')return{error:'globals missing'};
if(typeof _oHandAfterSweep!=='function')return{error:'_oHandAfterSweep is not global'};

_getS(); S.run=S.run||{}; S.run.tier=2;
S.run.dice=['bone','iron','flint','lead','amber','brass'];
S.run.cards=S.run.cards||[]; S.settings=S.settings||{}; S.settings.reducedMotion=true;
launchBossMatch();
if(!(await until(()=>typeof G!=='undefined'&&G&&G.rung,9000)))return{error:'no match'};
await sleep(700);

/* ---- A: the arithmetic ------------------------------------------------- */
const A=[];
function probe(mats,snuff,expect){
  G.matchOppDice=mats.slice();
  G._oSnuffLane=snuff;
  const got=_oHandAfterSweep();
  A.push({loadout:mats.length,snuffLane:snuff,expected:expect,got:got,ok:got===expect});
}
const SIX=['bone','iron','flint','lead','amber','jade'];
probe(SIX,-1,6);                    // no snuff
probe(SIX,2,5);                     // snuffed
probe(SIX,5,5);                     // snuffed on the last seat
probe(SIX,9,6);                     // out of range - must not subtract
probe(['bone','iron','flint'],1,2); // short loadout
probe(['bone'],0,1);                // floor

/* ---- B: is the value published on the real path? ----------------------- */
G.matchOppDice=SIX.slice();
G._oSnuffLane=undefined;
let observed=null, handDuring=null;
const tick=setInterval(function(){
  try{
    if(observed===null&&G&&typeof G._oSnuffLane==='number'&&G._oSnuffLane>=0){
      observed=G._oSnuffLane; handDuring=_oHandAfterSweep();
    }
  }catch(e){}
},60);
for(let t=0;t<3&&observed===null;t++){
  if(!G||G._endMatchFired)break;
  G._snuff={lane:3,live:true,turn:(G.oppTurnCount||0)+1};
  try{ runOppTurn(); }catch(e){ clearInterval(tick); return {error:'runOppTurn threw: '+e.message}; }
  await sleep(6000);
}
clearInterval(tick);

const arithOK=A.every(x=>x.ok);
return {
  arithmetic:A, allArithmeticOK:arithOK,
  publishedSnuffLane:observed, handWhilePublished:handDuring,
  publishWorks:observed===3&&handDuring===5,
  verdict:
    !arithOK ? 'FAIL - the helper computes the wrong hand'
    : observed===null ? 'INCONCLUSIVE - no snuff was ever published, so the live path is untested'
    : (observed!==3) ? 'FAIL - the published lane is not the snuffed one'
    : (handDuring!==5) ? 'FAIL - the hand was not reduced during a real snuffed turn'
    : 'PASS - arithmetic correct and the value is genuinely published on the live path'
};
