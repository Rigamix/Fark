# FARK — UNIFIED EFFECT SYSTEM PROPOSAL

For Code. Prompted directly by a real, named problem: cards and dice effects
breaking, fixing one regressing another. This isn't a balance question, it's
an architecture one — every bug found across this whole project's sim/audit
passes (Vagabond reading a stale variable, Starstone's wrong gate, Still
Waters checking the wrong field, the Fair-Trade/Break exploit, the double-
count bug) is the SAME underlying failure wearing a different costume: a
bespoke, one-off implementation per card/enchant instead of a shared system.

**Grounded in real prior art, not invented from scratch.** Balatro's Joker
system, and the "Trigger > Condition > Effect" abstraction the modding
community (Joker Forge) formalized to describe it. This is a known pattern —
Entity-Component-System / data-oriented design — not a bespoke proposal for
this game specifically.

**Fark already has a working, tested proof this pattern works here.** The
dialogue resolver built earlier this project (speaker_pool + min_stage +
conditions → resolved output, one function, every pool of content routes
through it) is structurally identical to what's proposed below, just applied
to a different domain. This isn't a new idea for this codebase.

## The vocabulary

**TRIGGER** — the pipeline event an effect hooks into. Fixed, small set,
covers everything currently in the game:
`dice_rolled`, `selection_changed`, `keep_committed`, `bust`, `bank`,
`hot_dice`, `turn_start`, `turn_end`, `match_start`, `match_end`,
`die_destroyed`, `icon_face_kept`.

**CONDITION** — the gate, evaluated against SHARED state, never duplicated
per-effect. This is the load-bearing rule: if two effects need to check "was
this die meaningfully used this bank," they read the SAME function, not two
independently-written approximations of the same idea. That divergence is
literally what broke Starstone.
Examples already needed by existing content: `material_match(family)`,
`kept_and_scored_this_bank`, `night_gte(N)`, `goal_state(boss_beaten |
enchant_owned)`, `heard(pool_id)` (already built for dialogue), `stage_gte(N)`.

**EFFECT** — the lever pulled, each with exactly ONE generic visual tied to
the effect TYPE, never hand-authored per card:
- `score_delta(amount)` — number pop + colour flash at the total
- `gold_delta(amount)` — coin icon + count-up
- `die_state_change(kill | hush | preserve | swap_material)` — the die
  itself fades, dims, or morphs; generic, not bespoke per card
- `reroll_grant(target)` — the existing tumble animation, reused
- `turn_flag_arm(condition, deferred_effect)` — a persistent glow that
  stays until consumed or the turn ends (this is Ward's actual shape)
- `info_reveal(target)` — the existing peek-style unveil, reused
- `extra_action_grant` — a distinct banner/transition

**Every card, enchant, and badge in this entire project is one trigger, zero
or more conditions, and one or more effects from this palette.** A new card
is a new ROW OF DATA selecting from an existing palette, not new code — same
"content is data, not code" principle already proven by the dialogue system.

## The one subtlety that matters most: query interception, not just effects

Some rules — Still Waters is the clean example — shouldn't apply an effect
directly. They should intercept a SHARED QUERY other effects already consult,
and change its answer. This is the actual lesson from Balatro's own hardest
case (a Joker that makes every "is this a face card?" check return true,
rather than transforming the card itself) — and it's the CORRECT fix for a
real bug already found here.

Still Waters should NOT be "for each of the six family traits, check if this
badge is worn, and if so don't fire." That's six special cases, the exact
shape of thing that breaks when a seventh family trait gets added later. It
should be ONE interception on the shared `family_trait_active(die)` query —
every family trait already has to call this before firing (or should, under
this system), so Still Waters answering `false` for the wearer's opponent
covers all six today AND any added tomorrow, automatically, for free.

## Three real bugs, decomposed, to prove the system before asking to build it

**Starstone's family trait** (the worst bug found this session — 77.5% win
rate for a fully random player):
- OLD: bespoke check, "banked anything while owning a Starstone die" —
  wrong axis entirely, diverged from how Amber's bonus was written.
- NEW: `trigger: bank`, `condition: material_match(starstone) AND
  kept_and_scored_this_bank`, `effect: score_delta(+500)`. Amber's triple
  bonus reads the SAME `kept_and_scored_this_bank` condition — they cannot
  drift apart again, because there's only one definition of the check.

**Vagabond's Break row** (reading a stale, structurally-broken variable):
- OLD: `G._oUnbanked`, written once, read in a context where it no longer
  meant what the reader assumed, because of turn alternation.
- NEW: `trigger: turn_end` writes `last_completed_turn_bank` as a defined
  pipeline output, for everyone, always. Vagabond's Break row (`trigger:
  die_destroyed`, `condition: material_match(vagabond)`, `effect:
  steal(source: opponent.last_completed_turn_bank)`) reads that instead of a
  one-off variable nobody else was maintaining.

**Still Waters gating by brand instead of family:**
- OLD: `if (d.ench && stillWaters())` — checks the wrong field, punishes
  players for having enchanted a die rather than suppressing the family
  trait itself.
- NEW: query interception as described above. One hook, not a per-family
  special case, correct for every family including ones that don't exist
  yet.

## Layering — cards, family traits, and enchants stacking on one die

Stress-tested directly, not assumed. Two different findings, one reassuring,
one requiring a real addition to what was proposed above.

**The score layer resolves for free — PROVIDED conditions are precise, not
approximate.** Amber's triple bonus stacked with Tithe on the same die: Amber's
condition isn't "is this die Amber material," it's "did this die contribute
to a natural, matched-value triple." A Tithe-branded face, kept, resolves
through the icon path and banks zero — it never enters triple-detection at
all. The layers don't conflict because their conditions were never actually
contesting the same ground. This only holds because the condition was written
precisely; a loose version ("is Amber material") would reopen exactly the gap
that broke Starstone.

**The die-state layer needed a real fix, not just a reassurance.** Break
already can't target a Preserved die or a borrowed one — both discovered
separately, as one-off exceptions, during the sim pass. Left as written, both
checks would live INSIDE Break's own implementation — meaning the next effect
that wants to kill a die (a plausible future Obsidian card, "Sacrifice," is
exactly this shape) either re-derives both checks from scratch or forgets one,
which is the literal shape of every bug found this session.

FIX: these checks belong to the `kill` variant of `die_state_change` itself,
as a shared gate every consumer inherits, not to Break specifically. Two
genuinely distinct tiers, not one — collapsing them would be imprecise in the
same way that broke Starstone:
- **Universal, applies to nearly any die-targeting effect**: is this die LIVE
  at all (not Preserved/inert, not already destroyed). Blocks kill AND reroll
  AND anything else that touches a specific die.
- **Kill-specific, one tier narrower**: the borrowed-die exclusion does NOT
  generalize to reroll — rerolling a borrowed die is fine, nothing permanent
  happens to it. It's specifically about PERMANENT removal, so it's scoped to
  `kill` alone, not promoted to the universal tier it doesn't belong to.

**Flagged now, triggers nothing yet: score-effect ordering.** Every current
bonus in this game is additive (+200, +500, flat gold) — no multiplier
exists anywhere yet, which is exactly why this hasn't caused a visible bug.
This is the SPECIFIC failure mode that makes Balatro's own system fragile
("+mult before xmult, no exceptions," per the research above) — the moment
this game adds a multiplicative effect, resolution order stops being
arbitrary and starts being able to change the actual number two additive-
looking effects produce together. Decide the ordering rule (proposal: all
additive effects resolve in trigger-registration order, THEN all
multiplicative effects, as a fixed two-pass structure) before it's needed,
not after something breaks because two effects turned out not to commute.

## Visual language — one recognizable pattern per primitive, not per card

Three axes, matching the three example types given directly (glow, bounce,
opacity) — each maps to a different KIND of thing happening, which is what
makes the assignment principled rather than arbitrary:
- **MOTION** = uncertainty or change-in-progress (a die about to become
  unknown again).
- **LIGHT/COLOR** = value or state (how much something matters, or whether
  it's been muted).
- **OPACITY** = existence or information (present, hidden, or gone).

| Primitive | Axis | Visual | Why |
|---|---|---|---|
| `score_delta` | Light | Warm sheen sweep across the die/number, brief | Value being recognized — "catching the light" |
| `gold_delta` | Motion | Coin icon, single downward pop-bounce | A discrete "landing," different RHYTHM than reroll's jitter even though both are motion |
| `die_state: kill` | Opacity | Crack/fracture, fragments, fade to nothing | Final, irreversible — reuses the ALREADY-established Obsidian-shatter flavor rather than inventing a second "destruction" look |
| `die_state: hush` | Light | Desaturation, glow dims toward grey | Muted, not destroyed — matches "Still Waters" by name, and reads as clearly DIFFERENT from kill's fragmenting |
| `die_state: preserve` | Light | Warm amber glow from within/beneath (ALREADY specced in the match brief — cited here, not reinvented) | Protected, held safe — the existing spec already got this right |
| `die_state: swap_material` | Opacity | Brief ripple/shimmer, material dissolves and re-forms | Identity changing while the object itself persists — distinct from kill (object gone) and hush (object dimmed but unchanged) |
| `reroll_grant` | Motion | Quick, low-amplitude jitter, BEFORE the die's own real tumble | Signals "this reroll was GRANTED," kept visually distinct from the tumble that follows once it actually executes |
| `turn_flag_arm` | Light | Slow, breathing pulse-glow, persists until consumed | Primed and waiting — ongoing, not a single instant, unlike every other row here |
| `info_reveal` | Opacity | Fade from translucent/hidden to fully opaque | Direct, literal mapping — hidden information becoming visible IS a transparency change |
| `extra_action_grant` | — (turn-level, not die-level) | Full banner/transition, deliberately NOT a per-die effect | A bigger structural moment; the one primitive that was never going to fit the die-scoped table above |

**Cards use the SAME vocabulary their effect invokes — this is the direct
answer to "should apply to cards as well."** A card is a delivery mechanism
for one or more of the primitives above, nothing more — so when it fires, the
CARD OBJECT gets a scaled-down, source-flavored version of whatever visual its
effect uses, plus a brief connecting motion (a short trail or spark) toward
whatever die or number it's affecting. A card whose effect is `score_delta`
sheens itself, softer than the target's own sheen, with a visible line
between them. This is the exact mechanism the Balatro research found makes
causality readable without text: Jokers visually pulse AT THE SAME MOMENT as
the number they're affecting changes, so the player learns what synergizes
with what by watching, not by reading a tooltip. Same principle, same
payoff — a player should be able to tell WHAT KIND of thing a new card does
from its visual alone, before ever reading its text, because the visual
vocabulary is shared and small enough to become genuinely recognizable.



## Tier 2 — badges are a different KIND of thing, not a missing row

Everything above fires ONCE at a trigger and applies a change. Badges don't
do that — they're persistent, whole-match rules. Treating a badge as one
more entry in the Tier-1 table would be the same imprecision that broke
Starstone: forcing a genuinely different shape into a container built for
something else. Walking all eight tells against the Tier-1 table to find
what's actually needed, rather than assuming the table already covered them:

- **`bank_void(condition)`** — NEW. Not a value change, a conditional
  cancellation of the bank event itself. Covers Last Call (void if the
  amount is under 500) and Reckoning (void unless it matches the boss's
  last bank) — same shape, different condition, one primitive.
- **`match_rule_modifier(constrains: trigger, rule)`** — NEW. Persists for
  the whole match; constrains WHICH or HOW OFTEN a Tier-1 trigger can fire.
  Covers Drill Order (caps `dice_rolled` at 3/turn) and Zero Hour (forces
  `turn_end` early off `icon_face_kept`).
- **`effect_magnitude_modifier(scope, multiplier)`** — NEW. Does nothing on
  its own; amplifies whatever OTHER effect produces when it fires. Covers
  Kindred. Visual rule, not a new visual: whatever primitive it's scaling
  plays its OWN existing visual again, or larger/brighter — Kindred never
  needs a bespoke animation, it intensifies one that already exists.
- **Still Waters RECLASSIFIED**, not newly covered — it was already built as
  query-interception, but it's the SAME persistent, whole-match shape as the
  three above. It's a `match_rule_modifier` whose rule is "this query
  returns differently," not its own separate category. Real unification,
  not relabeling for its own sake.
- **Steeped, checked and NOT new** — worth showing the negative result, not
  just the positive ones. It's `score_delta(+100)` firing at every roll,
  feeding the same turn-bank pot the EXISTING bust mechanic already zeroes.
  No new primitive; just an old one used at a per-roll trigger instead of
  per-keep.

**Visual for the match-rule tier**: ambient, not momentary, since these are
persistent for the whole match — the already-established worn-badge
presence or cursed-seat smoke IS this tier's resting visual. At the SPECIFIC
MOMENT a rule actually constrains something (the roll cap is hit, a bank
gets voided), that gets its own punctuation: a screen-edge or border pulse,
deliberately NOT a per-die visual, since the thing happening isn't scoped to
one die, it's scoped to the match's own rules.

**Cursed matches, directly: no new primitve needed.** A cursed seat is "pick
one `match_rule_modifier` from the boss pool, apply it symmetrically" — once
this tier exists properly, cursed matches fall out for free. This is the
actual proof of the system's central claim: new "content" (which modifier is
active) never needs new code, just a new pool entry.

## Two gaps in the enchant layer this pass also found

**Snuff is not `kill`.** `kill` (Break, and any future card like Sacrifice)
is permanent — gone until next match. Snuff is temporary with AUTOMATIC
return after one opponent turn. These need to be siblings, not the same
primitive stretched to cover both: `die_state_change` gets a `suspend`
variant alongside `kill`, `hush`, `preserve`, `swap_material` — same
opacity-axis family as `kill` visually (the die visibly recedes, not
fragments), but reverses automatically rather than needing a restoration
event.

**Fog and Still Waters are the same idea aimed at different targets.**
Both mute something for a specific consumer — Still Waters mutes a family-
trait CHECK, Fog mutes what an AI's decision logic can SEE about one die.
Rather than inventing a second "muted" concept, both should be the SAME
`suppress(target, consumer)` primitive, sharing the desaturation visual
already specified for `hush` — Still Waters suppresses for the query layer,
Fog suppresses for the opponent AI's own heuristic, same visual language
either way, since to the player watching, both read as "something here got
quietly muted."

## A third role, not a primitive: Observer (feats, dialogue reactions)

Everything above ACTS on game state. Feats and the dialogue trait-reaction
layer don't — they WATCH the same trigger stream and produce a disconnected
side effect (a cosmetic pin; a line of speech). That's a structurally
different ROLE, not a gap in the primitive table, and it's worth its own
category rather than being forced into Tier 1 or Tier 2.

**Feats.** An Observer, by definition, cannot emit a Tier-1 or Tier-2
effect — it can only fire its own cosmetic unlock when a pattern in the
trigger stream is satisfied (e.g. "WISH GRANTED" = `extra_action_grant`
sourced from Falling Star, fired twice in one match). This isn't just a
category label — it's the EXISTING "feats must never grant power" design
law, now structurally enforced rather than remembered. A feat that
accidentally touched score or gold stops being a review miss and becomes a
thing the architecture doesn't allow to exist. Visual: reuses the opacity
axis (existence) already defined above — a small icon solidifies/travels
toward the feats wall, distinct from every per-die and per-match visual,
since nothing about the CURRENT match's state changed.

**The dialogue trait-reaction layer is also an Observer**, subscribing to a
curated subset of triggers (bust, bank-with-a-magnitude-condition). Same
rule applies, and this is where a REAL bug risk was found, not just a
completeness gap.

**Ordering, stated once, applying to every trigger — this is the actual
fix, not a footnote:** if a bank gets `bank_void`'d (Last Call, Reckoning)
and the dialogue system's "big bank" check reads the RAW amount instead of
the FINAL resolved one, a player could have their bank voided to zero and
still hear a cheerful "Now THAT'S a bank!" — the same shape of bug as the
double-count issue already found this session (something read before it
was fully resolved). Fix: three-phase resolution, per trigger, no
exceptions —
1. Tier-2 modifiers resolve first (void, cap, or amplify the outcome)
2. Tier-1 effects apply using the FINAL values
3. Observers (feats, dialogue) react only to what actually, finally
   happened

This also confirms Kindred's Tier-2 placement from the section above for
the same underlying reason — it modifies a magnitude before the thing it's
modifying finalizes, same ordering requirement, not a coincidence.

**Relics need no new primitives, but one principle had to be stated
explicitly to make that true.** Checked against all three known relics:
Grog's Tooth is Obsidian's existing shatter trait with its own parameters
overridden (10%/+1500 instead of 6%/+1000) — pure data, no new mechanism.
Brutus's Shield is a die with Ward permanently pre-applied — already fully
supported, any die can carry an enchant. Corvus's Ledger is the interesting
case: it's Starstone's exact trigger/condition/effect shape, attached to a
die that ISN'T Starstone material — which only works if an effect tuple
attaches to the DIE INSTANCE itself, never derived purely from a material
lookup. That principle wasn't stated before this pass; stating it now closes
the gap without adding machinery — a relic is just a die instance carrying
its own tuple, independent of what the die visibly is.

## What this is NOT proposing

Not a rewrite of match flow, UI, or anything outside how card/dice/badge
EFFECTS get defined and resolved. Not a claim that every current bug is
caused by this (some are ordinary implementation bugs unrelated to
architecture). Not something to build alongside ongoing balance work — this
needs to be its own dedicated pass, because doing it half-migrated (some
cards on the new system, some still bespoke) would be worse than not doing
it, reintroducing exactly the "which version is authoritative" confusion
this whole project has fought all session.

## What's NOT done here, flagged rather than implied complete

The full decomposition of every existing card, enchant, and badge (~50+
pieces of content) into this vocabulary — the three examples above prove the
system can represent real, already-known-broken content, not that all of it
has been translated. That's the actual next step if this direction is
confirmed: a complete inventory pass, THEN a migration plan, before any code
changes. Sized, real, separate work — not implied finished by this proposal.
