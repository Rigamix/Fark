# -*- coding: utf-8 -*-
u"""P891: I gave the withdrawn verdict the wrong parent, in three documents.
The withdrawal stands; the reason I put my name to does not.

THE ARCHAEOLOGY, and it is decisive rather than statistical:
  3d3e892 (P11)  11:27:11  _runEconomySim and PWIN/BWIN born, today's literals
  9cf44e9        12:53:53  "TRAP at 4% run wins" written into the brief
  b4f6c24 (P13)  12:58:23  the free silver bust-save added to _runBalanceSim
  c2134d6 (P888) 2026-08-30 the save removed
`git log -S` on each constant literal returns exactly one commit, 3d3e892, so
they have never been edited; and P11's file contains zero occurrences of the
contaminating line. THE 4% PREDATES THE DEFECT BY FOUR AND A HALF MINUTES. My
account - "the number came from a sim whose match layer hard-coded the very
immunity under test" - is chronologically impossible, and I wrote it into the
master brief, docs/OPEN.md and the archive index.

THE WITHDRAWAL IS STILL RIGHT, on reasons that survive:
  - At P11 the LIVE GAME carried a real silver bust-shield, with its own VFX
    and sound. That is a shipped mechanic since retired ("RELIABILITY, NOT
    SAFETY"), not a sim defect - so the verdict measured a game that no longer
    exists. Different story, same conclusion.
  - _runBalanceSim is MATCH-level and nothing in it can fail a run, so it could
    never have produced a run-win number. This is the one that makes the
    verdict unrepairable rather than merely stale.
  - Two of the three named components are not modellable: famDef('ward') is
    false and insurance is retired.

AND THE 4% HAS A REPRODUCIBLE PARENT THAT IS NOT SILVER. _runEconomySim with
the SHIPPED constants returns runsWon = 4% in 5 of 5 replicates of 10,000 runs
when every band is pinned to band-1 rates - a run that never gets past a single
family die. That is the only ~4% the stored model can produce; band-2 pinned
gives 20.4%, unpinned 23%. It matches the second half of the very sentence the
4% sits in - "the real risk is defense-only builds lacking any win condition" -
and NOT the silver label, because silver is not in gearLevel's `strong` set, so
a full-silver stack sits at band 2 and reads 20.4%. The likeliest history is
that the number was produced for the no-win-condition case and the silver label
was attached to it.

THE CONSTANTS ARE STALE, NOT CONTAMINATED, and that is a live finding of its
own. Occupancy-weighted against the fixed sim, only one is materially wrong:
PWIN[2] 0.62 -> 0.443, overstated by ~18pp. PWIN[1] 0.55 -> 0.527, PWIN[3]
0.68 -> 0.683, BWIN 0.45/0.55/0.62 -> 0.482/0.548/0.656. Band 0 is dead code:
`fam` always starts with one family die so gearLevel can never return 0, proven
twice over - a 40,000-run occupancy census returns zero for band 0, and moving
PWIN[0] between 0.0 and 1.0 leaves runsWon unchanged.

Downstream, runsWon goes 23% -> 4.6-10%, against the brief's own recorded
target of 25-35% full-run wins. That is the one recorded conclusion this
changes, and it is a bigger deal than the silver line was. The silver defect
itself changes nothing here: 4.6% against 5.0%.
"""
import io, os, sys, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
edits = []


def patch(rel, pairs):
    p = os.path.join(ROOT, rel)
    s = io.open(p, encoding='utf-8', newline='').read()
    for old, new, label in pairs:
        pat = re.escape(old).replace('\\\n', '\n').replace('\n', '\\r?\n')
        ms = list(re.finditer(pat, s))
        if len(ms) != 1:
            sys.exit('ANCHOR x%d for %s in %s (nothing written)'
                     % (len(ms), label, rel))
        m = ms[0]
        rep = new.replace('\n', '\r\n') if '\r\n' in m.group(0) else new
        s = s[:m.start()] + rep + s[m.end():]
        edits.append(rel + ': ' + label)
    io.open(p, 'w', encoding='utf-8', newline='').write(s)


patch('docs/briefs/FARK_MASTER_BRIEF.md', [
    (u"""  **VERDICT WITHDRAWN, not re-run.** The "TRAP at 4% run wins" number came
  from a sim whose match layer hard-coded the very immunity under test - one
  free bust-save a turn for owning a silver die, plus one per ward charge
  (fixed P888). It did not measure the stack, it granted it. It also cannot
  be repaired by re-running: `_runBalanceSim` is MATCH-level and nothing in
  it can fail a run, and two of the three named components no longer exist -
  Insurance is retired and Ward halves rather than rescues.""",
     u"""  **VERDICT WITHDRAWN, not re-run.** Two reasons make it unrepairable rather
  than merely stale. `_runBalanceSim` is **MATCH-level** - nothing in it can
  fail a run - so it could never have produced a run-win number at all; and
  two of the three named components are not modellable, since `famDef('ward')`
  is false and Insurance is retired. On top of that the verdict was measured
  against a game that no longer exists: at the time the LIVE game carried a
  real silver bust-shield, with its own VFX and sound, which has since been
  retired (*"RELIABILITY, NOT SAFETY"*).
  **A correction to an earlier version of this note.** It said the 4% "came
  from a sim whose match layer hard-coded the very immunity under test (fixed
  P888)". That is **chronologically impossible** and was my error: the
  constants and the 4% were committed at 11:27 and 12:53, and the offending
  line entered `_runBalanceSim` at 12:58 - four and a half minutes *after* the
  claim. The sim defect is real and is fixed, but it is not this number's
  parent.
  **The 4% does have a reproducible parent, and it is not silver.**
  `_runEconomySim` with the shipped constants returns `runsWon` = 4% in 5 of 5
  replicates of 10,000 runs **when every band is pinned to band-1 rates** - a
  run that never gets past a single family die. Band-2 pinned gives 20.4%,
  unpinned 23%. That matches the second half of this very sentence - *"the
  real risk is defense-only builds lacking any win condition"* - and not the
  silver label, since silver is not in `gearLevel`'s `strong` set and a
  full-silver stack sits at band 2. The number was most likely produced for
  the no-win-condition case and the silver label attached to it.""",
     '1 the wrong parent, corrected'),
    (u"""  **RUN-level impact is still unmeasured.** `tools/sim_power_e.js` is the
  only harness that can answer it and has never been pointed here.""",
     u"""  **RUN-level impact is still unmeasured for silver specifically.**
  `tools/sim_power_e.js` is the only harness that can answer it and has never
  been pointed here.
  **Separately, and bigger than the silver line was:** `_runEconomySim`'s
  `PWIN`/`BWIN` constants are **stale, not contaminated** - `git log -S` dates
  them to their birth commit, unedited since, and they match readings recorded
  in `PROTO_NOTES` the same hour, so the header sentence is literally true.
  But 1,140 commits of tuning later, occupancy-weighted against the fixed sim,
  **`PWIN[2]` is overstated by ~18pp** (0.62 against a measured 0.443); the
  other three live constants are within a few points. Feeding the corrected
  values through takes `runsWon` from **23% to 4.6-10%**, against the
  **25-35%** run-win target recorded in this section. Gold does not move
  (survivor bias), and the pity metric reads 0% under every input including
  all-zero win rates, so it is insensitive to these constants. **Band 0 is
  dead code** - `fam` always starts with one family die, so `gearLevel` can
  never return 0 and `PWIN[0]`/`BWIN[0]` are never read.""",
     '2 the stale-constant finding'),
])

patch('docs/OPEN.md', [
    (u"""1. **`_runEconomySim`'s `PWIN`/`BWIN` constants.** It is run-level but rolls no
   dice \u2014 it takes win rates as hard-coded numbers copied from the balance
   sim's gear-band rows, which were silver-bearing. Every `runsWon` and pity
   number it has produced rests on them, and **this is the most likely ancestor
   of the "4% run wins" figure.**""",
     u"""1. ~~**`PWIN`/`BWIN` are contaminated.**~~ **WRONG, AND MINE.** Measured:
   the constants are **stale, not contaminated**. `git log -S` on each literal
   returns exactly one commit \u2014 their birth \u2014 and that file contains zero
   occurrences of the contaminating line, which arrived **91 minutes later**.
   They match readings recorded in `PROTO_NOTES` the same hour, so the header
   sentence is literally true. **The "4% run wins" figure was committed four
   and a half minutes BEFORE the defect existed**, so the defect cannot be its
   parent and my "most likely ancestor" was chronologically impossible.
   What IS true, and matters more: **1,140 commits later they are badly out of
   date.** Occupancy-weighted against the fixed sim, `PWIN[2]` is **overstated
   by ~18pp** (0.62 vs a measured 0.443); the other three live constants are
   within a few points. Corrected, `runsWon` goes **23% \u2192 4.6\u201310%** against
   the brief's recorded **25\u201335%** target \u2014 *that* is the conclusion this
   moves. The silver defect changes nothing here (4.6% vs 5.0%). Gold does not
   move; **the pity metric is insensitive to these constants entirely** \u2014 it
   reads 0% under every input including all-zero win rates, so my claim that
   pity numbers rest on them was also wrong. **Band 0 is dead code:**
   `gearLevel` can never return 0, proven by a 40,000-run occupancy census and
   by moving `PWIN[0]` between 0 and 1 with no effect.
   *Recommendation: correct the constants before quoting the run-win target
   again. Yours \u2014 it is a design target question, not a bug.*""",
     '3 the residual I got wrong'),
    (u"""2. **`G3-late` is untested.** It carries silver plus `bankAdd:500` and
   starstone. `G2-mid` measured as unmoved by the fix (inside noise), but G3
   has not been checked and it is an "intended gear" row in the acceptance
   targets.""",
     u"""2. ~~**`G3-late` is untested.**~~ **MEASURED, no action.** Across arms it
   moves +0.29pp patron and \u22121.87pp boss, at or barely outside a 1.0pp floor
   (n=14,400 matches per band per arm). The fix does not move it.""",
     '4 G3-late closed'),
])

patch('docs/archive/README.md', [
    (u"""**Its \u00a79 still carries the full-silver "TRAP at 4% run wins" verdict, which is WITHDRAWN** \u2014 the sim that produced it hard-coded the bust immunity it was used to judge (fixed P888) and is match-level, so it could not have produced a run number at all. The live brief has the withdrawal and the re-measurement. |""",
     u"""**Its \u00a79 still carries the full-silver "TRAP at 4% run wins" verdict, which is WITHDRAWN** \u2014 `_runBalanceSim` is match-level and could not have produced a run number at all, and two of the three named components (Ward, Insurance) are not modellable. The verdict also predates the sim's silver defect by four and a half minutes, so that defect is *not* its parent; what it did measure was a live silver bust-shield that has since been retired. The live brief has the withdrawal, the corrected parent and the re-measurement. |""",
     '5 the archive pointer, corrected'),
])

# ── post-asserts ────────────────────────────────────────────────────
b = io.open(os.path.join(ROOT, 'docs', 'briefs', 'FARK_MASTER_BRIEF.md'),
            encoding='utf-8', newline='').read()
if 'hard-coded the very immunity under test - one' in b:
    sys.exit('the wrong parent survives in the brief (nothing written)')
if b.count('chronologically impossible') != 1:
    sys.exit('the correction is not stated exactly once (nothing written)')
o = io.open(os.path.join(ROOT, 'docs', 'OPEN.md'), encoding='utf-8',
            newline='').read()
if 'most likely ancestor' in o and 'chronologically impossible' not in o:
    sys.exit('OPEN.md still asserts the wrong ancestor (nothing written)')
a = io.open(os.path.join(ROOT, 'docs', 'archive', 'README.md'),
            encoding='utf-8', newline='').read()
if 'hard-coded the bust immunity it was used to judge' in a:
    sys.exit('the archive pointer still names the wrong parent (nothing written)')

print('done: %d edits\n  %s' % (len(edits), '\n  '.join(edits)))
