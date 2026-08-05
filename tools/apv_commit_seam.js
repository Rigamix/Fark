/* apv_commit_seam — the rival commits real dice through the player's own path.
 *
 * P479 made famCommitBonus seat-aware and had the rival call it with actor 'o'.
 * The point is REUSE: one derivation of isTriple/isStraight/jade/hitFirst/
 * hitLast for both seats, because two would be free to drift - which is what
 * five of tonight's findings turned out to be.
 *
 * So this checks the SHARED FUNCTION behaves correctly for both actors, rather
 * than driving a rival turn and hoping one fires. The derivation is the thing
 * under test; the wiring is checked separately from the shipped source.
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

/* A REAL MATCH IS REQUIRED. famCommitBonus reads G, and shoot.js loads at the
   menu where G is null - a first run returned null for every derivation check
   because the helper bailed before calling anything. */
await until(() => typeof famCommitBonus === 'function' && typeof famFire === 'function', 15000);
const v = {}, seen = [];
const _real = famFire;
famFire = function (hook, ev) {
  try { if (hook === 'commit') seen.push({actor:ev&&ev.actor, n:(ev&&ev.sel||[]).length,
        isTriple:ev&&ev.isTriple, isStraight:ev&&ev.isStraight}); } catch(e) {}
  return _real.apply(this, arguments);
};

/* the shared derivation, exercised for each seat with the SAME dice */
const trip = [{val:5,mat:'bone'},{val:5,mat:'bone'},{val:5,mat:'bone'}];
function fire(sel, actor, fam) {
  const g = (typeof G !== 'undefined' && G) ? G : null;
  if (!g) return null;
  const savedP = g.pF, savedO = g.oF, savedPool = g.pool, savedOpp = g.oppDice;
  g.pF = fam; g.oF = fam; g.pool = sel.slice(); g.oppDice = sel.slice();
  const n = seen.length;
  let out = null;
  try { out = famCommitBonus(sel, 1000, actor); } catch(e) { v._err = String(e).slice(0,70); }
  g.pF = savedP; g.oF = savedO; g.pool = savedPool; g.oppDice = savedOpp;
  return { out: out, ev: seen.slice(n)[0] || null };
}
/* a non-empty family list is required or the function returns early by design */
const fam = [{id:'bloom', tier:1}];
const P = fire(trip, 'p', fam), O = fire(trip, 'o', fam);
v._p = P && P.ev; v._o = O && O.ev;

v.bothSeatsRaise = !!(P && P.ev && O && O.ev);
v.actorsAreRight = !!(P && P.ev && P.ev.actor === 'p' && O && O.ev && O.ev.actor === 'o');
/* SAME dice must derive the SAME shape - that is the whole reason for one path */
v.sameDerivation = !!(P && O && P.ev && O.ev
  && P.ev.isTriple === O.ev.isTriple && P.ev.isStraight === O.ev.isStraight
  && P.ev.n === O.ev.n);
v.tripleDetected = !!(P && P.ev && P.ev.isTriple === true);

/* the rival's call site is wired, and after the reroll block that can void it */
v.wiredAfterReroll = (function(){
  try {
    const t = runOppTurn.toString();
    const sel = t.indexOf('var _oSel=[]');
    const rr  = t.indexOf('_playerRerollKeptArmed');
    const cm  = t.indexOf("famCommitBonus(_oSel,total,'o')");
    v._idx = {sel:sel, reroll:rr, commit:cm};
    return sel >= 0 && rr >= 0 && cm > rr;
  } catch(e) { return false; }
})();

famFire = _real;
const notes = {};
for (const k of Object.keys(v)) { if (k[0] === '_') { notes[k] = v[k]; delete v[k]; } }
return { verdict: v, notes: notes };
