# -*- coding: utf-8 -*-
u"""Append the pass-2 section to CARD_AUDIT.md.

The first attempt went through a bash heredoc whose payload contained a triple
quote; python raised SyntaxError, the doc was never written, and the `git`
command on the following line ran anyway - committing a message that described
a section that does not exist.

Two lessons, both already on the books and both skipped again:
  - do not push multi-line content through heredocs; use the Write tool
  - do not chain a commit after a step whose failure it cannot see
"""
import io, os

P = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                 'docs', 'CARD_AUDIT.md')
s = io.open(P, encoding='utf-8').read()
assert 'Pass 2' not in s, 'the section is already there'

s = s.rstrip() + u"""

---

# Pass 2 - quantities written as WORDS, which pass 1 could not see

Pass 1 compared **digits**. It classified 24 cards "NO NUMBERS" - but several
state a quantity in words, and a digit scan sees none of it:

| card | text | effect |
|---|---|---|
| `hold_the_line` | "first **two** turns" | `turns:2` |
| `sundays_rest` | "first **three** turns" | `turns:3` |
| `grogs_bump` | "**Twice** per match... **TWO** dice" | `uses:2, swapN:2` |
| `point_of_order` | "every **2nd** turn" | `interval:2` |
| `the_sermon` | "every **4th** turn" | `interval:4` |

**That was pass 1's blind spot, not a clean result** - "24 need reading" was
hiding a checkable subset. `tools/card_audit2.py`.

## Result: also clean

**22 cards carry a word-quantity. Every one matches its effect.** That includes
`hold_the_line` (2) and `sundays_rest` (3) - the exact pair P469 touched when it
fixed the `<=` / `<` off-by-one, now verified against their own text.

## Two instrument corrections, both caught before reporting

**Ordinals are not quantities.** "first two turns" means *two*; mapping `first`
-> 1 made `hold_the_line` read `[1,2]` and `sundays_rest` `[1,3]`, flagging two
correct cards. Removed - the ordinals that genuinely *are* quantities ("every
2nd turn") keep their entries.

**Prose can state a derived total.** `grogs_bump` says *"Four dice ruined over a
match"* - that is `swapN:2` x `uses:2`, a consequence rather than a parameter.
The tool still flags it and this note explains why it is benign; special-casing
it would hide a future real mismatch behind the same shape.

## Where the audit stands

**Every mechanically checkable claim across all 41 cards holds** - wiring, digit
quantities, word quantities. What remains needs reading and cannot be automated:
**direction** (does it take from the right side), **ownership** (does the
player's copy mirror the boss's), and whether the effect does the *right thing*
with the right number. Two passes shrank the list; they did not replace it.
"""
io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('pass 2 section appended to CARD_AUDIT.md')
