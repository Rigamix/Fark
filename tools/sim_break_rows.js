/* THE FIVE UNVALIDATED BREAK ROWS — the same two numbers Obsidian already has.
 *
 * Brief §4's Obsidian result is a TIMING finding, not a power one: breaking
 * immediately is a net LOSS across a match (~3,471 vs ~4,425), while on a turn
 * with no future to protect it flips hard positive (1,140 vs 409, bust 46% ->
 * 8%). The other five rows - Amber, Starstone, Silver, Jade, Vagabond - are
 * design proposals with no numbers at all. This gets them the same pair.
 *
 * THE FAMILY IS FORCED, NOT CHOSEN. The harness's breakTarget picks by
 * breakRowValue(), which is a hardcoded guess (obsidian 5, vagabond 4,
 * starstone 3, amber 2, silver 1, jade 1). Measuring row value with a policy
 * that selects targets BY that guess would measure the guess. So each batch
 * gets exactly one break-branded die, of one family, and the target is
 * determined by construction.
 *
 * NAIVE vs INFORMED IS THE WHOLE INSTRUMENT. Those two agents differ in one
 * thing only - the informed one withholds the skull until the last turn - so
 * the gap between them is Break timing and nothing else. Per family:
 *   informed - naive  >  0   the row rewards holding it for the last turn
 *   informed - naive ~= 0   timing does not matter for this row
 *   informed - naive  <  0   the row wants to be spent early
 */
var seed=(window.__FSIM_SEED!==undefined)?window.__FSIM_SEED:20260803;
/* 260 IS TOO SMALL AND THE FILE SHOULD SAY SO. At tier 4 both Gregs win about
   1% of matches, so 260 runs puts every win-rate figure between one and six
   MATCHES - a single result moves the rate .38 points and no timing sign can
   be read off it. Raise this to the low thousands for anything quotable;
   docs/BREAK_ROWS_2026-08-03.md has the full caveat. */
var N=(window.__FSIM_N!==undefined)?window.__FSIM_N:800;
var TIER=(window.__FSIM_TIER!==undefined)?window.__FSIM_TIER:4;
var FAMS=['obsidian','amber','starstone','silver','jade','vagabond'];
var out={seed:seed,n:N,tier:TIER,rows:{},notes:[],
         breakRowValueGuess:{obsidian:5,vagabond:4,starstone:3,amber:2,silver:1,jade:1}};

FSIM.quiet();
var t0=performance.now();
FAMS.forEach(function(fam){
  /* THE BRAND GOES ON A BONE DIE AND THE FAMILY DIE IS THE TARGET, which is
     the opposite of the first version of this file and the whole reason its
     numbers were void. Break destroys ONE OTHER die: with the brand on the
     family die and bone everywhere else, every batch destroyed bone and fired
     the MUNDANE NO-OP row - six families measured, one row actually tested.
     The tell was starstone and vagabond coming back byte-identical.
     With exactly one non-bone die in the loadout the target is still
     determined by construction, since breakRowValue scores bone at 0 and every
     family above it - so this does not reintroduce the guess it avoids. */
  var gear={key:'brk_'+fam,
            dice:['bone',fam,'bone','bone','bone','bone'],
            ench:['break',null,null,null,null,null],
            badge:null,fcards:[]};
  var r={};
  ['greg_naive','greg_informed'].forEach(function(k){
    FSIM.installRng(seed);
    var b=FSIM.runBatch(FSIM.POLICIES[k],{tier:TIER,gear:gear},N);
    r[k]={win:+(100*b.winRate.p).toFixed(1),
          bank:Math.round(b.meanBank.mean),
          bustPerTurn:+(100*b.bustRate.p).toFixed(1),
          capEnd:b.capEndPct,
          errors:b.errors};
  });
  /* the timing signal: informed minus naive */
  r.timingDelta={win:+(r.greg_informed.win-r.greg_naive.win).toFixed(1),
                 bank:r.greg_informed.bank-r.greg_naive.bank};
  out.rows[fam]=r;
});
out.ms=Math.round(performance.now()-t0);
FSIM.loud();FSIM.restoreRng();
return out;
