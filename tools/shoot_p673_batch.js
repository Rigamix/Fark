/* One frame with: the Raritas two-line bubble, the polished focus tip, the new
 * pause icon, and Whisper's face-down cards. SUITE: exclude */
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
_getS();
famApplyPick({ id: 'powder_keg', tier: 2 });
try { G = null; } catch (e) {}
launchBossMatch();
if (!await until(() => typeof G !== 'undefined' && G && G.pF && G.pF.length, 14000)) return { err: 'no match' };
/* WAIT FOR THE TURN, not a fixed sleep: startPTurn's famRenderRow closes any
   open focus, so a tap before it is erased a second later - which is exactly
   what a fixed 2600ms sleep kept photographing (diagnosed via a removal-
   primitive wrap: the killer stack was startPTurn -> famRenderRow -> close). */
await until(() => G && G.phase === 'idle', 15000);
await sleep(500);

G.oCards.push('old_roads');
famRenderRow();
await sleep(200);
DLG.oppKey = DLG.oppKey || 'GROG';
DLG.show("Heard something odd today. Someone important, coming through. Nobody's said a name yet.");
famCardTap(0);
await sleep(600);
const tip=document.getElementById('cardFocusTip');
const w0=tip?tip.querySelector('.cft-name span.w'):null;
const wcs=w0?getComputedStyle(w0):null;
return { faceDown: document.querySelectorAll('#famRowO .fcv.facedown').length,
  tipExists: !!tip,
  cardFocused: !!document.querySelector('#famRowP .fcv.focus'),
  word0: w0?{opacity:wcs.opacity,animName:wcs.animationName,animDelay:wcs.animationDelay,
             animPlayState:wcs.animationPlayState,display:wcs.display,color:wcs.color,
             fontSize:wcs.fontSize,rect:JSON.parse(JSON.stringify(w0.getBoundingClientRect())),
             running:w0.getAnimations().length}:null,
  tipStyleLeftTop:(tip?tip.style.left+' / '+tip.style.top:null),
  tipComputedTop:tip?getComputedStyle(tip).top:null,
  screenScroll:document.getElementById('screen-match').scrollTop,
  occluder:(function(){const r=w0.getBoundingClientRect();
    const e=document.elementFromPoint(r.left+r.width/2,r.top+r.height/2);
    const chain=[];let n=e;while(n&&chain.length<6){chain.push(n.id||n.className||n.tagName);n=n.parentElement;}
    return chain;})(),
  tipInScreen:document.getElementById('screen-match').contains(tip),
  tipParent:tip.parentElement?(tip.parentElement.id||tip.parentElement.className):null };
