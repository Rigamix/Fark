/* HOW WIDE DOES THE BUBBLE HAVE TO BE FOR THREE LINES?
 * SUITE: exclude   (a measurement)
 *
 * Denis: "should not have 4 lines, 3 at most and wider text."
 *
 * Narrowing cannot fix a line count - the shrink-to-fit search minimises width
 * AT the natural count, so a line that needs four at the cap still needs four.
 * The cap itself has to move. This measures how far, against the real corpus
 * rather than against the one line that happened to be on screen: every line
 * the game can actually say, laid out in the real element at the real font, at
 * a range of candidate caps.
 *
 * WHAT IT REPORTS is the worst case at each cap, not the average - a cap that
 * holds three lines for most lines and four for the longest has not solved
 * anything, because the longest lines are exactly the ones that overflow.
 */
const sleep = ms => new Promise(r => setTimeout(r, ms));
const until = async (fn, ms) => { const t0 = Date.now();
  while (Date.now() - t0 < ms) { try { if (fn()) return true; } catch(e){} await sleep(60); } return false; };
const vis = el => { if (!el || !el.isConnected) return false;
  const s = getComputedStyle(el), r = el.getBoundingClientRect();
  return s.display !== 'none' && s.visibility !== 'hidden' && +s.opacity > 0.05 && r.width > 1 && r.height > 1; };
const tap = el => { if (!vis(el)) return false; const r = el.getBoundingClientRect();
  const o = {bubbles:true, cancelable:true, clientX:r.left+r.width/2, clientY:r.top+r.height/2};
  el.dispatchEvent(new PointerEvent('pointerdown',o)); el.dispatchEvent(new PointerEvent('pointerup',o));
  el.dispatchEvent(new MouseEvent('click',o)); return true; };

for (let a = 0; a < 3; a++) {
  tap(document.getElementById('hsBtnBottom')); await sleep(2000);
  await until(() => { const d = document.querySelector('.nrdie'); return d && d._floatDone; }, 9000);
  tap(document.querySelector('.nrdie')); await sleep(1400);
  tap(document.getElementById('nrTakeBtn')); await sleep(2400);
  if (await until(() => typeof launchSeat === 'function' && S && S.run, 9000)) break;
}
if (typeof launchSeat !== 'function') return { skip: 'launchSeat unreachable' };
try { G = null; } catch (e) {}
launchSeat(0);
if (!await until(() => typeof G !== 'undefined' && G && G.pCards !== undefined, 14000))
  return { err: 'match never started' };
await sleep(1500);

/* the real corpus: every line PATRON_LINES can produce, plus the boss barks in
   OPP_DIALOGUE, because both go through this same box */
const lines = [];
try { PATRON_LINES.forEach(r => { if (r && r.t) lines.push(r.t); }); } catch (e) {}
try { Object.keys(OPP_DIALOGUE).forEach(k => {
  const d = OPP_DIALOGUE[k];
  Object.keys(d).forEach(cat => { const v = d[cat];
    if (Array.isArray(v)) v.forEach(t => { if (typeof t === 'string') lines.push(t); }); });
}); } catch (e) {}
if (!lines.length) return { err: 'no dialogue corpus found' };

const tx = document.getElementById('dlgText');
const sc = document.getElementById('dlgScroll');
const box = document.getElementById('dlgBox');
box.classList.add('show');
const lineH = parseFloat(getComputedStyle(tx).lineHeight);

/* measure a line at an explicit TEXT width, through the real element so the
   real font, letter-spacing and word-spacing all apply */
/* THE CONTROL THIS NEEDED FROM THE START: report the width the element
   ACTUALLY got, not the one that was asked for. A first run returned "5 lines"
   at every candidate from 215px to 368px - a number that does not move when its
   input moves by 71% is not measuring that input. The scroll's own max-width
   was constraining the text whatever width was set on it, so widening it did
   nothing. The cap has to come off the PARENT for the child's width to mean
   anything. */
function linesAt(text, wpx) {
  sc.style.maxWidth = 'none';
  tx.innerHTML = jitterText('“' + text + '”');
  tx.style.whiteSpace = '';
  tx.style.width = wpx + 'px';
  void tx.offsetWidth;
  return { lines: Math.round(tx.scrollHeight / lineH), got: tx.offsetWidth };
}

/* the widest text box each cap allows: cap% of the shell, less the scroll's
   own horizontal padding */
const shell = document.querySelector('.dlg-box .dlg-inner').offsetWidth;
const padX = parseFloat(getComputedStyle(sc).paddingLeft) + parseFloat(getComputedStyle(sc).paddingRight);

const CAPS = [66, 72, 78, 84, 90, 94];
const PADS = [68, 48, 36];   /* current 34+34, then tighter */
const out = { corpus: lines.length, shell, currentPadX: padX, lineHeight: lineH, caps: [] };

/* only the long tail matters - sort by character count and take the worst 40 */
const worst = lines.slice().sort((a, b) => b.length - a.length).slice(0, 40);
out.longest = worst[0];
out.longestChars = worst[0].length;

CAPS.forEach(cap => {
  PADS.forEach(pad => {
    const wpx = Math.floor(shell * cap / 100) - pad;
    let over3 = 0, max = 0, gotW = 0;
    worst.forEach(t => { const r = linesAt(t, wpx);
      if (r.lines > 3) over3++; if (r.lines > max) max = r.lines; gotW = r.got; });
    out.caps.push({ cap: cap + '%', padX: pad, askedW: wpx, gotW: gotW,
                    applied: Math.abs(gotW - wpx) < 3, worstLines: max, linesOver3: over3 });
  });
});
tx.style.width = '';
box.classList.remove('show');
return out;
