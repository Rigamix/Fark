/* Denis's correction: "I can win active cards from the start like I currently
 * do? Only limitation is boss cards, limited to boss encounters."
 *
 * My OPEN.md question 2 asked whether section 2 had made actives boss-only. It
 * had not, and the question was wrong: section 2 deletes CARDS-table actives,
 * which the player has never been able to hold, while the cards a player
 * actually drafts are FAM_CARDS, a different table with its own kinds.
 *
 * Read: famOffer's pool filter is _famDraftable + tavern/tier rules, with no
 * `kind` test anywhere. But a filter that LOOKS absent is exactly the claim
 * this project keeps getting wrong from reading, so this DRAWS instead - 400
 * night-1 offers - and asks how many actives actually come out.
 */
if(typeof famOffer!=='function')return {err:'no famOffer'};
_getS();
S.run.tier=0;                     /* night 1 */
S.run.fcards=[];                  /* nothing owned, so nothing is tier-locked out */

const kinds={active:0,passive:0,other:0};
const seenActive=new Set(), seenAny=new Set();
let draws=0;
for(let i=0;i<400;i++){
  let off=[];
  try{off=famOffer(false)||[];}catch(e){return {err:'famOffer threw: '+e.message};}
  off.forEach(c=>{
    if(!c||!c.id)return;
    draws++;
    seenAny.add(c.id);
    const d=(typeof famDef==='function')?(famDef(c.id)||c):c;
    if(d.kind==='active'){kinds.active++;seenActive.add(c.id);}
    else if(d.kind==='passive')kinds.passive++;
    else kinds.other++;
  });
}
/* the table's own composition, so the draw rate can be judged against it */
const tblActive=FAM_CARDS.filter(c=>c.kind==='active').length;
const tblPassive=FAM_CARDS.filter(c=>c.kind==='passive').length;

return {
  night:1,
  offersDrawn:draws,
  kinds,
  distinctActivesOffered:[...seenActive].sort(),
  distinctCardsOffered:seenAny.size,
  tableComposition:{active:tblActive,passive:tblPassive,total:FAM_CARDS.length},
  activeShareOfDraws:+(kinds.active/draws).toFixed(3),
  activeShareOfTable:+(tblActive/(tblActive+tblPassive)).toFixed(3),
  VERDICT:{
    /* the instrument drew anything at all */
    drewSomething: draws>0,
    /* the answer to Denis's question */
    activeFamilyCardsOfferedOnNight1: kinds.active>0,
    /* and not as a token: the draw rate tracks the table, i.e. nothing is
       quietly down-weighting them */
    notQuietlySuppressed: (kinds.active/draws) > (tblActive/(tblActive+tblPassive))*0.4,
  },
};
