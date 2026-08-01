/* Do the relic tints reach the renderer, keyed by the id the game uses? */
const hex=n=>'0x'+(n>>>0).toString(16).padStart(6,'0');
const RELICS=['grogs_tooth','mabels_thimble','finnicks_palm','corvus_ledger_d',
              'brutus_shield','aldrics_square','whispers_fang','ambrose_weight'];
const out={};
out.tints={};out.rough={};out.missing=[];
RELICS.forEach(id=>{
  const c=D3X.MATCOL[id];
  if(c===undefined)out.missing.push(id); else out.tints[id]=hex(c);
  out.rough[id]=D3X.ROUGH[id];
});
/* the ids the game actually uses, so a key that matches nothing shows up */
out.realIds=DICE_TYPES.filter(d=>d.relic).map(d=>d.id);
out.everyRealIdHasATint=out.realIds.every(id=>D3X.MATCOL[id]!==undefined);
out.staleKeyGone=D3X.MATCOL.corvus_ledger===undefined;
out.verdict={
  allEightTinted: out.missing.length===0,
  keyedByRealId:  out.everyRealIdHasATint===true,
  staleKeyRemoved:out.staleKeyGone===true
};
return out;
