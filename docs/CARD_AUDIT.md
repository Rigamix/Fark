# The patron card audit — pass 1: the cheap check is clean

41 cards went from provably-inert to live in one commit (P473). The difficulty
delta says they work **in aggregate**; an aggregate moving correctly is
compatible with individual cards being silently wrong in ways that cancel out.
None had been checked on its own.

Rerun with `tools/card_audit.py`.

## Result

| verdict | count |
|---|---|
| **UNWIRED** — mechanic/type with no dispatch anywhere | **0** |
| **MISMATCH** — a number in the text absent from the effect | **0** |
| `ok` — text numbers all backed by the effect object | 17 |
| NO NUMBERS — text promises no quantity | 24 |

**Every pooled card reaches a live dispatch, and every stated number is the
number the effect uses.** That is the whole automatable claim.

## What it does not claim

`ok` is necessary, not sufficient — a card can use its stated amount in entirely
the wrong direction and pass this. And **NO NUMBERS is a reading list, not a
pass**: 24 cards promise behaviour without a quantity (`steal_die`,
`reroll_all_kept`, `block_activations`…), and nothing mechanical can check those.
**That is where the remaining audit value is, and it is a reading task.**

## The tool produced six false findings first

It reported six MISMATCHes — `beginners_luck` "unbacked 200", `campaign_veteran`
"unbacked 0", and four more. Every one was the **thousands separator**: the card
text writes `1,200`, and a plain 2–6 digit match splits that into `200`;
`2,000` becomes `000` → 0.

**And the first fix silently did nothing.** It went through a bash heredoc, and
the `` in `\d{3}` was written as a **literal backspace byte**. The pattern
became `(?=\d{3}<BS>)` — which prints looking correct, matches nothing, and
leaves the false findings in place *while appearing repaired*. Three further
rounds of debugging chased a function whose printed source was right.

This is the second time tonight: `until_audit.py` invented eight false findings
by the same mechanism. There is a standing rule that backslash-containing
patches go through the Write tool rather than a heredoc. **The rule existed and
I skipped it.** The repair is now a plain `.replace(',', '')` with no escapes at
all, so there is nothing left for a quoting layer to corrupt.

**Worth noting what made it findable:** six mismatches with `500` unbacked in
four of them was too concentrated to be six independent bugs. The
suspicious-uniformity check caught it before it was reported as a finding.

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
