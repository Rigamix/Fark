/* D22 - Drill Order's roll cap is derived four different ways, and one of them
 * is a literal.
 *
 *   24405  _drillCap        (G._tell.id==='drill_order')?G._tell:_tellById(...)   player
 *   29209  runOppTurn.step  oppRollNum>=3                                        LITERAL
 *   13288  famRenderRow     (_st&&_st.maxRolls)||3                               sleeve chip
 *   25174  hot-dice DLG     G._tell.maxRolls||3, gated on G._tell.id             dialogue
 *
 * THE DEFECT IS LATENT AND THAT IS WHY IT NEEDS DRIVING, not reading: the RUNGS
 * record carries maxRolls:3, so all four agree TODAY. The probe therefore
 * RETUNES THE RECORD - the exact maintenance act the defect is waiting for - and
 * asks whether every surface moved with it. A probe that only read the current
 * build would report four agreeing numbers and call it clean.
 *
 * ARMS
 *   A  player cap        _drillCap().cap must follow the record
 *   B  sleeve chip       famRenderRow's "SLEEVED: ... n/N" must follow it too
 *   C  the rival         driven: seal the rule, run real opponent turns, count
 *                        the roll seam. Capped at the literal 3 before the fix.
 *   C-control            THE SAME COUNT WITH THE RULE OFF. If the rival cannot
 *                        reach 4 rolls unrestricted, "never exceeded 3" measures
 *                        the dice, not the cap, and arm C is void. Reported as
 *                        its own verdict key so a void arm is visible rather
 *                        than passing quietly.
 *   D  the DLG gate      a SLEEVED Drill Order at the cap must still get the
 *                        "hot dice rolls free" line. 25174 re-asks G._tell
 *                        instead of _ruleActive - D20's shape exactly - so a
 *                        sleeve over any other tell was enforced in silence.
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
const REC = _tellById('drill_order');
if (!REC) return { skip: 'no drill_order record' };
const WAS = REC.maxRolls;
const RETUNE = 5;                       /* the maintenance act the defect waits for */
REC.maxRolls = RETUNE;
notes._record = { before: WAS, retunedTo: REC.maxRolls };
v.retuneTookOnTheRecord = REC.maxRolls === RETUNE;    /* control */

/* A - the player's cap, through the real _drillCap */
G._sealRule = 'drill_order'; G._sleeve = null; G._tell = null;
G.turnRollCount = 0; G.pool = [];
const capP = (_drillCap() || {}).cap;
notes._armA = { cap: capP };
v.playerCapFollowsTheRecord = capP === RETUNE;

/* B - the sleeve chip, through the real famRenderRow */
G._sealRule = null; G._sleeve = 'drill_order'; G._tell = { id: 'last_call', name: 'LAST CALL', desc: '' };
G.turnRollCount = 1;
try { famRenderRow(); } catch (e) { notes._bErr = String(e).slice(0, 80); }
const chip = [...document.querySelectorAll('div')].filter(e => /SLEEVED:/.test(e.textContent || '')
  && (e.textContent || '').length < 120).map(e => e.textContent.trim())[0] || '';
notes._armB = { chip: chip };
v.sleeveChipFollowsTheRecord = new RegExp('/' + RETUNE + '\\b').test(chip);

/* D - the hot-dice dialogue gate, asked the way the rule system asks it.
       Not the DOM line (that needs a real hot-dice moment) but the CONDITION
       the line is gated on, evaluated in the sleeved state arm B set up. */
const gateOldShape = !!(G && G._tell && G._tell.id === 'drill_order');
const gateRuleSystem = !!_ruleActive('drill_order', 'p');
notes._armD = { sleeve: G._sleeve, tell: G._tell && G._tell.id,
                asksGTell: gateOldShape, asksRuleSystem: gateRuleSystem };
/* THIS ASSERTS THE PREMISE, NOT THE FIX, and the distinction is why it is
   worded this way. The first version required both questions to agree - a key
   that can NEVER pass, because their disagreement in a sleeved state is the
   entire defect, and it would have sat red in the suite forever until someone
   stopped reading it. What is true here before and after P567 is that the rule
   is LIVE (_ruleActive true) while the slot the dialogue used to read is EMPTY
   of it. That the gate now asks the rule system is a code-level fact, asserted
   by P567's own gate (`G._tell.id==='drill_order'&&` must be 0), because the
   hot-dice line needs a real hot-dice moment to observe and this probe does not
   manufacture one. */
v.sleevedDrillOrderIsLiveButAbsentFromGTell = gateRuleSystem && !gateOldShape;

/* C - the rival, driven. Count the opponent's roll seam through a wrapped
       famFire; unwrapped in a finally so a throw cannot leave the game stubbed
       for whatever runs next in this page. */
async function oppRolls(ruleOn, trials) {
  const seen = [];
  const real = window.famFire;
  /* AND THE RIVAL NEVER BANKS VOLUNTARILY. Without this the persona banks after
     one roll and every arm reads 1 - the void check fired twice before this
     line existed. Stubbing oppShouldBank isolates the ROLL CAP from the banking
     policy, which is the only variable this arm is about: the turn now ends on
     a bust or on the cap, and nothing else. */
  const realBank = window.oppShouldBank;
  try {
    if (typeof realBank === 'function') window.oppShouldBank = function () { return false; };
    for (let t = 0; t < trials; t++) {
      let n = 0;
      window.famFire = function (hook, ev) { if (hook === 'roll' && ev && ev.actor === 'o') n++; return real.apply(this, arguments); };
      G._sealRule = ruleOn ? 'drill_order' : null; G._sleeve = null; G._tell = null;
      G.oPts = 0; G.pPts = 0; G.target = 999999;   /* never finish on the target */
      G._endMatchFired = false;
      /* THE TURN'S OWN FLAG, after two worse instruments. Waiting on
         `G.phase !== 'opp'` returned instantly (no such phase) and counted only
         the synchronous roll. Waiting for a 1.2s quiet period was WORSE than
         useless: the gap between steps is _oppDelay(1900), so it declared the
         turn over mid-turn, started the next trial, and let the previous turn's
         ghost timers increment the new trial's counter - which is how an arm
         with a hard cap of 3 reported 4. `G._oppTurnActive` has exactly two
         writers, set at 29003 and cleared on the first line of finOpp (30063),
         and finOpp is the single exit for bank, bust and cap alike. */
      G._oppTurnActive = false;
      try { runOppTurn(); } catch (e) { notes._cErr = String(e).slice(0, 80); }
      const started = await until(() => G && G._oppTurnActive, 4000);
      const ended = await until(() => !G || !G._oppTurnActive, 60000);
      await sleep(400);
      seen.push(n);
      if (!started || !ended) notes._cIncomplete = (notes._cIncomplete || 0) + 1;
    }
  } finally { window.famFire = real; if (typeof realBank === 'function') window.oppShouldBank = realBank; }
  return seen;
}
const onRolls  = await oppRolls(true, 6);
const offRolls = await oppRolls(false, 6);
const maxOn = Math.max.apply(null, onRolls.concat([0]));
const maxOff = Math.max.apply(null, offRolls.concat([0]));
notes._armC = { withRule: onRolls, maxWithRule: maxOn, withoutRule: offRolls, maxWithoutRule: maxOff };
/* THE VOID CHECK. If the rival never reaches 4 rolls even unrestricted, then
   "capped at 3" is a fact about the dice and arm C says nothing. */
v.rivalCanExceedThreeRollsUnrestricted = maxOff > 3;
v.rivalCapFollowsTheRecord = maxOff > 3 && maxOn > 3;

REC.maxRolls = WAS;                     /* leave the record as it was found */
notes._restored = REC.maxRolls;

for (const k of Object.keys(v)) { if (k[0] === '_') { notes[k] = v[k]; delete v[k]; } }
return { verdict: v, notes: notes };
