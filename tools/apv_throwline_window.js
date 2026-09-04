/* THE WINDOW RULING 3.12 ACTUALLY LIVES IN: after the bank, before their roll.
 *
 * apv_table_extent measured both rows FULL at once, which the file's own markup
 * comment says is impossible ("the turns alternate, so only one is ever full").
 * A contradiction with a source already in hand is a stop, so this settles it
 * before anything is built on either reading. The suspect is the probe: it
 * ended the turn through endPTurn() to dodge the Mending gate, and clearRow is
 * called by the BANK path rather than by endPTurn - so the previous run left
 * the player's row standing itself and then measured it.
 *
 * This one banks for real. Mending holds the bank shut while a turn is one roll
 * old, so the turn takes two rolls and the gate is READ rather than assumed.
 *
 * AND THE MEASUREMENT THAT MATTERS: #throwLine is the grid cell both rows share
 * and is what an effect must anchor to while a row is empty - the file says
 * #oppDiceRow collapses to zero, and the previous run measured exactly that
 * (0x0). So the question is whether the CELL keeps its geometry when both rows
 * are empty, because that is the only anchor available in this window.
 */
eval(await (await fetch('/tools/_fxh.js')).text());
const out = {};

const m = await FXH.match(1);
if (!m.ok) return {err: m.why, detail: m};
const _ff = setInterval(() => {
  try { if (typeof G !== 'undefined' && G) G._ffMult = 0.05; } catch (e) {}
}, 150);

const R = (el) => {
  if (!el) return null;
  const r = el.getBoundingClientRect();
  return {x: Math.round(r.left), y: Math.round(r.top),
          w: Math.round(r.width), h: Math.round(r.height)};
};
const kids = (id) => (document.getElementById(id) || {children: []}).children.length;

const survey = (tag) => ({
  tag, phase: (typeof G !== 'undefined' && G) ? G.phase : null,
  throwLine: R(document.getElementById('throwLine')),
  playerRow: R(document.getElementById('playerDiceRow')),
  oppRow: R(document.getElementById('oppDiceRow')),
  playerKids: kids('playerDiceRow'), oppKids: kids('oppDiceRow'),
  keptRow: R(document.getElementById('keptRow')), keptKids: kids('keptRow'),
  dg: R(document.getElementById('dgCanvas')),
  dgSized: FXH.sizedOf(document.getElementById('dgCanvas')),
  seatXs: [].slice.call((document.getElementById('playerDiceRow') ||
    {children: []}).children).map(e => Math.round(e.getBoundingClientRect().left)),
});

/* ROLL ONE, keep the scorers */
const r1 = await FXH.rollAndSettle();
out.roll1 = {ok: r1.ok, why: r1.why};
const keep = () => {
  let n = 0;
  try {
    ((G && G.pool) || []).filter(d => !d.committed).forEach(d => {
      if ((d.val === 1 || d.val === 5) && d.el) { FXH.tap(d.el); n++; }
    });
  } catch (e) {}
  return n;
};
out.kept1 = keep();
const bb = () => document.getElementById('btnBank');
out.gateAfterRoll1 = {disabled: !!(bb() && bb().classList.contains('disabled')),
                      mendHeld: !!(bb() && bb().classList.contains('mend-held'))};

/* ROLL TWO - what clears the Mending gate */
const r2 = await FXH.rollAndSettle({noLoad: true});
out.roll2 = {ok: r2.ok, why: r2.why};
out.kept2 = keep();
out.gateAfterRoll2 = {disabled: !!(bb() && bb().classList.contains('disabled')),
                      mendHeld: !!(bb() && bb().classList.contains('mend-held'))};

out.beforeBank = survey('player turn, dice on the line');

/* THE REAL BANK */
const pT0 = (G.pTurns || 0);
if (bb() && !bb().classList.contains('disabled')) FXH.tap(bb());
const banked = await FXH.until(() => (G.pTurns || 0) !== pT0 ||
  G.phase === 'opp' || G._oppTurnActive, 30000);
out.bankedMs = banked;
/* THE WINDOW: banked, and their dice have not arrived */
out.theWindow = survey('BANKED - the window 3.12 paints in');

const dealt = await FXH.until(() => (G.oppDice || []).length > 0 &&
  kids('oppDiceRow') > 0, 120000);
out.dealtMs = dealt;
if (dealt != null) out.afterDeal = survey('their dice have landed');
try { clearInterval(_ff); } catch (e) {}

const W = out.theWindow, A = out.afterDeal, B = out.beforeBank;
out.VERDICT = {
  theBankActuallyHappened: banked != null,
  /* THE CONTRADICTION, settled one way or the other */
  onlyOneRowIsEverFull: !!W && !!A &&
    !(B.playerKids > 0 && B.oppKids > 0) && !(A.playerKids > 0 && A.oppKids > 0),
  /* the cell survives an empty window - the anchor 3.12 needs */
  throwLineKeepsItsBoxWhenEmpty: !!W && !!W.throwLine &&
    W.throwLine.w > 10 && W.throwLine.h > 10,
  /* and it is the same box before and after, or it is not an anchor */
  throwLineIsStable: !!W && !!B && !!A &&
    B.throwLine.x === W.throwLine.x && W.throwLine.x === A.throwLine.x &&
    B.throwLine.y === W.throwLine.y && W.throwLine.y === A.throwLine.y &&
    B.throwLine.w === A.throwLine.w,
  reachedTheDeal: dealt != null,
};
out.PASS = Object.keys(out.VERDICT).every(k => out.VERDICT[k] === true);
out.FAILED = Object.keys(out.VERDICT).filter(k => out.VERDICT[k] !== true);
return out;
