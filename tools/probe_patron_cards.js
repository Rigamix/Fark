/* WHICH ROSTER IS ACTUALLY IN A PATRON'S HAND?
 *
 * Two sources disagree and neither gets to win by assertion:
 *   - the asset-registry comment says the 133-card CARDS roster is RETIRED
 *   - _generatePatronInner builds a patron hand from CARDS, and
 *     pCardCount = tierIndex>=2 ? 3 : tierIndex>=1 ? 2 : 0  with cardChance:1,
 *     which reads as "every patron from night 2 up always draws 3"
 *
 * I handed Denis a 132-card art list that trusted the second reading. He says
 * the live deck is far smaller and that I am conflating two versions of the
 * game. So this asks the game instead of either of us: launch real patron
 * matches and read what ends up in G.oCards, resolving every id against both
 * rosters.
 *
 * Reports ids, not just counts - a count cannot tell you WHICH roster won.
 */
  const sleep = ms => new Promise(r => setTimeout(r, ms));
  const until = async (fn, ms) => { const t0 = Date.now();
    while (Date.now() - t0 < ms) { try { if (fn()) return true; } catch (e) {} await sleep(50); }
    return false; };

  if (typeof S === 'undefined' || typeof launchPatronMatch !== 'function')
    return { error: 'launchPatronMatch missing - probe never reached the game' };

  const oldIds = new Set((typeof CARDS !== 'undefined' ? CARDS : []).map(c => c && c.id));
  const npcIds = new Set((typeof NPC_CARDS !== 'undefined' ? NPC_CARDS : []).map(c => c && c.id));
  const famIds = new Set((typeof FAM_CARDS !== 'undefined' ? FAM_CARDS : []).map(c => c && c.id));

  const out = { rosterSizes: { CARDS: oldIds.size, NPC_CARDS: npcIds.size, FAM_CARDS: famIds.size },
                tiers: [], seenOld: [], seenNpc: [], seenFam: [], seenUnknown: [] };

  /* also ask the generator directly - it is the function under suspicion, and
     calling it is cheaper and less stateful than a full match */
  if (typeof generateOppCards === 'function' && typeof TIERS !== 'undefined') {
    for (let t = 0; t < 8; t++) {
      const rung = (TIERS[t] && TIERS[t].boss) || null;
      let bossDraw = [];
      try { if (rung) bossDraw = generateOppCards(rung, 0) || []; } catch (e) {}
      out.tiers.push({ tier: t, bossPool: (rung && rung.cardPool) ? rung.cardPool.length : 0,
                       bossDraw: bossDraw });
    }
  }

  /* now a real patron match per tier, which is the only thing that proves the
     patron branch fires at all */
  for (let t = 0; t < 8; t++) {
    try {
      _getS();
      S.run = S.run || {};
      S.run.tier = t;
      S.run.dice = ['bone','bone','bone','bone','bone','bone'];
      S.run.cards = S.run.cards || [];
      launchPatronMatch();
    } catch (e) { out.tiers[t] && (out.tiers[t].launchErr = e.message); continue; }
    const ok = await until(() => typeof G !== 'undefined' && G && G.rung, 8000);
    if (!ok) { out.tiers[t] && (out.tiers[t].noMatch = true); continue; }
    const held = (G.oCards || []).slice();
    const row = out.tiers[t] || (out.tiers[t] = { tier: t });
    row.patronHeld = held;
    row.patronCount = held.length;
    for (const id of held) {
      if (npcIds.has(id)) out.seenNpc.push(id);
      else if (famIds.has(id)) out.seenFam.push(id);
      else if (oldIds.has(id)) out.seenOld.push(id);
      else out.seenUnknown.push(id);
    }
    await sleep(120);
  }

  const uniq = a => Array.from(new Set(a));
  out.seenOld = uniq(out.seenOld); out.seenNpc = uniq(out.seenNpc);
  out.seenFam = uniq(out.seenFam); out.seenUnknown = uniq(out.seenUnknown);
  out.verdict = out.seenOld.length
    ? 'OLD ROSTER IS LIVE in patron hands (' + out.seenOld.length + ' distinct ids seen)'
    : 'no old-roster card reached a patron hand in this sample';
  window.__patronCards = out;
  return out;
