# The five unvalidated Break rows — instrument built, result NOT yet trustworthy

**Read the last section before quoting any number here.** The measurement runs
and differentiates the six families, but the sample cannot support the
conclusion it looks like it supports.

## Why this needed its own instrument

Brief §4's Obsidian result is a **timing** finding, not a power one: breaking
immediately is a net loss across a match, while on a turn with no future to
protect it flips hard positive. Amber, Starstone, Silver, Jade and Vagabond
have no numbers at all — they are design proposals.

Two choices make the pass measure the rows rather than the harness's opinion
of them:

**The family is forced, not chosen.** `breakTarget` picks by `breakRowValue()`,
which is a hardcoded guess — obsidian 5, vagabond 4, starstone 3, amber 2,
silver 1, jade 1. Selecting targets *by* that guess and then reporting row value
would measure the guess. Each batch holds exactly one non-bone die, so the
target is determined by construction.

**Naive vs informed is the whole instrument.** Those two agents differ in one
thing only — the informed one withholds the skull until the last turn — so the
gap between them is Break timing and nothing else, reproducing the shape of the
Obsidian finding rather than inventing a new metric.

## The first run was void, and the tell is worth keeping

I put the break brand **on** the family die. Break destroys *one other* die, and
every other die was bone — so all six batches fired the **mundane no-op row**.
Six families measured, one row actually tested.

**The tell was `starstone` and `vagabond` returning byte-identical numbers.**
Two different families cannot agree to three significant figures by chance.
Corrected: the brand goes on a bone die and the family die is the target.

## What the corrected run shows

Tier 4, N=260 per agent, six families, all six distinct.

| family | naive win / bank | informed win / bank | timing delta | guessed rank |
|---|---|---|---|---|
| obsidian | 2.3% / 1,430 | 0.8% / 1,302 | −1.5% / −128 | 5 |
| vagabond | 1.9% / 954 | 0.8% / 899 | −1.1% / −55 | 4 |
| amber | 0.4% / 707 | 0% / 700 | −0.4% / −7 | 2 |
| starstone | 0.8% / 689 | 0% / 700 | −0.8% / +11 | 3 |
| jade | 0% / 656 | 0.4% / 809 | +0.4% / +153 | 1 |
| silver | 0.4% / 634 | 0% / 770 | −0.4% / +136 | 1 |

**One observation is defensible.** The naive bank ordering — obsidian 1,430 >
vagabond 954 > amber 707 > starstone 689 > jade 656 > silver 634 — tracks
`breakRowValue`'s guessed ranking closely, and it does so **independently**,
because the family was forced rather than selected by that guess. Soft
corroboration that the hardcoded ordering is not badly wrong.

## Why the rest is NOT trustworthy — and this is the point

**The win-rate column is noise at this sample size.** At N=260:

- 0.4% is **one win**
- 0.8% is **two wins**
- 2.3% is **six wins**

A single match swings the rate by 0.38 points, so every "timing delta" in that
column is between one and four matches wide. The signs cannot be read.

**And the win rates are floored for a structural reason.** Both agents are
Gambler Greg (threshold 1,000), the roster's most reckless policy, at tier 4
where the tier sweep's four-agent mean was 8%. Greg alone lands near the bottom
of a 30.5-point spread. That is fine for an A/B where both sides are Greg — but
it puts the absolute numbers in a range where noise dominates.

**The bank deltas are the usable signal and are still thin.** −128 to +153 on
means of 634–1,430, from 260 matches.

## The scaling wall: DIAGNOSED

Not wall-clock. **~46 KB is retained per match and never released**, so the
limit is **cumulative matches in a page load** — which is why raising the wait
ceiling 60s → 300s moved nothing.

Measured in one page at increasing batch sizes: **ms/match is flat** (3.96 →
4.42, 1.12× across 100→600) and **DOM nodes are constant** at 515, so it is not
per-match cost growth and not a DOM leak. Heap goes 4.8 → 63.1 MB over 1,300
cumulative matches.

Extrapolated against every run whose outcome is known, the wall sits between
321 MB and 435 MB:

| run | matches | predicted heap | outcome |
|---|---|---|---|
| break rows N=260 | 3,120 | ~145 MB | completed |
| tier sweep | 7,040 | ~321 MB | completed |
| break rows N=800 | 9,600 | ~435 MB | **failed** |
| break rows N=2,000 | 24,000 | ~1,081 MB | **failed** |

**Workaround, proven:** run one family per page load. Obsidian at N=2,000 —
4,000 matches — completed in 17s at 137 MB, exactly as predicted.
`tools/sim_break_one.js` does this; the six-family pass is six invocations, not
one.

**The retention itself is still unfixed.** Something holds ~46 KB per match.
Finding and releasing it would remove the ceiling entirely and is worth doing
before any large study, not just this one.

## AND THE INSTRUMENT FAILS ITS OWN CONTROL — do not run the other five

Obsidian is the one row with a published result, so it was run first to test the
instrument rather than the row. **It does not reproduce the finding.**

| agent | win | bank | bust/turn |
|---|---|---|---|
| naive (break early) | 1.05% [0.69, 1.60] | 1,436 [1,400, 1,472] | 89.0% |
| informed (hold to last turn) | 1.00% [0.65, 1.54] | 1,325 [1,289, 1,362] | 91.7% |

Brief §4 says breaking immediately is a **net loss** across a match. This says
holding it is worse by 111 bank — and the bank confidence intervals **do not
overlap**, so that is a real difference in the **opposite direction** to the
published result.

**And the bust rate is 89–92% per turn**, which is not a plausible number for
any build. A silver hand busts ~26% of turns and an all-bone hand ~49%. An agent
busting nine turns in ten is not playing the game the finding was measured on.

So the instrument is measuring *something*, cleanly and repeatably, and it is
not the thing it claims. The likely cause is the agent: both sides are Gambler
Greg at threshold 1,000, and a Break brand that banks zero while removing a die
pushes an already-greedy policy into rolling dead hands. That is a setup fault,
not a finding.

**The five unvalidated rows should NOT be run through this instrument until it
reproduces Obsidian.** Running them would produce six well-formed tables of
numbers measuring the wrong thing — which is precisely the failure the void
first run already demonstrated once.

## What a real pass needs, once it can run

- **N in the low thousands** — now possible, one family per page load.
- **A mid-table agent as well as Greg**, so the result is not read off the
  policy least able to win.
- **Explicit last-turn isolation.** The Obsidian finding quoted a single-turn
  comparison (1,140 vs 409). Naive-vs-informed approximates it across a whole
  match; it is not the same measurement.

**Nothing in this document should be used to tune a Break row.** The sample
size is solved; the instrument is not — it fails its own control, in the
opposite direction, with an implausible bust rate underneath it.

## Reproduce

```bash
node tools/sim_run.js tools/sim_break_rows.js
```

~14 seconds at N=260.
