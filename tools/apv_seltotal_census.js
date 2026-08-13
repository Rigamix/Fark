/* CENSUS OF SCORE DISPLAYS IN THE PLAYER DICE AREA DURING SELECTION.
 * Reproduces the complaint state: per-die +tags, gold selTotal, white number
 * below. Reports every numeric element: id/class, text, color, rect.
 */
const sleep = ms => new Promise(r => setTimeout(r, ms));
const until = async (fn, ms) => { const t0=Date.now();
  while(Date.now()-t0<ms){ try{ if(fn()) return true; }catch(e){} await sleep(80);} return false; };
const vis = el => { if(!el||!el.isConnected) return false; const s=getComputedStyle(el),r=el.getBoundingClientRect();
  return s.display!=='none'&&s.visibility!=='hidden'&&+s.opacity>0.05&&r.width>1&&r.height>1; };
const tap = el => { if(!el) return false; const r=el.getBoundingClientRect();
  const o={bubbles:true,cancelable:true,clientX:r.left+r.width/2,clientY:r.top+r.height/2};
  el.dispatchEvent(new PointerEvent('pointerdown',o)); el.dispatchEvent(new PointerEvent('pointerup',o));
  el.dispatchEvent(new MouseEvent('click',o)); return true; };
const snap = label => {
  const items = [];
  const grab = (el, name) => { if(!el) { items.push({name, missing:true}); return; }
    const s=getComputedStyle(el), r=el.getBoundingClientRect();
    items.push({name, id:el.id||null, cls:el.className||null, text:(el.textContent||'').trim(),
      visible:vis(el), color:s.color, top:Math.round(r.top), left:Math.round(r.left)});
  };
  document.querySelectorAll('.selTag').forEach((e,i)=>grab(e,'selTag'+i));
  grab(document.getElementById('selTotal'),'selTotal');
  grab(document.getElementById('keptTotal'),'keptTotal');
  document.querySelectorAll('.kept-pts').forEach((e,i)=>grab(e,'kept-pts'+i));
  grab(document.getElementById('turnPts'),'hud-turnPts');
  grab(document.getElementById('statusBot'),'statusBot');
  grab(document.getElementById('keptTray'),'keptTray');
  return {label, phase:G&&G.phase, turnPts:G&&G.turnPts, kept:G&&G.kept.length, items};
};

for (let a = 0; a < 3; a++) { tap(document.getElementById('hsBtnBottom')); await sleep(2000);
  await until(()=>{const d=document.querySelector('.nrdie');return d&&d._floatDone;},9000);
  tap(document.querySelector('.nrdie')); await sleep(1400);
  tap(document.getElementById('nrTakeBtn')); await sleep(2400);
  if (await until(()=>typeof launchSeat==='function'&&S&&S.run,9000)) break; }

const out = { snaps: [] };
_getS();
try { G = null; } catch (e) {}
launchBossMatch();
if (!await until(() => typeof G !== 'undefined' && G && G.pool !== undefined, 14000)) return { err: 'no match' };
await sleep(2600);
/* get to the player's choosing phase */
for (let k = 0; k < 6 && G.phase !== 'choosing'; k++) {
  if (G.phase === 'idle') { try { handleRoll(); } catch(e){ out.rollErr=String(e); } }
  await until(() => G.phase === 'choosing', 6000);
}
if (!await until(() => G.phase === 'choosing' && G.pool.some(d=>!d.committed), 20000))
  return { err: 'never choosing', phase: G.phase, locked: G._rollLocked };
await sleep(1200);

/* select scoring dice: a 1 and a 5 if available, else any 1s/5s */
const scorers = G.pool.filter(d=>!d.committed && (d.val===1||d.val===5));
if (!scorers.length) return { err:'no 1s or 5s', vals:G.pool.map(d=>d.val) };
const pick = scorers.slice(0,2);
for (const d of pick) { tap(d.el); await sleep(300); }
await sleep(500);
out.picked = pick.map(d=>d.val);
out.snaps.push(snap('A: first selection, nothing kept yet'));

/* keep + roll again to populate the kept tray, then select again */
try { handleRoll(); } catch(e){ out.roll2Err=String(e); }
await sleep(3500);
if (!await until(() => G.phase === 'choosing', 15000)) { out.note='no second choosing: '+G.phase; return out; }
await sleep(800);
const s2 = G.pool.filter(d=>!d.committed && (d.val===1||d.val===5)).slice(0,2);
for (const d of s2) { tap(d.el); await sleep(300); }
await sleep(600);
out.picked2 = s2.map(d=>d.val);
out.snaps.push(snap('B: second selection, kept dice below'));
return out;
