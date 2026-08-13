/* D23b RE-DERIVATION: double-rule seat — one badge, two rules — does the
 * second (sleeved) rule now get a visible HUD surface with a live counter?
 * SUITE: exclude
 *
 * Shape: boss match (seat's own tell on #tellBadge) + S.run.sleeve='drill_order'.
 * Asserts: badge shows only the seat tell; #famAux SLEEVED chip exists, is
 * VISIBLE (computed style + rect), names the sleeved rule, and carries the
 * roll counter; counter ticks after a roll; _drillCap enforces.
 */
const sleep = ms => new Promise(r => setTimeout(r, ms));
const until = async (fn, ms) => { const t0=Date.now();
  while(Date.now()-t0<ms){ try{ if(fn()) return true; }catch(e){} await sleep(60);} return false; };
const vis = el => { if(!el||!el.isConnected) return false; const s=getComputedStyle(el),r=el.getBoundingClientRect();
  return s.display!=='none'&&s.visibility!=='hidden'&&+s.opacity>0.05&&r.width>1&&r.height>1; };
const tap = el => { if(!el) return false; const r=el.getBoundingClientRect();
  const o={bubbles:true,cancelable:true,clientX:r.left+r.width/2,clientY:r.top+r.height/2};
  el.dispatchEvent(new PointerEvent('pointerdown',o)); el.dispatchEvent(new PointerEvent('pointerup',o));
  el.dispatchEvent(new MouseEvent('click',o)); return true; };

for (let a = 0; a < 3; a++) { tap(document.getElementById('hsBtnBottom')); await sleep(2000);
  await until(()=>{const d=document.querySelector('.nrdie');return d&&d._floatDone;},9000);
  tap(document.querySelector('.nrdie')); await sleep(1400);
  tap(document.getElementById('nrTakeBtn')); await sleep(2400);
  if (await until(()=>typeof launchSeat==='function'&&S&&S.run,9000)) break; }

const out = {};
_getS();
S.run.sleeve = 'drill_order';
save();
try { G = null; } catch (e) {}
launchBossMatch();
if (!await until(() => typeof G !== 'undefined' && G && G._tell, 14000)) return { err: 'no match/tell' };
/* wait out the tell splash so the badge is its steady-state self */
await until(() => !document.querySelector('.tell-splash'), 8000);
await sleep(600);

out.tell = G._tell && G._tell.id;
out.sleeve = G._sleeve;
out.doubleRule = !!(G._tell && G._sleeve && G._tell.id !== G._sleeve);

const badge = document.getElementById('tellBadge');
out.badge = badge ? { text: badge.textContent.replace(/\s+/g,' ').trim().slice(0,60), visible: vis(badge) } : null;

const aux = document.getElementById('famAux');
const chip = aux ? [...aux.children].find(c => /SLEEVED/.test(c.textContent)) : null;
out.chip = chip ? { text: chip.textContent.replace(/\s+/g,' ').trim(), visible: vis(chip),
  rect: (r=>({x:Math.round(r.x),y:Math.round(r.y),w:Math.round(r.width),h:Math.round(r.height)}))(chip.getBoundingClientRect()),
  title: chip.title.slice(0,90) } : null;
out.auxVisible = vis(aux);

/* overlap check: is anything else painted on top of the chip's centre? */
if (chip) {
  const r = chip.getBoundingClientRect();
  const topEl = document.elementFromPoint(r.x + r.width/2, r.y + r.height/2);
  out.chipHittable = !!topEl && (topEl === chip || chip.contains(topEl));
  out.topElAtChip = topEl ? (topEl.id || topEl.className || topEl.tagName) : null;
}

/* enforcement side */
out.drillCap = (typeof _drillCap==='function') ? _drillCap() : 'no fn';
out.rollCount0 = G.turnRollCount || 0;

/* roll once, watch the counter tick on the chip */
const rollBtn = document.getElementById('btnRoll');
out.rollBtnDisabled0 = rollBtn ? rollBtn.disabled : null;
if (rollBtn && !rollBtn.disabled) {
  tap(rollBtn);
  await until(() => (G.turnRollCount||0) > out.rollCount0, 6000);
  await sleep(1800);
  const chip2 = aux ? [...aux.children].find(c => /SLEEVED/.test(c.textContent)) : null;
  out.afterRoll = { rollCount: G.turnRollCount||0,
    chipText: chip2 ? chip2.textContent.replace(/\s+/g,' ').trim() : null,
    chipVisible: vis(chip2) };
}
return out;
