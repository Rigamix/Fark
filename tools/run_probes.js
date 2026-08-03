#!/usr/bin/env node
/* THE PROBE RUNNER. Phase 1 of both plans - they share it, so it is built once.
 *
 *   node tools/run_probes.js              run the suite, compare to baseline
 *   node tools/run_probes.js --record     write the baseline from this run
 *   node tools/run_probes.js --only amber run probes whose name matches
 *
 * WHAT IT RUNS. Only probes that carry a `verdict` object - the convention every
 * assertion probe in this project already follows. The other ~31 apv_*.js files
 * are one-off diagnostics from a single investigation; they measure and do not
 * claim, and a runner that treated them as tests would be reporting noise.
 *
 * FIVE THINGS THAT WOULD MAKE THIS LIE, and what is done about each:
 *
 * 1. SHARED STATE. Six probes stub globals - doBust, _ruleActive, famLog,
 *    famFire - to observe them. Two in one page and the second measures the
 *    first's stub. Each probe therefore gets its OWN shoot.js invocation, which
 *    is a fresh browser and a fresh page. Slower, and not negotiable.
 * 2. A DEAD DEV SERVER. It died twice during one session. Without a pre-flight
 *    check that failure arrives as fourteen identical false failures, which is
 *    the most misleading possible output. Checked once, up front, fail fast.
 * 3. KNOWN FAILURES. Some assertions are expected to be red right now - the
 *    plan names one, no relic has a .dtype- block. A suite that is red on day
 *    one gets ignored by day two. The baseline records what is red TODAY so the
 *    runner can report NEW breakage, which is the only thing worth alarming on.
 * 4. A PROBE THAT CRASHES vs ONE THAT FAILS. A page error is not a failed
 *    assertion - it usually means the probe itself is stale. Reported as ERROR,
 *    counted separately, never silently folded into failures.
 * 5. NON-DETERMINISM. These drive a live match with real dice. A probe whose
 *    verdict depends on what was rolled will flap. Any probe that flaps between
 *    runs belongs in the measure pile, not here - the runner surfaces flapping
 *    by comparing against the baseline rather than hiding it.
 */
const { execFileSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const HERE = __dirname;
const URL = process.env.FARK_URL || 'http://localhost:8084/fark_proto.html';
const BASELINE = path.join(HERE, 'probe_baseline.json');
const RECORD = process.argv.includes('--record');
const onlyIx = process.argv.indexOf('--only');
const ONLY = onlyIx > -1 ? process.argv[onlyIx + 1] : null;

/* ── which probes are assertions ── */
const probes = fs.readdirSync(HERE)
  .filter(f => /^apv_.*\.js$/.test(f))
  .filter(f => {
    const src = fs.readFileSync(path.join(HERE, f), 'utf8');
    /* an explicit opt-out, for measurement probes that happen to contain the
       word - they investigate, they do not claim, and a suite that adopts them
       reports noise */
    if (/SUITE:\s*exclude/.test(src)) return false;
    return /verdict\s*[:=]/.test(src);
  })
  .filter(f => !ONLY || f.includes(ONLY))
  .sort();

/* ── pre-flight: is anything serving? ── */
function preflight() {
  try {
    const out = execFileSync(process.execPath, [
      path.join(HERE, 'shoot.js'), '--url', URL, '--eval-file', path.join(HERE, '_preflight.js')
    ], { encoding: 'utf8', timeout: 120000, stdio: ['ignore', 'pipe', 'pipe'] });
    return /"ok":true/.test(out);
  } catch (e) { return false; }
}
fs.writeFileSync(path.join(HERE, '_preflight.js'),
  'return {ok:!!document.getElementById("end-ov"),title:document.title};\n');

console.log('probe runner — ' + probes.length + ' assertion probes\n' + URL + '\n');
if (!preflight()) {
  console.error('DEAD SERVER (or the page did not build) at ' + URL);
  console.error('Nothing was run. Start the dev server and try again — running the');
  console.error('suite against a dead server produces N identical false failures,');
  console.error('which is worse than no result.');
  process.exit(2);
}

/* ── run ── */
const results = {};
let pass = 0, fail = 0, err = 0, skip = 0, ind = 0;
for (const p of probes) {
  process.stdout.write(p.padEnd(34));
  let json = null, crashed = null;
  try {
    const out = execFileSync(process.execPath, [
      path.join(HERE, 'shoot.js'), '--url', URL, '--eval-file', path.join(HERE, p)
    ], { encoding: 'utf8', timeout: 300000, stdio: ['ignore', 'pipe', 'pipe'] });
    const m = out.match(/^setup:\s*(\{[\s\S]*?\})\s*$/m);
    if (m) json = JSON.parse(m[1]); else crashed = 'no setup: line';
  } catch (e) {
    crashed = String((e.stdout || '') + (e.stderr || e.message)).slice(-200);
  }

  if (crashed) { console.log('ERROR   ' + crashed.replace(/\s+/g, ' ').slice(0, 70)); err++; results[p] = { error: true }; continue; }
  /* A PROBE THAT DECLINES IS NOT A PROBE THAT FAILED. Some need a precondition
     the runner cannot guarantee - break_borrowed needs three free dice and the
     roll decides that. Returning {err|skip} with no verdict means "I could not
     run", which is a different fact from "the game is wrong", and folding the
     two together is how a suite starts lying. */
  const v = json && json.verdict;
  if (!v && json && (json.err || json.skip)) {
    console.log('skip    ' + String(json.err || json.skip).slice(0, 60));
    skip++; results[p] = { skipped: true }; continue;
  }
  if (!v || typeof v !== 'object') { console.log('ERROR   returned no verdict'); err++; results[p] = { error: true }; continue; }

  /* A VERDICT KEY MUST BE A BOOLEAN. The first baseline run caught this the
     hard way: apv_bust_settle returned "no bust this roll" - a STRING - for a
     check whose forced bust had not fired, and `=== false` happily passed it.
     An indeterminate check reported as a pass is precisely the lying suite this
     runner's header is about, so anything that is not true/false is called out
     and counted apart from both. */
  const bad  = Object.keys(v).filter(k => v[k] === false);
  const indet = Object.keys(v).filter(k => typeof v[k] !== 'boolean');
  results[p] = v;
  if (bad.length) { console.log('FAIL    ' + bad.join(', ')); fail++; }
  else if (indet.length) {
    console.log('INDET   ' + indet.map(k => k + '=' + JSON.stringify(v[k])).join(', ').slice(0, 62));
    ind++;
  } else { console.log('pass    ' + Object.keys(v).length + ' checks'); pass++; }
}

console.log('\n' + pass + ' pass, ' + fail + ' fail, ' + err + ' error');

/* ── EVERY RUN IS RECORDED, because an intermittent failure that is only ever
   printed to a terminal is unfindable by construction ──────────────────────
   On 2026-08-03 one run of four showed a FAIL that the next three did not, and
   the name was lost with the scrollback. That is the second intermittent in
   this suite - apv_bust_settle flapped earlier the same day - and neither got
   diagnosed, because by the time you know it flaps the evidence is gone.
   Three clean runs afterwards are not an explanation; they are three chances
   to observe it that were not taken.
   So: one line per run, appended, naming exactly what was not green. Cheap
   enough to leave on forever, and the next flap arrives with its own evidence
   instead of a memory of one. */
try {
  const notGreen = {};
  for (const p of Object.keys(results)) {
    const v = results[p];
    if (v.error) { notGreen[p] = 'error'; continue; }
    if (v.skipped) { notGreen[p] = 'skip'; continue; }
    const bad = Object.keys(v).filter(k => v[k] === false);
    const ind = Object.keys(v).filter(k => typeof v[k] !== 'boolean');
    if (bad.length) notGreen[p] = 'FAIL:' + bad.join(',');
    else if (ind.length) notGreen[p] = 'INDET:' + ind.join(',');
  }
  fs.appendFileSync(path.join(HERE, 'probe_history.jsonl'),
    JSON.stringify({ at: new Date().toISOString(), pass, fail, err,
                     notGreen }) + '\n');
} catch (e) { console.log('(history not written: ' + e.message + ')'); }

/* ── compare to the baseline, so only NEW breakage is alarming ── */
if (RECORD) {
  fs.writeFileSync(BASELINE, JSON.stringify(results, null, 1));
  console.log('\nbaseline recorded — ' + Object.keys(results).length + ' probes');
  console.log('Red entries in here are KNOWN failures. The point of the file is');
  console.log('that a suite which is red on day one gets ignored by day two.');
  process.exit(0);
}
if (!fs.existsSync(BASELINE)) {
  console.log('\nno baseline yet — run with --record once this run looks right');
  process.exit(fail || err ? 1 : 0);
}
const base = JSON.parse(fs.readFileSync(BASELINE, 'utf8'));
const regressions = [];
for (const p of Object.keys(results)) {
  const now = results[p], was = base[p];
  if (!was) { regressions.push(p + ' — new probe, not in baseline'); continue; }
  if (now.error && !was.error) { regressions.push(p + ' — now errors'); continue; }
  for (const k of Object.keys(now)) {
    if (now[k] === false && was[k] !== false) regressions.push(p + ' :: ' + k);
  }
}
if (regressions.length) {
  console.log('\nREGRESSIONS vs baseline (' + regressions.length + '):');
  regressions.forEach(r => console.log('  ' + r));
  process.exit(1);
}
console.log('\nno regressions vs baseline');
process.exit(0);
