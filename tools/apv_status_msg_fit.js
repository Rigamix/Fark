/* HOW MUCH OF THE STATUS LINE ACTUALLY FITS?
 * SUITE: exclude
 *
 * Denis: "the text that appears to tell me what my cards do is too big and
 * cropped out."
 *
 * .status-msg is `white-space:nowrap` at 5cqw, so a message wider than the strip
 * cannot wrap and overflows BOTH edges - it is centred, so it loses the start
 * and the end at once, which is why his screenshot reads "RED — THEIR SHORT
 * FUSE IS BROKEN FOR THE".
 *
 * Measured here on the real element at the real font, in a real match:
 *   - the strip's usable width
 *   - scrollWidth for each of the corpus's longest real messages
 *   - the character budget one line actually has
 * A fix sized off the corpus alone would be guessing at the font.
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
if (!await until(() => typeof G !== 'undefined' && G && G.pF, 14000)) return { err: 'no match' };
await sleep(2400);

const el   = document.getElementById('statusBot');
const strip= document.getElementById('botStrip');
const screenW = document.getElementById('screen-match').getBoundingClientRect().width;
const cs = getComputedStyle(el);

/* the real messages, longest first, straight from the corpus */
const CORPUS = [
  'HAIR OF THE DOG — YOUR FIRST BANK NEXT MATCH IS DOUBLED',
  'TAMPERED — THEIR SHORT FUSE IS BROKEN FOR THE NIGHT',
  'ILL OMEN DECLARED — THEY BUST THIS TURN, OR PAY YOU DO',
  'FROZEN — IT KEEPS ITS FACE THROUGH REROLLS THIS TURN',
  'SLEIGHT READY — THEIR NEXT ROLL COMES BACK',
  'PICKPOCKET LIFTS 450',
  'NOT NOW'
];

const rows = [];
for (const m of CORPUS) {
  setStatusMsg(m, 'gold');
  await sleep(30);
  const r = el.getBoundingClientRect();
  rows.push({
    chars: m.length,
    scrollW: el.scrollWidth,
    clientW: el.clientWidth,
    boxW: +r.width.toFixed(1),
    boxLeft: +r.left.toFixed(1),
    boxRight: +r.right.toFixed(1),
    /* the two numbers that say "cropped": does the ink reach past the screen? */
    overflowsBox: el.scrollWidth > el.clientWidth + 1,
    offScreenLeft: +(0 - r.left).toFixed(1),
    offScreenRight: +(r.right - screenW).toFixed(1),
    lines: Math.round(r.height / (parseFloat(cs.lineHeight) || 1))
  });
}

return {
  screenW: +screenW.toFixed(1),
  strip: strip ? { w: +strip.getBoundingClientRect().width.toFixed(1) } : null,
  style: { fontSize: cs.fontSize, whiteSpace: cs.whiteSpace, lineHeight: cs.lineHeight,
           maxWidth: cs.maxWidth, letterSpacing: cs.letterSpacing },
  rows
};
