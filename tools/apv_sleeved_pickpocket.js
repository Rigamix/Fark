/* D20 - a sleeved Pickpocket binds nobody once anything else occupies G._tell.
 *
 * The caller already asks the rule system:
 *     if(_ruleActive('pickpocket','p')){setTimeout(_maybeFireCutpurse,650);}
 * and the callee re-asked a different question - what is in G._tell - and
 * refused. _ruleActive is symmetric for a sleeve (`if(G._sleeve===id)return
 * true`) while _applySleeve installs into G._tell only when it is EMPTY, so a
 * sleeved pickpocket over a seat carrying any other rule is live by the rule
 * system and invisible to the function that implements it.
 *
 * THREE ARMS, matching D20's own matrix, and the first and third are controls:
 *   A  the tell IS pickpocket          - must fire (it always did)
 *   B  tell last_call + sleeve         - the bug: _ruleActive true, no palm
 *   C  tell + sleeve both pickpocket   - must fire (it always did)
 * A fix that made the palm fire unconditionally would pass B and break nothing
 * visible - C alone would not catch it, but a fourth arm does:
 *   D  no pickpocket anywhere          - must NOT fire
 *
 * The palm is randomised at `chance` (.30), so each arm is driven until it
 * fires or a generous attempt budget runs out, and the ATTEMPT COUNT is
 * reported: an arm that "did not fire" in three tries would prove nothing.
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

tap(document.getElementById('hsBtnBottom')); await sleep(1800);
await until(() => { const d = document.querySelector('.nrdie'); return d && d._floatDone; }, 9000);
tap(document.querySelector('.nrdie')); await sleep(1300);
tap(document.getElementById('nrTakeBtn')); await sleep(2200);
await until(() => [...document.querySelectorAll('.ptcard')].filter(vis).length > 0, 9000);
const pc = [...document.querySelectorAll('.ptcard')].filter(vis)[0]; if (pc) { tap(pc); await sleep(1700); }
const sit = [...document.querySelectorAll('span,div,button')].filter(e => vis(e) && e.children.length <= 1
  && /^SIT\s*DOWN$/i.test((e.textContent || '').trim()))[0];
if (sit) { tap(sit); if (sit.parentElement) tap(sit.parentElement); }
if (!(await until(() => vis(document.getElementById('screen-match')), 9000))
 || !(await until(() => typeof G !== 'undefined' && G && G.phase === 'idle', 30000))) {
  return { skip: 'setup did not reach an idle match' };
}

const v = {}, notes = {};
const PP = _tellById('pickpocket');
notes._tell = PP ? { id: PP.id, chance: PP.chance } : null;
v.pickpocketRuleExists = !!(PP && PP.id === 'pickpocket');

/* one attempt: a fresh pool, then the function under test.
   MEASURED ON THE SYNCHRONOUS MARKER, not the pool. The first version of this
   probe watched G.pool.length and reported ZERO palms in all four arms on both
   builds - including control A, which has always worked. The removal happens
   inside a setTimeout behind a 650ms flight animation, so the pool had not
   changed yet when the check ran. `victim.el.classList.add('die-palmed')` is
   what the palm does synchronously once it has committed to a victim, so that
   is what a synchronous probe can honestly read. */
function attempt() {
  G.pCards = (G.pCards || []).filter(c => c !== 'iron_grip');   /* the counter-card */
  G.pool = [1,5,2,3,4,6].map((val,i) => ({lane:i, mat:'bone', val:val, committed:false,
    _frozen:false, sel:false, ench:null, el:document.createElement('div')}));
  try { _maybeFireCutpurse(); } catch (e) { notes._err = String(e).slice(0,80); }
  return G.pool.some(d => d.el && d.el.classList.contains('die-palmed'));
}
function drive(setup, budget) {
  setup();
  let fired = false, n = 0;
  for (; n < budget && !fired; n++) fired = attempt();
  return { fired: fired, attempts: n };
}
const BUDGET = 120;   /* at chance .30, P(miss 120 times) is vanishing */

const A = drive(() => { G._tell = {id:'pickpocket', chance:.30}; G._sleeve = null; G._sealRule = null; }, BUDGET);
const B = drive(() => { G._tell = {id:'last_call'};              G._sleeve = 'pickpocket'; G._sealRule = null; }, BUDGET);
const C = drive(() => { G._tell = {id:'pickpocket', chance:.30}; G._sleeve = 'pickpocket'; G._sealRule = null; }, BUDGET);
const D = drive(() => { G._tell = {id:'last_call'};              G._sleeve = null; G._sealRule = null; }, BUDGET);
notes._arms = { A_tellIsPickpocket:A, B_sleevedOverOtherTell:B, C_both:C, D_noneAnywhere:D };
notes._ruleActiveInB = (() => { G._tell = {id:'last_call'}; G._sleeve = 'pickpocket';
  return { p:_ruleActive('pickpocket','p'), o:_ruleActive('pickpocket','o') }; })();

v.firesWhenTellIsPickpocket = A.fired;          /* control */
v.firesWhenSleevedOverAnotherTell = B.fired;    /* the finding */
v.firesWhenBoth = C.fired;                      /* control */
v.silentWhenPickpocketIsNowhere = !D.fired;     /* the over-correction control */

for (const k of Object.keys(v)) { if (k[0] === '_') { notes[k] = v[k]; delete v[k]; } }
return { verdict: v, notes: notes };
