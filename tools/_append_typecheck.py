# -*- coding: utf-8 -*-
u"""Append the type-vs-uses finding to CARD_AUDIT.md and file it in the backlog."""
import io, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'docs', 'CARD_AUDIT.md')
s = io.open(P, encoding='utf-8').read()
assert 'decorative `type`' not in s, 'already appended'

s = s.rstrip() + u"""

---

# Follow-up: `type:'once'` is decorative on 11 of 14 cards

Prompted by asking whether `quick_hands` and `grogs_bump` sharing
`_sb3MaxUses` was the same shape as the `gain_pts` / `punish_busts` shared
defaults. **It is not** - `_sb3MaxUses` is a per-card local computed from that
card's own `eff.uses` inside the `G.oCards.forEach`. But the question found
something adjacent and wider.

## The measurement

**14 pooled cards declare `type:'once'` or `type:'twice'`. Only 3 have that
`type` gated anywhere** - `challenge` (×2) and `steal_low_bank`. For the other
**11**, nothing reads it for their mechanic:

| card | mechanic | type | uses | enforced by |
|---|---|---|---|---|
| `grogs_bump` | `swap_best_to_3` | `twice` | **2** | `uses` - `type` ignored |
| `quick_hands` | `swap_best_to_3` | `once` | absent | `eff.uses\\|\\|1` |
| `blessed_dice`, `crown_authority` | `reroll_all_kept` | `once` | absent | a boolean `usedOnce` flag |
| `blessed_confiscation`, `royal_seizure` | `steal_die` | `once` | absent | boolean flag |
| `collateral_die`, `sticky_fingers_die` | `swap_die` | `once` | absent | boolean flag |
| `iron_gate_npc` | `steal_on_bust` | `once` | absent | boolean flag |
| `one_more_round` | `bust_survive` | `once` | absent | boolean flag |
| `the_last_stitch_npc` | `bust_bank_half` | `once` | absent | boolean flag |

## Why it is worth recording

**Nothing is wrong today** - every `type` agrees with what is actually enforced.
The problem is that `type` **reads as authoritative and is not**.

`grogs_bump` is the sharpest case: it carries `type:'twice'` *and* `uses:2`, two
fields for one fact. Rebalancing it from twice to once by editing the obvious
one - `type` - **would change nothing**, and the card would keep firing twice
while its data says once. That is the same latent-drift class as the `||500`
defaults folded into `BUST_FX`, one field over and across eleven cards instead
of two.

## Not fixed here

Two defensible directions and they are not equivalent: **enforce `type`** (it
becomes the single source and `uses` goes away), or **remove it** from cards
whose mechanic ignores it (the boolean flag becomes the honest single source).
Backlogged rather than chosen.
"""
io.open(P, 'w', encoding='utf-8', newline='').write(s)

B = os.path.join(ROOT, 'docs', 'AUDIT_BACKLOG.md')
t = io.open(B, encoding='utf-8').read()
T = u"## Open, low-stakes"
assert t.count(T) == 1
t = t.replace(T, T + u"""

- **`type:'once'` is decorative on 11 of 14 pooled cards.** Only `challenge`
  and `steal_low_bank` gate on `effect.type`; everywhere else the use-count is
  enforced by `eff.uses||1` or a boolean flag, and `type` is never read.
  Nothing is wrong today - all 14 agree - but `grogs_bump` carries
  `type:'twice'` **and** `uses:2`, so rebalancing it via the obvious field would
  silently do nothing. Either enforce `type` or drop it from the mechanics that
  ignore it. Same latent-drift class as the `||500` defaults. See
  `docs/CARD_AUDIT.md`.""")
io.open(B, 'w', encoding='utf-8', newline='').write(t)
print('type-vs-uses finding appended and backlogged')
