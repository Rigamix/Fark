# The mechanic table — scoped before building

Ruled: build the `BREAK_TRIGGERS` equivalent for relics and materials. Rerun
with `tools/mechanic_table.py` and `tools/mechanic_portable.py`.

**An earlier version of this file said 46 branches / 31 mechanics and "17
straight table rows". Both were wrong, and both were my instruments' fault.**
Corrected below, with what caused each.

## 51 branches, 34 mechanics

The first count used `[a-z_]+` for a mechanic name — **a character class
narrower than the names it was matching**. `single1_bonus`, `single5_bonus` and
`swap_best_to_3` were invisible to it. That is a false negative: it does not
look wrong, so nothing prompts a second look.

## The 14 multi-function mechanics are player/opponent mirrors

Every one is an opponent function paired with its player equivalent:

| pair | what the two functions are |
|---|---|
| `finOpp` + `handleBank` | 9 mechanics — the **rival's** bank and the **player's** bank |
| `_tryBustSave` + `step` | `bust_immune_turns`, `bust_survive` |
| `doBust` + `step` | `bust_bank_half` |
| `_oppBustOut` + `doBust` | `gain_pts`, `punish_busts` |
| `finOpp` + `handleBank` + `startPTurn` | `challenge` |

**Not one is a semantic collision.** This was scoped expecting the Trade problem
— names shared by things that are not the same — and it is the opposite: the
same player/opponent duplication the CFX bus exists to remove, one layer down.
That drift is not hypothetical; it is what `_npcFamCard` turned out to be.

## "17 straight table rows" was the wrong evidence for the claim

A site count answers *where* a mechanic appears. It says nothing about whether
the branch **body** can leave the function it sits in — and that is what decides
if a row is possible. Measured (`mechanic_portable.py`): **2 of 18 are portable
as-is.** `hidden_cards`, `reduce_first_roll`.

The first run of that tool said 16 needed heavy threading, some reading ten
locals. **That was also wrong** — it counted each branch's own scratch
variables (`_sbN`, `_dgI`, `_ofx`) as outside dependencies, because JS `var`
hoisting puts them in the function scope and the check could not tell them from
real ones. Subtracting the body's own declarations is the corrected measure.

## What the corrected column actually shows: three dispatcher shapes

| shape | signature | mechanics |
|---|---|---|
| **owner** | `(effect, npc)` + optional flag | `reroll_all_kept`, `steal_die`, `swap_die`, `block_activations`, `limit_activations`, `reroll_scoring`, `swap_best_to_3`, `halve_big_bank` |
| **scoring** | `(effect, eVals, i, wildLevel)` | `wild_triple`, `wild_quad`, `wild_straight`, `triple_bonus` |
| **one-offs** | private | `immune_modifiers`, `reckless`, `shatter_bonus`, `starstone_bonus` |

**`npc` — which side — is the only local eight of them need.** That is the same
owner parameter the 14 mirrors need, arriving from a second, independent
direction. The three `wild_*` mechanics need an *identical* trio, which is a
signature rather than a coincidence.

## So the honest answer to "can one table replace the branches"

**Not one. About three — and that is still the right move.** `BREAK_TRIGGERS`
gets one table and two dispatch sites; this gets three, against fourteen
functions today. What it buys is the same thing: no branch reads a mechanic
name, and each player/opponent pair stops being two copies free to drift.

## Order

1. **The owner-shaped group**, because `npc` is already the parameter the
   mirrors need — the two halves of this refactor share a signature.
2. **The scoring group**, self-contained inside `scoreRoll`.
3. **The one-offs last**, or never — four branches in four functions is not
   obviously worth a row each.

**Not started.** This is the scoping pass.

---

# `ill_omen`'s mirror is blocked on a missing value — see `OPEN.md` §5

The moment exists; the payload does not. `endPTurn` zeroes `G.turnPts` on its
first working line, the bust path clears it earlier, and nothing records whether
the turn ended in a bank or a bust. Six call sites across both endings. Same
shape as `commit`. The one open part is a design call, so it lives in `OPEN.md`.
