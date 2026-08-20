# Patron leveling — tech brief

## This is a spec that already exists, not a new design

Before writing anything new, worth being direct: the master design doc
already specifies almost exactly what's being asked for here, in
detail, and it doesn't appear to be implemented. This brief surfaces
that existing spec rather than inventing a new one — the design work
was already done; what's missing is the build.

Direct quotes from the source doc:

> Patron loadout generation: trait biases family (aggro->obsidian,
> hoard->amber, combo->vagabond/starstone, straights->jade, ones->silver,
> triples->amber/jade), with off-diagonal patrons appearing occasionally
> from night 3+ as curveballs. Patron card count by night: 0-1 early, up
> to 3 late; card tiers follow the same night locks as the player.

And the trait/persona relationship that spec depends on:

> Trait = temperament (when they bank/push). Family = tools (what they
> can do). Keep both; they are orthogonal scouting reads. Trait seals:
> single-colour dark red wax, symbol only. Mapping: ones = STEADY
> (anchor), triples = BULLISH (fist), straights = ORDERLY (ladder),
> aggro = RECKLESS (crossed daggers), hoard = GREEDY (coin pouch),
> combo = CUNNING (mask).

So the spec directly answers the two things flagged as missing:

- **Cards**: scale from 0-1 early to 3 by late nights, with tiers
  following the same night-lock schedule the player's own cards use.
  This is the "one or no card at night 2" problem, already solved on
  paper — the count should already be rising, and apparently isn't.
- **Special die**: each of the six personas (which the same doc
  confirms map one-to-one to the six dialogue traits) has an explicit
  family bias for what die material that patron leans toward owning —
  aggro toward obsidian, hoard toward amber, and so on. "No special
  die" is the family bias never actually being applied.

## What to verify before building, not assume

This session found real, repeated gaps between what a design doc says
and what's actually wired — worth checking rather than trusting the
quote above is already live in some partial form.

1. **Does patron loadout generation currently read this trait→family
   table at all**, or is `dieBias` (referenced elsewhere in the
   codebase) doing something else entirely? If a `dieBias` mechanism
   already exists, it needs to be read directly before assuming it
   either matches or ignores this spec — don't guess either way.
2. **Does "card count by night" currently key off the actual current
   night number**, or off something else (times this specific patron
   has been encountered, a flat constant, nothing at all)? The doc's
   phrasing ("card count *by night*") reads as tied to the current
   night globally, not to a per-patron encounter counter — meaning a
   patron dealt for the first time on night 6 should already show up
   at night-6 strength, not need to "catch up" over several
   encounters. Worth confirming that's the actual intended reading
   before building either version.
3. **Does each named patron already carry a persona assignment**
   (ones/triples/straights/aggro/hoard/combo) from the NPC AI work
   done earlier this session? If so, that's the direct hook for both
   the card-family bias and the die-family bias — reuse it rather
   than build a second, parallel character-typing system. If not,
   that assignment needs to happen first, and it's worth doing
   through the same calibrated mechanism (phase 2's `_npcDecide`
   core) rather than assigned by hand per patron.

## One real warning, already learned once tonight the hard way

There are three different six-way taxonomies live in this codebase at
once: `PERSONAS` (ones/triples/straights/aggro/hoard/combo — loadout
archetypes), dialogue `trait:` pools (cunning/greedy/orderly/reckless/
steady/strong — note "strong," not "bullish," as the actual key), and
the six card families themselves (amber/jade/silver/obsidian/
starstone/vagabond). The design doc above treats the first two as
intentionally, explicitly aligned — that's confirmed, not a risk. What
still needs checking is whether the *code's actual key names* match
across all three systems, since a naming mismatch between them
(`strong` vs `bullish` already caught once this session) is exactly
the kind of thing that produces content that's written correctly and
silently never fires. Verify the literal keys line up before wiring
anything that reads across these three systems.

## Design gap the existing spec doesn't fully cover

The quoted spec is thorough on card count and family bias, but doesn't
say what happens to a patron's card *tier* progression in detail
beyond "follows the same night locks as the player" — worth confirming
whether that means literally the same numeric night-gates the player's
own card tiers use, or a patron-specific schedule that happens to look
similar. Also not addressed: whether "up to 3 late" caps at exactly 3
for every patron regardless of persona, or whether that ceiling itself
varies — the existing text reads as a flat cap, but worth confirming
rather than assuming.

## Ruled: growth is alluded to in dialogue, not silent

Decided — patrons should be recognizable across a run, their dialogue
should evolve alongside their mechanical growth, and they should
occasionally, directly reference having changed. Two separate pieces,
both reusing mechanisms already built and proven tonight rather than
inventing new ones.

### Piece 1: backstory pools gain lines by night band, not just cards

The existing 3-line backstory pool per patron stays as the baseline
(nights 1-3). From night 4 and again from night 7, a patron becomes
eligible for one or two additional backstory lines that acknowledge
who they've become — same night-band cadence already ruled for card
count, so the two systems grow in step rather than on separate
schedules a player might notice disagreeing.

Mechanically this is a direct extension of the King thread's own
gating, not a new system: `night_gte(4)` and `night_gte(7)` conditions
already exist in `_DLG_COND` (confirmed live, used tonight for the
Discrepancy thread's tier 3). Backstory lines get the same condition
type the King and Discrepancy tiers already use — the resolver
mechanism doesn't need to change at all, only which lines carry which
condition.

### Piece 2: a dedicated, rare "I've changed" beat

Separate from the expanded backstory pool — a small set of lines (one,
maybe two per patron) that fire specifically on the *first* encounter
after a growth threshold is crossed, not on ordinary repeat visits.
This is the "sometimes mentions it" piece specifically, and it needs
to stay rare to land — every encounter referencing it would flatten
the exact thing that makes it feel earned.

Shape: a new priority slot in the resolver, structurally similar to
the existing greeting tier (fires once, exclusive, beats the ordinary
pool) but keyed to a different trigger — not "first time meeting this
patron ever," but "first time meeting them since their band changed."
Needs one new piece of per-patron state to track (something like "last
band this patron was seen at"), separate from the existing "have I
met them at all" flag the stage-0/stage-1 win/loss system already
carries — read before building whether that flag can be reused or
whether a second one is genuinely needed.

**Scope note**: this brief covers the mechanism only. Writing the
actual band-3/band-7 backstory additions and the growth-acknowledgment
lines for all thirty patrons is a separate, later content pass — same
sequencing as tonight's dialogue work throughout (mechanism first,
verified, then content written against a confirmed-working hook).
