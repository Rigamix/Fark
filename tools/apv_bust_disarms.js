/* P948 (3.13): BANK KEEPS, BUST CLEARS - and only this turn's armings.
 *
 * THREE TRIALS, AND THE THIRD IS THE ONE THAT DISCRIMINATES. "A bust clears the
 * marks" passes on an implementation that clears EVERY live mark, and that
 * implementation is wrong: a mark armed on an earlier turn was already paid for
 * by the bank that ended that turn and must survive. Trials A and B alone would
 * green-light it. Trial C is the ruling's actual content.
 *
 * AND EVERY TRIAL IS GATED ON ITS OWN EVENT HAVING HAPPENED. A bust that never
 * occurred leaves the mark alive and reads exactly like a disarm that did not
 * fire; a bank that was refused leaves it alive and reads exactly like a pass.
 * So the bust is confirmed by G._featBusts moving and the bank by G.pPts moving,
 * before either verdict is allowed to mean anything.
 */
eval(await (await fetch('/tools/_fxh.js')).text());
const out = {};
const m = await FXH.match(1);
if (!m.ok) return {err: m.why, detail: m};
const _ff = setInterval(() => {
  try { if (typeof G !== 'undefined' && G) G._ffMult = 0.05; } catch (e) {}
}, 150);

/* no shields, or an eaten bust is not a bust and the trial measures nothing */
try { G.pCards = []; G.pF = []; G.oF = []; } catch (e) {}

const BUST = [2, 3, 4, 6, 2, 3, 2, 3, 4, 6, 2, 3];
const SCORE = [1, 5, 1, 5, 1, 5, 1, 5, 1, 5, 1, 5];

const mine = () => FXH.until(() => typeof G !== 'undefined' && G &&
  G.phase === 'idle' && !G._oppTurnActive && !G._endMatchFired, 120000);

/* roll a hand that cannot score and wait for the turn to actually end */
async function bustTurn() {
  const restore = FXH.loadDice(BUST.slice());
  const busts0 = G._featBusts || 0, turns0 = G.pTurns || 0;
  FXH.tap(document.getElementById('btnRoll'));
  const ended = await FXH.until(() => (G.pTurns || 0) !== turns0 ||
    (G._featBusts || 0) !== busts0, 90000);
  restore();
  return {ended: ended != null, bustsMoved: (G._featBusts || 0) !== busts0,
          featBusts: G._featBusts || 0, pTurns: G.pTurns || 0};
}

/* keep everything and bank, two rolls so the Mending gate is open */
async function bankTurn() {
  const pts0 = G.pPts || 0;
  for (let i = 0; i < 2; i++) {
    const r = await FXH.rollAndSettle({vals: SCORE.slice()});
    if (!r.ok) return {ok: false, why: r.why};
    try {
      ((G && G.pool) || []).filter(d => !d.committed).forEach(d => {
        if ((d.val === 1 || d.val === 5) && d.el) FXH.tap(d.el);
      });
    } catch (e) {}
  }
  const bb = document.getElementById('btnBank');
  out.bankGate = {disabled: !!(bb && bb.classList.contains('disabled'))};
  if (bb && !bb.classList.contains('disabled')) FXH.tap(bb);
  const banked = await FXH.until(() => (G.pPts || 0) !== pts0, 60000);
  return {ok: banked != null, ptsMoved: (G.pPts || 0) !== pts0, pPts: G.pPts || 0};
}

/* ── A. arm, then BUST: the mark must not survive ─────────────────── */
await mine();
try { G._laneMark = {}; } catch (e) {}
const aArmed = _lmArm('_snuff', 2, 1);
const aStamp = (_lmMap()[2] || {}).armedOn;
out.A = {armed: aArmed, armedOn: aStamp, pTurnsAtArm: G.pTurns || 0};
out.A.bust = await bustTurn();
out.A.markLiveAfter = !!((_lmMap()[2] || {}).live);
out.A.laneFreeAfter = _lmOccupied(2) === false;

/* ── B. arm, then BANK: the mark must survive and fire (the control) ── */
await mine();
try { G._laneMark = {}; } catch (e) {}
const bArmed = _lmArm('_snuff', 3, 1);
out.B = {armed: bArmed, armedOn: (_lmMap()[3] || {}).armedOn};
out.B.bank = await bankTurn();
out.B.markLiveAfterBank = !!((_lmMap()[3] || {}).live);
const dealt = await FXH.until(() => (G.oppDice || []).length > 0 &&
  (document.getElementById('oppDiceRow') || {children: []}).children.length > 0, 120000);
out.B.reachedRival = dealt != null;
out.B.fired = dealt == null ? null : {seats: (G.oppDice || []).map(d => d && d.lane),
                                      published: ((G._oSnuffLanes) || []).slice()};

/* ── C. AN OLDER MARK SURVIVES A BUST. The discriminating trial. ───── */
await mine();
try {
  G._laneMark = {};
  _lmArm('_fog', 1, 1);
  /* backdate it by one player turn: a mark a previous BANK already paid for */
  _lmMap()[1].armedOn = (G.pTurns || 0) - 1;
} catch (e) { out.cSetupErr = e.message; }
out.C = {armedOn: (_lmMap()[1] || {}).armedOn, pTurnsNow: G.pTurns || 0,
         liveBefore: !!((_lmMap()[1] || {}).live)};
out.C.bust = await bustTurn();
out.C.markLiveAfter = !!((_lmMap()[1] || {}).live);
try { clearInterval(_ff); } catch (e) {}

out.VERDICT = {
  /* the events under test actually occurred */
  trialABusted: out.A.bust.ended === true && out.A.bust.bustsMoved === true,
  trialBBanked: out.B.bank.ok === true && out.B.bank.ptsMoved === true,
  trialCBusted: out.C.bust.ended === true && out.C.bust.bustsMoved === true,
  /* the stamp exists at all */
  theArmingTurnIsRecorded: typeof out.A.armedOn === 'number',
  /* A: BUST CLEARS */
  aBustTakesThisTurnsArming: out.A.markLiveAfter === false,
  andFreesTheLane: out.A.laneFreeAfter === true,
  /* B: BANK KEEPS - the other direction, without which A passes on code
     that simply deletes every mark it can find */
  aBankKeepsIt: out.B.markLiveAfterBank === true,
  andItStillFires: !!(out.B.fired && out.B.fired.published.indexOf(3) >= 0),
  /* C: THE RULING'S ACTUAL CONTENT */
  anOlderMarkSurvivesTheBust: out.C.liveBefore === true && out.C.markLiveAfter === true,
};
out.PASS = Object.keys(out.VERDICT).every(k => out.VERDICT[k] === true);
out.FAILED = Object.keys(out.VERDICT).filter(k => out.VERDICT[k] !== true);
return out;
