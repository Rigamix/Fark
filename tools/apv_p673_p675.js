/* P673-P675 MEASURED: the focus polish, Raritas in every bubble, the pause
 * icon's box, and Whisper's hand actually hiding.
 * SUITE: exclude
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

const out = {};
out.raritasLoadable = await document.fonts.load('italic 600 16px Raritas').then(f => f.length > 0).catch(e => String(e));

for (let a = 0; a < 3; a++) { tap(document.getElementById('hsBtnBottom')); await sleep(2000);
  await until(()=>{const d=document.querySelector('.nrdie');return d&&d._floatDone;},9000);
  tap(document.querySelector('.nrdie')); await sleep(1400);
  tap(document.getElementById('nrTakeBtn')); await sleep(2400);
  if (await until(()=>typeof launchSeat==='function'&&S&&S.run,9000)) break; }

_getS();
famApplyPick({ id: 'powder_keg', tier: 2 });
try { G = null; } catch (e) {}
launchBossMatch();
if (!await until(() => typeof G !== 'undefined' && G && G.pF && G.pF.length, 14000)) return { err: 'no match' };
await sleep(2600);

/* ── P673: the focus tip ────────────────────────────────────────────── */
famCardTap(0);
await sleep(350);
const tip = document.getElementById('cardFocusTip');
if (tip) {
  const name = tip.querySelector('.cft-name'), body = tip.querySelector('.cft-body');
  const ncs = getComputedStyle(name), bcs = getComputedStyle(body);
  out.focus = {
    title: name.textContent,
    noNumeral: !/\sII|\sIII/.test(name.textContent),
    titleSize: ncs.fontSize,
    noShadow: ncs.textShadow === 'none' && bcs.textShadow === 'none',
    justified: bcs.textAlign === 'justify',
    lastLine: bcs.textAlignLast,
    tracking: bcs.letterSpacing,
    tipWidth: tip.getBoundingClientRect().width.toFixed(1),
    noTeachLine: !/drag past/.test(tip.textContent)
  };
  /* the tier pip above the art: the card is tier 2, pip must be hit-testable */
  const card = document.querySelector('#famRowP .fcv');
  const pip = card.querySelector('.fcvTier');
  if (pip) {
    const pr = pip.getBoundingClientRect();
    const at = document.elementFromPoint(pr.left + pr.width/2, pr.top + pr.height/2);
    out.pip = { exists: true, zIndex: getComputedStyle(pip).zIndex,
      topmostAtItsCentre: at === pip || pip.contains(at) };
  } else out.pip = { exists: false };
}
famCardTap(0); await sleep(150);

/* ── P674: the bubble speaks Raritas and the example fits two lines ─── */
DLG.oppKey = DLG.oppKey || 'GROG';
DLG.show("Heard something odd today. Someone important, coming through. Nobody's said a name yet.");
await sleep(600);
const dt = document.getElementById('dlgText');
const dcs = getComputedStyle(dt);
out.bubble = {
  family: dcs.fontFamily.slice(0, 40),
  isRaritas: /Raritas/.test(dcs.fontFamily),
  style: dcs.fontStyle, weight: dcs.fontWeight,
  lines: Math.round(dt.getBoundingClientRect().height / parseFloat(dcs.lineHeight))
};
try { DLG.hide && DLG.hide(); } catch (e) {}

/* ── P675a: the pause box ───────────────────────────────────────────── */
const mp = document.getElementById('matchPause');
const mpi = mp && mp.querySelector('img');
out.pause = mp ? {
  aspect: getComputedStyle(mp).aspectRatio,
  src: mpi ? mpi.src.split('/').pop() : null,
  imgLoaded: mpi ? mpi.naturalWidth : 0,
  boxVsImg: (() => { const b = mp.getBoundingClientRect(), i = mpi.getBoundingClientRect();
    return { bw: b.width.toFixed(1), bh: b.height.toFixed(1), iw: i.width.toFixed(1), ih: i.height.toFixed(1) }; })()
} : null;

/* ── P675b: whisper's hand hides, and firing reveals ────────────────── */
G.oCards.push('old_roads');
famRenderRow();
await sleep(200);
const row = document.getElementById('famRowO');
out.hidden = {
  handHidden: _npcHandHidden(),
  faceDown: row.querySelectorAll('.fcv.facedown').length,
  npcTotal: (G.oCards||[]).length,
  artImgsInFaceDown: [...row.querySelectorAll('.fcv.facedown img')].length
};
/* tap a hidden card: says HIDDEN, not the rules */
const hidCid = G.oCards[0];
npcOppTap(hidCid);
await sleep(200);
const t2 = document.getElementById('cardFocusTip');
out.hidden.tapSaysHidden = t2 ? /HIDDEN/.test(t2.textContent) && !/gold|point|bank/i.test(t2.querySelector('.cft-body').textContent) : null;
npcOppTap(hidCid); await sleep(120);

/* firing reveals THAT card and only it */
triggerCard(hidCid, 'FIRES', false);
await sleep(250);
out.reveal = {
  revealedFlag: !!(G._npcRevealed && G._npcRevealed[hidCid]),
  thatCardFaceUp: !(row.querySelector('.fcv[data-cid="' + hidCid + '"]')||{classList:{contains:()=>null}}).classList.contains('facedown'),
  thatCardHasArtOrCover: !!row.querySelector('.fcv[data-cid="' + hidCid + '"] .fcvIn'),
  othersStillDown: row.querySelectorAll('.fcv.facedown').length
};
return out;
