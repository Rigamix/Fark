# The control arm, made exhaustive — and what it corrected

P481 landed `_legalKeeps` deliberately inert so the persona CHOICE could be a
separate change with its own before/after. That inertness is the **tier-0
control** for the difficulty measurement that follows, not tidy sequencing —
without it, any delta carries the unstated assumption that enumeration
introduced nothing on its own.

Which makes it worth more than one sample. It had one.

## What P481's control actually checked

```js
v.bestMatchesMaximal = !!(K.length && r && K[0].pts === r.total);
```

**One dice set** — `[5,5,5,2,3,4]` — and **points only**. Two gaps, both
load-bearing:

1. **One sample is not a baseline.** A 6-die bone roll has 462 distinct
   multisets; every size 1..6 together is 923. The whole space is cheap.
2. **Points are not the keep.** `_legalKeeps` sorts by points descending, so
   `K[0]` is *a* maximal-points candidate. Two candidates can score identically
   while keeping a different **number of dice** — and the leftovers are what get
   rerolled. Same points, different dice is a real behaviour change that a
   points-only check calls inert.

## The exhaustive result

`tools/apv_keep_control.js`, every roll of 1–6 bone dice:

| | |
|---|---|
| scoring rolls swept | **852** |
| points disagree with `used[]` | **0** |
| **dice count disagrees** | **0** |
| top candidates tied at same score | 7 |
| …of those, distinct keeps **by value** | **0** |

So routing the NPC's keep through `_legalKeeps` and taking `K[0]` reproduces the
old `used[]` keep exactly, on dice as well as points, everywhere.

## Two things the sweep corrected, both mine

**I predicted ties would be common and was wrong.** The reasoning was that
keeping `[5,2]` should score 50 — same as `[5]` alone but holding one more die —
giving a same-points/different-size tie. Measured: `scoreSelection([5,2])`
returns **-1**. The scorer rejects any keep containing a non-scoring die, so
`_legalKeeps` drops it at `if(pts<0) continue`. Every candidate is an all-scoring
subset, the maximal one is the full set of scoring dice, and every proper subset
scores strictly less.

That makes zero ties a **property**, not a blind detector — and it was confirmed
as such rather than assumed: `probe_tie_check.js` fed the tie test a hand-built
same-points/different-size list and it fired.

**Then the corrected assertion failed, and the failure was informative.** The
original `tieRuleIsExplicitNotSortOrder = true` was hardcoded — a verdict key
that cannot fail, which is exactly the lying-suite shape the runner's own header
warns about. Replacing it with the real claim `topCandidateIsUnique` produced an
immediate **FAIL**: 7 of 852 rolls do have several candidates tied at the top.

`probe_tie_check2.js` resolved it — all 7 are index-distinct but **value-identical**
(which of three matching 1s to keep), and **0** are distinct keeps by value. So
the keep is determinate even where the index-subset is not, which is the property
inertness actually needs. The assertion is now
`topKeepIsDeterminateByValue`, and it passes.

A tautology asserted nothing; the real assertion found my model of the data was
slightly wrong within a minute of being written.

**Stated limit — and it turned out to be the load-bearing one.** The sweep is
all-bone, with `cards=[]`. Closing it found that routing is **NOT inert** when
the rival holds a wild: 38 point-divergences and 7 dice-divergences across the
462 rolls containing a jade 6, worst case `23456` scoring 50 against 750.

So the conclusion below holds **for bone only**. See `WILD_SEAT_ASYMMETRY.md`
and `OPEN.md` 11 - the wiring is blocked on that ruling, not on the persona
policy. A limit written down is not the same as a limit checked; this one sat
in the doc for exactly one commit before it mattered.

## What this hands to the persona work

The maximal keep is always the full set of scoring dice, and it is unique. So
**choosing is necessarily choosing to score less now** in exchange for more dice
left live. There is no free variation among equal-value options — the personas
trade points for rerolls, or they take the maximum.

Concretely, `[1,1,1,5]` offers: 1050 (0 dice left), 1000 (1 left), 250 (1 left),
200 (2 left), 150 (2 left), 100 (3 left), 50 (3 left). A "keep the fewest dice
that still score" persona takes **50 and rerolls three**, against a maximal
persona's **1050 and rerolls none**. The lever is very strong, which is an
argument for picking the first policy carefully — see `OPEN.md` §10.
