# -*- coding: utf-8 -*-
u"""Append passes 4 and 5 to CARD_AUDIT.md, through the Write tool."""
import io, os

P = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                 'docs', 'CARD_AUDIT.md')
s = io.open(P, encoding='utf-8').read()
assert 'Pass 4' not in s, 'already appended'

s = s.rstrip() + u"""

---

# Passes 4-5 - the BANK-modifying branches, which pass 3 was blind to

Pass 4 set out to scope the ~17 dice-moving cards. **Its first cut mislabelled
five mechanics as dice-movers** - `flat_bonus`, `double_first_bank`,
`gain_when_ahead`, `halve_first_bank`, `halve_big_bank`. They move no dice at
all. They change `total` / `pts` - **the bank** - and the money reaches a score
pool *outside the branch*, so pass 3's `G.pPts` / `G.oPts` regex never saw them.

**Ten branches had gone unchecked for direction**, and four now route through
the `BANK_FX` table built earlier tonight, so the arithmetic no longer looks
like arithmetic at the call site either.

## The invariant needs the enclosing FUNCTION, not just the card list

The function decides whose bank is on the table:

| | in `handleBank` (player's bank) | in `finOpp` / `_oppFx*` (patron's bank) |
|---|---|---|
| **patron's card** | lowers | raises |
| **player's card** | raises | lowers |

## Result: 10 branches, 0 helping the wrong side

Every one matches the table above. Combined with pass 3, **23
direction-checked branches and none pointing the wrong way.**

## The refactor blindness fired three times, the third inside the tool checking for it

1. **Pass 3**: `SCORE_DRAIN.periodic_drain` and P467's rewritten `challenge`
   stopped looking like `+=` / `-=`. 10 of 15 classified.
2. **Pass 4**: five bank-modifiers had no score-pool signature at all and were
   filed as dice-movers.
3. **Pass 5**: `span_of('finOpp')` reported five of ten branches as `(other)` -
   because **P470 extracted `finOpp`'s loops into `_oppFxOwnA/B/Player/Drain`
   earlier tonight**. The tool written to catch refactor blindness was blinded
   by the same refactor.

Kept rather than quietly fixed, because all three were found only by looking at
coverage rather than at the verdict column. **A clean "0 wrong" from a checker
that can see two thirds of its subject is not a result.**

## One more thing worth recording

Pass 5's first draft printed a hardcoded `ok` verdict column - a display, not a
check. It was replaced with a computed one before any result was reported. That
is precisely the failure this audit exists to find, produced by the audit.

## What is still a reading task

The genuine dice-movers - `steal_die`, `swap_die`, `swap_best_to_3`,
`reroll_all_kept`, `reduce_first_roll` - plus the activation controls
(`block_activations`, `limit_activations`, `immune_modifiers`) and
`hidden_cards`. Those have no score or bank signature, and whether they touch
the *right dice* cannot be inferred from shape.
"""
io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('passes 4-5 appended')
