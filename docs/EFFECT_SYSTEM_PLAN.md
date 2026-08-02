# Effect system — how I'd tackle it

> **STATUS: Phase 1 is complete (`1850e3c`) and its findings challenge Phases 3
> and 4 as written.** Both carry a CHALLENGED banner below. The plan's own
> closing instruction was *"start with Phase 1 alone and re-plan after it"* —
> this is that re-plan, awaiting a decision. Map: `EFFECT_INVENTORY.md`.

Plan for `docs/briefs/FARK_EFFECT_SYSTEM_PROPOSAL.md`. No code yet.

**Backup done:** tag `pre-effect-system` on `a0aed7d`, pushed. That's the last
commit of the bespoke-effects era — `git diff pre-effect-system` answers "what
did this change" at any point, and `git checkout pre-effect-system` gets the
whole game back.

---

## First: the diagnosis is right, and I can show it

I fixed five bugs today. Every one is the shape the proposal names:

| Bug | The actual failure |
|---|---|
| Starstone paying on any bank | A condition written on the wrong axis, diverging from how Amber's bonus was written |
| Still Waters gating on `d.ench` | The wrong field, checked in one place, six family traits never consulted |
| Vagabond reading `G._oUnbanked` | A one-off variable nobody else maintained |
| Fair Trade → Break costing nothing | A die-legality check living inside one consumer |
| The double-count on bank | Something read before it was fully resolved |

Not one of those is a typo. They're all *the same missing thing*: no shared
definition of a check, so two places drifted. That's an architecture argument,
and it's the correct one.

**But note what that also means:** those five are *already fixed*, individually.
The migration's job isn't to fix them — it's to make the sixth one impossible.
That's a real goal, and it's worth being honest that its payoff is future bugs
not happening, which is harder to see than a bug closing.

---

## The one thing I'd change about the proposal's sequencing

The proposal says: inventory → migration plan → code. I'd insert one phase
*before* migration that it doesn't call out, because it delivers most of the
value at a fraction of the risk.

**Build the shared conditions and queries first, and have the existing bespoke
code call them — without migrating anything.**

`kept_and_scored_this_bank`, `family_trait_active(die)`, `die_is_live`,
`last_completed_turn_bank`. Today each of those is either duplicated or absent.
Landing them as real shared functions, and rewriting the *existing* call sites
to use them, closes the entire class of bug the proposal is about — while the
game still runs on the code we've been testing all session.

Why this matters: every bug in that table was a **condition** problem, not an
effect-dispatch problem. Not one was caused by the lack of a trigger table. So
the conditions are where the value is, and they can land independently.

If we do only this phase and stop, the project is meaningfully better off. That
is not true of any other single phase.

---

## Phases

### Phase 0 — A behavioural baseline *(prerequisite, not optional)*

The real risk isn't the migration, it's that **there's no way to tell whether it
broke something.** One 34,000-line file, no test suite, ~50 pieces of content
whose behaviour lives only in the code being replaced.

We have the beginnings of one: ~20 `tools/apv_*.js` probes written today, each
driving a live match and asserting real values. That's the seed of a regression
suite, not yet a suite.

**Deliverable:** one runner that executes every probe and reports pass/fail, plus
new probes for each content piece that has none — recording what it does *now*,
right or wrong. A migration is only provably safe if "same behaviour" is
machine-checkable.

*Sizing:* this is the phase most likely to be underestimated and the one I'd
most resist skipping.

### Phase 1 — Inventory

Decompose all ~50 cards, enchants, badges and relics into
trigger / condition(s) / effect(s). The proposal's own stated next step.

**The valuable output is the rows that DON'T fit.** A clean table proves nothing
except that the vocabulary was written by someone who'd seen the content. The
misfits are where the vocabulary is actually wrong, and finding them on paper
costs hours instead of weeks.

Three I'd expect to fight, from having just worked in this code:
- **Jade's Break row** ("claims/replaces the interrupted roll") — that's not
  `reroll_grant`, it's a re-entrancy rule about a roll already in flight.
- **Fair Trade** — a *loan* with its own clock, two tiers with genuinely
  different durations. Not obviously a trigger/condition/effect at all.
- **Honeytrap** — "your next roll pulls one die into matching" reaches forward
  into a roll that hasn't happened. That's a constraint on generation, not an
  effect on a result.

### Phase 2 — Shared conditions and queries *(the phase above)*

### Phase 3 — The resolver and the ordering rule

> **CHALLENGED BY PHASE 1'S FINDINGS — awaiting Denis. Do not build this as
> written.** See `EFFECT_INVENTORY.md` §2b and the Phase 1 report.
>
> **The multiplier decision below should be dropped.** Kindred is the only
> doubling in the game and it is NOT a multiplier: "double strength" means
> something structurally different for each of the five whitelisted enchants —
> Tithe 2× gold, Ward two-thirds instead of a half, Snare halves twice on one
> shot, Snuff and Fog hold a seat two turns rather than two lanes. Break and
> Trade are excluded because no coherent 2× exists. **Nothing multiplies, and
> nothing will.** Settling an arithmetic rule for it invents a requirement.
>
> **What Phase 3 should settle instead: EFFECT LIFETIME.** Four enchants
> (Snare, Snuff, Fog, Trade) are lane markers with a placement, a window and an
> expiry — Snare's whole design correction was *shortening the window*. Nothing
> in the vocabulary below expresses that, and it is the concept the content
> actually needs.
>
> **The trigger bus is 69% built already.** `CFX` dispatches on seven hooks and
> carries 20 of 29 live cards. This phase is finishing and naming it, not
> designing it.

The trigger bus, the three-phase resolution (Tier-2 modifiers → Tier-1 effects →
Observers), and the additive-then-multiplicative rule.

**Decide the multiplier rule now even though nothing multiplies yet** — the
proposal is right that this is the one that silently changes numbers later. Cheap
now, expensive after content depends on the accident.

### Phase 4 — Migrate, in dependency order

> **CHALLENGED BY PHASE 1'S FINDINGS — awaiting Denis. Two corrections.**
>
> **1. The first group is wrong.** Enchants are called "newest, best
> understood" — true, and they are also where the vocabulary needs its HARDEST
> new concept: four of the seven are lifetime-markers and Quicksilver is a
> permission rather than an effect. **The 20 cards already on `CFX` are the
> honest first group** — the ones the existing vocabulary already fits.
>
> **2. A group is missing from this list entirely.** Nine live cards are
> hardcoded at call sites with NO `CFX` entry: `bloom`, `cultivate`,
> `vanguard_f`, `for_keeps` and all five tavern cards. A migration that
> enumerates the effect table cannot see them, which is exactly where the
> half-migration this plan warns about would leave its hole. (The five tavern
> cards may not belong on a match-scoped bus at all — they act on the RUN.)
>
> Counts below are also stale: 69 items, not ~50; 29 live cards, not ~31.

Enchants first (7, newest, best understood, already share `_iconFire`), then
family traits (6), then cards (~31), then badges (8, the Tier-2 shape).

**Migrate one group completely before starting the next.** The proposal is
emphatic that a half-migration is worse than none, and it's right — but the unit
of "half" is a *group*, not the whole system. Enchants fully on the new bus with
cards still bespoke is coherent. Four enchants migrated and three not is not.

### Phase 5 — Observers

Feats and the dialogue trait-reaction layer. Structurally enforces "feats must
never grant power" — currently a rule we remember, afterwards a thing the
architecture won't allow. Cheapest phase, best ratio.

---

## What I'd want decided before starting

1. **This or the backlog, not both.** The proposal says don't run it alongside
   balance work, and I agree. But there are six open decisions, a pending sim
   re-run on a dead baseline, the card audit that never finished, and NPC card
   AI unbuilt. Doing this *first* means those wait; doing it *after* means
   migrating more content than exists today. **My recommendation: this first,
   but only after the card audit finishes** — migrating a card whose behaviour
   is unknown or broken means faithfully preserving a bug into the new system.
2. **Opponent-side enchants are scheduled after the pricing pass.** They add a
   whole side to the trigger stream. Better to build the bus knowing they're
   coming than to retrofit — worth pulling that decision forward.
3. **Is the loss screen in scope?** It has no art and the old treatment. Not an
   effects question, but it's the other half of a screen we just rebuilt.

## What I'd push back on, mildly

The proposal's claim that every bug found is the same failure is *nearly* true
and slightly overstated — it says so itself, and it's right to. Of today's
fixes, the two CSS ones (the dropped `.ptcard .lwho` rule, the iOS glow gate) and
the prop-shadow `ASPECT` table have nothing to do with effect architecture. They
were lookup tables keyed on names the things didn't have, and a support probe
that asked an API about itself.

Which is worth saying because **that's the same root pattern one level up**: a
shared table nobody verified against its consumers. The effect system fixes it
for effects. It doesn't fix it for art, CSS, or asset lookups — and those
produced just as many bugs today. Worth knowing the win is scoped.

---

## Sizing, honestly

Phase 0 and 1 are the ones I can estimate: a few sessions, mostly reading and
probe-writing, low risk, high information. Phases 3–4 I can't estimate until the
inventory says how many pieces resist the vocabulary. If the answer is "three
and they're small," it's a large but ordinary refactor. If it's "twelve," the
vocabulary needs another pass before any code is written.

**I'd start with Phase 1 alone and re-plan after it.** It's cheap, it's the
proposal's own recommendation, and it's the only thing that can tell us whether
the rest of this plan is the right shape.
