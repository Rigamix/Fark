# The patron card audit — pass 1: the cheap check is clean

41 cards went from provably-inert to live in one commit (P473). The difficulty
delta says they work **in aggregate**; an aggregate moving correctly is
compatible with individual cards being silently wrong in ways that cancel out.
None had been checked on its own.

Rerun with `tools/card_audit.py`.

## Result

| verdict | count |
|---|---|
| **UNWIRED** — mechanic/type with no dispatch anywhere | **0** |
| **MISMATCH** — a number in the text absent from the effect | **0** |
| `ok` — text numbers all backed by the effect object | 17 |
| NO NUMBERS — text promises no quantity | 24 |

**Every pooled card reaches a live dispatch, and every stated number is the
number the effect uses.** That is the whole automatable claim.

## What it does not claim

`ok` is necessary, not sufficient — a card can use its stated amount in entirely
the wrong direction and pass this. And **NO NUMBERS is a reading list, not a
pass**: 24 cards promise behaviour without a quantity (`steal_die`,
`reroll_all_kept`, `block_activations`…), and nothing mechanical can check those.
**That is where the remaining audit value is, and it is a reading task.**

## The tool produced six false findings first

It reported six MISMATCHes — `beginners_luck` "unbacked 200", `campaign_veteran`
"unbacked 0", and four more. Every one was the **thousands separator**: the card
text writes `1,200`, and a plain 2–6 digit match splits that into `200`;
`2,000` becomes `000` → 0.

**And the first fix silently did nothing.** It went through a bash heredoc, and
the `` in `\d{3}` was written as a **literal backspace byte**. The pattern
became `(?=\d{3}<BS>)` — which prints looking correct, matches nothing, and
leaves the false findings in place *while appearing repaired*. Three further
rounds of debugging chased a function whose printed source was right.

This is the second time tonight: `until_audit.py` invented eight false findings
by the same mechanism. There is a standing rule that backslash-containing
patches go through the Write tool rather than a heredoc. **The rule existed and
I skipped it.** The repair is now a plain `.replace(',', '')` with no escapes at
all, so there is nothing left for a quoting layer to corrupt.

**Worth noting what made it findable:** six mismatches with `500` unbacked in
four of them was too concentrated to be six independent bugs. The
suspicious-uniformity check caught it before it was reported as a finding.

---

# Pass 2 - quantities written as WORDS, which pass 1 could not see

Pass 1 compared **digits**. It classified 24 cards "NO NUMBERS" - but several
state a quantity in words, and a digit scan sees none of it:

| card | text | effect |
|---|---|---|
| `hold_the_line` | "first **two** turns" | `turns:2` |
| `sundays_rest` | "first **three** turns" | `turns:3` |
| `grogs_bump` | "**Twice** per match... **TWO** dice" | `uses:2, swapN:2` |
| `point_of_order` | "every **2nd** turn" | `interval:2` |
| `the_sermon` | "every **4th** turn" | `interval:4` |

**That was pass 1's blind spot, not a clean result** - "24 need reading" was
hiding a checkable subset. `tools/card_audit2.py`.

## Result: also clean

**22 cards carry a word-quantity. Every one matches its effect.** That includes
`hold_the_line` (2) and `sundays_rest` (3) - the exact pair P469 touched when it
fixed the `<=` / `<` off-by-one, now verified against their own text.

## Two instrument corrections, both caught before reporting

**Ordinals are not quantities.** "first two turns" means *two*; mapping `first`
-> 1 made `hold_the_line` read `[1,2]` and `sundays_rest` `[1,3]`, flagging two
correct cards. Removed - the ordinals that genuinely *are* quantities ("every
2nd turn") keep their entries.

**Prose can state a derived total.** `grogs_bump` says *"Four dice ruined over a
match"* - that is `swapN:2` x `uses:2`, a consequence rather than a parameter.
The tool still flags it and this note explains why it is benign; special-casing
it would hide a future real mismatch behind the same shape.

## Where the audit stands

**Every mechanically checkable claim across all 41 cards holds** - wiring, digit
quantities, word quantities. What remains needs reading and cannot be automated:
**direction** (does it take from the right side), **ownership** (does the
player's copy mirror the boss's), and whether the effect does the *right thing*
with the right number. Two passes shrank the list; they did not replace it.

---

# Pass 3 - DIRECTION and OWNERSHIP: does a card benefit its holder?

Passes 1 and 2 checked that stated numbers are the numbers used. Neither can
check whether the effect moves them the RIGHT WAY - and that is exactly where
tonight's two real bugs lived: `challenge` charging the rival twice, and
`ill_omen` reading "busted" on one seat and "scored nothing" on the other.

**Direction is not purely a reading task.** Whose card it is comes from the
enclosing loop (`G.oCards` / `G.pCards`, by brace extent); who gains comes from
which pool the branch credits. `tools/card_audit3.py`.

## Result: 13 attributable branches, 0 pointing the wrong way

| mechanic | patron's copy | player's copy |
|---|---|---|
| `gain_pts` | +patron | +player |
| `steal_pct` | +patron | +player |
| `steal_low_bank` | +patron | +player |
| `punish_busts` | -player | -patron |
| `periodic_drain` | -player | -patron |
| `challenge` | -player | -patron |
| `bust_bank_half` | - | +player |

**Every mechanic present on both seats inverts correctly.** `bust_bank_half`
appears once because its patron-side occurrence is a query, not a dispatch -
established in pass 1 of the bust-mirror work.

## Coverage, stated rather than implied

**15 branches touch a score pool. 13 sit inside an identifiable card list** and
all 13 point correctly. The other 2 are not inside a card-list loop, so
ownership cannot be attributed mechanically - they are not passes, they are
out of this instrument's reach.

## The instrument was blind to three branches, all from tonight's own refactors

The first run classified 10 of 15. The three it missed were
`SCORE_DRAIN.periodic_drain(...)` (twice) and P467's rewritten `challenge`
deduction - **code refactored earlier tonight**. Moving arithmetic into a table
row is cleaner and simultaneously stops the sign LOOKING like a `+=` or `-=`.

Worth keeping: **a refactor can blind a checker that was reading the old shape**,
and the honest fix is to teach the tool the new form rather than report 10 and
call it 15.

## What is still genuinely a reading task

Magnitude sensibility, whether each trigger condition matches its prose, and the
~17 cards that move **dice** rather than points - rerolls, swaps, seizures.
Three passes have shrunk the list to those; none of them replaces reading it.

---

# Passes 4-5 - the BANK-modifying branches, which pass 3 was blind to

Pass 4 set out to scope the ~17 dice-moving cards. **Its first cut mislabelled
five mechanics as dice-movers** - `flat_bonus`, `double_first_bank`,
`gain_when_ahead`, `halve_first_bank`, `halve_big_bank`. They move no dice at
all. They change `total` / `pts` - **the bank** - and the money reaches a score
pool *outside the branch*, so pass 3's `G.pPts` / `G.oPts` regex never saw them.

**Ten branches had gone unchecked for direction**, and four now route through
the `BANK_FX` table built earlier tonight, so the arithmetic no longer looks
like arithmetic at the call site either.

## The invariant needs the enclosing FUNCTION, not just the card list

The function decides whose bank is on the table:

| | in `handleBank` (player's bank) | in `finOpp` / `_oppFx*` (patron's bank) |
|---|---|---|
| **patron's card** | lowers | raises |
| **player's card** | raises | lowers |

## Result: 10 branches, 0 helping the wrong side

Every one matches the table above. Combined with pass 3, **23
direction-checked branches and none pointing the wrong way.**

## The refactor blindness fired three times, the third inside the tool checking for it

1. **Pass 3**: `SCORE_DRAIN.periodic_drain` and P467's rewritten `challenge`
   stopped looking like `+=` / `-=`. 10 of 15 classified.
2. **Pass 4**: five bank-modifiers had no score-pool signature at all and were
   filed as dice-movers.
3. **Pass 5**: `span_of('finOpp')` reported five of ten branches as `(other)` -
   because **P470 extracted `finOpp`'s loops into `_oppFxOwnA/B/Player/Drain`
   earlier tonight**. The tool written to catch refactor blindness was blinded
   by the same refactor.

Kept rather than quietly fixed, because all three were found only by looking at
coverage rather than at the verdict column. **A clean "0 wrong" from a checker
that can see two thirds of its subject is not a result.**

## One more thing worth recording

Pass 5's first draft printed a hardcoded `ok` verdict column - a display, not a
check. It was replaced with a computed one before any result was reported. That
is precisely the failure this audit exists to find, produced by the audit.

## What is still a reading task

The genuine dice-movers - `steal_die`, `swap_die`, `swap_best_to_3`,
`reroll_all_kept`, `reduce_first_roll` - plus the activation controls
(`block_activations`, `limit_activations`, `immune_modifiers`) and
`hidden_cards`. Those have no score or bank signature, and whether they touch
the *right dice* cannot be inferred from shape.

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
| `quick_hands` | `swap_best_to_3` | `once` | absent | `eff.uses\|\|1` |
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
