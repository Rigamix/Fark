# The bust-path mirrors: 2 of 7, not 7 — the table mostly isn't there

Ran the `mirror_diff` pass over the seven mechanics I proposed as the remaining
mirror pairs. **The premise mostly does not hold.** Reading is what settled it,
as it did for `handleBank`/`finOpp`.

## What each one turned out to be

| mechanic | verdict |
|---|---|
| `single1_bonus` | **never a pair** — `step`'s occurrence is a `.some()` query: *does the opponent hold a die with this mechanic* |
| `single5_bonus` | **never a pair** — same query |
| `bust_bank_half` | **never a pair** — `doBust`'s side is a `.find()` query; only `step`'s is a dispatch |
| `bust_survive` | **two different rules.** Player: unconditional save, once per card. Boss: `Math.random() < eff.chance` **and** halves its bank. Not one rule from two seats |
| `bust_immune_turns` | **differs.** Player `G.turnNum <= (eff.turns||2)`, boss `oppTurnCount < eff.turns` — `<=` vs `<`, and a default on one side only |
| `gain_pts` | **true mirror**, one missing default (`||500` on one side) |
| `punish_busts` | **true mirror**, one missing default (`||2` on one side) |

## The mistake in proposing them, which is mine from an hour ago

I built the pair list from `mechanic_table.py`, which groups **every occurrence**
of a mechanic name by enclosing function. `mechanic_kind.py` exists specifically
to separate dispatch from query, and it was written tonight, after the same
error. **I had the corrected instrument and used the uncorrected number.**

And the bar itself was a proxy. *"Appears in a player function and an opponent
function"* stands in for *"is the same rule written twice"*. In the bank case
they coincided. Here they do not: three pairs were a query beside a dispatch, and
one was two genuinely different designs sharing a name — which is the
`challenge` frozen-vs-live lesson repeating at a different site.

## What is actually worth doing

**Two rows, not seven** — `gain_pts` and `punish_busts`, both true mirrors whose
only divergence is a default present on one side and absent on the other. That is
the same shape as `gain_when_ahead`, and the same fix: one row carries the
default and both seats inherit it.

**And one thing to check before it is a row, not after:** `bust_immune_turns`'
`<=` versus `<`. If `turns` is 2, the player is immune on turns 1 **and 2**
while the boss is immune only on turn 1. That is an off-by-one between two copies
of one card, and it is a question about intent, not a merge — it goes to
`OPEN.md` rather than into a table.

**`bust_survive` should not be tabulated at all.** A probabilistic save that
costs half the bank and an unconditional one are different cards wearing one
mechanic name.
