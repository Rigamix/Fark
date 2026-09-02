/* THE REROLL CENSUS — a standing check, and a prompt to classify rather than a
   number to reconcile.
 *
 * WHY IT IS A TOOL AND NOT AN ASSERT IN A PATCH SCRIPT. P900 put the census in
 * `_p900_seam_and_env.py`, which is a one-shot: it ran once and will never run
 * again, so it guarded the moment it was written and nothing after. And what it
 * printed on failure was "the census in the comment is stale: _setDieVal 6,
 * reDrawDieFace 25" - a number to bump, which is how a guard becomes a
 * formality. This says WHICH line, WHY it matters, and WHAT to do.
 *
 * IT DERIVES, IT DOES NOT ENUMERATE. There is no hand-maintained exempt list -
 * that would be the same defect one level up. A site is a reroll if the value
 * it writes comes from a RANDOM FACE SOURCE (_rollD, rollFace, rollFaceExclude)
 * near the call; a forced value (`d.val=5`, a peeked face, a transmute target)
 * is not. Checked against a hand classification of all 31 sites: the rule
 * agreed on every one.
 *
 * THE EXEMPTION IS AN INLINE COMMENT, so it lives with the code it excuses.
 * Write NOT-A-REROLL and a reason within two lines of the call and this stops
 * asking - a reason at the site beats a list somewhere else that nobody reads.
 *
 * Usage:  node tools/zv_reroll_census.js [file.html]
 * Exit 1 if any in-place value change from a random source has no tag and no
 * stated reason.
 */
const fs = require('fs'), path = require('path');
const F = process.argv[2] || path.join(__dirname, '..', 'fark_proto.html');
const lines = fs.readFileSync(F, 'utf8').split(/\r?\n/);

const CALL = /(?:_setDieVal|reDrawDieFace)\s*\(/;
const DEFN = /function\s+(?:_setDieVal|reDrawDieFace)\s*\(/;
const RANDOM = /_rollD\s*\(|rollFace\s*\(|rollFaceExclude\s*\(/;
const TAG = /_dieReroll\s*\(/;
const EXEMPT = /NOT-A-REROLL/;
/* the window is the STATEMENT, not the line: a site may compute its face a
   line or two above the write, and a tag is armed just before it.
   FIVE, not three, and the third value it was tried at. At 3 the rival's
   sleight site read as a forced value - its `d.val=rollFace(d.mat)` sits four
   lines above its reDrawDieFace, outside the window - so a tagged reroll was
   scored as one that needed no tag. A census that misses a site is worse than
   one that asks about an innocent line: the false positive costs a reading,
   the false negative is the bug this tool exists to prevent. */
const W = 5;
const near = (i, re) => {
  for (let j = Math.max(0, i - W); j <= Math.min(lines.length - 1, i + W); j++)
    if (re.test(lines[j])) return true;
  return false;
};

const untagged = [], tagged = [], exempt = [], forced = [];
lines.forEach((ln, i) => {
  if (!CALL.test(ln) || DEFN.test(ln)) return;
  /* a comment that merely mentions the call is not a call site */
  if (/^\s*(\*|\/\*|\/\/)/.test(ln)) return;
  const entry = {line: i + 1, text: ln.trim().slice(0, 110)};
  if (!near(i, RANDOM)) { forced.push(entry); return; }
  if (near(i, EXEMPT)) { exempt.push(entry); return; }
  if (near(i, TAG)) { tagged.push(entry); return; }
  untagged.push(entry);
});

const rel = path.relative(process.cwd(), F).replace(/\\/g, '/') || F;
console.log('reroll census over ' + rel);
console.log('  in-place value changes : ' + (untagged.length + tagged.length +
                                             exempt.length + forced.length));
console.log('  forced value (no roll) : ' + forced.length);
console.log('  rerolls, tagged        : ' + tagged.length);
console.log('  rerolls, exempted      : ' + exempt.length);
console.log('  rerolls, UNTAGGED      : ' + untagged.length);

if (!untagged.length) { console.log('\nevery reroll is accounted for.'); process.exit(0); }

console.log('');
untagged.forEach(u => {
  console.log('UNTAGGED REROLL at ' + rel + ':' + u.line);
  console.log('    ' + u.text);
  console.log('  This changes a die\'s value from a random face source, so it is a');
  console.log('  reroll, and D3X.MARKS\' `reroll` row will be blind to it - the die');
  console.log('  will tumble unmarked while every other card\'s reroll is ringed.');
  console.log('  -> if it IS a card or enchant reroll: call');
  console.log('     _dieReroll(d.el, D3X.BEAT_INK.<ink>) BEFORE the value changes,');
  console.log('     using that card\'s existing ink rather than a new colour.');
  console.log('  -> if it is NOT one (an ordinary deal, or a forced value that only');
  console.log('     looks random): write NOT-A-REROLL and the reason within two');
  console.log('     lines of the call, and this census will stop asking.');
  console.log('');
});
console.log('Do not "fix" this by editing a count. There is no count to edit -');
console.log('the classification is derived from the code every time it runs.');
process.exit(1);
