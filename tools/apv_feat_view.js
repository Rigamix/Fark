/* apv_feat_view — the feat view returns the same answers and refuses writes.
 *
 * P457 routed feat checks through _featView(G) instead of G. Two things have to
 * be true and they fail in opposite directions:
 *
 *   SAME ANSWERS. A view missing a field a check reads makes that feat silently
 *   stop firing - a feat that never awards is indistinguishable from a feat
 *   nobody earned. So every check is evaluated against the raw G and the view,
 *   on a fixture that turns each one ON, and the two must agree 23 for 23.
 *
 *   REFUSES WRITES. If the proxy does not throw, the enforcement is decorative
 *   and the invariant is still just discipline wearing a wrapper.
 *
 * AND THE HOLE IS ASSERTED AT ITS MEASURED SIZE. Seven checks read S.run
 * directly rather than through the argument, which a facade cannot stop. That
 * is a known gap, not a discovery - so this pins it: S.run must still be
 * writable (proving the gap is real and understood) while everything reached
 * THROUGH the view must not be. A test that pretended the gap was closed would
 * be worse than the gap.
 */
const sleep = ms => new Promise(r => setTimeout(r, ms));
const until = async (fn, ms) => { const t0 = Date.now();
  while (Date.now() - t0 < ms) { try { if (fn()) return true; } catch(e){} await sleep(60); } return false; };

const ready = await until(() => typeof _featView === 'function'
  && typeof FEATS !== 'undefined' && FEATS.length, 15000);
if (!ready) return { err: 'the feat view is not defined' };

/* a G with every feat condition satisfied at once - the point is agreement
   between two readings of the same state, not whether any given feat is true */
const fixture = {
  _isBoss: true, _famBankCount: 1, _famMinBank: 99999,
  _featBloom: 5, _featBusts: 0, _featJade: true, _featMaxBank: 99999,
  _featMaxDeficit: 99999, _featMaxRolls: 9, _featOmenTrue: true,
  _featShatterBanked: 3, _featStarChain: 3, _featSticky: true,
  _featWardSaves: 2, _forKeeps: true, _handicap: 'last_call', _sleeve: 'kindred',
  matchDice: ['bone', 'bone', 'bone', 'bone', 'bone', 'bone'],
  rung: { key: 'grog', name: 'GROG' }
};

const out = { disagree: [], threw: [] };
for (const f of FEATS) {
  if (typeof f.check !== 'function') continue;
  let raw, viewed;
  try { raw = !!f.check(fixture); } catch (e) { raw = 'threw:' + e.message.slice(0, 40); }
  try { viewed = !!f.check(_featView(fixture)); }
  catch (e) { viewed = 'threw:' + e.message.slice(0, 40); out.threw.push(f.id); }
  if (raw !== viewed) out.disagree.push({ id: f.id, raw: raw, viewed: viewed });
}
out.checked = FEATS.filter(f => typeof f.check === 'function').length;

/* the proxy must refuse */
const v = _featView(fixture);
let setThrew = false, delThrew = false;
try { v._isBoss = false; } catch (e) { setThrew = true; }
try { delete v._isBoss; } catch (e) { delThrew = true; }

/* and the copies must be copies - writing the array through the view must not
   reach the real one */
let arrFrozen = false;
try { v.matchDice.push('iron'); } catch (e) { arrFrozen = true; }
out.realDiceLen = fixture.matchDice.length;

/* THE KNOWN HOLE, pinned rather than pretended away: S.run is reachable as a
   global, so it stays writable. If this ever becomes false the gap closed and
   this probe should be updated deliberately, not silently. */
let sRunStillWritable = false;
try {
  if (typeof S !== 'undefined' && S) {
    S.run = S.run || {};
    S.run._probeCanary = 1;
    sRunStillWritable = S.run._probeCanary === 1;
    delete S.run._probeCanary;
  }
} catch (e) {}

return {
  ...out,
  setThrew, delThrew, arrFrozen, sRunStillWritable,
  verdict: {
    everyFeatAgrees:   out.disagree.length === 0,
    noneThrewThroughView: out.threw.length === 0,
    writeThrows:       setThrew === true,
    deleteThrows:      delThrew === true,
    arrayIsFrozenCopy: arrFrozen === true && out.realDiceLen === 6,
    /* documented gap, asserted at its size */
    knownHoleStillOpen: sRunStillWritable === true,
    checkedAllFeats:   out.checked === 23
  }
};
