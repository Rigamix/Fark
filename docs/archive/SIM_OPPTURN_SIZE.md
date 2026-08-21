# Sizing the sim's opponent-turn fix — smaller than it looked

Ruled: build it. The sim's `F.oppTurn` reimplements the opponent's turn loop and
never runs `finOpp`'s nine card branches.

## First, a correction to how I described the gap

I reported this as *"a patron that punishes the player but structurally cannot
help itself"*, and escalated it on that basis. **The direction is wrong.**

`finOpp` iterates **both** card lists — every bank fires the banker's own cards
*and* the opponent's, symmetric with `handleBank`. The nine split:

| list | mechanics | favours |
|---|---|---|
| `G.oCards` — the patron's own | `flat_bonus`, `double_first_bank`, `gain_when_ahead` | **the patron** |
| `G.pCards` — the player's | `steal_pct`, `steal_low_bank`, `block_low_bank`, `challenge`, `halve_first_bank`, `periodic_drain` | **the player** |

All six player-held ones take from the patron's bank or score. So the sim omits
**three patron-favouring effects and six player-favouring ones** — by count it
understates **the player** more than the patron.

**The stop stands; my reason for it did not.** No bank-triggered card effect
fires during the patron's turn, for either seat, so the sim measures a game
where that whole layer is absent. What cannot be claimed is that this biases
difficulty in the patron's favour — the omitted effects lean the other way.

I got this wrong by reading `finOpp` as "the patron's function" and assuming the
cards it iterates are the patron's. That is the same
nearest-thing-in-the-window mistake as the card-id attribution, on ownership
this time.

Rerun with `tools/sim_oppturn_size.py`.

## The measurement, and the correction inside it

The question was never "how many lines" — it was **why `finOpp` was
reimplemented**, since that reason is the work. The harness says `runOppTurn` is
"an animation chain end to end", so the suspected blocker was presentation
braided into the state changes.

| unit measured | braided statements | branches needing a split |
|---|---|---|
| **lines** (first pass) | 45 | 2 of 9 |
| **statements** (correct) | **3** | **0 of 9** |

The line-level pass counted `pts=BANK_FX.flat_bonus(pts,eff);triggerCard(...)`
as braided. That is **two statements sharing a line**, trivially separable — JS
separates statements with `;`. Measuring the wrong unit overstated the work by an
order of magnitude, and it is the same proxy mistake as the rest of tonight, on
the unit of measurement this time.

## What that means for the approach

**All nine card branches are cleanly separable today.** The state changes and
the presentation are already distinct statements; nothing needs untangling
first. `finOpp` is 504 statements, only ~130 of which touch state — and **the
sim does not need `finOpp`, it needs the card-effect portion of it.**

So the shape is the one already used five times tonight, one level up:

> **Extract the branches into shared functions that both `finOpp` and
> `F.oppTurn` call**, one per existing call site. The rule moves; the
> presentation stays at the call site.

**Four call sites, not one** — the branches are not contiguous. They span 24% to
94% of a 30,000-character function, interleaved with short-pour and
taxing-breath logic, and `periodic_drain` runs *after* `G.oPts += pts`:

| construct | mechanics |
|---|---|
| `G.oCards.forEach` [7049..8433] | `flat_bonus`, `double_first_bank` |
| `G.oCards.forEach` [8489..8866] | `gain_when_ahead` |
| `G.pCards.forEach` [10159..12842] | `steal_pct`, `steal_low_bank`, `block_low_bank`, `challenge`, `halve_first_bank` |
| `G.pCards.forEach` [28233..28582] | `periodic_drain` — **after the bank lands** |

**Mirror the existing structure rather than reorganising it.** Making the nine
contiguous would mean moving code across the point where the bank lands, which
is real behavioural risk for no gain.

**And `FSIM.quiet()` needs extending.** It stubs 11 functions but not
`triggerCard`, `setStatusMsg`, `famLog` or `updHUD` — the four the branches call
most. `setTimeout` is stubbed, so deferred `DLG` work already cannot fire, but
those four would do real DOM work in every simulated match.

That is meaningfully smaller than "route the sim through real game logic". The
turn *loop* stays reimplemented — it is genuinely an animation chain with timers,
and that was a sound decision. Only the **effects** move.

## What still has to be decided during the build

1. **Presentation suppression.** `FSIM.quiet()` exists; whether it already
   silences `triggerCard`/`spawnPop` or needs extending is unmeasured.
2. **Ordering.** `finOpp` applies card effects at a specific point relative to
   its other logic (reckoning, short pour, silver tongue — 3 genuinely braided
   statements, none of them card branches). The extracted function must be
   called at the same point in both, or the sim measures a different game again.
3. **A before/after.** Patron strength will rise once its cards work. That is
   the correction, not a regression — but it must be measured on the same seeds
   so the change is attributable, given `OPEN.md` §6 already records two
   difficulty changes landing on one axis without separation.

**Not started.** This is the sizing pass, and its result is that the job is a
shared-function extraction rather than a rewrite.
