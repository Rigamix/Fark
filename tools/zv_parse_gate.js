/* THE PARSE GATE. Every inline <script> in the page must still parse after a
   patch. A syntax error inside one script kills that script only, so the page
   still loads and still looks alive - which is exactly why this has to be a
   gate and not an eyeball.
   Standalone because it kept being re-implemented inside one-off build scripts
   (zcr_build.js, zd_trade_buildpatch.js, probe_e_dryrun_apply.js all carry a
   copy). Usage: node tools/zv_parse_gate.js [file.html] */
const fs = require('fs'), path = require('path'), vm = require('vm');
const F = process.argv[2] ||
  path.join(__dirname, '..', 'fark_proto.html');
const src = fs.readFileSync(F, 'utf8');

const re = /<script\b([^>]*)>([\s\S]*?)<\/script>/gi;
let m, n = 0, bad = 0, skipped = 0;
while ((m = re.exec(src)) !== null) {
  const attrs = m[1] || '', body = m[2];
  if (/\bsrc\s*=/.test(attrs)) { skipped++; continue; }
  /* a type that is not JS is data, not code - JSON-LD, templates, importmaps */
  const t = /\btype\s*=\s*["']?([^"'\s>]+)/.exec(attrs);
  if (t && !/^(text\/javascript|application\/javascript|module)$/i.test(t[1])) {
    skipped++; continue;
  }
  n++;
  /* the line number in the FILE, so a failure points at the page and not at
     an offset inside an anonymous fragment */
  const line = src.slice(0, m.index).split('\n').length;
  try {
    new vm.Script(body, {filename: F + ':' + line});
  } catch (e) {
    bad++;
    console.error('PARSE FAIL at ' + F + ':' + line + '\n  ' + e.message);
  }
}
console.log('parse gate: ' + n + ' inline script(s) checked, ' +
            skipped + ' skipped (src/non-JS), ' + bad + ' failed');
process.exit(bad ? 1 : 0);
