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

## The blocker: this pass does not scale, and it fails as SILENCE

I tried to fix the sample size and could not. Measured:

| N | outcome |
|---|---|
| 260 | completes, ~13s |
| 800 | **never produces a result** |
| 2,000 | **never produces a result**, even at a 300s ceiling |

**N=260 finishes in 13 seconds and 3× that finishes never.** That is not a
linear timeout, so raising the wait does not fix it — I raised it from 60s to
300s and N=2,000 still failed. Something else caps this pass and I have not
diagnosed it.

**The failure mode is the dangerous part: it exits 0 with no `setup:` line.**
A capped run, a crashed run and a run with nothing to say are indistinguishable
from the outside. That is the same shape as the rest of this session's bugs —
a limit that expresses itself as absence.

**So the sample size is the blocker, and it is not a matter of patience.**
Diagnosing why the harness stops scaling is its own task and should come before
anyone promises Break-row numbers.

## What a real pass needs, once it can run

- **N in the low thousands** — currently impossible, see above.
- **A mid-table agent as well as Greg**, so the result is not read off the
  policy least able to win.
- **Explicit last-turn isolation.** The Obsidian finding quoted a single-turn
  comparison (1,140 vs 409). Naive-vs-informed approximates it across a whole
  match; it is not the same measurement.

**Nothing in this document should be used to tune a Break row.** The instrument
is right now; the run is not big enough.

## Reproduce

```bash
node tools/sim_run.js tools/sim_break_rows.js
```

~14 seconds at N=260.
