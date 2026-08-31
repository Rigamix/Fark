# -*- coding: utf-8 -*-
u"""P893b: setting priority on the parent does NOT cover the tree, measured.

P893 set the browser to BELOW_NORMAL on the assumption that Chromium's children
inherit the parent's priority class at creation. Sampled against our own
profile marker while a run was live, eleven processes:

    BelowNormal 7 | AboveNormal 1 | Normal 2 | Idle 1

So about two thirds inherited and the rest did not - Chromium sets priorities on
some of its own children deliberately, the GPU process highest. The parent-only
call was a third of a fix, and the comment claiming it covered the tree "in
practice" was wrong on a measurement I had already taken.

A second pass runs two seconds after spawn and sets every process carrying THIS
run's profile directory name to BelowNormal. The marker is the mkdtemp basename
rather than the full path, which is unique per run and needs no path escaping.
Asynchronous and unref'd, so it never delays or holds open a run, and wrapped
so a machine without PowerShell loses the priority and nothing else.

Two seconds because the children that miss inheritance are spawned during
startup; a pass at spawn time would find only the parent. Chromium re-tunes
renderer priorities dynamically as pages load, so this is a floor for the
steady state rather than a guarantee for every instant - which is honest about
what one pass can do, and enough for the thing it is for: a background batch
that has to leave the machine usable.
"""
import io, os, sys, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'tools', 'shoot.js')
s = io.open(P, encoding='utf-8', newline='').read()


OLD = u"""/* BELOW NORMAL, so a background batch yields to whoever is actually using the
   machine. Chromium's children inherit the parent's priority class at
   creation and are created after spawn() returns, so setting it here covers
   the tree in practice. Best effort: a platform that refuses must cost the
   run nothing. */
try { require('os').setPriority(proc.pid,
        require('os').constants.priority.PRIORITY_BELOW_NORMAL); }
catch (e) { /* not supported here - the run is still correct, just louder */ }"""

NEW = u"""/* BELOW NORMAL, so a background batch yields to whoever is actually using the
   machine. Best effort throughout: a platform that refuses must cost the run
   nothing but noise. */
try { os.setPriority(proc.pid, os.constants.priority.PRIORITY_BELOW_NORMAL); }
catch (e) {}
/* THE PARENT IS NOT THE TREE, measured. Sampling our own processes while a run
   was live gave BelowNormal 7, AboveNormal 1, Normal 2, Idle 1 - so about two
   thirds inherit and the rest do not, because Chromium sets priorities on some
   of its own children deliberately (the GPU process highest). An earlier
   version of this comment claimed the parent call covered the tree; it covered
   a third of it.
   So: a second pass, two seconds in - the children that miss inheritance are
   spawned during startup, and a pass at spawn time would find only the parent.
   Matched on THIS run's profile basename, which is unique per run and needs no
   path escaping. Async and unref'd so it never delays or holds open a run.
   Chromium re-tunes renderer priorities as pages load, so this is a floor for
   the steady state, not a guarantee for every instant. */
setTimeout(function () {
  try {
    var mark = path.basename(PROFILE);
    var ps = 'Get-CimInstance Win32_Process -Filter "Name=\\'msedge.exe\\' or ' +
             'Name=\\'chrome.exe\\'" | Where-Object { $_.CommandLine -like ' +
             "'*" + mark + "*' } | ForEach-Object { try { " +
             '(Get-Process -Id $_.ProcessId).PriorityClass = ' +
             "'BelowNormal' } catch {} }";
    require('child_process').execFile('powershell.exe',
      ['-NoProfile', '-NonInteractive', '-EncodedCommand',
       Buffer.from(ps, 'utf16le').toString('base64')],
      function () {});
  } catch (e) {}
}, 2000).unref();"""

pat = re.escape(OLD).replace('\\\n', '\n').replace('\n', '\\r?\n')
ms = list(re.finditer(pat, s))
if len(ms) != 1:
    sys.exit('ANCHOR x%d (nothing written)' % len(ms))
m = ms[0]
rep = NEW.replace('\n', '\r\n') if '\r\n' in m.group(0) else NEW
s = s[:m.start()] + rep + s[m.end():]

code = re.sub(r'/\*.*?\*/', '', s, flags=re.S)
if 'PriorityClass' not in code:
    sys.exit('the tree pass is missing (nothing written)')
if '.unref()' not in code:
    sys.exit('the timer is not unrefd - it could hold a run open (nothing written)')
if code.count('setPriority(proc.pid') != 1:
    sys.exit('the parent call is not present exactly once (nothing written)')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: the priority pass covers the tree')
