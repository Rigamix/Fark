/* ZERO HOUR / CAST — does a keep worth nothing finish?
 *
 * Backlog 1 and 3. Plays a real match through the real entry chain (see
 * shoot_play.js — do not synthesise a screen), then brands a die that has
 * already been rolled: `ench.face` is set to the face the die actually came
 * up on, so the brand is live without touching the roll. Everything after
 * that is the game's own handlers, tapped through the DOM.
 *
 * Waiting for D3X to stop spinning is NOT waiting for the turn: the game
 * holds phase 'rolling' a little longer, and every handler in here returns
 * early during it. Wait for 'choosing'.
 *
 *   node tools/shoot.js --eval-file tools/shoot_zero_hour.js --out zh.png
 */
const sleep = ms => new Promise(r => setTimeout(r, ms));
const until = async (fn, ms) => { const t0 = Date.now();
  while (Date.now() - t0 < ms) { try { if (fn()) return true; } catch (e) {} await sleep(70); }
  return false; };
const trace = [];
const vis = el => {
  if (!el || !el.isConnected) return false;
  const s = getComputedStyle(el), r = el.getBoundingClientRect();
  return s.display !== 'none' && s.visibility !== 'hidden' && +s.opacity > 0.05
         && r.width > 1 && r.height > 1;
};
const screenNow = () => [...document.querySelectorAll('.screen')].filter(vis).map(e => e.id).join(',');
const tap = (el, why) => {
  if (!vis(el)) { trace.push('SKIP ' + why + ' (not visible)'); return false; }
  const r = el.getBoundingClientRect();
  const o = {bubbles:true, cancelable:true, clientX:r.left+r.width/2, clientY:r.top+r.height/2};
  el.dispatchEvent(new PointerEvent('pointerdown', o));
  el.dispatchEvent(new PointerEvent('pointerup', o));
  el.dispatchEvent(new MouseEvent('click', o));
  trace.push('tap ' + why);
  return true;
};

/* ── the entry chain, all of it load-bearing ── */
trace.push('start=' + screenNow());
tap(document.getElementById('hsBtnBottom'), 'NEW RUN');
await sleep(1800);
await until(() => { const d = document.querySelector('.nrdie'); return d && d._floatDone; }, 9000);
tap(document.querySelector('.nrdie'), 'focus offered die');
await sleep(1300);
tap(document.getElementById('nrTakeBtn'), 'TAKE IT');
await sleep(1900);
const patron = [...document.querySelectorAll('.ptcard')].filter(vis)[0];
if (patron) { tap(patron, 'patron'); await sleep(1700); }
const sit = [...document.querySelectorAll('span,div,button')]
  .filter(e => vis(e) && e.children.length <= 1 && /^SIT\s*DOWN$/i.test((e.textContent || '').trim()))[0];
if (sit) { tap(sit, 'SIT DOWN'); if (sit.parentElement) tap(sit.parentElement, 'SIT DOWN (parent)'); }
await until(() => vis(document.getElementById('screen-match')), 9000);
const ready = await until(() => typeof G !== 'undefined' && G && G.phase === 'idle', 14000);
trace.push('matchReady=' + ready + ' patron=' + (G && G.rung ? G.rung.name : '?'));

/* ── helpers ── */
const dis = id => { const e = document.getElementById(id); return e && e.classList.contains('disabled') ? 'off' : 'on'; };
const stat = () => ((document.getElementById('statusBot') || {}).textContent || '').trim() ||
                   ((document.getElementById('statusTop') || {}).textContent || '').trim();
const snap = label => ({ label, phase: G.phase,
  ROLL: dis('btnRoll'), BANK: dis('btnBank'),
  verb: ((document.getElementById('bankVerb') || {}).textContent || '').trim(),
  kept: G.kept.map(k => ({ vals: k.vals, pts: k.pts })),
  turnPts: G.turnPts, pPts: G.pPts, status: stat() });
/* brand the face the die is ALREADY showing: live brand, untouched roll */
const brand = d => { d.ench = { t: 'tithe', face: d.val }; try { reDrawDieFace(d); } catch (e) {} };
const freeDice = () => G.pool.filter(d => !d.committed);
const tapDie = d => tap(d.el, 'die val=' + d.val + (d.ench ? ' BRANDED' : ''));
const armTell = on => { if (on) G._tell = { id: 'last_call', name: 'ZERO HOUR', icon: '\u{1F37B}' };
                        else G._tell = null; };
/* roll and wait for the turn to actually be the player's again */
const rollAndSettle = async why => {
  tap(document.getElementById('btnRoll'), 'ROLL ' + why);
  const got = await until(() => G.phase === 'choosing' || G.phase === 'idle', 12000);
  await sleep(300);
  trace.push('settled(' + why + ')=' + got + ' phase=' + G.phase +
             ' vals=' + freeDice().map(d => d.val).join(''));
  return got;
};

const steps = [];
const errs = [];
window.addEventListener('error', e => errs.push(String(e.message)));
const gold0 = S.run.gold;

/* ═══ CASE 1 — CAST with no tell: fires, banks nothing, turn carries on ═══ */
armTell(false);
await rollAndSettle('case1');
const c1 = freeDice()[0];
brand(c1);
tapDie(c1);
await sleep(350);
steps.push(snap('C1 brand selected — want BANK=on verb=CAST'));
tap(document.getElementById('btnBank'), 'BANK/CAST');
await sleep(700);
steps.push(snap('C1 after CAST — want BANK=off ROLL=on, kept has no empty entry'));
const goldAfterC1 = S.run.gold;

/* ═══ CASE 2 — the reported bug. A branded keep is the turn's ONLY keep and
       Grog's tell says the turn is over, so there is nothing to bank. ═══ */
armTell(true);
const turn2 = G.turnNum;
const c2 = freeDice()[0];
if (!c2) steps.push({ label: 'C2 SKIPPED — no free die left' });
else {
  brand(c2);
  tapDie(c2);
  await sleep(350);
  steps.push(snap('C2 brand selected, tell armed'));
  tap(document.getElementById('btnBank'), 'BANK/CAST (arms Zero Hour)');
  await sleep(400);
  steps.push(snap('C2 mid beat — want ROLL=off BANK=off, status ZERO HOUR'));
  await sleep(1500);
  steps.push(snap('C2 after — want phase=opp, nothing banked'));
}

/* ═══ CASE 3 — Zero Hour on the ROLL commit, WITH points on the table.
       Should bank them and end the turn. ═══ */
const backP = await until(() => G.phase === 'idle' || G.phase === 'choosing', 90000);
trace.push('playerTurnAgain=' + backP + ' phase=' + G.phase + ' pPts=' + G.pPts);
let c3 = { label: 'C3 SKIPPED — never got the table back' };
if (backP) {
  armTell(true);
  await rollAndSettle('case3');
  const scorer = freeDice().find(d => d.val === 1 || d.val === 5);
  const other = freeDice().find(d => d !== scorer);
  if (!scorer || !other) steps.push({ label: 'C3 SKIPPED — roll had no lone scorer plus a spare' });
  else {
    const pts0 = G.pPts;
    tapDie(scorer);
    brand(other);
    tapDie(other);
    await sleep(350);
    steps.push(snap('C3 scorer + brand selected'));
    tap(document.getElementById('btnRoll'), 'ROLL (commit, arms Zero Hour)');
    await sleep(2200);
    steps.push(snap('C3 after — want phase=opp and pPts up from ' + pts0));
  }
}

return { trace, steps, errs,
  turnAdvancedAfterC2: G.turnNum > turn2,
  goldC1: goldAfterC1 - gold0, goldTotal: S.run.gold - gold0,
  zeroHourFlag: !!G._zeroHourEnds, rollLocked: !!G._rollLocked };
