# -*- coding: utf-8 -*-
u"""Append the silver re-derivation's residuals to docs/OPEN.md, after the
bustsPerMatch resolution already there.

Offset insert: OPEN.md has MIXED line endings (CRLF for the first four lines,
LF after), so splitting on either corrupts it.
"""
import io, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'docs', 'OPEN.md')
s = io.open(P, encoding='utf-8', newline='').read()

MARK = u'generalised from a filtered view.'
i = s.find(MARK)
if i < 0:
    sys.exit('the bustsPerMatch resolution is not there (nothing written)')
if u'SILVER: WHAT THE RE-DERIVATION LEFT OPEN' in s:
    sys.exit('the residuals are already there (nothing written)')
cut = i + len(MARK)

NEW = u"""

### SILVER: WHAT THE RE-DERIVATION LEFT OPEN

The full-silver verdict in `FARK_MASTER_BRIEF.md` is **withdrawn, not
re-run** — its instrument granted the immunity it was used to judge, and no
harness that touches `_runBalanceSim` can produce a run-win number at all.
Re-measured (2,000 matches/cell): six-silver is indistinguishable from the
shipped G2-mid gear and +22–25pp over all-bone. **Not a trap, not a menace.**

Two things fell out that are more useful than the verdict was:

**Six silver is unbuildable.** `DICE_STORE` stocks silver at 1 per run, every
purchase path guards on the stock, and the starter draft adds at most one more
— ceiling of two, three with Brutus's Shield. **The buildable two-silver stack
beats two 100g IRONS by +0.8 to +1.3pp, which is inside noise.** A 580g die
performing like a 100g one is the live question, and it is a pricing one.
*Recommendation: yours — either Silver's price comes down or its weighting goes
up. I have not touched either.*

**The bug's leverage ran backwards from the intuition.** The free save was
worth 4.8pp of a 7.2pp apparent gain for ONE silver among bones (67% of it),
and +0.2pp for six. It inflated *thin* silver builds, not stacked ones — so the
defect cannot by itself explain a "stacking is a trap" verdict.

**Still carrying the same contamination, not yet re-derived:**

1. **`_runEconomySim`'s `PWIN`/`BWIN` constants.** It is run-level but rolls no
   dice — it takes win rates as hard-coded numbers copied from the balance
   sim's gear-band rows, which were silver-bearing. Every `runsWon` and pity
   number it has produced rests on them, and **this is the most likely ancestor
   of the "4% run wins" figure.**
2. **`G3-late` is untested.** It carries silver plus `bankAdd:500` and
   starstone. `G2-mid` measured as unmoved by the fix (inside noise), but G3
   has not been checked and it is an "intended gear" row in the acceptance
   targets.
3. **A cross-harness discrepancy, flagged not concluded.** Measured per-turn
   player bust rate is silver/bone ≈ **0.33–0.40**; the recorded anchor in
   `FARK_ENCHANT_BADGE_REWORK.md` is **0.54–0.58**. The denominators genuinely
   differ — `FSIM.measureTurnBust` plays turns with no match around them, so it
   has no early exit at target and no last-licks branch — so this is a lead for
   a dedicated check, **not** a finding.

**Fixed on the way (P890), because my own P888 broke it:** FSIM's
`__shippedCompat` emulated two differences from the shipped sim, one of which
was the free bust-save P888 deleted. Left alone, `sim_verify`'s control would
have been inverted — the compat arm granting a save the thing it models no
longer has, reporting a gap *in FSIM's favour*, which is the worst direction
for a check whose job is to catch FSIM being wrong. The save half is deleted;
the hot-dice half is untouched and still real.

**Checked and cleared, so you don't have to:** the `_runCowardiceGate` verdict
survives (PUSH PAYS, margin ~18.5 against a threshold of 5; the bug inflated it
by ~2.5pp). The **TWICE SAVED** feat is reachable — it reads `_featWardSaves`,
which is incremented where a ward halves a busted turn, so it tracks ward saves
and those still exist."""

io.open(P, 'w', encoding='utf-8', newline='').write(s[:cut] + NEW + s[cut:])
print('OPEN.md: silver residuals appended')
