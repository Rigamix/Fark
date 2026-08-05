# -*- coding: utf-8 -*-
u"""Append the pass-3 section to CARD_AUDIT.md, through the Write tool."""
import io, os

P = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                 'docs', 'CARD_AUDIT.md')
s = io.open(P, encoding='utf-8').read()
assert 'Pass 3' not in s, 'already appended'

s = s.rstrip() + u"""

---

# Pass 3 - DIRECTION and OWNERSHIP: does a card benefit its holder?

Passes 1 and 2 checked that stated numbers are the numbers used. Neither can
check whether the effect moves them the RIGHT WAY - and that is exactly where
tonight's two real bugs lived: `challenge` charging the rival twice, and
`ill_omen` reading "busted" on one seat and "scored nothing" on the other.

**Direction is not purely a reading task.** Whose card it is comes from the
enclosing loop (`G.oCards` / `G.pCards`, by brace extent); who gains comes from
which pool the branch credits. `tools/card_audit3.py`.

## Result: 13 attributable branches, 0 pointing the wrong way

| mechanic | patron's copy | player's copy |
|---|---|---|
| `gain_pts` | +patron | +player |
| `steal_pct` | +patron | +player |
| `steal_low_bank` | +patron | +player |
| `punish_busts` | -player | -patron |
| `periodic_drain` | -player | -patron |
| `challenge` | -player | -patron |
| `bust_bank_half` | - | +player |

**Every mechanic present on both seats inverts correctly.** `bust_bank_half`
appears once because its patron-side occurrence is a query, not a dispatch -
established in pass 1 of the bust-mirror work.

## Coverage, stated rather than implied

**15 branches touch a score pool. 13 sit inside an identifiable card list** and
all 13 point correctly. The other 2 are not inside a card-list loop, so
ownership cannot be attributed mechanically - they are not passes, they are
out of this instrument's reach.

## The instrument was blind to three branches, all from tonight's own refactors

The first run classified 10 of 15. The three it missed were
`SCORE_DRAIN.periodic_drain(...)` (twice) and P467's rewritten `challenge`
deduction - **code refactored earlier tonight**. Moving arithmetic into a table
row is cleaner and simultaneously stops the sign LOOKING like a `+=` or `-=`.

Worth keeping: **a refactor can blind a checker that was reading the old shape**,
and the honest fix is to teach the tool the new form rather than report 10 and
call it 15.

## What is still genuinely a reading task

Magnitude sensibility, whether each trigger condition matches its prose, and the
~17 cards that move **dice** rather than points - rerolls, swaps, seizures.
Three passes have shrunk the list to those; none of them replaces reading it.
"""
io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('pass 3 appended')
