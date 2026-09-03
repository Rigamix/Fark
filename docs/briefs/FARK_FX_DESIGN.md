# EFFECTS, AS DESIGN — what makes one clear, and the timings that make it land

*2026-08-30. The companion to `FARK_FX_AUDIT.md`. That document says what
is broken in the plumbing. This one says what an effect is FOR, decides
what each family of effect in Fark should be, and gives the numbers.*

*One correction to the audit before anything else: it said Fark has two
canonical FX pipelines. **There are three.** I missed `FKFX` (18352–18516),
and it is the best-designed thing in this part of the file. Most of Part
Two is about what it already gives us.*

---

# PART ONE — HOW TO THINK ABOUT AN EFFECT

## 1. The only question that matters

Fark is push-your-luck. Strip everything else away and the player does
one thing, over and over: **look at the table, decide whether to roll
again.** That is the game.

So the test for every effect is not "does this look good." It is:

> **Does this make the next decision easier to make, and more exciting to
> make?**

An effect that is beautiful and does not touch that decision is
decoration, and decoration competes for the same attention the decision
needs. An effect that carries information the decision requires is
mechanics, and it earns whatever screen time it takes.

Everything below is downstream of that sentence.

## 2. Three jobs, three grammars — and never mix them

Every effect in a game like this is doing exactly one of three jobs.
They feel completely different and they need completely different
treatment. **Almost every clarity bug in Fark is one of these done in
another one's grammar.**

### BEAT — "something just happened"

A card fired. A die rerolled. Points scored. A die broke.

- **Instant, then gone.** 150–600 ms.
- **Anchored to the thing that changed**, so the eye is pulled to it.
- **Loud is fine.** It has the screen to itself and then it leaves.
- Its job is to say *what changed and because of what*.

### STATE — "this is true right now"

This die is frozen. This seat is fogged. This die is dampened. This brand
is spent.

- **Lasts as long as the fact.** Seconds, a turn, a match.
- **Must be readable with zero motion**, because the player reads the
  table while deciding, and a state that only exists during its animation
  is a state they have to wait for.
- **Quiet, and constant.** A state that pulses forever is a state that
  becomes invisible in ninety seconds — the eye filters repeating motion.
- Its job is to be *countable at a glance*: three dice, one of them
  frozen.

### THREAT — "this is what will happen if you do that"

Tap a die to break it. These two dice will be rerolled. This is the seat
that gets snuffed.

- **Lasts exactly as long as the choice is open.**
- **Marks a set, not a thing** — it says *which are eligible*.
- Must disappear the instant the choice is made or abandoned, or it
  becomes a lie.

**The rule: never render one job in another's grammar.** A state rendered
as a beat is a fact you saw once and can no longer check. A beat rendered
as a state is noise. A threat that outlives its choice is a bug the
player will read as one.

## 3. The clarity ladder

A state has to answer four questions, in this order, and each one fails
independently:

1. **WHICH?** Unambiguously anchored to one die. *(This is the misaligned
   square. It fails first and it poisons the rest — a mark you can't
   attribute is worse than no mark.)*
2. **WHAT?** Distinguishable from the other states at a glance. Colour
   and treatment do this. A glyph does not — see the budget below.
3. **HOW MUCH?** Intensity, if the effect has degrees.
4. **HOW LONG?** Remaining duration. **The one almost everybody skips.**
   "This seat is fogged" is half the information; "…for one more turn" is
   the half the player is actually making a decision with.

## 4. The readability budget — this is a phone

Six dice in a row. Each is 13cqw — about 50 px on a phone. That is the
whole budget and it forces three rules:

- **Colour and silhouette are the first read. A glyph is the second.** A
  10 px `❄` in the corner of a 50 px die is not readable at a glance and
  it is invisible while the die tumbles. A frozen die should be *blue,
  and look cold*; the snowflake is only the confirmation once you've
  already noticed.
- **One state per spot, visually.** Settled by ruling (§9b): one lane
  carries one mark, so no combined form ever has to be designed for the
  enchants. Non-enchant states — frozen, dampened, blind — still need a
  priority order, because they come from card effects rather than brands
  and can co-occur on one die. Rank them by what changes the player's
  decision most: **VEIL beats CRUST beats DIM** (a die you cannot read
  outranks one that behaves oddly, which outranks one that is out of
  play). Stacking two treatments on 50 px produces mud.
- **Peripheral legibility is the target, not foveal.** The player is
  looking at the score, or at their cards. The state must register
  without being looked at directly. That means value contrast and
  saturation, not detail.

## 5. Causality is read from ordering, not from arrows

If A causes B, the player learns it from **A visibly happening before B**.
Simultaneous reads as unrelated. This is the cheapest teaching tool in
games and it costs nothing but sequencing.

A corollary that matters here: when N things happen together, **stagger
them**. Stagger turns a mess into a count. Six dice reacting at once is
a flash; six dice reacting 70 ms apart is *six dice reacting*. Balatro's
entire scoring readout is this one trick.

## 6. Wind-up → strike → settle

The best-feeling effects have three parts, and the first is the one
people cut:

- **Wind-up** — something is about to happen. Even 80–120 ms of it moves
  the eye to the right place *before* the payload arrives, which is the
  difference between seeing an effect and having seen one.
- **Strike** — the moment itself. Short, hard, on the beat.
- **Settle** — the world is now different. This is where a beat hands off
  to a state.

**The missing wind-up is Fark's biggest single loss** and I'll name the
specific one in Part Two.

---

# PART TWO — WHAT FARK ACTUALLY HAS

## 7. There is a beat engine, and it is good

`FKFX` (18352–18516) is a proper effect grammar and I missed it in the
audit. It is:

- **Nine instruments** — `SET`, `PAY`, `COIN`, `STRIKE`, `TRANSFORM`,
  `FATE`, `BREAK`, `ARM`, `LEDGER` (18426). Each is a composed
  performance, not a single tween: `STRIKE` is flash → thud → shake →
  debris at +20 ms → dust at +80 ms.
- **Five primitives** — `_spray`, `_glow`, `_flash`, `_beam`, `_motion`
  (18381–18415), plus eight named sound families.
- **A power parameter** `p` (1–3) that scales intensity, so the same
  instrument plays louder for a bigger version of the same idea.
- **41 mapped ids** with a colour each, and a fallback that resolves an
  unmapped card to *its family's* instrument and *its family's* colour
  (18501). A new card gets a coherent effect by existing.

That last property is the good one. **This is exactly the architecture
I would have proposed.** It is already written.

**It has two call sites** (16038, 23931).

### What that costs, concretely

- **All ten `mat:*` rows are unreachable.** `mat:amber`, `mat:jade`,
  `mat:obsidian`, `mat:starstone`, `mat:ruby`, `mat:lucky` and four more
  are authored, coloured, assigned an instrument — and nothing ever calls
  `FKFX.play('mat:…')`. A whole vocabulary for what the premium dice *do*
  is written and silent.
- **Four of the five primitives don't work on a match die.** This is the
  audit's layer problem showing up inside the good system:

  | primitive | on a 3D match die | why |
  |---|---|---|
  | `_spray` | **works** | goes to `FX.emit`, z-index 9500, above everything |
  | `_motion` `dx/dy` | **works** | D3X reads the chip's rect for position (28951) |
  | `_motion` `sc` | **dropped** | table scale comes from `d.w0`, captured once |
  | `_motion` `rt` | **dropped** | D3X owns the quaternion |
  | `_glow` | **invisible** | drop-shadow on a chip under `#d3xCanvas` |
  | `_flash` | **invisible** | appends a div to the chip, same layer |
  | `_beam` | **invisible** | same |

  So `STRIKE` plays as sound + shake + debris (its shake is `dx` — it
  survives), while `SET`'s squash and `TRANSFORM`'s 360° spin are
  silently dropped. **`TRANSFORM` is the instrument for jade, bloom,
  cultivate and transmute, and its signature move does not play.**

  There is also a live hazard: `_motion` writes `opacity`, and D3X hides
  any die whose computed opacity is ≤ .02 (28984). An instrument that
  fades through zero deletes the die.

## 8. There is no state engine at all

**Every symptom Denis has reported is a STATE being faked with a BEAT.**

That is the whole diagnosis in one line, and it explains why the fixes
have never stuck: they were tuning the wrong grammar.

| the fact | how it is rendered today | which grammar it needs |
|---|---|---|
| this seat is fogged, until their turn | a 3.2 s `☁` at the moment it fires | STATE |
| this die is frozen | a box-shadow + a 10 px `❄` on an invisible chip | STATE |
| this die is dampened | a gradient on an invisible chip | STATE |
| this die can be broken | `cursor:pointer` and nothing else | THREAT |
| this brand is spent | a class, drawn by `_spentLook` | STATE (this one is right) |

Fog is the clearest case. The effect is *"the rival cannot see this
seat"* — that is a fact about the table that the player should be able to
look at and count on while deciding. It is currently a three-second
animation that plays once, after the decision it was supposed to inform.

## 9. The three moments Fark drops

Walk the Fog enchant end to end. Five moments; the game renders two.

| # | moment | job | today |
|---|---|---|---|
| 1 | the brand is on a face | STATE | ✅ baked into the die's UV — correct |
| 2 | **that face lands** | **BEAT (anticipation)** | ❌ **nothing** |
| 3 | you keep it — banks 0, fires instead | BEAT | ✅ `FKFX.play('ench:fog')` |
| 4 | **the rival's seat is marked, until their turn** | **STATE** | ❌ nothing |
| 5 | it resolves on their die | BEAT | ⚠️ a body-level emoji |

**Moment 2 is the best moment in the enchant system and it does not
exist.** Your branded face coming up is the little jolt the whole
purchase was for — it's the slot-machine cherry, the "oh, here we go."
It needs 200 ms of wind-up and nothing more. Adding it is close to free
and it is the single highest-value change in this document.

Moment 4 is the one Denis asked for by name, and it is a state.

## 9b. RULING: one mark per spot — and a die that is all enchant

**Denis, 2026-08-30, in two parts:**

> *"You can have several fog enchants. When an enchant is activated in
> match you can't have another one in that spot until it has affected the
> opponent (unless it's the one that gives you gold, etc)."*
>
> *"You should be able to have a die made entirely of enchants — when
> buying an enchant and it selects a face at random, it should not select
> a face with an enchant already there."*

**My earlier draft of this section proposed a purchase-time guard. That
was wrong** — it would have banned owning two fogs, which is the opposite
of the ruling. The exclusion is on the **spot**, at **fire time**, and
only for the enchants that occupy one.

### 9b.1 The rule, stated exactly

- **Occupying enchants** — `fog`, `snuff`, `snare`. They arm a lane and
  pay out on the rival's turn, so they hold a spot for a window.
- **Non-occupying** — `tithe` (gold), `trade`, `break`, `ward`. They
  resolve on the spot or on your own turn, hold nothing, and are never
  refused.
- **The rule:** an occupying enchant may not fire into a lane that
  already carries a live mark. Any type against any type — a second fog,
  or a snuff on top of a fog, both refused, on the same grounds.
- **The window ends when it has affected the opponent**, which is
  `_lmRetire` / the last `_lmSpend` — not when the turn ends.

### 9b.2 The current model gets this wrong in both directions

Three module keys, one per enchant type (23468, 23578, 23591):

```js
G._fog   = {lane, live, turn, turns}
G._snuff = {lane, live, turn, turns}
G._snare = {lane, live, turn, turns}
```

Because the key is the **type**, not the **spot**:

| case | should be | is |
|---|---|---|
| fog on lane 1, fog on lane 3 | **both live** — different spots | **impossible.** `_lmArm` is `G[key]=m` (24076), a plain overwrite. The first is silently lost — it fired, it played its beat, it logged *"FOG — THEY WILL NOT SEE THAT SEAT"*, it banked zero, and it did nothing |
| fog on lane 2, snuff on lane 2 | **refused** — one spot | **both live.** Two different keys, no one compares lanes |

So the model forbids exactly what Denis wants and permits exactly what he
doesn't. Neither is a tuning problem; the key is on the wrong axis.

### 9b.3 The fix: key the mark by the spot

```js
/* ONE MARK PER SPOT. Keyed by LANE, not by enchant type - which is the
   ruling stated as a data structure: two fogs on two lanes are two
   entries, and a second mark on one lane has nowhere to go. The three
   G._fog / G._snuff / G._snare keys collapse into this; _lmDue's callers
   ask "what is on lane N" instead of "where is the fog". */
G._laneMark = { 2:{t:'fog', turn:5, turns:2}, 4:{t:'snare', turn:5, turns:1} };
```

`_lmArm(key,lane,turns,extra)` becomes `_lmArm(t,lane,turns,extra)` and
**returns false when the lane is taken**, which is the whole enforcement:

```js
function _lmArm(t,lane,turns,extra){
  if(!G)return false;
  G._laneMark=G._laneMark||{};
  if(G._laneMark[lane]&&G._laneMark[lane].live)return false;/* the ruling */
  ...
  G._laneMark[lane]=m;return true;
}
```

Three read sites change shape (35911, 36234, 36300) and each gets
*simpler*: they currently search the rival's dice for one matching a
stored lane; now the lane is the key and the rival's die at that lane is
a direct lookup.

### 9b.4 What a refused brand does — and why it must not bank zero

`_iconFire` (23907) is built on one law: **a brand banks zero *because* it
fired.** If the fire is refused, the second half of that sentence is
false, so the first half must be too.

A refused brand **scores its natural face** — 100 for a 1, 50 for a 5 —
and stays branded for a later turn. Three things follow, all of which the
code has to honour together:

- `_iconFire` must return before it plays `FKFX`, before it logs, before
  it sets `brand-spent`, and before the `zero_hour` check (23940) — a
  brand that did not fire must not end the turn.
- The die leaves `_iconSel` and joins `_scoreDice`, so `_splitIcons`
  (23987, called at 32378) is where the refusal is easiest to apply
  cleanly.
- The player needs to be told, or they will read it as the brand failing.
  A short status line — *"THAT SEAT IS ALREADY MARKED"* — plus the die
  scoring normally is enough; nothing is lost, so it should not read as a
  penalty.

### 9b.5 "A die made entirely of enchants" — that is two faces, not six

This one has a constraint Denis may not have in mind, and it is measured
rather than arbitrary, so it is worth stating before anything is built.

**Only a natural 1 or 5 can take a brand** (`_iconFaces`, 41945 — and it
is the one place that decides). The comment there gives the reason and the
number:

> *"Branding a 2/3/4/6 is nearly free — those faces almost never score on
> their own (~8% of rolls) where 1 and 5 carry ~66% — so a brand there
> hands a would-be-bust roll a guaranteed non-bust alternative it would
> not otherwise have had: measured at a 25% flat cut in single-roll bust
> rate… the same unconditional safe keep Silver's original identity was
> deleted to remove."*

So a fully-branded die is **a 1 and a 5, both branded. Two enchants, and
the die can never score a point again.** Every face that was worth
something now does something instead.

**That is a better build than six faces would be.** It is a real
commitment — you give up the die's entire scoring contribution — and it
is legible: *this die doesn't make points, it makes things happen.* Six
branded faces would be the opposite: a die that can never bust, which is
the 25% bust-rate cut the design already rejected once.

**Denis confirmed 1-and-5, 2026-08-30. Settled — do not reopen it.**

There is a second reason it is the right restriction, and it is the one
that makes the whole feature safe: **branding a 1 or a 5 is bust-rate
neutral by construction.** Those faces already prevented a bust, so
turning one into an effect changes what the keep *does*, never whether a
legal keep exists. Branding a 2/3/4/6 would manufacture bust-preventers
that did not exist — which is the 25% above, and why the ceiling is two
brands rather than six.

### 9b.6 What the change costs

Lifting the one-brand-per-die cap is contained but not free. In order of
how much each touches:

| what | today | needs |
|---|---|---|
| `S.run.dieEnch[i]` | one `{t,face}` | up to two — face-keyed, `{1:{t},5:{t}}` |
| the sale guard (42285) | `if(S.run.dieEnch[i])return` | refuse only if **that face** is taken |
| `_iconFaceRoll(mat)` (41961) | draws from 1/5 by material only | must take the slot and drop already-branded faces — **this is Denis's ask, and it is two lines once the model above exists** |
| `_iconFire` (23907) | reads `d.ench.t` | read the brand for the **landed** face |
| `_dieIsIcon` (23856) / `_brandSpent` (23846) | `d.val===d.ench.face` | `d.val` is *a* branded face |
| the UV bake (25246, 25295) | composites one glyph into cell `(face-1)` | loop the faces; the cache key becomes the pair |
| `brand-spent` / `_spentLook` (23947, 27594) | per **die** | per **face** — a spent 1 must not grey out a die showing its 5 |

Note the sale guard already refuses when no legal face remains (`null`
from `_iconFaceRoll`, and the caller declines rather than branding
something illegal) — so "this die is full" is a path that exists and
just needs the second face added to the count.

**`_dieIsIcon` is the dangerous row in that table**, and it is worth
saying why rather than leaving it as one line among seven. `anyScoring`
decides whether a roll is a bust, and it already knows about brands:

```js
/* a branded face is a legal keep worth nothing, so a roll showing one
   is NOT a bust */
return !!(dice&&dice.some(_dieIsIcon));
```

`_dieIsIcon` is `d.val===d.ench.face && !_brandSpent(d)`. Both halves
break under two brands: `d.val` must match *any* branded face, and a
spent 1 must not disqualify a die showing its branded 5. Get either wrong
and the game **declares a bust on a roll that had a legal keep** — in a
push-your-luck game that is the worst possible defect, it takes the
player's whole turn, and it will read as the die being broken rather than
the check. Drive it directly: a die branded on both faces, rolled to each
of them, with the other brand spent, against a table with nothing else
scoring.

### 9b.7 What this does to the effects work

It raises the value of the two things Part Two already called out.

- **Moment 2 — the landing brand — becomes the main event.** A
  two-brand die lands a brand on ~33% of its rolls instead of ~17%. The
  anticipation beat stops being a nice touch and becomes the thing that
  makes the build feel alive.
- **The ink has to identify the enchant, not just say "branded."** One
  die can now be two different things depending on which face is up. §11's
  rule — one ink per idea, the same on the card, the brand, the beat and
  the state — is what carries that, and it stops being optional.
- **The refusal in 9b.4 needs its own small beat.** Not a failure sound:
  the brand scored instead. A brief DIM on the already-marked rival lane
  is the honest reading — *that spot is taken* — and it reuses the state
  layer rather than adding anything.

---

# PART THREE — THE GRAMMAR TO BUILD

Three vocabularies, deliberately narrow. The narrowness is the point: a
player learns four state treatments in a night, not twelve.

## 10. BEAT — keep FKFX, widen its reach

No new design. Fix the four dead primitives so the instruments play as
written, then call it from the places that should have been calling it:
material effects, card arming, die destruction, value changes.

**The rule for a new beat: it does not get its own code. It gets a `meta`
row.** If none of the nine instruments fits, that is an argument for a
tenth instrument — not for a bespoke effect. Nine is already generous;
adding a tenth should feel like a decision.

## 11. STATE — four treatments, and no more

A state is painted on the mark layer from `_hullOf` (audit §7), so it is
the die's real silhouette. Four forms cover everything Fark has:

| form | reads as | for |
|---|---|---|
| **RIM** | a coloured outline hugging the die | selection, eligibility, "this one" |
| **VEIL** | a translucent wash over the whole face | fog, blind — *you cannot read this* |
| **CRUST** | a treatment on the edges, face still readable | frozen, dampened — *it works differently* |
| **DIM** | desaturate + darken, no colour added | spent, committed, out of play |

Four rules that make them work:

1. **No idle animation.** A state is still. It may animate *on* (150 ms)
   and *off* (200 ms), and nothing in between. The current
   `seatMarkPulse 2.4s infinite` (3933) is a state pulsing forever, which
   is exactly the thing the eye learns to ignore.
2. **Colour is the identity.** Each state owns one, and it is the same
   colour its enchant/card uses everywhere else — the ink already exists
   in `ENCH_ICONS` (`fog:#a8b0b8`, `snare:#a888c0`, `ward:#9ab0d0`, …)
   and in `FKFX.meta`. **Do not pick new colours.** One ink per idea,
   across the card, the brand, the beat and the state, is how a player
   learns what purple means without being told.
3. **The glyph is optional and always secondary.** Draw it at ≥ 40% of
   the die's width, centred on the hull, never a corner badge. If it
   doesn't fit at that size, the state doesn't get a glyph — the colour
   carries it.
4. **Duration must show.** If a state expires, its form must carry the
   count. Cheapest version that works: the RIM drawn as N segments, one
   per remaining turn — two segments for a Kindred-doubled fog, one after
   it spends. Readable without a number, at 50 px, at a glance.

## 12. THREAT — one treatment, and it must be a set

One form: **a RIM in the acting card's own ink, on every eligible die,
plus DIM on every ineligible one.** The dimming is what makes it a set —
without it the player reads "these are highlighted" instead of "these are
the ones."

Two rules:

- **It appears with the prompt and dies with the choice.** Not a timer.
  It is bound to the armed state and cleared when the state clears —
  which is exactly the `_steadyDisarm` seam that already exists.
- **Break is the deliberate exception to "don't mark candidates."** P856
  cut candidate marking as noise and was right for Steady Hand, where any
  die is legal and the status line says so. Break marks a *subset* for a
  *destructive* pick — which are eligible is information the player needs
  to have before they commit. Keep it, and make it the only one.

---

# PART FOUR — THE TIMINGS

## 13. The bands, and what they mean

These are perceptual, not stylistic. Choose the band from the job.

| band | reads as | use for |
|---|---|---|
| **0–80 ms** | simultaneous | acknowledgement of a tap; anything that must feel like it was *your* doing |
| **100–200 ms** | snap — caused by input | wind-up; a state appearing; a card lifting |
| **220–400 ms** | a discrete event | the strike of a beat; a die reacting |
| **450–700 ms** | a small performance | a full instrument, a destruction |
| **> 700 ms** | waiting | only for something the player chose to watch |

**The hard rule: nothing the player sits through more than twice a turn
may exceed 400 ms.** A reroll happens constantly. A die shattering
happens rarely. They do not get the same budget.

## 14. Anchor everything to the roll

The game already has a fundamental beat and effects should be written
against it rather than picking round numbers:

- `KICK.ms = 460` — the throw
- `PHYS.cap = 700` — the hard ceiling on a die settling
- so **the roll-to-read cycle is roughly 500–700 ms**

That gives the spine:

> **Beats resolve inside the settle. States own the read.**

By the time the dice have stopped and the player is deciding, every beat
should be finished and every state should be steady and legible. A beat
still playing during the read is competing with the decision it exists to
inform.

Two consequences worth stating outright:

- An effect triggered *by* the roll (a landing brand, a material firing)
  has ~500 ms of cover and should use it — it costs no perceived time at
  all, because the player is already waiting for the dice.
- An effect triggered *by a tap* (a card, a reroll) has no cover, so it
  must be short. This is why the reroll budget below is tight.

## 15. Stagger

| n things | gap | why |
|---|---|---|
| 2–3 | 90 ms | reads as deliberate, each one lands |
| 4–6 | 70 ms | still countable, total stays under 400 ms |
| 7+ | 45 ms | accept it reads as a sweep, not a count |

Below 50 ms things merge. Above ~120 ms it drags. When in doubt, 70.

## 16. The timing sheets

**Card-driven reroll (Grog's Flask, Encore, Sleight) — total ≤ 400 ms**

| t | what | note |
|---|---|---|
| 0 | card acknowledges the tap | must be at 0 — this is "you did that" |
| +60 | card fires: `FKFX` instrument, its ink | the cause, before the effect |
| +140 | die 1 wind-up: RIM in the card's ink, 100 ms | the eye arrives before the change |
| +210 | die 1 value changes + spray | the strike |
| +210 | *die 2 wind-up begins* | 70 ms stagger from die 1 |
| +280 | die 2 value changes | |
| +380 | rims fade (200 ms) | |
| ~400 | table is readable | |

The card acting before the dice is the whole point. Right now everything
fires on frame 0 and the causal link is left for the player to infer.

**A brand landing (moment 2) — 200 ms, inside the settle, free**

| t | what |
|---|---|
| 0 | die settles |
| +80 | brand face: 120 ms RIM-in, in the enchant's ink, plus a 3-note `chime` |
| +200 | holds as a steady state for as long as the face is up |

Under a fifth of a second, entirely inside time the player is already
spending, and it converts "I own an enchant" into "it's happening."

**An enchant firing on keep (moment 3) — 300–450 ms**

Already correct. `FKFX.play('ench:'+t)` at the keep. One change: the
substitution is the mechanic — *it banks zero and does this instead* —
so the beat must visibly replace the score pop, not play beside it. If a
"+0" ever renders next to a firing brand, that is the bug.

**A lane mark (moment 4) — a state, not a duration**

| phase | treatment |
|---|---|
| arm (`_lmArm`) | VEIL fades in over the marked seat, 200 ms, enchant ink |
| hold | steady. No pulse. Segmented rim = turns remaining |
| spend (`_lmSpend`) | one segment drops, 150 ms |
| fire / retire | the beat plays, then the veil fades out over 250 ms |

**A die being destroyed — 550 ms, and it may be loud**

Rare, permanent, and the player chose it. `BREAK` + `D3X.shatter` already
do this and it is the best effect in the game. Leave it alone.

## 17. Interruption

One rule, and it is the same one the dialogue system needed:

> **A beat never blocks input. If the player acts mid-beat, the beat
> finishes on its own layer and the input is honoured immediately.**

The corollary: if an effect *must* be seen before the player acts, it is
not an effect — it is a prompt, and it gets a status line and an armed
state, like Break does.

## 18. `reducedMotion`

Motion goes, information stays. `FX.emit` already skips emission
(30998). Extend the same rule to the mark layer: **states still paint,
they just appear instantly instead of fading in; beats collapse to a
120 ms flash of their ink.** Never remove a state under reduced motion —
it is information, and the setting is about vestibular comfort, not about
playing with less of the game.

---

# PART FIVE — IMPLEMENTATION

Ordered so each step is independently visible and independently
verifiable. Nothing here is a new system.

1. **Fix FKFX's four dead primitives.** `_glow`, `_flash` and `_beam`
   move onto the over-canvas from audit §7.1 and paint on the hull;
   `_motion`'s `sc` and `rt` either drive D3X's scale/quaternion or are
   removed from the instrument definitions so nobody writes a keyframe
   that silently does nothing. **Guard `opacity`** so an instrument can
   never delete a die (28984). *All nine instruments become what they
   were written to be, and the two existing call sites get better for
   free.*
2. **Moment 2 — the landing brand.** ~200 ms, one new trigger at settle,
   uses the state layer once it exists. Do it early because it is the
   biggest feel gain per line in this document.
3. **Build the four state forms** (RIM / VEIL / CRUST / DIM) on the
   over-canvas, driven from state reads, not CSS classes. `selected` and
   `cardmark` port over first as the control: they work today, so if the
   port changes how they look, the port is wrong.
4. **Move the states onto it** — frozen, blind, dampened, spent — and
   delete the CSS from audit §3.
5. **Lane marks from `_lmArm`.** Arm-to-fire, both sides, segmented rim
   for turns remaining. This is Denis's original complaint and it is the
   first step that visibly answers it.
6. **Threat treatment** — Break's candidate set, rim + dim, bound to the
   armed flag.
7. **Wire the ten dead `mat:*` rows.** One `FKFX.play('mat:'+d.mat, …)`
   at the point a material's effect resolves. Ten authored effects come
   on at once; expect to re-tune `p` once they are audible together.
8. **`reducedMotion` pass** (§18) once both layers exist.

Steps 1, 3 and 4 are the same job seen from three sides, and together
they should remove more lines than they add.

---

# PART SIX — VERIFICATION

Design claims need design tests. These are the ones that can fail.

- **The glance test.** Freeze-frame a settled table with three different
  states live. Someone who has not seen it must name which dice are
  affected and how many kinds of thing are happening. If they need to
  watch it move, the state grammar has failed rule 11.1.
- **The count test.** Fog a seat for two turns. At any frame before the
  first spend, the remaining count must be readable without a number.
  Then spend one and check it changed.
- **Causality.** Record a card-driven reroll at 60 fps and step through
  it. The card's beat must have visibly started before the first die
  changes. If they share a frame, §16's stagger did not land.
- **The 400 ms rule.** Instrument every effect the player triggers more
  than twice a turn and assert its total span. Reroll, keep, select. Any
  one over 400 ms is friction, whatever it looks like.
- **No idle motion on a state.** Hold a settled table with a frozen and a
  fogged die for ten seconds and diff the mark-layer pixels between
  frames 60 and 600. Non-zero means something is pulsing that shouldn't.
- **Nothing outlives its cause** (from the audit, still the important
  one). Bust, hot-dice clear and destroy a die mid-effect; assert no
  state paints for a die whose state is false.
- **The instrument audit.** After step 1, play all nine instruments on a
  match die and confirm each one's signature move is visible.
  `TRANSFORM` spinning is the specific check — it is the one that is
  provably dropped today.

---

# THE SHORT VERSION

Fark has a good beat engine used twice, and no state engine at all. Every
clarity problem is a state being told as a beat: fog is a fact you need
while deciding, delivered as a three-second animation after the decision.

Build the four state forms, keep FKFX for beats, and give the branded
face its 200 ms of wind-up when it lands — that last one is the cheapest
good feeling on the table and it currently does not exist.
