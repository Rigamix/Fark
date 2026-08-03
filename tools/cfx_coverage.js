/* Phase 4 group split, measured live — who is on CFX and who is hardcoded?
 *
 * Phase 4 migrates in two groups: the cards already on `CFX`, then the ones
 * with no CFX entry at all. That second group is the whole reason the split
 * exists: **a migration that enumerates the effect table structurally cannot
 * see them**, so they would have been silently left behind and the migration
 * would have reported success.
 *
 * The plan's counts are known-stale — it says so itself ("69 items, not ~50; 29
 * live cards, not ~31") — so this measures rather than reads.
 *
 * IT ASKS CFX ITSELF, at runtime, rather than grepping for `CFX.foo=`. A grep
 * finds the shapes it was written for; an entry assigned in a loop, spread in
 * from another object, or attached under a computed key is invisible to it and
 * present in the object. The whole point of this group is finding what an
 * enumeration misses, so the enumeration had better be of the real thing.
 *
 * AND FOR THE ONES NOT ON CFX, "hardcoded" is not one condition. Reported per
 * card: whether the id appears anywhere in the source at all, because a card
 * with an effect wired somewhere bespoke and a card with NO implementation
 * both show up as "not on CFX" and they are completely different problems.
 */
const sleep = ms => new Promise(r => setTimeout(r, ms));
await sleep(300);

if (typeof FAM_CARDS === 'undefined' || typeof CFX === 'undefined') {
  return { err: 'FAM_CARDS or CFX not defined at this point' };
}

const HOOKS = ['canUse', 'use', 'roll', 'bank', 'bankBonus', 'turnStart', 'bust'];
const live = (typeof FAM_LIVE === 'object' && FAM_LIVE) || {};

const onBus = [], offBus = [];
FAM_CARDS.forEach(c => {
  const e = CFX[c.id];
  const row = {
    id: c.id, fam: c.fam, kind: c.kind,
    live: !!live[c.id],
    hooks: e ? HOOKS.filter(h => typeof e[h] === 'function') : [],
    extraKeys: e ? Object.keys(e).filter(k => HOOKS.indexOf(k) < 0) : []
  };
  (e ? onBus : offBus).push(row);
});

/* how many hooks does the bus actually carry, and which are unused? */
const hookUse = {};
HOOKS.forEach(h => { hookUse[h] = onBus.filter(r => r.hooks.indexOf(h) >= 0).length; });

/* CFX entries that match no card at all - the other direction of the same
   drift, and the one nobody thinks to check */
const famIds = new Set(FAM_CARDS.map(c => c.id));
const orphanCfx = Object.keys(CFX).filter(k => !famIds.has(k));

return {
  totals: {
    famCards: FAM_CARDS.length,
    onBus: onBus.length,
    offBus: offBus.length,
    liveOffBus: offBus.filter(r => r.live).length,
    orphanCfxEntries: orphanCfx.length
  },
  hookUse: hookUse,
  onBus: onBus.map(r => r.id + ' [' + r.hooks.join(',') + ']'
                        + (r.extraKeys.length ? ' +' + r.extraKeys.join(',') : '')),
  offBus: offBus.map(r => ({ id: r.id, fam: r.fam, kind: r.kind, live: r.live })),
  orphanCfx: orphanCfx
};
