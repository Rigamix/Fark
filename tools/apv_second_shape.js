/* apv_second_shape — BANK_TAKE, SCORE_DRAIN, and the challenge double-charge.
 *
 * The two rows are pure functions and checked directly. The challenge fix is
 * arithmetic buried inside finOpp, which is not callable — so rather than
 * re-testing a COPY of what I believe I wrote, the three shipped lines are
 * EXTRACTED from runOppTurn.toString() and executed against controlled values.
 * A copy would pass even if the patch had landed somewhere else entirely.
 */
const sleep = ms => new Promise(r => setTimeout(r, ms));
const until = async (fn, ms) => { const t0 = Date.now();
  while (Date.now()-t0 < ms) { try { if (fn()) return true; } catch(e){} await sleep(60);} return false; };
await until(() => typeof BANK_TAKE !== 'undefined' && typeof runOppTurn === 'function', 15000);
if (typeof BANK_TAKE === 'undefined') return { skip: 'BANK_TAKE not defined' };
const v = {};

/* ── the two rows ── */
v.stealPct   = BANK_TAKE.steal_pct(1000, {pct:0.25}) === 250
            && BANK_TAKE.steal_pct(101,  {pct:0.5})  === 51;   /* ceil, not floor */
v.stealNoPct = BANK_TAKE.steal_pct(500, {}) === 0;

v.drainClamps = SCORE_DRAIN.periodic_drain(300, {amount:500}) === 0   /* never negative */
             && SCORE_DRAIN.periodic_drain(1000,{amount:400}) === 600;
v.drainNoAmount = SCORE_DRAIN.periodic_drain(700, {}) === 700;

/* ── the challenge fix, run from the SHIPPED source ── */
const src = runOppTurn.toString();
/* STRIP COMMENTS BEFORE ASSERTING ABSENCE. The patch's own comment QUOTES the
   expression it removed, and toString() returns comments - so this tripped on
   the note explaining the fix rather than on live code. Same trap as every
   other time an assert read its own explanation as the thing explained. */
const code = src.replace(/\/\*[\s\S]*?\*\//g, '');
v.oldExprGone = code.indexOf('eff.penalty-penalty') < 0;
v.newExprPresent = src.indexOf('_chFromBank') >= 0;

const grab = /var _chFromBank=[\s\S]{0,220}?G\.oPts=Math\.max\(0,G\.oPts-\(penalty-_chFromBank\)\);/.exec(src);
v._extracted = grab ? grab[0].replace(/\s+/g,' ').slice(0,150) : null;
if (grab) {
  /* CAPTURE THE ORIGINALS FIRST. `arguments[0]` stays LINKED to the pts
     parameter, which the extracted code reassigns, so reading it afterwards
     gave the new value and made a correct fix look like it lost nothing. */
  const run = new Function('pts','oPts','effPen', `
    var _p0=pts,_o0=oPts;
    var G={oPts:oPts}; var penalty=Math.min(effPen,G.oPts+pts);
    ${grab[0]}
    return {pts:pts,oPts:G.oPts,lost:_p0+_o0-(G.oPts+pts)};`);
  const a = run(200, 1000, 500);   /* used to lose 700 */
  const b = run(600, 1000, 500);   /* used to lose 1000 */
  const c = run(100,  300, 500);   /* cannot afford: capped at 400 */
  v._cases = {a:a, b:b, c:c};
  v.exactlyPenalty = a.lost === 500 && b.lost === 500;
  v.cappedWhenPoor = c.lost === 400 && c.oPts === 0 && c.pts === 0;
  v.bankPaysFirst  = b.pts === 100 && b.oPts === 1000;  /* 600-500 bank, pool untouched */
} else { v.exactlyPenalty = null; v.cappedWhenPoor = null; v.bankPaysFirst = null; }

/* BANK_FX from the previous pass must be undisturbed */
v.bankFxIntact = typeof BANK_FX !== 'undefined' && Object.keys(BANK_FX).length === 4;

const notes = {};
for (const k of Object.keys(v)) { if (k[0] === '_') { notes[k] = v[k]; delete v[k]; } }
return { verdict: v, notes: notes };
