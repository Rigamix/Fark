/* THE TWO PRESERVE DEFECTS, tested together because P514 fixed them together.
 *
 * A - captured MATERIAL. CFX.preserve.use read k.mat, which is selDice[0].mat,
 *     the first die of the whole commit. So a keep of [3 bone, 3 iron, 3 flint,
 *     1 lead] stored the 1 as BONE and minted a bone 1 next turn.
 *     The adversarial shape matters: the scoring die must NOT be first in the
 *     commit, or k.mat happens to be right and the bug hides. Any test that
 *     keeps a lone 1 passes against the broken code.
 *
 * B - payout NUMDICE. The payout recomputed from matchDice.length, discarding
 *     Whisper's Hex applied earlier in the same startPTurn. Player told "YOU
 *     HAVE 5 DICE", then handed five instead of four.
 *
 * MEASURED, per PRESERVE (denominator stated):
 *   A: the material stored in G._famPreserve, against the material of the die
 *      that actually carried the 1 or the 5
 *   B: G.numDice after the payout, with the Hex armed and without
 *
 * Both arms compute what the OLD code would have produced from the same state,
 * so each result is a contrast rather than an assertion.
 */
const sleep = ms => new Promise(r => setTimeout(r, ms));
const until = async (fn, ms) => { const t0 = Date.now();
  while (Date.now() - t0 < ms) { try { if (fn()) return true; } catch (e) {} await sleep(50); }
  return false; };

if (typeof CFX === 'undefined' || !CFX.preserve) return { error: 'CFX.preserve not reachable' };
if (typeof launchBossMatch !== 'function') return { error: 'game globals missing' };

async function reachMatch(dice) {
  try {
    _getS();
    S.run = S.run || {};
    S.run.tier = 2;
    S.run.dice = dice.slice();
    S.run.cards = S.run.cards || [];
    S.settings = S.settings || {}; S.settings.reducedMotion = true;
    launchBossMatch();
  } catch (e) { return 'launch: ' + e.message; }
  if (!(await until(() => typeof G !== 'undefined' && G && G.rung, 9000))) return 'no match';
  await sleep(600);
  try { if (typeof startPTurn === 'function') startPTurn(); } catch (e) {}
  await sleep(200);
  return null;
}

/* ---------- ARM A: the captured material ---------- */
let A = {};
{
  const err = await reachMatch(['bone','iron','flint','lead','amber','brass']);
  if (err) return { error: 'arm A ' + err };
  /* a commit whose FIRST die is not the scoring one: three 3s then a 1 on lead */
  G.kept = [{
    vals: [3, 3, 3, 1],
    mat: 'bone',                              /* selDice[0].mat - the trap */
    pts: 300,
    dice: [{ val: 3, mat: 'bone' }, { val: 3, mat: 'iron' },
           { val: 3, mat: 'flint' }, { val: 1, mat: 'lead' }]
  }];
  const oldWouldStore = G.kept[0].mat;
  const trueMat = G.kept[0].dice.filter(d => d.val === 1 || d.val === 5)[0].mat;
  let ok = null;
  try { ok = CFX.preserve.use({ tier: 1 }); } catch (e) { return { error: 'A use threw: ' + e.message }; }
  await sleep(200);
  A = {
    used: ok,
    storedMat: G._famPreserve ? G._famPreserve.mat : null,
    storedVal: G._famPreserve ? G._famPreserve.val : null,
    trueMatOfScoringDie: trueMat,
    oldWouldHaveStored: oldWouldStore,
    pass: !!(G._famPreserve && G._famPreserve.mat === trueMat)
  };
}

/* ---------- ARM B: numDice with the Hex armed ---------- */
let B = {};
{
  const err = await reachMatch(['bone','iron','flint','lead','amber','brass']);
  if (err) return { error: 'arm B ' + err, A: A };
  const lanes = (G.matchDice || []).length;
  /* arm the preserve payout and the hex, then run the turn start that consumes both */
  G._famPreserve = { val: 1, mat: 'lead', pts: 100, crack: 0 };
  G._npcHexArmed = true;
  try { if (typeof startPTurn === 'function') startPTurn(); } catch (e) {}
  await sleep(500);
  B = {
    matchDiceLanes: lanes,
    numDiceAfter: G.numDice,
    expectedWithHexAndPreserve: Math.max(1, Math.max(3, lanes - 1) - 1),
    oldRecomputeWouldGive: Math.max(1, lanes - 1),
    pass: G.numDice === Math.max(1, Math.max(3, lanes - 1) - 1)
  };
}

return {
  A_material: A, B_numDice: B,
  verdict: (A.pass && B.pass) ? 'PASS - both'
         : (A.pass ? 'PARTIAL - material fixed, numDice not'
         : (B.pass ? 'PARTIAL - numDice fixed, material not' : 'FAIL - neither'))
};
