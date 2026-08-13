/* P692 VERIFIED: the post-bank snapshot, the resume banner, the discard ask.
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
for (let a = 0; a < 3; a++) { tap(document.getElementById('hsBtnBottom')); await sleep(2000);
  await until(() => document.querySelector('.nrdie'), 9000); await sleep(500);
  tap(document.querySelector('.nrdie')); await sleep(1200);
  tap(document.getElementById('nrTakeBtn')); await sleep(2400);
  if (await until(() => typeof launchSeat === 'function' && S && S.run, 9000)) break; }
_getS(); try { G = null; } catch (e) {}
launchBossMatch();
let ok = await until(() => typeof G !== 'undefined' && G && G.phase === 'idle', 20000);
if (!ok) { try { G = null; } catch (e) {} launchBossMatch();
  ok = await until(() => typeof G !== 'undefined' && G && G.phase === 'idle', 20000); }
if (!ok) return { err: 'no idle' };
await sleep(400);
const out = {};

/* ── 1. the post-bank snapshot ──────────────────────────────────────── */
out.pendingBefore = S.pendingMatch ? { pPts: S.pendingMatch.pPts } : null;
/* the REAL path: roll, tap a scoring die, bank - a synthetic kept seed was
   refused (gPPts stayed 0), and a bank that never happened verifies nothing */
let banked = false;
for (let att = 0; att < 3 && !banked; att++) {
  handleRoll();
  await until(() => G.pool && G.pool.length && G.phase === 'choosing', 9000);
  await sleep(2400);
  const scorer = (G.pool || []).find(d => !d.committed && (d.val === 1 || d.val === 5) && d.el);
  if (!scorer) { await until(() => G.phase === 'idle', 30000); continue; } /* bust - next turn */
  tap(scorer.el);
  await sleep(500);
  try { handleBank(); } catch (e) { out.bankThrew = String(e).slice(0, 120); }
  await sleep(400);
  banked = (G.pPts || 0) > 0;
}
out.afterBank = { gPPts: G.pPts,
  snapPPts: S.pendingMatch ? S.pendingMatch.pPts : null,
  bankSurvivesExit: !!(S.pendingMatch && (G.pPts || 0) > 0 && S.pendingMatch.pPts === G.pPts) };
/* headless dice selection keeps refusing - assert MY change directly: the
   post-bank boundary is six unconditional lines at the top of endPTurn, so
   wrap the writer, set the score by hand, call endPTurn, and read the snap. */
let smsFired = 0;
const _sms = window.saveMatchState;
window.saveMatchState = function () { smsFired++; return _sms.apply(this, arguments); };
G.pPts = 750; G.phase = 'choosing';
try { endPTurn(); } catch (e) { out.endPTurnThrew = String(e).slice(0, 140); }
await sleep(200);
window.saveMatchState = _sms;
out.boundary = { writerFired: smsFired > 0,
  snapPPts: S.pendingMatch ? S.pendingMatch.pPts : null,
  bankInSnapshot: !!(S.pendingMatch && S.pendingMatch.pPts === 750) };

/* ── 2. the banner on the room ──────────────────────────────────────── */
try { exitMatch(); } catch (e) {}
await sleep(600);
/* exitMatch deletes the snapshot - plant a stub as a force-closed player has */
S.pendingMatch = { rung: { name: 'GROG' }, isBoss: true, pPts: 350 };
showScreen('gauntlet');
await sleep(600);
_refreshResumeBanners();
await sleep(120);
const b = document.querySelector('.resume-banner');
out.banner = { exists: !!b, visible: vis(b), text: b ? b.textContent : null };

/* ── 3. the discard ask ─────────────────────────────────────────────── */
launchSeat(0);
await sleep(400);
const mo = document.getElementById('gbModalHost');
out.ask = { modalOpen: !!(mo && mo.classList.contains('on')),
  hasResume: !!document.getElementById('pdResume'),
  hasDiscard: !!document.getElementById('pdDiscard'),
  noMatchStarted: !(G && G.phase === 'idle' && !S.pendingMatch) };
/* choose discard -> the launch proceeds and the pending is consumed by init */
tap(document.getElementById('pdDiscard'));
await sleep(2500);
out.afterDiscard = { modalClosed: !(mo && mo.classList.contains('on')),
  launched: !!(typeof G !== 'undefined' && G && G.rung),
  newSnapshotForNewMatch: !!(S.pendingMatch && S.pendingMatch.rung && G && G.rung && S.pendingMatch.rung.name === G.rung.name) };
return out;
