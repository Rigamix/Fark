/* WIN-SCREEN BOTTOM-UI TIMING, v2. SUITE: exclude
 * v1 polled with setTimeout(100) and every mark landed on the final poll —
 * the poll loop was starved, so the times measured the instrument. v2 uses
 * MutationObservers: the timestamp is taken inside the observer callback,
 * a microtask after the DOM flip, immune to poll starvation. */
const sleep = ms => new Promise(r => setTimeout(r, ms));
const until = async (fn, ms) => { const t0=Date.now();
  while(Date.now()-t0<ms){ try{ if(fn()) return true; }catch(e){} await sleep(60);} return false; };
const vis = el => { if(!el||!el.isConnected) return false; const s=getComputedStyle(el),r=el.getBoundingClientRect();
  return s.display!=='none'&&s.visibility!=='hidden'&&+s.opacity>0.05&&r.width>1&&r.height>1; };
const tap = el => { if(!vis(el)) return false; const r=el.getBoundingClientRect();
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
S.run.gold = 200; save();
try { G = null; } catch (e) {}
launchSeat(0);
if (!await until(() => typeof G !== 'undefined' && G && G.pool && G.target, 14000)) return { err: 'no match' };
await sleep(1500);
out.isBoss = !!G._isBoss; out.target = G.target;

const resCard = document.getElementById('resCard');
const ov = document.getElementById('end-ov');
const resTitle = document.getElementById('resTitle');
const resScores = document.querySelector('#end-ov .res-scores');
const log = {};
let t0 = 0;
const now = () => Math.round(performance.now() - t0);

const moCard = new MutationObserver(() => {
  if (log.resCard_show === undefined && resCard.classList.contains('show')) log.resCard_show = now();
  if (log.fo_wrap_inDom === undefined && resCard.querySelector('.fo-wrap')) log.fo_wrap_inDom = now();
});
moCard.observe(resCard, { attributes: true, attributeFilter: ['class'], childList: true, subtree: true });

const moTitle = new MutationObserver(() => {
  if (log.title_anim_start === undefined && resTitle.style.animation && resTitle.style.animation !== 'none')
    log.title_anim_start = now();
});
moTitle.observe(resTitle, { attributes: true });

const moScores = new MutationObserver(() => {
  if (log.scores_fadein === undefined && resScores.classList.contains('fade-in')) log.scores_fadein = now();
  if (log.scores_lifted === undefined && resScores.classList.contains('lifted')) log.scores_lifted = now();
});
moScores.observe(resScores, { attributes: true });

const moOv = new MutationObserver(() => {
  if (log.end_ov_show === undefined && ov.classList.contains('show')) log.end_ov_show = now();
  if (log.fo_skip_hoisted === undefined && ov.querySelector(':scope>.fo-skip')) log.fo_skip_hoisted = now();
});
moOv.observe(ov, { attributes: true, childList: true });

const gw = document.getElementById('resGoldWrap');
const moGold = new MutationObserver(() => {
  if (log.gold_wrap_shown === undefined && gw.style.display === 'flex') log.gold_wrap_shown = now();
});
moGold.observe(gw, { attributes: true });

/* reference timers: if these fire late, the environment (not the game) is
   the delay. Long tasks caught too, to tell throttling from a blocked thread. */
const ref = {}; out.longTasks = [];
try { new PerformanceObserver(l => l.getEntries().forEach(e =>
  out.longTasks.push({ start: Math.round(e.startTime - (performance.now() - (performance.now()-t0)) ), at: Math.round(e.startTime), dur: Math.round(e.duration) })))
  .observe({ entryTypes: ['longtask'] }); } catch (e) {}
t0 = performance.now();
[100, 500, 700, 1300, 1800].forEach(d => setTimeout(() => { ref['t' + d] = now(); }, d));
G.pPts = G.target + 50;
endMatch(true);
log.endMatch_returned = now();
out.refTimers = ref;

await until(() => log.fo_wrap_inDom !== undefined, 15000);
await sleep(700);
log.settled_probe_at = now();

/* final visibility census */
out.visible = {
  fo_cards: [...document.querySelectorAll('#end-ov .fo-offer .fo-card')].map(vis),
  fo_slots: [...document.querySelectorAll('#end-ov .fo-slot')].map(vis),
  fo_skip: vis(document.querySelector('#end-ov .fo-skip')),
  end_btns: vis(document.getElementById('end-btns')),
  end_btns_display: document.getElementById('end-btns').style.display
};
/* are any entrance animations still running on the offer block? */
out.runningAnims = resCard.getAnimations({ subtree: true })
  .filter(a => a.playState === 'running')
  .map(a => a.animationName || a.transitionProperty || 'anon').slice(0, 10);
out.phase = window._endScreenPhase;
out.timeline_ms = log;
return out;
