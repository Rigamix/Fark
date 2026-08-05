# Sizing: real NPC selection, `commit`, and opponent enchants

Measured before building, per the four questions. `tools/npc_selection_size.py`.

## Q1 — Can the NPC reuse the player's evaluation, or is it welded to the UI?

**It can call it. Every candidate is pure.**

| function | lines | UI/DOM calls |
|---|---|---|
| `scoreRoll` | 530 | **0** |
| `scoreSelection` | 49 | **0** |
| `anyScoring` | 8 | **0** |
| `famCommitBonus` | 34 | **0** |
| `oppShouldBank` | 102 | **0** |
| `dieRank` | 1 | **0** |

This was the trap the pass existed to avoid — "the NPC just needs to call what
the player calls" is only true if that path isn't tap-bound. **It isn't.** Real
selection is a *call*, not an extraction.

## Q2 — Does that produce `commit`'s payload? **It already does.**

The biggest finding, and it inverts the assumed ordering.

`commit`'s payload derives entirely from `selD`, which is
`G.pool.filter(x => x.sel && !x.committed)` — a set of dice. `isTriple`,
`isStraight`, `jade`, `hitFirst`, `hitLast` are all **computed from selD**, not
from anything the tap supplied.

**And the NPC already produces exactly that set today.** It calls `scoreRoll`
and reads `used[]` — a per-die boolean of what the scorer consumed — then does
`G.oppDice.filter(d => !d.kept).forEach((d,i) => { if(used[i]) d.kept = true; })`.

So the rival's chosen dice exist, aligned by index, right now.

> **`commit` does not have to wait for the decision work.** Its payload is
> derivable today from `used[]`, with no new logic. The seam was held for a
> ruling on what a rival "committing dice" means — and the answer is that it
> already commits real dice; it just doesn't *choose between options*.

## What is actually missing: choice, not selection

The NPC takes the scorer's single maximal answer. It never weighs *keep three
fives* against *keep one and reroll five dice*. Measured: `.sel` flags set **0**
times, `scoreSelection` called **0** times, `famCommitBonus` called **0** times.

So "real decision-making" is: **enumerate candidate keeps → score each →
choose by persona.** Genuinely new logic, but it sits entirely on pure functions
that already exist.

## Q3 — Opponent enchants: parallel, and small

| | |
|---|---|
| `scoreRoll` already takes `dieEnchs` | **8** references |
| player enchant array `_enchArr` | **47** references |
| **opponent enchant array** | **0** |

The scoring engine already applies per-die enchants. There is simply no
opponent-side array to hand it. **This does not depend on the selection work at
all** — different data, same engine — so it is parallel, not sequential, and it
is closer to plumbing than to design.

## Q4 — Levers: the structure is already there

`persona` (49 references), `behavior` (17), `dieBias` (11), `rung.agg` (8),
`minBank` (8), `diceStop` (7), `chaotic` (4), `adaptive` (3).

**Smallest real slice:** one threshold that biases *which* candidate keep gets
chosen — reusing `agg` and `minBank` rather than adding a field. Hesitation and
timing are presentation on top of that choice and should follow it, not lead.

## Recommended order, and it differs from the assumption

1. **Raise `commit` now.** The payload exists; this is unblocked today and was
   only ever waiting on a question the measurement answers.
2. **Opponent enchants**, in parallel — independent, engine-side already done.
3. **Candidate-selection choice**, the substantial piece, on pure functions.
4. **One persona lever** biasing the choice, once there are choices to bias.
5. The decision-moment dialogue stays parked — genuinely downstream of 3.
