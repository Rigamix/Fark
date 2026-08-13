/* P693-695: seat-tap auto-resume, the portable shadow fallback, boot resume.
 * The probe returns before a scheduled reload; the shot 6s later must show
 * the MATCH screen again with no tap - that is P695's proof. SUITE: exclude */
const sleep = ms => new Promise(r => setTimeout(r, ms));
const until = async (fn, ms) => { const t0=Date.now();
  while(Date.now()-t0<ms){ try{ if(fn()) return true; }catch(e){} await sleep(60);} return false; };
const vis = el => { if(!el||!el.isConnected) return false; const s=getComputedStyle(el),r=el.getBoundingClientRect();
  return s.display!=='none'&&s.visibility!=='hidden'&&+s.opacity>0.05&&r.width>1&&r.height>1; };
const tap = el => { if(!vis(el)) return false; const r=el.getBoundingClientRect();
  const o={bubbles:true,cancelable:true,clientX:r.left+r.width/2,clientY:r.top+r.height/2};
  el.dispatchEvent(new PointerEvent('pointerdown',o)); el.dispatchEvent(new PointerEvent('pointerup',o));
  el.dispatchEvent(new MouseEvent('click',o)); return true; };
const inkArea = () => { const cv = document.getElementById('dsCanvas'); if (!cv || !cv.width) return 0;
  const d = cv.getContext('2d').getImageData(0, Math.floor(cv.height*0.35), cv.width, Math.floor(cv.height*0.4)).data;
  let a2 = 0; for (let i = 3; i < d.length; i += 16) if (d[i] > 30) a2++; return a2; };

/* P694 first: force the iOS path BEFORE any shadow paints */
window.__cfBlur = false;

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
const bossName = G.rung && G.rung.name;
const out = { bossName };

/* the iOS-path shadows */
handleRoll();
await until(() => G.pool && G.pool.length >= 3, 8000);
await sleep(2600);
out.iosPath = { cfBlur: window.__cfBlur, inkArea: inkArea(), painted: inkArea() > 40 };

/* P693: walk away (no exit - the snapshot survives), tap a seat, be BACK */
out.pendingExists = !!S.pendingMatch;
showScreen('gauntlet');
await sleep(800);
launchSeat(0);
await sleep(2500);
out.autoResume = { backAtMatch: vis(document.getElementById('screen-match')),
  sameRung: !!(G && G.rung && G.rung.name === bossName) };

/* P695: schedule a cold boot; the screenshot 6s from now is the assertion */
setTimeout(function () { location.reload(); }, 400);
return out;
