# FARK — PATRON LORE SYSTEM

For Code and for future writing passes. Builds on the CURSED SEAT rename
(see FARK_MASTER_BRIEF.md section 1) — that rename is what surfaced this
whole idea: a purple-smoke "curse" is exactly the kind of thing tavern
patrons would gossip about, wrongly, which is the seed of everything
below. This doc proposes an ARCHITECTURE (cheap, a few small additions to
what already exists) plus a SEED CAST of six named patrons proving the
shape works, before scaling to a full roster.

## The core idea, one paragraph

A small pool of named, recurring patrons sits alongside the existing
algorithmic (persona x family x trait) patron generation — most seats
each night stay fully generic as they are today, but occasionally a
NAMED patron with a real goal, quirk, and dialogue ladder gets drawn
instead. Named patrons remember the player (a simple per-run stage
counter, nothing more) and occasionally reference EACH OTHER in their
own lines — never systemically checked or enforced, purely written —
so a player who's met two connected patrons in either order gets to
notice the connection themselves. That noticing is the entire payoff.
Everything else is restraint: short lines, no forced reading order, not
every patron gets a saga, some get one line ever and nothing more.

## Architecture (what Code actually needs to build)

**The one governing principle: there is exactly ONE resolver function.**
A named patron's personal arc, ambient town-gossip content (Peck's
pool), and any future line category all run through the SAME procedure,
fed different pools and keys. There is no per-patron code, no per-thread special casing. A new
patron or a new line is a new ROW OF DATA, never a new code path. This
is the actual answer to "how does this stay clean at 30 patrons instead
of 6" — the system doesn't grow, only the data does.

### The data shape

Every speakable line, whatever it belongs to, is the same small record:

```
{
  speaker_pool: "patron:hollis" | "gossip:town" | ...
  min_stage: <int>       // floor, not exact match — see resolution below
  conditions: [ <predicate>, ... ]   // optional, all must hold (AND)
  text: "..."
}
```

`conditions` are simple predicates read off state the game ALREADY
tracks — never invented state built solely for flavor. Examples:
`night_gte(6)`, `night_lte(2)`, `boss_beaten("grog")`,
`enchant_owned("ward")`. This is the actual dividing line for what's
allowed to be a condition at all: if it's a query against existing save/
run state, it's fair game and cheap. If it would require a NEW data
structure invented only to support a line of dialogue (a relationship
graph, a "has heard rumor X" flag with no other purpose), it doesn't
belong here — that's exactly the complexity this system exists to avoid.
Patron-to-patron REFERENCES stay prose-only for this reason (see below,
unchanged from the first pass) — cross-references would need new state
with no other use; goal-state does not, since bosses-beaten and
enchants-owned are already tracked for other reasons entirely.

### Resolution algorithm (the one function everything calls)

Given a speaker context (a specific named patron, or a thread pool) and
the current run state:

1. Gather every line belonging to that speaker_pool.
2. Filter to lines where `current_stage >= min_stage` AND every
   condition evaluates true against current state.
3. Among survivors, rank by specificity: MORE conditions attached wins
   over fewer at the same min_stage (lets a conditional override sit
   beside an unconditional default at the same stage — e.g. Ferrand's
   normal stage-0 line vs. a variant that only fires if Grog is already
   beaten, per the worked example below).
4. Among ties, highest `min_stage` wins (prefer the most advanced
   applicable line over an earlier one that happens to still qualify).
5. If candidates are STILL tied after both rules (same specificity, same
   min_stage — e.g. a patron with two separate unconditioned personal
   lines, like Ferrand's Grog-goal line and his King-reaction line, both
   eligible at once), pick RANDOMLY among the tied survivors. This is
   deliberate, not an unhandled edge case: a little variance in what a
   familiar named patron says on repeat encounters is a small, free
   improvement, not a gap to close with more ordering rules.
6. Deliver the winning line. Increment that patron's stage counter by
   1 — always, regardless of which line fired, one operation, no
   branching.
7. If NOTHING survives step 2 (shouldn't happen with a min_stage:0,
   no-conditions line always present as a floor — that's a content
   requirement, not an engine concern: every patron pool needs at least
   one unconditional stage-0 line so step 2 can never return empty).

### Priority when a patron could speak either personal or thread content

If a named patron is flagged as gossip-eligible (Peck, in the seed
set), they have lines from BOTH `patron:<id>` and `gossip:town`
available at once. Resolve personal lines first; only fall back to a
gossip line if the patron's own pool is fully exhausted (stage past
their last personal min_stage) — keeps an arc from getting crowded out
by ambient texture, while still giving an "exhausted" patron something
live to say instead of repeating themselves forever. Peck's own pool
is ENTIRELY gossip content by design (see seed cast) — for him this
rule is moot, personal and gossip are the same pool. A future named
patron could carry both a real personal arc AND gossip eligibility,
which is exactly the case this priority rule exists for.

### Draw algorithm (who gets seated)

1. Per seat, roll whether this seat attempts a named-cast draw at all
   (proposal: ~1-in-3; tune by feel, not locked).
2. If yes, filter the named-cast pool to patrons eligible THIS NIGHT:
   not already seated elsewhere this same night (hard requirement,
   avoids duplicating a named patron across two seats at once), and any
   patron-specific night-range gate if one's been authored (none of the
   seed six need this, but the field should exist for later patrons
   meant to appear only from a given night onward, mirroring how family
   cards are already night-gated).
3. Weight the eligible pool: full weight if `stage < patron's max
   authored stage` (fresh or mid-arc), reduced weight once a patron is
   exhausted (proposal: ~0.3x) — keeps the pool from visibly repeating
   the same few faces once the roster is still small, without making an
   exhausted patron vanish outright.
4. Pick one via weighted random. If none eligible or the roll says no
   named draw, fall back to the existing generic generator, unchanged.

### Worked example, tracing real seed content through the algorithm

Ferrand's pool: `{min_stage:0, text:"Boot's mine..."}`,
`{min_stage:0, conditions:[boss_beaten("grog")], text:"Someone beat me
to it. Fark."}`.
- Player meets Ferrand for the first time (stage 0), Grog still alive:
  only the unconditional stage-0 line survives filtering → fires.
- Player meets Ferrand for the first time, but has ALREADY beaten Grog
  and taken his badge in an earlier seat this run: BOTH stage-0 lines
  survive filtering; the conditional one wins on specificity (more
  conditions attached) → "Someone beat me to it. Fark." fires instead,
  automatically, with zero new code — the resolver's own ranking rule
  produced the right outcome from data alone.
- Player meets Ferrand a second time (stage now 1, Grog still alive):
  the unconditional line's `min_stage:0` still clears the floor (it's
  a floor, not an exact match) and remains the only eligible line →
  fires again. This is the correct, intended behavior for a patron
  whose authored content is deliberately this thin — Ferrand doesn't
  need a stage-1 line to be a complete, working character; repeating
  the goal line is fine, the CONDITION swap is what carries his arc,
  not stage progression.

### Writing rules, unchanged from the first pass

**Connections are PROSE ONLY.** When patron B's line references patron
A, there is no engine check for whether the player has met A — the
line fires purely on B's own resolution, and the connection is
discovered by the PLAYER's memory, never verified by the game. This is
what keeps cross-patron texture cheap: no relationship graph, ever.

**Vague-reference rule**, hard constraint for any future writer: a line
may reference another character by NAME, ROLE/PROFESSION, or a past
ACTION/EVENT — never a physical or species descriptor. "That weird
healer" is legal. "That witch badger" is not. Character art isn't
guaranteed locked for every named patron, and this rule is what keeps
the lore layer safe to write far ahead of the art pipeline.

**In-world slang: "Fark."** The game's own name, repurposed in-fiction
   as a mild curse/exclamation — a small, cheap joke that costs nothing
   to implement and rewards a player who notices. Forms: "Fark" (bare
   exclamation), "for Fark's sake," "Farking [adjective]." USE SPARINGLY
   — an interjection dropped once in a while, never a tic repeated in
   every line. Overuse kills it.

## Why there is no ESCALATING central thread — refined, not reversed

A single voice reporting fixed STATUS on a fixed schedule has a real
replay-value problem: Fark is a repeated-run roguelike, so a player's
second, tenth, and fiftieth run all hit the same three lines in the
same order, and "word from the Hall" becomes recognized noise fast.
That principle still holds and still killed the Hall thread specifically.

What does NOT have this problem, and is worth building: a shared TOPIC
with MANY INDEPENDENT VOICES reacting to it, rather than one voice
reporting its status. The replay value comes from WHICH patron gets
drawn and HOW THEY PERSONALLY take it, not from a fixed sequence — the
same "different slice each run" property the small-connection web
already has, just anchored to one popular topic instead of scattered
across many. This is the shape for "the King" below: an ensemble of
short, personality-revealing reactions, no order, no escalation, no
required sequence, and (mostly) no resolution — the few that DO react
to elapsed time do so as one more independent voice's opinion, not as
a status update superseding the others.

This still runs through the same resolver as everything else — a new
pool TYPE (`reaction:<topic>`), not a new mechanism. The one new rule:
exclude lines the player has already heard from this pool THIS RUN when
drawing again, so a single run doesn't repeat the same reaction twice —
a simple per-run "already used" set, resets naturally with the run like
everything else here.

## Dialect: a small family of invented slang, not one gimmick word

"Fark" stays, but demoted to the rarest, mildest register — overused
before, per the correction. The richer, more frequently-reached-for
vocabulary is built around the game's OWN dice language, so it reads as
native rather than bolted on:

- **The Roller** — an unexplained folk personification of luck/chance,
  sworn by the way real speech swears by higher powers, never given
  lore beyond that. Generates a whole family on its own: *"Roller's
  teeth"* (mild exclamation), *"by the Roller"* (a light oath),
  *"Roller take it"* (real frustration), *"Roller's own luck"* (dry,
  said of someone catastrophically unlucky).
- **Bust-hand** — a noun. An insult for a fool or a habitual loser.
  Reuses "bust" in a different grammatical role than the mechanic uses
  it, so it colors the world without colliding with the game term.
- **Born rolling ones** — a compliment. Describes someone naturally
  gifted or lucky (1 being the single most valuable individual face,
  already meaningful to any player who's played a single match).

## The town: Thistleford

Named to echo Krox Thistledown's surname already on screen — local
family names deriving from local geography is free coherence once
noticed, costs nothing to set up. Three pieces of THIN town texture,
deliberately kept to three so the tavern stays the whole stage:

- **The Green Fair** — a spring festival, building anticipation.
- **Millstone Bridge** — out since midwinter, the council swearing it'll
  be fixed by spring, third year running.
- **A late frost** — threatening the early plantings. Can sit beside
  the Fair in the SAME line without either becoming a plot: *"Green
  Fair's near enough you can smell it. If the frost lets the orchards
  be."*

None of these need a stage ladder or a resolution — same "never
confirmed, never required" texture as everything else here, just kept
thinner and lower-frequency than a patron's own personal content.

## Anthropomorphic texture: idiom, never the punchline

The cast is all anthropomorphic animals, and that can flavor the
DIALECT the way real English borrows animal behavior into idiom —
*"stubborn as a badger in a hedge," "keeps his coin like a squirrel
keeps its nuts."* That second one fits Hollis's established coin-
anxiety without needing to know or ever state what species Hollis
actually is — it works as ambient vernacular anyone might use, not a
joke ABOUT a specific character's own species. Hard rule: never let an
idiom become a running gag pattern, never make species itself the
punchline of a line. One idiom folded naturally into a line here and
there is texture. Species-based jokes as a pattern is Zootopia, and
that's explicitly not this game's register.

## The King

An unresolved rumor that someone royal might visit before the season's
done — deliberately as thin as "a King," nothing more specified, ever.
Wide eligibility: most patrons, named or generic, can plausibly have
SOME opinion about a King visiting their town, so this pool should be
open by default rather than needing per-patron opt-in. Mostly flat
(`min_stage:0`, no conditions), proving the ensemble-of-reactions shape
works without any escalation:

- *"If he so much as brushes past me, I'm never washing this sleeve
  again."*
- *"Kings don't travel light, they say. Question is whether any of it's
  meant for spending in here."*
- *"A King, in Thistleford. Next you'll tell me the Roller pays her
  tabs."*
- *"If he does come, someone'll have to sweep. Won't be me, and it
  won't be you either, so who's left, then?"*
- *"A King's guard's purse is still a purse. Just saying."*
- *"Kings drink same as anyone once they're three cups in. Seen it
  before, don't much care to see it again."*
- *"Can't say what I'd even do. Bow, I s'pose. Never bowed to anyone in
  my life."*
- *"Bet the whole house on it being true. Bust-handed fool that I am."*

One line carries a `night_gte(6)` condition — the light-touch temporal
texture, still just one more independent voice's take, not a status
update: *"Season's near out and still no King. Told you lot. Told
you."*

A NAMED patron can also carry a PERSONAL, bespoke reaction that outranks
the shared pool under the same specificity rule already governing Peck's
gossip fallback — personal content wins over ambient content whenever
both are eligible. Ferrand gets one, demonstrating the pattern:
*"A King wants a game, he can find me. I don't run from crowns any more
than blades."* — distinctly Ferrand's bluster, not the everyman
ensemble voice.

## Seed cast

Six patrons, proving the shape: two who form a two-voice joke pair (the
CURSED SEAT scenario), one who carries a mechanical goal plus a debt-
connection to another, one repurposed as the low-frequency town-gossip
carrier, one with a goal that can react to real run progress, and two
who are fully standalone one-liners — proving restraint is a real
design choice here, not a gap.

---

**ODO** — trapper, rough trade, plausibly unwashed for entirely mundane
reasons. No goal, no stage ladder beyond the two lines below — this
character exists entirely to deliver the Cursed-seat joke and nothing
else.
- A DIFFERENT patron's line, fired when Odo is elsewhere in the room or
  gossiped about generally: *"That trapper in the corner — smoke's been
  round him three nights running. Somebody crossed him bad."*
- Odo's own line, when the player actually sits with him: *"Aye,
  cursed. Cursed by geography, mate. No bath house on the traplines.
  Sit if you dare."*
Works standalone either order; pays off best if the player's heard both.

**HOLLIS** — anxious, careful with coin, clerk-adjacent. GOAL: saving
toward a Ward enchant — "the shield," in his own words, never the game's
exact term. QUIRK: counts and recounts his coin visibly.
- Stage 0: *"Every coin twice bought, twice spent, twice worried over.
  I'll have my shield yet."*
- Stage 1: *"Owe the trapper a little still. He's not one to forget it,
  either."* (references Odo by role only — "the trapper" — legal under
  the vague-reference rule, recognizable by context to a player who's
  met him, meaningless if they haven't)

**PECK** — REPURPOSED, was the Hall-thread carrier, now the low-
frequency town-gossip carrier instead. Gossip/courier-adjacent
personality unchanged; content now pulls from a FLAT pool (no stage
ladder, no escalation, no required order — matches the "thin, never a
plot" texture the town section asks for), any one of which might fire:
- *"Green Fair's near enough you can smell it. If the frost lets the
  orchards be."*
- *"Millstone Bridge still out. Third year the council's sworn it'll
  be fixed by spring."*
- *"Frost took the early plantings. Good thing about a bad frost —
  cheap talk, that's all it costs you."*

**FERRAND** — proud, wounded pride, ex-soldier energy. GOAL: beat GROG
specifically and take his badge — an old grudge, deliberately never
explained further. QUIRK: bluster, refuses to admit fear. TRIMMED — the
Hall-touching second line is cut, no replacement needed; the goal-driven
content stands fine alone and demonstrates the condition system on its
own (see the worked example above):
- Stage 0 (Grog not yet beaten): *"Boot's mine. Bruiser owes me that
  much and worse besides."*
- Stage 0 (Grog already beaten this run): *"Someone beat me to it.
  Fark."*

**FENN** — quiet, solitary, cares about dice and nothing else. No goal,
no connections, one line, ever: *"Careful with the bone ones. Mine chip
if you look at them wrong."*

**TAM** — unreasonably devoted to the innkeep's cooking. No goal, no
patron connections — references the INNKEEP instead (safe, an
already-established character), one line, ever: *"Her stew alone's
worth the losing. Don't tell her I said the losing part."*

---

Connection density check on this seed batch: Odo, Hollis, and Ferrand
touch something beyond themselves (a debt pair plus a goal-condition) —
3 of 6 for PATRON-to-patron/mechanic connections specifically, closer
to 50% than the original 60% target, with Peck now carrying ambient
TOWN texture instead of counting as a patron-connection. If 60% patron-
to-patron density matters more than the exact mechanism, that's an easy
knob once the cast scales past six — more named patrons means more
opportunities for small pairs without needing every single one to
carry a connection. Fenn and Tam stay deliberately, fully standalone.

## Next steps (not done here, flagged for a decision)

- Scale target for the full named-cast pool — this seed is 6, proposing
  20-30 for launch; needs a call on how much authored content is worth
  building versus leaning on the existing generic system for volume.
- Whether named patrons need any art distinction from generic ones, or
  share the same portrait pipeline (recommend sharing it — inventing a
  visual "named-cast" tier would contradict the vague-reference rule's
  whole reason for existing, which is staying safely ahead of art).
- The Tankard badge's repurposing as tavern flavor (see the master
  brief's badge section) could live IN this system — "the tankard
  behind the bar, some say it's why nobody's robbed the till in forty
  years" — as a piece of unattributed house folklore nobody needs to
  confirm or deny. Proposal, not written yet.

## Cast expansion: 24 named patrons from real character art

Reviewed against actual portraits (Characters.zip). Species-family
confirmed against the naming system already established — the art
draws directly from those categorized name lists, which is why
identity below is stated with confidence rather than guessed. Krox,
Eira, Nebb, and Regis match the original Grog-table mockup exactly, so
they're grouped as an in-fiction justified cluster (regulars who've
sat his table before) rather than needing an invented reason to know
each other. Golgoth and Remny don't fit any prior category — treated
as true one-offs below.

This pass gives every character a full IDENTITY (species impression,
class/trade, demeanor) and locks the CONNECTION MAP. Not every
character gets a full multi-stage dialogue ladder yet — that's a
larger follow-on pass, flagged at the end rather than compressed into
this one. A handful of lines are written now specifically to prove the
best connections land in the established voice.

### Grog's regulars

In-fiction reason to know each other: they've sat his table before,
canonically, per the existing mockup.

- **KROX** — tanner, unbothered, still. The quiet one of the four.
- **EIRA** — sharp, watchful, does letters for people who can't.
- **NEBB** — restless where Eira's still. The two get mistaken for one
  another constantly and both hate it — a good, cheap two-voice bit:
  *"Not her. Never her. Ask again and I'll charge you for the
  insult."* (Nebb, stage 0)
- **REGIS** — self-appointed master of ceremonies at a table nobody
  asked him to run.

### Corvus's world

- **CORBIN** — clerk in the counting house, precise to a fault.
- **SPARR** — courier, never sits still long enough to be precise
  about anything. Contrast pair with Corbin, no scripted rivalry
  needed, the demeanor difference does the work.
- **PELL** — unconnected to either. A fletcher. Keeps the bird cluster
  from reading as one joke told three times.

### The hoofed thread

- **OSGOOD** — old soldier or old farmer depending who's asking, and
  he'll answer differently depending on his mood. Gruff.
- **RILLA** — his niece, runs a stall, worries about him more than he'd
  like: *"He'll tell you he was a soldier. Ask him which war and watch
  him change the subject."* (Rilla, stage 0, references Osgood by
  relation only)
- **DUNSTAN** — a smith. Entirely separate from the above two.

### Feline quartet, deliberately not a friend group

- **RASK** — muscle for hire, rough edges.
- **SIL** — the healer. CANONIZES the very first vague-reference
  example from this whole system's founding brief: another patron's
  line, unchanged in spirit, now has a real payoff — *"I think that
  weird healer put a curse on me self!"* resolves, for a player who
  meets her, into Sil's own dry deflation: *"No curse. Bad luck and
  worse ale. I can't fix either, but I can charge you for trying."*
- **THORNE** — a hunter, solitary by nature, minimal connective tissue
  on purpose.
- **VESS** — always closing a deal, mercantile instinct never off.

### Rodent cluster

- **NELL** — card-sharp, sharpest wit at any table she sits.
- **SQUIB** — her younger sibling, trouble: *"She taught me everything
  I know and still cleans me out. Tell me that's fair."* (Squib,
  stage 0, references Nell by relation)
- **TUCK** — the cook. CROSSES into the existing seed cast: a running,
  low-stakes rivalry with Tam over whose read on the innkeep's cooking
  actually counts — *"Tell whoever's been talking up her stew that the
  bread's the real work. Always has been."* (Tuck, stage 0, references
  Tam by role/topic only, never by name)
- **TWILL** — a weaver, meticulous, unconnected to the rest.

### Aquatic cluster

- **MUDGE** — a ferryman, brings news from downriver that occasionally
  flatly CONTRADICTS Peck's town gossip — a nice friction point between
  two unrelated, equally unverifiable sources: *"Whatever they're
  saying about the bridge in here, downriver says different. Believe
  whichever suits you."* (Mudge, stage 0)
- **NIX** — odd, the patron others half-jokingly blame for luck swings.
  Natural home for the Roller family of slang: *"Don't sit near me on
  a cold streak. I only carry the one kind of luck and it's not the
  Roller's."*
- **POLL** — repeats what he's heard slightly wrong, every time,
  including (occasionally) a garbled version of Peck's own lines — a
  non-linear payoff for a player who's heard both and catches the
  drift: *"Heard the bridge is fixed. Or burned. One of the two, m'
  sure."*

### Standalones

- **ROAN** — runs errands for the innkeep specifically. Loyal, little
  else needed.
- **GOLGOTH** — the most physically imposing design in the set, given
  almost nothing to say on purpose — same subversion the Odo-curse joke
  was built on. Looks like the one to be scared of. One line, ever:
  *"...No, go on. I was only sitting."*
- **REMNY** — insists he remembers things that plainly never happened.
  Talks past people more than to them. One line, ever: *"You were here
  Tuesday too. Don't tell me you weren't, I remember faces."* (delivered
  regardless of whether the player has, in fact, ever been here on a
  Tuesday — the joke is that he's simply always confident and always
  wrong)

### Connection density on this batch

Counting cross-links: Nebb↔Eira, Rilla↔Osgood, Squib↔Nell, Tuck↔Tam
(existing cast), Mudge↔Peck (existing cast), Poll↔Peck (existing cast),
plus the four-person Grog-table cluster and Nix's thematic tie to the
Roller slang — roughly 60% of this batch touches something beyond
itself, back in range after the seed set's smaller sample ran under
target. Golgoth, Thorne, Twill, Dunstan, Roan stay deliberately
standalone.

### Not done in this pass, flagged rather than compressed

Full multi-stage dialogue ladders (the stage-0/stage-1/goal-condition
pattern the original seed six have) for all 24 — this pass locks
identity and connections, which is the harder creative work and the
part most likely to need Denis's read before more time goes into
prose. Expanding each to a full ladder is a real next pass, scoped
separately rather than rushed here.
