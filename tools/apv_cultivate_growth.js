/* D16 - Cultivate says "for the rest of the match. Stacks." and stored the
 * growth on the POOL DIE OBJECT (`d._cult`), which every turn boundary replaces.
 *
 * THE MEASUREMENT READS BOTH STORES, old and new, and that is deliberate: a
 * probe that only knew about G._cultArr would report the pre-patch build as
 * "no growth anywhere" - true, but for the wrong reason, and it would read
 * identically to a build where the effect had been deleted outright. Reading
 * both is what makes the before/after pair mean something.
 *
 * SEVEN ARMS. Two are controls against a broken instrument, two against an
 * over-correction:
 *
 *   A  CONTROL, the mechanism. Commit the same dice twice; the second commit
 *      must pay 50 per jade die. A probe reporting "no growth" without this arm
 *      cannot be told apart from one that never fired the hook - the shape that
 *      made apv_reroll_kept_split pass green against a broken build.
 *   B  WHERE IT LIVES. Carriers on the pool objects vs on G.
 *   C  THE TURN BOUNDARY. Drive the game's own startPTurn and count what is
 *      still reachable. This was the defect: 0.
 *   D  THE SNAPSHOT. saveMatchState, then look in S.pendingMatch.
 *   E  CONTROL, THE ONLY PATH THAT EVER PAID. powder_keg.use un-commits in
 *      place (the same objects), and it is the only un-commit in the file that
 *      does not then discard the pool - so before this fix it was the sole
 *      route by which Cultivate had ever scored a point. It must still work.
 *   F  IT TRAVELS. Drive Finnick's real Sticky Fingers over a grown lane: the
 *      growth leaves with the die, and a lane the card did not touch keeps its
 *      own. Denis's OPEN 9 ruling, applied to the second per-die fact.
 *   G  IT SPLICES. Remove a lane between two grown lanes and the survivors must
 *      slide down with their dice, not stay behind on the wrong seats.
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

/* ── the growth counter. Bounded, cycle-guarded, and it must never walk into a
      DOM node: every pool die carries `el` and the element graph is unbounded.
      Counts BOTH stores so the same file measures both builds. ── */
function cultIn(root, label) {
  const seen = new Set(); let total = 0, sites = [];
  (function walk(o, path, depth) {
    if (!o || depth > 5 || typeof o !== 'object') return;
    if (o.nodeType !== undefined || seen.has(o)) return;
    seen.add(o);
    for (const k of Object.keys(o)) {
      let val; try { val = o[k]; } catch (e) { continue; }
      if (k === '_cult') { total += (val || 0); sites.push(path + '._cult=' + val); continue; }
      if (k === '_cultArr' && Array.isArray(val)) {
        const sum = val.reduce((a, n) => a + (n || 0), 0);
        if (sum > 0) { total += sum; sites.push(path + '._cultArr=[' + val.join(',') + ']'); }
        continue;
      }
      if (val && typeof val === 'object' && val.nodeType === undefined) walk(val, path + '.' + k, depth + 1);
    }
  })(root, label, 0);
  return { total: total, sites: sites.slice(0, 8), n: sites.length };
}
/* one die's growth, whichever build this is */
const growthAt = d => (G._cultArr && typeof d.lane === 'number' ? (G._cultArr[d.lane] || 0) : 0) || (d._cult || 0);

/* ── a fresh table of six with three jade dice showing a triple ── */
function seed() {
  G.pF = [{ id: 'cultivate', tier: 1, state: {} }];
  G._cultArr = [];
  G.pool = [3,3,3,2,4,6].map((val, i) => ({ lane: i, val: val, mat: i < 3 ? 'jade' : 'bone',
    ench: null, sel: false, committed: false, _frozen: false, el: document.createElement('div') }));
  return G.pool.slice(0, 3);            /* the three jade dice */
}
const BASE = 100;                        /* famCommitBonus returns pts, so the growth is the delta */

/* A - the mechanism */
const jade = seed();
const a1 = famCommitBonus(jade, BASE);
const a2 = famCommitBonus(jade, BASE);
notes._armA = { firstCommit: a1, secondCommit: a2, growthPaid: a2 - BASE,
                growth: jade.map(growthAt), lanes: jade.map(d => d.lane) };
v.growthPaysWhenTheObjectSurvives = (a2 - BASE) === 150;   /* 3 jade x 50 */

/* B - where the growth is stored, right after a stamping commit */
seed();
famCommitBonus(G.pool.slice(0, 3), BASE);
const onPool = cultIn(G.pool, 'pool'), onG = cultIn(G, 'G');
notes._armB = { poolCarriers: onPool.n, poolTotal: onPool.total,
                gTotal: onG.total, gSites: onG.sites };
v.growthIsStamped = onG.total > 0;       /* control: the stamp landed at all */

/* C - THE DEFECT. The game's own turn boundary. */
let boundary = 'startPTurn';
try { startPTurn(); } catch (e) { boundary = '_turnTableClear (' + String(e).slice(0,60) + ')';
                                  try { _turnTableClear(); } catch (e2) {} }
await sleep(900);
const afterTurn = cultIn(G, 'G');
notes._armC = { boundaryDriven: boundary, reachableAfter: afterTurn.total,
                carriers: afterTurn.n, sites: afterTurn.sites, poolLen: (G.pool || []).length };
v.growthSurvivesTheTurnBoundary = afterTurn.total > 0;

/* D - the snapshot. Fresh stamp, since C just cleared the table.
     WITH A SENTINEL BRAND, and that control is load-bearing. saveMatchState
     wraps its whole body in a try/catch that swallows, behind an early return
     on `!S.pendingMatch || G._practice` - so "the growth is not in the
     snapshot" and "saveMatchState did nothing at all" produce the identical
     reading. The brand rides along on the line directly above the growth's, so
     if the brand lands and the growth does not, the patch is wrong; if neither
     lands, the arm measured nothing and says so. */
seed();
G._enchArr = [{ t: 'tithe', face: 1 }, null, null, null, null, null];
famCommitBonus(G.pool.slice(0, 3), BASE);
try { saveMatchState(); } catch (e) { notes._saveErr = String(e).slice(0, 80); }
const _pm = (typeof S !== 'undefined' && S && S.pendingMatch) || {};
const snap = cultIn(_pm, 'pendingMatch');
const brandLanded = !!(_pm._enchArr && _pm._enchArr[0] && _pm._enchArr[0].t === 'tithe');
notes._armD = { inSnapshot: snap.total, carriers: snap.n, sites: snap.sites,
                snapshotExists: !!(typeof S !== 'undefined' && S && S.pendingMatch),
                saveMatchStateRan: brandLanded, cultArrOnG: (G._cultArr || []).slice(0, 3),
                cultArrInSnapshot: (_pm._cultArr || null), practice: !!(G && G._practice) };
v.saveMatchStateActuallyRan = brandLanded;   /* control */
v.growthIsInTheSnapshot = snap.total > 0;

/* E - CONTROL. Only the survival is read: the keg rerolls every face, so
       re-committing would measure the dice rather than the store. */
const kegJade = seed();
famCommitBonus(kegJade, BASE);
const beforeKeg = kegJade.map(growthAt);
try { CFX.powder_keg.use({ id: 'powder_keg', tier: 1, state: {} }); }
catch (e) { notes._kegErr = String(e).slice(0, 80); }
const afterKeg = kegJade.map(growthAt);
notes._armE = { beforeKeg: beforeKeg, afterKeg: afterKeg,
                sameObjects: kegJade.every(d => (G.pool || []).indexOf(d) >= 0) };
v.growthSurvivesPowderKeg = afterKeg.every(n => n > 0);

/* F - it travels, driven through Finnick's real card rather than the helper.
       Lane 0 is the unique best die AND the grown one; lane 5 is neither. */
let fFired = false, fN = 0;
for (; fN < 40 && !fFired; fN++) {
  G.matchDice = ['jade','bone','bone','bone','bone','flint'];
  G.matchOppDice = ['bone','bone','bone','bone','bone','bone'];
  G._cultArr = [150, 0, 0, 0, 0, 250];
  G.oCards = ['sticky_fingers_die']; G.pCards = [];
  G.npcCardState = G.npcCardState || {}; G.npcCardState.usedOnce = {};
  G.turnNum = 6; if (G.rung) G.rung._coldShoulder = false;
  try { startPTurn(); } catch (e) { notes._fErr = String(e).slice(0, 80); }
  await sleep(120);
  fFired = !!G.npcCardState.usedOnce['sticky_fingers_die'];
}
notes._armF = { attempts: fN, fired: fFired, matchDice: (G.matchDice || []).slice(0, 6),
                growth: (G._cultArr || []).slice(0, 6) };
v.stickyFingersActuallyFired = fFired && G.matchDice[0] !== 'jade';   /* control */
v.growthTravelsWithTheDie    = (G._cultArr || [])[0] === 0;
v.untouchedLaneKeepsItsGrowth = (G._cultArr || [])[5] === 250;        /* over-correction control */

/* G - it splices. Remove the middle of three grown lanes. */
G.matchDice = ['jade','bone','jade','bone','bone','bone'];
G._enchArr = [null, null, null, null, null, null];
G._cultArr = [100, 0, 300, 0, 0, 0];
G.pool = []; G.numDice = 6;
try { _removeDieAt(1); } catch (e) { notes._gErr = String(e).slice(0, 80); }
notes._armG = { matchDice: (G.matchDice || []).slice(), growth: (G._cultArr || []).slice() };
v.growthSlidesWithItsSeat = (G._cultArr || [])[0] === 100 && (G._cultArr || [])[1] === 300
                            && (G.matchDice || [])[1] === 'jade';

/* H - Trade is the other card whose own comment says "the brand leaves with the
       die", and it clears the seat by hand rather than through the helper. If
       growth stayed behind, the rival's die would inherit it - the same
       laundering, one card over. Driven through the real handler, not the
       helper it now calls.
       THE CATALOGUE IS `ENCH_ICONS`, NOT `ENCHANTS`. Measured, after this arm
       first threw on ENCHANTS.trade: ENCH_ICONS carries the full enchant
       definitions (name/price/glyph/desc/fire) and ENCHANTS holds exactly one
       key, `quicksilver`. The name is a leftover; the control below is what
       turned a silent "growth did not move" into a visible wrong-object. */
G.matchDice    = ['jade','bone','bone','bone','bone','bone'];
G.matchOppDice = ['starstone','bone','bone','bone','bone','bone'];
G._enchArr     = [{ t: 'trade', face: 2 }, null, null, null, null, null];
G._cultArr     = [400, 0, 0, 0, 0, 700];
G._tradeSwaps  = [];
try { ENCH_ICONS.trade.fire({ lane: 0, side: 'p' }); } catch (e) { notes._hErr = String(e).slice(0, 90); }
notes._armH = { matchDice: (G.matchDice || []).slice(0, 2), growth: (G._cultArr || []).slice(0, 6),
                brand: (G._enchArr || [])[0] };
v.tradeActuallySwapped        = G.matchDice[0] === 'starstone';   /* control */
v.growthLeavesOnATrade        = (G._cultArr || [])[0] === 0;
v.tradeLeavesOtherLanesAlone  = (G._cultArr || [])[5] === 700;    /* over-correction control */

for (const k of Object.keys(v)) { if (k[0] === '_') { notes[k] = v[k]; delete v[k]; } }
return { verdict: v, notes: notes };
