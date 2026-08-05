# The effect-system plan — re-planned at its own checkpoint

The plan closed with *"I'd start with Phase 1 alone and re-plan after it."* All
six phases (0–5) are now behind us, so this is that checkpoint, done late rather
than not at all.

**The headline: the plan is finished.** Not abandoned, not superseded —
completed, with the last phase measured and pinned tonight. What follows is what
actually remains, from measured state rather than from a list written before any
of it was known.

## Where the six phases landed

| phase | | evidence |
|---|---|---|
| 0 — behavioural baseline | done | the probe suite, now 38 probes |
| 1 — inventory | done | `EFFECT_INVENTORY.md`; its re-plan was ruled |
| 2 — shared conditions | done | `EFFECT_PHASE2_GUARDS.md` |
| 3 — resolver / ordering | done | ruled, all three re-plan changes taken |
| 4 — migrate in dependency order | done | `PHASE4_MIGRATION.md` |
| 5 — observers | done | `P5_OBSERVERS.md`, pinned by `apv_observers` |

## What actually remains, and what each is worth

**1. `commit` — the last ungated seam.** Seven of eight raise. This one is held
for a ruling, not for work: its payload describes *the shape of a selection the
player made*, and the rival scores a roll and banks instead. **Blocked on a
decision, not on effort.** `SEAM_TWO_LEFT.md`.

**2. The mechanic tables stop where they are — deliberately.** Five shipped;
the remaining 13 single-site mechanics **should not** be tabulated. The bar is
*removes a copy*, and they have no second copy to drift from. `TABLE_BAR.md`.
**This is a decision to not do work, and it should survive the next person
noticing an inconsistency.**

**3. The sim cannot answer difficulty questions of a certain size.** Not a stop
any more — the reason I escalated it was wrong and is retracted — but three real
limits stand: `F.oppTurn` reimplements the turn loop; `spread` is `max−min` over
four agents and **unsound for mid-sized deltas**; four agents is a small sample.
`SPREAD_AUDIT.md`, `SIM_OPPTURN_SIZE.md`.

**4. `block_low_bank`** — implemented on both seats, declared by no card.
Backlogged, needs a design call. `AUDIT_BACKLOG.md`.

**5. Two plan decisions never made** — opponent-side enchants after the pricing
pass, and whether the loss screen is in scope. Both still open, both Denis's.

## What the plan asked to decide, revisited

It listed three preconditions. One is now settled: *"a pending sim re-run on a
dead baseline"* — re-run at five seeds, and the `generateOppCards` lift measured
separately and attributably (`OPPCARDS_LIFT_MEASURED.md`). The other two are
items 5 above.

## The honest recommendation

**Stop treating the effect system as the organising thread.** It is done, and
continuing to work a finished list is how a plan outlives its usefulness. The
remaining items are four independent decisions and one deliberate non-decision —
none of them a phase, none blocking each other.

**And the thing genuinely worth doing next is not on this plan at all:** the
patron card layer went live tonight after being dormant since the P1 cutover.
Every one of those 41 cards is now dealt for the first time, and **none has been
seen in a real match.** The measured difficulty delta says they work in
aggregate; nothing says any individual card behaves as its description claims.
That is the card audit the plan itself flagged as never finished — and it now
has a reason to happen that it did not have this morning.
