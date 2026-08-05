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
 * WHAT IT DOES NOT CLAIM. This going green means the old roster is not being
 * dealt. It does not mean the roster is safe to delete.
 *
 * UPDATED WHEN THE OPPONENT STUB WAS LIFTED (P473). This used to assert
 * `opponentStubHolds` - that generateOppCards returns []. THE STUB WAS NEVER
 * THE INVARIANT; it was one disposable way of enforcing one. The invariant is
 * that NO RETIRED ID IS EVER DEALT, and that is now asserted directly, so it
 * holds whichever mechanism patron cards arrive by.
 *
 * The header used to say the opponent's cards were "PARKED - P5 brings NPC
 * cards back as FAMILY cards". That read the stub's own "NPC family cards land
 * in P5" as meaning generateOppCards stays dead forever. Ruled otherwise: the
 * two mechanisms are not exclusive - oCards/mechanic dispatch and
 * _famInitOpp/CFX run alongside each other, as the family layer already does.
 * CARDS is the retired 133-card roster; NPC_CARDS is the current one. Dealing
 * from the second is not resurrecting the first, and this probe now says so in
 * those terms instead of guarding a mechanism.
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
/* the current roster, to tell "dealt something" apart from "dealt something OLD" */
const curIds = new Set((typeof NPC_CARDS !== 'undefined' ? NPC_CARDS : []).map(c => c.id));
const oppOld = Array.isArray(opp) ? opp.filter(id => oldIds.has(id)) : [];
const oppUnknown = Array.isArray(opp) ? opp.filter(id => !curIds.has(id)) : [];
const effOld = Array.isArray(eff) ? eff.filter(id => oldIds.has(id && id.id ? id.id : id)) : [];
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
  oppDealt: Array.isArray(opp) ? opp : String(opp),
  oppOld: oppOld, oppUnknown: oppUnknown,
  verdict: {
    /* THE INVARIANT, three ways. Not "the stub holds" - the stub was one
       disposable enforcement of this, and P473 replaced it with a real deal.
       What must never be true is that a RETIRED id reaches a hand. */
    playerDealsNoOld: Array.isArray(eff) && effOld.length === 0,
    oppDealsNoOld: Array.isArray(opp) && oppOld.length === 0,
    /* and everything dealt is a card that actually exists in the CURRENT
       roster - an unknown id is a card that resolves to null and silently does
       nothing, which looks identical to a boss playing badly */
    oppDealsOnlyKnown: Array.isArray(opp) && oppUnknown.length === 0,
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
