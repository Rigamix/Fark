/* Parse gate: pull every inline <script> out of a build and compile it with
   vm.Script. Compile-only, nothing executes.

   THE DEFAULT USED TO BE tools/_zv_trade_scratch.html - an UNTRACKED scratch
   build left over from one investigation in July. Every bare `node
   tools/zv_trade_parsegate.js` since then compiled that frozen file and
   reported PASS, whatever had just been edited. It is the gate that is
   supposed to fail the chain, and it was passing vacuously: a whole session of
   patches to fark_proto.html were gated against a file none of them touched.
   Caught because the reported char count never moved across three different
   edits.

   Two things now make that impossible rather than unlikely. The default is the
   GAME, and the file actually read is printed with its mtime - so a stale
   input is visible in the output instead of hiding behind the word PASS. */
const fs = require('fs');
const vm = require('vm');
const path = process.argv[2] || 'fark_proto.html';
if (!fs.existsSync(path)) {
  console.log('PARSE GATE FAIL -> no such file: ' + path);
  process.exit(1);
}
const html = fs.readFileSync(path, 'utf8');
console.log('gating ' + path + '  (' + html.length + ' bytes, modified '
  + fs.statSync(path).mtime.toISOString() + ')');
const re = /<script(?![^>]*\bsrc=)[^>]*>([\s\S]*?)<\/script>/gi;
let m, i = 0, bad = 0;
while ((m = re.exec(html)) !== null) {
  i++;
  const code = m[1];
  const before = html.slice(0, m.index);
  const startLine = before.split('\n').length;
  try {
    new vm.Script(code, { filename: path + '#script' + i });
    console.log('script ' + i + ' (starts line ' + startLine + ', ' + code.length + ' chars): OK');
  } catch (e) {
    bad++;
    console.log('script ' + i + ' (starts line ' + startLine + '): PARSE FAIL -> ' + e.message);
  }
}
console.log(bad === 0 ? 'PARSE GATE PASS (' + i + ' scripts)' : 'PARSE GATE FAIL');
process.exit(bad === 0 ? 0 : 1);
