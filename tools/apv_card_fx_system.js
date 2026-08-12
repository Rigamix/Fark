/* DOES THE FEEDBACK VOCABULARY ACTUALLY LAND ON THE SCREEN?
 * SUITE: exclude
 *
 * P666 added cardFx(kind,target) and wired Tamper to it; P667 collapsed three
 * copies of the die sparkle band into one _sparkBand. Three questions, and each
 * is answered by reading the DOM after the game itself did the work - not by
 * checking that a function exists.
 *
 *   1  does _sparkBand draw the shapes, INCLUDING the diamond the feats
 *      overlay could never draw before
 *   2  does the CSS the vocabulary depends on exist (the keyframes, .fcv.broken)
 *   3  Tamper played through famUse: does the rival's card come back GREY, and
 *      does the shake land on the element that survives famRenderRow
 *
 * Q3 is the one that matters. The first draft of this patch put cardFx BEFORE
 * famRenderRow, which rebuilds the row's innerHTML - so the class went onto an
 * element that was thrown away a line later and nothing would have moved. The
 * probe reads the class off the LIVE row after the call, which is the only
 * reading that can tell those two apart.
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

const out = { present: {}, sparkBand: null, css: {}, tamper: null };

/* ── 1. the shared band, drawn into a scratch host ───────────────────── */
out.present.sparkBand = typeof _sparkBand === 'function';
out.present.cardFx    = typeof cardFx === 'function';
out.present.fxEl      = typeof _fxEl === 'function';

if (out.present.sparkBand) {
  const host = document.createElement('div');
  /* THE CLASS MATTERS. Every rule in the shared band is a DESCENDANT selector -
     `.nrparts span`, not `span`. A bare div in the body matches none of them, so
     the first run of this probe reported clipPath:none and animationName:none
     and that said nothing about the CSS at all. */
  host.className = 'nrparts';
  document.body.appendChild(host);
  /* the exact call the feats overlay now makes - the one that could not draw a
     diamond before this patch */
  _sparkBand(host, { c:['#e1a755','#ffd98a'], shape:['star','star','diamond','dot','dot'] },
             { count: 400, spread: 60, drift: 30 });
  const spans = [...host.querySelectorAll('span')];
  const byCls = {};
  spans.forEach(s => { byCls[s.className] = (byCls[s.className]||0) + 1; });
  /* a shape that has no clip-path rule renders as a square - which is what the
     feats overlay's missing .pdiamond would have done silently */
  const dia = host.querySelector('span.pdiamond');
  out.sparkBand = {
    total: spans.length,
    byClass: byCls,
    diamondHasClipPath: dia ? getComputedStyle(dia).clipPath !== 'none' : null,
    diamondClipPath: dia ? getComputedStyle(dia).clipPath.slice(0, 60) : null,
    colours: [...new Set(spans.map(s => s.style.getPropertyValue('--pc')))].sort(),
    animates: dia ? getComputedStyle(dia).animationName : null
  };
  host.remove();
}

/* ── 2. the CSS the vocabulary depends on ────────────────────────────── */
{
  const names = new Set(); const rules = [];
  for (const sh of document.styleSheets) {
    let rs; try { rs = sh.cssRules; } catch (e) { continue; }
    for (const r of rs) {
      if (r.type === CSSRule.KEYFRAMES_RULE) names.add(r.name);
      if (r.selectorText) rules.push(r.selectorText);
    }
  }
  out.css.keyframes = { fxShake: names.has('fxShake'), fxPulse: names.has('fxPulse'),
                        nrSpark: names.has('nrSpark'), cardFired: names.has('cardFired') };
  out.css.brokenRule   = rules.filter(s => /\.fcv\.broken/.test(s));
  out.css.sharedBand   = rules.filter(s => /nrparts span,/.test(s));
  /* the three copies should be ONE selector list now */
  out.css.bandCopies   = rules.filter(s => /\bspan\.pdiamond\b/.test(s));
}

/* ── 3. Tamper, played for real ──────────────────────────────────────── */
for (let a = 0; a < 3; a++) { tap(document.getElementById('hsBtnBottom')); await sleep(2000);
  await until(()=>{const d=document.querySelector('.nrdie');return d&&d._floatDone;},9000);
  tap(document.querySelector('.nrdie')); await sleep(1400);
  tap(document.getElementById('nrTakeBtn')); await sleep(2400);
  if (await until(()=>typeof launchSeat==='function'&&S&&S.run,9000)) break; }

if (typeof launchSeat !== 'function') { out.tamper = { skip: 'launchSeat unreachable' }; return out; }

_getS();
famApplyPick({ id: 'tamper', tier: 1 });
try { G = null; } catch (e) {}

/* A BOSS, NOT A PATRON. The first run of this probe launched seat 0 and found
   G.oF empty - and that is not a harness failure, it is how the game works:
   _famInitOpp gives family cards ONLY when _bossKey(rung) is truthy, or when a
   rung carries its own fcards, which no patron rung does. So Tamper has nothing
   to break in a patron match and its feedback can only ever be seen on a boss
   night. launchBossMatch is that path, and it is the game's own. */
out.bossPathExists = typeof launchBossMatch === 'function';
if (out.bossPathExists) launchBossMatch(); else launchSeat(0);

if (!await until(() => typeof G !== 'undefined' && G && G.pF && G.pF.length, 14000))
  { out.tamper = { err: 'match never started or hand empty' }; return out; }
await sleep(2200);

const idx = G.pF.findIndex(c => c && c.id === 'tamper');
/* WHAT THE RIVAL IS HOLDING IS REPORTED, NOT ASSUMED. Tamper needs a live rival
   card; if a patron seat brings none, that is the finding, not a failure. */
out.tamper = {
  playerHand: G.pF.map(c => c && c.id),
  rivalHandFromState: (G.oF || []).map(c => c && ({ id: c.id, broken: !!c.broken })),
  rivalCardsRendered: document.querySelectorAll('#famRowO .fcv').length,
  tamperIndex: idx
};

if (idx < 0 || !(G.oF || []).some(o => o && !o.broken)) {
  out.tamper.note = 'no live rival card to break in this seat — Tamper not exercised';
  return out;
}

const target = (G.oF || []).filter(o => !o.broken).sort((a,b) => b.tier - a.tier)[0];
out.tamper.targetId = target.id;

const played = famUse(idx);
out.tamper.famUseReturned = played;
/* P668 defers the beat by one frame ON PURPOSE - famUse re-renders the row
   after the effect returns, so anything applied synchronously is discarded.
   Two frames here, then read: early enough that the 460ms shake is still on. */
await new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)));
await sleep(60);

/* read the LIVE row - the element famRenderRow left behind, not the one the
   call started with */
const el = document.querySelector('#famRowO .fcv[data-cid="' + target.id + '"]');
out.tamper.targetStillInDom = !!el;
if (el) {
  const cs = getComputedStyle(el);
  out.tamper.classes      = el.className;
  out.tamper.hasBroken    = el.classList.contains('broken');
  out.tamper.hasShake     = el.classList.contains('fx-shake');
  out.tamper.filter       = cs.filter;
  out.tamper.greyApplied  = /grayscale/.test(cs.filter);
  /* is it MOVING? a running finite animation on this element */
  out.tamper.running = el.getAnimations().filter(a => a.playState === 'running')
                         .map(a => a.animationName || (a.effect && a.effect.getKeyframes && 'css'));
}
out.tamper.stateBroken = (G.oF || []).map(c => ({ id: c.id, broken: !!c.broken }));

/* and it must SURVIVE the next row rebuild - broken is a fact, not a beat */
await sleep(900);
famRenderRow();
const el2 = document.querySelector('#famRowO .fcv[data-cid="' + target.id + '"]');
out.tamper.afterRerender = el2 ? {
  hasBroken: el2.classList.contains('broken'),
  greyApplied: /grayscale/.test(getComputedStyle(el2).filter)
} : null;

return out;
