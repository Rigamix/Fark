/* IS THE RIVAL'S HAND ONE ROW NOW — AND DOES EVERYTHING THAT POINTED AT THE
 * OLD BAR STILL LAND?
 * SUITE: exclude
 *
 * P670 folded G.oCards into the family row and retired buildCBar's #oppCards
 * bar; P671 gave the card sheet its parchment. Each claim is read off the live
 * DOM in a REAL boss match (launchBossMatch — the path that deals both card
 * systems), not off the code:
 *
 *   1  #oppCards holds zero .mcard; #famRowO holds oF+oCards cards
 *   2  no .card-outer inside the row — the aging observer keys on that class,
 *      so its absence IS the absence of the weathering
 *   3  the spent bake: a start_bonus card (her_lucky_coin) renders grey from
 *      the first frame, measured filter not just class
 *   4  triggerCard on an npc card flashes the .fcv (fx-pulse) and drops its
 *      label into the row — the old code would have no-opped silently
 *   5  npcOppTap opens #gbSheet.fam-sheet on parchment (measured background),
 *      and a plain _gbSheetOpen afterwards resets to grey — no variant leak
 *   6  art: grogs_bump's webp actually painted (naturalWidth>0); an id with no
 *      webp shows the CARD_BG cover instead of a broken image
 *   7  the same fold in a PATRON match (launchSeat) — the route I didn't build
 *      this for still renders their npc cards in the row
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

for (let a = 0; a < 3; a++) { tap(document.getElementById('hsBtnBottom')); await sleep(2000);
  await until(()=>{const d=document.querySelector('.nrdie');return d&&d._floatDone;},9000);
  tap(document.querySelector('.nrdie')); await sleep(1400);
  tap(document.getElementById('nrTakeBtn')); await sleep(2400);
  if (await until(()=>typeof launchSeat==='function'&&S&&S.run,9000)) break; }

const out = {};
_getS();
try { G = null; } catch (e) {}
launchBossMatch();
if (!await until(() => typeof G !== 'undefined' && G && G.oF && G.oCards, 14000)) return { err: 'no boss' };
await sleep(2600);

/* ── 1. one row ─────────────────────────────────────────────────────── */
const row = document.getElementById('famRowO');
const bar = document.getElementById('oppCards');
out.state = { oF: (G.oF||[]).map(c=>c.id), oCards: (G.oCards||[]).slice() };
out.mcardsInBar = bar ? bar.querySelectorAll('.mcard').length : null;
out.fcvInRow = row ? row.querySelectorAll('.fcv').length : null;
out.rowMatchesState = out.fcvInRow === (G.oF.length + G.oCards.length);
out.rowCids = row ? [...row.querySelectorAll('.fcv')].map(e => e.dataset.cid) : [];

/* ── 2. no weathering hook ──────────────────────────────────────────── */
out.cardOuterInRow = row ? row.querySelectorAll('.card-outer').length : null;
out.agingCanvasInRow = row ? row.querySelectorAll('canvas').length : null;

/* ── 3. spent bake, measured ────────────────────────────────────────── */
const luck = row && row.querySelector('.fcv[data-cid="her_lucky_coin"]');
if (luck) {
  const cs = getComputedStyle(luck);
  out.luckyCoin = { hasSpent: luck.classList.contains('spent'),
    filterDimmed: /saturate\(0\.25\)|brightness\(0\.55\)/.test(cs.filter),
    filter: cs.filter.slice(0, 60) };
} else out.luckyCoin = { note: 'her_lucky_coin not dealt this run', dealt: G.oCards.slice() };

/* ── 4. triggerCard lands on the row ────────────────────────────────── */
const tgtCid = G.oCards[0];
if (tgtCid) {
  triggerCard(tgtCid, 'TEST FIRE', false);
  await sleep(120);
  const fc = row.querySelector('.fcv[data-cid="' + tgtCid + '"]');
  const lbl = row.querySelector('.card-trig-label[data-cid="' + tgtCid + '"]');
  out.trigger = { cid: tgtCid,
    pulsed: !!(fc && (fc.classList.contains('fx-pulse') ||
              fc.getAnimations().some(a => a.playState==='running' && /fxPulse/.test(a.animationName||'')))),
    labelInRow: !!lbl, labelText: lbl ? lbl.textContent : null };
}

/* ── 5. the parchment sheet, and no leak ────────────────────────────── */
if (tgtCid) {
  npcOppTap(tgtCid);
  await sleep(300);
  const sh = document.getElementById('gbSheet');
  const cs = sh ? getComputedStyle(sh) : null;
  out.sheet = { cls: sh ? sh.className : null,
    isFamSheet: !!(sh && sh.classList.contains('fam-sheet')),
    bg: cs ? cs.backgroundColor : null,
    isParchment: cs ? cs.backgroundColor === 'rgb(231, 214, 172)' : null,
    hasName: sh ? sh.textContent.length > 20 : null };
  _gbSheetClose(); await sleep(250);
  _gbSheetOpen('<div>plain</div>'); await sleep(120);
  const cs2 = getComputedStyle(sh);
  out.sheetNoLeak = { cls: sh.className, bgBackToGrey: cs2.backgroundColor === 'rgb(214, 214, 214)' };
  _gbSheetClose(); await sleep(200);
}

/* ── 6. art: real webp painted; missing webp shows the cover ────────── */
const bumpImg = row.querySelector('.fcv[data-cid="grogs_bump"] img');
out.artLoaded = bumpImg ? { naturalWidth: bumpImg.naturalWidth, painted: bumpImg.naturalWidth > 0 } : 'grogs_bump not dealt';
/* an id known to have NO webp: grogs_flask (boss signature) */
const scratch = document.createElement('div'); scratch.className = 'fcv-scratch';
scratch.innerHTML = famCardArt('grogs_flask', 1, {});
document.body.appendChild(scratch);
await sleep(900); /* let the img 404 and remove itself */
out.coverFallback = {
  imgSurvived: !!scratch.querySelector('img'),
  coverThere: !!scratch.querySelector('.fcvCover'),
  coverBg: scratch.querySelector('.fcvCover') ? scratch.querySelector('.fcvCover').style.background : null,
  markupNonEmpty: scratch.innerHTML.length > 40 };
scratch.remove();

/* ── 7. the patron route ────────────────────────────────────────────── */
try { endMatch && null; } catch (e) {}
try { G = null; } catch (e) {}
launchSeat(0);
if (await until(() => typeof G !== 'undefined' && G && G.oCards !== undefined, 12000)) {
  await sleep(2400);
  const row2 = document.getElementById('famRowO');
  out.patron = {
    oF: (G.oF||[]).length, oCards: (G.oCards||[]).slice(),
    fcvInRow: row2 ? row2.querySelectorAll('.fcv').length : null,
    mcardsInBar: (document.getElementById('oppCards')||{querySelectorAll:()=>[]}).querySelectorAll('.mcard').length,
    matches: row2 ? row2.querySelectorAll('.fcv').length === ((G.oF||[]).length + (G.oCards||[]).length) : null
  };
} else out.patron = { err: 'patron match did not start' };

return out;
