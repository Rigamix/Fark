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
