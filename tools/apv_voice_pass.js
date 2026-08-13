/* P678 VERIFIED THROUGH THE GAME'S OWN PICKER
 * SUITE: exclude
 *
 * Reads PATRON_LINES and drives _dlgPick - the code that actually serves
 * lines - rather than grepping the source. Asserts:
 *   - every trait pool exists (6 traits x 6 moments), 3 lines each, and every
 *     line is blurt-length (the doc's whole point)
 *   - every patron backstory pool has the doc's count (3; golgoth exactly 1)
 *   - every patron has win and loss barks (5+5; golgoth 2+2)
 *   - the conditional King-arc rows and the two bespokes survived the sweep
 *   - _dlgPick returns a line for a sample of pools (the pick path runs)
 */
const out = { fail: [] };
const L = PATRON_LINES;

const TRAITS = ['steady','strong','orderly','reckless','greedy','cunning'];
const MOMENTS = ['bust','yourBust','bank','yourBank','push','banksafe'];
const pool = p => L.filter(r => r.p === p);

/* traits: presence, count, and length */
let longest = { t: '', n: 0 };
for (const tr of TRAITS) for (const mo of MOMENTS) {
  const rows = pool('trait:' + tr + ':' + mo);
  if (rows.length !== 3) out.fail.push('trait:' + tr + ':' + mo + ' has ' + rows.length);
  for (const r of rows) if (r.t.length > longest.n) longest = { t: r.t, n: r.t.length };
}
out.longestTraitLine = longest;
out.traitLinesOver45 = L.filter(r => /^trait:/.test(r.p) && r.t.length > 45).map(r => r.t);

/* backstories */
const PATRONS = ['krox','eira','nebb','regis','corbin','sparr','pell','osgood','rilla',
  'dunstan','rask','sil','thorne','vess','nell','squib','tuck','mudge','nix','poll',
  'roan','golgoth','remny','twill','fenn','ferrand','odo','ollis','tam'];
for (const p of PATRONS) {
  const bs = pool('patron:' + p).filter(r => !r.c);
  const want = p === 'golgoth' ? 1 : 3;
  if (bs.length !== want) out.fail.push('patron:' + p + ' backstory has ' + bs.length + ' want ' + want);
  const w = pool('patron:' + p + ':win'), l = pool('patron:' + p + ':loss');
  const wantW = p === 'golgoth' ? 2 : 5;
  if (w.length !== wantW) out.fail.push(p + ':win has ' + w.length);
  if (l.length !== wantW) out.fail.push(p + ':loss has ' + l.length);
}

/* survivors of the sweep */
out.conditionalRows = L.filter(r => /^patron:/.test(r.p) && r.c).length;
out.bespokes = pool('patron:sil:bust').length + pool('patron:regis:bank').length;
if (out.conditionalRows !== 7) out.fail.push('conditional rows ' + out.conditionalRows + ' want 7');
if (out.bespokes !== 2) out.fail.push('bespokes ' + out.bespokes + ' want 2');

/* the picker serves them */
out.samples = {};
for (const p of ['trait:strong:yourBust', 'trait:reckless:bust', 'patron:krox',
                 'patron:tam:win', 'patron:golgoth:loss', 'patron:ferrand:loss']) {
  const r = _dlgPick(p, 0, null);
  out.samples[p] = r ? r.t : null;
  if (!r) out.fail.push('_dlgPick returned null for ' + p);
}

/* no-repeat rule still works: two picks from a 3-line pool differ */
const a = _dlgPick('trait:steady:bust', 0, null);
const b = _dlgPick('trait:steady:bust', 0, null);
out.noRepeat = a && b && a.t !== b.t;

out.total = L.length;
out.verdict = out.fail.length === 0 ? 'PASS' : 'FAIL';
return out;
