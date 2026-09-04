/* NO CONTROL BYTES IN A SOURCE FILE. Runs with the parse gate after every patch.
 *
 * WHY THIS IS A GATE AND NOT A RULE. The heredoc-escape trap fired three times in
 * one session against a rule already written down, and the third instance was a
 * comment ABOUT the rule carrying the fault it described. "Be careful with
 * backslashes" is something you have to remember at the moment you are least
 * likely to; a gate does not need remembering.
 *
 * WHAT IT CATCHES, precisely. A backslash escape passed through a heredoc into
 * Python arrives as a real escape: `\1` becomes chr(1), `\n` becomes a newline.
 * Both are invisible in a diff and neither breaks a parse - the sed replacement
 * that lost its capture group still ran, and would have parsed achieved=0 on
 * every batch and abandoned every cell after three "empty" ones. A fix that
 * breaks the thing it fixes, silently, is exactly the failure mode worth a gate.
 *
 * SCOPE: the game file and every tool. Tab, newline and carriage return are
 * legal; everything else below 0x20, plus DEL, is not. Binary and image files
 * are not scanned - the extension list is the filter.
 */
const fs = require('fs'), path = require('path');
const ROOT = path.join(__dirname, '..');
const EXT = ['.js', '.py', '.sh', '.html', '.md', '.json', '.css', '.txt'];
const SKIP = ['node_modules', '.git', 'Art', 'out3d', 'assets', 'optimized'];

/* tab (0x09), newline (0x0A) and carriage return (0x0D) are the only control
   characters a source file has any business holding */
const LEGAL = new Set([0x09, 0x0A, 0x0D]);
const bad = [];
let scanned = 0;

function walk(dir) {
  let entries;
  try { entries = fs.readdirSync(dir, {withFileTypes: true}); } catch (e) { return; }
  for (const e of entries) {
    if (SKIP.includes(e.name)) continue;
    const p = path.join(dir, e.name);
    if (e.isDirectory()) { walk(p); continue; }
    if (!EXT.includes(path.extname(e.name))) continue;
    let s;
    try { s = fs.readFileSync(p, 'utf8'); } catch (e2) { continue; }
    scanned++;
    for (let i = 0; i < s.length; i++) {
      const c = s.charCodeAt(i);
      if ((c < 0x20 && !LEGAL.has(c)) || c === 0x7f) {
        const line = s.slice(0, i).split('\n').length;
        bad.push({file: path.relative(ROOT, p), line,
                  code: '0x' + c.toString(16).padStart(2, '0'),
                  near: JSON.stringify(s.slice(Math.max(0, i - 45), i + 15))});
        break;/* one report per file is enough to send someone to it */
      }
    }
  }
}

walk(ROOT);

if (bad.length) {
  console.log('CONTROL BYTES FOUND — a backslash escape almost certainly became a');
  console.log('real character on the way into the file. These do not break a parse');
  console.log('and do not show in a diff.');
  for (const b of bad) console.log('  %s:%d  %s near %s', b.file, b.line, b.code, b.near);
  console.log('FAILED: %d file(s) of %d scanned', bad.length, scanned);
  process.exit(1);
}
console.log('control-byte gate: %d files scanned, 0 stray control bytes', scanned);
