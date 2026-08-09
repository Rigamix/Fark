/* ASSERT AGAINST CODE, NEVER AGAINST TEXT.

   Four patch assertions in one session failed by matching the OLD code quoted
   inside the NEW comment that explains its removal. Each fix narrowed the
   problem instead of solving it:

     1. `_dropLanes` matched the words "its own _dropLanes" in prose
     2. "unreachable today ..." matched the claim quoted in its own correction
     3. `G._breakPending={src:c.die}` matched the same
     4. `oLane` matched a comment reading "ONLY lane MOVES, NEVER oLane"

   After (3) I switched to "unique full lines", which is what let (4) through.
   Denis's verdict, and it is the right one: the text-matching problem was never
   solved, only narrowed. Anything short of stripping comments properly will
   keep finding new ways to fail the same way.

   A REGEX CANNOT DO THIS. /\*.*?\*\/ over a 2MB file mis-pairs against `/*`
   inside string literals and regex literals - measured, it swallowed real code
   in P528 and reported a guard missing that was present. So this is a scanner:
   it tracks single quotes, double quotes, template literals (including ${}
   nesting), line comments, block comments, and regex literals.

   AND IT CHECKS ITSELF. Regex-literal detection in JS needs context, and this
   scanner uses a heuristic for it. So after stripping, every <script> block is
   RE-COMPILED with vm.Script. If the stripped source no longer parses, the
   stripper got something wrong and this tool REFUSES TO ANSWER rather than
   returning a count that might be nonsense. A tool that cannot tell the real
   thing from something resembling it is the whole failure mode being fixed
   here; it must not be reintroduced one level up.

   Usage:
     node tools/assert_code.js <file> "<needle>" [expectedCount]
     node tools/assert_code.js --self-test
   Exit 0 on match, 1 on mismatch or on a stripper that broke the parse. */
const fs = require('fs');
const vm = require('vm');

function stripComments(src){
  let out = '';
  let i = 0;
  const n = src.length;
  /* what kind of token could legally precede a regex literal */
  let prevSignificant = '';
  const tplStack = [];   /* depth of ${ } inside template literals */
  while (i < n) {
    const c = src[i], d = src[i+1];
    /* line comment */
    if (c === '/' && d === '/') {
      while (i < n && src[i] !== '\n') i++;
      continue;
    }
    /* block comment - replaced by a space so tokens either side stay apart,
       and newlines preserved so reported line numbers do not drift */
    if (c === '/' && d === '*') {
      i += 2;
      let nl = '';
      while (i < n && !(src[i] === '*' && src[i+1] === '/')) { if (src[i] === '\n') nl += '\n'; i++; }
      i += 2;
      out += ' ' + nl;
      continue;
    }
    /* string literals */
    if (c === "'" || c === '"') {
      const q = c; out += c; i++;
      while (i < n) {
        if (src[i] === '\\') { out += src[i] + (src[i+1]||''); i += 2; continue; }
        out += src[i];
        if (src[i] === q) { i++; break; }
        i++;
      }
      prevSignificant = 'str';
      continue;
    }
    /* template literal, with ${ } nesting */
    if (c === '`') {
      out += c; i++;
      while (i < n) {
        if (src[i] === '\\') { out += src[i] + (src[i+1]||''); i += 2; continue; }
        if (src[i] === '`') { out += src[i]; i++; break; }
        if (src[i] === '$' && src[i+1] === '{') {
          out += '${'; i += 2; tplStack.push(1);
          /* fall back to the main loop so comments inside ${} are stripped too */
          break;
        }
        out += src[i]; i++;
      }
      prevSignificant = 'str';
      continue;
    }
    if (c === '}' && tplStack.length) {
      /* leaving a ${} - resume template scanning */
      tplStack.pop(); out += c; i++;
      while (i < n) {
        if (src[i] === '\\') { out += src[i] + (src[i+1]||''); i += 2; continue; }
        if (src[i] === '`') { out += src[i]; i++; break; }
        if (src[i] === '$' && src[i+1] === '{') { out += '${'; i += 2; tplStack.push(1); break; }
        out += src[i]; i++;
      }
      continue;
    }
    /* regex literal - only where a regex may legally begin */
    if (c === '/' && !/[A-Za-z0-9_$)\]]/.test(prevSignificant)) {
      let j = i + 1, inClass = false, ok = false;
      while (j < n) {
        const e = src[j];
        if (e === '\\') { j += 2; continue; }
        if (e === '\n') break;
        if (e === '[') inClass = true;
        else if (e === ']') inClass = false;
        else if (e === '/' && !inClass) { ok = true; break; }
        j++;
      }
      if (ok) {
        j++;
        while (j < n && /[a-z]/.test(src[j])) j++;
        out += src.slice(i, j); i = j; prevSignificant = ')'; continue;
      }
    }
    if (!/\s/.test(c)) prevSignificant = c;
    out += c; i++;
  }
  return out;
}

/* every inline <script> body, so the check can compile what it produced */
function scriptBodies(html){
  const out = [];
  let i = 0;
  while (true) {
    const a = html.indexOf('<script', i);
    if (a < 0) break;
    const gt = html.indexOf('>', a);
    if (gt < 0) break;
    const b = html.indexOf('</script>', gt);
    if (b < 0) break;
    out.push(html.slice(gt + 1, b));
    i = b + 9;
  }
  return out;
}

function stripVerified(path){
  const raw = fs.readFileSync(path, 'utf8');
  const stripped = stripComments(raw);
  /* THE SELF-CHECK. If removing comments broke the syntax, the scanner is
     wrong and any count taken from it is worthless. */
  const before = scriptBodies(raw), after = scriptBodies(stripped);
  if (before.length !== after.length) {
    throw new Error('stripper changed the script count: ' + before.length + ' -> ' + after.length);
  }
  after.forEach(function(body, k){
    try { new vm.Script(body); }
    catch (e) { throw new Error('stripped script ' + (k+1) + ' no longer parses: ' + e.message); }
  });
  return stripped;
}

module.exports = { stripComments, stripVerified };

if (require.main === module) {
  if (process.argv[2] === '--self-test') {
    const cases = [
      ["var a=1;/* var a=2; */", 'var a=2;', 0, 'block comment removed'],
      ["var s='/* not a comment */';", 'not a comment', 1, 'string survives'],
      ['var s="a//b";', '//b', 1, 'line comment inside a string survives'],
      ['var r=/\\/\\*/;var x=1;', 'x=1', 1, 'regex containing a comment opener'],
      ['var t=`x${/*gone*/1}y`;', 'gone', 0, 'comment inside a template expression'],
      ['a = b / c; // gone', 'gone', 0, 'division is not a regex'],
    ];
    let bad = 0;
    cases.forEach(function(c){
      const got = (stripComments(c[0]).split(c[1]).length - 1);
      const ok = got === c[2];
      if (!ok) bad++;
      console.log((ok ? '  OK   ' : '  FAIL ') + c[3] + '  (expected ' + c[2] + ', got ' + got + ')');
    });
    console.log(bad ? 'SELF-TEST FAILED' : 'SELF-TEST PASS');
    process.exit(bad ? 1 : 0);
  }
  const [path, needle, expected] = process.argv.slice(2);
  if (!path || needle === undefined) {
    console.log('usage: node tools/assert_code.js <file> "<needle>" [expectedCount]');
    process.exit(1);
  }
  let stripped;
  try { stripped = stripVerified(path); }
  catch (e) { console.log('REFUSING TO ANSWER - ' + e.message); process.exit(1); }
  const count = stripped.split(needle).length - 1;
  if (expected === undefined) { console.log('count(code only) = ' + count); process.exit(0); }
  const want = Number(expected);
  const ok = count === want;
  console.log((ok ? 'OK' : 'MISMATCH') + ': found ' + count + ' in code, wanted ' + want);
  process.exit(ok ? 0 : 1);
}
