/* apv_rulings — the three rulings: real reroll, type-as-truth, block_low_bank gone.
 *
 * P475 the card says reroll so it rerolls; P476 deletes a mechanic no card
 * declares; P477 makes `type` the single source of a card's use limit.
 * All three are Law 7 - gameplay decides, never code convenience.
 */
const sleep = ms => new Promise(r => setTimeout(r, ms));
const until = async (fn, ms) => { const t0=Date.now();
  while (Date.now()-t0<ms) { try { if (fn()) return true; } catch(e){} await sleep(60);} return false; };
await until(() => typeof _useCap === 'function' && typeof rollFace === 'function', 15000);
const v = {};

/* ── P477: type is the source of truth ── */
v.capFromType = _useCap({type:'once'}) === 1 && _useCap({type:'twice'}) === 2
             && _useCap({type:'thrice'}) === 3;
/* a card with no type at all still gets a sane floor rather than undefined */
v.capDefaults = _useCap({}) === 1 && _useCap(undefined) === 1;
/* and it resolves a CARD ID, which is what the call sites pass */
v.capByCardId = (function(){
  try { return _useCap('grogs_bump') === 2 && _useCap('quick_hands') === 1; }
  catch(e) { v._capErr = String(e).slice(0,60); return false; }
})();
/* the duplicate field is gone - type now carries it alone */
v.usesFieldGone = (function(){
  try { const c = getNpcCard('grogs_bump');
    return !!c && c.effect && c.effect.uses === undefined && c.effect.type === 'twice'; }
  catch(e) { return false; }
})();

/* ── P476: block_low_bank is gone ── */
/* STRIP COMMENTS BEFORE SEARCHING. A first version searched raw toString()
   and reported false because the PROSE still cited block_low_bank while the
   code did not - checking a claim about executable behaviour against text that
   includes commentary about it. */
v.blockLowBankGone = (function(){
  try {
    const strip = t => t.replace(/\/\*[\s\S]*?\*\//g, '');
    const src = strip(handleBank.toString())
      + strip(typeof runOppTurn === 'function' ? runOppTurn.toString() : '')
      + ['_oppFxOwnA','_oppFxOwnB','_oppFxPlayer','_oppFxDrain']
          .map(n => typeof window[n]==='function' ? strip(window[n].toString()) : '').join('');
    return src.indexOf('block_low_bank') < 0;
  } catch(e) { return false; }
})();

/* ── P475: reroll_all_kept actually rerolls ──
   The branch lives inside a card loop, so this checks the SHIPPED source for
   the reroll and the absence of the wipe, rather than driving a boss card. */
v.rerollNotWipe = (function(){
  try {
    const src = (typeof runOppTurn === 'function' ? runOppTurn.toString() : '')
      + (typeof _afterRollImpl === 'function' ? _afterRollImpl.toString() : '')
      + (typeof handleRoll === 'function' ? handleRoll.toString() : '');
    v._hasReroll = src.indexOf('rollFace(dd.mat)') >= 0;
    v._hasRescore = src.indexOf('_rrTotal') >= 0;
    v._wipeGone = src.indexOf('KEPT DICE WIPED') < 0;
    return v._hasReroll && v._hasRescore && v._wipeGone;
  } catch(e) { v._rrErr = String(e).slice(0,60); return false; }
})();

/* nothing earlier moved */
v.tablesIntact = typeof BANK_FX !== 'undefined' && Object.keys(BANK_FX).length === 4
              && typeof BUST_FX !== 'undefined' && typeof WILD_LEVEL !== 'undefined';

const notes = {};
for (const k of Object.keys(v)) { if (k[0] === '_') { notes[k] = v[k]; delete v[k]; } }
return { verdict: v, notes: notes };
