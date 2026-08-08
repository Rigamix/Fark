/* DOES A RESUME REFUND FAMILY-CARD CHARGES? Proven by doing it, not by reading.
 *
 * saveMatchState (10235) carries 72 fields - matchDice, _enchArr, numDice,
 * npcCardState, activeCardState, _wardCharges - and NONE of pF, oF,
 * _famPreserve, _ftDead, _snuff, _snare, _fog. newG rebuilds pF via _famInit
 * (23049), and _famInit sets charges from the card definition (12731), i.e.
 * full. So spending charges then resuming should hand them all back.
 *
 * That is read from three functions. It is not a demonstration. This drives
 * the real save and the real resume and reads the charges on the other side.
 *
 * MEASURED, per RESUME (denominator stated): the charge count on every entry
 * of G.pF, before spending, after spending, and after resumeMatch().
 *
 * PASS (bug present) : charges return to their pre-spend values across a resume
 * PASS (bug absent)  : charges survive the resume as spent
 * Either is a real answer. The probe reports what it saw and does not assume.
 *
 * SELF-CHECK, and it is the important one: if the spend step does not actually
 * lower any charge, the resume comparison is vacuous - "unchanged" would look
 * identical to "correctly restored". The probe refuses to report a verdict
 * unless it first observed a real decrease.
 */
const sleep = ms => new Promise(r => setTimeout(r, ms));
const until = async (fn, ms) => { const t0 = Date.now();
  while (Date.now() - t0 < ms) { try { if (fn()) return true; } catch (e) {} await sleep(50); }
  return false; };

if (typeof launchBossMatch !== 'function') return { error: 'game globals missing' };
if (typeof saveMatchState !== 'function') return { error: 'saveMatchState not reachable' };
if (typeof resumeMatch !== 'function') return { error: 'resumeMatch not reachable' };

const snapshotCharges = () => {
  const pf = (typeof G !== 'undefined' && G && G.pF) ? G.pF : [];
  const of = (typeof G !== 'undefined' && G && G.oF) ? G.oF : [];
  return {
    player: pf.map(c => ({ id: c.id, tier: c.tier, charges: c.charges })),
    rival:  of.map(c => ({ id: c.id, tier: c.tier, charges: c.charges })),
    playerTotal: pf.reduce((a, c) => a + (c.charges || 0), 0),
    rivalTotal:  of.reduce((a, c) => a + (c.charges || 0), 0)
  };
};

/* reach a real boss match - night 6 so the rival is dealt 2 family cards and
   the player's own loadout carries some */
try {
  _getS();
  S.run = S.run || {};
  S.run.tier = 5;
  S.run.dice = ['silver','jade','jade','starstone','jade2','bone'];
  S.run.cards = S.run.cards || [];
  S.run.fcards = (S.run.fcards && S.run.fcards.length) ? S.run.fcards
                 : [{ id: 'transmute', tier: 2 }, { id: 'preserve', tier: 2 }];
  S.settings = S.settings || {}; S.settings.reducedMotion = true;
  launchBossMatch();
} catch (e) { return { error: 'launch: ' + e.message }; }

if (!(await until(() => typeof G !== 'undefined' && G && G.rung, 9000)))
  return { error: 'never reached a match' };
await sleep(700);

const before = snapshotCharges();

/* SPEND. Decrement directly on the live objects, which is exactly what every
   card consumption path does (_oEnc.charges--, c.charges--). Using the game's
   own field rather than firing a specific card keeps this about persistence
   rather than about any one card's trigger conditions. */
let spent = 0;
try {
  (G.pF || []).forEach(c => { if (c.charges > 0) { c.charges--; spent++; } });
  (G.oF || []).forEach(c => { if (c.charges > 0) { c.charges--; spent++; } });
} catch (e) {}

const afterSpend = snapshotCharges();

const reallyDropped = (afterSpend.playerTotal + afterSpend.rivalTotal)
                    < (before.playerTotal + before.rivalTotal);

/* SAVE, leave, RESUME - the real functions, in the real order */
let saveErr = null, resumeErr = null;
try { saveMatchState(); } catch (e) { saveErr = e.message; }
await sleep(300);
try { if (typeof showScreen === 'function') showScreen('menu'); } catch (e) {}
await sleep(700);
try { resumeMatch(); } catch (e) { resumeErr = e.message; }
if (!(await until(() => typeof G !== 'undefined' && G && G.rung, 9000)))
  return { error: 'resume never reached a match', saveErr: saveErr, resumeErr: resumeErr };
await sleep(900);

const afterResume = snapshotCharges();

const refunded = (afterResume.playerTotal + afterResume.rivalTotal)
               > (afterSpend.playerTotal + afterSpend.rivalTotal);
const fullyRefunded = (afterResume.playerTotal + afterResume.rivalTotal)
                   === (before.playerTotal + before.rivalTotal);

return {
  before: before, afterSpend: afterSpend, afterResume: afterResume,
  chargesSpent: spent,
  saveErr: saveErr, resumeErr: resumeErr,
  verdict: !reallyDropped
    ? 'VOID - the spend did not lower any charge, so the resume comparison proves nothing'
    : (fullyRefunded ? 'BUG CONFIRMED - every spent charge came back across the resume'
      : (refunded ? 'BUG CONFIRMED (partial) - some charges came back'
                  : 'NO BUG - spent charges survived the resume'))
};
