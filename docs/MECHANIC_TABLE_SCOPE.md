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

## The "owner signature" was my instrument's artifact — retracted

I reported that `npc` was the only local eight of the branches needed, called it
the same owner parameter the 16 mirrors need, and said two independent
investigations had converged on it. **That was wrong, and it was the headline.**

`npc` is not "which side". Every one of its fifteen binding sites is
`var npc=getNpcCard(cid)` — **the card object**, the loop binder over the boss's
card ids, exactly what `effect` is. My portability tool did not have `npc` or
`cid` in its given-set, so it counted **each row's own subject as an outside
dependency**. Eight unrelated branches then looked like they shared a parameter.

With `npc`/`cid` where they belong: **5 portable as-is** — `hidden_cards`,
`reduce_first_roll`, `reroll_all_kept`, `steal_die`, `swap_die`.

## What convergence is actually left, stated at its real strength

| cluster | shared locals | mechanics |
|---|---|---|
| `scoreRoll` | `eVals`, `i`, `wildLevel` | `wild_triple`, `wild_quad`, `wild_straight` |
| `_afterRollImpl` | `free` | `reroll_scoring`, `swap_best_to_3` |
| `canActivateCard` | `blocked` | `block_activations`, `limit_activations` |
| one-offs | private | `halve_big_bank`, `immune_modifiers`, `reckless`, `starstone_bonus`, `shatter_bonus`, `triple_bonus` |

**Each cluster is branches sharing their own enclosing function's locals** —
which is what you would expect by default, not evidence of a cross-cutting
concept. The `wild_*` trio is three variants of one scoring rule sitting
together. Real, but unremarkable. **There is no owner parameter.**

## So the honest answer to "can one table replace the branches"

**Five rows move cleanly. The rest are per-function clusters that each want a
small local dispatcher, not one shared table.** That is a smaller and duller
result than the three-shape version I reported, and it is what the evidence
supports once the tool stops counting subjects as dependencies.

The 16 player/opponent mirrors are still a real and separate finding —
unaffected by this, since it rests on which functions a mechanic appears in, not
on what its body reads.

## Order

1. **The 5 portable rows**, which are genuinely just data.
2. **The `scoreRoll` cluster**, self-contained and the largest real one.
3. **The mirrors**, on their own evidence, separately from any of this.

**Not started.** This is the scoping pass.

---

# `ill_omen`'s mirror is blocked on a missing value — see `OPEN.md` §5

The moment exists; the payload does not. `endPTurn` zeroes `G.turnPts` on its
first working line, the bust path clears it earlier, and nothing records whether
the turn ended in a bank or a bust. Six call sites across both endings. Same
shape as `commit`. The one open part is a design call, so it lives in `OPEN.md`.
