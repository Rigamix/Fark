/* Q43: is HALF MEASURE obtainable? Run the game's OWN draft filter. */
const R={};
const hm=CARDS.filter(c=>c.id==='half_measure')[0]||null;
R.defined=!!hm;
R.flags=hm?{rarity:hm.rarity,npcOnly:!!hm.npcOnly,npc:!!hm.npc,dep:!!hm.dep,counter:!!hm.counter,type:hm.type||null}:null;
/* which tiers list its rarity in their draft pool? */
R.tiersOfferingTin=[];
try{(TIERS||[]).forEach((t,i)=>{if(t&&Array.isArray(t.draftPool)&&t.draftPool.indexOf(hm.rarity)>=0)R.tiersOfferingTin.push(i);});}catch(e){}
/* the exact predicate the draft uses */
try{
  R.isBlocked=(typeof _isBlocked==='function')?_isBlocked(hm):'no fn';
  R.goldOK=(typeof _goldDraftOK==='function')?_goldDraftOK(hm):'no fn';
  R.silverOK=(typeof _silverDraftOK==='function')?_silverDraftOK(hm):'no fn';
}catch(e){R.predErr=String(e);}
R.passesDraftFilter=!!(hm&&!hm.npcOnly&&!hm.npc&&!hm.dep&&R.isBlocked===false&&R.goldOK!==false&&R.silverOK!==false);
/* and the NPC-side pool builder at 11194 */
R.inNpcPoolBuilder=!!(hm&&!hm.npcOnly&&!hm.type&&!hm.dep&&!hm.counter);
/* the counter's meaning: kept.vals counts DICE, so an icon die (which banks 0)
   still contributes a val - which is the question's substance */
R.counterCountsIconDie=(function(){
  const kept=[{vals:[1,5]},{vals:[3]}];      /* 3 dice committed, one of them scoring 0 */
  return kept.reduce((a,k)=>a+k.vals.length,0)===3;
})();
/* the OTHER card people mean by the name */
const mt=(typeof NPC_CARDS!=='undefined'?NPC_CARDS:[]).filter(c=>c.id==='measure_twice')[0]
      ||CARDS.filter(c=>c.id==='measure_twice')[0]||null;
R.measure_twice=mt?{npcOnly:!!mt.npcOnly,owner:mt.owner||null,rarity:mt.rarity}:'not found';
return R;
