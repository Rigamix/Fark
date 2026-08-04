# P5's other half — the opponent already holds cards, and none of them work

`tools/opp_cards_fire.py` reruns this.

## Two stale beliefs, both corrected by reading

**`PROTO_NOTES` says NPC usage lands in P5 with "G.oF stays []".** It doesn't.
`_famInitOpp(rung)` is implemented and deals a boss **1–3 family cards** from
its own family (`BOSS_FAM`), scaling with the night: one card, two from night
4, three from night 7. `G.oF` is populated at match init, line ~22640.

**So the opponent HAS cards.** The question was never whether to give it any.

## Every passive effect the opponent holds is inert

`famFire` iterates `['p','o']`, so an opponent card's hooks are visited. What
happens then turns on one helper:

```js
function _fxMine(ev){return !!(ev&&ev.mine&&ev.owner==='p');}
```

A hook gated on `_fxMine` returns immediately for an opponent-owned card.
Measured across all 44 hooks in `CFX`, restricted to the **passive** ones —
the hooks `famFire` fires for both sides, as opposed to `canUse`/`use`, which
only run when the player taps:

| | count | |
|---|---|---|
| **player-only** | **15** | `bloom.commit`, `cultivate.commit`, `double_or_nothing.bank`, `falling_star.bank`, `fools_gold_f.bust`, `fools_gold_f.deadRoll`, `ill_omen.rivalTurn`, `pickpocket.bank`, `reprisal.bank`, `retort.bust`, `short_fuse.bust`, `short_fuse.commit`, `slow_cook.bankBonus`, `slow_cook.roll`, `vanguard_f.commit` |
| owner-aware | 3 | `short_fuse.turnStart`, `slow_cook.bust`, `slow_cook.turnStart` — all state **resets**, not effects |
| ungated | 0 | |

**15 of 15 real effects are player-only.** A boss is dealt cards, the player is
shown them, and not one of them does anything.

## This is a design question, not a wiring job

Making a hook owner-aware is not `_fxMine(ev)` → `ev.mine`. Each needs a
decision about what the opponent's version *means*:

- **`pickpocket.bank`** lifts points from the rival on bank. Opponent-side that
  is the boss lifting from the player — symmetric, and probably fine.
- **`ill_omen.rivalTurn`** is declared on your turn and pays on the rival's. For
  an opponent-held copy, "the rival's turn" is the **player's** turn. The seam
  exists; which side it fires on is a rule.
- **`double_or_nothing.bank`** already has an NPC implementation elsewhere, in
  the `_npcFamCard` block — so making the CFX hook owner-aware would give the
  boss the effect **twice**.
- **`fools_gold_f.deadRoll`** claims the roll and cancels a bust. An opponent
  claiming its own dead roll changes NPC turn pacing, which the sim is tuned
  against.

That last pair is the reason this is not a sweep: `_npcFamCard` is a **second,
already-live opponent implementation** for `slow_cook`, `retort`,
`double_or_nothing` and `pickpocket`. Any card migrated onto the bus for the
opponent has to be removed from there in the same move, or it fires twice.

**Needs a ruling before building.** In `OPEN.md`.
