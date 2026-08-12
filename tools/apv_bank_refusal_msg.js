/* WHEN A GROG MATCH REFUSES A BANK, WHAT DOES THE PLAYER ACTUALLY READ?
 * SUITE: exclude
 *
 * Denis: "When I can't bank for example in a grog match because my score ain't
 * high enough there should be a text that tells me so."
 *
 * The message already existed. handleBank writes
 *     setStatusMsg('LAST CALL — NOTHING UNDER 800','red')
 * and then, eight lines later and unconditionally,
 *     setStatusMsg('BANKED 0 LAST CALL — BANK <800','gold')
 * to the same element. So the refusal was on screen for no frames and the
 * player saw a gold success line for a rejected bank. Ambrose's Reckoning has
 * the identical shape.
 *
 * This reads the element AFTER handleBank returns - the only reading that can
 * tell "written" from "still there".
 *
 * The rule is switched on through the game's own gate (_ruleActive reads
 * G._sealRule), not by editing handleBank's inputs. G.kept IS seeded, and that
 * is a deliberate scope call: what is under test is which message survives, not
 * how dice come to be kept.
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

_getS();
try { G = null; } catch (e) {}
launchBossMatch();
if (!await until(() => typeof G !== 'undefined' && G && G.pool, 14000)) return { err: 'no match' };
await sleep(2400);

/* RECORD THE CALLS, NOT THE ELEMENT. Reading the DOM after handleBank returns
   measured nothing: banking hands the turn over and the status is cleared on
   the way out, so all three cases - including the normal control - came back
   empty. The defect was never about the final pixel anyway; it was a SECOND
   setStatusMsg call overwriting the first. So capture the sequence. */
let CALLS = [];
const realSSM = window.setStatusMsg;
window.setStatusMsg = function (m, c) { CALLS.push({ m: String(m), c: c || '' }); return realSSM.apply(this, arguments); };
const read = () => CALLS.slice();

const out = {};

/* ── LAST CALL: a 150 bank against an 800 floor ─────────────────────── */
G._tell = _tellById('last_call');
G._sealRule = 'last_call';
G._tellState = G._tellState || {};
out.ruleActive = _ruleActive('last_call', 'p');
G.kept = [{ pts: 150, vals: [5], dice: [] }];
G._turnBonusPot = 0;
CALLS = []; G.phase = 'choosing';
try { handleBank(); } catch (e) { out.lastCallThrew = String(e); out.stack = String(e.stack||'').slice(0, 400); }
await sleep(40);
out.lastCall = read();
out.lastCallRefusalStands = /LAST CALL/.test(out.lastCall.text) && /red/.test(out.lastCall.cls);
out.lastCallShowsBanked   = /BANKED/.test(out.lastCall.text);

/* ── RECKONING: the same shape, three lines up in the same function ── */
await sleep(500);
G._sealRule = 'reckoning';
G._tell = _tellById('reckoning');
G._tellState = { lastNpcBank: 900 };
G.kept = [{ pts: 200, vals: [5], dice: [] }];
G._turnBonusPot = 0;
CALLS = []; G.phase = 'choosing';
try { handleBank(); } catch (e) { out.reckoningThrew = String(e); }
await sleep(40);
out.reckoning = read();
out.reckoningRefusalStands = /RECKONING/.test(out.reckoning.text) && /red/.test(out.reckoning.cls);
out.reckoningShowsBanked   = /BANKED/.test(out.reckoning.text);

/* ── and a NORMAL bank must still say BANKED ────────────────────────── */
await sleep(500);
G._sealRule = null; G._tell = null; G._tellState = {};
G.kept = [{ pts: 350, vals: [5], dice: [] }];
G._turnBonusPot = 0;
CALLS = []; G.phase = 'choosing';
try { handleBank(); } catch (e) { out.normalThrew = String(e); }
await sleep(40);
out.normal = read();
out.normalStillBanks = /BANKED/.test(out.normal.text);

return out;
