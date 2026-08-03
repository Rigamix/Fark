/* famLog: does a burst survive, and can it speak off the match screen?
 *
 * Two failures this asserts against, both measured before the fix:
 *   OVERWRITE - setStatusMsg assigns textContent, so two effects resolving in
 *     the same synchronous tick left only the second. 105 call sites feed it.
 *   A HIDDEN DIV - statusTop/statusBot live inside #screen-match, so every
 *     famLog from the shop, the loadout or a settle path wrote into an element
 *     on a page that was not displayed.
 *
 * THE BURST IS FIRED SYNCHRONOUSLY, in one tick, because that is the shape of
 * the bug. Spacing the calls out would test a queue that was never needed. */
const sleep = ms => new Promise(r => setTimeout(r, ms));

const out = { seen: [], notes: [] };

/* observe every announcement the queue makes, on either surface */
const seen = out.seen;
const _realSet = window.setStatusMsg;
window.setStatusMsg = function(m, c) { seen.push({ where: 'strip', m: String(m) }); return _realSet.apply(this, arguments); };
const _realToast = window._famToast;
window._famToast = function(m, c) { seen.push({ where: 'toast', m: String(m) }); return _realToast.apply(this, arguments); };

out.currentScreenReadable = (typeof _currentScreen !== 'undefined');
out.screenAtStart = (typeof _currentScreen !== 'undefined') ? _currentScreen : null;

/* ── 1. THE BURST. Five in one tick, the way a hot-dice chain fires. ── */
const BURST = ['ALPHA', 'BRAVO', 'CHARLIE', 'DELTA', 'ECHO'];
BURST.forEach(m => famLog(m));
out.queuedImmediately = _famQ.length;      /* proof they were held, not dropped */
await sleep(5200);                          /* drain: 1 immediate + 4 at 380-820ms */
out.burstSeen = seen.filter(s => BURST.indexOf(s.m) >= 0).map(s => s.m);
out.burstLost = BURST.filter(m => out.burstSeen.indexOf(m) < 0);

/* ── 2. OFF-MATCH. The menu is up, so the strips are on a hidden screen. ── */
seen.length = 0;
famLog('OFF MATCH ONE', 'gold');
await sleep(1200);
const toastEl = document.getElementById('famToast');
out.toastExists = !!toastEl;
if (toastEl) {
  const r = toastEl.getBoundingClientRect(), cs = getComputedStyle(toastEl);
  out.toast = { text: toastEl.textContent, w: Math.round(r.width), h: Math.round(r.height),
                opacity: cs.opacity, display: cs.display,
                /* the whole point: it must NOT be inside the match screen */
                insideMatchScreen: !!toastEl.closest('#screen-match') };
}
out.offMatchWentTo = seen.map(s => s.where);

/* a toast that renders but is invisible is the same bug wearing a hat */
out.toastVisible = !!(out.toast && +out.toast.opacity > 0.9
                      && out.toast.w > 1 && out.toast.h > 1);

window.setStatusMsg = _realSet;
window._famToast = _realToast;

out.verdict = {
  burstFullyDelivered: out.burstLost.length === 0,
  burstWasQueued:      out.queuedImmediately >= 4,
  offMatchUsesToast:   out.offMatchWentTo.length > 0 && out.offMatchWentTo.every(w => w === 'toast'),
  toastOutsideMatch:   out.toastExists && out.toast.insideMatchScreen === false,
  toastActuallyVisible: out.toastVisible
};
return out;
