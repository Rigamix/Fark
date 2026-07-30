# Fark — second round of design questions

Everything here came out of *playing* the cards rather than reading them. Each
one blocks a fix: the bug is understood and the patch is small, but what the fix
should DO is a rules call.

Grouped by card. The physics question is last and is a different kind of question.

---

## FAIR TRADE

**1. A borrowed die gets shattered. What happens?**

Fair Trade lends you a die from your stash for a turn. If that borrowed die is
then destroyed mid-turn (Obsidian's shatter, Break), the game currently keeps a
note saying "return the die in lane 3" — and next turn it hands lane 3 back to
whatever die is standing there now, **destroying a die you actually own, for the
rest of the match.**

That has to change; the question is to what.

- **A. The loan is simply void.** The borrowed die is gone, nothing is returned,
  your own die comes back next turn as if the trade never happened.
- **B. You lose the die you lent against it.** The shatter costs you the stash
  die permanently — a real risk attached to borrowing.
- **C. The borrowed die cannot be shattered at all** — it is on loan, it is not
  yours to break.

*A is the safe reading. B makes the card a genuine gamble. C is the fussiest to
explain but the kindest.*

**2. Tier I and tier II are currently identical.** Tier I says the loan lasts
"for this roll only" and tier II says "for the turn" — but tier I's loan lasts
the whole turn too, so upgrading buys nothing. Should tier I really end at the
first roll (making it markedly weaker), or should the tiers differ some other way?

---

## STEADY HAND

**3. Should a reroll that lands on the same face say so?**

Steady Hand rerolls one die. If it comes up the same number, there is currently
no feedback at all — the tap reads as if nothing happened and the charge looks
wasted. Options: a small "same again" beat, a shake on the die, or leave it
(the die visibly tumbles, so the player can see it re-rolled).

**4. Can a die you have already selected be a Steady Hand target?**

Mechanically yes, but the gold selection paint hides the red target ring, so
there is no way to tell. Either the rings need to combine visually, or a
selected die should not be a legal target.

---

## PRESERVE

Preserve is built and passes 15 of 16 played routes, but is not in the game yet:
it needs two holes closed first (the amber die re-qualifies for Preserve, and
resume refunds the charge). Those are mine to fix. These two are not:

**5. Does busting crack the amber?** You arm Preserve, then bust that same turn.
Does the amber die still arrive next turn, or does the bust take it — losing both
the die and the charge? Currently it survives.

**6. Should the player choose which die goes into the amber?** The card takes the
first scoring die it finds. Letting the player tap the one they want is more
control and more taps; taking the first is simpler and occasionally annoying.

---

## ART

**7. Two family cards have no art** and paint as a browser broken-image glyph:
`steady_hand` and `fair_trade`. Unlike the main card renderer, the family-card
renderer has no fallback. Either the art, or I add the same self-removing
fallback the other renderer uses (colour swatch + emoji).

---

## THE THROW — a different kind of question

Not a rules call, but the trade needs a decision. Measured over 120 throws with
lanes held sacred:

| | time to rest | lands in lane | correction after landing |
|---|---|---|---|
| **now** | 1.55s | 88% | **1.944** |
| **aimed** | 1.52s | 85% | **0.000** |

The game currently *pushes* each die into its lane while it is landing. The
alternative is to throw each die repeatedly in secret — the whole flight is
computed before anything is drawn — and play back one that happened to land in
its lane on its own. Same speed, same accuracy, but nothing is ever pushed: every
frame the player sees is honest physics.

**8. Is a rare, visible correction acceptable in exchange for no correction at
all the rest of the time?** Neither approach is perfect on its own: aiming misses
the lane on about one throw in seven, so those few would still need a nudge. The
choice is between a small correction on *every* throw, or an occasional one on a
*few* — with the risk that a rare correction is more noticeable precisely because
it is rare.
