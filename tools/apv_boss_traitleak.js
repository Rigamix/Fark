/* BOSS MATCH TRAIT/PATRON DIALOGUE LEAK PROBE
 * SUITE: exclude
 * 1) new run, 2) launch a patron seat so _lastSeatArt/_lastSeatTrait get set,
 * 3) bail back and launchBossMatch, 4) inspect the globals + what _dlgEvent
 * and the getLine wrapper actually return for boss-match categories.
 */
const sleep = ms => new Promise(r => setTimeout(r, ms));
const until = async (fn, ms) => { const t0=Date.now();
  while(Date.now()-t0<ms){ try{ if(fn()) return true; }catch(e){} await sleep(60);} return false; };
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
_getS();_ensureNight();
/* sit at a patron seat to populate the globals, like a real player would */
launchSeat(0);
if (!await until(() => typeof G !== 'undefined' && G && G.rung, 12000)) return { err: 'no patron match' };
await sleep(800);
out.afterPatron = { art: window._lastSeatArt, trait: window._lastSeatTrait,
                    rung: G.rung && G.rung.name, isBoss: !!G._isBoss };

/* now a boss match, same run */
try { G = null; } catch (e) {}
launchBossMatch();
if (!await until(() => typeof G !== 'undefined' && G && G.rung && G._isBoss !== undefined, 14000)) return { err: 'no boss match' };
await sleep(1500);
out.inBoss = { art: window._lastSeatArt, trait: window._lastSeatTrait,
               rung: G.rung && G.rung.name, isBoss: !!G._isBoss,
               oppKey: window.DLG && DLG.oppKey };

/* what the lore layer returns for boss-match moments */
out.dlgEvent = {};
['bust','yourBust','bank','yourBank','push','banksafe'].forEach(m=>{
  const r = _dlgEvent(m);
  out.dlgEvent[m] = r ? r.slice(0,60) : null;
});
/* which pool that came from: re-run _dlgPick directly */
out.pools = {
  patronPoolHit: window._lastSeatArt ? !!_dlgPick('patron:'+String(window._lastSeatArt).toLowerCase()+':bust',0,null) : null,
  traitPoolHit: !!_dlgPick('trait:'+window._lastSeatTrait+':bust',0,null)
};
/* what MATCH_START would do in the boss match via the wrapper: _DLG_PERSONAL
   routes to _dlgSay(_lastSeatArt) — sample it */
out.dlgSaySample = (function(){ const r=_dlgSay(window._lastSeatArt); return r?r.slice(0,60):null; })();
/* boss persona/trait fields — does the boss even carry a trait of its own? */
out.bossRung = { key: G.rung.key, persona: G.rung.persona||null,
                 ptTrait: (typeof PT_TRAIT!=='undefined'&&G.rung.persona)?PT_TRAIT[G.rung.persona]||null:null };
return out;
