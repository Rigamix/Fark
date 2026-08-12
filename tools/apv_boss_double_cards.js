/* THE DOUBLED CARDS AT THE TOP OF A BOSS MATCH
 * SUITE: exclude
 *
 * Denis: "On boss match I still see a doubling up of cards... a small one and
 * behind it, two big ones with the weathering effect I had asked to completely
 * remove."
 *
 * An earlier attempt at this could not reach a real boss - it launched a patron
 * and set _isBoss afterwards, so both rows were empty and it measured nothing.
 * launchBossMatch is the game's own path and fills G.oF properly.
 *
 * The question is not "are there extra cards" - the screenshot answers that. It
 * is WHICH RENDERER draws them, because there are two candidates and they are
 * fed by two different state arrays:
 *
 *   #famRowO  .fcv     famRenderRow, from G.oF   - the live family engine
 *   #oppCards .mcard   buildCBar,     from G.oCards - the legacy loadout
 *
 * So: count both, report what each is fed, and report the geometry - a renderer
 * that draws nothing still leaves a box, and a box is not a card.
 */
const sleep = ms => new Promise(r => setTimeout(r, ms));
const until = async (fn, ms) => { const t0=Date.now();
  while(Date.now()-t0<ms){ try{ if(fn()) return true; }catch(e){} await sleep(60);} return false; };
const vis = el => { if(!el||!el.isConnected) return false; const s=getComputedStyle(el),r=el.getBoundingClientRect();
  return s.display!=='none'&&s.visibility!=='hidden'&&+s.opacity>0.05&&r.width>1&&r.height>1; };
const tap = el => { if(!vis(el)) return false; const r=el.getBoundingClientRect();
  const o={bubbles:true,cancelable:true,clientX:r.left+r.width/2,clientY:r.top+r.height/2};
  el.dispatchEvent(new PointerEvent('pointerdown',o)); el.dispatchEvent(new PointerEvent('pointerup',o));
  el.dispatchEvent(new MouseEvent('click',o)); return true; };
const box = el => { if (!el) return null; const r = el.getBoundingClientRect();
  return { x:+r.left.toFixed(1), y:+r.top.toFixed(1), w:+r.width.toFixed(1), h:+r.height.toFixed(1) }; };

for (let a = 0; a < 3; a++) { tap(document.getElementById('hsBtnBottom')); await sleep(2000);
  await until(()=>{const d=document.querySelector('.nrdie');return d&&d._floatDone;},9000);
  tap(document.querySelector('.nrdie')); await sleep(1400);
  tap(document.getElementById('nrTakeBtn')); await sleep(2400);
  if (await until(()=>typeof launchSeat==='function'&&S&&S.run,9000)) break; }

_getS();
try { G = null; } catch (e) {}
launchBossMatch();
if (!await until(() => typeof G !== 'undefined' && G && G.oF, 14000)) return { err: 'boss never started' };
await sleep(2600);

/* every element in the rival's half of the screen that LOOKS like a card */
const shot = sel => [...document.querySelectorAll(sel)].map(el => ({
  cls: el.className, cid: el.dataset ? el.dataset.cid : null,
  box: box(el), visible: vis(el),
  filter: getComputedStyle(el).filter.slice(0, 70)
}));

return {
  state: {
    oF: (G.oF || []).map(c => c && { id: c.id, tier: c.tier, broken: !!c.broken }),
    oCards: (G.oCards || []).map(c => c && (c.id || c)),
    pF: (G.pF || []).map(c => c && c.id),
    pCards: (G.pCards || []).map(c => c && (c.id || c))
  },
  famRowO: { box: box(document.getElementById('famRowO')), cards: shot('#famRowO .fcv') },
  oppCards: { box: box(document.getElementById('oppCards')), cards: shot('#oppCards .mcard') },
  /* anything else card-shaped up there that neither renderer owns */
  strays: shot('#screen-match .mcard, #screen-match .fcv')
            .filter(c => c.box && c.box.y < 420)
};
