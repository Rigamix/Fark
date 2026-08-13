/* TRACK THE STRIPS AND THE DIALOGUE BOX THROUGH A LIVE TURN.
 * Samples positions every 150ms for ~14s while driving a match, records every
 * DISTINCT position each element occupies plus the dice state at the time. */
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
try { G = null; } catch (e) {}
launchBossMatch();
if (!await until(() => typeof G !== 'undefined' && G && G.pF !== undefined, 14000)) return { err: 'no match' };
await sleep(400);

/* force the dialogue box on so we can watch it */
try { DLG.show('Measuring the table, hold still.'); } catch(e) { out.dlgShowErr = String(e); }

const g = id => document.getElementById(id);
const rnd = v => Math.round(v*10)/10;
const samples = [];
const t0 = Date.now();
let lastKey = '';
while (Date.now() - t0 < 15000) {
  try {
    const dlg = g('dlgBox').getBoundingClientRect();
    const ts = g('topStrip').getBoundingClientRect();
    const bs = g('botStrip').getBoundingClientRect();
    const tl = g('throwLine').getBoundingClientRect();
    const nOpp = g('oppDiceRow').querySelectorAll('.die').length;
    const nPl = g('playerDiceRow').querySelectorAll('.die').length;
    const nTags = document.querySelectorAll('.selTag,#selTotal').length;
    const rec = {
      t: Date.now()-t0,
      dlgTop: rnd(dlg.top), dlgH: rnd(dlg.height),
      topStripTop: rnd(ts.top), topVis: getComputedStyle(g('topStrip')).visibility,
      botStripTop: rnd(bs.top), botVis: getComputedStyle(g('botStrip')).visibility,
      throwTop: rnd(tl.top), throwBot: rnd(tl.bottom),
      nOpp, nPl, nTags,
      phase: (window.G&&G.phase)||'?',
      msgTop: (g('statusTop').textContent||'').slice(0,26),
      msgBot: (g('statusBot').textContent||'').slice(0,26)
    };
    const key = [rec.dlgTop,rec.topStripTop,rec.botStripTop,rec.throwTop,rec.nOpp,rec.nPl,rec.nTags,rec.phase,rec.msgTop,rec.msgBot].join('|');
    if (key !== lastKey) { samples.push(rec); lastKey = key; }
  } catch(e) { samples.push({err:String(e)}); }
  /* drive the player turn along */
  const rb = g('btnRoll');
  if (rb && vis(rb) && !rb.disabled) tap(rb);
  await sleep(150);
}
out.samples = samples.slice(0, 60);
out.dlgCS = (function(){ const s=getComputedStyle(g('dlgBox')); return {pos:s.position, top:s.top}; })();
out.hudH = getComputedStyle(document.documentElement).getPropertyValue('--hud-h');
out.screenMatchW = rnd(g('screen-match').getBoundingClientRect().width);
return out;
