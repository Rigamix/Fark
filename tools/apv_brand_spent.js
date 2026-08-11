/* NOTE 2 / OPEN 1i - a cast brand is spent for the turn.
 *
 * Denis ruled (a): make "this turn" TRUE. As shipped a brand could fire twice in
 * one turn, because hot dice rebuilds the pool and hands the same brand back
 * live - so the card's own promise was false as written.
 *
 * THE STATE IS KEYED ON THE ENCH OBJECT, not the lane, precisely so it survives
 * that rebuild. This probe therefore tests the rebuild directly rather than
 * trusting that reasoning: it fires a brand, then replaces the pool the way the
 * hot-dice branch does - fresh die objects carrying the SAME ench reference -
 * and asks whether the brand is still live.
 *
 * ARMS
 *   A  CONTROL: a fresh brand IS a live icon. If this fails the predicate is
 *      broken in the other direction and every "not live" below is meaningless.
 *   B  after firing, the same die is no longer a live icon
 *   C  THE HOT-DICE CASE: a NEW pool object carrying the same ench is also not
 *      live. This is the one the ruling exists for.
 *   D  the turn boundary clears it - the real startPTurn, not a hand reset
 *   E  CONTROL: a DIFFERENT brand on the table is untouched. A fix that marked
 *      every brand spent would pass A-D and break the game.
 *   F  the bust consequence, stated rather than discovered later: a row whose
 *      only live face is a spent brand no longer counts as having a legal keep.
 */
const sleep = ms => new Promise(r => setTimeout(r, ms));
const until = async (fn, ms) => { const t0 = Date.now();
  while (Date.now() - t0 < ms) { try { if (fn()) return true; } catch(e){} await sleep(60); } return false; };
const vis = el => { if (!el || !el.isConnected) return false;
  const s = getComputedStyle(el), r = el.getBoundingClientRect();
  return s.display !== 'none' && s.visibility !== 'hidden' && +s.opacity > 0.05 && r.width > 1 && r.height > 1; };
const tap = el => { if (!vis(el)) return false; const r = el.getBoundingClientRect();
  const o = {bubbles:true, cancelable:true, clientX:r.left+r.width/2, clientY:r.top+r.height/2};
  el.dispatchEvent(new PointerEvent('pointerdown',o)); el.dispatchEvent(new PointerEvent('pointerup',o));
  el.dispatchEvent(new MouseEvent('click',o)); return true; };

tap(document.getElementById('hsBtnBottom')); await sleep(1800);
await until(() => { const d = document.querySelector('.nrdie'); return d && d._floatDone; }, 9000);
tap(document.querySelector('.nrdie')); await sleep(1300);
tap(document.getElementById('nrTakeBtn')); await sleep(2200);
await until(() => [...document.querySelectorAll('.ptcard')].filter(vis).length > 0, 9000);
const pc = [...document.querySelectorAll('.ptcard')].filter(vis)[0]; if (pc) { tap(pc); await sleep(1700); }
const sit = [...document.querySelectorAll('span,div,button')].filter(e => vis(e) && e.children.length <= 1
  && /^SIT\s*DOWN$/i.test((e.textContent || '').trim()))[0];
if (sit) { tap(sit); if (sit.parentElement) tap(sit.parentElement); }
if (!(await until(() => vis(document.getElementById('screen-match')), 9000))
 || !(await until(() => typeof G !== 'undefined' && G && G.phase === 'idle', 30000))) {
  return { skip: 'setup did not reach an idle match' };
}

const v = {}, notes = {};
/* a real brand from the live catalogue, on a face the die is showing */
const TITHE = { t: 'tithe', face: 1 }, WARD = { t: 'ward', face: 5 };
notes._catalogue = { titheIsIcon: !!(window.ENCH_ICONS && ENCH_ICONS.tithe),
                     wardIsIcon: !!(window.ENCH_ICONS && ENCH_ICONS.ward) };
if (!notes._catalogue.titheIsIcon) return { skip: 'tithe is not an icon enchant here' };

function seed() {
  G._castEnch = [];
  G.phase = 'choosing';
  G.pool = [
    { lane: 0, val: 1, mat: 'bone', ench: TITHE, sel: false, committed: false, el: document.createElement('div') },
    { lane: 1, val: 5, mat: 'bone', ench: WARD,  sel: false, committed: false, el: document.createElement('div') },
    { lane: 2, val: 3, mat: 'bone', ench: null,  sel: false, committed: false, el: document.createElement('div') },
  ];
  return G.pool;
}

/* A - CONTROL: fresh brands are live */
let p = seed();
v.aFreshBrandIsALiveIcon = _dieIsIcon(p[0]) === true && _dieIsIcon(p[1]) === true;
notes._armA = { tithe: _dieIsIcon(p[0]), ward: _dieIsIcon(p[1]), plain: _dieIsIcon(p[2]) };

/* B - fire it, and it stops being live */
try { _iconFire(p[0], 'p'); } catch (e) { notes._fireErr = String(e).slice(0, 90); }
notes._armB = { spent: _brandSpent(p[0]), stillIcon: _dieIsIcon(p[0]),
                classOnDie: p[0].el.className, castCount: (G._castEnch || []).length };
v.aFiredBrandIsNoLongerALiveIcon = _dieIsIcon(p[0]) === false;
v.theDieCarriesTheSpentClass = /brand-spent/.test(p[0].el.className);

/* C - THE HOT-DICE CASE. Rebuild the pool the way that branch does: brand new
       die objects, same ench reference, fresh elements. */
const rebuilt = { lane: 0, val: 1, mat: 'bone', ench: TITHE, sel: false, committed: false,
                  el: document.createElement('div') };
G.pool = [rebuilt, p[1], p[2]];
notes._armC = { sameEnchRef: rebuilt.ench === TITHE, stillIcon: _dieIsIcon(rebuilt) };
v.aRebuiltDieWithTheSameBrandIsAlsoSpent = _dieIsIcon(rebuilt) === false;

/* E - CONTROL: the OTHER brand is untouched. A blanket fix passes everything
       above and ruins the game. */
v.aDifferentBrandIsUntouched = _dieIsIcon(p[1]) === true;

/* F - the consequence, asserted rather than left to be discovered: with only a
       spent brand live, the row has no legal keep. */
G.pool = [rebuilt];
notes._armF = { iconOnTable: _iconOnTable(G.pool) };
v.aSpentBrandNoLongerRescuesTheRow = _iconOnTable(G.pool) === false;

/* D - the real turn boundary clears it */
seed();
try { _iconFire(G.pool[0], 'p'); } catch (e) {}
const beforeTurn = _brandSpent(G.pool[0]);
try { startPTurn(); } catch (e) { notes._turnErr = String(e).slice(0, 90); }
await sleep(800);
const probe = { lane: 0, val: 1, mat: 'bone', ench: TITHE, ench2: null };
notes._armD = { spentBefore: beforeTurn, castArrAfter: (G._castEnch || []).length,
                liveAfter: _dieIsIcon(probe) };
v.theTurnBoundaryClearsIt = beforeTurn === true && _dieIsIcon(probe) === true;

for (const k of Object.keys(v)) { if (k[0] === '_') { notes[k] = v[k]; delete v[k]; } }
return { verdict: v, notes: notes };
