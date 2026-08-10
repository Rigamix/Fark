/* THE RIVAL'S ARMED ACTIVES: the charge survives a resume and the effect does not.
 *
 * P511 taught the match snapshot to carry pF/oF, because without them a resume
 * rebuilt both hands at full charge and every spent card came back - measured
 * 4 -> 2 -> 4. That fixed the COST. It did not carry the FLAGS the cost buys.
 *
 * `_npcArmActives` spends a charge and sets a flag:
 *     sleight    c.charges--; G._oSleight=true      consumed at the player's
 *                                                   first roll (_afterRollImpl,
 *                                                   turnRollCount===0)
 *     ill_omen   c.charges--; G._oIllOmen={tier}    consumed at 28464
 * Neither flag is in the snapshot. And the snapshot is written at the END of
 * startPTurn - which is INSIDE both windows, because the rival arms during its
 * turn and the player's turn has not rolled yet. So the ordinary auto-save at
 * every turn boundary lands exactly where the flag is live.
 *
 * Net: reload with a Sleight armed and the rival has paid for nothing. It is
 * savescummable in the player's favour and it needs no exotic timing - it is
 * every resume from the menu while a rival active is armed.
 *
 * THE CONTROL IS THE POINT. A probe that reports "the flags are gone" proves
 * nothing if the resume restored nothing at all, so this asserts in the same
 * breath that _oGrudgeStack (which IS in famState's neighbours) and the spent
 * CHARGES both come back. Loss and survival, measured on the same reload.
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

/* the run-start chain the rest of the suite uses */
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

const v = {}, notes = {};

/* ── ARM THEM THROUGH THE REAL PATH ─────────────────────────────────────
   Not by setting the flags. _npcArmActives is what spends the charge, and a
   probe that writes G._oSleight itself would prove nothing about whether the
   cost is ever paid. Give the rival the cards and the conditions it gates on,
   then let it decide. */
G.oF = [{id:'sleight', tier:1, charges:2, state:{}},
        {id:'ill_omen', tier:1, charges:2, state:{}}];
G.pPts = 1200; G.oPts = 0; G._pLastRolls = 4;
G._oSleight = false; G._oIllOmen = null;
G._oGrudgeStack = 3;                    /* the control: this one IS carried */
try { _npcArmActives(); } catch (e) { notes._armErr = String(e).slice(0, 90); }

const chargesNow = G.oF.map(c => c.id + ':' + c.charges);
notes._armed = { sleight: !!G._oSleight, illOmen: !!G._oIllOmen, charges: chargesNow };
v.armingSpentACharge = G.oF.every(c => c.charges === 1);
v.bothFlagsArmed = !!G._oSleight && !!G._oIllOmen;
if (!v.armingSpentACharge || !v.bothFlagsArmed) {
  for (const k of Object.keys(v)) { if (k[0] === '_') { notes[k] = v[k]; delete v[k]; } }
  return { verdict: v, notes: notes,
    skip: 'the rival never armed, so the resume below would measure nothing' };
}

/* ── THE ORDINARY AUTO-SAVE. startPTurn's last statement, verbatim. ────── */
saveMatchState();
const snap = S && S.pendingMatch;
/* the fields live in famState under their name WITHOUT the leading underscore
   (G._oSleight -> famState.oSleight), which is the convention the rest of that
   object already uses. The first version of this probe looked for `_oSleight`
   on the snapshot's top level and reported it absent after the fix landed. */
const fsOf = sn => (sn && sn.famState) || {};
notes._snapshotCarries = snap ? {
  famState: !!snap.famState,
  oF: !!fsOf(snap).oF,
  oSleight: 'oSleight' in fsOf(snap),
  oIllOmen: 'oIllOmen' in fsOf(snap),
  grudge: Object.prototype.hasOwnProperty.call(snap, '_oGrudgeStack')
} : null;

/* ── RELOAD IT, through the button the player actually presses ────────── */
G._endMatchFired = false;
resumeMatch();
const _back = await until(() => typeof G !== 'undefined' && G && G._resumedAt !== undefined
  || (typeof G !== 'undefined' && G && G.oF && G.oF.length && vis(document.getElementById('screen-match'))), 15000);
await sleep(2500);

const after = {
  sleight: !!(G && G._oSleight),
  illOmen: !!(G && G._oIllOmen),
  grudge: G && G._oGrudgeStack,
  charges: (G && G.oF || []).map(c => c.id + ':' + c.charges)
};
notes._afterResume = after;
notes._backAtMatch = _back;

/* the control: the resume DID restore things */
v.spentChargesSurviveResume = after.charges.length === 2
  && after.charges.every(s => /:1$/.test(s));
v.aCarriedFieldSurvives = after.grudge === 3;
/* the finding */
v.armedSleightSurvivesResume = after.sleight;
v.armedIllOmenSurvivesResume = after.illOmen;

/* ── AND THE PLAYER'S HALF OF THE SAME PATTERN ──────────────────────────
   The two above were driven end to end because the question was whether the
   rival ever PAYS. For the rest the question is narrower and the arming path
   is irrelevant to it: does the snapshot carry the field at all. So these are
   set directly and the SNAPSHOT is read - a structural check, stated as one.
   _famSleight and _famIllOmen are the player's mirrors of the two above;
   _famBankCount seeds "is this your first bank" (Hair of the Dog) and
   _famMinBank is reseeded from it, so losing the count silently rewrites the
   smallest-bank-this-match a card is keyed on. */
const PLAYER_SIDE = ['_famSleight', '_famIllOmen', '_famPeekVals',
                     '_famHoneyVal', '_famKegTriple', '_famBankCount', '_famMinBank'];
G._famSleight = true; G._famIllOmen = {tier:2}; G._famPeekVals = [3,3,3];
G._famHoneyVal = 5; G._famKegTriple = 4; G._famBankCount = 3; G._famMinBank = 250;
saveMatchState();
const fs2 = fsOf(S && S.pendingMatch);
/* G._famSleight -> famState.famSleight: drop the leading underscore, nothing
   else. Stripping `_fam` instead looked for `Sleight` and found nothing, which
   reported a landed fix as missing. */
const missing = PLAYER_SIDE.filter(f => !(f.replace(/^_/, '') in fs2));
notes._playerSideMissingFromSnapshot = missing;
notes._playerSideValues = PLAYER_SIDE.map(f => f + '=' + JSON.stringify(fs2[f.replace(/^_/, '')]));
v.playerArmedFlagsAreSnapshotted = missing.length === 0;

/* ── THE FALSY ARM, which is the whole point of the guards ───────────────
   The restore is written `!==undefined`, not `||`, because _famBankCount and
   _famMinBank are numbers that are legitimately 0. Every check above armed
   something first, so all of them would pass on a `||` restore too - the arm
   that tells the two apart is this one, and without it the patch's stated care
   is untested.
   It matters concretely: _famBankCount seeds `is this your FIRST bank`, which
   is what Hair of the Dog pays on. A restore that turned 0 back into undefined
   would re-open that window on every reload. */
G._famBankCount = 0; G._famMinBank = 0; G._famSleight = false;
G._oSleight = false; G._oIllOmen = null;
saveMatchState();
const fs3 = fsOf(S && S.pendingMatch);
notes._falsyInSnapshot = { bankCount: fs3.famBankCount, minBank: fs3.famMinBank,
                           famSleight: fs3.famSleight, oSleight: fs3.oSleight };
G._famBankCount = 99; G._famMinBank = 99;   /* poison, so a no-op restore shows */
G._endMatchFired = false;
resumeMatch();
await until(() => vis(document.getElementById('screen-match')), 15000);
await sleep(2500);
notes._falsyAfterResume = { bankCount: G && G._famBankCount, minBank: G && G._famMinBank,
                            famSleight: G && G._famSleight };
v.zeroSurvivesAsZero = (G && G._famBankCount) === 0 && (G && G._famMinBank) === 0;

for (const k of Object.keys(v)) { if (k[0] === '_') { notes[k] = v[k]; delete v[k]; } }
return { verdict: v, notes: notes };
