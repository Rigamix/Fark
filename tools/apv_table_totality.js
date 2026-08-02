/* PHASE 2 — every lookup table must cover its domain.
 *
 * Four of today's bugs were one shape: a table keyed by id that did not contain
 * every id its consumers would look up, failing SILENTLY to a default.
 *   ASPECT   15 of 38 props  -> missing ones drew SQUARE shadows
 *   MATCOL   key corvus_ledger, id corvus_ledger_d -> that relic never tinted
 *   FEAT_ART 12 of 32 feats  -> the other 20 took the loud overlay path
 *   .dtype-  0 of 8 relics   -> relics draw with default die vars in 2D
 *
 * Each assertion below is the check that would have caught one of them.
 *
 * SOME TABLES ARE FUNCTION-SCOPED and cannot be read from page scope - ASPECT
 * lives inside the props renderer. Rather than change game code to expose it
 * (Phase 2 is meant to be additive), those are read out of the served SOURCE.
 * That is weaker - it proves the literal in the file is total, not that the
 * live object is - and it is marked `via:'source'` wherever used so nobody
 * mistakes one for the other. */
const out = { tables: {}, notes: [] };
const src = await (await fetch('fark_proto.html')).text();

/* pull `var NAME={...}` out of the source and list its top-level keys */
function sourceKeys(name){
  const i = src.indexOf('var ' + name + '={');
  if (i < 0) return null;
  let d = 0, j = src.indexOf('{', i), end = -1;
  for (let k = j; k < src.length; k++){
    if (src[k] === '{') d++;
    else if (src[k] === '}') { d--; if (!d) { end = k; break; } }
  }
  if (end < 0) return null;
  const body = src.slice(j + 1, end);
  const keys = [];
  body.replace(/(^|[,{\s])([A-Za-z_][A-Za-z0-9_]*)\s*:/g, (m, p, k) => { keys.push(k); return m; });
  return keys;
}

function check(label, have, want, via){
  const missing = want.filter(w => have.indexOf(w) < 0);
  const extra   = have.filter(h => want.indexOf(h) < 0);
  out.tables[label] = { have: have.length, want: want.length,
                        missing: missing.slice(0, 12), missingCount: missing.length,
                        strayKeys: extra.slice(0, 12), via: via || 'live' };
  return missing.length === 0;
}

/* ── 1. MATCOL over every die the game can put on the table ── */
let matcolOK = null;
try{
  const ids = DICE_TYPES.map(d => d.id);
  matcolOK = check('MATCOL', Object.keys(D3X.MATCOL), ids);
}catch(e){ out.notes.push('MATCOL: ' + e.message); }

/* ── 2. ASPECT over the prop files it draws shadows for ── */
let aspectOK = null;
try{
  const names = (src.match(/var PROP_POOL=\[[^\]]*\]/) || [''])[0];
  const keys = sourceKeys('ASPECT');
  /* the domain is the files, which a page cannot list - so use the names the
     shipped templates actually reference, which is the set that can bite */
  const used = new Set();
  (window.FK_PROP_TEMPLATES || []).forEach(t => (t.props || []).forEach(q => used.add(q.n)));
  aspectOK = keys ? check('ASPECT', keys, [...used], 'source') : null;
  if (!keys) out.notes.push('ASPECT: could not read the literal from source');
}catch(e){ out.notes.push('ASPECT: ' + e.message); }

/* ── 3. FEAT_ART over FEATS ── */
let featOK = null;
try{
  const ids = (typeof FEATS !== 'undefined' ? FEATS : []).map(f => f.id);
  featOK = check('FEAT_ART', Object.keys(typeof FEAT_ART !== 'undefined' ? FEAT_ART : {}), ids);
}catch(e){ out.notes.push('FEAT_ART: ' + e.message); }

/* ── 4. every relic id has a .dtype- CSS block (KNOWN RED) ── */
let dtypeOK = null;
try{
  const relics = DICE_TYPES.filter(d => d.relic).map(d => d.id);
  const seen = new Set();
  for (const sh of document.styleSheets){
    let rs = null; try{ rs = sh.cssRules; }catch(e){ continue; }
    for (const r of rs) if (r.selectorText) String(r.selectorText)
      .replace(/\.dtype-([A-Za-z0-9_]+)/g, (m, id) => { seen.add(id); return m; });
  }
  dtypeOK = check('.dtype- blocks', [...seen], relics);
}catch(e){ out.notes.push('dtype: ' + e.message); }

/* ── 5. every live family card resolves to art ── */
let cardOK = null;
try{
  const live = Object.keys(typeof FAM_LIVE !== 'undefined' ? FAM_LIVE : {}).filter(k => FAM_LIVE[k]);
  const ALIAS = ['anchor_f','bookends_f'];   /* alias onto vanguard_f, need none */
  const missing = [];
  for (const id of live){
    if (ALIAS.indexOf(id) >= 0) continue;
    try{ if (!(await fetch('assets/cards/' + id + '.webp')).ok) missing.push(id); }
    catch(e){ missing.push(id); }
  }
  out.tables['card art'] = { have: live.length - missing.length, want: live.length - ALIAS.length,
                             missing: missing.slice(0,12), missingCount: missing.length, via: 'live' };
  cardOK = missing.length === 0;
}catch(e){ out.notes.push('card art: ' + e.message); }

/* ── 6. every patron portrait resolves ── */
let portraitOK = null;
try{
  const miss = [];
  for (const n of (typeof PT_ART_POOL !== 'undefined' ? PT_ART_POOL : [])){
    try{ if (!(await fetch(PT_CHAR + n + PT_CHAR_EXT)).ok) miss.push(n); }catch(e){ miss.push(n); }
  }
  out.tables['patron portraits'] = { have: (PT_ART_POOL||[]).length - miss.length,
    want: (PT_ART_POOL||[]).length, missing: miss.slice(0,12), missingCount: miss.length, via: 'live' };
  portraitOK = miss.length === 0;
}catch(e){ out.notes.push('portraits: ' + e.message); }

out.verdict = {
  matcolTotal:    matcolOK,
  aspectTotal:    aspectOK,
  featArtTotal:   featOK,
  relicDtypeTotal:dtypeOK,
  cardArtTotal:   cardOK,
  portraitsTotal: portraitOK
};
return out;
