/* do the two new family-card arts resolve on the path the game asks for? */
const R={};
const probe=async u=>{try{const r=await fetch(u);return r.ok;}catch(e){return false;}};
for(const id of ['steady_hand','fair_trade','ward','slow_cook','preserve'])
  R[id]=await probe('assets/cards/'+id+'.webp');
/* and every LIVE family card, so nothing else is quietly missing */
const live=[];
try{
  Object.keys(FAM_LIVE).forEach(id=>{ if(FAM_LIVE[id])live.push(id); });
}catch(e){R.err=String(e);}
const missing=[];
for(const id of live){ if(!(await probe('assets/cards/'+id+'.webp'))) missing.push(id); }
R.liveCards=live.length;
R.stillMissing=missing;
return R;
