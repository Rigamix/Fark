/* P681 QUICK WINS, MEASURED LIVE
 * SUITE: exclude */
const sleep = ms => new Promise(r => setTimeout(r, ms));
const until = async (fn, ms) => { const t0=Date.now();
  while(Date.now()-t0<ms){ try{ if(fn()) return true; }catch(e){} await sleep(60);} return false; };
const vis = el => { if(!el||!el.isConnected) return false; const s=getComputedStyle(el),r=el.getBoundingClientRect();
  return s.display!=='none'&&s.visibility!=='hidden'&&+s.opacity>0.05&&r.width>1&&r.height>1; };
const tap = el => { if(!vis(el)) return false; const r=el.getBoundingClientRect();
  const o={bubbles:true,cancelable:true,clientX:r.left+r.width/2,clientY:r.top+r.height/2};
  el.dispatchEvent(new PointerEvent('pointerdown',o)); el.dispatchEvent(new PointerEvent('pointerup',o));
  el.dispatchEvent(new MouseEvent('click',o)); return true; };
const out = {};

/* ── mid-float pick: tap a die ~400ms after the deal, no settle wait ──── */
tap(document.getElementById('hsBtnBottom')); await sleep(2000);
await until(() => document.querySelector('.nrdie'), 9000);
await sleep(400); /* well inside the 1.6-2s float window */
const d0 = document.querySelector('.nrdie');
out.midFloat = { floatDoneBefore: !!(d0 && d0._floatDone) };
tap(d0); await sleep(1200);
out.midFloat.zoomOpened = !!document.querySelector('.nrdie.zoom');
out.midFloat.takeBtn = vis(document.getElementById('nrTakeBtn'));
tap(document.getElementById('nrTakeBtn')); await sleep(2400);
await until(() => typeof launchSeat === 'function' && S && S.run, 9000);

/* ── the win-offer CSS: picked leaves, others grey ────────────────────── */
const scratch = document.createElement('div');
scratch.innerHTML = '<div class="fo-wrap taken"><div class="fo-card picked"></div><div class="fo-card"></div></div>';
document.body.appendChild(scratch);
await sleep(50);
const pk = scratch.querySelector('.fo-card.picked'), un = scratch.querySelector('.fo-card:not(.picked)');
out.offer = { pickedOpacity: getComputedStyle(pk).opacity, pickedScale: getComputedStyle(pk).scale,
              unpickedOpacity: getComputedStyle(un).opacity, unpickedFilter: getComputedStyle(un).filter.slice(0,30) };
scratch.remove();

/* ── focus: tap-away + strips fade + no caption ───────────────────────── */
_getS();
famApplyPick({ id: 'powder_keg', tier: 2 });
try { G = null; } catch (e) {}
launchBossMatch();
if (!await until(() => typeof G !== 'undefined' && G && G.phase === 'idle', 16000)) return { err: 'no idle', out };
await sleep(400);
famCardTap(0); await sleep(250);
const ms = document.getElementById('screen-match');
out.focus = {
  tipOpen: !!document.getElementById('cardFocusTip'),
  tipOpenClass: ms.classList.contains('tip-open'),
  stripFaded: getComputedStyle(document.getElementById('botStrip')).opacity === '0'
};
/* tap bare wood, far from any card */
const woodTap = new PointerEvent('pointerdown', { bubbles: true, clientX: 215, clientY: 400 });
document.getElementById('screen-match').dispatchEvent(woodTap);
await sleep(150);
out.focus.tapAwayClosed = !document.getElementById('cardFocusTip');
out.focus.stripBack = getComputedStyle(document.getElementById('botStrip')).opacity === '1';
/* npc tip: no caption */
const cid = (G.oCards || [])[0];
if (cid) { npcOppTap(cid); await sleep(200);
  const t = document.getElementById('cardFocusTip');
  out.focus.npcSub = t ? (t.querySelector('.cft-sub') ? t.querySelector('.cft-sub').textContent : '(no sub el)') : null;
  npcOppTap(cid); await sleep(100); }

/* ── the removed texts stay removed at runtime ────────────────────────── */
out.noHolds = !PATRON_LINES.some(r => / HOLDS \d/.test(r.t));
return out;
