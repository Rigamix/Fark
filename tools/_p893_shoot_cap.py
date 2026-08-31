# -*- coding: utf-8 -*-
u"""P893: shoot.js gets a concurrency cap and runs below normal priority, so a
long batch in the background leaves the machine usable.

WHAT HAPPENED. A ladder batch fanned out to 61 live browser processes and had
to be killed because the machine became unusable. Nothing in shoot.js limited
how many runs could be in flight at once - the orphan sweep cleans up AFTER a
run dies, which is a different problem - and every browser ran at normal
priority, competing with foreground work on equal terms.

THE CAP COUNTS RUNS, NOT PROCESSES, and it does it with fs alone. Every run
already writes its own pid into `.shoot-owner` inside its profile directory,
which is how the orphan sweep tells "still running" from "abandoned". Counting
profile directories whose owner pid is still alive therefore counts CONCURRENT
RUNS exactly, with no PowerShell round-trip - which matters because the gate
polls, and the sweep's enumeration costs about a second per call.

It sits AFTER both sweeps and BEFORE this run creates its own profile, so a run
never counts itself and abandoned profiles are already gone by the time it
looks. Default 2. `--max N` or FARK_SHOOT_MAX override it, and `--max 0` turns
the gate off for someone who knows what they are doing and is not using the
machine.

A run that waits says so once, and gives up after fifteen minutes with a
distinct exit code rather than blocking a batch for ever - a silent wait is
indistinguishable from a hang, and the caller needs to be able to tell.

BELOW-NORMAL PRIORITY on the browser. Chromium's children inherit the parent's
priority class at creation, and they are created after the spawn returns, so
setting it on the parent immediately covers the tree in practice. It is a
best-effort call inside a try: a platform that refuses it should cost a run
nothing.

--renderer-process-limit caps the per-browser fan as well, because the two
multiply: the cap bounds how many browsers, this bounds how many processes each
one is. Neither alone would have prevented 61.
"""
import io, os, sys, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'tools', 'shoot.js')
s = io.open(P, encoding='utf-8', newline='').read()
edits = []


def sub(old, new, label):
    global s
    pat = re.escape(old).replace('\\\n', '\n').replace('\n', '\\r?\n')
    ms = list(re.finditer(pat, s))
    if len(ms) != 1:
        sys.exit('ANCHOR x%d for %s (nothing written)' % (len(ms), label))
    m = ms[0]
    rep = new.replace('\n', '\r\n') if '\r\n' in m.group(0) else new
    s = s[:m.start()] + rep + s[m.end():]
    edits.append(label)


# ── 1. the gate, between the sweeps and this run's own profile ──────
sub(u"""/* A FIXED root, not the per-session scratchpad: the sweep above has to be
   able to recognise last week's orphans, and a path that changes every
   session cannot be a marker. */""",
    u"""/* ── the concurrency cap ───────────────────────────────────────────
   A ladder batch once fanned out to 61 live browsers and had to be killed
   because the machine became unusable. The sweeps above clean up after a run
   DIES; nothing limited how many could be alive at once.

   IT COUNTS RUNS, NOT PROCESSES, using fs alone. Every run writes its pid to
   .shoot-owner in its profile directory - that is how the sweep tells "still
   running" from "abandoned" - so profile directories with a live owner ARE
   the concurrent runs. No PowerShell: the gate polls, and the sweep's
   enumeration costs about a second a call.

   It sits after both sweeps and before this run makes its own profile, so a
   run never counts itself and abandoned profiles are already gone.

   --max N or FARK_SHOOT_MAX override the default; --max 0 disables the gate
   for someone who is not using the machine. A waiting run says so once and
   gives up after fifteen minutes with its own exit code, because a silent
   wait is indistinguishable from a hang. */
const SHOOT_MAX = (function(){
  var i = process.argv.indexOf('--max');
  var v = (i >= 0 && process.argv[i + 1] !== undefined)
    ? parseInt(process.argv[i + 1], 10)
    : parseInt(process.env.FARK_SHOOT_MAX || '', 10);
  return (Number.isFinite(v) && v >= 0) ? v : 2;
})();
function liveShootRuns(){
  var dirs;
  try { dirs = fs.readdirSync(PROFILE_ROOT); } catch (e) { return 0; }
  var n = 0;
  for (var i = 0; i < dirs.length; i++) {
    if (dirs[i].indexOf('shoot-') !== 0) continue;
    var owner = null;
    try {
      owner = parseInt(fs.readFileSync(
        path.join(PROFILE_ROOT, dirs[i], '.shoot-owner'), 'utf8').trim(), 10);
    } catch (e) { continue; }        /* no claim - the sweep's problem, not ours */
    if (!owner) continue;
    /* sends no signal, throws if gone. PID reuse reads as "alive", which fails
       SAFE here: the worst case is waiting for a slot we could have taken. */
    try { process.kill(owner, 0); n++; } catch (e) {}
  }
  return n;
}
if (SHOOT_MAX > 0) {
  var _waited = 0, _WAIT_CAP = 15 * 60 * 1000, _said = false;
  while (liveShootRuns() >= SHOOT_MAX) {
    if (!_said) {
      console.log('shoot: ' + liveShootRuns() + ' run(s) already active, cap ' +
                  SHOOT_MAX + ' - waiting for a slot (--max 0 disables)');
      _said = true;
    }
    if (_waited >= _WAIT_CAP) {
      console.log('shoot: no slot after ' + Math.round(_WAIT_CAP / 60000) +
                  'm - giving up rather than hanging the batch');
      process.exit(3);
    }
    /* a real synchronous sleep, no dependency and no busy-spin */
    Atomics.wait(new Int32Array(new SharedArrayBuffer(4)), 0, 0, 1500);
    _waited += 1500;
  }
}

/* A FIXED root, not the per-session scratchpad: the sweep above has to be
   able to recognise last week's orphans, and a path that changes every
   session cannot be a marker. */""",
    '1 the concurrency gate')

# ── 2. cap the per-browser process fan ──────────────────────────────
sub(u"""  '--use-gl=angle', '--use-angle=swiftshader',""",
    u"""  '--use-gl=angle', '--use-angle=swiftshader',
  /* the two multiply: the cap above bounds how many BROWSERS, this bounds how
     many processes each one is. Neither alone would have prevented 61. */
  '--renderer-process-limit=2',""",
    '2 the renderer fan')

# ── 3. below-normal priority ────────────────────────────────────────
sub(u"""const proc = spawn(EDGE, FLAGS, { stdio: ['ignore', 'pipe', 'pipe'] });""",
    u"""const proc = spawn(EDGE, FLAGS, { stdio: ['ignore', 'pipe', 'pipe'] });
/* BELOW NORMAL, so a background batch yields to whoever is actually using the
   machine. Chromium's children inherit the parent's priority class at
   creation and are created after spawn() returns, so setting it here covers
   the tree in practice. Best effort: a platform that refuses must cost the
   run nothing. */
try { require('os').setPriority(proc.pid,
        require('os').constants.priority.PRIORITY_BELOW_NORMAL); }
catch (e) { /* not supported here - the run is still correct, just louder */ }""",
    '3 below-normal priority')

# ── post-asserts, comments stripped ─────────────────────────────────
code = re.sub(r'/\*.*?\*/', '', s, flags=re.S)
if 'liveShootRuns' not in code or code.count('function liveShootRuns') != 1:
    sys.exit('the run counter is not defined exactly once (nothing written)')
if 'PRIORITY_BELOW_NORMAL' not in code:
    sys.exit('priority is not set (nothing written)')
if '--renderer-process-limit=2' not in code:
    sys.exit('the renderer cap is missing (nothing written)')
# the gate must come BEFORE this run creates its own profile, or it counts itself
_gate = code.index('while (liveShootRuns()')
_mine = code.index('mkdtempSync')
if _gate > _mine:
    sys.exit('the gate runs after the profile is made - it would count itself '
             '(nothing written)')
# and AFTER the sweeps, or it counts profiles that are about to be cleaned
_sweep = code.rindex('sweepStaleProfiles')
if _gate < _sweep:
    sys.exit('the gate runs before the sweeps (nothing written)')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d edits (%s)' % (len(edits), ', '.join(edits)))
