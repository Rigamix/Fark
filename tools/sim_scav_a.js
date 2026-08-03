/* sim_scav_a.js — SCAVENGER, probe A: the structural cheats.
 * Tail for tools/sim_run.js (harness already in scope as FSIM).
 * Reads only. Never edits fark_proto.html.
 *
 *  A1  every branded face the SHOP can produce, across every die type
 *  A2  the Kindred `doubles` whitelist vs ruling #32
 *  A3  the one-Ward loadout cap, through the REAL purchase function
 *  A4  born brands (Brutus's relic) and the cap's side doors
 *  A5  Zero Hour's activation route vs every other badge's
 */
var SEED = (window.__FSIM_SEED != null) ? window.__FSIM_SEED : 20260731;
FSIM.installRng(SEED);
FSIM.quiet();

var OUT = {seed: SEED, probe: 'A'};

/* ── shared: a clean run ────────────────────────────────────────────── */
function freshRun(dice, inv) {
  _getS();
  S.run = S.run || {};
  S.run.dice = (dice || ['bone','bone','bone','bone','bone','bone']).slice();
  S.run.diceInv = (inv || []).slice();
  S.run.dieEnch = S.run.dice.map(function(){return null;});
  S.run.dieEnchInv = S.run.diceInv.map(function(){return null;});
  S.run.gold = 100000;
  S.run._enchV = 3; S.run._enchTradeV = 1;
  S.run.tier = 3; S.run.sleeve = null; S.run.tells = [];
  return S.run;
}

/* ══ A1. THE 1/5 RESTRICTION, over every die the game ships ══════════ */
(function () {
  var mats = [];
  try { mats = Object.keys(DICE_TYPES); } catch (e) {}
  if (!mats.length) { try { mats = DICE.map(function(d){return d.id;}); } catch (e) {} }
  var rows = [], illegalStatic = [], illegalDrawn = [], noFace = [];
  mats.forEach(function (m) {
    var dt = null; try { dt = getDie(m) || {}; } catch (e) { dt = {}; }
    var faces = dt.faces || [1,2,3,4,5,6];
    var legal = [];
    try { legal = _iconFaces(m); } catch (e) { legal = ['ERR']; }
    legal.forEach(function (f) { if (f !== 1 && f !== 5) illegalStatic.push({mat:m, face:f}); });
    /* the shop's own draw, 3000 times */
    var seen = {};
    for (var i = 0; i < 3000; i++) {
      var f = null; try { f = _iconFaceRoll(m); } catch (e) { f = 'ERR'; }
      seen[String(f)] = (seen[String(f)] || 0) + 1;
    }
    Object.keys(seen).forEach(function (k) {
      if (k !== '1' && k !== '5' && k !== 'null') illegalDrawn.push({mat:m, face:k, n:seen[k]});
    });
    if (!legal.length) noFace.push(m);
    rows.push({mat:m, faces:faces.join(''), legal:legal.join(''), drawn:Object.keys(seen).sort().join('/'),
               eff:(dt.effect && dt.effect.mechanic) || null});
  });
  OUT.A1 = {
    nMaterials: mats.length,
    drawsPerMaterial: 3000,
    illegalStaticFaces: illegalStatic,
    illegalDrawnFaces: illegalDrawn,
    materialsWithNoLegalFace: noFace,
    rows: rows
  };
})();

/* A1b — the point-of-sale guard: can a FORGED face get through _gbEnchantApply? */
(function () {
  var res = [];
  [2,3,4,6,1,5].forEach(function (face) {
    freshRun(['bone','bone','bone','bone','bone','bone']);
    var before = S.run.gold;
    try { _gbEnchantApply('tithe', 0, face, null, true); } catch (e) {}
    var got = S.run.dieEnch[0];
    res.push({forcedFace: face, landed: got ? got.face : null, charged: before - S.run.gold});
  });
  OUT.A1b = {forgedFaceAtPointOfSale: res};
})();

/* ══ A2. Kindred's doubling whitelist ════════════════════════════════ */
(function () {
  var want = {tithe:true, ward:true, snare:true, snuff:true, fog:true, 'break':false, trade:false};
  var got = {}, mismatch = [];
  Object.keys(ENCH_ICONS).forEach(function (k) {
    got[k] = !!ENCH_ICONS[k].doubles;
    if (want[k] !== undefined && want[k] !== got[k]) mismatch.push({ench:k, ruled:want[k], shipped:got[k]});
  });
  OUT.A2 = {shippedDoubles: got, ruling32Mismatch: mismatch};
})();

/* ══ A3. THE ONE-WARD CAP, driven through the real sale ══════════════ */
(function () {
  var out = {};

  /* (a) buy Ward on lane 0 then on lane 1..5 — the plain attempt */
  freshRun();
  _gbEnchantApply('ward', 0, _iconFaceRoll('bone'), null, true);
  var attempts = [];
  for (var i = 1; i < 6; i++) {
    var g0 = S.run.gold;
    try { _gbEnchantApply('ward', i, _iconFaceRoll('bone'), null, true); } catch (e) {}
    attempts.push({lane:i, landed: !!(S.run.dieEnch[i] && S.run.dieEnch[i].t === 'ward'), spent: g0 - S.run.gold});
  }
  out.plainSecondSale = {wards: S.run.dieEnch.filter(function(e){return e&&e.t==='ward';}).length, attempts: attempts};

  /* (b) STASH THE WARD, THEN BUY ANOTHER. famDieStash moves the brand into
     dieEnchInv; _wardOwned counts that array too — does it? */
  freshRun();
  _gbEnchantApply('ward', 0, _iconFaceRoll('bone'), null, true);
  try { famDieStash(0); } catch (e) { out.stashErr = e.message; }
  var g1 = S.run.gold;
  try { _gbEnchantApply('ward', 0, _iconFaceRoll(S.run.dice[0]), null, true); } catch (e) {}
  out.stashThenBuy = {
    inv: (S.run.dieEnchInv || []).map(function(e){return e ? e.t : null;}),
    loadout: (S.run.dieEnch || []).map(function(e){return e ? e.t : null;}),
    spent: g1 - S.run.gold,
    totalWards: ((S.run.dieEnch||[]).concat(S.run.dieEnchInv||[]))
                 .filter(function(e){return e && e.t === 'ward';}).length
  };

  /* (c) EQUIP a second warded die back in: can two wards ever co-exist in the
     six? Only reachable if (b) let a second one be sold. */
  try {
    var eq = [];
    for (var j = 0; j < (S.run.diceInv || []).length; j++) eq.push(j);
    if (eq.length) famDieEquip(0);
  } catch (e) {}
  out.afterEquip = {
    loadoutWards: (S.run.dieEnch||[]).filter(function(e){return e && e.t==='ward';}).length,
    loadout: (S.run.dieEnch||[]).map(function(e){return e ? e.t : null;})
  };

  /* (d) does the harness's own buildLoadout honour it? (already claimed; verify) */
  var lo = FSIM.buildLoadout({dice:['bone','bone','bone','bone','bone','bone'],
                              ench:['ward','ward','ward',null,null,null]});
  out.harnessBuild = {wards: lo.ench.filter(function(e){return e && e.t==='ward';}).length,
                      refused: lo.refused};
  OUT.A3 = out;
})();

/* ══ A4. BORN BRANDS — the relic, and whether two can exist ══════════ */
(function () {
  var out = {};
  var mats = []; try { mats = Object.keys(DICE_TYPES); } catch (e) {}
  var born = [];
  mats.forEach(function (m) {
    var b = null; try { b = _bornEnch(m); } catch (e) {}
    if (b) born.push({mat:m, t:b.t, face:b.face});
  });
  out.materialsWithBornBrands = born;

  /* (a) relic + a bought ward: the migration should refund the bought one */
  freshRun(['bone','bone','bone','bone','bone','bone']);
  _gbEnchantApply('ward', 0, _iconFaceRoll('bone'), null, true);
  var gA = S.run.gold;
  S.run.dice[3] = 'brutus_shield';
  try { _enchInit(); } catch (e) { out.err = e.message; }
  out.relicArrivesAfterWard = {
    refund: S.run.gold - gA,
    enchs: (S.run.dieEnch||[]).map(function(e){return e ? (e.t + (e.born?'(born)':'')) : null;}),
    wards: (S.run.dieEnch||[]).filter(function(e){return e && e.t==='ward';}).length
  };

  /* (b) TWO relics in the same loadout — the born pass has no cap of its own */
  freshRun(['brutus_shield','brutus_shield','bone','bone','bone','bone']);
  try { _enchInit(); } catch (e) {}
  out.twoRelics = {
    enchs: (S.run.dieEnch||[]).map(function(e){return e ? (e.t + (e.born?'(born)':'')) : null;}),
    loadoutWards: (S.run.dieEnch||[]).filter(function(e){return e && e.t==='ward';}).length,
    wardOwnedSaysYes: (function(){try{return _wardOwned(-1);}catch(e){return 'ERR';}})()
  };

  /* (c) can a second relic be ACQUIRED? is it in the shop stock at all? */
  var stock = null;
  try { stock = _initDiceStock(); } catch (e) {}
  out.brutusShieldInShopStock = stock ? (stock.brutus_shield !== undefined ? stock.brutus_shield : 'absent') : 'no _initDiceStock';

  /* (d) refund farm: run _enchInit repeatedly on the two-relic loadout */
  freshRun(['brutus_shield','bone','bone','bone','bone','bone']);
  _gbEnchantApply('tithe', 1, _iconFaceRoll('bone'), null, true);
  var gB = S.run.gold;
  for (var r = 0; r < 25; r++) { try { _enchInit(); } catch (e) {} }
  out.repeatedEnchInitGold = S.run.gold - gB;

  OUT.A4 = out;
})();

/* ══ A5. Zero Hour's activation route ════════════════════════════════ */
(function () {
  var out = {};
  /* _iconFire tests G._tell.id directly; every other badge asks _ruleActive.
     Sleeve a badge in a PATRON match and see which rules bind. */
  ['last_call','kindred','still_waters','first_strike'].forEach(function (id) {
    freshRun();
    S.run.sleeve = id;
    S.run.dieEnch[0] = {t:'tithe', face:1};
    S.run.dieEnch[1] = {t:'tithe', face:5};
    var set = FSIM.setupMatch({tier:3, dice:S.run.dice.slice(),
      ench:[null,null,null,null,null,null], badge:id});
    var G = FSIM.getG();
    G._enchArr = [{t:'tithe',face:1},{t:'tithe',face:5},null,null,null,null];
    out[id] = {
      ruleActive: (function(){try{return _ruleActive(id,'p');}catch(e){return 'ERR';}})(),
      tellId: G._tell ? G._tell.id : null,
      sleeve: G._sleeve || null,
      zeroHourWouldFire: !!(G._tell && G._tell.id === 'last_call'),
      kindredActive: (function(){try{return _kindredActive();}catch(e){return 'ERR';}})(),
      stillWaters: (function(){try{return _stillWaters();}catch(e){return 'ERR';}})()
    };
  });
  /* and the same four sleeved into a BOSS match, where the boss's own tell
     already occupies G._tell */
  out.boss = {};
  ['last_call','kindred'].forEach(function (id) {
    freshRun();
    S.run.sleeve = id;
    var set = FSIM.setupMatch({tier:3, boss:true, dice:S.run.dice.slice(),
      ench:[null,null,null,null,null,null], badge:id});
    var G = FSIM.getG();
    out.boss[id] = {
      bossTell: G._tell ? G._tell.id : null,
      sleeve: G._sleeve || null,
      ruleActive: (function(){try{return _ruleActive(id,'p');}catch(e){return 'ERR';}})(),
      zeroHourWouldFire: !!(G._tell && G._tell.id === 'last_call')
    };
  });
  OUT.A5 = out;
})();

FSIM.loud(); FSIM.restoreRng();
return OUT;
