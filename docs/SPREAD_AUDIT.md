# Where else has `spread` been trusted? Audited — one claim, not many

Asked after finding that `spread` (max − min win% across agents) discards all but
two data points by construction. That was true of every prior measurement too,
so: what else rests on it?

**Four documents use it. Three are safe. One is not, and it is the one already
flagged.**

## The metric fails in exactly one regime

`max − min` is fine for two kinds of claim and bad for a third:

| claim shape | is `spread` sound? | why |
|---|---|---|
| "these are **equal**" (small spread) | **yes** | noise can only *widen* max−min, so a small one is strong evidence of equality |
| "this **collapsed hugely**" (34.8 → 4.3) | **yes** | the effect dwarfs any plausible noise |
| "this moved **a bit**" (6.2 points) | **no** | the same regime where noise is 8–14 |

## The four documents

| doc | claim | verdict |
|---|---|---|
| `archive/FEEL_2026-07-31.md:62` | humanlike agents spread **4.1** at n=800 → "honest playstyles are genuinely equal", a standing ruling | **safe** — argues equality *from* a small spread, the regime where the metric is strongest. n=800 gives ±3.5 per agent, so 4.1 is indistinguishable from 0, which is what it concluded |
| `archive/SIM_RESULTS_2026-07-31.md:63` | roster spread **34.8 → 4.3** with Starstone → "it stops mattering who is playing" | **safe** — a 30-point collapse is far outside any noise band |
| `archive/FEEL_2026-07-31.md:147` | same 34.8 → 4.3 | **safe**, same reason |
| `AGGRESSION_2026-08-03.md` | fall **32.1 → 25.9**, a 6.2-point improvement | **unsound** — already retracted in `AGGRESSION_REMEASURE.md` |

**Nothing else needs revisiting.** The archived rulings happen to sit in the two
regimes where a brittle max−min still works, and it is worth saying *why* rather
than just clearing them: they argue equality or a landslide, never a nudge.

## One thing nobody should do, which is not yet written down anywhere

**A 4-agent spread and an 8-agent spread are not comparable numbers.**
`max − min` grows with sample count even when the underlying distribution is
identical — more draws means a more extreme best and worst. `sim_tier_sweep`
uses **four** agents; the 34.8 / 4.3 figures come from **eight**.

So the aggression document's per-tier spreads and the archived roster spreads
must never be read on the same axis, and any future run that changes the agent
count breaks comparability with everything before it. That is not a flaw in the
old numbers; it is a trap for the next person who puts them in one table.
