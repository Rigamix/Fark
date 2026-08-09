/* Both exits of _removeDieAt must take the SAME targeted snapshot, and neither
   may take the full one.

   Checked against comment-stripped CODE, because the fifth assertion failure of
   this session came from a patch comment quoting the very call it removed -
   "was saveMatchState() - the FULL snapshot" - which a raw text search counts
   as the thing still being there. tools/assert_code.js exists for this and I
   used a raw search anyway. */
const { stripVerified } = require('./assert_code.js');

const src = stripVerified('fark_proto.html');
const i = src.indexOf('function _removeDieAt(lane,opts){');
if (i < 0) { console.log('FAIL: _removeDieAt not found'); process.exit(1); }
const j = src.indexOf('\nfunction ', i + 10);
const body = src.slice(i, j);

const count = t => body.split(t).length - 1;
const snapCalls = count('_snapDiceOnly();');
const fullSaves = count('saveMatchState()');
const helperOnce = src.split('function _snapDiceOnly(){').length - 1;
const definedBefore = src.indexOf('function _snapDiceOnly(){') < i;

const rows = [
  ['both exits call the shared snapshot', snapCalls === 2, snapCalls + ' call(s)'],
  ['no full saveMatchState inside it',    fullSaves === 0, fullSaves + ' found'],
  ['the helper is defined exactly once',  helperOnce === 1, helperOnce],
  ['and defined before its caller',       definedBefore, definedBefore],
];
let bad = 0;
for (const [label, ok, extra] of rows) {
  if (!ok) bad++;
  console.log('  ' + (ok ? 'OK   ' : 'FAIL ') + label.padEnd(40) + ' ' + extra);
}
console.log(bad ? 'FAILURES: ' + bad : 'both doors agree');
process.exit(bad ? 1 : 0);
