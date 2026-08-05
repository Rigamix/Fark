# -*- coding: utf-8 -*-
u"""Append the estimator test to SPREAD_AUDIT.md - it falsifies that doc's own fix."""
import io, os

P = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                 'docs', 'SPREAD_AUDIT.md')
s = io.open(P, encoding='utf-8').read()
assert 'Tested' not in s, 'already appended'

s = s.rstrip() + u"""

---

# Tested: a better estimator gains nothing. The sample is the limit.

This document argued `spread` (max − min) is unsound for mid-sized deltas
**because it discards all but two of the four agents**, and implied a
fuller-information estimator would resolve smaller changes. **That was reasoned,
not measured. It is wrong.**

Measured with `tools/spread_alternatives.py`: five seeds, per-agent win rates
kept, three estimators computed from **the same run** - `spread`, population
`sd`, and mean absolute deviation.

| estimator | t0 → t7 fall | seed-noise | **signal-to-noise** | smallest resolvable change |
|---|---|---|---|---|
| `spread` | 35.33 | 3.35 | **10.6** | 19% of its range |
| `sd` | 14.95 | 1.41 | **10.6** | 19% of its range |
| `mad` | 12.92 | 1.22 | **10.6** | 19% of its range |

**Identical, to one decimal, for all three.** Because `sd / spread = 0.424 ±
0.006` across every tier and every seed - the four agents' dispersion has a
stable *shape*, so `sd` is `spread` on another scale, and **rescaling cannot
change a signal-to-noise ratio.**

## What this changes

**The conclusion stands; the reason and the fix do not.**

- **Still true:** `spread` cannot resolve a mid-sized delta. The aggression
  pass's 6.2 and the oppCards lift's spread column remain unreportable.
- **Wrong:** that max−min throwing away data was the cause. It is mechanically
  true and empirically irrelevant here.
- **Wrong:** that switching estimator would help. It is busywork - all three
  resolve the same 19% of their own range.
- **The actual limit is the FOUR-AGENT SAMPLE** (and N per agent). To resolve
  smaller moves the sweep needs more agents or more matches, not a better
  formula.

## Worth keeping as a method note

A plausible mechanism ("it discards data, so it must be noisier") was stated
confidently, repeated several times, and used to justify declining results. One
run falsified it. **The estimator question was cheap to test and was not tested
until it was about to drive work** - which is the same shape as everything else
this project keeps finding, applied to a claim of mine rather than to the code.
"""
io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('estimator test appended to SPREAD_AUDIT.md')
