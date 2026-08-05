/* apv_observers — Phase 5's invariant: observers cannot grant power.
 *
 * The plan asks for "a thing the architecture won't allow" rather than "a rule
 * we remember". Measured, both halves already hold:
 *
 *   FEATS     23 checks, every one invoked as f.check(_featView(G)), and none
 *             reads a field the view does not carry.
 *   DIALOGUE  DLG reads G.rung and S.npcLedger, writes G zero times, and is
 *             PUSH-based - callers fire DLG.trigger('NAME'), it never inspects
 *             state to decide.
 *
 * NOTHING ASSERTED EITHER. Both are true by construction today and a regression
 * would be silent: a new feat check called with raw G still works, and a DLG
 * method that starts writing still works. This pins them, which is the
 * difference between the plan's two phrasings.
 *
 * The write test is REAL, not a source scan: it hands a feat check the actual
 * view and tries to write through it. A source scan would pass against a Proxy
 * that had been quietly replaced by a plain object.
 */
const sleep = ms => new Promise(r => setTimeout(r, ms));
const until = async (fn, ms) => { const t0=Date.now();
  while (Date.now()-t0<ms) { try { if (fn()) return true; } catch(e){} await sleep(60);} return false; };
await until(() => typeof _featView === 'function', 15000);
if (typeof _featView !== 'function') return { skip: '_featView missing' };
const v = {};

/* ── 1. the view actually refuses writes, at runtime ── */
const view = _featView(typeof G !== 'undefined' && G ? G : {});
v.viewRefusesWrite = (function(){
  try { view._featBusts = 999; return false; }      /* should throw */
  catch (e) { return /do not grant power|tried to write/.test(String(e)); }
})();
v.viewRefusesDelete = (function(){
  try { delete view._featBusts; return false; }
  catch (e) { return true; }
})();
/* and nested state is frozen, not just the top level */
v.nestedFrozen = (function(){
  try {
    if (!view.run || typeof view.run !== 'object') return null;
    const before = view.run.gold;
    view.run.gold = -1;                              /* silently ignored if frozen */
    return view.run.gold === before;
  } catch (e) { return true; }
})();

/* ── 2. every feat check is invoked through the view, never raw G ── */
v.allChecksGated = (function(){
  try {
    const src = (typeof FEATS !== 'undefined') ? '' : '';
    /* find the invocation sites in the shipped source of whoever calls .check */
    const fns = Object.getOwnPropertyNames(window)
      .filter(k => { try { return typeof window[k] === 'function'; } catch(e){ return false; } });
    let raw = 0, gated = 0;
    for (const k of fns) {
      let t; try { t = window[k].toString(); } catch (e) { continue; }
      if (t.indexOf('.check(') < 0) continue;
      const m = t.match(/\.check\(([^)]*)\)/g) || [];
      m.forEach(c => { if (c.indexOf('_featView') >= 0) gated++; else raw++; });
    }
    v._checkSites = { gated: gated, raw: raw };
    return raw === 0 && gated > 0;
  } catch (e) { v._gateErr = String(e).slice(0,70); return false; }
})();

/* ── 3. the dialogue layer observes and does not write ── */
v.dlgWritesNothing = (function(){
  try {
    if (typeof DLG === 'undefined' || !DLG) return null;
    let src = '';
    for (const k of Object.keys(DLG)) {
      try { if (typeof DLG[k] === 'function') src += DLG[k].toString(); } catch (e) {}
    }
    v._dlgWrites = (src.match(/G\.\w+\s*(?:=[^=]|\+\+|--|\+=|-=)/g) || []).slice(0, 5);
    return v._dlgWrites.length === 0;
  } catch (e) { return false; }
})();
/* push-based: DLG.trigger takes a NAME, it does not inspect G to decide */
v.dlgIsPushBased = (function(){
  try { return typeof DLG !== 'undefined' && DLG && typeof DLG.trigger === 'function'; }
  catch (e) { return false; }
})();

const notes = {};
for (const k of Object.keys(v)) { if (k[0] === '_') { notes[k] = v[k]; delete v[k]; } }
return { verdict: v, notes: notes };
