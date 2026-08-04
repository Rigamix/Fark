/* apv_runscope_seam — matchArmed dispatches all three, and only when it should.
 *
 * P452 replaced three hand-written `if(...){G._x=true;famLog(...)}` stamps with
 * one _rsFire('matchArmed') over RSX. The three are independent - they write
 * three different flags and read none of each other's - so unlike the commit
 * hook there is no ordering or accumulation to verify. What there IS to verify
 * is that each still fires under exactly its old condition and stays silent
 * otherwise: a dispatch that quietly drops one card looks identical to a card
 * whose condition was false.
 */
const sleep = ms => new Promise(r => setTimeout(r, ms));
const until = async (fn, ms) => { const t0 = Date.now();
  while (Date.now() - t0 < ms) { try { if (fn()) return true; } catch(e){} await sleep(60); } return false; };

const ready = await until(() => typeof _rsFire === 'function' && typeof RSX === 'object', 15000);
if (!ready) return { err: 'the run-scoped seam is not defined' };
/* G IS NULL BETWEEN MATCHES - endMatch sets it so deliberately. Assign the
   binding directly: `window.G = {}` does not reach it, which the first run of
   this probe found by throwing on null. */
if (typeof G === 'undefined' || !G) { G = {}; }

const out = {};
function fire(plays, rung) {
  G._forKeeps = false; G._doubleStakes = false; G._highTable = false;
  G.rung = rung || {};
  _rsFire('matchArmed', { plays: plays });
  return { fk: !!G._forKeeps, ds: !!G._doubleStakes, ht: !!G._highTable };
}

out.none        = fire({}, {});
out.forKeeps    = fire({ for_keeps: true }, {});
out.doubleStakes= fire({ double_stakes: true }, {});
out.highTable   = fire({}, { _highTable: true });
out.allThree    = fire({ for_keeps: true, double_stakes: true }, { _highTable: true });

/* the table is the registry: a card silently missing from RSX would make its
   flag never set, and every check above would still pass for the others */
out.rsxCards = Object.keys(RSX).sort();
out.hooksPresent = Object.keys(RSX).filter(k => typeof RSX[k].matchArmed === 'function').length;

G._forKeeps = false; G._doubleStakes = false; G._highTable = false;

const eq = (a, b) => a.fk === b.fk && a.ds === b.ds && a.ht === b.ht;
return {
  ...out,
  verdict: {
    silentWithNothingArmed: eq(out.none, { fk: false, ds: false, ht: false }),
    forKeepsAlone:   eq(out.forKeeps,     { fk: true,  ds: false, ht: false }),
    doubleStakesAlone: eq(out.doubleStakes,{ fk: false, ds: true,  ht: false }),
    /* High Table reads G.rung, not ev.plays - it is not player-armed */
    highTableFromRung: eq(out.highTable,  { fk: false, ds: false, ht: true }),
    allThreeTogether: eq(out.allThree,    { fk: true,  ds: true,  ht: true }),
    allThreeRegistered: out.hooksPresent === 3,
    registryIsTheThree: out.rsxCards.join(',') === 'double_stakes,for_keeps,high_table'
  }
};
