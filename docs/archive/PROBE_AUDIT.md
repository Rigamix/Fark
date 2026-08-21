# Probes that verify less than their name claims

Standing audit item, opened after three separate checks stayed green through the
exact failures they existed to catch.

## Why this is its own class of bug

A failing check announces itself. A check that **asks a narrower question than
its name** passes forever while the thing it is named for breaks. Three
confirmed instances, all in one stretch:

| check | claimed | actually verified | what got through |
|---|---|---|---|
| `rivalSeatWorks` | the rival seat works | `.length > 0` | anything, as long as it returned an array |
| `straightsProtectsAFive` | the policy is right | `runLen>=5` when a five exists | trading a **complete** six-run (1500) for 750 |
| `triplesPrefersATriple` | the policy is right | `isTriple === true` | keeping six 1s as a bare 1000, **-7000** |

The last two were green through both persona bugs. What caught all three was
reading the **trades** — not the verdicts, and not the aggregate deltas.

## And the audit's first instrument had the same flaw

A regex scan for weak *syntax* (`= true`, `typeof … === 'function'`, `.length >
0`) flagged 7 of 151 assertions, nearly all `_`-prefixed diagnostics that never
reach a verdict. It found almost nothing, because the failure mode is
**semantic**: the gap is between a name and a meaning, and no pattern match sees
that. Recorded because it is the same shape as the bug it was hunting.

The scan that worked compared **name strength** (does it contain Works /
Correct / Matches / Applies / Fires) against **expression strength** (does it
ever compare two computed values).

## Repaired

- **`rivalSeatWorks` → `rivalSeatEnumeratesCorrectly`.** Now asserts every
  candidate scores, every candidate is a real subset of the dice handed in,
  every `left` is consistent, and the best equals the scorer's own maximal for
  that seat. It passes — the seat was in fact correct, which is exactly why the
  weak version survived so long.
- **`drainSafe` → `drainDoesNotThrow`.** The check is `try { … } return true`.
  That is not safety: it passes on a drain that silently does nothing or drains
  the wrong seat. Strengthening needs facts about what drain *should* do that
  have not been measured, so the **name** was narrowed to what is verified
  rather than left overclaiming. Closing the gap by narrowing the claim is a
  real fix; leaving a name that promises more is not.

## Repaired in the second pass (P503) — and the fix was renaming, on evidence

Filed rather than patched under pressure, and resolving them properly needed one
fact that had not been established: **is the structural check the only guard, or
a second one?** Counted:

| probe | behavioural checks alongside |
|---|---|
| `apv_bank_fx` | **8** — flatBonus, doubleBank, halveEven/Odd, gain*, rowsArePure, defaults |
| `apv_bust_fx` | **6** — gainPtsCard, punishCard, defaults, survivesUndefined, noStaleFallbacks, earlierTablesIntact |
| `apv_commit_seam` | **4** — bothSeatsRaise, actorsAreRight, sameDerivation, tripleDetected |
| `apv_fog_index` | **5**, including a 4,746-case sweep |
| `apv_deadroll_opp` | 2 — raisesWithArray, ungatedNothing |

**So none of them was a weak substitute for a behavioural test.** They are
refactor guards: they catch wiring being moved or deleted even when the
behavioural checks happen to still pass. That is a real job, and adding a
duplicate behavioural assertion beside an existing one would have been noise.

What was actually wrong is that a source-position check reported a verdict
sounding like proven behaviour. So the **names** moved to the checks:

| was | now |
|---|---|
| `placedCorrectly` | `raiseSitsAfterEncoreAndBeforeBustSave` |
| `bothSeatsWired` (bank_fx) | `bothSeatsReferenceTheTable` |
| `bothSeatsWired` (bust_fx) | `bothSeatsReferenceTheTable` |
| `wiredAfterReroll` | `commitCallSitsAfterTheRerollBlock` |
| `reExpansionIsWired` | `reExpansionPresentInSource` |

`placedCorrectly` was the one that motivated the audit: it inferred
**correctness of placement** from substring offsets — the identical inference
that let `straightsProtectsAFive` stay green while a complete six-run was traded
away. Each now carries a comment naming the sibling that covers the behaviour,
so the structural check is visibly not meant to stand alone.

All five green after renaming; baseline re-recorded.

## Previously suspect — now resolved above

Structural `toString()` checks that read a source substring and report a
behavioural-sounding verdict:

| probe | check |
|---|---|
| `deadroll_opp` | `placedCorrectly` |
| `bank_fx` / `bust_fx` | `bothSeatsWired` |
| `commit_seam` | `wiredAfterReroll` |
| `fog_index` | `reExpansionIsWired` |

For "is it wired" a source check is arguably the right question, and these were
written knowing that. `placedCorrectly` is the weakest — it infers correctness
of *placement* from a substring, which is the same inference `straightsProtectsAFive`
made. Not changed here because each needs its own behavioural replacement
designed, and a rushed strengthening would be worse than an honest name.

## The rule

**Either the check verifies what the name says, or the name says what the check
verifies.** Both are valid repairs. What is not valid is a name that promises
behaviour while the expression asks about presence.
