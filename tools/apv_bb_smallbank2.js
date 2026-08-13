/* Counterfactual: does the same line hold ONE line at width 191? SUITE: exclude */
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
_getS(); try { G = null; } catch (e) {}
launchBossMatch();
if (!await until(() => typeof G !== 'undefined' && G, 14000)) return { err: 'no match' };
await sleep(2600);
DLG.oppKey = DLG.oppKey || "GROG";
if (DLG.hideTimer) clearTimeout(DLG.hideTimer);
DLG.show("Small bank's still a bank.");
await sleep(400);
const textEl = document.getElementById('dlgText');
const lh = parseFloat(getComputedStyle(textEl).lineHeight);
const lines = w => { textEl.style.width = w; return +(textEl.scrollHeight / lh).toFixed(2); };
const out = {};
out.asShipped = { w: textEl.style.width, lines: +(textEl.scrollHeight/lh).toFixed(2) };
out.at190 = lines('190px');
out.at191 = lines('191px');
out.at192 = lines('192px');
/* and repeat the whole show 5x to see rounding flakiness */
out.repeats = [];
for (let i=0;i<5;i++){ DLG.hide(); await sleep(50); DLG.show("Small bank's still a bank."); await sleep(60);
  out.repeats.push({ w: textEl.style.width, lines: +(textEl.scrollHeight/lh).toFixed(2) }); }
return out;
