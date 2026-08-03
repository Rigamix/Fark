/* EVERY CFX HANDLER MUST CORRESPOND TO A LIVE CARD.
 *
 * Five surfaces this session ran correctly and could never be reached:
 * #screen-bossreward (no showScreen caller), #rulesOverlay (entry button not
 * visible), body::before (display:none), and CFX handlers for tar_pit and
 * _ward_retired - both retired from FAM_LIVE, both still carrying effect code.
 *
 * Five is enough that this stops being a thing to notice and becomes step one
 * of any refactor: does this handler answer to anything the game can still
 * offer? A dead handler is not harmless - it is content a migration will
 * faithfully carry forward, and a reader will treat as live.
 *
 * FAM_LIVE is the domain. A CFX key outside it is unreachable by construction:
 * the draft pools and the offer check both read FAM_LIVE, so a card absent from
 * it can never be equipped, and famFire only walks equipped cards. */
const out = { notes: [] };
if (typeof CFX === 'undefined' || typeof FAM_LIVE === 'undefined') {
  return { err: 'CFX or FAM_LIVE not in scope' };
}
const handlers = Object.keys(CFX);
const live = Object.keys(FAM_LIVE).filter(k => FAM_LIVE[k]);
/* the alias table is real indirection, not a loophole: anchor_f and bookends_f
   both resolve to vanguard_f, so a handler keyed by an alias IS reachable */
const alias = (typeof _FAM_ALIAS !== 'undefined') ? _FAM_ALIAS : {};
const resolves = k => live.indexOf(alias[k] || k) >= 0;

out.handlerCount = handlers.length;
out.liveCount = live.length;
out.dead = handlers.filter(k => !resolves(k));
/* and the other direction: a live card with no handler is not a bug - it may be
   hardcoded at a call site - but the count is worth reporting, because Phase 1
   measured exactly that and it is the group a table-driven migration misses */
out.liveWithoutHandler = live.filter(k => !CFX[k]);

out.verdict = {
  noDeadHandlers: out.dead.length === 0,
  /* reported, never asserted: 9 live cards are deliberately hardcoded */
  countsReconcile: (out.handlerCount - out.dead.length) > 0
};
return out;
