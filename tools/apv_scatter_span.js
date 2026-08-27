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
const ok=runs.filter(r=>r.leftFrac!==undefined);
const ixs=ok.map(r=>r.ix);
const lf=ok.map(r=>r.leftFrac);
const zf=ok.map(r=>r.zPosFrac);
const mean=a=>a.reduce((x,y)=>x+y,0)/a.length;
const sd=a=>{const m=mean(a);return Math.sqrt(mean(a.map(v=>(v-m)*(v-m))));};
return {samples:ok.length,
  impactX:{min:Math.min(...ixs),max:Math.max(...ixs),sd:+sd(ixs).toFixed(2)},
  leftFrac:{min:Math.min(...lf),max:Math.max(...lf),sd:+sd(lf).toFixed(3),mean:+mean(lf).toFixed(2)},
  depthSignVaries:{min:Math.min(...zf),max:Math.max(...zf),sd:+sd(zf).toFixed(3)},
  verdicts:{
    impactRoamsRow:Math.max(...ixs)>2.0&&Math.min(...ixs)<-2.0,
    partingBroken:sd(lf)>0.12,
    depthNotOneCoinFlip:sd(zf)>0.05||(Math.max(...zf)<1&&Math.min(...zf)>0)},
  verdict:Math.max(...ixs)>2.0&&Math.min(...ixs)<-2.0&&sd(lf)>0.12};
