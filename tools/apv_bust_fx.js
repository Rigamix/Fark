/* apv_bust_fx — BUST_FX resolves the two mirrors' numbers identically per seat.
 *
 * Each mechanic has exactly ONE card, and the boss side used to repeat that
 * card's values as `||` fallbacks while the player side had none. The rows now
 * hold them, so this checks the rows return the card's real numbers AND that
 * both seats plus BOTH MESSAGES read from the row — a message computing its
 * number from a second copy of the expression is the challenge pattern in
 * miniature, and that is exactly how the boss's gain_pts line was written.
 */
const sleep = ms => new Promise(r => setTimeout(r, ms));
const until = async (fn, ms) => { const t0=Date.now();
  while (Date.now()-t0<ms) { try { if (fn()) return true; } catch(e){} await sleep(60);} return false; };
await until(() => typeof BUST_FX !== 'undefined', 15000);
if (typeof BUST_FX === 'undefined') return { skip: 'BUST_FX not defined' };
const v = {};

/* rows return the real cards' values */
v.gainPtsCard = BUST_FX.gain_pts.amount({amount:500}) === 500;
v.punishCard  = BUST_FX.punish_busts.threshold({threshold:2}) === 2
             && BUST_FX.punish_busts.penalty({penalty:1500}) === 1500;
/* and the defaults match what the boss side used to hardcode */
v.defaults = BUST_FX.gain_pts.amount({}) === 500
          && BUST_FX.punish_busts.threshold({}) === 2
          && BUST_FX.punish_busts.penalty({}) === 1500;
/* undefined effect must not throw or produce NaN - the player side had no guard */
v.survivesUndefined = BUST_FX.gain_pts.amount(undefined) === 500
                   && BUST_FX.punish_busts.penalty(null) === 1500;

/* the real card definitions still carry the numbers the rows default to */
v._cards = (function(){
  try {
    const out = {};
    for (const c of (typeof NPC_CARDS !== 'undefined' ? NPC_CARDS : [])) {
      const e = c && c.effect;
      if (e && (e.mechanic === 'gain_pts' || e.mechanic === 'punish_busts'))
        out[c.id] = {m:e.mechanic, amount:e.amount, threshold:e.threshold, penalty:e.penalty};
    }
    return out;
  } catch(e) { return null; }
})();

/* BOTH SEATS AND BOTH MESSAGES wired. doBust is the player's, _oppBustOut is
   nested inside runOppTurn - the same not-a-global trap as finOpp. */
v.bothSeatsWired = (function(){
  try {
    const p = doBust.toString();
    const o = (typeof runOppTurn === 'function') ? runOppTurn.toString() : '';
    v._pHits = (p.match(/BUST_FX\./g) || []).length;
    v._oHits = (o.match(/BUST_FX\./g) || []).length;
    return v._pHits >= 3 && v._oHits >= 4;
  } catch(e) { v._wireErr = String(e).slice(0,60); return false; }
})();

/* nothing hardcodes the old fallbacks any more, in either seat */
v.noStaleFallbacks = (function(){
  try {
    const all = doBust.toString() + ((typeof runOppTurn === 'function') ? runOppTurn.toString() : '');
    return all.indexOf('amount||500') < 0 && all.indexOf('penalty||1500') < 0
        && all.indexOf('threshold||2') < 0;
  } catch(e) { return false; }
})();

/* earlier tables undisturbed */
v.earlierTablesIntact = typeof BANK_FX !== 'undefined' && Object.keys(BANK_FX).length === 4
                     && typeof BANK_TAKE !== 'undefined' && typeof WILD_LEVEL !== 'undefined';

const notes = {};
for (const k of Object.keys(v)) { if (k[0] === '_') { notes[k] = v[k]; delete v[k]; } }
return { verdict: v, notes: notes };
