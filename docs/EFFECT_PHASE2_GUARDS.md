# Effect Phase 2 — the condition vocabulary, read out of the handlers

**Derived, not designed.** `famFire` dispatches and checks nothing, so every
handler hand-writes its own guard — and that is exactly where Vagabond's stale
read, Starstone's wrong gate and Still Waters' wrong field lived. The shared
layer's vocabulary therefore has to come from what the content already asks for.

Extracted by `tools/effect_guards.py`: **42 hooks across 22 cards.**

## 1. One condition dominates, and it is spelled identically every time

```js
if(!ev.mine||ev.owner!=='p')return;
```

**Nine occurrences, character-for-character**, across `bank`, `bankBonus`,
`roll` and `bust` — `slow_cook` ×2, `falling_star`, `pickpocket`, `reprisal`,
`retort`, `short_fuse`, `fools_gold_f`, `double_or_nothing`.

That is the whole ownership question — *does this event belong to me, the
player?* — asked nine times by hand. **`famFire` already computes `ev.mine` and
every handler re-derives it anyway.**

This is the first thing the condition layer should own, and the cheapest: nine
call sites, one meaning, zero disagreement between them today. The risk it
removes is that they ever drift apart — which is precisely how Vagabond ended up
reading a stale variable while its dispatch was perfect.

## 2. `canUse` is a QUERY, not a guarded handler — the content already splits them

**Thirteen cards define `canUse` and not one of them guards.** They return a
predicate directly. Every other hook opens with an early return.

Phase 2 is titled *"shared conditions and queries"* and the split it names is
already present in the content: `canUse` answers **"is this legal right now"**,
the event hooks answer **"does this event concern me"**. Those are different
shapes and should not be given one mechanism.

## 3. Dice availability is NOT a shared query — and this section was wrong

I wrote that `!free.length` was the second shared condition, "asked constantly
and computed locally each time". Measured, the sets are **four different
things**:

| handlers | set |
|---|---|
| `encore`, `stargazer`, `steady_hand` | `!committed && !_frozen` |
| `sacrifice` | `!committed && !_shattered` |
| `transmute` | `!committed` |
| `powder_keg` | **the whole pool, kept dice included** |

`_frozen` is a within-turn hold; `_shattered` is a destroyed die. A helper
folding these together would let a card touch a die it must not — and would
quietly take Powder Keg's *"blow up your whole roll, kept ones included"* away
from it, which is the card's entire identity.

**And `tamper` was never a dice query at all.** Its `live` is
`(G.oF||[]).filter(o => !o.broken)` — the opponent's **unbroken cards**. I
grouped it by the variable *name* rather than by what it holds: the same
surface-resemblance mistake this document exists to catalogue, committed inside
the document.

**So there is no lift here.** Four predicates, four meanings, one deliberate
no-filter, and a fifth site about something else entirely. `_fxMine` stands
alone for now, and the code says why there is no `_fxFreeDice()`.

## 4. NOT EVERY GUARD IS PURE — and a shared layer that assumes purity will break

`powder_keg.use` opens with:

```js
if(_tryBustSave(free))return;
```

**`_tryBustSave` SPENDS a bust save.** The guard is not a test, it is an attempt
that mutates. Hoisting guards into a condition layer that evaluates them
speculatively, caches them, or runs them for several handlers would **double-spend
the save**.

This is the single most important constraint on Phase 2's design, and it would
not have shown up in a vocabulary designed top-down — it only appears because the
guards were read.

## 5. Two dead handlers — now deleted

`tar_pit` and `_ward_retired` both have `CFX` entries. Tar Pit is not in
`FAM_LIVE` (retired in favour of Snuff) and Ward-the-card was retired when the
Ward enchant took the job. **22 cards carry handlers; 20 are reachable** — which
reconciles exactly with the Phase 1 count of 20 routed of 29 live.

Same pattern as `#screen-bossreward` and `#rulesOverlay`: code that runs
correctly and can never be reached. **Both deleted in P439**, and
`apv_cfx_reachable` now asserts it rather than leaving it to be noticed —
handler count is 20, matching Phase 1's "20 routed of 29 live" exactly.

## What this says about Phase 2's shape

| | |
|---|---|
| **Lift first** | `isMine(ev)` — 9 identical sites, one meaning |
| **Keep separate** | `canUse` is a predicate; event hooks are guarded handlers |
| **NOT a second query** | dice availability is four different sets — see §3 |
| **Hard constraint** | guards may have side effects; no speculative or cached evaluation |
| **Delete** | 2 dead handlers |

**What Phase 2 must NOT do:** invent a condition vocabulary richer than the
content asks for. Measured, it asks for **one** liftable condition — ownership.
Legality is a different shape (`canUse` is a predicate, not a guard), dice
availability is four incompatible sets, and per-card state presence is one line
inside three guards that already read it.

That is a much smaller answer than "shared conditions and queries" implies, and
it is the honest one. The section above that claimed a second shared query was
**wrong when written** and is corrected in place — which is itself the argument
for deriving this from the content twice rather than designing it once.

## Reproduce

```bash
python tools/effect_guards.py
```
