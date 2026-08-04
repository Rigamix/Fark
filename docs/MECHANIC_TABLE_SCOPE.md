# The mechanic table — scoped before building

Ruled: build the `BREAK_TRIGGERS` equivalent for relics and materials. One keyed
table replacing scattered `effect.mechanic === '...'` branches.
`tools/mechanic_table.py` reruns this.

## 46 branches are 31 mechanics, and they split cleanly

**17 mechanics appear in exactly one function.** Straight table rows:
`wild_triple`, `wild_quad`, `wild_straight`, `triple_bonus`, `starstone_bonus`,
`swap_die`, `steal_die`, `reduce_first_roll`, `shatter_bonus`,
`reroll_scoring`, `reroll_all_kept`, `reckless`, `halve_big_bank`,
`hidden_cards`, `block_activations`, `limit_activations`, `immune_modifiers`.

**14 span several functions — and every one is the same pattern.**

| pair | what the two functions are |
|---|---|
| `finOpp` + `handleBank` | 9 mechanics — the **rival's** bank and the **player's** bank |
| `_tryBustSave` + `step` | `bust_immune_turns`, `bust_survive` — player bust save, rival bust save |
| `doBust` + `step` | `bust_bank_half` |
| `_oppBustOut` + `doBust` | `gain_pts`, `punish_busts` |
| `finOpp` + `handleBank` + `startPTurn` | `challenge` (3 sites) |

**Not one of the 14 is a semantic collision.** They are **player/opponent
mirrors** — the same effect written twice, once per side.

## Which changes what the work is

This was scoped expecting the Trade problem: names shared by things that are not
the same. That is not what is there. **It is the identical player/opponent
duplication the CFX bus exists to remove**, surfacing one layer down in the
materials system.

So the table is not only consolidation. A `mechanic`-keyed table that takes an
owner — the way `famFire` already passes `ev.owner` — collapses each pair to
**one row**, and the second copy stops being a place for the two sides to drift.
That drift is not hypothetical: it is exactly what `_npcFamCard` turned out to
be for the family cards.

## Order this suggests

1. **The 17 single-site mechanics first.** No open question, no mirror to
   reconcile, and it proves the table shape before the harder half.
2. **Then the 14 pairs, one at a time**, each read to confirm the two sides
   genuinely match before they collapse. A pair that has already drifted is a
   bug found, not an obstacle — but it must be found rather than merged over.

**Not started.** This is the scoping pass; the read of each pair is the next
thing.

---

# And `ill_omen`'s mirror is blocked on the same shape as `commit`

Ruled: mirror it, with trigger and payoff flipping together.

**The moment exists; the value does not.** A boss-held `ill_omen` pays when the
*player's* turn resolves — that is `endPTurn`. But `endPTurn` zeroes `G.turnPts`
on its first working line, the bust path clears it earlier still, and **nothing
marks whether the turn ended in a bank or a bust**. It has six call sites across
both kinds of ending.

So raising `rivalTurn` there needs a value — "what did the player score this
turn" — threaded from six places. That is the same shape as `commit`: the seam's
moment is findable, the seam's *payload* is not.

The ruling stands and is recorded. What it needs first is that value, which is
one scoping pass covering both `commit` and this.
