/* P858: the impact roams the row, depth varies per die, and the P733
 * two-lobe parting must NOT come back. Drives scatterRow directly over
 * many synthetic busts with a realistic settled row (all dice sharing
 * one z, as the solver pins them). Reports:
 *  - impact x spread (was confined to +-0.8)
 *  - per-die kick direction spread in DEPTH (was one sign for the row)
 *  - the parting test: fraction of dice pushed left, per bust. A
 *    centre blast pins this at ~0.5 every time; a roaming impact makes
 *    it vary across the full range. Low variance = the disease. */
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(fn,ms)=>{const t0=Date.now();while(Date.now()-t0<ms){try{if(fn())return true;}catch(e){}await sleep(100);}return false;};
if(!await until(()=>typeof launchSeat==='function',20000))return {err:'no boot'};
if(typeof _getS==='function')_getS();
window._fkDiscardOk=true;
try{delete S.pendingMatch;}catch(e){}
try{if(S.run&&S.run.night){S.run.night.seatsPlayed=S.run.night.roster.map(()=>false);S.run.night.results=S.run.night.roster.map(()=>null);}}catch(e){}
launchSeat(0);
if(!await until(()=>typeof G!=='undefined'&&G&&G.phase==='idle',15000))return {err:'no match'};
await sleep(3000);
/* the 3D layer must be live or scatterRow early-returns 0 */
if(!await until(()=>D3X&&D3X.ready&&!D3X.fail&&D3X.PHYS&&D3X.PHYS.on,15000))
  return {err:'D3X not ready',ready:!!(D3X&&D3X.ready),fail:!!(D3X&&D3X.fail),phys:!!(D3X&&D3X.PHYS&&D3X.PHYS.on)};
/* synthetic row: 6 dice on a line, shared z, like a real settled row */
const LANES=[-4.0,-2.4,-0.8,0.8,2.4,4.0];
const mkRow=()=>LANES.map((x,i)=>({match:true,phys:{x,z:0.6},chip:{closest:()=>true},
  burst:null,kick:null,_i:i}));
const runs=[];
for(let r=0;r<40;r++){
  const row=mkRow();
  const savedDice=D3X.dice;
  D3X.dice=row;
  let n=0;try{n=D3X.scatterRow('#playerDiceRow');}catch(e){runs.push({err:String(e)});D3X.dice=savedDice;continue;}
  const imp=D3X._lastImpact||{};
  const kicks=row.map(d=>d.kick?{x:+d.kick.vx.toFixed(3),z:+d.kick.vz.toFixed(3),lane:d.phys.x}:null).filter(Boolean);
  D3X.dice=savedDice;
  if(!kicks.length){runs.push({n,none:true});continue;}
  const left=kicks.filter(k=>k.x<0).length;
  const zPos=kicks.filter(k=>k.z>0).length;
  runs.push({n,ix:+(imp.x||0).toFixed(2),leftFrac:+(left/kicks.length).toFixed(2),
    zPosFrac:+(zPos/kicks.length).toFixed(2)});
}
/* P858b (review): THE SYMPTOM LEG. Every assertion above measures ix/iz/
   _pz - the inputs P858 changed - so none of them can fail for the reason
   the probe exists. P733's parting was about FINAL POSITIONS ("two stacks
   left and right"), so measure those: sort each bust's end positions,
   take the largest ADJACENT gap over the mean adjacent gap. A parting is
   one oversized gap with the dice bunched either side; a healthy scatter
   has gaps of comparable size. This leg fails when the SYMPTOM returns,
   whatever mechanism caused it.
   The threshold is calibrated, not guessed: the same maths is run with
   P858's parameters reverted (impact pinned to +-0.8, one shared depth)
   to measure what a parting actually scores. */
const gapRatio=finals=>{
  const f=finals.slice().sort((a,b)=>a-b);
  const gaps=[];for(let i=1;i<f.length;i++)gaps.push(f[i]-f[i-1]);
  if(!gaps.length)return null;
  const mean=gaps.reduce((a,b)=>a+b,0)/gaps.length;
  return mean>0?+(Math.max(...gaps)/mean).toFixed(2):null;
};
/* live build: end position is phys.x + the kick's x displacement, the
   same endX the clamp computes three lines below the code P858 touched */
const liveRatios=[];
for(let r=0;r<40;r++){
  const row=mkRow();const saved=D3X.dice;D3X.dice=row;
  try{D3X.scatterRow('#playerDiceRow');}catch(e){}
  D3X.dice=saved;
  const finals=row.filter(d=>d.kick).map(d=>d.phys.x+d.kick.vx);
  if(finals.length===LANES.length){const g=gapRatio(finals);if(g)liveRatios.push(g);}
}
/* CONTROL = THE DISEASE, not the previous build. An earlier draft of
   this leg calibrated against pre-P858 parameters, which was wrong:
   that code already contains P799's fix, so it measured P858 improving
   on a healthy build by 11% and proved nothing about parting. The real
   control is P733's mechanism - direction taken from sign(phys.x), so
   every die left of centre goes left and every die right goes right,
   which is what produced "two stacks left and right". */
const partedRatios=[];
for(let r=0;r<40;r++){
  const finals=LANES.map(x=>{
    const ang=(x<0?Math.PI:0)+(Math.random()-0.5)*0.73;/* P733: sign(phys.x) + 42deg jitter */
    const mag=1.15*(0.55+Math.random()*0.35)*1.4;
    return x+Math.cos(ang)*mag;
  });
  const g=gapRatio(finals);if(g)partedRatios.push(g);
}
const mn=a=>a.reduce((x,y)=>x+y,0)/a.length;
const liveMean=+mn(liveRatios).toFixed(2),partedMean=+mn(partedRatios).toFixed(2);
const liveMax=Math.max(...liveRatios),partedMax=Math.max(...partedRatios);

const ok=runs.filter(r=>r.leftFrac!==undefined);
const ixs=ok.map(r=>r.ix);
const lf=ok.map(r=>r.leftFrac);
const zf=ok.map(r=>r.zPosFrac);
const mean=a=>a.reduce((x,y)=>x+y,0)/a.length;
const sd=a=>{const m=mean(a);return Math.sqrt(mean(a.map(v=>(v-m)*(v-m))));};
return {samples:ok.length,
  parting:{liveMean,liveMax,partedMean,partedMax,
    liveRatios:liveRatios.slice(0,8),partedRatios:partedRatios.slice(0,8)},
  impactX:{min:Math.min(...ixs),max:Math.max(...ixs),sd:+sd(ixs).toFixed(2)},
  leftFrac:{min:Math.min(...lf),max:Math.max(...lf),sd:+sd(lf).toFixed(3),mean:+mean(lf).toFixed(2)},
  depthSignVaries:{min:Math.min(...zf),max:Math.max(...zf),sd:+sd(zf).toFixed(3)},
  verdicts:{
    impactRoamsRow:Math.max(...ixs)>2.0&&Math.min(...ixs)<-2.0,
    partingBroken:sd(lf)>0.12,
    depthNotOneCoinFlip:sd(zf)>0.05||(Math.max(...zf)<1&&Math.min(...zf)>0),
    /* the symptom leg: the live build must sit clearly below what the
       pre-P858 parameters score through the same maths */
    noPartingInFinalPositions:liveMean<partedMean*0.85},
  verdict:Math.max(...ixs)>2.0&&Math.min(...ixs)<-2.0&&sd(lf)>0.12
    &&liveMean<partedMean*0.85};
