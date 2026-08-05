/* apv_bank_fx — BANK_FX computes exactly what the two copies did.
 *
 * P465 pulled the arithmetic shared by handleBank and finOpp into one table.
 * A consolidation's whole claim is "the numbers did not change", so every row
 * is checked against the expression it replaced, with EXACT values — an
 * inequality cannot tell "the row works" from "the row returns the input".
 *
 * The odd-number halving case is deliberate: the old code was
 * `half=Math.floor(a/2); a-=half`, so 101 must leave 51, not 50. A row written
 * as `Math.ceil(a/2)` would pass on every even number and fail only here.
 */
const sleep = ms => new Promise(r => setTimeout(r, ms));
const until = async (fn, ms) => { const t0 = Date.now();
  while (Date.now() - t0 < ms) { try { if (fn()) return true; } catch(e){} await sleep(60); } return false; };
await until(() => typeof BANK_FX !== 'undefined', 15000);
if (typeof BANK_FX === 'undefined') return { skip: 'BANK_FX not defined' };
const F = BANK_FX, v = {};

v.rowsPresent = ['flat_bonus','double_first_bank','halve_first_bank','gain_when_ahead']
  .every(k => typeof F[k] === 'function') && Object.keys(F).length === 4;

/* flat_bonus: was total+=eff.amount */
v.flatBonus = F.flat_bonus(100, {amount:50}) === 150 && F.flat_bonus(0, {amount:700}) === 700;
/* the rival used eff.amount BARE - undefined would have made NaN. Now 0. */
v.flatBonusDefault = F.flat_bonus(100, {}) === 100;

/* double_first_bank: was total*=2 */
v.doubleBank = F.double_first_bank(300, {}) === 600 && F.double_first_bank(0, {}) === 0;

/* halve_first_bank: was half=floor(a/2); a-=half. ODD NUMBERS ARE THE TEST. */
v.halveEven = F.halve_first_bank(400, {}) === 200;
v.halveOdd  = F.halve_first_bank(101, {}) === 51;   /* 101 - floor(101/2) = 51 */
v._halve101 = F.halve_first_bank(101, {});

/* gain_when_ahead: the player had ||500, the rival had nothing. Both now do. */
v.gainExplicit = F.gain_when_ahead(100, {amount:200}) === 300;
v.gainDefault  = F.gain_when_ahead(100, {}) === 600;

/* rows must be pure - no reads of G, no side effects on the effect object */
const probe = {amount: 50};
F.flat_bonus(10, probe);
v.rowsArePure = probe.amount === 50 && Object.keys(probe).length === 1;

/* BOTH SEATS REALLY DO CALL THE TABLE. finOpp is NOT a global - it is nested
   inside runOppTurn - so a first version of this check asked whether finOpp
   was reachable and reported false for the rival side while the wiring was
   fine. That is the same mistake as everything else tonight: it measured
   reachability and I read it as wiring. The rival's code is looked for where
   it actually lives. */
v._rivalHost = (typeof runOppTurn === 'function') ? 'runOppTurn' : null;
v.bothSeatsWired = (function(){
  try {
    const ROWS = ['flat_bonus','double_first_bank','halve_first_bank','gain_when_ahead'];
/* THE RIVAL'S BANK CODE NO LONGER LIVES IN runOppTurn. P470 extracted its four
   card-effect loops into named functions so the sim could call them, and this
   probe went red by searching the old location - the code moved, nothing
   vanished (verified: every marker is in the extracted set, none in
   runOppTurn). A structural refactor SHOULD break a probe that hard-codes
   structure; the fix is to name the new structure, not to loosen the check. */
const _rivalSrc = (function(){
  var out = (typeof runOppTurn === 'function') ? runOppTurn.toString() : '';
  ['_oppFxOwnA','_oppFxOwnB','_oppFxPlayer','_oppFxDrain'].forEach(function(n){
    if (typeof window[n] === 'function') out += window[n].toString();
  });
  return out;
})();
    const hb = handleBank.toString();
    const ro = _rivalSrc;
    v._playerRows = ROWS.filter(k => hb.indexOf('BANK_FX.'+k) >= 0);
    v._rivalRows  = ROWS.filter(k => ro.indexOf('BANK_FX.'+k) >= 0);
    return v._playerRows.length === 4 && v._rivalRows.length === 4;
  } catch(e) { v._wireErr = String(e).slice(0,60); return false; }
})();

/* DIAGNOSTICS OUT OF THE VERDICT. run_probes marks a probe INDET if ANY verdict
   key is non-boolean, so the _-prefixed values I was returning for debugging
   made every one of these probes indeterminate in the suite - passing when run
   by hand, invisible as a regression guard where it counts. Underscore keys
   move to notes; a genuine null stays in the verdict, because "did not run"
   SHOULD read as indeterminate. */
const notes = {};
for (const k of Object.keys(v)) { if (k[0] === '_') { notes[k] = v[k]; delete v[k]; } }
return { verdict: v, notes: notes };
