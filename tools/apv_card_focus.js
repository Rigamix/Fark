/* THE ARCH AND THE GROW-AND-READ FOCUS, MEASURED IN A LIVE MATCH
 * SUITE: exclude
 *
 * P672 claims: the rival's cards arch like the player's (mirrored); tapping a
 * card grows it smoothly and raises word-by-word text; a second tap dismisses;
 * a drag dismisses; and no sheet or PLAY button appears at the table any more.
 * Each read off the computed styles and live DOM, not the code.
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
famApplyPick({ id: 'powder_keg', tier: 2 });
try { G = null; } catch (e) {}
launchBossMatch();
if (!await until(() => typeof G !== 'undefined' && G && G.pF && G.pF.length, 14000)) return { err: 'no match' };
await sleep(2600);

/* ── 1. the arch ────────────────────────────────────────────────────── */
const rowO = document.getElementById('famRowO');
out.arch = [...rowO.querySelectorAll('.fcv')].map(e => {
  const cs = getComputedStyle(e);
  return { cid: e.dataset.cid, rotate: cs.rotate, translate: cs.translate };
});
/* mirrored arch for 3: +6.5 up, 0, -6.5 up */
out.archIsMirrored = out.arch.length === 3 &&
  out.arch[0].rotate === '6.5deg' && /-/.test(out.arch[0].translate) &&
  (out.arch[1].rotate === '0deg'||out.arch[1].rotate==='none') &&
  out.arch[2].rotate === '-6.5deg';

/* ── 2. tap: grow + words, above ────────────────────────────────────── */
const myCard = document.querySelector('#famRowP .fcv');
famCardTap(0);
await sleep(350);
const tip = document.getElementById('cardFocusTip');
out.focusOpen = {
  cardHasFocus: myCard.classList.contains('focus'),
  scale: getComputedStyle(myCard).scale,
  tipExists: !!tip,
  words: tip ? tip.querySelectorAll('span.w').length : 0,
  titleText: tip ? tip.querySelector('.cft-name').textContent : null,
  bodyNonEmpty: tip ? tip.querySelector('.cft-body').textContent.length > 10 : false,
  tipAboveCard: tip ? tip.getBoundingClientRect().bottom <= myCard.getBoundingClientRect().top + 4 : null,
  wordsAnimating: tip ? [...tip.querySelectorAll('span.w')].some(w =>
      w.getAnimations().some(a => /cftWord/.test(a.animationName||''))) : false,
  noSheet: !document.querySelector('#gbSheet.on'),
  noPlayButton: !tip || !/PLAY/.test(tip.textContent)
};
/* title darker than the family accent (the standing rule) */
if (tip) {
  const t = getComputedStyle(tip.querySelector('.cft-name')).color;
  out.titleColor = t;
  const m = t.match(/\d+/g).map(Number);
  const fam = famDef(G.pF[0].id), accent = (FAMILIES[fam.fam]||{}).color || '#f0c860';
  const c = document.createElement('i'); c.style.color = accent; document.body.appendChild(c);
  const a = getComputedStyle(c).color.match(/\d+/g).map(Number); c.remove();
  out.titleDarkerThanAccent = (m[0]+m[1]+m[2]) < (a[0]+a[1]+a[2]);
}

/* ── 3. second tap dismisses ────────────────────────────────────────── */
famCardTap(0);
await sleep(120);
out.secondTap = { tipGone: !document.getElementById('cardFocusTip'),
                  focusGone: !myCard.classList.contains('focus') };

/* ── 4. rival tap: below ────────────────────────────────────────────── */
famOppTap(0);
await sleep(200);
const tip2 = document.getElementById('cardFocusTip');
const oppCard = rowO.querySelector('.fcv');
out.rivalFocus = { tipExists: !!tip2,
  tipBelowCard: tip2 ? tip2.getBoundingClientRect().top >= oppCard.getBoundingClientRect().bottom - 6 : null };
famOppTap(0); await sleep(100);

/* npc card too */
const npcCid = (G.oCards||[])[0];
if (npcCid) {
  npcOppTap(npcCid);
  await sleep(200);
  const t3 = document.getElementById('cardFocusTip');
  out.npcFocus = { tipExists: !!t3, noSheet: !document.querySelector('#gbSheet.on'),
    title: t3 ? t3.querySelector('.cft-name').textContent : null };
  npcOppTap(npcCid); await sleep(100);
}

/* ── 5. a drag start dismisses ──────────────────────────────────────── */
famCardTap(0);
await sleep(150);
const r = myCard.getBoundingClientRect();
const mk = (t, x, y) => new MouseEvent(t, { bubbles: true, cancelable: true, clientX: x, clientY: y });
myCard.dispatchEvent(mk('mousedown', r.left+r.width/2, r.top+r.height/2));
document.dispatchEvent(mk('mousemove', r.left+r.width/2+18, r.top+r.height/2-18));
await sleep(80);
out.dragDismiss = { tipGone: !document.getElementById('cardFocusTip') };
document.dispatchEvent(mk('mouseup', r.left+r.width/2+18, r.top+r.height/2-18));
await sleep(100);

return out;
