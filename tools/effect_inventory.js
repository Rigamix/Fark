/* SUITE: exclude — extraction, not an assertion.
 *
 * EFFECT PLAN PHASE 1 needs the roster it is decomposing to be the LIVE one.
 * Every wrong answer this project has produced came from working off a
 * document instead of the code — the feat roster was four lists, the badge
 * rules had ids from the rules they replaced, `assets/` was declared dead
 * while holding every font. So the inventory is read out of the running game.
 *
 * Emits every piece of content the effect system would have to express:
 * enchants, family traits, Break's per-family death rows, family cards, the
 * table rules, and relics — with the fields that reveal SHAPE (does it have
 * charges, tiers, a duration, a target) rather than just names. */
const out = {};

/* ── enchants: the seven icon faces plus Quicksilver ── */
/* TWO TABLES, and guessing one name got an empty roster on the first run.
   ENCH_ICONS holds the seven face-branded ones; ENCHANTS holds Quicksilver
   alone, because it is a whole-die passive with no face — which is itself a
   shape finding, not a bookkeeping quirk. */
out.enchants = (typeof ENCH_GRID !== 'undefined' ? ENCH_GRID : []).map(k => {
  const icon = (typeof ENCH_ICONS !== 'undefined' && ENCH_ICONS[k]) ? ENCH_ICONS[k] : null;
  const plain = (typeof ENCHANTS !== 'undefined' && ENCHANTS[k]) ? ENCHANTS[k] : null;
  const d = icon || plain;
  return { id: k,
           name: d ? d.name : null,
           faceBranded: !!icon,
           doubles: !!(d && d.doubles),          /* Kindred whitelist = "has a meaningful 2x" */
           hasFire: !!(d && typeof d.fire === 'function'),
           price: d ? d.price : null,
           desc: d ? (d.desc || '') : '' };
});

/* ── Break's death rows, one per family ── */
out.breakRows = Object.keys(typeof BREAK_TRIGGERS !== 'undefined' ? BREAK_TRIGGERS : {})
  .map(fam => ({ family: fam, msg: BREAK_TRIGGERS[fam].msg }));

/* ── family cards ── */
out.famCards = (typeof FAM_CARDS !== 'undefined' ? FAM_CARDS : []).map(c => ({
  id: c.id, fam: c.fam, kind: c.kind, name: c.name,
  live: !!(typeof FAM_LIVE !== 'undefined' && FAM_LIVE[c.id]),
  charges: c.charges || null,          /* an active with uses */
  p: c.p || null,                      /* tiered numeric payload */
  unique: !!c.unique,
  consumable: !!c.consumable,
  hasCFX: !!(typeof CFX !== 'undefined' && CFX[c.id]),
  cfxHooks: (typeof CFX !== 'undefined' && CFX[c.id]) ? Object.keys(CFX[c.id]) : [],
  text: (c.text && c.text[0]) ? c.text[0] : (c.eff || '')
}));

/* ── table rules (badges/tells), including the parked one ── */
out.rules = [];
(typeof RUNGS !== 'undefined' ? RUNGS : []).forEach(r => {
  if (r.tell) out.rules.push({ id: r.tell.id, name: r.tell.name, boss: r.name,
                               fields: Object.keys(r.tell).filter(k => k !== 'id' && k !== 'name' && k !== 'desc' && k !== 'icon'),
                               desc: r.tell.desc });
});
Object.keys(typeof PARKED_TELLS !== 'undefined' ? PARKED_TELLS : {}).forEach(k => {
  const t = PARKED_TELLS[k];
  out.rules.push({ id: t.id, name: t.name, boss: '(parked)',
                   fields: Object.keys(t).filter(k2 => k2 !== 'id' && k2 !== 'name' && k2 !== 'desc' && k2 !== 'icon'),
                   desc: t.desc });
});

/* ── relics: dice that carry an effect ── */
out.relics = (typeof DICE_TYPES !== 'undefined' ? DICE_TYPES : [])
  .filter(d => d.relic)
  .map(d => ({ id: d.id, name: d.name, effect: d.effect || null,
               mechanic: (d.effect && d.effect.mechanic) || null,
               bornEnch: d.bornEnch || null }));

/* ── the plain family traits, which live on the die materials ── */
out.materials = (typeof DICE_TYPES !== 'undefined' ? DICE_TYPES : [])
  .filter(d => !d.relic && d.effect)
  .map(d => ({ id: d.id, name: d.name,
               mechanic: (d.effect && d.effect.mechanic) || null }));

out.counts = {
  enchants: out.enchants.length,
  breakRows: out.breakRows.length,
  famCardsLive: out.famCards.filter(c => c.live).length,
  famCardsTotal: out.famCards.length,
  rules: out.rules.length,
  relics: out.relics.length,
  materials: out.materials.length
};
out.counts.total = out.counts.enchants + out.counts.breakRows + out.counts.famCardsLive
                 + out.counts.rules + out.counts.relics + out.counts.materials;
return out;
