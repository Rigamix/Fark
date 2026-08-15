/* SUITE: exclude. THE TAIL: how long does a throw spend crawling?
 * Measures, per die, the frames after its last FAST frame - the visible
 * 'sliding into place'. */
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(fn,ms)=>{const t0=Date.now();while(Date.now()-t0<ms){try{if(fn())return true;}catch(e){}await sleep(100);}return false;};
const out={rolls:[]};
await setup();
if(!await until(()=>{const g=E('G');return g&&g.phase;},4000))return {err:'no match'};
const stat=()=>{
  const dx=E('window.D3X');
  let ds=dx.dice.filter(d=>d.match&&d.roll&&d.roll.sol&&d.roll.sol.frames);
  if(!ds.length)return null;
  const sol=ds[0].roll.sol;                 /* one tape only */
  ds=ds.filter(d=>d.roll.sol===sol&&sol.frames[0][d.roll.i]);
  if(!ds.length)return null;
  const fr=sol.frames,dt=E('D3X.PHYS.dt')*1000;
  const per=ds.map(d=>{
    const i=d.roll.i;
    let lastFast=0,crawl=0;
    for(let f=1;f<fr.length;f++){
      const a=fr[f-1][i],b=fr[f][i];
      const dv=Math.abs(b.x-a.x)+Math.abs(b.y-a.y)+Math.abs(b.z-a.z);
      if(dv>0.05)lastFast=f;                 /* clearly moving */
      if(dv>0.004&&dv<=0.05)crawl++;         /* creeping - the drag */
    }
    return {frames:fr.length,lastFast,tail:fr.length-lastFast,
      tailMs:Math.round((fr.length-lastFast)*dt),crawl};
  });
  return {frames:fr.length,tapeMs:Math.round(fr.length*dt),
    worstTailMs:Math.max(...per.map(p=>p.tailMs)),
    medTailMs:per.map(p=>p.tailMs).sort((a,b)=>a-b)[Math.floor(per.length/2)],
    worstCrawl:Math.max(...per.map(p=>p.crawl))};
};
for(let r=0;r<6;r++){
  E('handleRoll()');
  if(!await until(()=>E('window.D3X').dice.some(d=>d.match&&d.roll),12000))break;
  await sleep(200);
  const s=stat();if(s)out.rolls.push(s);
  await until(()=>{const dx=E('window.D3X');return dx.dice.filter(d=>d.match).every(d=>!d.roll);},25000);
  await sleep(400);
  try{E('G.pool.forEach(function(d){d.committed=false;d.sel=false;});G.phase="choosing"');}catch(e){}
}
out.crawls=out.rolls.map(r=>r.worstCrawl).sort((a,b)=>a-b);
out.medCrawl=out.crawls[Math.floor(out.crawls.length/2)];
out.avgTapeMs=Math.round(out.rolls.reduce((a,r)=>a+r.tapeMs,0)/Math.max(1,out.rolls.length));
out.avgWorstTailMs=Math.round(out.rolls.reduce((a,r)=>a+r.worstTailMs,0)/Math.max(1,out.rolls.length));
out.avgCrawl=Math.round(out.rolls.reduce((a,r)=>a+r.worstCrawl,0)/Math.max(1,out.rolls.length));
return out;
