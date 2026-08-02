/* THE BADGE REMAP — and the class of bug it kept turning up.
 *
 * Three rules moved: Grog Zero Hour -> Last Call (own id, 800), Mabel Steeped
 * -> Zero Hour, Steeped parked with no badge. Each move could fail silently in
 * the same way, and that shape is what this asserts:
 *
 *   A RULE MUST BE REACHABLE BY ALL THREE ROUTES IT CLAIMS. A boss badge, a
 *   sleeve, and a sealed seat are three doors to the same rule. Zero Hour read
 *   `G._tell.id` directly, so it worked as a badge and was DEAD through the
 *   other two - while being claimable as boss spoils. Steeped had the split in
 *   the other direction: it ACCRUED through _ruleActive and PAID OUT through
 *   G._tell, which agreed only while Mabel wore it.
 *
 * So every check below drives a rule through a door that is NOT its badge. */
const out = { rungs: {}, notes: [] };

/* ── the roster, as the game defines it ── */
RUNGS.forEach(r => { if (r.tell) out.rungs[r.name] = { id: r.tell.id, name: r.tell.name }; });

const grog  = RUNGS.find(r => r.key === 'drunkard');
const mabel = RUNGS.find(r => r.key === 'peasant');
out.grogTell  = grog  && grog.tell  ? { id: grog.tell.id,  name: grog.tell.name,  minBank: grog.tell.minBank } : null;
out.mabelTell = mabel && mabel.tell ? { id: mabel.tell.id, name: mabel.tell.name } : null;

/* ── a parked rule still has to be findable, or the seal pool gets null ── */
const parked = _tellById('steeped');
out.parkedSteeped = parked ? { id: parked.id, name: parked.name, perRoll: parked.perRoll } : null;
out.steepedOnNoBadge = !RUNGS.some(r => r.tell && r.tell.id === 'steeped');

/* every id the seal pool can roll must resolve — a pool entry that returns
   null is a cursed seat with no rule, which looks like nothing happening */
out.sealPool = _SEAL_POOL.slice();
out.sealPoolUnresolvable = _SEAL_POOL.filter(id => !_tellById(id));

/* ── the three doors ── */
/* Stub a minimal G rather than driving a match: _ruleActive reads exactly
   these three fields and nothing else, so this exercises the real function
   against the real tables. */
const realG = (typeof G !== 'undefined') ? G : null;
function doors(id){
  const r = {};
  G = { _tell: { id: id }, _sleeve: null, _sealRule: null }; r.badge  = _ruleActive(id, 'p');
  G = { _tell: null,       _sleeve: id,   _sealRule: null }; r.sleeve = _ruleActive(id, 'p');
  G = { _tell: null,       _sleeve: null, _sealRule: id   }; r.seal   = _ruleActive(id, 'p');
  return r;
}
/* ALL EIGHT, plus the parked one. P428 renamed three ids to match the rules
   they carry (first_strike/still_waters/kindred, formerly in_arrears/
   confession/counterfeit) - a rename is exactly the change that can leave a
   rule resolving through one door and not another, so every rule the game has
   is walked rather than a chosen five. */
out.doors = {};
['last_call', 'zero_hour', 'pickpocket', 'first_strike', 'drill_order',
 'still_waters', 'kindred', 'reckoning', 'steeped'].forEach(id => {
  out.doors[id] = doors(id);
});
/* and no rule may still answer to a retired id */
out.staleIds = ['in_arrears', 'confession', 'counterfeit'].filter(id => !!_tellById(id));
out.retiredRules = Object.keys(_RETIRED_RULES || {});

/* ── the payout path, not just the flag ── */
/* Steeped's bonus is READ in four places that used to key off G._tell. Prove
   the source text no longer contains that read at all, since a stubbed G
   cannot exercise a bank. */
out.steepedDirectReads = null;
try {
  const src = document.documentElement.outerHTML;
  out.steepedDirectReads = (src.match(/G\._tell\.id===['"]steeped['"]/g) || []).length;
  out.zeroHourDirectReads = (src.match(/G\._tell\.id===['"]last_call['"]/g) || []).length;
}catch(e){ out.notes.push('source read: ' + e.message); }

if (realG) G = realG; else try { G = null; }catch(e){}

out.verdict = {
  grogIsLastCall:     !!(out.grogTell && out.grogTell.id === 'last_call'
                         && out.grogTell.name === 'LAST CALL' && out.grogTell.minBank === 800),
  mabelIsZeroHour:    !!(out.mabelTell && out.mabelTell.id === 'zero_hour'
                         && out.mabelTell.name === 'ZERO HOUR'),
  steepedParkedNotLost: !!out.parkedSteeped && out.steepedOnNoBadge,
  everySealRuleResolves: out.sealPoolUnresolvable.length === 0,
  /* the headline: every rule reachable through all three doors */
  allRulesReachAllDoors: Object.keys(out.doors).every(id =>
    out.doors[id].badge && out.doors[id].sleeve && out.doors[id].seal),
  noStaleRuleIds: out.staleIds.length === 0,
  everyBadgeIdMatchesItsRule: RUNGS.filter(r => r.tell).every(r =>
    r.tell.id === r.tell.name.toLowerCase().replace(/^the /, '').replace(/\s+/g, '_')),
  noDirectTellReads:  out.steepedDirectReads === 0 && out.zeroHourDirectReads === 0
};
return out;
