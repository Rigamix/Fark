/* DO BUST-SAVE CARDS FIRE FOR THE REAL RIVAL, AND NEVER FOR THE MODEL?
 *
 * The real runOppTurn honours NPC card effects on a bust:
 *   bust_survive       one_more_round          (GROG)
 *   bust_bank_half     the_last_stitch_npc     (MABEL)
 *   bust_immune_turns  hold_the_line           (BRUTUS)
 *   bust_immune_turns  sundays_rest            (WHISPER)
 * F.oppTurn deals the rival cards but applies none of these - it just breaks
 * out of the loop on a zero-scoring roll.
 *
 * Every boss holding one of those four shows a large bust gap (4.0x, infinite,
 * 2.9x, 4.8x). FINNICK holds none and its bust rates MATCH (0.40 vs 0.39) -
 * the disqualifying condition, checked before writing this probe, and passed.
 *
 * NOT saves despite matching a "bust" grep, and excluded deliberately:
 *   immune_modifiers  family_crest, never_saw_a_robe  - modifier immunity
 *   punish_busts      judgment_npc                    - punishes the PLAYER
 *   steal_on_bust     iron_gate_npc                   - steals, does not save
 *
 * TREATMENT: MABEL (tier 1). Chosen over CORVUS deliberately - Mabel's
 * bust_bank_half is deterministic rather than chance-gated, her real bust rate
 * is exactly 0.00 against the model's 0.13, and CORVUS's headline 6.7x rests
 * on ONE bust in 48 turns (95% interval ~0.00-0.11), which is the weakest
 * sample on the board.
 * CONTROL: FINNICK (tier 2), which must show zero fires on both sides.
 *
 * PREDICTIONS, registered before running:
 *   1. real MABEL   - the_last_stitch_npc fires, and on most busting turns
 *   2. model MABEL  - ZERO save fires (no effect application exists)
 *   3. real FINNICK - ZERO save fires (holds no save card)
 *   4. model FINNICK- ZERO save fires
 * If real MABEL shows no fires either, the saves are not reaching the rival
 * and the hypothesis is dead before any port.
 *
 * INSTRUMENT: wrap triggerCard, which the save path calls with the card id.
 * The saves themselves are inline locals in runOppTurn and cannot be wrapped
 * directly. A wrap that fails to take reports zero, which is indistinguishable
 * from "never fires" - so ALL triggerCard calls are counted too, and a zero
 * total means the instrument failed rather than the mechanism being absent.
 */
const SAVE_IDS = ['one_more_round', 'the_last_stitch_npc', 'hold_the_line', 'sundays_rest'];
const TIERS = [1, 2];
const NAMES = {1: 'MABEL (treatment)', 2: 'FINNICK (control)'};
const SIM_N = 80, REAL_MATCHES = 6, REAL_TURNS = 10;
const LOADOUT = {1: ['silver','bone','bone','bone','bone','bone'],
                 2: ['silver','jade','bone','bone','bone','bone']};
const PRATE = {1: 591, 2: 533};

const sleep = ms => new Promise(r => setTimeout(r, ms));
const until = async (fn, ms) => { const t0 = Date.now();
  while (Date.now() - t0 < ms) { try { if (fn()) return true; } catch (e) {} await sleep(50); }
  return false; };

if (typeof triggerCard !== 'function') return { error: 'triggerCard not reachable' };

let tag = null;
const fires = {}, allFires = {};
const _realTrigger = triggerCard;
window.triggerCard = function (cid) {
  if (tag) {
    allFires[tag] = (allFires[tag] || 0) + 1;
    if (SAVE_IDS.indexOf(cid) >= 0) {
      fires[tag] = fires[tag] || {};
      fires[tag][cid] = (fires[tag][cid] || 0) + 1;
    }
  }
  try { return _realTrigger.apply(this, arguments); } catch (e) { return undefined; }
};

const rows = [];
for (const t of TIERS) {
  /* ---- MODEL ---- */
  tag = 'model:' + t;
  let mTurns = 0, mBusts = 0;
  for (let i = 0; i < SIM_N; i++) {
    FSIM.installRng(20260807 + i);
    const gear = { key:'g', dice: LOADOUT[t].slice(),
                   ench:[null,null,null,null,null,null], badge:null, fcards:[] };
    try { const r = FSIM.simMatch(FSIM.POLICIES.carl, { tier:t, boss:true, gear:gear });
          mTurns += r.oppTurns||0; mBusts += r.oBusts||0; } catch(e) {}
  }

  /* ---- REAL ---- */
  tag = null;
  let rTurns = 0, rBusts = 0;
  for (let m = 0; m < REAL_MATCHES; m++) {
    await until(() => typeof G === 'undefined' || !G || !G._oppTurnActive, 8000);
    await sleep(160);
    try {
      _getS();
      S.run = S.run || {};
      S.run.tier = t;
      S.run.dice = LOADOUT[t].slice();
      S.run.cards = S.run.cards || [];
      S.settings = S.settings || {}; S.settings.fastRival = true;
      launchBossMatch();
    } catch (e) { break; }
    if (!(await until(() => typeof G !== 'undefined' && G && G.rung && G.matchOppDice, 9000))) break;
    await sleep(300);
    tag = 'real:' + t;
    for (let i = 0; i < REAL_TURNS; i++) {
      if (G._oppTurnActive) break;
      const t0 = (G.oTurns || 0), p0 = (G.oPts || 0);
      try { runOppTurn(); } catch (e) { break; }
      if (!(await until(() => G && (G.oTurns || 0) > t0, 20000))) break;
      rTurns++;
      if ((G.oPts || 0) - p0 <= 0) rBusts++;
      try {
        G.pPts = (G.pPts || 0) + PRATE[t];
        if (G._endMatchFired || G.oPts >= (G.target || 1e9) || G.pPts >= (G.target || 1e9)) break;
      } catch (e) { break; }
      await sleep(90);
    }
    tag = null;
  }

  const sum = o => o ? Object.values(o).reduce((p, c) => p + c, 0) : 0;
  rows.push({ tier: t, boss: NAMES[t],
              realTurns: rTurns, realBusts: rBusts,
              realBustRate: rTurns ? +(rBusts / rTurns).toFixed(3) : null,
              realSaveFires: sum(fires['real:' + t]), realSaveBreakdown: fires['real:' + t] || {},
              realAllCardFires: allFires['real:' + t] || 0,
              modelTurns: mTurns, modelBusts: mBusts,
              modelBustRate: mTurns ? +(mBusts / mTurns).toFixed(3) : null,
              modelSaveFires: sum(fires['model:' + t]),
              modelAllCardFires: allFires['model:' + t] || 0 });
}

window.triggerCard = _realTrigger;
return rows;
