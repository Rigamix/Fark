/* Census v2. The v1 run conflated two different things and so agreed with
   nobody: an id in two DEFINITION tables is a collision; an id in a
   definition table and a REFERENCE list is a foreign key doing its job.
   NPC_RESCUES/NPC_ARMS rows are named for the card whose effect they run,
   and _RELIC_FAM is keyed by DICE_TYPES id on purpose. Counting those as
   collisions is what produced the inflated first number. */
const DEF={},REF={};
const add=(bag,name,v)=>{ let x; try{x=eval(v||name);}catch(e){return;} if(x!=null)bag[name]=x; };
['CARDS','NPC_CARDS','DICE_TYPES','FEATS','FAM_CARDS','ENCHANTS','ENCH_ICONS'].forEach(n=>add(DEF,n));
['NPC_RESCUES','NPC_ARMS','_RELIC_FAM','_SEAL_POOL','FAM_LIVE','NPC_FAM_READY','BOUNTY_POOL'].forEach(n=>add(REF,n));
/* tells are defined in two places: on RUNGS rows and in PARKED_TELLS */
let tellIds=[];
try{ tellIds=RUNGS.filter(r=>r&&r.tell&&r.tell.id).map(r=>r.tell.id); }catch(e){}
try{ tellIds=tellIds.concat(Object.keys(PARKED_TELLS)); }catch(e){}
DEF['TELLS']=[...new Set(tellIds)].map(id=>({id}));

const idsOf=v=>{
  if(Array.isArray(v))return v.map(r=>(r&&typeof r==='object')?r.id:r).filter(x=>typeof x==='string');
  if(v&&typeof v==='object')return Object.keys(v);
  return [];
};
const defWhere={},defCounts={};
for(const [n,v] of Object.entries(DEF)){
  const ids=idsOf(v); defCounts[n]=ids.length;
  ids.forEach(id=>{(defWhere[id]||(defWhere[id]=[])).push(n);});
}
const collisions={};
for(const [id,ts] of Object.entries(defWhere)){
  const u=[...new Set(ts)];
  if(u.length>1)collisions[id]=u;
}
/* foreign keys: an id in a reference list that resolves to a definition table */
const fk={},refCounts={};
for(const [n,v] of Object.entries(REF)){
  const ids=idsOf(v); refCounts[n]=ids.length;
  ids.forEach(id=>{ if(defWhere[id])(fk[n]||(fk[n]=[])).push(id+' -> '+defWhere[id].join('+')); });
}
/* dangling: a reference id that resolves to NOTHING */
const dangling={};
for(const [n,v] of Object.entries(REF)){
  idsOf(v).forEach(id=>{ if(!defWhere[id])(dangling[n]||(dangling[n]=[])).push(id); });
}
const C=CARDS, actives=C.filter(c=>c.type==='active');
return {
  defCounts, refCounts,
  collisionCount:Object.keys(collisions).length,
  collisions,
  foreignKeysByList:Object.fromEntries(Object.entries(fk).map(([k,v])=>[k,v.length])),
  danglingRefs:dangling,
  activesTotal:actives.length,
  bossActive:actives.filter(c=>c.npc).map(c=>c.id),
  nonBossActive:actives.filter(c=>!c.npc).map(c=>c.id),
};
