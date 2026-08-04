/* apv_challenge_both — both seats lose exactly the stated penalty, capped.
 *
 * P466 fixed the rival over-charging; P467 fixed the player under-charging. The
 * claim is now SYMMETRY, so this runs the SHIPPED lines from both functions on
 * IDENTICAL inputs and requires identical losses. Extracted from toString(),
 * not reconstructed — a copy proves the arithmetic is right, not that it
 * shipped, and those have diverged in this file before.
 *
 * The pool-0 case is the one that used to do nothing at all while announcing a
 * penalty, so it is pinned explicitly rather than left to a general rule.
 */
const sleep = ms => new Promise(r => setTimeout(r, ms));
const until = async (fn, ms) => { const t0=Date.now();
  while (Date.now()-t0<ms) { try { if (fn()) return true; } catch(e){} await sleep(60);} return false; };
await until(() => typeof handleBank === 'function' && typeof runOppTurn === 'function', 15000);
const v = {};
const strip = t => t.replace(/\/\*[\s\S]*?\*\//g, '');

/* ── the player's shipped lines ── */
const pSrc = strip(handleBank.toString());
const pGrab = /var _chPenP=[\s\S]{0,300}?G\.pPts=Math\.max\(0,\(G\.pPts\|\|0\)-\(_chPenP-_chFromBankP\)\);/.exec(pSrc);
/* ── the rival's shipped lines ── */
const rSrc = strip(runOppTurn.toString());
const rGrab = /var _chFromBank=[\s\S]{0,240}?G\.oPts=Math\.max\(0,G\.oPts-\(penalty-_chFromBank\)\);/.exec(rSrc);
v._pFound = !!pGrab; v._rFound = !!rGrab;

/* CAPTURE ORIGINALS IN NAMED LOCALS, the same way the rival's runner does. A
   first version patched the generated source with a string .replace to recover
   the starting bank, which mangled the function and produced no output at all. */
function runPlayer(pool, bank, pen) {
  const f = new Function('pool','total','pen', `
    var _p0=total,_o0=pool;
    var G={pPts:pool,npcCardState:{challengePenalty:pen}};
    ${pGrab ? pGrab[0] : ''}
    return {pool:G.pPts, bank:total, lost:(_o0+_p0)-(G.pPts+total)};`);
  return f(pool, bank, pen);
}
function runRival(pool, bank, pen) {
  const f = new Function('pool','pts','effPen', `
    var _p0=pts,_o0=pool; var G={oPts:pool};
    var penalty=Math.min(effPen,G.oPts+pts);
    ${rGrab ? rGrab[0] : ''}
    return {pool:G.oPts, bank:pts, lost:(_o0+_p0)-(G.oPts+pts)};`);
  return f(pool, bank, pen);
}

const CASES = [[1000,200,500],[100,1000,500],[0,1000,500],[300,100,500],[1000,600,500]];
const rows = [];
let symmetric = true, exact = true;
for (const [pool,bank,pen] of CASES) {
  let p=null,r=null;
  try { p = runPlayer(pool,bank,pen); } catch(e){ v._pErr=String(e).slice(0,70); }
  try { r = runRival(pool,bank,pen); } catch(e){ v._rErr=String(e).slice(0,70); }
  const want = Math.min(pen, pool+bank);          /* capped at what they hold */
  if (!p || !r || p.lost !== r.lost) symmetric = false;
  if (!p || !r || p.lost !== want || r.lost !== want) exact = false;
  rows.push({in:[pool,bank,pen], want:want, player:p&&p.lost, rival:r&&r.lost});
}
v._rows = rows;
v.bothSeatsFound = !!pGrab && !!rGrab;
v.seatsAgree     = symmetric;
v.losesExactly   = exact;
/* the case that used to be a no-op */
const zero = rows.find(x => x.in[0] === 0);
v.emptyPoolStillCharges = !!zero && zero.player === 500 && zero.rival === 500;

const notes = {};
for (const k of Object.keys(v)) { if (k[0] === '_') { notes[k] = v[k]; delete v[k]; } }
return { verdict: v, notes: notes };
