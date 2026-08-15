/* SUITE: exclude. THE SEEDED A/B for P736. Same throws, fix on and off.
 * No new code needed to toggle: creepFrames huge disables the rest snap,
 * laneRadius 0 disables the in-lane release - both are the shipped
 * constants, so ARM B is exactly the old behaviour. */
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(fn,ms)=>{const t0=Date.now();while(Date.now()-t0<ms){try{if(fn())return true;}catch(e){}await sleep(80);}return false;};
const out={};
await setup();
if(!await until(()=>{const g=E('G');return g&&g.phase;},4000))return {err:'no match'};
gw();
/* a deterministic Math.random inside the FRAME, so both arms solve the
   identical throw (same values, same impulses, same everything) */
W.__seed=function(s){
  var x=s>>>0;
  W.Math.random=function(){
    x^=x<<13;x>>>=0;x^=x>>17;x^=x<<5;x>>>=0;return (x>>>0)/4294967296;
  };
};
W.__unseed=(function(orig){return function(){W.Math.random=orig;};})(W.Math.random);

/* per-die crawl: frames where THIS die moved in the creep band - the
   visible slow drag - plus its own last-moving frame */
const measure=()=>{
  const dx=E('window.D3X');
  let ds=dx.dice.filter(d=>d.match&&d.roll&&d.roll.sol&&d.roll.sol.frames);
  if(!ds.length)return null;
  const sol=ds[0].roll.sol;
  ds=ds.filter(d=>d.roll.sol===sol&&sol.frames[0][d.roll.i]);
  const fr=sol.frames,dtms=E('D3X.PHYS.dt')*1000;
  const per=ds.map(d=>{
    const i=d.roll.i;let crawl=0,lastMove=0;
    for(let f=1;f<fr.length;f++){
      const a=fr[f-1][i],b=fr[f][i];
      const dv=Math.abs(b.x-a.x)+Math.abs(b.y-a.y)+Math.abs(b.z-a.z);
      if(dv>0.004)lastMove=f;
      if(dv>0.004&&dv<=0.05)crawl++;
    }
    return {crawl,dragMs:Math.round(crawl*dtms)};
  });
  return {frames:fr.length,tapeMs:Math.round(fr.length*dtms),
    totalDragMs:per.reduce((a,p)=>a+p.dragMs,0),
    worstDragMs:Math.max(...per.map(p=>p.dragMs))};
};

const arm=async(label,on,seeds)=>{
  /* ARM B restores the pre-P736 behaviour through the shipped dials */
  E('D3X.PHYS.creepFrames='+(on?6:1e9));
  E('D3X.PHYS.laneRadius='+(on?0.54:0));
  const rows=[];
  for(const sd of seeds){
    E('G.kept=[];G.pool.forEach(function(d){d.committed=false;d.sel=false;d._frozen=false;});G.phase="choosing";');
    W.__seed(sd);
    E('handleRoll()');
    const started=await until(()=>E('window.D3X').dice.some(d=>d.match&&d.roll),12000);
    W.__unseed();
    if(!started)continue;
    await sleep(150);
    const m=measure();if(m)rows.push(m);
    await until(()=>{const dx=E('window.D3X');return dx.dice.filter(d=>d.match).every(d=>!d.roll);},25000);
    await sleep(250);
  }
  const avg=k=>Math.round(rows.reduce((a,r)=>a+r[k],0)/Math.max(1,rows.length));
  return {n:rows.length,tapeMs:avg('tapeMs'),totalDragMs:avg('totalDragMs'),
    worstDragMs:avg('worstDragMs'),rows:rows.map(r=>r.worstDragMs)};
};

const seeds=[101,202,303,404,505,606,707,808];
out.fixOn=await arm('on',true,seeds);
out.fixOff=await arm('off',false,seeds);
E('D3X.PHYS.creepFrames=6');E('D3X.PHYS.laneRadius=0.54');
out.dragDeltaMs=out.fixOff.worstDragMs-out.fixOn.worstDragMs;
out.dragPct=out.fixOff.worstDragMs?Math.round(100*out.dragDeltaMs/out.fixOff.worstDragMs):0;
out.tapeDeltaMs=out.fixOff.tapeMs-out.fixOn.tapeMs;
return out;
