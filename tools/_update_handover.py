# -*- coding: utf-8 -*-
u"""Refresh NEXT_SESSION.md section 0 - a lot landed after it was last written."""
import io, os

P = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                 'docs', 'NEXT_SESSION.md')
s = io.open(P, encoding='utf-8').read()

# EM-DASH, not a hyphen. The heading was written with one and this anchor was
# typed with the other, so the assert fired on a zero match - which is the assert
# doing its job rather than the patch silently writing nothing.
OLD = u"""## 0. READ THIS FIRST — one fact changes how the rest of this doc reads

**`generateOppCards` begins `return [];`** (P1-cutover stub, comment says *"NPC
family cards land in P5"*). So **`G.oCards` is always empty in the live game.**
Verified in a real match: `G.oCards.length === 0`, `G.oF.length === 1`."""
assert s.count(OLD) == 1, 'section 0 header matched %d' % s.count(OLD)

NEW = u"""## 0. READ THIS FIRST - the state, and what is waiting on you

**The patron card layer is LIVE.** `generateOppCards` used to begin
`return [];` - a P1-cutover stub that made `G.oCards` permanently empty. **P473
lifted it**, so all 41 pooled patron cards are dealt for the first time since
that cutover.

**Measured on its own** (`OPPCARDS_LIFT_MEASURED.md`), five seeds, same-seed
before/after: win rate falls 0.8-3.8 points at every tier that draws cards, and
**tier 0 is identical to the decimal** - it is the one tier whose patrons have no
card pool, so it is the control, and it held. Bosses are genuinely stronger.
The `spread` column moved too and is **not** reportable - see `SPREAD_AUDIT.md`.

**Still two different systems, and the doc below blurs them:**

| layer | state |
|---|---|
| **family cards** - `G.oF`, CFX, `_famInitOpp` | works |
| **NPC cards** - `G.oCards`, `mechanic===` | **now works too** (P473) |

### Waiting on a ruling - nothing is blocked

- **`OPEN.md` §8** - `blessed_dice` / `crown_authority` say "reroll", the code
  wipes the kept dice and turn points. Text or code, both defensible.
- **`commit`** - the last ungated seam, 7 of 8 raise. Its payload describes the
  shape of a *selection*, and the rival scores a roll and banks instead.
  `SEAM_TWO_LEFT.md`.

### Done since this doc was written

The **effect-system plan is finished** - all six phases, re-planned at its own
checkpoint (`EFFECT_PLAN_REPLAN.md`). Phase 5 (Observers) measured and pinned by
`apv_observers`. Five mechanic tables shipped and the remaining 13 single-site
mechanics **deliberately not** tabulated (`TABLE_BAR.md` - the bar is *removes a
copy*). Law 6 (symmetry by default) is in the brief with its two named
exceptions. The **card audit is complete** - six passes, one finding
(`CARD_AUDIT.md`).

### The habit worth carrying in

Instruments were wrong more than a dozen times last session and **every one
measured something adjacent to the question** - timing delays read as rule
parameters, lines as statements, a captured block missing the condition that
gated it, a regex holding a literal backspace byte. Standing checks:

- **a unanimous result or a zero delta is a tell, not a finding** - three
  identical sim runs are what uncovered the P1 stub
- **ask what a checker can SEE before trusting what it says** - three separate
  coverage gaps were found that way, one of them inside the tool written to
  catch coverage gaps
- **before changing a stub or guard, grep what references it**, not only what it
  references"""
io.open(P, 'w', encoding='utf-8', newline='').write(s.replace(OLD, NEW))
print('handover section 0 refreshed')
