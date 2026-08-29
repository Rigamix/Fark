/* Runtime id census: reads the REAL table arrays out of the loaded page
   rather than grepping the source. A grep counts text that looks like a
   row; this counts rows the game actually has. shoot.js wraps this file
   in (async()=>{ ... })(), so the body just returns. */
const NAMES=['CARDS','NPC_CARDS','DICE_TYPES','FEATS','FAM_CARDS','RUNGS','TIERS',
             'ENCH','ENCHANTS','RELICS','_SEAL_POOL','PARKED_TELLS','HANDICAPS',
             'NPC_RESCUE','RESCUES','TRINKETS','PERKS','SHOP_ITEMS','_RELIC_FAM'];
const tables={},missing=[];
for(const n of NAMES){
  let v;
  try{ v=eval(n); }catch(e){ missing.push(n); continue; }
  if(v==null){missing.push(n);continue;}
  tables[n]=v;
}
const extra={};
for(const k of Object.keys(window)){
  try{
    const v=window[k];
    if(Array.isArray(v)&&v.length>2&&v.every(r=>r&&typeof r==='object'&&typeof r.id==='string')){
      if(!(k in tables)){extra[k]=v.length;tables[k]=v;}
    }
  }catch(e){}
}
const idsOf=v=>{
  if(Array.isArray(v))return v.map(r=>(r&&typeof r==='object')?r.id:r).filter(x=>typeof x==='string');
  if(v&&typeof v==='object')return Object.keys(v);
  return [];
};
const where={},counts={};
for(const [name,v] of Object.entries(tables)){
  const ids=idsOf(v);
  counts[name]=ids.length;
  ids.forEach(id=>{ (where[id]||(where[id]=[])).push(name); });
}
const dupes={},within={};
for(const [id,ts] of Object.entries(where)){
  const uniq=[...new Set(ts)];
  if(uniq.length>1)dupes[id]=uniq;
  if(ts.length>uniq.length)within[id]=ts;
}
const byDepth={};
Object.entries(dupes).forEach(([id,ts])=>{(byDepth[ts.length]||(byDepth[ts.length]=[])).push(id);});
const C=(typeof CARDS!=='undefined'?CARDS:[]);
const actives=C.filter(c=>c.type==='active');
const bossCards=actives.filter(c=>c.npc);
const rungTells=(typeof RUNGS!=='undefined'?RUNGS:[]).map(r=>({rung:r.id||r.name,tell:r.tell?r.tell.id:null}));
return {
  counts, missing, extraFound:extra,
  totalCollidedIds:Object.keys(dupes).length,
  byDepth:Object.fromEntries(Object.entries(byDepth).map(([k,v])=>[k,v.sort()])),
  dupes,
  dupWithinOneTable:within,
  activesTotal:actives.length,
  bossCardIds:bossCards.map(c=>c.id),
  nonBossActiveIds:actives.filter(c=>!c.npc).map(c=>c.id),
  rungTells,
};
