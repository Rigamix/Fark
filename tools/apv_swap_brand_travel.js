/* D11 / OPEN section 9 - a swapped or downgraded die leaves its brand on the seat.
 *
 * Denis ruled: THE BRAND TRAVELS WITH THE DIE, matching Trade (18750,
 * `G._enchArr[L]=null` on the way out). His reasoning is the measurement this
 * probe has to make visible: leaving the brand behind means Sticky Fingers
 * LAUNDERS a bad die - the player hands over a jade, receives a bone, and keeps
 * the jade's Tithe on the seat. Strictly better for the player than the card's
 * own name suggests.
 *
 * TWO LIVE SITES, both guaranteed boss cards, both driven here through the real
 * startPTurn:
 *   A  sticky_fingers_die  best_for_worst  25494  - Finnick's cardPool[0]
 *   B  collateral_die      downgrade_best  25508  - Corvus's pool
 *
 * TWO CONTROLS, and the second is the one that matters:
 *   C  THE SWAP ACTUALLY HAPPENED. matchDice must change and usedOnce must
 *      increment. Without this, "the brand is still there" is indistinguishable
 *      from "the card never fired" - the shape that made apv_reroll_kept_split
 *      pass green against a broken build earlier in this investigation.
 *   D  AN UNTOUCHED LANE KEEPS ITS BRAND. A fix that cleared the whole array
 *      would pass A and B and quietly delete every other brand on the table.
 *
 * NOT DRIVEN, and stated rather than implied: three more copies of the same
 * body exist at 30489 (_npcEndOfTurnActives), 32368 (activateSleightOfHand) and
 * 32664/32677 (activateStickyFingersPlayer / activateCollateralPlayer). All
 * three are unreachable today - `sleight_of_hand` carries dep:true and sits in
 * no cardPool, and sticky_fingers_die/collateral_die carry npcOnly:true, which
 * every player draft pool filters out (33987, 33992, 33993, 35295, 35550). They
 * are patched anyway: both npcOnly cards already ship a `playerDesc` written
 * for the player's hand, so the dead path is a landmine, not a dead end.
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
const TITHE = { t: 'tithe', face: 1 }, SEAL = { t: 'seal', face: 3 }, WARD = { t: 'ward', face: 5 };
const brandOf = e => (e && e.t) || null;

/* the block under test lives inline in startPTurn behind `Math.random()>0.5`
   and `G.turnNum >= 2`, so each arm re-seeds and re-fires until usedOnce says
   the card went off. The attempt count is reported: "did not fire" in three
   tries would prove nothing. */
async function drive(cid, matchDice, budget) {
  let n = 0;
  for (; n < budget; n++) {
    G.matchDice    = matchDice.slice();
    G.matchOppDice = ['bone','bone','bone','bone','bone','flint'];
    /* lane 0 always moves; lane 1 moves under collateral only; lane 5 never
       moves under either card. One seed, so the same array proves both the
       finding and control D. */
    G._enchArr     = [TITHE, SEAL, null, null, null, WARD];
    G.oCards       = [cid];
    G.pCards       = [];                                       /* no iron_grip */
    G.npcCardState = G.npcCardState || {};
    G.npcCardState.usedOnce = {};
    G.turnNum = 6;
    if (G.rung) G.rung._coldShoulder = false;
    try { startPTurn(); } catch (e) { notes['_err_' + cid] = String(e).slice(0, 90); }
    await sleep(120);
    if (G.npcCardState.usedOnce[cid]) break;
  }
  return { attempts: n + 1, fired: !!(G.npcCardState.usedOnce || {})[cid],
           matchDice: (G.matchDice || []).slice(0, 6),
           brands: (G._enchArr || []).slice(0, 6).map(brandOf) };
}

/* A - Finnick swaps your best die away. Lane 0 jade is the unique best. */
const A = await drive('sticky_fingers_die', ['jade','bone','bone','bone','bone','flint'], 40);
notes._armA = A;

/* B - Corvus downgrades your two best to bone. Lanes 0 and 1. */
const B = await drive('collateral_die', ['jade','starstone','bone','bone','bone','flint'], 40);
notes._armB = B;

/* C - CONTROL: the cards actually fired and actually moved a die. */
v.stickyFingersActuallyFired  = A.fired && A.matchDice[0] !== 'jade';
v.collateralActuallyFired     = B.fired && B.matchDice[0] === 'bone' && B.matchDice[1] === 'bone';

/* the finding: does the brand leave with the die? */
v.stickyFingersBrandTravels   = A.brands[0] === null;
v.collateralBrandTravels      = B.brands[0] === null && B.brands[1] === null;

/* D - CONTROL: a lane the card did not touch keeps its brand. Lane 5 under
      both cards, and lane 1 under Sticky Fingers, which only moves lane 0. A
      fix that cleared the array wholesale would pass every arm above. */
v.untouchedLaneKeepsItsBrand  = A.brands[5] === 'ward' && B.brands[5] === 'ward' && A.brands[1] === 'seal';

for (const k of Object.keys(v)) { if (k[0] === '_') { notes[k] = v[k]; delete v[k]; } }
return { verdict: v, notes: notes };
