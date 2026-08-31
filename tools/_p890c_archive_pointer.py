# -*- coding: utf-8 -*-
u"""P890c: point the archive's own index at the withdrawn silver verdict, and
correct the residual I raised that the archive had already answered.

THE DUPLICATION IS REAL BUT ALREADY HANDLED. The withdrawn verdict appears
twice: docs/briefs/FARK_MASTER_BRIEF.md (fixed) and
docs/archive/FARK_MASTER_BRIEF.md (a superseded copy). There is no separate
run-sim findings document anywhere in the repo - I grepped the whole tree, not
the one file. The archive README already flags that copy as a "Stale
duplicate ... still being read from", so the mechanism exists; what it does not
do is name THIS claim, which is what a grep for silver would land on. So the
existing rows are extended rather than a new marker invented, and the archived
text itself is left exactly as it was - the point of an archive is that a
decision can be traced back to what it was made against.

AND THE ARCHIVE HAD ALREADY ANSWERED MY THIRD RESIDUAL. I flagged a
"cross-harness discrepancy" - a measured per-turn silver/bone bust ratio of
0.33-0.40 against a recorded 0.54-0.58 anchor - as a lead needing a dedicated
check. Ruling #24 in SIM_RESULTS_2026-07-31.md had already swept that ratio
across seventeen policy cells and found it runs 0.126 to 0.864, monotone in how
deep the turn pushes, and is explicitly NOT policy-invariant. My number sits
inside that sweep. It is not a discrepancy, it is the documented policy
dependence, and those figures came through FSIM, whose compat bust-save is off
by default, so they were never contaminated by the defect P888 removed.

That is the third time this run that the file or its neighbours had written
down the thing I was about to go and measure.
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


patch('docs/archive/README.md', [
    (u"""| `FARK_MASTER_BRIEF.md` | **Stale duplicate**, eight days behind `briefs/FARK_MASTER_BRIEF.md` and still being read from. Same trap as the match brief below, found the same way. |""",
     u"""| `FARK_MASTER_BRIEF.md` | **Stale duplicate**, eight days behind `briefs/FARK_MASTER_BRIEF.md` and still being read from. Same trap as the match brief below, found the same way. **Its \u00a79 still carries the full-silver "TRAP at 4% run wins" verdict, which is WITHDRAWN** \u2014 the sim that produced it hard-coded the bust immunity it was used to judge (fixed P888) and is match-level, so it could not have produced a run number at all. The live brief has the withdrawal and the re-measurement. |""",
     '1 the brief row names the withdrawn verdict'),
    (u"""| `SIM_RESULTS_2026-07-31.md` | **Every figure is stale**""",
     u"""| `SIM_RESULTS_2026-07-31.md` | Still the best source on one thing: **Ruling #24's finding that the Silver:bone bust ratio is NOT policy-invariant** (0.126\u20130.864 across seventeen policy cells, monotone in push depth) is sound and was measured through FSIM, whose compat bust-save is off by default \u2014 so it is untouched by the defect P888 removed, and it explains any silver ratio that disagrees with the 0.54\u20130.58 anchor. Otherwise: **every figure is stale**""",
     '2 the sim-results row keeps its one live finding'),
])

# ── correct my own residual in OPEN.md ──────────────────────────────
patch('docs/OPEN.md', [
    (u"""3. **A cross-harness discrepancy, flagged not concluded.** Measured per-turn
   player bust rate is silver/bone \u2248 **0.33\u20130.40**; the recorded anchor in
   `FARK_ENCHANT_BADGE_REWORK.md` is **0.54\u20130.58**. The denominators genuinely
   differ \u2014 `FSIM.measureTurnBust` plays turns with no match around them, so it
   has no early exit at target and no last-licks branch \u2014 so this is a lead for
   a dedicated check, **not** a finding.""",
     u"""3. ~~**A cross-harness discrepancy.**~~ **RESOLVED \u2014 and the archive had
   already answered it before I raised it.** I measured a per-turn silver/bone
   bust ratio of **0.33\u20130.40** against the **0.54\u20130.58** anchor and flagged it
   as a lead. Ruling #24 in `docs/archive/SIM_RESULTS_2026-07-31.md` had
   already swept that ratio across **seventeen policy cells** and found it runs
   **0.126 \u2192 0.864**, monotone in how deep the turn pushes, and is explicitly
   **not policy-invariant**. My number sits inside that sweep. It is the
   documented policy dependence, not a discrepancy \u2014 and those figures came
   through FSIM, whose compat bust-save is off by default, so they were never
   contaminated. **No action.** What the anchor is missing is the caveat that
   it holds at one policy only, which Ruling #24 already says.""",
     '3 the residual I should not have raised'),
])

print('done: %d edits\n  %s' % (len(edits), '\n  '.join(edits)))
