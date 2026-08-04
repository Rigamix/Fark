# Two measurements: completion count, and seam sizing

Both re-measurement, not build. `tools/rework_completion.py` and
`tools/seam_five.py` rerun them.

## 1. Rework completion, per category

Denominator is the Phase 1 inventory, unchanged at **69**.

| Category | total | on shared machinery | what "shared" means here |
|---|---|---|---|
| Family cards, live | 29 | **23** | a `CFX[id]` entry |
| Enchants | 8 | **3** | state through `_lm*` |
| Break death rows | 6 | **6** | `BREAK_TRIGGERS`, one keyed table, 2 dispatch sites |
| Table rules (badges) | 9 | **9** | reached via `_ruleActive(id,side)` |
| Relics | 8 | **0** | `effect.mechanic` dispatch |
| Material family traits | 9 | **0** | same |
| **TOTAL** | **69** | **41** | |

Blended, with the arithmetic shown because it was asked for: **41 / 69 =
59.4%**. The per-category rows are the answer; the blend hides that badges are
finished and relics have not started.

**"Shared" is not the same mechanism per category**, and pretending it were
would be the mistake this rework exists to remove. Each row states its own test.

**Relics and materials score zero for a measured reason, not a felt one.**
Both dispatch on `effect.mechanic`, and there are **46 `mechanic===` branches
across 14 functions** — `handleBank` 10, `finOpp` 9, `scoreRoll` 4, `doBust` 4,
and ten more. A 46-arm switch in one function would be a dispatcher; 46 checks
spread across fourteen is bespoke wearing a data field.

**The six family cards off the bus are the run-scoped six** — `for_keeps`,
`double_stakes`, `the_tab`, `hair_of_the_dog`, `marked_table`, `high_table` —
ruled off the match bus deliberately. Not unmigrated work.

**The five enchants off `_lm*`** are `tithe`, `ward`, `break`, `trade`,
`quicksilver`. Measured in Phase 3: Ward is a charge counter, Trade a
transaction log, neither a lane marker. Also not a queue.

### A counting correction worth keeping

Parsing `FAM_LIVE` statically gave **22** live cards against the inventory's 29,
and included `anchor_f` and `bookends_f` — `FAM_LIVE` keys for cards **cut** from
`FAM_CARDS`, so they are live flags pointing at nothing. The game's own answer is
`FAM_CARDS.filter(d => FAM_LIVE[d.id])`, evaluated in-page. The static number
would have understated the denominator by 7 *and* named two cut cards as
outstanding work.

**Small real find:** `anchor_f` and `bookends_f` are stale `FAM_LIVE` entries.

## 2. The five remaining seams, sized per seam

| seam | kind | why |
|---|---|---|
| `bust` | **GATE** | `_oppBustOut()` is a named inner function with 4 call sites all funnelling through it — one call covers every bust exit |
| `bankBonus` | **GATE** | one canonical site: `G.oPts+=pts;_npcActuallyBanked=true` |
| `commit` | **DECISION** | 10 candidate sites, and they are genuinely different — the rival re-scores under fog, encore and reprisal variants. No single canonical commit. This is the `seatCommit` question again |
| `deadRoll` | **BEHAVIOUR** | **no counterpart exists.** The rival's turn never asks "did this roll score nothing" |
| `rivalTurn` | **BEHAVIOUR** | the semantics **invert**: for a boss-held card "the rival" is the *player*, so its moment is `endPTurn`, not `runOppTurn` |

**Two gates, one decision, two behaviour.** That is the size — not a guess, and
materially smaller than "five remain".

**The one flagged earlier as needing new opponent behaviour was `deadRoll`, and
that is confirmed.** But it is **not the only one**: `rivalTurn` is equally
structural for a different reason — its moment exists, in the wrong function,
with inverted meaning. The earlier framing named one; there are two.

### A reclassification from reading rather than counting

`bust` first measured as DECISION on 9 sites. Four of those are one function's
definition, its call, a comment and a counter. Reading them moved it to GATE.
Same step that disqualified `endMatch` and `seatCommit` — the count says where
to look, never what is there.
