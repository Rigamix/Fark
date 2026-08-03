/* apv_legacy_retired — the old 133-card roster stays retired.
 *
 * P1b retired the previous game's card roster on BOTH sides and deliberately
 * deferred the physical deletion: "~330 old effect sites now inert; physical
 * deletion deferred (dead code, no behavior)". So 133 definitions and 147 art
 * files sit in the file doing nothing, held back by three one-line stubs.
 *
 * THAT IS A FRAGILE WAY TO KEEP CONTENT DEAD. Every one of those stubs is a
 * `return []` on the first line of a function whose remaining twenty lines
 * still read the old pools and still work. Delete the stub by accident, or
 * "restore" one while fixing something nearby, and the old roster comes back
 * live with no error and no visible break - it would just start dealing cards
 * from the previous game again. Nothing today would catch that.
 *
 * So this asserts the retirement rather than trusting it, and it does so by
 * CALLING the functions rather than reading the source: a `return []` that has
 * been commented out still looks like a `return []` to a grep of the file.
 *
 * WHAT IT DOES NOT CLAIM. The opponent's cards are not merely retired - they
 * are PARKED. P5 brings NPC cards back as FAMILY cards, and the authored boss
 * pools (Grog's her_lucky_coin, Mabel's mabels_pinch) stay as the design record
 * of each boss's card identity. This probe going green means the old roster is
 * not being dealt. It does not mean the roster is safe to delete.
 */
const sleep = ms => new Promise(r => setTimeout(r, ms));
await sleep(400);

const out = { checked: [], leaked: [] };

/* the old roster's ids, from the array itself rather than a copy that can rot */
const oldIds = new Set((typeof CARDS !== 'undefined' ? CARDS : []).map(c => c.id));

/* ── 1. the player-side stub ── */
let eff = null;
try { eff = effectiveCards(); } catch (e) { eff = 'threw: ' + e; }
out.checked.push({ fn: 'effectiveCards', got: Array.isArray(eff) ? eff.length : eff });

/* ── 2. the opponent-side stub. Fed a rung that DOES have an old-roster pool,
   because calling it with nothing proves only that nothing came back from
   nothing - the boss table is where the old ids actually live. ── */
let opp = null;
try {
  opp = generateOppCards({ key: 'grog', cardPool: ['her_lucky_coin', 'grogs_bump'],
                           cardCount: 2, cardChance: 1 }, 2);
} catch (e) { opp = 'threw: ' + e; }
out.checked.push({ fn: 'generateOppCards', got: Array.isArray(opp) ? opp.length : opp });

/* ── 3. nothing old is actually being held ── */
function held() {
  const a = [];
  try { if (S && S.run && S.run.cards) a.push(...S.run.cards.filter(Boolean)); } catch (e) {}
  try { if (G && G.pCards) a.push(...G.pCards); } catch (e) {}
  try { if (G && G.oCards) a.push(...G.oCards); } catch (e) {}
  return a;
}
held().forEach(id => { if (oldIds.has(id)) out.leaked.push(id); });

/* ── 4. and the art loader stays off the old tree ── */
let artSrc = '';
try { artSrc = _cardArtImg('honeytrap') || ''; } catch (e) { artSrc = 'threw'; }
const oldTree = /assets\/Card_ART\//.test(artSrc);

return {
  oldRosterSize: oldIds.size,
  checked: out.checked,
  leaked: out.leaked,
  artSrc: artSrc.slice(0, 90),
  verdict: {
    playerStubHolds: Array.isArray(eff) && eff.length === 0,
    opponentStubHolds: Array.isArray(opp) && opp.length === 0,
    nothingOldHeld: out.leaked.length === 0,
    /* PROMOTED INTO THE VERDICT NOW THE ART IS ARCHIVED. This was recorded and
       deliberately NOT asserted while _cardArtImg still built an
       assets/Card_ART/ src, because a probe that ships permanently red teaches
       people to ignore it - the same reason the five known 2px overflows came
       out of apv_font_metrics' verdict. The 149 files have moved to
       assets/_archive/Card_ART/ and the loader returns '', so the condition is
       now true and failing it would mean a real regression.
       Phrased "off" rather than "on" deliberately: a key whose TRUE value
       describes the BAD state passes the suite while reading like a complaint,
       which is how a check ends up asserting the opposite of what it looks
       like it asserts. */
    artLoaderOffOldTree: !oldTree
  }
};
