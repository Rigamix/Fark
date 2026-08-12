/* WHICH ROW DOES A REAL RUN PUT THE PLAYER'S CARDS IN?
 * SUITE: exclude
 *
 * Denis: "Can't drag anything in match", still, after P656 made #playerCards
 * hit-testable. So the question stops being "can the touch reach the card" and
 * becomes "is there a card there at all".
 *
 * THE DRAFT WRITES S.run.fcards (the family engine). #playerCards is built from
 * G.pCards, which comes from S.run.cards - the legacy four-slot loadout. If the
 * draft never writes that, the drag row is empty in every real run and every
 * verification that seeded S.run.cards by hand was testing a row the player
 * never fills. That is the claim; this counts both rows after taking a card
 * through the real draft.
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
for(let a=0;a<3;a++){ tap(document.getElementById('hsBtnBottom')); await sleep(2000);
  await until(()=>{const d=document.querySelector('.nrdie');return d&&d._floatDone;},9000);
  tap(document.querySelector('.nrdie')); await sleep(1400);
  tap(document.getElementById('nrTakeBtn')); await sleep(2400);
  if(await until(()=>typeof launchSeat==='function'&&S&&S.run,9000)) break; }
if (typeof launchSeat !== 'function') return { skip: 'launchSeat unreachable' };

/* take a card THE WAY THE GAME DOES - through the draft's own apply */
_getS();
const before = { runCards: (S.run.cards||[]).filter(Boolean).slice(),
                 fcards: (S.run.fcards||[]).map(c=>c.id) };
const offer = { id: FAM_CARDS.filter(c=>c.fam!=='tavern')[0].id, tier:1 };
famApplyPick(offer);
const after = { runCards: (S.run.cards||[]).filter(Boolean).slice(),
                fcards: (S.run.fcards||[]).map(c=>c.id) };

try { G = null; } catch (e) {}
launchSeat(0);
if (!await until(() => typeof G !== 'undefined' && G && G.pCards !== undefined, 14000))
  return { err: 'match never started' };
await sleep(2600);

return {
  arm: 'which-row',
  draftWrote: { before, after,
                wroteToLegacyLoadout: after.runCards.length !== before.runCards.length,
                wroteToFamily: after.fcards.length !== before.fcards.length },
  inMatch: { gPCards: (G.pCards||[]).slice(), gPF: (G.pF||[]).map(c=>c.id) },
  rows: { playerCardsMcards: document.querySelectorAll('#playerCards .mcard').length,
          famRowPCards: document.querySelectorAll('#famRowP .fcv').length },
  /* the drag is bound in initCardDrag, which buildCBar calls for .mcard only */
  draggableElements: document.querySelectorAll('#playerCards .mcard').length,
  tappableFamilyCards: document.querySelectorAll('#famRowP .fcv').length,
};
