/* the OFF distribution only - runnable against a build that has no flag */
_getS();
const N=6000;
const BOSSES=[[3,'CORVUS'],[6,'WHISPER'],[7,'AMBROSE'],[0,'GROG']];
try{ if(typeof NPC_SYN_WEIGHTING!=='undefined')NPC_SYN_WEIGHTING=false; }catch(e){}
const out={hasFlag:(typeof NPC_SYN_WEIGHTING!=='undefined'),dist:{}};
BOSSES.forEach(([tier,name])=>{
  const rung=TIERS[tier]&&TIERS[tier].boss; if(!rung)return;
  const c={}; rung.cardPool.forEach(id=>{c[id]=0;});
  for(let i=0;i<N;i++)(generateOppCards(rung,0)||[]).forEach(id=>{c[id]=(c[id]||0)+1;});
  const tot=Object.keys(c).reduce((a,k)=>a+c[k],0)||1;
  const f={}; Object.keys(c).sort().forEach(k=>{f[k]=+(c[k]/tot).toFixed(3);});
  out.dist[name]=f;
});
return out;
