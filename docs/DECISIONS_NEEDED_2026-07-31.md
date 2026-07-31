# Decisions needed — the sim's leftovers

> **SUPERSEDED in part by `FEEL_2026-07-31.md`**, which reorders these by what
> a player actually runs into and adds the one this list MISSED — see below.
> The options and recommendations here still stand; read that document first.

**A CORRECTION.** This list said six. It should have said seven: **Starstone's
unconditional +500 per die on every bank** is blocker #3 of five in the sim
report and it is in none of the six items below. No commit closes it either, so
it fell out of the fix list and the decision list at the same time. It is the
single strongest thing in the game — two Starstone plus four bone wins 77.5% for
a completely RANDOM player against an all-bone baseline of 3.0% — and it makes
banking small and often the optimal line, which is the inverse of a
push-your-luck game. Written up as exhibit C of section 2 in FEEL_2026-07-31.md.

Six questions. Each one is a case where **the code does exactly what the spec
says and the spec is the problem**, so I can't fix them by reading harder — they
need your call. Recommendation given for each; say "your rec" and I'll take it.

Everything the sim found that was a genuine *bug* is already fixed and deployed
(icon sweep, Vagabond double-pay, Starstone's extra turn bypassing the cap).

---

## 1. Amber's Break makes a turn that never has to end

**The spec says this on purpose.** `FARK_ENCHANT_BADGE_REWORK.md` line 214:
"the current turn becomes bust-immune for its remainder — you may keep pushing
without risk until you choose to bank."

Read literally that is an infinite points machine, and the sim confirmed it:
asked for 20,000 points, **98.5% of immune turns were still running** when the
harness's own 60-roll guard stopped them. One Break on turn 1 takes a
near-starting loadout from 35.7% to 98.7%. A player who understands it never
banks, because they cannot lose.

Every other Break row is one-shot: +1000, one extra turn, one safe bank, one
reroll, one steal. Amber is the only one that grants an *ongoing state*.

**Options**

- **A — one bust, not every bust.** Amber eats the next bust, then it's spent.
  Still "temporary invincibility", still Amber's own verb, same shape as its
  five siblings. *Recommended.*
- **B — keep unlimited, add a hard cap.** e.g. immunity ends after 3 saves or
  at 2,500 turn points. Keeps the fantasy, bounds the exploit, but it's a
  number a player has to be told rather than a rule they can feel.
- **C — leave it.** It is a build-defining payoff you have to spend a die to
  get. But it is currently the strongest thing in the game by a distance.

---

## 2. Fair Trade → Break costs no die

`_removeDieAt`'s Fair-Trade branch hands the lane back to the benched die and
returns early — `matchDice` isn't spliced, `numDice` isn't decremented. **This
matches ruling #2 exactly.** The ruling is the hole.

So you borrow a die, Break the borrowed one, collect the guaranteed family
payout, and still have six dice. Whole matches, both arms firing Break about
once each: borrow-and-break **48.6%** at 6.00 dice; break-your-own **15.2%** at
5.00 dice.

**Options**

- **A — the loan can't be broken.** Break refuses a borrowed die outright.
  One line, no new state, and it reads as a rule ("you can't destroy what isn't
  yours"). *Recommended.*
- **B — breaking the loan ends it.** The lender's die is destroyed for real and
  you go to five. Costs a die, as intended, but the die belonged to someone else.
- **C — leave it**, and accept Break+Trade as the intended top build.

---

## 3. The six briefed brands are a net downgrade

Night-8 dice + badge + 3 tier-3 cards with **no brands** wins **99.0%**. The
identical build with the six briefed brands wins **81.0%**. Paired delta
**−18.0**, n=800.

Break alone accounts for −29.0 of it; playing the timing right returns +22.3.
So brands are *skill-gated to break even* while everything else in the shop is
an unconditional gain. The enchant layer is the one system that punishes you for
engaging with it.

**Options**

- **A — Break's cost is the problem, not brands generally.** Retune Break's
  price/downside so a naive player is roughly neutral and a good one is ahead.
  *Recommended* — it's the one row carrying the whole loss.
- **B — buff the other five** to compensate, leaving Break as the risky one.
- **C — accept it as a deliberate expert layer**, and make the tooltip say so.

---

## 4. The specced loadout costs more gold than the game pays out

Maxed loadout: **5,990g**. A *perfect* run earns **5,921g** lifetime, and only
**4,205g** before night 8. So the briefed build cannot be bought, ever, by
anyone.

Compounding it: **buying a die destroys that slot's brand with no refund**, so
the correct purchase order is dice-then-brands — which is exactly the order that
guarantees you never get round to brands. In practice a dedicated shopper
reaches **2.0 of 6** brands; jade2 gets bought in 2% of runs.

**Options**

- **A — refund the brand when its die is replaced.** Fixes the ordering trap on
  its own and is the fair reading of what the player bought. *Recommended,
  independent of the price question.*
- **B — raise payouts** so the lifetime curve clears ~6,000g.
- **C — cut brand prices.**

A + B is probably the real answer; A alone is worth doing regardless.

---

## 5. Still Waters isn't the counter the brief says it is

`FARK_ENCHANT_BADGE_REWORK.md` §3 states Still Waters hard-counters
Break+Obsidian. It doesn't, and it can't as written: hushing keys on a die
*having a brand*, and Break needs only **one** branded die anywhere. So the
cheapest build — Break on one die, plain Obsidian everywhere else — pays in
full **with the badge worn**. Measured: 200 driven breaks, all-branded → 1000
without badge / 0 with; one-branded → **1000 both ways**.

**Options**

- **A — hush by family, not by brand.** Still Waters silences the *family*
  effect whether or not the die is branded. Makes the brief's claim true.
  *Recommended.*
- **B — correct the brief** and let Still Waters be an anti-*enchant* badge only.

Cheap either way — but the doc and the code currently say opposite things, and
one of them has to move.

---

## 6. Difficulty stops climbing after tier 3

Night-1 win rate at tiers 3–7: **30.8 / 33.0 / 36.4 / 33.9 / 32.3** — flat
inside its own error bars. What actually changes is the *shape*: matches stop
being races and become 8-turn point comparisons. Cap-decided endings go
**0.3% at tier 0 → 85.5% at tier 7**, because patron targets climb 5,000 →
9,500 while opponent mean bank barely moves (4,473 → 6,220).

So tiers 4–7 aren't harder, they're **longer and more anticlimactic** — most
end on a scoreboard rather than someone reaching the target.

**Options**

- **A — raise NPC bank aggression with tier** instead of raising targets, so
  late matches stay races. *Recommended.*
- **B — lower late targets** to what an NPC can actually chase.
- **C — accept cap-decided endings as the late-game texture**, and give the cap
  a real presentation (a countdown, a final-round callout).

---

## Not a decision — a harness bug that invalidates numbers

`tools/sim_harness.js:249` writes `S.run._enchTradeV=2;`. The shipped
`_enchInit` legacy-Trade migration fires on `_enchTradeV!==1`, nulls every
`{t:'trade'}` brand and refunds 350g — and `newG` calls `_enchInit()`
unconditionally right after `buildLoadout`. **Every Trade measurement made with
the shared harness measured an empty lane**, and the gold curve is inflated by
the phantom refund. Fix is to write `1`. Anything Trade-related in
`SIM_RESULTS_2026-07-31.md` should be re-run before it is trusted.
