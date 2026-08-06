# -*- coding: utf-8 -*-
u"""P483 - the sweep must not wait 30 minutes to collect an orphan.

MEASURED AFTER P482, and it is why this patch exists rather than a claim that
P482 finished the job:

  happy path      -> 0 dirs left   OK
  dead server     -> 0 dirs left   OK  (the old exit(3) leak)
  SIGTERM mid-run -> 1 dir left, 183.5 MB, and ZERO orphan msedge processes

The browser tree died but nothing removed the directory, so cleanup() never
ran. That is expected on Windows: a terminate is not a catchable POSIX signal,
so process.on('SIGTERM') is BEST EFFORT here and cannot be the guarantee.
The startup sweep is the only real bound - which makes its rule load-bearing,
and a pure 30-minute age gate leaks up to 30 minutes of runs at ~183MB each.

THE FIX: make a profile say who owns it.

  - on launch, write the owning PID into <PROFILE>/.shoot-owner
  - the sweep reads it. Owner dead -> orphan, remove NOW regardless of age.
    Owner alive -> in use, never touch. No marker -> fall back to the age gate.

process.kill(pid, 0) throws ESRCH when the process is gone; it sends nothing.

PID REUSE is the only false reading, and it fails SAFE: a recycled PID makes a
dead owner look alive, so the dir is skipped and the 30-minute age gate
collects it on a later run. The sweep never deletes a live profile.
"""
import io, os

SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'shoot.js')
with io.open(SRC, encoding='utf-8') as f:
    s = f.read()
orig = s

# ── 1. the sweep learns to ask who owns a profile ──
OLD = u"""      try {
        var st = fs.statSync(p);
        if (!st.isDirectory()) continue;
        if (Date.now() - st.mtimeMs < STALE_MS) continue;   /* still live */
        fs.rmSync(p, { recursive: true, force: true });
        n++;
      } catch (e) { /* locked or vanished - the next run will get it */ }"""
assert s.count(OLD) == 1, 'sweep body matched %d' % s.count(OLD)
s = s.replace(OLD, u"""      try {
        var st = fs.statSync(p);
        if (!st.isDirectory()) continue;

        /* WHO OWNS THIS? A dir whose owner process is gone is an orphan and
           can go immediately - waiting on an age gate is what let a week of
           runs pile up. Measured: a terminate on Windows is not catchable,
           so cleanup() does not always get to run and this is the real bound. */
        var owner = null;
        try { owner = parseInt(fs.readFileSync(path.join(p, '.shoot-owner'), 'utf8').trim(), 10); }
        catch (e) { owner = null; }

        if (owner) {
          var alive = true;
          /* sends no signal - throws ESRCH if the process is gone. PID reuse
             reads as "alive", which fails SAFE: the age gate gets it later. */
          try { process.kill(owner, 0); } catch (e) { alive = false; }
          if (alive) continue;                                 /* in use */
        } else if (Date.now() - st.mtimeMs < STALE_MS) {
          continue;                        /* no marker - fall back to age */
        }

        fs.rmSync(p, { recursive: true, force: true });
        n++;
      } catch (e) { /* locked or vanished - the next run will get it */ }""")

# ── 2. stamp the owner into the new profile, before the browser starts ──
OLD_P = u"const PROFILE = fs.mkdtempSync(path.join(os.tmpdir(), 'shoot-'));"
assert s.count(OLD_P) == 1, 'PROFILE anchor matched %d' % s.count(OLD_P)
s = s.replace(OLD_P, OLD_P + u"""
/* claim it, so a later run can tell "still running" from "abandoned" without
   guessing from a timestamp */
try { fs.writeFileSync(path.join(PROFILE, '.shoot-owner'), String(process.pid)); } catch (e) {}""")

# ── gates, BEFORE the write ──
assert s != orig, 'nothing changed'
assert s.count(".shoot-owner") == 2, 'marker written once and read once'
assert s.count("process.kill(owner, 0)") == 1
assert s.count("fs.rmSync") == 2, 'still exactly the sweep and the cleanup'
assert "if (KEEP) return;" in s, 'P482 keep-guard must survive'
assert s.count("function cleanup()") == 1
assert s.count("process.on('exit', cleanup)") == 1
assert s.count("'/T'") == 1, 'tree-kill must survive'
assert s.count('{') == s.count('}'), 'brace mismatch %d vs %d' % (s.count('{'), s.count('}'))

with io.open(SRC, 'w', encoding='utf-8', newline='') as f:
    f.write(s)
print('P483 applied: profiles are owned; dead owner = collected on next run')
