/* NOTE 7 - taps should land above and below a die, but never across a lane.
 *
 * Denis: "Register my taps for each lane/die even if I tap a bit above or below
 * each die (not on the sides though), basically a taller hitbox."
 *
 * TWO CLAIMS THAT PULL IN OPPOSITE DIRECTIONS, so both are measured:
 *   TALLER   a tap above/below a die's painted box selects that die
 *   NOT WIDER a tap does not reach into a neighbour's lane
 * A pad that satisfied only the first would be an easy pass and a worse game.
 *
 * DRIVEN, NOT GEOMETRIC. The vertical claim is settled by dispatching a REAL tap
 * above a die and asking whether it became selected - the same route a finger
 * takes, through _dieTapRouter and toggleDie - rather than by reading a
 * bounding box and trusting it maps to behaviour.
 *
 * elementFromPoint IS used for the horizontal claim, because "does a lane steal"
 * is a question about hit-testing rather than about selection: a point just
 * inside die N+1's box must not resolve into die N's subtree.
 *
 * CONTROLS
 *   - a tap on a die's CENTRE selects it. If that fails the harness is broken
 *     and every reading below is noise.
 *   - the pad exists at all and has non-zero height, so "taps work above the
 *     die" cannot pass on a build where the pad never rendered.
 */
const sleep = ms => new Promise(r => setTimeout(r, ms));
const until = async (fn, ms) => { const t0 = Date.now();
  while (Date.now() - t0 < ms) { try { if (fn()) return true; } catch(e){} await sleep(50); } return false; };
const vis = el => { if (!el || !el.isConnected) return false;
  const s = getComputedStyle(el), r = el.getBoundingClientRect();
  return s.display !== 'none' && s.visibility !== 'hidden' && +s.opacity > 0.05 && r.width > 1 && r.height > 1; };
const tapEl = el => { if (!vis(el)) return false; const r = el.getBoundingClientRect();
  const o = {bubbles:true, cancelable:true, clientX:r.left+r.width/2, clientY:r.top+r.height/2};
  el.dispatchEvent(new PointerEvent('pointerdown',o)); el.dispatchEvent(new PointerEvent('pointerup',o));
  el.dispatchEvent(new MouseEvent('click',o)); return true; };
/* a tap at an arbitrary POINT, routed exactly as a finger would be */
function tapAt(x, y) {
  const el = document.elementFromPoint(x, y);
  if (!el) return null;
  const o = {bubbles:true, cancelable:true, clientX:x, clientY:y};
  el.dispatchEvent(new PointerEvent('pointerdown',o));
  el.dispatchEvent(new PointerEvent('pointerup',o));
  el.dispatchEvent(new MouseEvent('click',o));
  return el;
}

tapEl(document.getElementById('hsBtnBottom')); await sleep(1800);
await until(() => { const d = document.querySelector('.nrdie'); return d && d._floatDone; }, 9000);
tapEl(document.querySelector('.nrdie')); await sleep(1300);
tapEl(document.getElementById('nrTakeBtn')); await sleep(2200);
await until(() => [...document.querySelectorAll('.ptcard')].filter(vis).length > 0, 9000);
const pc = [...document.querySelectorAll('.ptcard')].filter(vis)[0]; if (pc) { tapEl(pc); await sleep(1700); }
const sit = [...document.querySelectorAll('span,div,button')].filter(e => vis(e) && e.children.length <= 1
  && /^SIT\s*DOWN$/i.test((e.textContent || '').trim()))[0];
if (sit) { tapEl(sit); if (sit.parentElement) tapEl(sit.parentElement); }
if (!(await until(() => vis(document.getElementById('screen-match')), 9000))
 || !(await until(() => typeof G !== 'undefined' && G && G.phase === 'idle', 30000))) {
  return { skip: 'setup did not reach an idle match' };
}

const v = {}, notes = {};
tapEl(document.getElementById('btnRoll'));
await until(() => G && (G.pool || []).length >= 2 && G.phase === 'choosing', 14000);
await sleep(1600);
const live = (G.pool || []).filter(d => !d.committed && d.el && d.el.isConnected);
if (live.length < 2) return { skip: 'need at least two live dice' };

const box = live[0].el.getBoundingClientRect();
const pad = live[0].el.querySelector('.die-hit');
const padBox = pad ? pad.getBoundingClientRect() : null;
notes._die = { w: +box.width.toFixed(1), h: +box.height.toFixed(1) };
notes._pad = padBox ? { h: +padBox.height.toFixed(1), w: +padBox.width.toFixed(1),
                        aboveDiePx: +(box.top - padBox.top).toFixed(1),
                        belowDiePx: +(padBox.bottom - box.bottom).toFixed(1) } : null;
/* CONTROL: the pad rendered and is taller than the die */
v.theHitPadExistsAndIsTaller = !!padBox && padBox.height > box.height + 10;
/* and is NOT wider - Denis's "not on the sides though", checked as geometry */
v.theHitPadIsNoWiderThanTheDie = !!padBox && padBox.width <= box.width + 1;

function selOf(d) { return !!d.sel; }
function clearSel() { (G.pool || []).forEach(d => { if (d.sel && !d.committed) { try { toggleDie(d); } catch (e) {} } }); }

/* CONTROL: a centre tap selects. If this fails nothing below means anything. */
clearSel(); await sleep(200);
const c = live[0].el.getBoundingClientRect();
tapAt(c.left + c.width / 2, c.top + c.height / 2);
await sleep(350);
v.aCentreTapSelectsTheDie = selOf(live[0]);
notes._centre = { selected: selOf(live[0]) };

/* THE FINDING: a tap ABOVE and BELOW the painted box selects the same die */
const ABOVE = 14, BELOW = 14;   /* px outside the die's own box */
clearSel(); await sleep(250);
const b1 = live[0].el.getBoundingClientRect();
tapAt(b1.left + b1.width / 2, b1.top - ABOVE);
await sleep(350);
const okAbove = selOf(live[0]);

clearSel(); await sleep(250);
const b2 = live[0].el.getBoundingClientRect();
tapAt(b2.left + b2.width / 2, b2.bottom + BELOW);
await sleep(350);
const okBelow = selOf(live[0]);

notes._vertical = { pxOutside: ABOVE, above: okAbove, below: okBelow };
v.aTapAboveTheDieSelectsIt = okAbove;
v.aTapBelowTheDieSelectsIt = okBelow;

/* THE OVER-CORRECTION CONTROL: a point inside the NEIGHBOUR's box must not
   hit-test into this die's subtree. Checked at the neighbour's own centre line
   and just inside its near edge. */
const A = live[0].el.getBoundingClientRect(), B = live[1].el.getBoundingClientRect();
function ownerAt(x, y) { const e = document.elementFromPoint(x, y); const d = e && e.closest && e.closest('.die'); return d; }
const nearEdgeX = (B.left < A.left) ? B.right - 3 : B.left + 3;
const o1 = ownerAt(B.left + B.width / 2, B.top + B.height / 2);
const o2 = ownerAt(nearEdgeX, B.top + B.height / 2);
notes._horizontal = { neighbourCentreOwnedBySelf: o1 === live[1].el,
                      neighbourNearEdgeOwnedBySelf: o2 === live[1].el };
v.aNeighboursLaneIsNotStolen = (o1 === live[1].el) && (o2 === live[1].el);

for (const k of Object.keys(v)) { if (k[0] === '_') { notes[k] = v[k]; delete v[k]; } }
return { verdict: v, notes: notes };
