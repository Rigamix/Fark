# `commit` and `deadRoll` — the last two seams, scoped

Scoped together because they share a precondition that only became true with
P473: a boss with a card wanting these moments previously had **no card and no
moment**. Rerun with `tools/seam_two_left.py`.

Six of eight opponent seams already raise — `turnStart`, `roll` (P459), `bust`,
`bankBonus` (P461), `rivalTurn` (P462).

## Safe to raise: every consumer gates

| seam | consumers | all gate on `_fxMine`? |
|---|---|---|
| `commit` | `short_fuse`, `bloom`, `cultivate`, `vanguard_f` | **yes** |
| `deadRoll` | one | **yes** |

So raising either **ungates nothing** — same as the six shipped. That was the
first question and it is settled.

## Both have a canonical moment. Neither has its payload.

| seam | the rival's moment | what the player's raise carries |
|---|---|---|
| `commit` | `oppBank+=total;` — **one site**, L28280 | `sel`, `isTriple`, `isStraight`, `jade`, `hitFirst`, `hitLast` |
| `deadRoll` | `if(total===0){_oppBustOut();return;}` — **one site**, L28078 | `free` |

At both sites the only expected local in scope is `fV` (face values). The
`scoreRoll` results nearby (`_qhR`, `_gbR`, `_stR`) are per-card evaluations,
not the turn's scoring.

**This is the `endPTurn` shape exactly** — the moment is findable, the value is
not — which is what P462 had to thread before `rivalTurn` could mirror.

## Which corrects two earlier readings, including one from tonight

- **The old note said** `commit` was *"10 genuinely different re-scoring sites"*
  and `deadRoll` *"needs the NPC to gain a concept it doesn't have"*. Both wrong:
  each has exactly one canonical site.
- **My first pass tonight said** `deadRoll` had **0** candidate sites — because
  the pattern searched for the *sim harness*'s `out.busted` form, not
  `runOppTurn`'s `total===0`. A zero I did not believe, and correctly so.

## The two are not the same size

**`deadRoll` is small.** One value — the rival's free dice at the moment its
roll scored nothing. `fV` and `G.oppDice` are both to hand; this is a derivation,
not a design question.

**`commit` is not.** Six values, and four of them (`isTriple`, `isStraight`,
`hitFirst`, `hitLast`) describe the *shape of a selection the player made*. The
rival does not select the same way — it scores a roll and banks. **What the
rival's "commit" even means is a design question**, the same class as
`challenge`'s frozen-vs-live terms, and it should be ruled rather than inferred
from whichever locals happen to be nearby.

## Recommendation

Ship `deadRoll` on its own — one derived value, all consumers gated, one site.
Hold `commit` for a ruling on what a rival committing dice means, because
guessing it would put a made-up payload on a real seam and nothing downstream
would flag it.
