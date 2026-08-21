/* "If I have 3 cards or so they should have similar (and the ability
 * to play them)." Measure the ABILITY half: of the family cards a
 * patron is actually dealt, how many can the NPC seat fire?
 *  - passive  -> works via famFire seams (both seats)
 *  - active + in NPC_FAM_READY -> playable
 *  - active + NOT in NPC_FAM_READY -> DEAD in an NPC hand
 * Sampled over 200 generated patrons per tier. */
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(fn,ms)=>{const t0=Date.now();while(Date.now()-t0<ms){try{if(fn())return true;}catch(e){}await sleep(120);}return false;};
if(!await until(()=>typeof generatePatron==='function'&&typeof FAM_CARDS!=='undefined',20000))return {err:'no boot'};
if(typeof _getS==='function')_getS();
const ready=(typeof NPC_FAM_READY!=='undefined')?Object.keys(NPC_FAM_READY):[];
const defOf=id=>FAM_CARDS.find(c=>c.id===id)||{};
const allActives=FAM_CARDS.filter(c=>c.kind==='active').map(c=>c.id);
const deadActives=allActives.filter(id=>ready.indexOf(id)<0);
const out={ready,allActives,deadActives,byTier:[]};
for(let t=0;t<8;t++){
  let n=0,passive=0,playable=0,dead=0,none=0;
  const deadSeen={};
  for(let i=0;i<200;i++){
    const p=generatePatron(t,null);
    const fc=p.fcards||[];
    if(!fc.length)none++;
    fc.forEach(c=>{
      n++;
      const d=defOf(c.id);
      if(d.kind!=='active')passive++;
      else if(ready.indexOf(c.id)>=0)playable++;
      else {dead++;deadSeen[c.id]=(deadSeen[c.id]||0)+1;}
    });
  }
  out.byTier.push({tier:t,night:t+1,
    cardsPer100Patrons:+(n/2).toFixed(1),
    emptyHands:+(none/2).toFixed(0)+'%',
    passive,playable,dead,
    deadPct:n?+(100*dead/n).toFixed(1):0,
    deadIds:deadSeen});
}
/* and the same question for BOSSES, for contrast */
const bossRows=[];
(typeof RUNGS!=='undefined'?RUNGS:[]).forEach(r=>{
  if(!r||!r.key||r.key==='patron')return;
  bossRows.push({boss:r.name,fam:(r.fcards||[]).map(c=>c.id||c).join(',')||'(none in RUNGS row)'});
});
return Object.assign(out,{bossRows,
  headline:{
    activesTotal:allActives.length,
    activesPlayableByNPC:ready.length,
    activesDeadInNPCHand:deadActives.length,
    deadList:deadActives}});
