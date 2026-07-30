/* BOTH ROWS, SAME METRICS, SEVERAL TURNS.
 *
 * Denis: "The NPC should have the exact same roll mechanics as me. THE SAME."
 * So measure them the same way and put the numbers side by side. One throw is
 * noisy - the physics is seeded off Math.random - so this walks several turns and
 * reports the WORST case each side ever reached, which is what a player notices.
 *
 * Reports per side: worst overlap between neighbouring dice, worst excursion past
 * the screen edge, and whether any die ever left the 430px screen.
 */
const sleep = ms => new Promise(r => setTimeout(r, ms));
const until = async (fn, ms) => { const t0 = Date.now();
  while (Date.now() - t0 < ms) { try { if (fn()) return true; } catch (e) {} await sleep(70); }
  return false; };
const vis = el => { if (!el || !el.isConnected) return false;
  const s = getComputedStyle(el), r = el.getBoundingClientRect();
  return s.display !== 'none' && s.visibility !== 'hidden' && +s.opacity > 0.05 && r.width > 1 && r.height > 1; };
const tap = (el) => { if (!vis(el)) return false;
  const r = el.getBoundingClientRect();
  const o = {bubbles:true, cancelable:true, clientX:r.left+r.width/2, clientY:r.top+r.height/2};
  el.dispatchEvent(new PointerEvent('pointerdown', o));
  el.dispatchEvent(new PointerEvent('pointerup', o));
  el.dispatchEvent(new MouseEvent('click', o)); return true; };

tap(document.getElementById('hsBtnBottom')); await sleep(1800);
await until(() => { const d = document.querySelector('.nrdie'); return d && d._floatDone; }, 9000);
tap(document.querySelector('.nrdie')); await sleep(1300);
tap(document.getElementById('nrTakeBtn')); await sleep(1900);
const p = [...document.querySelectorAll('.ptcard')].filter(vis)[0]; if (p) { tap(p); await sleep(1700); }
const sit = [...document.querySelectorAll('span,div,button')]
  .filter(e => vis(e) && e.children.length <= 1 && /^SIT\s*DOWN$/i.test((e.textContent||'').trim()))[0];
if (sit) { tap(sit); if (sit.parentElement) tap(sit.parentElement); }
await until(() => vis(document.getElementById('screen-match')), 9000);
await until(() => typeof G !== 'undefined' && G && G.phase === 'idle', 14000);

const SCREEN = window.innerWidth;
const seatOf = (el) => {
  const look = (arr) => { if (!arr) return undefined;
    for (const r of arr) if (r && r.el === el) return r.lane;
    return undefined; };
  let s = look(G.pool); if (s !== undefined) return s;
  s = look(G.oppDice); if (s !== undefined) return s;
  s = look(G._oppHeld); if (s !== undefined) return s;
  return null;
};
const measure = (rowId) => {
  const els = [...document.querySelectorAll('#' + rowId + ' .die')].filter(vis);
  if (!els.length) return null;
  const b = els.map(e => { const r = e.getBoundingClientRect();
      return { l: r.left, r: r.right, c: r.left + r.width / 2, seat: seatOf(e) }; })
    .sort((x, y) => x.c - y.c);
  const gaps = [];
  for (let i = 1; i < b.length; i++) gaps.push(+(b[i].l - b[i - 1].r).toFixed(1));
  const seats = b.map(x => x.seat);
  return { n: b.length, gaps, minGap: gaps.length ? Math.min(...gaps) : null,
    left: +b[0].l.toFixed(1), right: +b[b.length - 1].r.toFixed(1),
    offLeft: +Math.max(0, -b[0].l).toFixed(1),
    offRight: +Math.max(0, b[b.length - 1].r - SCREEN).toFixed(1),
    seats,
    seatsSorted: seats.every((v, i) => i === 0 || v === null || seats[i-1] === null || v >= seats[i-1]),
    seatsUnique: new Set(seats.map(String)).size === seats.length };
};
const acc = { player: [], opp: [] };
const record = (side, m) => { if (m && m.n > 1) acc[side].push(m); };

for (let turn = 0; turn < 3; turn++) {
  /* ── our turn ── */
  for (let g = 0; g < 8 && G.phase !== 'opp'; g++) {
    const rb = document.getElementById('btnRoll');
    if (!rb || rb.classList.contains('disabled') || !vis(rb)) break;
    tap(rb);
    await until(() => G.phase === 'choosing' || G.phase === 'idle' || G.phase === 'opp', 14000);
    await until(() => !(D3X.dice || []).some(d => d.roll), 12000);
    await sleep(650);
    record('player', measure('playerDiceRow'));
    if (G.phase === 'opp') break;
    const free = (G.pool || []).filter(d => !d.committed);
    const k = free.find(d => d.val === 1 || d.val === 5);
    if (k) { tap(k.el); await sleep(350); }
    const bb = document.getElementById('btnBank');
    if (k && vis(bb) && !bb.classList.contains('disabled') && g >= 1) { tap(bb); break; }
  }
  /* ── theirs ── */
  if (!(await until(() => G && G.phase === 'opp', 30000))) break;
  for (let s = 0; s < 30; s++) {
    await sleep(450);
    record('opp', measure('oppDiceRow'));
    if (G.phase !== 'opp') break;
  }
  if (!(await until(() => G && G.phase === 'idle', 40000))) break;
  await sleep(500);
}

const roll = (side) => {
  const a = acc[side];
  if (!a.length) return { samples: 0 };
  const worstGap = a.reduce((w, m) => (m.minGap !== null && (w === null || m.minGap < w) ? m.minGap : w), null);
  return {
    samples: a.length,
    worstOverlapPx: worstGap,
    everOverlapped: a.some(m => m.minGap !== null && m.minGap < 0),
    worstOffLeft: Math.max(...a.map(m => m.offLeft)),
    worstOffRight: Math.max(...a.map(m => m.offRight)),
    everOffScreen: a.some(m => m.offLeft > 0 || m.offRight > 0),
    seatsAlwaysSorted: a.every(m => m.seatsSorted),
    seatsAlwaysUnique: a.every(m => m.seatsUnique),
  };
};
return { screen: SCREEN, player: roll('player'), opp: roll('opp') };
