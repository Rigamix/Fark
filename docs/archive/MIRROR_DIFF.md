# `handleBank` vs `finOpp` — do the nine agree? Yes, all nine.

Before writing a table over 19 branches: **a pair that has already drifted is a
bug found, not an obstacle — but it has to be found rather than merged over.**
Merging two branches that quietly disagree picks a winner silently and deletes
the evidence. `ill_omen` was exactly that, and nobody had decided it.

Rerun with `tools/mirror_diff.py`.

## The answer

**All nine are the same rule seen from two seats.** The table is buildable and
no ruling is needed first.

Getting there took four passes, and three of the four disagreements the tool
reported were the tool:

| pass | agree | what was wrong |
|---|---|---|
| 1 | **0 / 9** | counted `setTimeout` delays and spark counts as rule parameters |
| 2 | 3 / 9 | compared guard *field names*; `playerOnce` vs `usedOnce` is which seat's bookkeeping, like `pPts` vs `oPts` |
| 3 | 5 / 9 | — |
| read | **9 / 9** | `branch()` captured the block but **not the `if` condition**, where the player's once-guard lives |

A 0-of-9 clean sweep was the first signal. That is not a finding, it is the
shape an instrument artifact makes.

## The two that needed reading, and what they turned out to be

**`halve_first_bank`, `block_low_bank`** — same rule. The player's guard sits in
the condition, which the extractor never read.

**`challenge`** — the player's copy reads
`G.npcCardState.challengeThreshold`, set from `npc.effect.threshold` at
`startPTurn`. Same values, **frozen at declaration on purpose**: challenge is
declared on one turn and resolved on the next. The rival resolves immediately
and reads `eff` live. A real design difference, not drift — and one the table
must preserve rather than flatten.

**`gain_when_ahead`** — the player defends with `eff.amount||500`; the rival
uses `npc.effect.amount` bare. Only `corvus_writ` carries this mechanic and it
*does* define `amount:500`, so **nothing is broken today**. It is latent
fragility: the day a second card omits `amount`, the rival adds `undefined` and
the score goes `NaN`. Worth fixing when the table lands, since a single row with
one default removes the asymmetry for free.

## What this means for the table

Nine rows, two dispatch sites, and the two sides can no longer drift. Two
constraints carried forward:

1. **`challenge` needs its terms frozen for the player and live for the rival.**
   The row must express *when* the terms are read, not just what they are.
2. **The default belongs in the row**, so both seats inherit it.

---

## CORRECTION 2026-09-04 — `flat_bonus` is not a clean mirror

`tools/mirror_diff.py` carried a corrupted word boundary: the `\b` in its
noise-stripping regex had been written through a heredoc and arrived as a
backspace byte (0x08), so the pattern matched nothing and presentation calls
were never stripped. An `eff.amount` sitting inside an unstripped
`triggerCard(...)` then counted as a rule parameter, manufacturing agreement.

Isolated against the Aug-21 snapshot so the tool is separated from code drift:

| | agree | differ | one side |
|---|---|---|---|
| Aug-21 code, broken regex (what was recorded) | 4 | 3 | 2 |
| Aug-21 code, fixed regex | **3** | **4** | 2 |
| today's code, fixed regex | **3** | **4** | 2 |

Today matches Aug-21 exactly, so **there is no code drift** - the disagreement
is longstanding and the tool was hiding it. The commit that recorded "4 clean
mirrors, 3 rulings, one dead mechanic" should read **3 clean mirrors, 4
rulings**.

**What actually differs.** Both seats call the same `BANK_FX.flat_bonus`, so the
EFFECT is identical; the GUARDS differ, in both directions:

- rival (`_oppFxOwnA`): `eff.type==='on_opp_bank' && eff.mechanic==='flat_bonus'`
- player: `eff && eff.mechanic==='flat_bonus' && (eff.amount||0)>0`

The player requires a positive amount and does not check `type`; the rival
checks `type` and does not require an amount. **Latent, not live**: only
`old_partners_badge` carries the mechanic today and it satisfies both. This is
the same species as the `gain_when_ahead` default already recorded above - a row
in the table removes it for free, and the row must carry BOTH conditions rather
than picking one seat's.

**The 9/9 headline stands as what it was.** It was reached by READING, not by
the tool - this document's own pass table ends `read | 9/9`. The tool never
reported nine.
