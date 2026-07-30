/* FIRST STRIKE, on the route it was shipped for and the one it could never
 * reach before: a SEALED seat.
 *
 * The badge's id (in_arrears) was REUSED by the new rule while still sitting in
 * _RETIRED_RULES, whose guard passes only the seat's own tell. So a sealed or
 * sleeved First Strike returned false and the reveal never opened. P367 released
 * the id and moved the gate onto _ruleActive.
 *
 * This proves both directions in one run: put the id back in the retired list and
 * the rule goes dead again, take it out and it fires. Plus the two other halves
 * of the downgrade - it is the PLAYER's reveal only, and In Arrears' debt chip is
 * gone from a badge that no longer touches gold.
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

const out = { seatTellId: G._tell ? G._tell.id : null };

/* ── the gate, both ways ── */
G._sealRule = 'in_arrears';           // a SEALED seat carrying First Strike
G._sleeve = null;
const wasTell = G._tell;
G._tell = { id: 'drill_order', name: 'DRILL ORDER' };  // NOT the seat's own tell

out.sealedActive_now = _ruleActive('in_arrears', 'p');
_RETIRED_RULES.in_arrears = 1;                          // put the guard back
out.sealedActive_ifStillRetired = _ruleActive('in_arrears', 'p');
delete _RETIRED_RULES.in_arrears;                       // and take it off again

/* confession/counterfeit must STILL be blocked - their old behaviour is live */
out.confessionStillBlocked = !_ruleActive('confession', 'p');
out.counterfeitStillBlocked = !_ruleActive('counterfeit', 'p');

/* ── the reveal actually opens, from the sealed seat ── */
G._firstStrikeOpen = false;
const box0 = document.getElementById('fsReveal');
out.revealBefore = !!(box0 && vis(box0));
_firstStrike('p');
await sleep(500);
const box = document.getElementById('fsReveal');
out.revealOpened = !!(box && vis(box));
out.revealShowsBothRows = box ? (box.querySelectorAll('.fs-row').length) : 0;
out.revealText = box ? (box.textContent || '').trim().slice(0, 120) : null;
out.revealDieChips = box ? box.querySelectorAll('.fs-die').length : 0;

/* ── it is the PLAYER's reveal: the rival firing one must not open it ── */
G._firstStrikeOpen = false;
if (box) box.remove();
document.documentElement.classList.remove('fkFirstStrike');
_firstStrike('o');
await sleep(300);
out.rivalCannotOpenIt = !document.getElementById('fsReveal');

/* ── the debt chip is gone from a badge that no longer costs gold ── */
G._tell = wasTell;
try { _updateTellHUD(); } catch (e) {}
await sleep(200);
out.arrearsChipPresent = !!document.getElementById('arrearsVal');
out.goldNow = S && S.run ? S.run.gold : null;
const rollBtn = document.getElementById('btnRoll');
if (rollBtn) { tap(rollBtn); await until(() => G.phase === 'choosing' || G.phase === 'idle', 14000); await sleep(600); }
out.goldAfterARoll = S && S.run ? S.run.gold : null;
out.rollCostNothing = out.goldNow === out.goldAfterARoll;

return out;
