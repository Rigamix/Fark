#!/usr/bin/env node
/* PHASE 5, step one — WHAT ASSETS DOES THIS FILE ACTUALLY NAME?
 *
 * The registry cannot be designed before this is answered, and the answer was
 * not what the plan assumed. The plan says `assets/` is the previous game's
 * folder and the registry should make it unreachable. Measured, that is wrong:
 * `assets/` still holds EVERY FONT IN THE GAME, including 'JMH Beda', the one
 * the whole project calls "the game's font". A registry that banned the folder
 * would ban the fonts.
 *
 * So this classifies rather than condemns. Four buckets:
 *
 *   current   Art/Assets/...        the art tree, resolves
 *   legacy    assets/...            the old tree, resolves - still load-bearing
 *   broken    anything that does NOT resolve on disk   <- the real bug class
 *   dynamic   built at runtime from a variable, cannot be checked statically
 *
 * The third bucket is why this runs at all. A path that does not resolve is a
 * 404 the player sees as a missing picture, and nothing in the codebase checks.
 *
 *   node tools/asset_inventory.js           summary
 *   node tools/asset_inventory.js --broken  just the ones that do not resolve
 *   node tools/asset_inventory.js --json    machine-readable, for the probe
 */
const fs = require('fs');
const path = require('path');

const ROOT = path.dirname(__dirname);
const SRC = path.join(ROOT, 'fark_proto.html');
const html = fs.readFileSync(SRC, 'utf8');

/* Every quoted string that looks like an asset path. Deliberately greedy about
   what counts as a path and strict about what counts as a FILE: a prefix
   constant like 'Art/Assets/Buttons/' is a real, useful entry but is not
   itself a file, so it is reported separately rather than as broken. */
const RE = /['"(]((?:Art\/Assets|assets)\/[^'"()\s>]*)/g;

const entries = [];
let m;
while ((m = RE.exec(html)) !== null) {
  const raw = m[1];
  const line = html.slice(0, m.index).split('\n').length;
  entries.push({ raw, line });
}

/* A path is DYNAMIC if the source concatenates onto it - `PT_P+name+'.png'`.
   Those cannot be resolved statically and must not be reported as broken;
   the tell is that the literal has no file extension. */
const EXT = /\.(png|jpe?g|webp|gif|svg|ttf|otf|woff2?|mp3|ogg|wav|json)$/i;

const seen = new Map();
for (const e of entries) {
  const rec = seen.get(e.raw) || { raw: e.raw, lines: [], count: 0 };
  rec.lines.push(e.line); rec.count++;
  seen.set(e.raw, rec);
}

const out = { current: [], legacy: [], broken: [], prefixes: [], dynamic: [] };
for (const rec of seen.values()) {
  const tree = rec.raw.startsWith('Art/Assets') ? 'current' : 'legacy';
  rec.tree = tree;
  if (!EXT.test(rec.raw)) {
    /* a directory prefix, or a path completed at runtime */
    rec.exists = fs.existsSync(path.join(ROOT, rec.raw))
      || fs.existsSync(path.join(ROOT, path.dirname(rec.raw)));
    (rec.raw.endsWith('/') ? out.prefixes : out.dynamic).push(rec);
    continue;
  }
  /* decodeURIComponent because Death&Taxes ships URL-encoded at one call site */
  let disk = rec.raw;
  try { disk = decodeURIComponent(rec.raw); } catch (e) {}
  rec.exists = fs.existsSync(path.join(ROOT, disk));
  if (!rec.exists) out.broken.push(rec);
  else out[tree].push(rec);
}

const sortByRaw = (a, b) => a.raw.localeCompare(b.raw);
Object.keys(out).forEach(k => out[k].sort(sortByRaw));

if (process.argv.includes('--json')) {
  console.log(JSON.stringify(out, null, 1));
} else if (process.argv.includes('--broken')) {
  if (!out.broken.length) console.log('no broken asset paths');
  out.broken.forEach(r => console.log(
    'BROKEN  ' + r.raw + '   (line' + (r.lines.length > 1 ? 's ' : ' ')
    + r.lines.slice(0, 4).join(', ') + (r.lines.length > 4 ? '…' : '') + ')'));
} else {
  console.log('asset inventory — fark_proto.html\n');
  console.log('  current (Art/Assets, resolves) : ' + out.current.length + ' distinct');
  console.log('  legacy  (assets/, resolves)    : ' + out.legacy.length + ' distinct');
  console.log('  BROKEN  (does not resolve)     : ' + out.broken.length + ' distinct');
  console.log('  prefixes (directory constants) : ' + out.prefixes.length);
  console.log('  dynamic (completed at runtime) : ' + out.dynamic.length);
  const legacyDirs = {};
  out.legacy.forEach(r => {
    const d = r.raw.split('/').slice(0, 2).join('/');
    legacyDirs[d] = (legacyDirs[d] || 0) + 1;
  });
  console.log('\n  what is still live in the OLD tree:');
  Object.keys(legacyDirs).sort().forEach(d =>
    console.log('    ' + d.padEnd(30) + legacyDirs[d]));
  if (out.broken.length) {
    console.log('\n  BROKEN:');
    out.broken.forEach(r => console.log('    ' + r.raw + '   line ' + r.lines[0]));
  }
}
