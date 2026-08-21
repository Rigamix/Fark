# Sizing: wiring `_legalKeeps` into the NPC

Measured before building. P481 landed the enumerator inert; this sizes what it
takes to make the NPC actually *choose*. Three findings, and one of them changes
what the pass even consists of.

## Why P481's inertness was a control, not tidiness

Worth restating precisely, because it changes how the next number is read.
`bestMatchesMaximal: true` is not "the port compiled" — it is **the tier-0 control
arm** for the difficulty measurement that follows, the same job the untouched
baseline did in the `generateOppCards` lift.

Without it, any delta from the selection change carries an unstated assumption:
*that enumerating candidates introduced nothing on its own.* Given how many things
tonight looked inert and were not, that assumption had to be **earned rather than
asserted**. It now is: the enumerator's best candidate is provably the same keep
`used[]` already produced, so any delta measured after wiring is attributable to
the *choice* and nothing else.

## Finding 1 — the keep step has THREE sites, not one

| line | site | wire it? |
|---|---|---|
| **L28129** | `runOppTurn` main keep — `_oSel` already collected here (P479) | **yes** |
| **L28239** | **`slippery_table` re-keep** — player card un-keeps everything, rescores, re-keeps from `_stR.used` | **yes** |
| L28312 | `anchor` — forces the last die kept when it shows 6 | **no** — an effect, not a selection |

L28239 is the one that would have been missed. It is a *player card* that
rescores the rival's roll and re-keeps maximally. Wire only L28129 and the
boss's persona silently evaporates whenever the player plays `slippery_table` —
a player card that quietly changes the opponent's personality, with no message
and no error. Exactly the "routes you didn't write" shape.

L28312 is correctly left alone: `anchor` overrides the choice by design, the same
way it does for the player.

## Finding 2 — the sim reimplements the keep step, so the instrument is blind

**This is the load-bearing one.**

`tools/sim_harness.js` `F.oppTurn` does **not** call the game's keep code. It has
its own copy:

```
L609  var total=r.total,used=r.used;
L624  var keptIdx={};for(var q=0;q<fV.length;q++)if(used&&used[q])keptIdx[q]=1;
```

So wiring the game alone and then measuring difficulty through the sim would run
the sim's *maximal* copy and report **zero delta** — a clean-looking zero that
means "the instrument never executed the change", not "the change is neutral".

That is `scrutinise-clean-results` with a live trigger: the zero would arrive
*before* anyone thought to ask whether the harness shares the code.

**Consequence for scope:** the choice function must live in the game and be called
by both, the same shape `famCommitBonus` took in P479 — one derivation, because
two would be free to drift. The harness already calls game functions
(`scoreRoll`, `effectiveCards`, `_dieIsIcon`), so this costs nothing structurally.

Note the harness *already has* the architecture on the player side —
`legalKeeps` (L448) feeding `policy.keep` (L514). The rival path simply never got
it. The sim has been able to choose all along; the rival never could, on either side.

## Finding 3 — a seat bug in `_legalKeeps`, inert today, wrong the moment it is wired

Mine, from P481:

```js
var locked=(G&&G.kept)?G.kept.reduce(function(a,k){return a+(k.pts||0);},0):0;
```

`G.kept` is the **player's** tray. `locked` is passed to `scoreRoll` as the running
bank, which threshold-sensitive cards read. The rival's equivalent is `oppBank` —
confirmed at L28120, where the live code calls
`scoreRoll(_gbFV, G.oCards, oppBank, ...)`.

So `_legalKeeps(free,'o')` scores every rival candidate against **the player's
locked points**. Harmless right now because nothing passes `'o'` yet.

**And the P481 probe said `rivalSeatWorks: true`.** It did — for its own definition
of works: *returns candidates without throwing*. Not *scores them against the
right bank*. Third time a check has vouched for the property next door to the one
that mattered.

**Not fixed in isolation.** Nothing calls `_legalKeeps` with `'o'` today, so the
fix would be unverifiable on its own — it belongs in the wiring patch, where the
call site that exercises it exists.

## Size

| piece | scope |
|---|---|
| `locked` seat fix | 1 line |
| choice function `_npcChooseKeep(keeps, actor)` | new, small, pure |
| game L28129 | replace `used[]` keep with enumerate → choose |
| game L28239 | same, on the `slippery_table` re-keep |
| harness `F.oppTurn` L624 | call the same chooser |
| before/after | same-seed, sim, with the maximal chooser as control |

Small **except** the choice function's policy, which is a design question, not a
sizing one — see `OPEN.md` §10. The plumbing is ready to build the moment that
lands; it is not blocked on anything measurable.
