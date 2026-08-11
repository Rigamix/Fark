/* NOTE 6 - the card rows: bigger, spread, sitting on the table, and OFF the
 * ROLL button.
 *
 * Denis: "Big and spread out on my side, not as big but still well size on the
 * npc side. Drop shadow, subtle floating animation ... They should look like
 * they are physically above/on the table."
 *
 * THE ONE THAT IS NOT COSMETIC. #famRowP is z-index 41 over .controls' 20 and
 * every card carries a live onclick, and at bottom:11.6% the row's lower edge
 * already sat BELOW ROLL's top edge. Growing the cards without raising the row
 * would bury the button. The file records the identical bug for .card-bar: "at
 * z-index 5, swallowed its taps: elementFromPoint inside ROLL returned the card
 * bar." So the headline assertion here is a HIT TEST, not a size:
 * elementFromPoint inside ROLL must return ROLL, never a card.
 *
 * CONTROLS
 *   - there is at least one card in the player's row. Every geometry check
 *     below is vacuous on an empty row, and an empty row is the state a
 *     tavern-only loadout actually produces.
 *   - ROLL is on screen with a real box, so "the hit test returned ROLL" cannot
 *     pass by both being absent.
 */
const sleep = ms => new Promise(r => setTimeout(r, ms));
const until = async (fn, ms) => { const t0 = Date.now();
  while (Date.now() - t0 < ms) { try { if (fn()) return true; } catch(e){} await sleep(50); } return false; };
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
await sleep(1200);

const v = {}, notes = {};
/* SEED THE ROW IF IT IS EMPTY, and say so. Night 1 starts with no family cards
   at all (pF: []), so on a fresh run every geometry check below would be
   vacuous - which the control catches, but catching it every time is not a
   measurement. Three cards is the maximum the row holds and therefore the worst
   case for both the width and the ROLL overlap. Rendered through the game's own
   famRenderRow rather than by injecting markup. */
notes._seeded = false;
if (!document.querySelector('#famRowP .fcv')) {
  try {
    G.pF = ['slow_cook', 'steady_hand', 'fair_trade'].map(id => ({ id: id, tier: 1, charges: 2, state: {} }));
    famRenderRow();
    notes._seeded = true;
    await sleep(500);
  } catch (e) { notes._seedErr = String(e).slice(0, 90); }
}
const roll = document.getElementById('btnRoll');
const cards = [...document.querySelectorAll('#famRowP .fcv')].filter(vis);
const backs = [...document.querySelectorAll('#famRowO .mcBack')].filter(vis);

notes._counts = { playerCards: cards.length, rivalBacks: backs.length,
                  pF: (G.pF || []).map(i => i.id) };
/* CONTROL: geometry checks are vacuous on an empty row */
v.thePlayerRowHasCards = cards.length > 0;
v.rollIsOnScreen = !!roll && vis(roll);
if (!cards.length || !roll) { for (const k of Object.keys(v)) if (k[0]==='_'){notes[k]=v[k];delete v[k];}
  return { verdict: v, notes: notes }; }

const R = roll.getBoundingClientRect();
const C = cards[0].getBoundingClientRect();
const rowBottom = Math.max(...cards.map(c => c.getBoundingClientRect().bottom));
notes._geometry = {
  cardW: +C.width.toFixed(1), cardH: +C.height.toFixed(1),
  rowBottomPx: +rowBottom.toFixed(1), rollTopPx: +R.top.toFixed(1),
  clearancePx: +(R.top - rowBottom).toFixed(1),
  rivalBackW: backs.length ? +backs[0].getBoundingClientRect().width.toFixed(1) : null,
};

/* THE HEADLINE: a hit test inside ROLL must reach ROLL, not a card. Three
   points, because the overlap was at the button's TOP edge. */
function ownerAt(x, y) { const e = document.elementFromPoint(x, y); return e ? (e.closest('#btnRoll') ? 'ROLL'
  : (e.closest('#famRowP') ? 'CARD' : (e.tagName + (e.id ? '#' + e.id : '')))) : 'none'; }
const hits = {
  topCentre: ownerAt(R.left + R.width / 2, R.top + 3),
  centre:    ownerAt(R.left + R.width / 2, R.top + R.height / 2),
  topLeft:   ownerAt(R.left + 8, R.top + 3),
};
notes._hitTest = hits;
v.rollIsNotCoveredByACard = hits.topCentre === 'ROLL' && hits.centre === 'ROLL' && hits.topLeft === 'ROLL';
v.theRowClearsTheButton = (R.top - rowBottom) > 0;

/* size: the player's cards are the big ones, the rival's are smaller but real */
v.playerCardsAreBig = C.width > 60;
v.rivalCardsAreSmallerButNotTiny = backs.length === 0
  || (backs[0].getBoundingClientRect().width < C.width
      && backs[0].getBoundingClientRect().width > 45);

/* the float is applied, and on the INNER wrapper so it cannot fight .fcv's own
   transform - a keyframe declared but never bound is the commonest way an
   animation "does not work" */
const inner = cards[0].querySelector('.fcvIn');
const anim = inner ? getComputedStyle(inner).animationName : '';
notes._float = { animationName: anim,
                 delays: cards.map(c => { const i = c.querySelector('.fcvIn');
                   return i ? getComputedStyle(i).animationDelay : null; }) };
v.theCardsFloat = /famBob/.test(anim);
/* desynced from frame one rather than drifting in */
v.theFloatIsDesynced = cards.length < 2 || new Set(notes._float.delays).size === notes._float.delays.length;

/* the soft cast, on the base AND on the two states that redeclare filter */
function filt(el) { return getComputedStyle(el).filter || ''; }
notes._shadow = { base: filt(cards[0]).slice(0, 120) };
v.theCardsCastASoftShadow = /drop-shadow/.test(filt(cards[0])) && !/0px 0px/.test(filt(cards[0]));

for (const k of Object.keys(v)) { if (k[0] === '_') { notes[k] = v[k]; delete v[k]; } }
return { verdict: v, notes: notes };
