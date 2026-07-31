/* EVERY ART PATH THE GAME CAN CONSTRUCT, tested against the server.
 * Uses the game's OWN id lists and its own path shapes, so extensions and
 * directories are whatever the code really uses rather than what I assume. */
const rows=[];
const add=(url,kind,id,live)=>rows.push({url,kind,id,live:!!live});

/* family cards -> assets/cards/<id>.webp (famCardArt) */
try{
  const live=(typeof FAM_LIVE!=='undefined')?FAM_LIVE:{};
  (FAM_CARDS||[]).forEach(d=>add('assets/cards/'+d.id+'.webp','family card',d.id,live[d.id]));
}catch(e){}
/* game/NPC cards -> assets/Card_ART/<id>.png (_cardArtImg) */
try{
  const ids=new Set();
  (typeof NPC_CARDS!=='undefined'?NPC_CARDS:[]).forEach(c=>c&&c.id&&ids.add(c.id));
  (typeof CARDS!=='undefined'?CARDS:[]).forEach(c=>c&&c.id&&ids.add(c.id));
  ids.forEach(id=>add('assets/Card_ART/'+id+'.png','game card',id,true));
}catch(e){}
/* enchant icons -> assets/ench_icons/<id>.png */
try{(ENCH_GRID||[]).forEach(id=>add(ENCH_ICON_DIR+id+'.png','enchant icon',id,true));}catch(e){}
/* patron portraits -> PT_P + <art>.png */
try{
  const seen=new Set();
  const rost=(S&&S.run&&S.run.night&&S.run.night.roster)||[];
  rost.forEach(r=>{if(r&&r.art&&!seen.has(r.art)){seen.add(r.art);add(PT_P+r.art+'.png','patron portrait',r.art,true);}});
  if(typeof PATRONS!=='undefined')(PATRONS||[]).forEach(p=>{if(p&&p.art&&!seen.has(p.art)){seen.add(p.art);add(PT_P+p.art+'.png','patron portrait',p.art,true);}});
}catch(e){}

const byUrl={},uniq=[];
rows.forEach(r=>{if(!byUrl[r.url]){byUrl[r.url]=r;uniq.push(r);}else if(r.live)byUrl[r.url].live=true;});
const missing=[];let present=0;
for(const r of uniq){
  let ok=false;
  try{const res=await fetch(r.url,{method:'GET'});ok=res.ok;}catch(e){ok=false;}
  if(ok)present++;else missing.push(r);
}
const byKind={};
missing.forEach(m=>{byKind[m.kind]=byKind[m.kind]||[];byKind[m.kind].push({id:m.id,url:m.url,draftable:m.live});});
return {checked:uniq.length,present,missingCount:missing.length,missingByKind:byKind};
