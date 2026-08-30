#!/usr/bin/env node
/* zv_decl_diff — the gate that would have caught P863's deletion of an entire
 * table, and did not exist because nobody had needed it yet.
 *
 * WHY IT EXISTS. P863 removed rows from two arrays. Its row-deleter overshot on
 * each table's LAST row and swallowed everything up to the next declaration —
 * including all 130 lines of NPC_BUST_SAVES, which happened to sit in the gap.
 * The parse gate caught the wreckage immediately and reported
 * "Unexpected token 'var'". That was read as "the array lost its bracket", the
 * bracket was restored, the gate went green, and the missing table shipped.
 *
 * A syntax error localises where PARSING failed, not what was DELETED. Once the
 * bracket was back the file parsed perfectly — it was simply missing a whole
 * well-formed declaration that three live call sites still referenced. The
 * result was a ReferenceError on the rival's bust path: NPCs froze mid-turn and
 * the match could not continue.
 *
 * So: for any patch that deletes code, "it still parses" is not the question.
 * "Does anything still reference what I removed" is. That is this.
 *
 * USAGE
 *   node tools/zv_decl_diff.js [baseRef] [file] [baseFile]
 *     baseRef   git ref to compare against  (default: HEAD)
 *     file      path to check               (default: fark_proto.html)
 *     baseFile  path INSIDE baseRef         (default: same as file)
 *
 * baseFile exists so the gate can be shown failing against the real broken
 * build rather than only passing on a good one — a check nobody has watched
 * fail is not known to work.
 *
 * Exit 1 if any top-level declaration present in baseRef is absent from the
 * working file AND still referenced by it. Deliberate deletions are silent as
 * long as nothing points at the hole, so this does not fight a real cleanup.
 */
const { execSync } = require('child_process');
const fs = require('fs');

const baseRef = process.argv[2] || 'HEAD';
const file = process.argv[3] || 'fark_proto.html';
const baseFile = process.argv[4] || file;

const DECL = /^(?:var|const|let|function)\s+([A-Za-z_$][\w$]*)/gm;

function decls(src) {
  const out = new Set();
  let m;
  DECL.lastIndex = 0;
  while ((m = DECL.exec(src))) out.add(m[1]);
  return out;
}

let base;
try {
  base = execSync(`git show ${baseRef}:${baseFile}`, { maxBuffer: 1 << 28 }).toString('utf8');
} catch (e) {
  console.error(`could not read ${baseRef}:${baseFile} — ${e.message}`);
  process.exit(2);
}
const live = fs.readFileSync(file, 'utf8');

const lost = [...decls(base)].filter(d => !decls(live).has(d)).sort();

/* A reference INSIDE a comment is not a reference. Strip block and line
   comments before counting, or every deletion that leaves a historical note
   behind reads as a live break — which is exactly the false alarm that would
   get this gate switched off. */
const code = live
  .replace(/\/\*[\s\S]*?\*\//g, ' ')
  .replace(/(^|[^:])\/\/[^\n]*/g, '$1 ');

const broken = [];
for (const d of lost) {
  const n = (code.match(new RegExp('\\b' + d.replace(/\$/g, '\\$') + '\\b', 'g')) || []).length;
  if (n > 0) broken.push({ name: d, refs: n });
}

console.log(`decl diff  ${file}  vs ${baseRef}`);
console.log(`  declarations in base : ${decls(base).size}`);
console.log(`  declarations now     : ${decls(live).size}`);
console.log(`  removed              : ${lost.length}${lost.length ? '  (' + lost.join(', ') + ')' : ''}`);

if (broken.length) {
  console.error('\nDECL DIFF FAIL — removed but STILL REFERENCED in code:');
  for (const b of broken) console.error(`  ${b.name}  <- ${b.refs} live reference${b.refs === 1 ? '' : 's'}`);
  console.error('\nEach of these throws a ReferenceError the first time that path runs.');
  console.error('A file can parse perfectly and still be missing a whole declaration.');
  process.exit(1);
}
console.log('DECL DIFF PASS — nothing removed is still referenced');
