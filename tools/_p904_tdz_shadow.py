# -*- coding: utf-8 -*-
u"""P904: a probe shadowed the page's `G`, and the harness reported it as a
game failure for four runs.

WHAT HAPPENED. apv_band_extent declared `const G = D3X.GLOW` near its foot. The
harness is eval'd into that same function scope, so every `G` inside it - and
inside the probe above the declaration - was in the const's TEMPORAL DEAD ZONE.
`typeof G` does not return 'undefined' for a shadowed let/const; it THROWS. So
FXH.match's idle predicate threw on every attempt, `until` caught it silently,
and the report said "match never became idle".

FOUR RUNS AND THREE WRONG THEORIES came out of that one sentence: an async boot
race (D3X.ready - the layer was up), showScreen('gauntlet') on a first launch
(it is fine), and an unseen boss's splash (the ladder seeds _bossSeen, but that
was not it either). Each was plausible, each was tested, each was wrong, and
none of them could have been right - the game was never involved.

THE FIX IS IN THE INSTRUMENT, NOT THE THEORY. `until` now counts throws and
keeps the last message: a predicate that throws on ALL of its attempts is a
broken predicate, and saying so is the difference between a wrong answer and no
answer. Still caught - a predicate that throws once while the page settles is
normal - but no longer silent.

AND THE THREE SPECULATIVE CHANGES COME BACK OUT. Each was made on a theory that
turned out to be wrong, and leaving them would be three unexplained differences
in a shared tool, each looking deliberate to the next reader. The only edits
that survive are the two the evidence supports: until reporting throws, and the
failure path reading G defensively, because a reporter that throws reports
nothing - which is exactly how a `typeof` guard failed here.
"""
import io, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
edits = []


def sub(path, old, new, label):
    s = io.open(path, encoding='utf-8', newline='').read()
    if s.count(old) != 1:
        sys.exit('ANCHOR x%d for %s (nothing written)' % (s.count(old), label))
    io.open(path, 'w', encoding='utf-8', newline='').write(s.replace(old, new))
    edits.append(label)


FXH = os.path.join(ROOT, 'tools', '_fxh.js')
PROBE = os.path.join(ROOT, 'tools', 'apv_band_extent.js')

# ── 1. until reports a predicate that always throws ─────────────────
sub(FXH,
    u"""  async function until(fn, ms){
    const t0 = Date.now();
    while (Date.now() - t0 < ms){
      try { if (fn()) return Date.now() - t0; } catch(e){}
      await sleep(120);
    }
    return null;
  }""",
    u"""  /* A PREDICATE THAT ALWAYS THROWS IS NOT A PREDICATE THAT IS NEVER TRUE, and
     conflating them cost four runs and three wrong theories. A probe declared
     `const G = D3X.GLOW` near its foot; this file is eval'd into that same
     function scope, so every `G` in here - including `typeof G` - was in the
     const's temporal dead zone and threw ReferenceError. The catch swallowed
     it, the poll timed out, and the report said "match never became idle",
     which sent the search to boot races, showScreen and boss splashes in turn.
     Throws are counted now and the last message kept on until.lastError. Still
     caught, because a predicate that throws once while the page settles is
     normal - but no longer silent when it throws every single time. */
  async function until(fn, ms){
    const t0 = Date.now();
    let threw = 0, tries = 0, last = null;
    while (Date.now() - t0 < ms){
      tries++;
      try { if (fn()) { until.lastError = null; return Date.now() - t0; } }
      catch(e){ threw++; last = (e && e.message) || String(e); }
      await sleep(120);
    }
    until.lastError = (tries && threw === tries)
      ? 'the predicate threw on all ' + tries + ' attempts: ' + last
      : (threw ? threw + '/' + tries + ' attempts threw: ' + last : null);
    return null;
  }""",
    '1 until reports throws')

# ── 2. the three speculative changes come back out ──────────────────
sub(FXH,
    u"""    /* WAIT FOR THE 3D LAYER, not just for the function to exist. D3X boots
       asynchronously - three.js, the loader, the model, cannon - and launching
       into that window intermittently produced a match that never reached
       idle: three runs lost to it in one session, while a bisect immediately
       afterwards reached idle in 500ms twice in a row from the same build.
       `launchBossMatch` being defined says the script parsed, which is a
       different question from the layer being able to deal a die. Polls the
       state, like everything else here, and reports the wait rather than
       hiding it - a boot that took most of the budget is worth seeing. */
    const bootMs = await until(() => typeof D3X === 'undefined' ||
                                     D3X.ready || D3X.fail, 30000);
    _getS(); window._fkDiscardOk = true;""",
    u"""    _getS(); window._fkDiscardOk = true;""",
    '2a the D3X.ready wait, reverted')

sub(FXH,
    u"""    S.run.tier = tier == null ? 1 : tier; S.run.gold = 500;
    /* SEED THE SEEN-BOSSES SET, which is what ladder_band.js does and this
       helper did not. A boss the run has not met gets an introduction - the
       splash the match screen carries as .has-splash - and a match sitting
       behind one never reaches `idle`, so this hung intermittently depending
       on which boss the tier happened to draw. That is why it passed all
       morning and then failed four runs in a row. */
    S.run._bossSeen = S.run._bossSeen || {drunkard:1,peasant:1,commoner:1,
      merchant:1,soldier:1,knight:1,noble:1,bishop:1};""",
    u"""    S.run.tier = tier == null ? 1 : tier; S.run.gold = 500;""",
    '2b the _bossSeen seeding, reverted')

sub(FXH,
    u"""    /* NO showScreen('gauntlet') HERE. Bisected: _getS() + launchBossMatch()
       reaches idle in 500ms every time, and so does the same pair AFTER a match
       already exists - but showScreen('gauntlet') before the FIRST launch of a
       fresh page leaves the match never reaching idle. Three runs were lost to
       it before the bisect isolated it, and the earlier "wait for D3X.ready"
       theory was wrong: the layer was up. launchBossMatch shows its own screen
       (measured: .screen.active is screen-match afterwards), so the call was
       doing nothing this helper needed. ladder_band.js never made it and never
       had the problem. */
    launchBossMatch();""",
    u"""    try { showScreen('gauntlet'); } catch(e){}
    launchBossMatch();""",
    '2c showScreen, restored')

# ── 3. the failure report survives, and cannot itself throw ─────────
sub(FXH,
    u"""      const ms = document.getElementById('screen-match');
      return {ok:false, why:'match never became idle', bootMs:bootMs,
              d3xReady:!!(window.D3X && D3X.ready),
              phase:(typeof G !== 'undefined' && G) ? G.phase : null,""",
    u"""      const ms = document.getElementById('screen-match');
      /* READ G DEFENSIVELY. `typeof G` is NOT safe when a caller has shadowed
         G with a let or const in the enclosing scope - it throws rather than
         answering, which is the trap that hid this for four runs. A reporter
         that throws reports nothing. */
      let phase = null, gWhy = null;
      try { phase = (typeof G !== 'undefined' && G) ? G.phase : null; }
      catch (e) { gWhy = 'G is shadowed by the caller: ' + ((e && e.message) || e); }
      return {ok:false, why:'match never became idle',
              predicate:until.lastError || null, gRead:gWhy,
              d3xReady:!!(window.D3X && D3X.ready), phase:phase,""",
    '3 the failure report cannot throw')

# ── 4. the probe stops shadowing ────────────────────────────────────
sub(PROBE,
    u"""const G = D3X.GLOW;
out.glowReach = {soft: G.soft, sy: G.sy, sx: G.sx, line: G.line, clear: G.clear,
                 estimateY: +(G.soft * G.sy + G.line / 2 + G.clear).toFixed(1),
                 estimateX: +(G.soft * G.sx + G.line / 2 + G.clear).toFixed(1)};""",
    u"""/* NOT `const G`. The page's G is a let, and a const of the same name anywhere
   in this probe's scope puts every G reference in the eval'd harness into its
   temporal dead zone - including `typeof G`, which throws instead of answering.
   That is what made FXH.match time out and report "match never became idle"
   through four runs. Never name a probe local after a page global. */
const GL = D3X.GLOW;
out.glowReach = {soft: GL.soft, sy: GL.sy, sx: GL.sx, line: GL.line,
                 clear: GL.clear,
                 estimateY: +(GL.soft * GL.sy + GL.line / 2 + GL.clear).toFixed(1),
                 estimateX: +(GL.soft * GL.sx + GL.line / 2 + GL.clear).toFixed(1)};""",
    '4 the probe stops shadowing G')

# ── post-asserts ────────────────────────────────────────────────────
fx = io.open(FXH, encoding='utf-8', newline='').read()
pr = io.open(PROBE, encoding='utf-8', newline='').read()
if 'until.lastError' not in fx or fx.count('until.lastError') < 3:
    sys.exit('until does not report throws (already written)')
if 'bootMs' in fx:
    sys.exit('a reverted change survived (already written)')
if '_bossSeen' in fx:
    sys.exit('the _bossSeen seeding survived (already written)')
if "showScreen('gauntlet')" not in fx:
    sys.exit('showScreen was not restored (already written)')
# and no probe in the tools tree may shadow a page global this way
import re
for name in os.listdir(os.path.join(ROOT, 'tools')):
    if not name.startswith('apv_') or not name.endswith('.js'):
        continue
    body = io.open(os.path.join(ROOT, 'tools', name), encoding='utf-8',
                   newline='').read()
    if re.search(r'^\s*(const|let)\s+G\s*=', body, re.M):
        sys.exit('%s still shadows the page global G (already written)' % name)

print('done: %d edits (%s)' % (len(edits), ', '.join(edits)))
