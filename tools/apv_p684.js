/* P684 FX SWEEP, MEASURED: every rebuilt spawner fires through FX.emit with
 * the game's shapes, and the hot-dice wash is gone.
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
if (!await until(() => typeof G !== 'undefined' && G && G.phase === 'idle', 16000)) return { err: 'no idle' };
await sleep(400);

/* intercept the engine */
const log = [];
const _emit = FX.emit;
FX.emit = function (o) { log.push({ shape: o.shape || 'square', color: o.color }); return _emit.apply(this, arguments); };
const run = (label, fn) => { log.length = 0; try { fn(); } catch (e) { return { label, err: String(e) }; }
  const shapes = {}; log.forEach(p => shapes[p.shape] = (shapes[p.shape] || 0) + 1);
  return { label, n: log.length, shapes, colors: [...new Set(log.map(p => p.color))].slice(0, 4) }; };

handleRoll();
await until(() => G.pool && G.pool.length && G.pool[0].el, 6000);
await sleep(2200);
const die = G.pool[0].el;

const out = { calls: [] };
out.calls.push(run('pixelSparks', () => spawnPixelSparks(die, 8)));
out.calls.push(run('shards', () => spawnShards(die, '#3a3a52')));
out.calls.push(run('obsidian', () => spawnObsidianBurst(die)));
out.calls.push(run('sawdust', () => spawnSawdust(die, 10)));
out.calls.push(run('fxSpray-ink', () => _fxSpray(die, '#d8b054', 12, { speed: 85, g: 70, size: 7, spread: 2.4 })));
out.calls.push(run('hotFountain', () => showHot()));

/* the wash: during .flash, the overlay背景 must stay transparent */
await sleep(120);
const ov = document.getElementById('hot-ov');
out.hotOv = { flashing: ov.classList.contains('flash'),
  bg: getComputedStyle(ov).backgroundColor,
  wordVisible: vis(ov.querySelector('.hot-word')) };
FX.emit = _emit;
return out;
