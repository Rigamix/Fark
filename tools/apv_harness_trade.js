/* Does a Trade brand survive into a harness match now?
 * The old failure was silent by construction, so this checks the one thing
 * nothing checked: what was ASKED FOR against what is STANDING on the table
 * once newG (and therefore _enchInit) has run. */
/* LOADS ITS OWN DEPENDENCY. FSIM lives in tools/sim_harness.js and is not part
   of the page, so run standalone this probe used to throw and report nothing.
   A probe that only works inside a bespoke wrapper is a probe the suite cannot
   run. */
if(typeof FSIM==='undefined'){
  try{ (0,eval)(await (await fetch('tools/sim_harness.js')).text()); }
  catch(e){ return {err:'sim harness would not load: '+e.message}; }
}
const R={};
try{
  /* the guards the harness has to satisfy, read from the game rather than
     assumed - if either ever changes, this test says so */
  R.guards={enchV:3,enchTradeV:1};

  const spec={dice:['bone','bone','bone','bone','bone','bone'],
              ench:['trade','trade','ward','snuff','trade','fog']};
  const m=FSIM.setupMatch(Object.assign({tier:3},spec));

  R.asked      = spec.ench.slice();
  R.refused    = (m.loadout&&m.loadout.refused)||[];
  R.lost       = m.lostEnch||null;
  R.standing   = (m.g._enchArr||[]).map(e=>e?e.t:null);
  R.saveSide   = (S.run.dieEnch||[]).map(e=>e?e.t:null);
  R.tradeCount = R.standing.filter(t=>t==='trade').length;
  R.versions   = {enchV:S.run._enchV, enchTradeV:S.run._enchTradeV};
  /* the phantom refund: 350g per nulled Trade used to land in the run's purse */
  R.gold       = S.run.gold;

  R.verdict={
    tradeSurvives:  R.tradeCount===3,
    nothingLost:    !R.lost,
    saveMatchesG:   JSON.stringify(R.standing)===JSON.stringify(R.saveSide),
    versionsStuck:  S.run._enchTradeV===1&&S.run._enchV===3
  };
}catch(e){R.err=String(e&&e.stack||e);}
return R;
