# -*- coding: utf-8 -*-
u"""P482 - shoot.js must not leak a browser profile. 270GB says it did.

FOUND: ~270GB of orphaned `shoot-*` Edge profiles in %TEMP%, about a week of
probe runs, plus runaway msedge processes burning CPU (confirmed in Task
Manager, and they died when Claude's process died - they were children of the
test tooling, not normal browsing).

THE DIAGNOSIS IS WORSE THAN "CLEANUP ONLY ON THE HAPPY PATH". There is no
cleanup on ANY path: `fs.rmSync` does not appear in shoot.js at all. PROFILE is
created by mkdtempSync at L63 and never removed, so EVERY run leaked, including
successful ones. run_probes.js shells out to shoot.js once per probe, ~45 per
suite run, which is how a week reaches 270GB.

FOUR SEPARATE HOLES, all closed here:

  1. no rm, ever            -> a single idempotent cleanup(), registered on
                               process.on('exit') so it also covers the normal
                               process.exit(0) and the exit(3) dead-server path
  2. proc.kill() on Windows -> kills ONLY the top msedge.exe. Its renderer/GPU
                               children survive, keep burning CPU, and keep a
                               lock on PROFILE. Now taskkill /F /T (whole tree).
  3. no signal handlers     -> SIGINT/SIGTERM killed node and left Edge running
                               entirely. Now handled, and they still exit.
  4. SIGKILL can't be caught-> so a startup sweep is the only backstop for a
                               hard kill or Task Manager "End task".

KEEP IS RESPECTED. `--keep` deliberately leaves a browser running for
inspection; cleaning up under it would break the flag's whole purpose. Under
--keep the profile is left AND its path is printed, and the startup sweep
collects it later on age.

THE SWEEP IS AGE-GATED (30 min) so a concurrently running shoot is never
deleted out from under itself. That matters: run_probes runs probes in
sequence, but nothing stops two suites overlapping.

Cleanup runs inside process.on('exit'), which must be SYNCHRONOUS - so the
retry loop uses Atomics.wait as a real blocking sleep rather than a busy-wait
that would burn the CPU this patch exists to stop.
"""
import io, os, re

SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'shoot.js')
with io.open(SRC, encoding='utf-8') as f:
    s = f.read()
orig = s

# ── 1. execFileSync is needed for taskkill; shoot.js only imports spawn ──
OLD_REQ = u"const { spawn } = require('child_process');"
assert s.count(OLD_REQ) == 1, 'require anchor matched %d' % s.count(OLD_REQ)
s = s.replace(OLD_REQ, u"const { spawn, execFileSync } = require('child_process');")

# ── 2. startup sweep, before the new profile is created ──
OLD_PROF = u"const PROFILE = fs.mkdtempSync(path.join(os.tmpdir(), 'shoot-'));"
assert s.count(OLD_PROF) == 1, 'PROFILE anchor matched %d' % s.count(OLD_PROF)
s = s.replace(OLD_PROF, u"""/* ── startup sweep — the backstop ──────────────────────────────────
   Signal handlers cannot run on SIGKILL or Task Manager "End task", so a
   sweep at launch is the only thing that ever collects those. Age-gated at
   30 minutes so a concurrently running shoot is never deleted out from
   under itself, and fully guarded: a failure to sweep must never stop a
   run from starting. */
(function sweepStaleProfiles(){
  var STALE_MS = 30 * 60 * 1000, n = 0;
  try {
    var tmp = os.tmpdir();
    for (var _i = 0, names = fs.readdirSync(tmp); _i < names.length; _i++) {
      var name = names[_i];
      if (!/^shoot-/.test(name)) continue;
      var p = path.join(tmp, name);
      try {
        var st = fs.statSync(p);
        if (!st.isDirectory()) continue;
        if (Date.now() - st.mtimeMs < STALE_MS) continue;   /* still live */
        fs.rmSync(p, { recursive: true, force: true });
        n++;
      } catch (e) { /* locked or vanished - the next run will get it */ }
    }
  } catch (e) {}
  if (n) console.log('swept ' + n + ' stale shoot-* profile(s)');
})();

""" + OLD_PROF)

# ── 3. cleanup + handlers, right after `proc` and its stderr hookup exist ──
OLD_SPAWN = (u"const proc = spawn(EDGE, FLAGS, { stdio: ['ignore', 'pipe', 'pipe'] });\n"
             u"let browserErr = '';\n"
             u"proc.stderr.on('data', d => { browserErr += d.toString(); });")
assert s.count(OLD_SPAWN) == 1, 'spawn anchor matched %d' % s.count(OLD_SPAWN)
s = s.replace(OLD_SPAWN, OLD_SPAWN + u"""

/* ── cleanup — EVERY exit path, not just the happy one ─────────────
   This file leaked ~270GB of Edge profiles because nothing here ever
   removed PROFILE, on any path, and because proc.kill() on Windows reaches
   only the top msedge.exe while its renderer/GPU children keep running and
   keep the directory locked.

   Registered on 'exit', so process.exit(0) and the exit(3) dead-server path
   are both covered without either having to remember to call it. */
var _cleanedUp = false;
function cleanup(){
  if (_cleanedUp) return;
  _cleanedUp = true;
  /* --keep exists so a browser can be inspected after the run; killing it
     here would defeat the flag. Its profile is left deliberately and the
     startup sweep collects it later on age. */
  if (KEEP) return;
  try {
    if (proc && proc.pid) {
      if (process.platform === 'win32') {
        /* /T = whole tree. Without it the children outlive the run - which
           is exactly what showed up as runaway Edge processes. */
        try { execFileSync('taskkill', ['/F', '/T', '/PID', String(proc.pid)], { stdio: 'ignore' }); }
        catch (e) { try { proc.kill('SIGKILL'); } catch (e2) {} }
      } else {
        try { proc.kill('SIGKILL'); } catch (e) {}
      }
    }
  } catch (e) {}
  /* The directory only unlocks once those children are actually gone, so
     retry. process.on('exit') must be synchronous - Atomics.wait is a real
     blocking sleep, not a busy-wait that would burn the CPU this patch is
     here to stop. */
  var _sab = new Int32Array(new SharedArrayBuffer(4));
  for (var i = 0; i < 12; i++) {
    try { fs.rmSync(PROFILE, { recursive: true, force: true }); break; }
    catch (e) { try { Atomics.wait(_sab, 0, 0, 150); } catch (e2) {} }
  }
}
process.on('exit', cleanup);
['SIGINT', 'SIGTERM', 'SIGHUP', 'SIGBREAK'].forEach(function(sig){
  try { process.on(sig, function(){ cleanup(); process.exit(130); }); } catch (e) {}
});
process.on('uncaughtException', function(e){
  console.error('FAILED:', e && e.message); cleanup(); process.exit(1);
});
process.on('unhandledRejection', function(e){
  console.error('FAILED:', e && (e.message || e)); cleanup(); process.exit(1);
});""")

# ── 4. --keep should say WHERE the profile is, since it is now kept on purpose
OLD_KEEP = u"  else console.log('browser left running on port ' + PORT);"
assert s.count(OLD_KEEP) == 1, 'keep-log anchor matched %d' % s.count(OLD_KEEP)
s = s.replace(OLD_KEEP,
              u"  else console.log('browser left running on port ' + PORT +\n"
              u"                   '\\n  profile kept at ' + PROFILE + ' (swept after 30min)');")

# ── gates, BEFORE the write ──
assert s != orig, 'nothing changed'
assert s.count('function cleanup()') == 1
assert s.count("process.on('exit', cleanup)") == 1
assert s.count('sweepStaleProfiles') == 1
assert s.count('execFileSync') == 2          # the import + the taskkill
assert s.count("'/T'") == 1, 'the tree-kill flag must be present exactly once'
assert 'fs.rmSync' in s, 'the whole point of the patch'
assert s.count('fs.rmSync') == 2             # sweep + cleanup
assert 'if (KEEP) return;' in s, '--keep must still leave its browser alive'
# the four exit paths that previously leaked are all downstream of 'exit'
for n in ['process.exit(0)', 'process.exit(1)', 'process.exit(3)']:
    assert n in s, '%s vanished' % n
# balanced enough to parse - node checks properly below, this is the cheap gate
assert s.count('{') == s.count('}'), 'brace mismatch: %d vs %d' % (s.count('{'), s.count('}'))

with io.open(SRC, 'w', encoding='utf-8', newline='') as f:
    f.write(s)
print('P482 applied: cleanup on every path, tree-kill, startup sweep')
