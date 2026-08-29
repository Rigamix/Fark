/* P863 - a save written before the twenty were deleted, loaded after.
 *
 * THE FIRST VERSION OF THIS PROBE PROVED NOTHING and said so: it set the
 * phantom ids on the live S and called _getS(), but the whole migration block
 * sits inside `if(!S){...}` and runs on FIRST LOAD only. With S already
 * populated the strip never executed, and the probe reported "nothing was
 * stripped" - a true statement about a code path it had not reached. The
 * positive control is the only reason that was visible.
 *
 * So this writes the save to localStorage and clears S to force the real
 * load path, which is also the path a returning player actually takes.
 *
 * TWO CONTROLS, because _cardGone's try/catch fails OPEN: if the catalog were
 * unreachable it returns false and strips nothing, which looks exactly like
 * having nothing to strip. A dead id that MUST go, and a live id that MUST
 * stay - neither alone is a measurement. */
if(typeof _getS!=='function')return {err:'no boot'};
_getS();
const fresh=JSON.parse(JSON.stringify(S));

/* a pre-P862 run: two deleted ids and two survivors in the deck, three more
   in the pouch. _p12CardsConverted is pre-set or the older P616 converter
   blanks every slot before the strip under test is reached. */
fresh.run._p12CardsConverted=1;
fresh.run.cards=['second_wind','the_tab','wild_die','loan'];
fresh.run.pouch=['coin_flip','the_pyre','mabels_stitch'];
localStorage.setItem('gambit4_proto',JSON.stringify(fresh));

S=null;            /* force the `if(!S)` first-load branch */
_getS();

const cards=(S.run.cards||[]).slice(0,4);
const pouch=(S.run.pouch||[]).slice(0,3);
return {
  cardsAfter:cards,
  pouchAfter:pouch,
  reachedTheLoadPath: !!S && S.run.cards!==undefined,
  deletedStripped: cards[1]===null&&cards[2]===null&&pouch[0]===null&&pouch[2]===null,
  survivorsKept: cards[0]==='second_wind'&&cards[3]==='loan'&&pouch[1]==='the_pyre',
  catalogReachable: (function(){try{return !!(CARDS_MAP['second_wind']&&!CARDS_MAP['the_tab']);}catch(e){return 'THREW: '+e.message;}})(),
  VERDICT:(cards[1]===null&&cards[2]===null&&pouch[0]===null&&pouch[2]===null
           &&cards[0]==='second_wind'&&cards[3]==='loan'&&pouch[1]==='the_pyre')?'PASS':'FAIL',
};
