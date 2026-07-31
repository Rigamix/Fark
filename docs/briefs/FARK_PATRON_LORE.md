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
SOME opinion, so this pool is open by default, no per-patron opt-in.

**RESTRUCTURED into three gated tiers — this closes a real continuity
bug, not a taste preference.** The original flat pool let a reaction
line ("I wonder if he'll bring gifts") fire before any patron had ever
established the rumor existed — a character responding to information
the player was never given. Fix: `heard()` conditions, reading off the
SAME per-run heard-set the resolver already maintains for de-dup
purposes — no new tracking, a new use of tracking that already exists.

**TIER 1 — INTRODUCTION** (`min_stage:0`, no conditions — this tier
must fire at least once before tier 2 or 3 can ever be eligible):

- *"Word from the Hall — someone's coming down this way before
  season's out. Might be, well. I don't rightly know who. Big,
  though."*
- *"Heard something odd today. Someone important, coming through.
  Nobody's said a name yet."*
- *"There's talk starting up. A visit, they're saying. Haven't heard
  the half of it myself."*
- *"First I'm hearing of it, but apparently there's a King thinking
  of coming this way."*
- *"Something's stirring beyond the usual gossip. A royal visit, if
  you believe it."*
- *"Innkeep's been extra particular about the place this week. Word
  is that's why."*
- *"Somebody mentioned a King might grace us with his presence. I
  laughed. They didn't."*

**TIER 2 — SPECULATION** (`conditions: [heard("king_intro")]` — every
line below requires tier 1 to have fired at least once this run first;
this is where the bulk of the original pool actually belonged all
along, since every one of these presupposes the rumor is already
known):

- *"If he so much as brushes past me, I'm never washing this sleeve
  again."*
- *"Kings don't travel light, they say. Question is whether any of
  it's meant for spending in here."*
- *"A King, in Thistleford. Next you'll tell me the Roller pays her
  tabs."*
- *"If he does come, someone'll have to sweep. Won't be me, and it
  won't be you either, so who's left, then?"*
- *"A King's guard's purse is still a purse. Just saying."*
- *"Kings drink same as anyone once they're three cups in. Seen it
  before, don't much care to see it again."*
- *"Can't say what I'd even do. Bow, I s'pose. Never bowed to anyone
  in my life."*
- *"Bet the whole house on it being true. Bust-handed fool that I
  am."*
- *"Word is he'll want a wife by the time he leaves. I've told my
  daughter to stay home that week."*
- *"Been hearing this exact rumor for three years running. Roller's
  own luck if it's ever true."*
- *"I'll take bets on it, actually. Even odds he shows, worse odds he
  sits down to play."*
- *"Not planning to be here that week, myself. Some of us have debts
  we'd rather a King not overhear about."*
- *"Nobody's told me how you're meant to address one. I'll just call
  him 'you' and hope for the best."*
- *"Won't change a thing about how I sit or how I drink. A King's
  still just a fellow with better tailors."*
- *"It's never the King himself worth watching. It's who he brings.
  That's where the real money walks in."*
- *"I've got a proposition ready, should he actually walk through
  that door. Every merchant in three towns has one, probably."*
- *"He'll owe somebody something by the time he leaves this place.
  Might as well be me."*
- *"Suspicious, if you ask me. Nobody just visits a place like this
  for no reason — and any bust-hand who tells you otherwise is
  selling something."*
- *"If he wants a game, I'm the one he should sit across from. Not
  being modest, just accurate."*
- *"I'll wager the whole thing's an excuse for the innkeep to charge
  double that week. Wouldn't blame her."*
- *"Half of me hopes he comes. Other half remembers what happened
  last time someone important visited anywhere I was standing."*
- *"Some say he plays dice himself. If that's true, Fark, I might
  actually be excited."*
- *"If it's true, I want to be the first to shake his hand. Or bow.
  Whichever's proper."*
- *"I've started practicing my best table manners, just in case.
  Feels foolish, doing it alone."*
- *"Wonder if he knows how to play. Real dice, not the polished kind
  they use up at the Hall."*
- *"My mother always said royalty smells like everyone else after a
  long ride. I intend to test that theory."*
- *"If he shows, I'm asking him straight out why. Politely. But
  straight out."*
- *"Half this town's already decided what they'll wear. I've decided
  not to decide."*
- *"A King in Thistleford would be the best story this town's told in
  years. True or not."*
- *"I keep picturing it wrong. Different crown every time I imagine
  it."*
- *"They say a King doesn't travel without at least a dozen watching
  him breathe. Can't imagine the noise."*
- *"If it happens, I want a seat with a view of the door. Best seat
  in the house, for once."*
- *"I've set aside my best coin, just in case there's a game to be
  had."*
- *"Told the family we might be entertaining royalty. They didn't
  believe me either."*
- *"Been saving a good bottle for the occasion. Might drink it myself
  if he never shows."*
- *"I've rehearsed what I'd say. Sounds a lot less impressive out
  loud than it did in my head."*
- *"If he plays, I'm sitting across from him myself. Somebody's got
  to."*
- *"Cleaned my best coat for the first time in a year. Feels like
  tempting fate."*

**TIER 3 — DEFLATION** (`conditions: [heard("king_intro"), night_gte(6)]`
— requires BOTH the rumor established AND late-run timing; still one
more independent voice's take, not a status update superseding the
others):

- *"Season's near out and still no King. Told you lot. Told you."*
- *"Starting to think the whole thing was somebody's idea of a joke.
  A slow one."*
- *"No King. No visit. Just a very long rumor that outstayed its
  welcome."*

**Why this stays "many voices," not a plot, despite the tiering:**
tiering enforces WHEN a category of reaction is allowed to fire, not
WHO delivers it or in what fixed sequence within the category — dozens
of different patrons across dozens of different runs can each deliver
a DIFFERENT tier-2 line, in any order relative to each other, as long
as SOME tier-1 line has fired first. That preserves the whole reason
the Hall thread was killed (no fixed, identical-every-run sequence)
while closing the actual bug (a reaction firing with nothing to react
to).

A NAMED patron can also carry a PERSONAL, bespoke reaction that
outranks the shared pool under the same specificity rule already
governing Peck's gossip fallback — personal content wins over ambient
content whenever both are eligible. Ferrand gets one, demonstrating
the pattern: *"A King wants a game, he can find me. I don't run from
crowns any more than blades."* — distinctly Ferrand's bluster, not the
everyman ensemble voice. (This bespoke override is exempt from the
tier gating — it's Ferrand's own reaction, not a pool entry, so it
follows his own stage rules per his personal pool, not the King
pool's tiers.)

## Seed cast

Six patrons, proving the shape: two who form a two-voice joke pair (the
CURSED SEAT scenario), one who carries a mechanical goal plus a debt-
connection to another, one repurposed as the low-frequency town-gossip
carrier, one with a goal that can react to real run progress, and two
who are fully standalone one-liners — proving restraint is a real
design choice here, not a gap.

---

**ODO** — trapper, rough trade, plausibly unwashed for entirely mundane
reasons. No goal. DEEPENED to match the standard the rest of the cast
now carries — the Cursed-seat joke is still his reason for existing,
but he's no longer down to exactly one line of his own.
- A DIFFERENT patron's line, fired when Odo is elsewhere in the room or
  gossiped about generally: *"That trapper in the corner — smoke's been
  round him three nights running. Somebody crossed him bad."*
- Odo's own lines (interchangeable, same specificity, resolver picks
  at random), when the player actually sits with him: *"Aye,
  cursed. Cursed by geography, mate. No bath house on the traplines.
  Sit if you dare."* *"Traplines don't care how you smell. Neither do
  the traps. We've an understanding."* *"You get used to your own
  company out there. Talking's a skill I'm a bit rusty at, if it's not
  obvious."*
Works standalone either order; pays off best if the player's heard both.

**HOLLIS** — anxious, careful with coin, clerk-adjacent. GOAL: saving
toward a Ward enchant — "the shield," in his own words, never the game's
exact term. QUIRK: counts and recounts his coin visibly. EXTENDED one
stage further, since his arc is a genuine, earned progression rather
than a flat pool — the system rewarding an actual saved-up goal is
exactly what stage-gating was built for.
- Stage 0: *"Every coin twice bought, twice spent, twice worried over.
  I'll have my shield yet."*
- Stage 1: *"Owe the trapper a little still. He's not one to forget it,
  either."* (references Odo by role only — "the trapper" — legal under
  the vague-reference rule, recognizable by context to a player who's
  met him, meaningless if they haven't)
- Stage 2: *"Almost there now. Just a little more, and I'll have my
  shield after all. Don't tell me the odds, I don't want to hear
  them."*

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
- *"Miller's raised his prices again. Third time this season. Might
  as well grind my own."*
- *"Someone's chickens keep turning up two streets over. Nobody's
  owned up to owning either the chickens or the trouble."*
- *"Roads are worse than the bridge, if you ask me, and nobody talks
  about the roads."*
- *"Heard there's a wedding coming before the Fair. Whole street's
  already arguing about whose garden gets used."*
- *"Someone's been at the grain stores again. Second time this month.
  Innkeep says it's rats. I've my doubts about the rats."*
- *"First proper sun we've had in a week. Won't last, but I'll take
  it while it does."*
- *"Cooper's apprentice ran off with a traveling show, they're
  saying. Or he just went to visit family. Depends who's telling
  it."*

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

- **KROX** — tanner, unbothered, still. The quiet one of the four:
  *"Still water and all that. I've heard every story this room tells
  twice over. Doesn't mean I need to say much back."* *"Leather
  doesn't rush. Neither do I. Works out."* *"You want noise, go
  bother Regis. I'll be here being unremarkable."* *"Ask me a question, I'll answer it. Ask me twice, you'll wait longer the second time."* *"Tanning's patient work. Rushed leather cracks. Rushed people do worse."* *"I've outlasted louder men than any at this table. Outlasting's a skill too."*
- **EIRA** — sharp, watchful, does letters for people who can't:
  *"Mistake me for Nebb again and I'll start signing letters in
  their name. See how they like that."* *"Half this room can't
  write their own name. I make a living off that, not that I'd say
  it to their face."* *"Watching costs nothing. Ask me what I've
  seen and it'll cost you plenty."* (mirrors Nebb below — same
  joke, other side, a bidirectional pair now rather than one voice) *"I've written apologies, threats, and marriage proposals this week alone. Guess which paid best."* *"People say more with what they don't write than what they do. I notice both."* *"Keep your secrets. I'll have them on paper eventually, one way or another."*
- **NEBB** — restless where Eira's still. The two get mistaken for one
  another constantly and both hate it — a good, cheap two-voice bit:
  *"Not her. Never her. Ask again and I'll charge you for the
  insult."* *"Can't sit still at a table where nothing's moving.
  Suppose that's my whole problem."* *"I hear things. Doesn't mean
  I say them. Mostly."* (Nebb, stage 0) *"Give me a task and I'm three steps into it before you've finished asking."* *"Eira reads people slow and careful. I just ask them straight out. Works about as well."* *"Sat still once. Didn't care for it. Haven't tried again."*
- **REGIS** — self-appointed master of ceremonies at a table nobody
  asked him to run: *"Someone has to keep order at this table. Grog
  certainly won't, and the rest of you are worse."* *"Someone at
  this table ought to have standards. Evidently it falls to me."*
  *"I've won here. I've lost here. Only one of those improved my
  posture."* *"Someone ought to announce the important arrivals properly. I've elected myself, since nobody else will."* *"I hold this table to a standard. The table, regrettably, does not always agree to be held."* *"A little ceremony never hurt anyone. A little more wouldn't hurt this lot either."*

### Corvus's world

- **CORBIN** — clerk in the counting house, precise to a fault:
  *"Every figure balanced twice before I sleep on it. Corvus doesn't
  abide a ledger that argues with itself."* *"A crooked column is
  worse than an honest loss. At least the loss tells you the
  truth."* *"I don't gamble. I audit people who do."* *"Corvus doesn't raise his voice. Doesn't need to, when the numbers already say everything."* *"I've seen more ruin from bad arithmetic than bad luck. Nobody wants to hear that."* *"Every ledger tells a story, if you're patient enough to read it straight."*
- **SPARR** — courier, never sits still long enough to be precise
  about anything. Contrast pair with Corbin, no scripted rivalry
  needed, the demeanor difference does the work: *"No time to sit
  proper. If I'm here, I'm between two places already."* *"Sit
  long enough in one place and you forget how fast the road
  actually is."* *"Ask me the news. I probably haven't caught up
  to it myself yet."* *"Fastest way between two towns isn't always the road. I've found a few shortcuts I won't share for free."* *"Feet don't rest easy. Never have. Doubt they'll start now."* *"I've delivered good news and bad in the same week to the same door. Neither changes how fast I knock."*
- **PELL** — unconnected to either. A fletcher. Keeps the bird cluster
  from reading as one joke told three times: *"Feathers are feathers
  to most. Mine fly true, which is more than I'll say for half this
  town's arrows."* *"Everyone wants the cheap shaft and the good
  feather. Can't have both, same as anything."* *"I don't play. I
  just like watching people lose to bad luck they could've bought
  better."* *"A good arrow's honest. Flies exactly where you aimed it, no better, no worse. Wish more things worked that way."* *"I don't need luck in my trade. Just a steady hand and better feathers than the next fletcher."* *"Watched plenty lose fortunes at this table. Never once watched an arrow lose on its own merit."*

### The hoofed thread

- **OSGOOD** — old soldier or old farmer depending who's asking, and
  he'll answer differently depending on his mood. Gruff: *"Ask me what
  I was before and you'll get a different answer each night. Pick the
  one you like."* *"Rilla worries too much. Somebody in the family
  has to, I suppose, and it isn't me."* *"Every scar's got a story.
  Mine have gotten better with age. The stories, not the scars."*
  (mirrors Rilla's tease about him — same bit, his own side) *"Youngsters ask too many questions about the old days. Old days don't answer back kindly."* *"I've buried better men than most at this table have met. Doesn't make for pleasant conversation, so I don't offer it."* *"Rilla thinks I don't notice her worrying. I notice. I just don't know what to do about it, same as her."*
- **RILLA** — his niece, runs a stall, worries about him more than he'd
  like: *"He'll tell you he was a soldier. Ask him which war and watch
  him change the subject."* *"Stall doesn't run itself. Neither does
  he, most days."* *"I'm told I smile too easy for this town. I've
  decided that's their problem."* (Rilla, stage 0, references Osgood
  by relation only) *"He won't say what he lost out there. I've stopped asking. Some things you let a person keep."* *"Every coin I make, I make twice — once for me, once in case he needs it and won't ask."* *"Folk think a smile means nothing's wrong. Sometimes it just means I've decided not to show it."*
- **DUNSTAN** — a smith. Entirely separate from the above two:
  *"Iron doesn't lie to you. Can't say the same for half what walks
  through that door."* *"Everything worth having gets hammered
  first. Applies to more than iron."* *"I fix what breaks. I don't
  ask why it broke. Keeps the work simple."* *"Bring me your broken things. I don't much care how they got that way."* *"Best trade in this town, and nobody thanks a smith till something breaks."* *"Fire doesn't care if you're patient. Neither do I, most days, but I've learned to fake it."*

### Feline quartet, deliberately not a friend group

- **RASK** — muscle for hire, rough edges: *"Work's work. Don't ask
  whose idea it was, ask if it paid — and don't ask the Roller
  either, she's never once answered me."* *"Don't ask what I did
  before this town. Ask what I'm doing tomorrow, that's the useful
  part."* *"Trouble finds the ones who go looking. I just happen to
  be standing where it lands."* *"I don't pick fights. I finish the ones other people start and forget to."* *"Ask around, they'll tell you I'm reliable. Ask nicely, and maybe they'll tell you why."* *"Most jobs pay in coin. The interesting ones pay in favors. I collect both."*
- **SIL** — the healer. CANONIZES the very first vague-reference
  example from this whole system's founding brief: another patron's
  line, unchanged in spirit, now has a real payoff — *"I think that
  weird healer put a curse on me self!"* resolves, for a player who
  meets her, into Sil's own dry deflation: *"No curse. Bad luck and
  worse ale. I can't fix either, but I can charge you for trying."*
  *"Half my custom thinks I'm cursing them. The other half thinks
  I'm curing them. Neither's quite right."* *"Bring me your aches,
  not your theories. I've no patience for the second kind."* *"I've fixed worse than a hangover with less thanks than this."* *"Folk come to me convinced they're dying. Usually it's just the ale talking. Occasionally it's worse, and then I earn my coin."* *"Cursed, poisoned, hexed — three different words for the same bad decision, usually."*
- **THORNE** — a hunter, solitary by nature, minimal connective tissue
  on purpose: *"Quieter out there than in here. That's the whole
  reason I go."* *"Town's got too many voices for my taste. Woods
  only ever say one thing at a time."* *"I don't miss much. Comes
  from years of not talking while others do."* *"Tracks don't lie to you the way people do. I prefer the company, honestly."* *"Spend enough time alone and silence stops being lonely. Starts being useful."* *"I hunt because I'm good at waiting. Most people aren't. Explains a lot about this table."*
- **VESS** — always closing a deal, mercantile instinct never off:
  *"Everything's got a price. Even the ones born rolling ones pay
  eventually — just later, and worse."* *"Everyone thinks they're
  the exception. Funny how the ledger never agrees."* *"I'll take
  your coin happily. I'll take your excuses less happily, and not
  for long."* *"I've sold rope to a man who owned a ship. Everyone needs something, even when they think they don't."* *"Fair price isn't the same as a low one. Took me years to convince people of that, and coin, mostly coin."* *"I don't gamble at this table. I just watch who's about to need a loan by morning."*

### Rodent cluster

- **NELL** — card-sharp, sharpest wit at any table she sits:
  *"Squib thinks I taught him everything. I taught him enough to
  lose interesting."* *"Cards don't lie. People do, constantly, and
  usually badly."* *"I could teach anyone to win. Wouldn't be half
  as fun watching them lose, though."* (mirrors Squib's line about
  her below — a bidirectional pair now, same pattern as Nebb/Eira) *"Every hand's a story if you're paying attention. Most people aren't, which is why I win."* *"Squib's got talent. Doesn't have patience yet. I didn't either, at his age."* *"I don't cheat. Don't need to. Watching's enough of an advantage most nights."*
- **SQUIB** — her younger sibling, trouble: *"She taught me everything
  I know and still cleans me out. Tell me that's fair."* *"One day
  I'll beat her clean. Today's not that day. Yesterday wasn't
  either."* *"Everyone's got a big sister who ruined gambling for
  them. Mine just did it with more style."* (Squib, stage 0,
  references Nell by relation) *"She says I've got talent. She also takes all my coin, so I don't know how much to trust the compliment."* *"I'm going to out-bluff her someday. Today's practice. So was yesterday."* *"Learned everything I know from watching her win. Still working on the winning part."*
- **TUCK** — the cook. CROSSES into the existing seed cast: a running,
  low-stakes rivalry with Tam over whose read on the innkeep's cooking
  actually counts — *"Tell whoever's been talking up her stew that the
  bread's the real work. Always has been."* *"Bread rises whether
  you believe in it or not. Faith's got nothing to do with baking."*
  *"Feed a table well and they forgive you almost anything.
  Almost."* (Tuck, stage 0, references Tam by role/topic only, never
  by name) *"Give me flour, water, and time, and I'll give you something worth losing money over."* *"Half this town thinks stew's the whole meal. Bread's doing the real work, quietly, same as always."* *"I've fed winners and losers the same plate. Losers eat slower. Winners don't taste a thing, too busy celebrating."*
- **TWILL** — a weaver, meticulous, unconnected to the rest:
  *"Every thread counted before it's cut. Rush it once and you're
  the bust-hand who ruined the whole bolt."* *"A crooked seam shows
  eventually. So does a crooked hand. I've an eye for both."*
  *"Patience isn't a virtue in my trade. It's the whole trade."* *"Cloth remembers every mistake you make in it. So do I, if I'm honest."* *"I've unpicked more bad work than I've ever started fresh. Most trades are like that, if you look close."* *"Slow and even beats fast and clever, every single time, in my trade at least."*

### Aquatic cluster

- **MUDGE** — a ferryman, brings news from downriver that occasionally
  flatly CONTRADICTS Peck's town gossip — a nice friction point between
  two unrelated, equally unverifiable sources: *"Whatever they're
  saying about the bridge in here, downriver says different. Believe
  whichever suits you."* *"River doesn't care what the town thinks
  it heard. Neither do I, most days."* *"Longest job in this town is
  being the one who actually saw something."* (Mudge, stage 0) *"I've carried more secrets across that water than fish, most days."* *"Folk say things to a ferryman they'd never say to a friend. Something about the water, maybe."* *"Peck hears it in here. I hear it out there. We rarely agree, and I rarely mind."*
- **NIX** — odd, the patron others half-jokingly blame for luck swings.
  Natural home for the Roller family of slang: *"Don't sit near me on
  a cold streak. I only carry the one kind of luck and it's not the
  Roller's."* *"Don't thank me if you win big near me. Don't blame
  me either. I only carry it, I don't hand it out."* *"Everyone
  wants my luck till they remember it comes with the rest of me."* *"I didn't ask for this reputation. Can't say I've done much to shake it either."* *"Bad luck's just luck that hasn't turned yet. I've been waiting a long while, myself."* *"The Roller doesn't play favorites. Everyone just remembers the nights she noticed them."*
- **POLL** — repeats what he's heard slightly wrong, every time,
  including (occasionally) a garbled version of Peck's own lines — a
  non-linear payoff for a player who's heard both and catches the
  drift: *"Heard the bridge is fixed. Or burned. One of the two, m'
  sure."* *"Heard it from someone who heard it from someone. Good
  enough for me."* *"I don't remember things wrong on purpose. It
  just comes out more interesting that way."* *"Told three different people three different versions of the same story today. All of them believed me. That's the real skill."* *"Facts get boring fast. I just help things along a little."* *"By the time a rumor reaches me, it's already wrong. I just make sure it stays interesting."*

### Standalones

- **ROAN** — runs errands for the innkeep specifically. Loyal, little
  else needed: *"She asks, I go. Don't need a better reason than
  that."* *"Ask me to fetch something and it's already halfway
  done. Ask me why and I've got nothing."* *"Loyalty's simple.
  Everyone else seems to make it complicated."* *"Don't need to understand every task. Just need to get it done before she asks twice."* *"Some folk think loyalty's owed. I think it's earned, and she's earned mine plenty."* *"I'm not much for talking. Better with my legs than my mouth, most days."*
- **GOLGOTH** — the most physically imposing design in the set, given
  almost nothing to say on purpose — same subversion the Odo-curse joke
  was built on. Looks like the one to be scared of. One line, ever:
  *"...No, go on. I was only sitting."*
- **REMNY** — insists he remembers things that plainly never happened.
  Talks past people more than to them. UNLIKE GOLGOTH below, expanded
  beyond one line on purpose — his joke is about being confidently
  WRONG, not about being silent, so more lines deepen the bit instead
  of undoing it: *"You were here Tuesday too. Don't tell me you
  weren't, I remember faces."* *"You had the amber die last time.
  Don't tell me you didn't, I remember these things."* *"We spoke of
  the King's visit already, you and I. Or someone did. Might've been
  you."* (all delivered with total, unearned confidence regardless of
  whether any of it happened — the joke is the confidence, not the
  accuracy) *"I never forget a face. Get the details wrong sometimes, but never the face."* *"You owe me a drink from last visit. Or I owe you one. One of us is right."* *"Funny how everyone remembers things differently. I remember them correctly. Differently, but correctly."*

### Connection density on this batch

Counting cross-links: Nebb↔Eira and Nell↔Squib are now true
bidirectional pairs (both sides carry a line referencing the other,
same pattern the Odo joke proved), Rilla↔Osgood likewise, Tuck↔Tam and
Mudge↔Peck and Poll↔Peck cross into the existing seed cast, plus the
four-person Grog-table cluster and Nix's thematic tie to the Roller
slang — still roughly 60% of this batch touching something beyond
itself. Golgoth, Thorne, Twill, Dunstan, Roan, Rask, Pell, Corbin/
Sparr (paired with each other but not the wider web), Vess stay
deliberately standalone or self-contained.

### Content volume — FULL ACCOUNTING, closed out

Started from a freshness measurement, not a guess: the original
1-line-per-patron, 9-King, 3-gossip volume produced an 84-95% repeat
rate across all three pools by a player's 10th run. Closing that gap
was staged across two passes; this section is the honest total.

**Named patron pools:** 23 of 24 now carry THREE interchangeable
lines each (randomly selected via the resolver's existing tie-break
rule — pure data, no new engine work). GOLGOTH stays at exactly one,
deliberately — his joke IS the sparseness, more lines would undo it,
not deepen it.

**`reaction:king`:** grown from 9 to 22 flat lines plus the one
night-gated deflation line (23 total). Kept to the same ensemble
principle throughout — every new line is a genuinely different
personality angle (etiquette panic, a betting angle, a marriage-
prospect joke, a gambling-dice challenge, entourage speculation, a
petition/debt angle, mixed dread-and-hope), not a rephrasing of an
existing one.

**`gossip:town`:** grown from 3 to 10 flat lines. Kept genuinely thin
in SUBJECT (still just small, mundane Thistleford texture — prices,
a stray-chicken nuisance, a wedding, a theft nobody's sure about) so
the town still reads as background, not a second setting competing
with the tavern.

**Seed six, deepened to the same standard where their design allows
it:** Odo goes from one line of his own to three (interchangeable).
Hollis gains a genuine stage 2 — his coin-saving arc actually pays
off now, which is exactly what stage-gating was built for. Ferrand
was already at comparable depth (two conditional variants plus a
personal King-override) and needed no further work. Fenn and Tam
stay at exactly one line each, same reasoning as Golgoth — their
minimalism is the character, not an unfinished draft.

**Slang density check across the whole expanded set:** roughly a
quarter to a third of lines in any given pool carry a Roller/bust-
hand/born-rolling-ones/Fark term — held deliberately steady at that
ratio through both passes, not allowed to climb as volume grew.

**What THIS pass could not close, because it isn't a writing gap:**
the seed six remain unseatable until they have portraits — no volume
of additional dialogue changes that, it's an art dependency, not a
content one. Scaling the named cast past 24 toward the original
30-patron target is the same kind of blocked: more writing without
more portraits doesn't move it. Both stay exactly where Round 3 of
the audit already flagged them.

**One concrete ask for Code, not yet just a suggestion:** if the
ambient pools' draw rate is anywhere near "half of all matches
attempt a reaction," cut it by roughly half. Measured against the
grown pool sizes above, pool growth alone still leaves the ambient
pools repeating 80%+ of the time by run 10 — throttling frequency is
what makes the growth actually pay off, the two levers compound and
neither alone is sufficient.

### Dialogue placement — CORRECTED

Does NOT belong on the patron peek sheet. The peek is built for a
"2-second read" (seal, dice, stake, SIT DOWN) — a fast mechanical
decision, and dialogue competes with that job rather than serving
it. Best current recommendation, pending confirmation: the WIN/LOSS
screen — already an established pause moment (the win/loss mockups
already show a character speaking there), and it's where a
condition-gated line like Ferrand's Grog-beaten variant actually
makes narrative sense (reacting to an outcome, not to a pre-match
glance). If a different destination gets settled on directly with
Code, update this section to match rather than leave two docs
disagreeing about where the resolver's output actually renders.

## In-match event reactions — NEW, was explicitly deferred, now built

Everything above reacts to ENCOUNTERING a character (stage counters,
conditions) or to pure atmosphere. Nothing reacted to what's actually
happening on the table, turn to turn — busting, banking big. Code
raised this exact gap two rounds ago; the answer at the time was to
hold off, because the pre-match personal-line content wasn't finished
and splitting effort across two surfaces before either was done would
have served neither. That reasoning is now stale — the pre-match side
is in a materially more complete state after the two passes above —
so the deferred piece is built now rather than left open indefinitely.

**Grain: TRAIT SEAL, not individual patron.** Every patron already
carries one of the six existing trait seals (STEADY, BULLISH, ORDERLY,
RECKLESS, GREEDY, CUNNING) — this reuses that field rather than
inventing new tagging work. Deliberately NOT written per-patron:
24 patrons x several event types x several lines each is 200+ lines
for personality nuance most of this cast hasn't earned yet at their
current depth. Trait-based coverage is smaller to write, applies to
EVERY match (not just the rare named-patron ones), and still delivers
real, distinct personality — a RECKLESS opponent busting reads
nothing like a STEADY one busting.

**ADDITIVE, never replacing the existing system.** The existing
64-call-site DLG system (hot dice, big banks, Drill Order) stays
exactly as it is for the generic case. This is a new pool
(`reaction:trait`, keyed by the CURRENT opponent's trait) that
resolves ahead of it via the same specificity rule used everywhere
else: a named patron's bespoke override (if one exists) beats the
trait pool, the trait pool beats the existing generic bark, and if
somehow neither applies, the existing generic bark still fires — the
event is never silent. "Big bank" reuses whatever threshold the
EXISTING bark trigger already uses; this does not define a second,
competing number.

**Four moments, six traits, TRIPLED to 72 lines (3 per bucket,
randomly selected at matching specificity, same mechanism as the
character pools — genuinely varied angle each time, not synonym-
swapped copies of the same sentence):**

- **STEADY** — bust: *"Well. That's that, then. Nothing for it but
  the next roll."* / *"No sense chasing what's gone. Next roll's the
  only one that matters."* / *"Didn't need that turn anyway. Plenty
  more coming."*
  your bust: *"Happens to the steadiest hand eventually. Don't take
  it personal."* / *"Even the patient ones go too far sometimes.
  You'll learn the line eventually."* / *"That's the game correcting
  itself. Happens to everyone, given time."*
  big bank: *"Slow and it adds up. Told you it would."* / *"Didn't
  rush it. Didn't need to."* / *"That's what waiting gets you. Every
  time, eventually."*
  your big bank: *"Lucky spread. Enjoy it, they don't come twice in a
  row."* / *"Fine bank. Won't be your last good one, I'd wager, but
  it won't be every time either."* / *"Steady hands make those too,
  now and then. Yours included, apparently."*
- **BULLISH** — bust: *"Fark it. Should've stopped a roll back."* /
  *"Should've quit while I was ahead. Never do, though."* / *"That
  one's on me. Won't happen twice tonight."*
  your bust: *"There it is. Knew you'd push too far."* / *"Greed'll
  do that. Every single time."* / *"Ha! Knew that turn had too much
  hope in it."*
  big bank: *"That's how it's done. Watch and learn."* / *"THAT'S a
  bank. Try and match it."* / *"Told you I don't play small."*
  your big bank: *"Fine roll. Won't happen again, mind."* / *"Not
  bad. Not better than mine, but not bad."* / *"Alright, that one
  earned a nod. Just the one."*
- **ORDERLY** — bust: *"Miscounted my odds, clearly. Won't happen
  twice."* / *"An error in my calculation. I'll adjust."* / *"Should
  have banked two rolls prior. Noted for next time."*
  your bust: *"Predictable, really. The dice favor patience, not
  greed."* / *"The odds always catch up. Every single time, without
  fail."* / *"Greed rarely survives contact with real numbers."*
  big bank: *"Exactly as planned. Every roll accounted for."* /
  *"Precisely the outcome I projected."* / *"Discipline, not
  fortune. There's a difference."*
  your big bank: *"An anomaly. The numbers will even out."* / *"A
  statistical outlier. Nothing more."* / *"Enjoy it. Regression is
  coming for us both eventually."*
- **RECKLESS** — bust: *"HA — worth it. Absolutely worth it."* /
  *"Worth every bit of that risk. Do it again in a heartbeat."* /
  *"Went down swinging. Only way I know how."*
  your bust: *"Told you! Told you to keep going!"* / *"SEE?! I love
  this game."* / *"You almost had me scared there. Almost."*
  big bank: *"See, THAT'S how you play this game."* / *"That's what
  happens when you actually COMMIT."* / *"Big or nothing. Just
  proved it."*
  your big bank: *"Now THAT'S a roll. Do it again, I dare you."* /
  *"Now we're talking! Do that again!"* / *"I respect that.
  Genuinely. Do it again so I can respect it more."*
- **GREEDY** — bust: *"There goes good coin. Every last piece of
  it."* / *"That hurts more than it should. Every coin, gone."* /
  *"Should've banked when I had the chance. Lesson learned,
  expensively."*
  your bust: *"Shame. All that could've been mine by now."* /
  *"Pity. I was already counting that in my head."* / *"Should've
  quit sooner. Their loss, my satisfaction."*
  big bank: *"Now THAT'S worth the seat price."* / *"Now THAT'S a
  night's work."* / *"Worth every coin I put on the table for this
  seat."*
  your big bank: *"That's my coin you're counting, near enough."* /
  *"Fine bank. I'll remember it, and I'll want it back eventually."*
  / *"That's a lot of coin walking away from me right now."*
- **CUNNING** — bust: *"Didn't want that turn anyway."* / *"That was
  intentional. Believe what you like."* / *"A necessary sacrifice.
  For reasons I won't explain."*
  your bust: *"Mm. Almost thought you had something there."* / *"Oh,
  unfortunate. Truly."* / *"I saw that coming. I always see it
  coming."*
  big bank: *"Exactly as I intended. Mostly."* / *"Everything's going
  precisely to plan. Whatever the plan is."* / *"Careful. I'm just
  getting started."*
  your big bank: *"Interesting. I'll remember that."* / *"Noted.
  Filed away for later."* / *"You'll regret showing me that,
  eventually."*

**Two bespoke named-patron overrides, proving the pattern rather than
attempting all 24.** Same specificity rule as Ferrand's King-reaction
override elsewhere in this doc — a named patron's own line beats
their trait bucket whenever it's actually worth writing one:
- Sil, own bust: *"No curse did that. Just bad dice."* (calls back to
  her established healer-deflection bit).
- Regis, own big bank: *"As I predicted. I predict many things."*
  (matches his established pomposity precisely).

**Not done here:** bespoke overrides for the other 22 — deliberately
left as trait-only for now, same "prove the shape, scale later"
pacing as everything else in this system. Which patrons deserve a
bespoke override is a taste call best made after seeing the trait
pool in actual play, not guessed at now.

### Volume status — current, honest, supersedes earlier notes in
this doc that are now stale

The ambient/structural layer got the volume pass: King restructured
into three gated tiers, 49 lines across tiers 2-3 plus 7 intro lines
(56 total, up from 23 flat); in-match trait reactions tripled from 24
to 72. Both were the highest-frequency-fire content, so they got
priority — a player encounters these far more often per run than any
single named patron's personal pool.

**NOT yet given the same volume pass: the 24 named-patron personal
pools.** They're still at 3 lines each (from the previous pass), not
the "many, so it doesn't repeat" depth the ambient and in-match pools
just received. This is a real, acknowledged gap, sequenced next —
not silently smaller because it matters less, but because doing
everything simultaneously at genuine depth in one pass risked
shallow, repetitive-feeling filler across 24 characters rather than
real variety. Named-patron bespoke in-match overrides (currently just
Sil and Regis) are the same kind of deferred-not-forgotten item.

## Win/loss reactions — patrons and bosses, NEW major addition

**Scope correction first, since it changes what belongs here:** win/loss
content must be about the OUTCOME specifically — "you beat me" / "I beat
you" — never general identity flavor redirected onto this screen. The
general backstory pools (the 138 patron lines, the King/gossip pools)
stay where they are; none of that content belongs here, and none of it
is duplicated below. This also means the earlier recommendation that
general backstory content renders on the win/loss screen was wrong in
scope — win/loss needed its OWN dedicated content, not a redirect. Where
the general backstory pool actually renders is a REOPENED, still-open
question — best current guess is the match-START moment (sitting down,
before the first roll), additive to the same in-match hooks the trait
reactions already use, but this is a guess flagged for confirmation, not
a ruling made here.

**Architecture: no new mechanism.** At match end the engine already knows
win or loss — that's how it picks which end screen to show. Filtering a
patron or boss's pool to only `outcome:win` or only `outcome:loss` lines
is one more condition, resolved the same way everything else in this
system resolves.

### Bosses — deeper than patrons, per "more personalised"

Two independent stage counters per boss (times lost to them, times beaten
them — NOT the same number, tracked separately), giving real
progression: stage 0 is the first-ever result of that type, stage 1 is
every subsequent one. Two interchangeable lines per stage, same random
tie-break as everywhere else in this system.

**GROG** — WIN (Grog beats you), stage 0: *"Hmph. Luck, that's all you
had. Try again if you've got the coin for it."* / *"That's the boot,
then. Don't say I didn't warn you."* stage 1: *"Back again? Some folk
never learn the shape of a losing streak."* / *"You're getting
predictable to beat. That's not a compliment."*
LOSS (you beat Grog), stage 0: *"Hmph. Lucky toss. I'll get you next
round."* / *"Fine. FINE. Take it. Doesn't mean you'll manage it twice."*
stage 1: *"You again. Starting to think that first win wasn't luck after
all."* / *"Alright. You've earned the right to stop gloating about it
now."*

**MABEL** — WIN, stage 0: *"There now. Everyone loses a hand now and
then, dear. Sit a while, have something warm."* / *"Oh, don't look so
glum. You'll have better luck with a full stomach next time."* stage 1:
*"Back so soon? I do worry about you, you know, even when you keep
losing to me."* / *"You're persistent, I'll give you that. Persistent
and hungry, probably."*
LOSS, stage 0: *"Well! Aren't you clever. Don't let it go to your head,
now."* / *"Beaten by a bit of luck and a full house, was I? Fine, fine.
Sit down, I'll get you something anyway."* stage 1: *"Twice now. I'm
almost proud, in a motherly sort of way."* / *"You keep this up and I'll
have to start taking you seriously."*

**FINNICK** — WIN, stage 0: *"Heh. Didn't even feel me take it, did you?
That's the trick of it."* / *"Better luck next time. Or don't. Suits me
either way."* stage 1: *"You keep coming back for the same trick. I keep
obliging."* / *"At this point I almost feel bad. Almost."*
LOSS, stage 0: *"Clever. I don't like clever. Clever costs me coin."* /
*"Alright, alright. You got the better of me this once. Don't let it go
to your head."* stage 1: *"Twice you've had my measure now. I'll need a
new trick."* / *"You're becoming a genuine problem for my business, you
know that?"*

**CORVUS** — WIN, stage 0: *"The numbers favored me tonight. They
usually do."* / *"A loss recorded, filed, and forgotten by morning.
Yours to remember, not mine."* stage 1: *"Another entry in the ledger.
You're becoming a reliable line item."* / *"I could set my books by how
often you lose to me. Comforting, in its way."*
LOSS, stage 0: *"Unexpected. I don't care for unexpected. I'll adjust my
figures."* / *"You've cost me tonight. I intend to recover it, one way
or another."* stage 1: *"Twice against the numbers now. I'm revising my
estimate of you."* / *"You're an anomaly I haven't priced in yet.
Uncomfortable, that."*

**BRUTUS** — WIN, stage 0: *"Discipline wins. Every time. Take that
lesson home with you."* / *"Three rolls, soldier. That's all you get at
my table. Learn it."* stage 1: *"Back for more drilling? Good. Some of
you need it repeated."* / *"Still haven't learned the count. We'll keep
at it till you do."*
LOSS, stage 0: *"...Hm. Discipline noted. Yours, this time."* / *"A fair
beating, soldier. Don't expect it to become a habit."* stage 1: *"Twice
you've held the line against me. I'm reassessing your training."* /
*"You're drilling well. I'll allow it, this once more."*

**ALDRIC** — WIN, stage 0: *"Thy cleverness forgets its breeding at
mine table. Confess it, and go in peace."* / *"A quiet lesson, freely
given. Take it as such."* stage 1: *"Thou returnest, still unconfessed.
Persistence is its own small virtue, I suppose."* / *"The same lesson,
again. I begin to wonder if it's landing at all."*
LOSS, stage 0: *"Well struck. I confess it plainly, as I'd ask of
thee."* / *"Mine own table, mine own lesson, turned back on me. Fair
enough."* stage 1: *"Twice bested. I begin to suspect thy cleverness
needs no quieting at all."* / *"A worthy return match. I'll not pretend
otherwise."*

**WHISPER** — WIN, stage 0: *"Mm. Predictable, in the end. I do so
enjoy being right."* / *"Marked dice sing loudest right before they
lose. Didn't you notice?"* stage 1: *"Back again. I do love a repeat
performance."* / *"Same result, different night. I'm not complaining."*
LOSS, stage 0: *"Oh. Well played. I'll remember that."* (echoes her
established CUNNING-trait line — she's the cunning boss, kept
deliberately consistent) / *"Unexpected. I do enjoy being surprised, on
the rare occasion it happens."* stage 1: *"Twice now. You're becoming
genuinely interesting to me."* / *"I'm starting to take you seriously.
Dangerous, for both of us."*

**AMBROSE** — WIN, stage 0: *"The house remembers your name. Tonight,
not fondly."* / *"A reckoning delivered. Come back when you're ready for
another."* stage 1: *"You keep returning to be reckoned with. I respect
the persistence, if nothing else."* / *"The house remembers every name
that's tried and failed. Yours is in good company."*
LOSS, stage 0: *"The house remembers your name. Tonight, rightly so."*
(the established line from the Ambrose victory card, reused deliberately
— not reinvented) / *"A reckoning, and I'm on the losing end of it.
Rare. Noted."* stage 1: *"Twice you've bested my table. The house is
taking notice of you now."* / *"You're no longer a name I'll forget by
morning."*

### Named patrons — flat, two lines per outcome, matching the volume
### standard, not the deeper boss treatment

**KROX** — win: *"Figured as much."* / *"No surprise there."* loss:
*"Huh. Wasn't expecting that."* / *"Fair enough. Didn't see it coming."*

**EIRA** — win: *"Predictable. I could've written that outcome down
before we started."* / *"Noted, and filed away."* loss: *"Well. I'll
need to revise my notes on you."* / *"Unexpected. I don't often say
that."*

**NEBB** — win: *"Course I did. Sat still long enough to prove it."* /
*"There we go. Told you I could focus when it mattered."* loss: *"Fark.
Didn't see that coming."* / *"Well, that's embarrassing. Won't happen
twice."*

**REGIS** — win: *"As I predicted. I predict many things."* / *"Order
restored to this table, as it should be."* loss: *"An aberration. I
shall permit it, this once."* / *"Well played. I suppose even I can be
surprised."*

**CORBIN** — win: *"The numbers favored me. They usually do."* /
*"Balanced, as expected."* loss: *"An error in my calculation
somewhere. I'll find it."* / *"Unaccounted for. I don't care for that."*

**SPARR** — win: *"Ha, quick as ever."* / *"Told you I don't slow down
for anyone."* loss: *"Didn't see that one coming, and I see most things
coming."* / *"Huh. You're faster than you look."*

**PELL** — win: *"Flew true. Same as always."* / *"No surprises from an
honest hand."* loss: *"Well. Even a good arrow misses sometimes."* /
*"Fair shot. I'll allow it."*

**OSGOOD** — win: *"Told you. Old hands still know a few tricks."* /
*"Experience wins out. Usually does."* loss: *"Hmph. Fair fight, that.
Rilla'll be pleased, at least."* / *"Well struck. Don't let it go to
your head, mind."*

**RILLA** — win: *"There, that's settled then."* / *"No hard feelings,
I hope."* loss: *"Oh! Well done, truly."* / *"That's a good win, that
is. Don't be modest about it."*

**DUNSTAN** — win: *"Solid work. Same as my forge."* / *"No cracks in
that outcome."* loss: *"Hm. Didn't see the weak point till it was too
late."* / *"Fair beating. I'll take the lesson."*

**RASK** — win: *"That's the job done, then."* / *"Nothing personal.
Just work."* loss: *"Huh. Didn't expect that from you."* / *"Fine. You
earned that one."*

**SIL** — win: *"No curse did that. Just good dice."* (mirrors her
established bust line exactly, deliberately) / *"Nothing to fix here.
You'll live."* loss: *"Well. Bad luck and worse dice, this time mine."*
/ *"Fair enough. I've had worse nights."*

**THORNE** — win: *"Quiet win. Prefer it that way."* / *"Didn't need to
say much. The result speaks."* loss: *"Hm. Missed that one."* / *"Fair.
Even a good hunter misses sometimes."*

**VESS** — win: *"Good outcome for me. Better for my ledger."* /
*"Everything has a price. Tonight, yours was steep."* loss: *"Well,
that's a loss I'll have to absorb."* / *"Fine deal, that. For you,
anyway."*

**NELL** — win: *"Told you. Cards don't lie, and neither do I about my
odds."* / *"That's how it's done."* loss: *"Huh. Didn't see that coming,
and I usually do."* / *"Well played. Genuinely."*

**SQUIB** — win: *"HA! Finally! Someone besides Nell!"* / *"See, I'm not
completely hopeless."* loss: *"Aw, come on. So close."* / *"Fine. FINE.
You got me."*

**TUCK** — win: *"That's the bread rising, same as always."* / *"Good
result. Good enough to celebrate with pie, maybe."* loss: *"Well, even
good bread falls flat sometimes."* / *"Fair enough. Feed you extra next
time, maybe."*

**TWILL** — win: *"Even seams. Every time."* / *"No mistakes in that
outcome."* loss: *"A dropped stitch, that was."* / *"Fair enough. I'll
unpick it and learn."*

**MUDGE** — win: *"Smooth crossing, that."* / *"No surprises on the
water tonight."* loss: *"Huh. Rough water, that."* / *"Fair enough. Even
the river surprises me sometimes."*

**NIX** — win: *"Told you. My luck, not yours."* / *"The Roller favored
me, this time."* loss: *"Ha! My own luck turned on me. Fitting,
really."* / *"Well, that's a first. Don't get used to it."*

**POLL** — win: *"Knew it'd go that way. Or something close to it."* /
*"Told everyone I'd win. Or I will, now."* loss: *"Huh, didn't see that
coming. Or maybe I did. Hard to say."* / *"Well, that's one story I'll
tell straight, for once."*

**ROAN** — win: *"Job's done."* / *"Simple as that."* loss: *"Huh.
Didn't expect that."* / *"Fair enough. Back to my errands."*

**REMNY** — win: *"Knew I'd win. I remember it happening before,
even."* / *"Course I won. I always do. Mostly."* loss: *"Well, that's
new. Don't remember losing before."* / *"Huh. I'll remember this one,
probably wrong, but I'll remember it."*

**GOLGOTH** — win: *"...Yeah."* loss: *"...Huh."* (deliberately just one
line each, no exception this time either — same reasoning as everywhere
else his entry appears in this doc)

### Volume tally, this addition

64 boss lines (8 bosses x 2 outcomes x 2 stages x 2 lines) + 94 patron
lines (23 x 2 outcomes x 2 lines, + Golgoth's 2) = 158 new lines.

### RESOLVED — the placement question above, and the earlier room-
### screen guess a few messages back. Both superseded by this, final.

Everything ambient — King ensemble, town gossip, the 138-line named-
patron backstory pool — lives INSIDE matches, at natural pauses,
spoken by whoever the player is currently facing. Not the room screen
(that guess is retracted), not a separate external screen at all.
"They don't have to live anywhere else" — the correct, simpler answer
this whole placement question was overcomplicating.

**Trigger: pause-based, not event-based — this is what distinguishes it
from the trait-reaction layer above.** The trait pool fires off SPECIFIC
mechanical events (a bust happened, a big bank happened). This pool
fires during NATURAL LULLS in a match's rhythm, unrelated to any
specific event — candidates: match start (sitting down, before the
first roll), right after a bank resolves and before the next roll,
during/just after the opponent's turn while the player is otherwise
idle. Pick RANDOMLY among whichever candidates are available each match,
rather than always firing at the same fixed beat — keeps the exact
moment from becoming predictable/expected.

**Rate: light-touch, proposed once per match as the starting default.**
This is ambient texture, not a firehose — firing at every available
pause point would turn flavor into noise. Tunable, same as the ambient
draw-rate knob proposed earlier in this document; adjust by feel once
it's actually playable.

**Speaker and priority: the CURRENT OPPONENT, same specificity rule as
everywhere else in this system.** If the player is facing a named
patron, that patron's own 6-line backstory pool is eligible and takes
priority. King and town gossip (widely eligible, per their own sections
above) fill in as the fallback — for a generic (unnamed) opponent, or
whenever the named opponent's own pool doesn't have anything eligible.
Personal beats ambient whenever both are eligible, the same rule
governing every other pool in this document.

**Additive to, not competing with, the trait-reaction layer.** A single
match can fire BOTH: a trait-based reaction when the opponent busts, AND
(independently, at a different pause point) one ambient/backstory line.
Two different layers, two different trigger types, same resolver, same
underlying architecture — this was always designed to support multiple
pool types running alongside each other, this is just the second one
actually specified with a real trigger mechanism rather than left as an
open guess.
