# The Break rows — all six measured, 2026-08-03

**Result: the timing read is universal. Every family rewards holding the skull
for the last turn, and Obsidian — the only row that had a published finding — is
the WEAKEST case of it.**

Base `bea`, tier 4, N=2,000 per agent, one page load per family.

| family | naive win / bank | informed win / bank | timing delta | bust n → i |
|---|---|---|---|---|
| obsidian | 16.70% / 3,516 | 20.20% / 3,938 | **+3.50 pts / +422** | 32.7% → 23.3% |
| vagabond | 20.00% / 3,465 | 26.60% / 4,090 | +6.60 pts / +625 | 29.0% → 18.6% |
| jade | 18.75% / 3,474 | 25.95% / 4,259 | +7.20 pts / +785 | 26.6% → 15.7% |
| starstone | 13.75% / 3,126 | 21.00% / 3,948 | +7.25 pts / +822 | 33.4% → 19.5% |
| amber | 16.55% / 3,290 | 24.70% / 4,124 | +8.15 pts / +834 | 30.8% → 19.3% |
| silver | 13.75% / 3,186 | 22.45% / 4,020 | **+8.70 pts / +834** | 28.9% → 17.4% |

**Bank confidence intervals are separated for all six** — this is not noise.

## What is established

**1. Brief §4's timing finding generalises.** It was written from Obsidian
alone: breaking immediately is a net loss across a match, and the correct play
is a timing read. That holds for **every** family, by +625 to +834 bank.

**2. Obsidian is the weakest case of it.** +422 bank against +625 to +834 for
the other five. The row chosen to teach the mechanic demonstrates it less
clearly than any row it was generalised to — worth knowing if Obsidian is ever
used as the tutorial example.

**3. The mechanism is visible in the bust column.** Informed bust rate is lower
in every family (32.7 → 23.3, 30.8 → 19.3, and so on). Holding the skull means
not spending a die, and a fuller hand busts less. **The cost of breaking early
is not the row's payout — it is the die you no longer have.**

## What is NOT established, and why

**The naive-bank column does not rank row VALUE, and must not be read that way.**
The family die sits in the loadout for the whole match contributing its **family
trait**, not only its Break row. So `naive bank` mixes "what the row paid" with
"what having a jade/amber/silver die in hand is worth", and the two cannot be
separated from this design.

That matters because the ordering *looks* like a ranking and partly disagrees
with `breakRowValue`'s hardcoded guess (obsidian 5, vagabond 4, starstone 3,
amber 2, silver 1, jade 1) — measured naive banks put jade near the top and
starstone at the bottom. **That disagreement is not evidence about the rows**;
it is what you would expect when a trait is confounded with a payout. Isolating
row value needs a different design — same die in both arms, break fired or not.

**The timing delta is clean** precisely because both arms hold the identical
die. The only difference is *when* the skull is played, so the trait cancels.

## How this was got wrong first, twice

**Run one was void.** The break brand went **on** the family die — but Break
destroys one *other* die, and every other die was bone, so all six batches fired
the **mundane no-op row**. Six families measured, one row tested. *The tell was
`starstone` and `vagabond` returning byte-identical numbers.*

**Run two failed its own control.** Both arms were Gambler Greg, and Obsidian
came out **backwards**. The roster sweep showed why — same gear, same seed, only
the policy varying:

```
rita 15.8   carl 20.1   otto 28.1   bea 32.0   ned 33.2   randy 33.9
greg_naive 88.7    greg_informed 91.8
```

**A factor of three off every other agent, at 1% win against 18–21%.** That is
not a strategy being measured; it is a policy that cannot parse the mechanic — a
Break brand banks zero *and* removes a die, and threshold-1000 answers by rolling
dead hands. **Treat a factor-of-three outlier as an instrument question before a
balance one.**

**And that reframes the near-miss.** Under-sampling alone gives a *noisy result
in the right direction*; it does not give a confident wrong-direction one. A
policy that cannot play the mechanic does exactly that, **at any sample size**.
So the protection was never the confidence intervals — it was stopping to ask
why 89% bust looked wrong before trusting anything built on it.

## The memory wall, and the workaround

The pass could not be scaled at first: N=260 completed in 13s, N=800 never
finished, N=2,000 never finished even with the wait ceiling raised 60s → 300s.

**Diagnosed: ~46 KB retained per match, never released.** The limit is
**cumulative matches in a page load**, not batch size and not wall-clock — which
is why a 5× ceiling changed nothing. Measured in one page at increasing sizes,
ms/match is flat (3.96 → 4.42) and DOM nodes constant at 515, so it is neither
cost growth nor a DOM leak.

| run | matches | predicted heap | outcome |
|---|---|---|---|
| break rows N=260 | 3,120 | ~145 MB | completed |
| tier sweep | 7,040 | ~321 MB | completed |
| break rows N=800 | 9,600 | ~435 MB | failed |
| break rows N=2,000 | 24,000 | ~1,081 MB | failed |

**Workaround: one family per page load.** 4,000 matches, ~137 MB, 39s.

**The retention is still unfixed** and caps every future study, not just this
one. Worth finding.

## Reproduce

```bash
bash tools/run_break_rows.sh
```

~4 minutes, six page loads.
