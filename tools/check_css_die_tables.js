/* die_texture_lab carries the GAME'S OWN D3 renderer, extracted verbatim out of
   fark_proto.html. That is a copy, and a copy of a game constant is the exact
   shape this audit has spent a session deleting. The difference between an
   acceptable copy and a bug is whether drift is detectable, so: re-extract from
   the game, compare to what the lab holds, and fail loudly when they part.

   WHY THE WHOLE RENDERER AND NOT JUST THE TABLES. The first attempt shipped
   D3's PLACE/FACE_ROT/TINT into the lab and re-implemented the cube by nesting
   CSS 3D transforms. It rendered flat, because the game uses no CSS 3D at all -
   D3.draw computes each face's matrix3d in JS and culls back-faces itself. Right
   constants, wrong algorithm, and it looked authoritative. Copying the code
   leaves nothing to re-implement incorrectly.

   Run: node tools/check_css_die_tables.js [path-to-lab] */
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

const HERE = __dirname;
const GAME = path.join(HERE, '..', 'fark_proto.html');
const LAB = process.argv[2] ||
  path.join(HERE, '..', '..', '..', '..', 'die_texture_lab.html');

function extractD3(src) {
  const i = src.indexOf('\nvar D3={') + 1;
  if (i <= 0) return null;
  const j = src.indexOf('D3.start=function(){', i);
  if (j < 0) return null;
  let depth = 0, k = src.indexOf('{', j);
  for (; k < src.length; k++) {
    if (src[k] === '{') depth++;
    else if (src[k] === '}' && --depth === 0) break;
  }
  return src.slice(i, src.indexOf('\n', k));
}

function extractCSS(src) {
  const sels = ['.d3slot{', '.d3shadow{', '.d3die{', '.d3f{', '.d3f .d3sh{',
                '.d3f .d3wash{', '.d3f .d3grnd{'];
  return sels.map(sel => {
    const a = src.indexOf('\n' + sel);
    if (a < 0) return null;
    return src.slice(a + 1, src.indexOf('}', a) + 1).trim();
  }).join('\n');
}

if (!fs.existsSync(LAB)) {
  console.log('SKIP: the lab is not at ' + LAB + ' (it is an untracked dev tool)');
  process.exit(0);
}
const game = fs.readFileSync(GAME, 'utf8');
const lab = fs.readFileSync(LAB, 'utf8');

const d3 = extractD3(game);
const css = extractCSS(game);
if (!d3 || !css) { console.log('FAIL: could not re-extract D3 from the game'); process.exit(1); }
const want = crypto.createHash('md5').update(d3 + css).digest('hex');

const m = /CSSDIE_SOURCE_STAMP="([0-9a-f]{32})"/.exec(lab);
if (!m) {
  console.log('FAIL: the lab has no CSSDIE_SOURCE_STAMP - was the CSS die removed?');
  process.exit(1);
}
const got = m[1];

/* the stamp could match while the lab's copy was hand-edited, so check the
   body too - a stamp that vouches for a body nobody compared is a display
   vouching for the thing it is supposed to be evidence about */
const bodyPresent = lab.includes('D3.make=function(host,opts)') &&
                    lab.includes('D3.draw=function(d)') &&
                    lab.includes('D3.start=function()');
/* NORMALISE LINE ENDINGS BEFORE COMPARING. fark_proto.html is LF and the lab is
   CRLF, so the injected copy is byte-different and semantically identical. The
   first run of this check failed on exactly that, which is worth keeping in
   mind: the STAMP passed, because the patch and this checker both compute it
   from the game and neither reads the lab's body. Only this comparison looks at
   what the lab actually holds - the stamp on its own is a number vouching for
   itself. */
const norm = t => t.replace(/\r\n/g, '\n');
const nlab = norm(lab), nd3 = norm(d3);
/* EXTRACT FROM THE LAB THE SAME WAY, AND HASH BOTH. The first version of this
   compared the first and last 400 characters, which would have passed a drift
   anywhere in the middle - and the middle is precisely where TINT lives, so the
   one table most likely to be edited was the one the check could not see. A
   sample of the ends is a proxy for the body, not the body. */
const labD3 = extractD3(nlab);
const bodyMatches = !!labD3 &&
  crypto.createHash('md5').update(labD3).digest('hex') ===
  crypto.createHash('md5').update(nd3).digest('hex');

const rows = [
  ['the lab carries a source stamp', !!m, got.slice(0, 12)],
  ['it matches the game today', got === want, got === want ? 'ok' : got.slice(0, 8) + ' vs ' + want.slice(0, 8)],
  ['the renderer body is present', bodyPresent, bodyPresent],
  ['the lab body hashes equal to the game', bodyMatches, bodyMatches],
];
let bad = 0;
for (const [label, ok, extra] of rows) {
  if (!ok) bad++;
  console.log('  ' + (ok ? 'OK   ' : 'FAIL ') + String(label).padEnd(38) + ' ' + extra);
}
if (bad) {
  console.log('\nFAILURES: ' + bad + '\nThe lab and the game disagree. Either the game\'s renderer moved on, or the');
  console.log('lab\'s copy was hand-edited. Re-run the extraction so the lab draws what the');
  console.log('game draws - do NOT reconcile it by editing the lab, which is how a copy');
  console.log('stops being a copy.');
}
process.exit(bad ? 1 : 0);
