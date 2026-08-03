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

## 3. The second shared query is dice availability

`!free.length` — **four** guards (`encore`, `stargazer`, `steady_hand`,
`transmute`, `tamper` via `!live.length`). "Are there dice I am allowed to touch"
is asked constantly and computed locally each time.

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

## 5. Two dead handlers

`tar_pit` and `_ward_retired` both have `CFX` entries. Tar Pit is not in
`FAM_LIVE` (retired in favour of Snuff) and Ward-the-card was retired when the
Ward enchant took the job. **22 cards carry handlers; 20 are reachable** — which
reconciles exactly with the Phase 1 count of 20 routed of 29 live.

Same pattern as `#screen-bossreward` and `#rulesOverlay`: code that runs
correctly and can never be reached.

## What this says about Phase 2's shape

| | |
|---|---|
| **Lift first** | `isMine(ev)` — 9 identical sites, one meaning |
| **Keep separate** | `canUse` is a predicate; event hooks are guarded handlers |
| **Second query** | free/live dice availability, 5 sites |
| **Hard constraint** | guards may have side effects; no speculative or cached evaluation |
| **Delete** | 2 dead handlers |

**What Phase 2 must NOT do:** invent a condition vocabulary richer than this. The
content asks for ownership, legality, dice availability and per-card state
presence. Four things. A layer offering forty would be fitted to nothing.

## Reproduce

```bash
python tools/effect_guards.py
```
