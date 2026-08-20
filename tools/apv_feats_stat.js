/* P840: the game-over FEATS stat counts REAL feats. Win a match with
 * the two migrated conditions armed plus normal play - evaluateFeats
 * must award them as roster rows, and _featsThisRun (the stat the
 * game-over screen reads) must equal the earned count, not the old
 * side-channel's 0-2. */
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(fn,ms)=>{const t0=Date.now();while(Date.now()-t0<ms){try{if(fn())return true;}catch(e){}await sleep(120);}return false;};
const tap=el=>{if(!el)return false;const r=el.getBoundingClientRect();
  const o={bubbles:true,cancelable:true,clientX:r.left+r.width/2,clientY:r.top+r.height/2};
  el.dispatchEvent(new PointerEvent('pointerdown',o));
  el.dispatchEvent(new PointerEvent('pointerup',o));
  el.dispatchEvent(new MouseEvent('click',o));return true;};
if(!await until(()=>typeof launchSeat==='function'&&typeof S!=='undefined',20000))return {err:'no boot'};
if(typeof _getS==='function')_getS();
const rosterHasBoth=FEATS.some(f=>f.id==='own_reckoning')&&FEATS.some(f=>f.id==='keg_triple');
launchSeat(0);
if(!await until(()=>typeof G!=='undefined'&&G&&G.phase==='idle',14000))return {err:'no match'};
await sleep(3000);
G._sleeve='reckoning';
G._famKegTriple=true;
S.run._featsThisRun=0;S.run.feats={};
const ren0=S.renown||0;
/* win: preset near target, bank a triple */
G.pPts=(G.target||2800)-900;try{updHUD();}catch(e){}
const Q=[1,1,1,2,3,4];
const realE=window._enchRollM;
window._enchRollM=(m,e)=>Q.length?Q.shift():realE(m,e);
tap(document.getElementById('btnRoll'));
if(!await until(()=>G.phase==='choosing',15000))return {err:'no roll'};
await sleep(600);
const ones=G.pool.filter(d=>!d.committed&&d.val===1);
tap(ones[0].el);await sleep(120);tap(ones[1].el);await sleep(120);tap(ones[2].el);await sleep(300);
const flagAtBank=G._famKegTriple;
tap(document.getElementById('btnBank'));
if(!await until(()=>G._endMatchFired,20000))return {err:'no win',flagAtBank};
const flagAfterWin=G._famKegTriple;
await sleep(1500);
const feats=Object.keys(S.run.feats||{});
const stat=S.run._featsThisRun||0;
const renGain=(S.renown||0)-ren0;
return {rosterHasBoth,feats,stat,renGain,flagAtBank,flagAfterWin,
  verdicts:{
    bothRowsInRoster:rosterHasBoth,
    bothAwarded:feats.indexOf('own_reckoning')>=0&&feats.indexOf('keg_triple')>=0,
    statCountsThem:stat===feats.length&&stat>=2,
    renownPaid:renGain>=50},
  verdict:rosterHasBoth&&feats.indexOf('own_reckoning')>=0&&feats.indexOf('keg_triple')>=0
    &&stat===feats.length&&stat>=2&&renGain>=50};
