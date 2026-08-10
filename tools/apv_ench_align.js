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

/* REACH THE MATCH BEFORE AUDITING IT. The first run of this probe returned
   null for all four checks - including the two synthetics that touch no UI -
   because shoot.js loads a FRESH page at the menu and (typeof G!=='undefined'?G:null) does not exist
   there. It audited a match that was never started. This is the run-start
   sequence the rest of the suite uses. */
tap(document.getElementById('hsBtnBottom')); await sleep(1800);
await until(() => { const d = document.querySelector('.nrdie'); return d && d._floatDone; }, 9000);
tap(document.querySelector('.nrdie')); await sleep(1300);
tap(document.getElementById('nrTakeBtn')); await sleep(2200);
await until(() => [...document.querySelectorAll('.ptcard')].filter(vis).length > 0, 9000);
const pc = [...document.querySelectorAll('.ptcard')].filter(vis)[0]; if (pc) { tap(pc); await sleep(1700); }
const sit = [...document.querySelectorAll('span,div,button')].filter(e => vis(e) && e.children.length <= 1
  && /^SIT\s*DOWN$/i.test((e.textContent || '').trim()))[0];
if (sit) { tap(sit); if (sit.parentElement) tap(sit.parentElement); }
const _atMatch = await until(() => vis(document.getElementById('screen-match')), 9000);
const _idle    = await until(() => typeof G !== 'undefined' && G && G.phase === 'idle', 30000);
if (!_atMatch || !_idle || typeof G === 'undefined' || !G) {
  return { skip: 'setup did not reach an idle match (atMatch=' + _atMatch + ' idle=' + _idle + ')' };
}


/* apv_ench_align — _enchArr stays aligned with matchDice when a die is removed.
 *
 * _enchArr is indexed by LANE. Break spliced both; steal_die (royal_seizure,
 * blessed_confiscation) and Sacrifice spliced only matchDice, so every enchant
 * above the removed lane moved onto a different die - silently.
 *
 * Tested by ACTUALLY REMOVING A DIE and checking the brand still sits on the
 * die it belongs to, rather than by looking for the splice in the source. A
 * source check would pass on a splice with the wrong index.
 */
const v = {};
if (typeof G === 'undefined' || !G) return { skip: 'no match' };

/* a known board: six dice, a brand on lane 4 only */
function board(){
  G.matchDice = ['bone','bone','bone','jade','amber','bone'];
  G._enchArr  = [null,null,null,null,'loaded',null];
}
/* the brand must still be on 'amber' after a removal below it */
function brandedMat(){
  const i = (G._enchArr||[]).findIndex(e => e === 'loaded');
  return i < 0 ? null : G.matchDice[i];
}

board();
v._before = { mat: brandedMat(), len: [G.matchDice.length, G._enchArr.length] };

/* remove lane 1, the way every fixed site now does */
G.matchDice.splice(1,1);
if (G._enchArr && 1 < G._enchArr.length) G._enchArr.splice(1,1);
v._afterFixed = { mat: brandedMat(), len: [G.matchDice.length, G._enchArr.length] };
v.brandStaysPut = brandedMat() === 'amber';
v.lengthsMatch  = G.matchDice.length === G._enchArr.length;

/* and the shape of the OLD bug, to prove the test can see it */
board();
G.matchDice.splice(1,1);               /* no _enchArr splice - the bug */
v._afterBug = { mat: brandedMat(), len: [G.matchDice.length, G._enchArr.length] };
v.testDetectsTheBug = brandedMat() !== 'amber';

/* every removal keeps the two arrays aligned.
   THIS WENT RED WITHOUT THE GAME CHANGING. It counted splices inside doBust,
   startPTurn and runOppTurn and found ZERO of either - md:0, ea:0 - so `md>0`
   failed and it reported the alignment bug as back. It was not: removal was
   consolidated into _removeDieAt (PR5) and those three no longer splice at all.
   A count of N sites cannot survive N becoming 1, and this probe's own header
   argues against source checks - "a source check would pass on a splice with
   the wrong index" - three lines before making one.
   So it now does what the header says. The structural half asks the stronger
   question the refactor made askable: not "is every site correct" but "is there
   only one site". The behavioural half runs it. */
v.allSitesFixed = (function(){
  try {
    if (typeof _removeDieAt !== 'function') { v._noCanonicalPath = true; return false; }
    const fn = _removeDieAt.toString();
    const md = (fn.match(/G\.matchDice\.splice\(/g)||[]).length;
    const ea = (fn.match(/G\._enchArr\.splice\(/g)||[]).length;
    v._counts = { matchDiceInRemoveDieAt: md, enchArrInRemoveDieAt: ea,
      documentWide: (document.documentElement.outerHTML.match(/G\.matchDice\.splice\(/g)||[]).length };
    if (md !== 1 || ea !== 1 || v._counts.documentWide !== 1) return false;
    /* and the real path keeps the brand on its own die */
    board();
    _removeDieAt(1);
    v._afterCanonical = { mat: brandedMat(), len: [G.matchDice.length, G._enchArr.length] };
    return brandedMat() === 'amber' && G.matchDice.length === G._enchArr.length;
  } catch(e) { v._canonErr = String(e).slice(0,80); return false; }
})();

const notes = {};
for (const k of Object.keys(v)) { if (k[0] === '_') { notes[k] = v[k]; delete v[k]; } }
return { verdict: v, notes: notes };
