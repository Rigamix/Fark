# Sizing the sim's opponent-turn fix — smaller than it looked

Ruled: build it. The sim's `F.oppTurn` reimplements the opponent's turn loop and
never runs `finOpp`'s nine card branches, so it models a patron that punishes the
player but structurally cannot help itself.

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

> **Extract the nine branches into a shared `_oppBankEffects(pts, …)` that both
> `finOpp` and `F.oppTurn` call.** The rule moves; the presentation stays at the
> call site, suppressed in the sim by the `FSIM.quiet()` flag that already
> exists.

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
