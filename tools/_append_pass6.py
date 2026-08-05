# -*- coding: utf-8 -*-
u"""Append the reading pass (6) to CARD_AUDIT.md and file the finding in OPEN.md."""
import io, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'docs', 'CARD_AUDIT.md')
s = io.open(P, encoding='utf-8').read()
assert 'Pass 6' not in s, 'already appended'

s = s.rstrip() + u"""

---

# Pass 6 - the reading pass. One real finding in 14 cards.

Everything mechanical was exhausted after pass 5. These 14 cards move dice or
gate activations, have no score or bank signature, and could only be checked by
reading each implementation against its own prose.

## Read and correct (13 cards)

| mechanic | cards | prose vs code |
|---|---|---|
| `steal_die` | `blessed_confiscation`, `royal_seizure` | `take_and_use` pushes to `matchOppDice` ("uses it"); `take_best` only splices ("you play with 5") |
| `swap_die` | `sticky_fingers_die`, `collateral_die` | `best_for_worst` swaps player's best for patron's worst; `downgrade_best` loops exactly **2** ("your TWO best") |
| `swap_best_to_3` | `grogs_bump`, `quick_hands` | `swapN:2` both; `swapTo` 3 vs 2 and `uses` 2 vs 1 - matching "→3 twice" and "→2 once" |
| `reduce_first_roll` | `mabels_pinch` | `chance:0.5` matches "Fifty percent". The 0.7 in the code is an unused fallback |
| `block_activations` | `the_sermon` | `turnCount % 4 === 0` - "every 4th turn" |
| `limit_activations` | `point_of_order` | `turnCount % 2 !== 0` blocks - "work every 2nd turn" |
| `immune_modifiers` | `family_crest`, `never_saw_a_robe` | restores the rung's own agg/chaotic/adaptive/minBank/diceStop |
| `hidden_cards` | `old_roads` | suppresses the mini-card render |

## THE FINDING: `reroll_all_kept` promises a reroll and delivers a wipe

**`blessed_dice` (Ambrose) and `crown_authority` (Whisper)** — tiers 7 and 6.

Their text, all three fields:
> "**Reroll** ALL your kept dice (once)"
> "forces you to **reroll** every die you selected — scoring or not"
> "the opponent must **reroll** every die they selected"

The entire implementation:
```js
G.kept=[];G.turnPts=0;
setStatusMsg(npc.name+' — KEPT DICE WIPED!','red');
SFX.bust(); Haptic.bust(); /* bust-shake on diceArea */
```

**There is no reroll anywhere in the branch.** It clears the kept dice, zeroes
the turn points, and plays the *bust* sound, the *bust* haptic and the bust
shake.

These are not the same effect. A reroll returns new values and a chance to keep
scoring; a wipe takes the dice **and** the accumulated turn score. Mid-turn on
800 kept points that is the difference between a gamble and a guaranteed loss.

**Note the inversion from `challenge`.** There the message lied and the code was
wrong. Here the code, the sound and the on-screen message all agree with each
other — **the card's own description is the outlier**, and it is the one thing a
player reads before deciding whether to fear the card.

**Needs a ruling, not a patch:** either the text becomes "wipes your kept dice
and turn points", or the implementation actually rerolls. Both are defensible
and they are very different cards.

## Where the audit ends

Six passes. **41 cards: 41 wired, 0 number mismatches, 23 direction-checked
branches with 0 wrong-way, 14 read by hand.** One finding, filed rather than
fixed.
"""
io.open(P, 'w', encoding='utf-8', newline='').write(s)

O = os.path.join(ROOT, 'docs', 'OPEN.md')
t = io.open(O, encoding='utf-8').read()
T = u"## Everything else you answered is now work, not a question"
assert t.count(T) == 1
t = t.replace(T, u"""## 8. `blessed_dice` / `crown_authority` say "reroll", the code wipes

Found by reading, in the card audit's last pass. Two top-tier cards (Ambrose,
Whisper) whose every text field promises a **reroll**:

> "forces you to **reroll** every die you selected — scoring or not"

The whole implementation is `G.kept=[]; G.turnPts=0;` plus the **bust** sound,
the **bust** haptic and the bust shake, with the message "KEPT DICE WIPED!".
**No reroll happens.**

A reroll returns new values and a chance to keep scoring. A wipe takes the dice
*and* the accumulated turn score — mid-turn on 800 kept points, the difference
between a gamble and a guaranteed loss.

**The unusual part:** the code, the sound and the in-game message all agree with
each other. The card's own description is the outlier — and it is the one thing
a player reads before deciding whether to fear the card.

**The ruling:** does the text change to "wipes your kept dice and turn points",
or does the implementation start actually rerolling? Both are defensible and
they are very different cards. Detail in `CARD_AUDIT.md` pass 6.

**Not blocking anything.**

---

""" + T)
io.open(O, 'w', encoding='utf-8', newline='').write(t)
print('pass 6 appended; OPEN.md 8 filed')
