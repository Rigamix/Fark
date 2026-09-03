/* P937's fallback, tested against the SHIPPED TEXT rather than a copy.
 *
 * WHY THIS EXISTS. The smoke batch reported `subBank 0`, which means the catch
 * never fired, which means the new fallback line never executed. The smoke test
 * verified the file still runs; it did not verify the change. And a bug inside a
 * catch block is the least visible kind there is - an undefined G.target or a
 * typo would surface mid-run, silently, inside the handler whose job is to
 * swallow errors.
 *
 * THE EXPRESSION IS EXTRACTED FROM ladder_band.js, NOT RETYPED. A test that
 * retypes the line under test passes when the shipped line is wrong; that is the
 * two-copies defect wearing a test's clothes. This greps the assignment out of
 * the file, compiles it, and runs it - so if the shipped text has a typo, this
 * fails.
 *
 * NODE ONLY, NO BROWSER. The ladder is running two-way concurrent and a third
 * browser is what killed its first batch.
 */
const fs = require('fs');
const path = require('path');
const src = fs.readFileSync(path.join(__dirname, 'ladder_band.js'), 'utf8');

/* pull the fallback assignment out of the catch block */
const m = src.match(/catch \(e\) \{ subBank\+\+;[\s\S]*?bank = ([\s\S]*?);\s*\}/);
if (!m) { console.log('FAIL: could not find the fallback assignment in ladder_band.js'); process.exit(1); }
const expr = m[1].replace(/\s+/g, ' ').trim();
console.log('extracted from ladder_band.js:');
console.log('  bank = ' + expr);

let fallback;
try { fallback = new Function('G', 'return (' + expr + ');'); }
catch (e) { console.log('FAIL: the shipped expression does not compile: ' + e.message); process.exit(1); }

/* THE CASES. The two behaviours the line must have, and the two ways it could
   quietly not have them. */
const cases = [
  {name: 'a WON match with a small turn - must bank',
   G: {pPts: 9600, turnPts: 50, target: 9500}, want: true},
  {name: 'a won match on the turn total alone - must bank',
   G: {pPts: 0, turnPts: 9500, target: 9500}, want: true},
  {name: 'not won, below 300 - must NOT bank',
   G: {pPts: 1000, turnPts: 250, target: 9500}, want: false},
  {name: 'not won, at 300 - must bank (the old threshold survives)',
   G: {pPts: 1000, turnPts: 300, target: 9500}, want: true},
  {name: 'not won, above 300 - must bank',
   G: {pPts: 1000, turnPts: 900, target: 9500}, want: true},
  /* the failure modes a catch block hides */
  {name: 'no target at all - must not claim a win',
   G: {pPts: 1000, turnPts: 50}, want: false},
  {name: 'no target, above 300 - still banks on the threshold',
   G: {pPts: 1000, turnPts: 400}, want: true},
  {name: 'empty G - must not throw and must not bank',
   G: {}, want: false},
];

let pass = 0, fail = 0;
for (const c of cases) {
  let got, err = null;
  try { got = !!fallback(c.G); } catch (e) { err = e.message; }
  const ok = err === null && got === c.want;
  if (ok) pass++; else fail++;
  console.log(["  ",ok?"PASS":"FAIL"," ",c.name.padEnd(52)," want=",c.want," got=",got,err?" THREW: "+err:""].join(""));/*
    */;
}

/* AND THE LINE MUST ACTUALLY CONTAIN BOTH CLAUSES - a fallback that passed the
   cases by luck of ordering would still be wrong if it lost the target term. */
const hasTarget = /target/.test(expr);
const hasThreshold = /300/.test(expr);
console.log('  %s the shipped line carries a target clause', hasTarget ? 'PASS' : 'FAIL');
console.log('  %s the shipped line carries the 300 threshold', hasThreshold ? 'PASS' : 'FAIL');
if (!hasTarget) fail++; else pass++;
if (!hasThreshold) fail++; else pass++;

console.log('\n%s  %d passed, %d failed', fail ? 'FAILED' : 'ALL PASS', pass, fail);
process.exit(fail ? 1 : 0);
