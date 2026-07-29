/* PLAY THE GAME. Do not build a game state by hand.
 *
 * Every time I have synthesised one (showScreen('match',{rung:...}),
 * launchSeat(), poking S.run) I have ended up photographing a game that is
 * not the one being played: a boss screen carrying old imagery, a fresh
 * profile still on the default 2D dice, a night that was never set up. The
 * real UI is the only thing that knows the real entry path.
 *
 * So this clicks: settings -> dice to 3D -> back -> NEW RUN -> first seat ->
 * ROLL. It reports what it saw at each step so a wrong turn is visible in the
 * log rather than silently photographed.
 *
 *   node tools/shoot.js --eval-file tools/shoot_play.js --out play.png
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
/* a real tap: the game binds onclick, and some handlers check pointer state */
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
const byText = (sel, txt) => [...document.querySelectorAll(sel)]
  .filter(e => vis(e) && (e.textContent || '').trim().toUpperCase().includes(txt.toUpperCase()))[0];

trace.push('start=' + screenNow());

/* ── NEW RUN. It is #hsBtnBottom, not #hsBtnTop, and the run starts from the
   menu directly - there is no dice-style choice to make: the 2D/3D toggle in
   the markup is vestigial and gates nothing. ── */
tap(document.getElementById('hsBtnBottom') ||
    byText('.hsBtn, [onclick]', 'NEW RUN'), 'NEW RUN');
await sleep(1800);
trace.push('afterNewRun=' + screenNow());

/* ── whatever the run screen offers: keep taking the first live control until
   a match opens. Logs every choice so a wrong turn shows up in the trace
   rather than being silently photographed. ── */
for (let step = 0; step < 8; step++) {
  if (vis(document.getElementById('screen-match'))) break;
  const here = screenNow();
  const cands = [...document.querySelectorAll('[onclick]')].filter(el => {
    if (!vis(el)) return false;
    const r = el.getBoundingClientRect();
    if (r.top > window.innerHeight || r.bottom < 0) return false;   /* below the fold */
    const oc = el.getAttribute('onclick') || '';
    return !/hideRenownInfo|togglePouch|closeSettings|resetRun|_gbRules|_gbSettings|toggleAudio|toggleSetting/.test(oc);
  });
  if (!cands.length) { trace.push('step' + step + ' nothing tappable on ' + here); break; }
  const go = cands.find(e => /launchSeat|Seat|PLAY|SIT|BEGIN|_gbSeat/i.test(
      (e.getAttribute('onclick') || '') + ' ' + (e.textContent || ''))) || cands[0];
  tap(go, 'step' + step + ' on ' + here + ' -> ' + (go.id || (go.getAttribute('onclick') || '').slice(0, 30)));
  await sleep(1700);
}
trace.push('beforeMatch=' + screenNow());

/* ── 4. roll ── */
const ok = await until(() => typeof G !== 'undefined' && G && G.phase === 'idle', 14000);
trace.push('matchReady=' + ok + ' phase=' + (typeof G !== 'undefined' && G ? G.phase : 'noG'));
if (ok) {
  tap(document.getElementById('btnRoll'), 'ROLL');
  await until(() => document.querySelectorAll('#playerDiceRow .die').length > 0, 6000);
  await until(() => window.D3X && D3X.dice.length >= 1, 9000);
  await until(() => !D3X.dice.some(d => d.roll), 9000);
  await sleep(500);
}

const sc = document.getElementById('screen-match');
return { trace,
  rung: (typeof G !== 'undefined' && G && G.rung) ? G.rung.name : null,
  diceStyle: S.settings && S.settings.diceStyle,
  bg: sc ? getComputedStyle(sc, '::before').backgroundImage.split('/').pop().replace(/["')]+$/, '') : null,
  domDice: document.querySelectorAll('#playerDiceRow .die').length,
  meshes: window.D3X ? D3X.dice.length : -1,
  vals: [...document.querySelectorAll('#playerDiceRow .die')].map(e => e._trueVal) };
