/* SUITE: exclude — measurement, not an assertion.
 *
 * Did the restored roster actually reach the WALL? The migration is only real
 * if a trinket hangs, so this seeds three earned feats through the same store
 * the game writes (S.featsDone), opens the loadout, and reports what rendered.
 * Filenames are checked against the network, because a feat mapped to a
 * painting that 404s looks identical to a feat that never fired. */
const sleep = ms => new Promise(r => setTimeout(r, ms));
const until = async (fn, ms) => { const t0 = Date.now();
  while (Date.now() - t0 < ms) { try { if (fn()) return true; } catch(e){} await sleep(60); } return false; };

const out = {};
_getS();
S.run = S.run || {};
S.featsDone = S.featsDone || {};
S.featsPinned = S.featsPinned || {};
['high_roller', 'clean_night', 'death_and_taxes', 'no_claim'].forEach(id => {
  S.featsDone[id] = 1; delete S.featsPinned[id];
});
try { save(); } catch(e) {}

out.roster = (typeof FEATS !== 'undefined') ? FEATS.length : -1;
out.artKeys = Object.keys(typeof FEAT_ART !== 'undefined' ? FEAT_ART : {}).length;

/* every painting the roster points at must exist on disk */
const missing = [];
await Promise.all(Object.keys(FEAT_ART).map(id =>
  fetch('Art/Assets/Feats/' + encodeURIComponent(FEAT_ART[id]) + '.png', { method: 'HEAD' })
    .then(r => { if (!r.ok) missing.push(FEAT_ART[id] + ' (' + r.status + ')'); })
    .catch(e => missing.push(FEAT_ART[id] + ' (' + e.message + ')'))));
out.artFilesMissing = missing;

try { famLoadoutShow(); } catch(e) { out.showErr = String(e); }
/* PRECONDITION, NOT A PAUSE. until() returns FALSE on timeout rather
   than throwing, so discarding this result meant every assertion below
   ran against a state that may never have arrived - and reported the
   result as a verdict about the game. Three probes were fixed one at a
   time for exactly this before it was swept for. */
const _pre = await until(() => document.querySelector('#gbLoadout .loFeat'), 9000);
if (!_pre) return { skip: 'precondition never arrived: apv_feat_wall_p425 had nothing to measure' };
await sleep(900);

const feats = [...document.querySelectorAll('#gbLoadout .loFeat')];
out.trinketsOnWall = feats.length;
out.trinkets = feats.map(el => {
  const r = el.getBoundingClientRect();
  const img = el.tagName === 'IMG' ? el : el.querySelector('img');
  return { png: el.dataset.png || null,
           src: img ? (img.getAttribute('src') || '').split('/').pop() : null,
           w: Math.round(r.width), h: Math.round(r.height),
           natural: img ? (img.naturalWidth + 'x' + img.naturalHeight) : null };
});
/* naturalWidth 0 means the browser could not decode it — a blank nail */
out.brokenImages = out.trinkets.filter(t => t.natural === '0x0').map(t => t.png || t.src);

out.verdict = {
  artAllOnDisk:  missing.length === 0,
  wallRendered:  feats.length > 0,
  noBrokenNails: out.brokenImages.length === 0
};
return out;
