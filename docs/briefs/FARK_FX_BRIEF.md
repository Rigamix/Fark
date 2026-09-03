# THE FX BRIEF — dice, cards and enchants: what an effect is for, what the file has, and what to build

*2026-08-30. **Supersedes `FARK_FX_AUDIT.md` and `FARK_FX_DESIGN.md`; delete
both.** They shared a spine and the second opened by correcting the first,
which is the duplication this project deletes rather than syncs.*

*Every line number is read from `fark_proto.html` as staged at Aug 30 12:11
— 81 citations checked, all resolve, plus 3.8's six (17511, 17520, 17958,
18123, 45415, 45459) read 2026-09-03 from the same copy. **P876 onward are
not in that copy**, so anything about them is from Code's reports, marked
where it matters. A re-stage is in hand; until it lands, treat offsets as
+628 to +1405 and re-resolve by symbol name, not by line.*

---

## 0. STATUS — read this first

**THIS FILE IS UNTRACKED, AND SO IS EVERY DOCUMENT I HAVE DELIVERED.**
`git status` shows `?? docs/briefs/FARK_FX_BRIEF.md`, and the same for
`FARK_DIALOGUE_VOICE.md`, `FARK_FX_AUDIT.md`, `FARK_FX_DESIGN.md`,
`FARK_BOSS_REWARD_BRIEF.md`, `FARK_DIALOGUE_AUDIT.md` and
`FARK_DIALOGUE_BUILD.md` — seven briefs outside version control. **I have
repeatedly described these as "committed to `docs/briefs/`". Writing a
file into a folder inside a repo is not committing it**, and the
consequence is concrete: a worktree checked out from git does not contain
this brief, so every instruction here that says "see the brief" has been
unreachable from a clean checkout. `git add docs/briefs/*.md`.

**And the supersession never happened.** `FARK_FX_AUDIT.md` (Aug 30
13:00) and `FARK_FX_DESIGN.md` (Aug 30 13:29) are still on disk beside
this file, which has instructed their deletion since the day it was
written. Three FX documents in one folder, two of them stale and
contradicting the third — the exact defect this brief exists to remove,
inside its own directory.

**Shipped: Part Six steps 1–6**, less one gap. P876/P877/P878 settled the
lane marks, the refusal and the harness; P879 took snare's miss to
`_lmSpend` and deleted `_lmRetire`; P880 built the over-canvas; P881–P883
fixed the FKFX primitives; P884 landed moment 2. Through `865752d`.

**Step 5 closed by P885.** The `sc` gap this brief claimed was wrong —
`sc` did reach the mesh, and P881's owner-routing is what carried it. It
was arriving at the wrong depth and duration, which is the real defect
P885 fixed by replacing the summary-statistic reduction with a keyframe
evaluator.

**`STATE_FORMS` shipped inert**, so nothing from P880–P883 is visible yet
beyond moment 2 and the corrected motion. That is the intended shape:
step 7 fills it.

**Settled by Denis, no longer open:** enchants occupy a spot, not a die
(3.1) · a mark that comes due either fires or misses, and both cost an
attempt (3.2) · a miss must look different from a fire (3.3) · brands go
on a natural 1 or 5 only, so two per die (3.4) · the lane is fixed at the
moment you keep the brand (3.5) · the difficulty levers are targets,
rewards and prices, never hearts (3.7) · a ghost or a mark follows its
die, not its seat (3.8) · silver drops to 120g / stock 3 as a placeholder,
its identity question deferred (3.9).

**The envelope is exact only under the unreachable-target harness — my
2026-09-02 justification for it was wrong.** `G.target` is shared
(`_handBackOrCap`), and `simTurn` banks the moment `myTotal+turn+bankAdd
>= target` (45808), *before* the policy closure is asked. I verified that
the closure ignores the target and wrote it as though `simTurn` did.
Truncation is real, so per-turn yield is stationary only once the target
is out of reach — which is exactly what Code built. **4c replaces the
ceiling with reach probability**, because a max-of-n only rises with n
and cells are compared against each other.

**Waiting on Denis: nothing. All four cleared 2026-09-03.** The anchoring
question turned out not to be a question (3.8 — the intent was written
down at P844 and the mechanism contradicts it); silver's price comes down
and the number falls out of 4b's instrument (3.9); two-brand support is
scheduled after step 7 (item 6); the repo is being re-staged so line
numbers can be verified rather than carried. Snuff's gate mismatch stays
recorded as residual.

**Shipped since:** P914 (`sanity()` turn cap — a match ending on the cap
is a complete match, asked *why* it ended rather than widening the band)
· P889 (step 7, the mark roster) · P919 `0715c13` (3.8) · P920 `ba11297`
(driver bust counter + the `banks+busts===pTurns` identity).

**Code's queue, in order:** 4b/4c → two-tier outcome smoke test
(requirement 4) → the ladder run → two brands.

---

# PART ONE — HOW TO THINK ABOUT AN EFFECT

## 1. The only question that matters

Fark is push-your-luck. Strip everything away and the player does one
thing repeatedly: **look at the table, decide whether to roll again.**

So the test for every effect is not "does this look good":

> **Does this make the next decision easier to make, and more exciting to
> make?**

Decoration competes for the attention the decision needs. Information the
decision requires earns whatever screen time it takes.

## 2. Three jobs, three grammars — and never mix them

**Almost every clarity bug in this game is one of these rendered in
another's grammar.**

**BEAT — "something just happened."** A card fired, a die rerolled, a die
broke. Instant then gone, 150–600 ms, anchored to what changed. Loud is
fine: it has the screen and then leaves. Its job is *what changed, and
because of what*.

**STATE — "this is true right now."** This die is frozen, this seat is
fogged, this brand is spent. Lasts as long as the fact. **Must be readable
with zero motion** — the player reads the table while deciding, and a
state that only exists during its animation is one they have to wait for.
Quiet and constant: a state that pulses forever becomes invisible in
ninety seconds, because the eye filters repeating motion. Its job is to be
*countable at a glance*.

**THREAT — "this is what happens if you do that."** Tap to break, these
two will reroll. Lasts exactly as long as the choice. Marks a **set**, not
a thing. Disappears when the choice is made or abandoned, or it is a lie.

A state rendered as a beat is a fact you saw once and can no longer check.
A beat rendered as a state is noise. A threat that outlives its choice
reads as a bug.

## 3. The clarity ladder

Four questions, in order, each failing independently:

1. **WHICH?** Anchored unambiguously to one die. Fails first and poisons
   the rest — a mark you cannot attribute is worse than no mark.
2. **WHAT?** Distinguishable from the other states at a glance. Colour and
   treatment do this; a glyph does not.
3. **HOW MUCH?** Intensity, where the effect has degrees.
4. **HOW LONG?** Remaining duration. The one almost everyone skips. *"This
   seat is fogged"* is half the information; *"…for one more attempt"* is
   the half the decision actually uses.

## 4. The readability budget — this is a phone

Six dice, each 13cqw — about 50 px. That is the whole budget.

**Colour and silhouette are the first read; a glyph is the second.** A
10 px `❄` in the corner of a 50 px die is unreadable at a glance and
invisible while the die tumbles. A frozen die should be *blue and look
cold*; the snowflake only confirms what you already noticed.

**One state per spot.** Settled by 3.1 for enchants. Non-enchant states —
frozen, dampened, blind — come from cards and can co-occur on one die, so
they need a priority order. Rank by what most changes the decision:
**VEIL beats CRUST beats DIM** (a die you cannot read outranks one that
behaves oddly, which outranks one out of play).

**Peripheral legibility is the target.** The player is looking at the
score or their cards. Value contrast and saturation, not detail.

## 5. Causality is read from ordering

If A causes B, the player learns it from **A visibly happening before B.**
Simultaneous reads as unrelated.

And when N things happen together, **stagger them** — stagger turns a mess
into a count. Six dice reacting at once is a flash; six dice 70 ms apart
is *six dice reacting*.

## 6. Wind-up → strike → settle

**Wind-up** — 80–120 ms that moves the eye to the right place *before* the
payload. The difference between seeing an effect and having seen one.
**Strike** — short, hard, on the beat. **Settle** — the world is different
now; this is where a beat hands off to a state.

This structure also gives the miss its shape (3.3): **a miss is wind-up
and settle with the strike removed.**

---

# PART TWO — WHAT THE FILE ACTUALLY HAS

## 7. Three canonical pipelines, and all three are good

**`FX.emit`** (30993–31120) — pooled particles, hard cap 300, sleeps when
idle, dpr clamped to 2, dt clamped to 32 ms, respects `reducedMotion`
(30998), shared shape table so a canvas particle and a DOM sparkle are one
silhouette. Six named spawners plus four inline emitters, one emitter. It
already does sprite-sheet playback.

**`_hullOf` + `_paintHalo`** (26645, 26712) — the die's eight corners
projected through the camera and gift-wrapped into a real convex hull,
repainted per frame. The correct answer to "follow the die's actual
shape", and it exists.

**`FKFX`** (18352–18516) — a full effect grammar. Nine instruments (`SET`,
`PAY`, `COIN`, `STRIKE`, `TRANSFORM`, `FATE`, `BREAK`, `ARM`, `LEDGER`,
18426), each a composed performance rather than a tween. Five primitives
(18381–18415) plus eight sound families. A power parameter `p`. 41 mapped
ids with inks, and a fallback resolving an unmapped card to *its family's*
instrument and colour (18501) — a new card gets a coherent effect by
existing.

**The gap is reach, not architecture.** `FKFX` has two call sites (16038,
23931). The hull painter serves two marks. Everything else is ad hoc.

## 8. The layer map — corrected

| z | element | knows the die's… |
|---|---|---|
| in-flow | `.die` chips in `#playerDiceRow` / `#oppDiceRow` | **centre, yes** — see below |
| 3 | `#dgCanvas`, hull painter (26637) | centre, size and rotation |
| 41 | `#d3xCanvas`, the WebGL dice (2893) | everything |
| 60 | `.fog-float` / `.peek-float` / `.honey-float` / `.vang-float` (4448) | centre, via a rect read |
| 9500 | `#fxLayer`, particles (31003) | centre, via a rect read |

**Sizing the mark canvases to the dice band.** `_paintHalo` sizes its
scratch to `cv.width/cv.height` (26721) and `_drawGlow` sizes `cv` to the
whole `#screen-match` rect — so shrinking the output canvas shrinks the
entire mip chain with it. Marks only ever appear around dice, and the
markup makes the band a *static* question rather than a measured one:

```html
<div class="above-dice-info" id="aboveDiceInfo"><div class="kept-tray" id="keptTray">
<div class="throw-line"      id="throwLine">   <!-- BOTH dice rows share this cell -->
<div class="kept-zone"       id="keptZone">    <!-- absolute, top:100%, reserved height -->
```

The two dice rows are not two places — they share one grid cell, so there
is no HUD gap to span, and the band is contiguous.

**But only two of the three reserve height, and the markup comment lies
about the third.** An earlier draft of this section cited three comments
as evidence and did not check the CSS behind them:

| container | reserved? | |
|---|---|---|
| `#throwLine` | yes | holds the dice |
| `#keptZone` | yes | `.kept-zone{padding-top:15cqw}` (2779) — proportional, correct |
| `#aboveDiceInfo` | **no** | `min-height:0` (4560), and its only child is `.kept-tray{display:none}` (4533) until `.has-items` (4538) |

So `#aboveDiceInfo` measures zero and **grows when the tray populates**,
which is what the markup's *"fixed height to prevent shifts"* claims to
prevent. Two consequences: the band cannot be measured in a state where
the tray is hidden, since a mark on a tray die would be clipped; and
whether the throwing row visibly moves on first keep is worth a look on
its own, separately from the band.

The band is therefore `union(#throwLine, #keptZone, tray-when-shown)` plus
the mesh rise and the glow reach, computed **once per layout** — but the
third term has to be measured with the tray up, not inferred from a
comment.

**Express the mesh rise in `cqw`, not pixels.** The mesh is drawn above
its DOM slot — measured at 19.8–23.2 px on a 430×900 device, and it does
not rise further in flight. But dice are `13cqw` (2727) and the kept zone
already reserves in `15cqw`, so the rise scales with the viewport. A
hard-coded 23 px clips on a tablet.

Hulls stay in `#screen-match` coordinates; only the transform moves:

```js
x.setTransform(dpr,0,0,dpr, -band.left*dpr, -band.top*dpr);
x.clearRect(band.left, band.top, band.width, band.height);
```

Same substitution for `g` and `S` inside `_paintHalo`. Nothing about the
blur, the punch, the line or the dials changes.

**`_slaveHost` (25709) is the fact that corrects the earlier audit.** It
projects each die's world position through the camera and writes
`d.chip.style.translate` every frame, at both match call sites (28875,
28922). The chip *is* dragged under the drawn die. The earlier claim that
"a DOM chip is not where the die is" was wrong.

**But it moves the chip's centre and nothing else.** The chip keeps its
flex-slot size and takes no rotation. So a CSS effect on a match chip is
in the right *place* and still the wrong *shape and size* — which is the
half of Denis's complaint that matters, since he described a square, not
an offset.

That gives the layer rule:

> **Marks that must match the silhouette — RIM, VEIL, CRUST, DIM — need
> `_hullOf`, and therefore a canvas. Marks that are a badge near the die —
> duration pips, a glyph, a number — are chip-anchored and work today.**

`#dgCanvas` sits at z 3, under the dice, which is right for a rim and is
why the selection glow reads as a halo. Anything that must cover a face
needs its twin above `#d3xCanvas`. Two canvases, one number apart — not a
sixth layer, and not a replacement for the chip anchor, which is free and
already correct for badges.

## 9. What is dead, invisible, or fighting itself

**A warning about every count in this section.** These are censuses of
*markers*, not of *mechanics* — they answer "what adds this class", not
"what does this thing". The two differ wherever no canonical seam exists.
Reroll is the proof: four sites wore `card-reroll`, and building the state
row turned up **three more reroll paths that never wore it** — Steady
Hand, Powder Keg and Quicksilver, none of which had any mark at all.
Quicksilver's own comment had recorded it years earlier (P684, *"the free
reroll was invisible — the face just changed"*). A row built on the four
that happened to carry the class would have worked on its one built path.

The rule that predicts where this bites: **where a canonical seam exists,
a class census is safe, because every path goes through the seam.**
`_setDieVal` makes value-changes countable; `_removeDieAt` makes removals
countable. Reroll had no seam, so its class census under-reported by 43%.
Any mark whose predicate reads a class rather than a state is suspect on
the same grounds, and freeze and blind are the two left in that shape.

**Nine classes still paint an axis-aligned box on a match die**:
`card-reroll` (4200), `crr-blue` (4213), `card-reroll-settle` (4221), the
four `eff-glow-*` (4154–4157), `die-frozen` (4305), `die-blind` (4298).
Each is specificity (0,2,0) with `!important`, and each sits *after*
`.die.d3on{box-shadow:none!important}` (2811), so each wins.

**Four more paint nothing at all.** `.die.d3on::before,::after{display:
none!important}` (2812) kills every pseudo-element, so `die-dampened`
(4170), `die-dampened-fresh` (4184), `die-kindred` (10083) and
`combo-glow` (4003) are **invisible in 3D, not misaligned.** Dampened is
a state with no representation whatsoever. That is a quieter failure than
a wrong square and it has been shipping unnoticed.

**Only one FKFX primitive reaches a settled die.**

| primitive | on a match die | why |
|---|---|---|
| `_spray` | **works** | goes to `FX.emit` at z 9500 |
| `_motion` `dx/dy` | **fights `_slaveHost`** | animates `translate` — the property `_slaveHost` writes inline every frame. `_slaveHost`'s own comment documents choosing `translate` *because* transform animations outrank inline style; `FKFX` reintroduces the bug on the safe property. STRIKE's shake detaches the hit box from the die for 240 ms |
| `_motion` `sc` / `rt` | dropped | table scale comes from `d.w0`; D3X owns the quaternion |
| `_glow` | dead | drop-shadow on an element with no opaque pixels |
| `_flash`, `_beam` | invisible | append a div to a chip under `#d3xCanvas` |

So `TRANSFORM` — the instrument for jade, bloom, cultivate and transmute —
plays as a sound and a spray with its 360° signature dropped.

**A live hazard:** `_motion` writes `opacity`, and D3X hides any die whose
computed opacity is ≤ .02 (28984). An instrument that fades through zero
deletes the die.

**Ten `mat:*` rows are unreachable.** `mat:amber`, `mat:jade`,
`mat:obsidian`, `mat:starstone`, `mat:ruby`, `mat:lucky` and four more are
authored, coloured and assigned an instrument. Nothing calls
`FKFX.play('mat:…')`.

**The flat 2D path is dead.** `window.D3_MATCH` is read three times
(23741, 25136, 29077) and assigned nowhere in the page; `location.hash`
appears zero times. Deleting the flat CSS costs players nothing. *(Code
reports three probes setting it on a `#flat` hash — not in the staged
`tools/`, so unverified here; cut them in the same patch.)*

**Three cleanup sweeps, three hand-written lists** (32614, 33328, 34295).
They overlap, disagree, and none clears `card-reroll`, `card-reroll-settle`,
`crr-blue`, `die-dampened`, `dampen-fade`, `die-blind`, `die-frozen` or
`die-kindred` — those rely entirely on their own timers. Deleting the CSS
deletes the lists too.

**`reducedMotion` is honoured by the good pipeline and ignored by the bad
one.** `FX.emit` skips emission; `body.reduced-motion` gates two CSS rules
in the whole file. None of the thirteen effect classes respects it.

## 10. Two constraints on the painter that shape the state layer

`_drawGlow` (27049) computes:

```js
var skip=!anyMatch||this._rolling();
if(!skip){ skip=true; for(...) if(q.chip.classList.contains('selected')){skip=false;break;} }
```

**It skips unless something is `selected`.** That is the cardmark hole:
Steady Hand removes `selected` and *then* adds `cardmark`, so the mark
never painted unless another die happened to be selected. P856 moved the
mark onto a painter that refuses to run in the state P856's own call site
creates. Code has fixed it (P876, measured 12490 px against a control that
zeroes) — see §8 for what the report did not say.

**It also skips while `_rolling()`.** A state must persist *through* a
roll — a fogged lane stays fogged while dice tumble. **The state pass
cannot reuse this guard**, and must not inherit the cost argument at 27085
(*"this canvas is only painted while dice are selected"*) that justified
it.

## 11. The three moments the enchant lifecycle drops

| # | moment | job | today |
|---|---|---|---|
| 1 | the brand is on a face | STATE | ✅ baked into the UV |
| 2 | **that face lands** | **BEAT — anticipation** | ❌ nothing |
| 3 | you keep it: banks 0, fires instead | BEAT | ✅ `FKFX.play('ench:'+t)` (23931) |
| 4 | **the rival's seat is marked until it resolves** | **STATE** | ❌ nothing |
| 5 | it fires, or it misses | BEAT | ⚠️ a 3.2 s body-level `☁` |

**Moment 2 is the best moment in the system and it does not exist.** Your
branded face coming up is the jolt the purchase was for. `_dieIsIcon`
(23856) is already the predicate for it. ~200 ms, inside the settle, free.

Under 3.4 a die can carry two brands, so it lands one on ~33% of rolls
rather than ~17% — which turns moment 2 from a nice touch into the thing
that makes the build feel alive.

---

# PART THREE — THE RULINGS

Denis's decisions, in one place, so nothing is re-litigated.

## 3.1 An enchant occupies a spot, not a die

You may own several fogs. What you may not do is fire an occupying
enchant into a lane that already carries a live mark — any type against
any type.

**Occupying:** `fog`, `snuff`, `snare`. **Non-occupying, never refused:**
`tithe`, `trade`, `break`, `ward`.

**The current model is keyed on the wrong axis.** Three module keys
(23468, 23578, 23591), one per *type*, each holding one lane. So two fogs
on two lanes are impossible — `_lmArm` is `G[key]=m`, a plain overwrite
(24072) — while fog and snuff on *one* lane both live, because nothing
compares lanes across two keys. It forbids what Denis wants and permits
what he doesn't.

The fix is one map keyed by lane:

```js
/* ONE MARK PER SPOT. Keyed by LANE, not by type - the ruling as a data
   structure: two fogs on two lanes are two entries, a second mark on one
   lane has nowhere to go. The three G._fog / G._snuff / G._snare keys
   collapse into this. */
G._laneMark = { 2:{t:'fog',turn:5,turns:2}, 4:{t:'snare',turn:5,turns:1} };
```

`_lmArm` returns false when the lane is taken; that return *is* the
enforcement. The three read sites (35911, 36234, 36300) each get simpler —
they currently search the rival's dice for a stored lane, and the lane
becomes the key.

**P877 shipped the refusal half only.** Two fogs on two lanes still
collide, because refusal cannot reach a case where the second lane is
legitimately free. Only the re-key fixes that. Code declined it inside
the rival's scoring path, correctly — fog splices parallel arrays under a
P491 comment about shifting indices.

## 3.2 A mark that comes due either fires or misses — both cost an attempt

**`turns` is a count of attempts, not of turns the mark lurks for.**

This reverses part of P876, and the ruling arrived after the patch, so no
blame attaches:

- **Fog and snuff were already correct.** Their unconditional `_lmSpend`
  inside the due block (35915, 36265) *is* miss semantics. A Kindred fog
  with two attempts that misses the first still gets the second. What the
  patch called "burning a window turn on a no-op" is the miss. **Back that
  change out.**
- **Snare is the one that is broken, and has been.** It calls `_lmRetire`
  only inside its success branch (36307). On a miss it does nothing, so
  the mark keeps `live:true` with `turn` pointing at the turn that just
  passed — `_lmDue` (24079) is false for ever after. Live for ever, due
  never. Snare arms with `turns:1` (23468) and its Kindred halves twice on
  one shot, so the whole fix is `_lmRetire('_snare')` on the miss path.
- **The comment above `_lmRetire` (24084) taught the wrong lesson.** It
  presents Snare as the considered pattern when Snare is the one missing a
  case. Rewrite it: a due mark always costs an attempt; `_lmRetire` is for
  effects whose hit consumes the whole window.

Under this rule no mark can outlive its count, so the immortal-mark
interaction between the re-arm and the refusal disappears by construction.
No cap needed.

## 3.3 A miss must look different from a fire

**A miss is wind-up and settle with the strike removed** — the veil lifts
and fades over ~250 ms, no flash, no sound, no particles. Same motion,
absent impact. It reads as *nothing was there* rather than as an error,
and it needs no new vocabulary.

The stakes are low and the visual should say so: the brand is permanent
(`S.run.dieEnch` persists), so a miss costs one attempt, not the enchant.

## 3.4 Brands go on a natural 1 or 5 — two per die, and such a die never scores

`_iconFaces` (41945) is the one place that decides, and its reasoning is
measured: branding a 2/3/4/6 is nearly free — those faces score alone ~8%
of the time against ~66% for 1 and 5 — so a brand there hands a would-be
bust roll a guaranteed non-bust alternative, at **25% off the single-roll
bust rate**, *"the same unconditional safe keep Silver's original identity
was deleted to remove."*

So a fully-branded die is a 1 and a 5, both branded, and **it can never
score a point again**. That is the better build: a real commitment, and
legible — *this die doesn't make points, it makes things happen.*

**Branding a 1 or 5 is bust-rate neutral by construction.** Those faces
already prevented a bust; turning one into an effect changes what the keep
*does*, never whether a legal keep exists. The two-brand ceiling falls out
of the same fact rather than being a separate limit.

## 3.5 The lane is fixed at the moment you keep the brand

`_iconFire` reads `_laneOf(d)` at fire time, and P844 (17511) states that
a Vagabond reorder is *"COSMETIC — same dice, same values, new seats."*

So **dragging a branded die before you keep it aims the mark; dragging it
afterwards does nothing**, because the mark then belongs to the rival's
seat.

That is a free synergy — no new code — and it makes Vagabond a targeting
tool rather than only a sequencing one. It is a read, not a lottery: the
rival's hand is a fixed roster per rung (36046), usually six and sometimes
five, and visible in the loadout panel, so a fog on the last lane against
a five-die rival misses every time. Misses stay possible in any lane,
since `_oFree` filters the rival's already-kept dice (36222) — so
targeting improves the odds rather than guaranteeing the hit, which is the
right shape for a bet.

## 3.6 A rule lives in the canonical predicate, not in a consumer

`_dieIsIcon` (23856) has **twelve readers**. P585's comment argues the
case directly: *"The test belongs here because this is the canonical
predicate — `_splitIcons`, `_iconOnTable`, `_iconRescuesRow`, the bust
check and `_markLoneCast` all read it, so the rule lands everywhere at
once rather than being restated per consumer."*

**P877 put the refusal in `_splitIcons` (23989), one reader of twelve.**
Two concrete divergences follow:

- `_markLoneCast` (33306) builds `_plain = free.filter(d=>!_dieIsIcon(d))`
  and sets `on = lone && _dieIsIcon(d)`. A refused brand still reads as an
  icon, so it is marked *will cast* — and then scores 100. A visual
  claiming an effect that will not happen, which is the exact bug class
  this whole workstream exists to remove.
- Last Stand (33142) gates on `!_dieIsIcon(free[0])`, deliberately. A
  refused brand alone on a 1 is now a plain scoring die, but the gate
  still sees an icon and declines to fire.

And 18232's comment asserts the parity outright — *"Reuses `_dieIsIcon`,
the same predicate `_splitIcons` itself uses"* — which the patch makes
false.

**Move the refusal into `_dieIsIcon`, beside `_brandSpent`.** A refused
brand is not a live icon for the same reason a spent one isn't. It should
be smaller than what shipped.

---

## 3.7 The difficulty levers: targets, rewards, prices — not hearts

**Denis, 2026-08-30.** If the ladder confirms the run-win projection sits
below the recorded 25–35% target, hearts stay at three. The available
levers are night targets, match rewards and die prices.

The order to reach in, and why it is not arbitrary:

**Prices first.** They are the only one of the three with an independent
correctness standard — a price can be *wrong*, where a target or a reward
can only be tuned. Silver already has evidence against it: two silver beat
two 100g irons by 0.8–1.3pp, inside noise, at 580g. Correcting that is
justified on its own merits and shortens the mid-game as a side effect,
which is one change carrying two arguments.

**Rewards second.** They move every player through the middle faster
without changing what any single match feels like. Safe, but blunt — a
multiplier on the whole economy.

**Targets last, and locally.** This is the only lever that touches the
core loop. A lower target means fewer turns, less pushing, less of the
tension the game is made of. If it is used it should be at the tiers where
the failure concentrates, not globally.

**The reason for that order is where the failure sits.** `PWIN[2]`
overstated by 18 points means the model believed the *middle* of a run was
far easier than it is — the player has escaped band 1, has not reached
band 3, and is losing more than half their seats with three hearts. That
phase should be tense, but it should be **short**. Being stuck there
losing coin flips for three nights is a duration problem wearing a
difficulty problem's clothes, and prices and rewards shorten it where
targets only soften it.

---

## 3.8 A ghost or a mark follows its die, not its seat

**Denis, 2026-09-03.** A pickpocket ghost and a honeytrap mark stay with
the die they were placed on. A Vagabond reorder moves them.

The reasoning is the same shape as 3.5 read from the other end. A lane
mark is aimed at a *seat on the rival's board* — you chose the seat, so
the seat is the promise, and it stays put. A ghost is placed on *a die* —
you chose the die, so the die is the promise. Two anchors is not an
inconsistency; it is each mark holding on to whichever thing the player
actually picked. The failure mode the other way is worse than untidy:
Vagabond could shuffle a mark off the die you aimed at and onto one you
didn't, which is a reorder doing something the card says it doesn't do
(*"scores normally — value is positioning"*, 14449).

### 3.8.1 This is already the stated intent — the code just doesn't do it

The comment at 17511 says it outright:

> *"P844: a vagabond reorder is COSMETIC — same dice, same values, new
> seats. It must not void a promise; **the floats just follow their
> dice.** Ghosts and marks are lane-stamped at mint for exactly this."*

So this is not a design choice that was never made. It was made, written
down, and then contradicted by its own mechanism, because the reorder
**renumbers `d.lane` on the die objects** (45415, `c.die.lane=L`). The
stamp at mint (17958, 18123) records the lane the die was *in*; after a
reorder that lane holds a different die, and `byLane[+g.dataset.lane]` at
17520 hands back the wrong one. `_famRefloatGhosts` runs at 45459 —
*after* the renumbering — so it reads fresh lanes against a stale stamp
every time.

Lane-stamping was never wrong. It just needs to move when the lanes move.

### 3.8.2 The fix is a third entry in a loop that already has two

The reorder's `_carry.forEach` (45406–45415) exists to carry lane-stamped
state across the renumbering, and it already carries two things — with
the scars to prove it:

```js
if(_ftBefore>=0&&c.die&&c.die.lane===_ftBefore)G._fairTrade.lane=_slots[i];
(G._tradeSwaps||[]).forEach(function(t,ti){
  if(t&&_tsBefore[ti]===c.die.lane)t.lane=_slots[i]; });
```

P530 taught it the loan's seat. P531's comment records what happened
next: *"P530 taught this loop to carry the loan and left its sibling
behind — measured, the die moved from seat 0 to seat 3, the loan followed
and the ledger stayed at 0."* The ghosts are the third sibling, and they
have been sitting there since P844.

Add them the same way, with the same discipline the two neighbours
already document:

- **Snapshot before the loop writes anything.** `_tsBefore` exists
  because *"an entry that has already moved gets matched a second time"*
  — the ghosts need their own `_ghBefore` for exactly that reason.
- **`lane` moves, `oLane` never does.** Honeytrap marks that reference
  the rival's board are untouched by a player reorder, per P531's rule.
- **Nothing changes in `_famRefloatGhosts`.** It keeps doing lane lookup;
  the lane is simply correct when it runs.

That is the whole change, and it is the 3.6 shape: the rule lives where
lanes are renumbered, not in each consumer of a lane. **Every future
lane-stamped thing enrols here** — which is the sentence that should go
in the comment, because this loop has now been extended three times by
someone discovering a sibling left behind.

---

## 3.9 Silver's price comes down

**Denis, 2026-09-03.** Silver is overpriced at 580g. Cut the price rather
than buff the die — a buff big enough to justify 580g reopens the
unconditional-safe-keep problem silver's original identity was deleted to
remove (3.4's measured 25% bust-rate cut), so it would be paying for the
price tag with the design.

**The direction is measured; the number is not.** What is measured: two
silver beat two 100g irons by 0.8–1.3pp — inside noise — and after the
sim fix silver busts at 0.62 against bone's 0.78 and clone's 0.58. So
silver does something, and that something is worth a great deal less than
5.8 irons.

**AMENDED 2026-09-03 — measured, and the answer is bigger than a price.**
At 14/arm silver's per-turn yield is indistinguishable from iron's and
1.5× is excluded (item 4). Iron costs 100g. So **silver is dominated at
any price above iron's**, and cutting 580g to 250g leaves it dominated —
a strictly worse buy that merely costs less. The pricing lever cannot fix
this on its own: either silver drops to roughly iron's price and stops
pretending to be a premium die, or it needs an effect the harness can
see. **The one thing the measurement cannot rule out is defensive value
near the target**, which the unreachable-target harness is blind to by
construction — so "silver is for surviving the last turn of a close
match" is a live design answer, and it is testable with reachable-target
matches at a high tier.

**RULED, Denis 2026-09-03: "make it cheap for now."** Silver goes to
**120g, stock 3** — shipped, and confirmed on disk at 12920.

**PROVENANCE CORRECTION.** Every "580g" in this section and in §3.9 above
was stale: **P892 had already cut silver to 320g** before any of this was
written. So the premium being argued against was 3.2× iron, not 5.8×, and
the lines reading "must earn ~5.8× iron" and "cannot rescue a 5.8×
premium" overstate by nearly a factor of two. **The ruling's destination
is untouched** — 320g against a measured 71–128g is still 2.5–4.5×
overpriced — but the figure was wrong, and the cause is that I reasoned
from a staged copy of `fark_proto.html` frozen at Aug 30 12:11 that was
never replaced. This is the first place that staleness reached a shipped
number rather than a caveat.

- **120g is inside the measured interval.** Fair value is 0.71–1.28×
  iron's 100g, i.e. 71–128g. 120 sits near the top of that — the benefit
  of the doubt goes to the defensive value the harness cannot see — and
  it collides with neither iron at 100 nor flint at 150.
- **The stock has to move with it, or the shop tells two stories.**
  `{mat:'silver', price:320, stock:1}` — the stock of 1 is the
  *second place* "silver is premium" is written down, and repricing alone
  leaves a 120g die carrying jade's scarcity. Stock 3 puts it beside lead
  and amber, where a cheap utility die belongs. One fact, two homes: the
  same defect class as the rest of this brief.
- **It is a placeholder and the file should say so.** The identity
  question is deferred, not answered. A comment at the price should
  record that the number came from an instrument blind to end-game
  defence, so whoever revisits it knows what was established and what
  was not.

**Price it with the instrument that is already being built.** Requirement
4b's mean per-turn yield is exactly the quantity a die's price should be
set against: run it once with two silver and once with two iron, same
policy, same band, and the difference *is* silver's contribution in
points per turn. That is the same instrument doing a second job rather
than a second experiment, and it means the price lands on evidence
instead of on my guess. Until it runs, the honest statement is *"far
closer to iron than to 580g"* and nothing more precise.

---

---

# PART FOUR — THE GRAMMAR

## 12. BEAT — keep FKFX, widen its reach

No new design. Fix the four dead primitives so the instruments play as
written, then call it where it should already be called: material effects,
card arming, die destruction, value changes.

**A new beat does not get its own code. It gets a `meta` row.** If none of
the nine instruments fits, that is an argument for a tenth — not for a
bespoke effect. Adding a tenth should feel like a decision.

## 13. STATE — four treatments, and no more

Painted from `_hullOf`, so every one is the die's real silhouette. **The
form decides which canvas**: light *outside* the silhouette goes under
the dice, where `_paintHalo`'s punch already makes it a ring; anything
that changes what you see *of the face* goes over.

| form | reads as | canvas | for |
|---|---|---|---|
| **RIM** | a coloured outline hugging the die | under (z3) | selection, eligibility, "this one" |
| **CRUST** | a treatment on the edges, face still readable | under (z3) | frozen, dampened — *it works differently* |
| **VEIL** | a translucent wash over the whole face | **over (z42)** | fog, blind — *you cannot read this* |
| **DIM** | desaturate and darken, no colour added | **material, not canvas** | spent, committed, out of play |

**The form decides the canvas for a state. A beat always paints over.**
Not by convention — because *a state is part of the table and a beat is
part of the moment*. A state should sit in the world with the dice and be
occluded by them, which is what "under" buys and what makes the selection
halo read as a halo. A beat is a notification about something that just
happened, and a notification sits on top. That is why two rims can want
different canvases without the rule having an exception in it.

Four rules:

1. **No idle animation.** A state may animate on (150 ms) and off
   (200 ms) and nothing between. `seatMarkPulse 2.4s infinite` is a state
   pulsing for ever, which is what the eye learns to ignore.

   *Corollary, and it is the cost lever:* **`through:true` is about
   presence, not fidelity.** A state must have no frame where it is
   absent — that is the whole of what surviving a roll means. It does not
   have to be repainted at full quality on every frame of a flight, and a
   CRUST on a tumbling die is not being read anyway (rule 4 above says a
   state is for the settled read). A cheaper path during flight that snaps
   to full quality at settle satisfies the design and covers the half of
   the cost a settled-frame cache cannot reach.
2. **Colour is the identity, and it is already chosen.** Each state uses
   its enchant's or card's existing ink — `fog:#a8b0b8`, `snare:#a888c0`,
   `ward:#9ab0d0` in `ENCH_ICONS`, and the 41 inks in `FKFX.meta`. **Do
   not pick new colours.** One ink per idea across card, brand, beat and
   state is how a player learns what a colour means without being told —
   and under 3.4 it stops being optional, since one die can now be two
   different things depending on the face up.
3. **The glyph is optional and always secondary.** ≥40% of the die's
   width, centred on the hull, never a corner badge. If it does not fit at
   that size, the state does not get a glyph.
4. **Duration shows.** Under 3.2 that is *attempts remaining*: the RIM
   drawn as N segments, one per attempt, one dropping on each miss or
   fire. Readable without a number, at 50 px, at a glance.

## 14. THREAT — one treatment, and it must be a set

**A RIM in the acting card's ink on every eligible die, plus DIM on every
ineligible one.** The dimming is what makes it a set — without it the
player reads "these are highlighted" instead of "these are the ones."

It appears with the prompt and dies with the choice, bound to the armed
state rather than to a timer — which is the `_steadyDisarm` seam that
already exists.

**Break is the deliberate exception to "don't mark candidates."** P856 cut
candidate marking as noise and was right for Steady Hand, where any die is
legal and the status line says so. Break marks a *subset* for a
*destructive* pick. Keep it, and make it the only one.

---

# PART FIVE — THE TIMINGS

## 15. The bands

| band | reads as | use for |
|---|---|---|
| 0–80 ms | simultaneous | acknowledging a tap |
| 100–200 ms | snap, caused by input | wind-up; a state appearing |
| 220–400 ms | a discrete event | the strike; a die reacting |
| 450–700 ms | a small performance | a full instrument; a destruction |
| > 700 ms | waiting | only for something the player chose to watch |

**Nothing the player sits through more than twice a turn may exceed
400 ms.** A reroll is constant; a shatter is rare. Different budgets.

## 16. Anchor everything to the roll

`KICK.ms = 460` (25556), `PHYS.cap = 700` (25765) — the roll-to-read cycle
is roughly 500–700 ms. That gives the spine:

> **Beats resolve inside the settle. States own the read.**

An effect triggered *by the roll* has ~500 ms of free cover and should use
it. One triggered *by a tap* has none, so it must be short.

## 17. Stagger

2–3 things: 90 ms. 4–6: 70 ms. 7+: 45 ms, and accept it reads as a sweep.
Below 50 they merge; above ~120 it drags. When unsure, 70.

## 18. The sheets

**Card-driven reroll (Grog's Flask, Encore, Sleight) — a beat that hands
off to a state**

This was originally written as one mark on a 400 ms budget and that was
wrong twice over. The die is physically in the air for about a second, so
a 400 ms mark expires before the new face is readable; and the thing on
the die is not a beat at all.

| t | what | kind |
|---|---|---|
| 0 | card acknowledges the tap | — |
| +60 | card fires: its `FKFX` instrument, its ink | **BEAT**, clock-bound |
| +140 | die 1: RIM in the card's ink fades in over 100 ms | **STATE** begins |
| +210 | die 2's rim begins — 70 ms stagger | |
| — | each rim **holds for that die's flight** | condition-bound |
| settle | rim fades over 200 ms as the face becomes readable | STATE ends |

**The card firing is a beat; the die being re-thrown is a state.** §6
already says this — *"Settle: the world is different now; this is where a
beat hands off to a state."* Origin is not lifetime. The rim answers
*"this die is being rerolled by that card"*, which is present tense, has a
condition, and must survive a roll because it **is** the roll. So it is a
row in `MARKS` with `through:true`, not an entry in `FX_MARKS` — the list
rule holds rather than cracking.

Two consequences worth stating so they are not rediscovered:

- **The predicate cannot be bare `d.roll`** — every die in an ordinary
  roll has that. Arming must tag the die with the cause, and the tag
  carries the ink. That is a legitimate write where arming-with-an-ink was
  not: an ink duplicates what the firing already knows, whereas *why this
  die is in the air* exists nowhere else. A state may be parameterised;
  what separates the lists is condition versus clock, not plain versus
  parameterised.

  *The tag is set at seven call sites because no cause-carrying seam
  exists — checked, not assumed (P899). If an eighth site ever forces a
  revisit, prefer carrying the cause **in `D3.roll`'s options** rather
  than stamping it beside the call: `D3.roll` is the sole caller of
  `_physQueue`, so the cause would be recorded atomically with the flight
  it explains instead of ~60 ms adrift, and omitting an argument to a call
  you are already writing is harder to forget than omitting a separate
  statement. Not worth churning tested code for on its own.*
- **§15's 400 ms rule does not bind this.** That rule is about effects
  that delay a decision. The tumble is not a delay before the information
  — it *is* the information arriving. Do not "fix" the reroll to fit
  400 ms; that would cut the throw.

**A brand landing (moment 2) — 200 ms, inside the settle, free**

Die settles → +80 ms: 120 ms RIM-in in the enchant's ink, plus a three-note
`chime` → +200 ms: holds as a steady state while the face is up.

**An enchant firing on keep (moment 3) — 300–450 ms**

Already correct. One requirement: the substitution *is* the mechanic, so
the beat must visibly **replace** the score pop, not play beside it. A
"+0" rendering next to a firing brand is the bug.

**A lane mark (moment 4) — a state, not a duration**

| phase | treatment |
|---|---|
| arm (`_lmArm`) | VEIL fades in over the marked seat, 200 ms, enchant ink |
| hold | steady. No pulse. Segmented rim = attempts remaining |
| fire | the beat plays, then the veil fades out over 250 ms |
| **miss** | **the veil fades out over 250 ms with no strike** (3.3) |

**A die being destroyed — 550 ms, and it may be loud.** `BREAK` +
`D3X.shatter` already do this and it is the best effect in the game.
Leave it alone — and note it is the *template*: the 3D layer does the
visible work, the CSS class survives only as a flat-path fallback.

## 19. Interruption

> **A beat never blocks input.** If the player acts mid-beat, the beat
> finishes on its own layer and the input is honoured immediately.

If an effect *must* be seen before the player acts, it is not an effect —
it is a prompt, and it gets a status line and an armed state, like Break.

## 20. `reducedMotion`

Motion goes, information stays. States still paint; they appear instantly
instead of fading. Beats collapse to a 120 ms flash of their ink. **Never
remove a state** — it is information, and the setting is about vestibular
comfort, not about playing with less of the game.

---

# PART SIX — BUILD ORDER

Ordered so each step is independently visible and independently
verifiable.

**Steps 1–3 shipped as P878 (`09c950c`).** Two amendments to what they
said, both settled:

- **Snare's miss is `_lmSpend`, not `_lmRetire`.** "A due mark costs an
  attempt" *is* `_lmSpend`; identical at `turns:1`, and it survives snare
  ever getting a second attempt. **`_lmRetire` then has zero callers —
  delete it**, as `_lmDefer` was. Nothing left needs it: snare is always
  one attempt, and fog/snuff under Kindred want two *firings*, so a hit
  must not consume the window. Three verbs — arm, due, spend — and the
  machinery is done. The effect bus cites the split at 14901 (*"a distinct
  outcome earns a distinct verb"*); that principle is right and the split
  was right under the old semantics, where a hit was gone whatever the
  turn count said and a miss did nothing. The ruling collapsed those into
  one effect on the marker. Update 14901's illustration; its point about
  `claim` stands.
- **The cardmark wake condition is bounded by shape count, not by time.**
  P876 added `cardmark` beside `selected` rather than removing the
  selection test, so 27085's cost argument survives — but the reason has
  to be *one thin hull on an empty surface*, not "transient 900 ms".
  `_breakBegin` (24418) adds `cardmark` with no timer, so a Break prompt
  paints for as long as the player deliberates. **The state layer cannot
  lean on "transient" at all**, since states are long-lived by definition,
  so establish the per-frame argument now.

Remaining, renumbered. **Step 4 is new** — the original order had FKFX and
the landing brand writing to a canvas that nothing created until later.

4. **Build the over-canvas.** `_glowCv` (26632) with a different id and
   z-index 42, plus its own draw pass. It must **not** inherit
   `_drawGlow`'s two guards (§10): not the `selected` wake condition, and
   not the `_rolling()` skip, because a state has to survive a roll. ~30
   lines, and it unblocks 5, 6 and 7 together.
5. **Fix FKFX's four primitives (§9).** *Shipped as P881/P882/P883 except
   for `sc` — see below.* `_glow`/`_flash`/`_beam` onto the over-canvas
   painting the hull; `_motion`'s `translate` collision with `_slaveHost`
   resolved by routing motion to the mesh; `rt` driven as a world-up yaw
   (P821's axis, so the scoring face stays up); `opacity` guarded so an
   instrument cannot delete a die.

   **`sc` is still a silent no-op and it is the more used of the two** —
   12 occurrences across `SET` and `ARM` against 6 for `rt`. It is also
   the easier one: scaling a die cannot change its number, and
   `_pulsePose` (25701–25706) is already its sibling, driving
   `d.obj.scale.setScalar(1+P.amp*…)` per frame four lines from the
   translation path P881 used. Drive it there, or strip `sc` from the
   instrument definitions — but the step is not closed while a keyframe
   property twelve authored keys use does nothing.
6. **Moment 2 — the landing brand.** Biggest feel gain per line in this
   document.
7. **Build the four state forms — and they do not all live on the same
   canvas.** RIM and CRUST are additive light at or outside the
   silhouette; they belong **under** the dice on `dgCanvas`, which is
   where the tuned dials already are. VEIL and DIM modify what you see of
   the face; they belong **over**, on the state canvas.

   **Do not port `selected` or `cardmark`.** The earlier instruction to
   move them "as the control" was wrong, and `_paintHalo` says why: it
   already punches the subject out of its own glow (`destination-out` on
   the hull, widened by `G.clear`, 26838) — *"cut the subject back out
   EXACTLY on its painted edge: everything left is outside the shape,
   which is the whole point."* The ring is a ring **by construction, not
   by occlusion**, so the die was never doing the occluding and z-order
   does not change its shape.

   The control that proves the new surface without moving a tuned one:
   **paint a shadow copy of the same hull on both canvases in the same
   frame and diff the two surfaces.** That isolates the surface from die
   pose, timing and renderer state, and the verdict is **byte-identical**
   — not "identical where it was visible". Then delete the shadow copy;
   `selected` and `cardmark` stay where they are, permanently. *(Done:
   0 differing bytes both orders, against a differ proven able to see
   37,331 for a changed ink and 120,643 for a changed hull.)*

   **`_drawGlow` becomes table-driven, and that is the whole change.**
   Under-forms cannot be a second writer to `dgCanvas` — `_drawGlow`
   clears it every frame, so a second pass is the two-writer defect again.
   But adding a third hardcoded branch beside `selected` and `cardmark` is
   the hand-maintained roster this file keeps deleting. One table instead:

```js
/* WHAT GETS PAINTED AROUND A DIE. One row per form. The layer decides
   which canvas paints it; `through` decides whether it survives a roll.
   Both guards _drawGlow used to hardcode are now derived from the rows,
   so a form added here can never go stale against a wake condition
   somebody forgot to widen. */
D3X.MARKS=[
  {id:'sel',    layer:'under', through:false, ink:'SEL_COL', style:'rim',
   on:function(d){return d.chip.classList.contains('selected');}},
  {id:'card',   layer:'under', through:false, ink:'CARD_MARK_INK', style:'rim',
   on:function(d){return d.chip.classList.contains('cardmark');}},
  {id:'frozen', layer:'under', through:true,  ink:'#64b4ff', style:'crust',
   on:function(d){return !!d._frozen;}},
  {id:'fog',    layer:'over',  through:true,  ink:'#a8b0b8', style:'veil',
   on:function(d){return _lmMarks(d,'fog');}},
];
```

   Three things fall out. The wake condition is *any row's `on()`*, not a
   list of class names. The `_rolling()` skip becomes **per row** rather
   than a global condition standing in for a per-row fact, and a roll with
   no state live still skips the whole pass, so the original optimisation
   survives for the common case.

   **`through` belongs only to condition-bound marks.** An earlier draft
   said beats take `through:false` because "a beat has no business
   surviving a roll" — right about persistence, wrong as a gate, and it
   contradicted this document's own §18: the card-reroll beat exists to
   play *while* the dice are re-thrown, so a roll gate would delete the
   first beat in the sheet. A state must survive a roll because its
   condition outlasts one; a beat is ended by its clock whatever the dice
   are doing, so the field does not apply to it at all. And the cost shape is
   explicit: `_paintHalo` is one call **per distinct ink present**, not
   per form and not per die.

   **Two corrections to this sketch, both found by building it.**

   *The predicate reads the chip, not the die.* `d` inside a roster row is
   D3X's `{chip,obj,mat}` record; game flags like `_frozen` live on the
   pool die. `on:d=>!!d._frozen` is undefined on every die, for ever, and
   looks entirely correct while doing nothing.

   *DIM is not a canvas form.* Its three jobs already have material
   routes — `_spentLook` (27594) for a spent brand, `_keptLook` (27604)
   for a committed die, `_trayTint` (27628) for one out of play. All three
   act on the die's own emissive map, which desaturates the material
   rather than washing a fill over the face. The table above listed three
   different existing mechanisms as one new form; only RIM, CRUST and VEIL
   are painted.
8. **Move the states over** — frozen, blind, dampened, spent — and delete
   the nine box rules and the four invisible pseudo rules (§9). *Shipped
   as P893's successor (`659ef10`): frozen and dampened as CRUST under,
   blind as VEIL over, spent via `_spentLook`; thirteen rules out, file
   1,516 bytes smaller.*

   **The eight inert beat classes are routed** (`011e109`, 18 call sites —
   `eff-glow` alone is thirteen). `MARKS` stays one row per thing a die
   can *wear*; `FX_MARKS` is one entry per *firing*, armed with its ink at
   fire time. Two lists because there are two lifetimes, and no exception
   in either.

   **The rule for which list a mark joins** — write it down or they will
   drift: *is this bounded by a condition or by a clock?* A condition-bound
   mark is a row in `MARKS`. A clock-bound one is an entry in `FX_MARKS`.
   Nothing is bounded by both.

   **One thing to watch:** `_paintHalo`'s punch was tuned for two canvas
   positions and there are now three. P777 distinguishes `punchUnder`,
   cutting inward for a canvas beneath its subject, from the dice's punch,
   which widens because that canvas sits over the painted *table*. A
   canvas over the *dice* is a third case: the cut has to land at the
   silhouette or a hair inside it, or a beat's ring washes the die's own
   rim. Invisible in the common case, and the case to check is two dice
   overlapping.
9. **The lane re-key (3.1)**, its own patch and probe. Then lane marks
   painted from `_lmArm` state, arm-to-fire, both sides, segmented rim.
10. **Threat treatment** — Break's candidate set, rim plus dim, bound to
    the armed flag.
11. **Delete the three sweep lists (§9).** They should have nothing left
    to clear; if one does, a class was missed at step 8.
12. **`_fxAnchor`** — spawners take the die's projected centre, not the
    chip rect. Smallest of these and the one most likely to be mistaken
    for the whole job.
13. **Wire the ten dead `mat:*` rows.** Expect to re-tune `p` once they
    are audible together.
14. **Resolve `die-kindred`** (CSS, no `classList.add` anywhere) and
    `spawnBankPop` (31430, an empty function called on three live bank
    paths). Wire or delete.
15. **`reducedMotion` pass** (§20).
16. **Delete the flat 2D path** and the probes that set `D3_MATCH`.

Steps 1, 2, 8 and 11 are net deletions. The whole thing should make the
file smaller, which is the test of whether it was done right.

---

# PART SEVEN — VERIFICATION

## 21. The harness constraint

Code measured `D3X._rolling()` taking **19 seconds** to clear headless
against ~700 ms real, and `_drawGlow` skips the whole pass while it is
true — so the glow canvas is never created inside a normal probe window.
**Every frame-timed test below must be state-polled with forced draws**,
never wall-clock timed. Poll until the physics tape drains, then call the
painter directly. Nothing stubbed; only the clock waited out.

## 22. The tests

- **No die effect paints an axis-aligned box.** Static, and the strongest
  check available: grep the stylesheet for `box-shadow|outline:|border:`
  in any rule matching `.die` that is not `:not(.d3on)` or a shop scope.
  Zero, and it must **stay** zero — this is what stops the tenth class
  becoming the eleventh.
- **A mark tracks a moving die.** Arm a mark, capture the painted
  centroid, run a re-throw, capture again. The centroid must equal the
  die's projected centre in *both* frames. Measuring only the settled
  frame passes on a mark nailed to the slot.
- **A state survives a roll.** Directly tests §10: fog a lane, roll,
  assert the mark paints on frames where `_rolling()` is true.
- **Enchant lifetime is continuous.** No frame between arm and resolution
  where the mark is absent. Assert on the gap, not on "the mark appeared".
- **A miss looks different from a fire.** Both paths, same lane, diff the
  painted output. If they are pixel-identical, 3.3 did not land.
- **Nothing survives its cause.** Bust, hot-dice clear and destroy a die
  mid-effect; assert no mark paints for a die whose state is false.
- **The false-bust probe (3.4).** A die branded on both faces, rolled to
  each, with the other brand spent, against a table with nothing else
  scoring. `anyScoring` (23316) reads `dice.some(_dieIsIcon)`, and
  `_dieIsIcon` currently tests `d.val===d.ench.face && !_brandSpent(d)` —
  both halves break under two brands. Getting either wrong **declares a
  bust on a roll that had a legal keep**, which takes the whole turn and
  will read as the die being broken rather than the check.
- **The canonical-predicate probe (3.6).** Refuse a brand, then assert
  `_markLoneCast` does not mark it and Last Stand's gate treats it as
  plain. A refusal that only `_splitIcons` knows about fails this.
- **Particle origin.** Fire `spawnShards` on a physics-offset die; assert
  the emission centre is near the die's projected centre. Do *not* assert
  it is inside the chip — that check passes on the broken version.
- **The 400 ms rule.** Instrument every effect the player triggers more
  than twice a turn; assert its total span.
- **No idle motion on a state.** Hold a settled table ten seconds with a
  frozen and a fogged die; diff the mark layer between frames.
- **The instrument audit.** After step 4, play all nine on a match die and
  confirm each signature move is visible. `TRANSFORM` spinning is the
  specific check — it is provably dropped today.

## 23. Rules about instruments themselves

**Every probe needs a control in both directions.** *Nothing is refused on
a clean table* is what stops an always-true predicate passing; *the canvas
goes to zero with nothing marked* is what proves the pixel counter
discriminates rather than always reporting ink. Both were done on P877 and
P876 and both should be standard.

**A display cannot vouch for a bug, in either direction.** Reasoning from
a visual symptom to an input consequence — *"the die is dimmed, therefore
it is untappable"* — is the same error as trusting a correct-looking
number beside a wrong value. `brand-spent` has two references (23947,
28550) and neither gates input.

**A check that cannot fail is not a check — and there are three species,
with different repairs.** Six instances this session, and calling them
one thing will get the wrong fix applied next time.

- **Vacuous scope — the check cannot fail *in the configuration it
  ships in*.** `bandsAreDistinct` short-circuits true below two bands,
  then the run was split one band per invocation. Same shape as *"every
  pool member appears at least once"*. **Repair: make the failure
  reachable in the shipped configuration**, not in the one it was
  written for.
- **Wide search space — the check cannot *distinguish* its target from
  Note this is the species the Ill Omen bug belongs to, in game logic
  rather than in a check — see below.
- **Wrong expectation — the check tests the right thing and asserts the
  wrong answer.** *"I assumed the miss paid the rival when the handler
  pays the player."* This is the worst of the three, because vacuous and
  wide-scoped checks merely fail to inform, while this one **passes when
  the code is broken and fails when it is correct** — a green run is
  affirmative evidence for the wrong conclusion. **Repair: derive the
  expected value from the code under test or from the card's own text,
  never from your model of what it ought to do.**
- **Wide search space — the check cannot *distinguish* its target from
  a lookalike elsewhere.** A file-wide count of `g.dataset.lane=String(`
  that already appears at the two ghost mint sites; `code.index` finding
  a mint site instead of the carry; `G.pTurns` matching the legitimate
  pre-match zero check; `_pT`'s own definition containing the read it
  exists to replace. **Repair: narrow the scope to the region the thing
  must be in** — scan from the return block, not from the declaration.

**The vacuous-guard family is not confined to tests — the Ill Omen bug is
one in shipped game logic.** `CFX.ill_omen.rivalTurn` branches on
`if(ev.pts<=0)` (18145), and `ev.pts` comes from `endPTurn`'s
`_pTurnPts`, which `handleBank` has already zeroed via
`_turnScoreClear()` before `endPTurn` is reached. The condition cannot be
false. A guard that cannot fail *is the bug*, not merely an untested one.

**And the comment above it is the origin, stating the defect as a
feature.** P463 at 33937:

> *"the omen's payout left here. It reads SCORED NOTHING, not BUSTED, and
> a bust already flows through endPTurn carrying 0 — so both outcomes
> resolve at the single site there, off the same value the rivalTurn seam
> carries."*

The consolidation onto one site was the right shape. The value chosen is
constant, so the branch died. The author verified that **busts** carry 0 —
true — and never asked whether banks also carry 0. **A one-sided
verification of a two-sided branch**, which is the same shape as counting
a mention instead of the thing, and it survived in the file as
documentation.

`G._pTurnPts` (35442) is meanwhile write-only — nothing in the file reads
it, and `ev.pts` has exactly one reader (18145). So the blast radius is
one card, which is verified rather than assumed.

**Keep a validated check running on rows you have already discarded.**
When the cap-run filter and the `banks+busts===pTurns` identity flagged
the same two rows, the agreement was the finding. Silencing the identity
on rows another filter has dropped removes the only way to notice the day
they *stop* agreeing — a row one keeps and the other rejects is the
signal that one of them has drifted. Downgrade it to a note on discarded
rows; do not skip it.

**The recurring harness failure: a broken probe lands in a state the game
legitimately produces.** Three instances in three rounds, and it is why
each one passed. `diceOnTable: 5` — a real rival card (POCKET SAND,
`reduce_first_roll`, p=0.7) also gives five. A canary planted outside the
rotated span "kept its die" — which is what a die that did not move
legitimately does. `_pTurnBanked` written without its stamp reads 0 —
which is what a bust legitimately produces. **The probe's fault was
observationally identical to a valid game state every time.** The
defence is the one found for Tar Pit: assert on a quantity the confound
cannot reach (`numDiceAfterStart`, not dice on the table), and before
trusting a green run, ask what *else* produces this reading.

**P932 fixed the stamp and left one writer of `turnNum` behind.** The
stamp is now written by `startPTurn` (33364, `G._pTurnBanked=0;
G._pTurnBankedTurn=G.turnNum;`) and `handleBank` writes only the amount
(36870, 36889). That is the right shape. But **`G.turnNum` has two
writers, not one**: 33364's and the resume path at 42156
(`G.turnNum=rd.turnNum` inside `params._resumeData`), which restores the
turn number and does not stamp. On the first player turn after a resume,
`_pTurnBankedTurn` is stale against a restored `turnNum`, so
`_pTurnBankedOK` is false — the dev build throws (37107) and production
falls to `(G.turnPts||0)||0`, which on a banking turn is **0, the Ill
Omen defect returning by the back door.**

**The rule, and it is checkable:** `_pTurnBankedTurn` must be written
wherever `G.turnNum` is written. Two sites; one is covered. Either stamp
at 42156 beside the restore (`G._pTurnBanked=0`, since a resumed match
has no in-flight banked amount) or carry the pair through
`saveMatchState`. Confirm first whether the resume path reaches
`startPTurn` on its own — I found no call within 40 lines of 42156, which
is suggestive, not proof.

**A safe fallback must not be shaped like the bug.** P930 falls back to 0
on a stamp mismatch, and 0 is exactly what makes `if(ev.pts<=0)` fire —
the Ill Omen defect. That is correct today, because a mismatch *is* the
bust path and 0 is the right answer there. But it means the guard cannot
distinguish a bust from a newly added credit path that forgot to stamp —
the four-times-failed shape it was built to catch. **Fix: initialise the
pair at turn start** (`_pTurnBanked=0`, `_pTurnBankedTurn=turnNum`) and
let `handleBank` overwrite the amount. Then the stamp always matches in
correct operation, busts read 0 by explicit write rather than by stale
mismatch, and a mismatch becomes a real fault worth throwing on. Same 3.6
move: the write belongs where every path passes, not on one branch.

**Counting assignments needs `=` not followed by `=`.**
`G._pTurnBankedTurn===G.turnNum` contains `G._pTurnBankedTurn=` as a
substring, which is how a pairing assert found 3 value writes against 4
stamp writes. Sixth instance of the wide-search-space species; match
`=[^=]`.

**And the identity is worth more than either.** `banks + busts ===
pTurns` — a player turn ends in exactly one of the two — was computable
from fields the driver already returned, on every run since P914, and
would have caught a bust counter that reported 9/9/0 on a match
containing a bust. **Before trusting a tool's fields, write down what
must be true among them.** An assert on an arithmetic identity between
already-collected values costs nothing and does not care how the tool is
configured, which is precisely the weakness of both species above.

---

# PART EIGHT — OPEN

**0. ~~`activateGrogsFlask` never sets `d.roll`.~~ Withdrawn — it does.**
`_setDieVal` → `reDrawDieFace` → `D3.roll(…,{dur:420})` → `_physQueue`
whenever the die's group is `match`, the same entry an ordinary roll uses.
Driven: `d.roll` appears 63 ms later, 1,017 frame-ms of flight against
1,433 for an ordinary roll. It was a reading reported as a measurement,
and this brief promoted it on that word without checking — my error as
much as its author's.

**The conflict it was standing on is real and larger.** The die is in the
air about a second; §18 budgets the reroll at 400 ms with the envelope
ending at 580 ms. So the rim decorates the throw and is gone roughly
440 ms before the face is readable — the mark expires before the
information it marks arrives. §18 now carries the fix.

**0b. One driver serves the tray questions and the ladder, and it needs
all three requirements up front.** The tray band cannot be measured with
`#keptTray` hidden, and whether `#throwLine` moves on first keep needs a
real keep — which is the same select-and-bank machinery the ladder was
missing when it returned 0/8. Build it once, to this spec, or it gets
built twice:

1. **Reliable select-and-bank.** Unblocks the tray questions. The four
   stalls at `phase=choosing` say the current path cannot always find a
   legal keep.
2. **The three threshold policies** — `bank300`, `bank500`, `hot`
   (45691). Without them the ladder measures a policy `PWIN` was never
   derived against, and the number is precise and about something else.
   This is a *requirement of the driver*, not a follow-on task.
3. **A self-check on the first match.** A working player's total scales
   with the tier's target; `~2000 regardless` is visible in row one. The
   driver should refuse to continue rather than let the analysis catch it
   at n=8. A per-match floor is the wrong shape — it rejects an honest
   loss and would have passed the original run's 3400-of-3800. The pair
   test (two targets 2.5× apart, totals must move 1.5×) is right, and its
   scope should be stated: **it catches "not playing the game", not
   "playing it slightly wrong."** A pass is not calibration.
4. **A plausibility check the pair test does not cover — and it wants to
   be a pair too.** Scaling correctly while winning 0% or 100% is broken,
   and the score gate sees neither. But an *absolute* band on one tier is
   the shape the score gate was rejected for: 2 of 10 is both a limping
   driver and a genuinely hard cell, so the band's lower edge can refuse a
   real finding. **Two tiers, and the win rate must fall.** Flatness is
   the tell for the outcome exactly as it is for the score. 0/10 and
   10/10 still fail on sight; a legitimately brutal cell no longer does.
   Twenty matches, ~24 minutes, and it is the check that would have
   stopped the original run without any argument about luck.
4b. **Compute the reachable-score envelope — as per-turn yield, not as
   a played-out ceiling.** `TURN_CAP_PATRON=8`, `TURN_CAP_BOSS=10`, plus
   a ninth turn for the trailing side (`_finalAnswerUsed`, granted in the
   `pPts<oPts` branch — and an envelope run is *always* trailing, so it is
   collected every match) and starstone's `_extraTurn`, which multiplies
   against the budget rather than adding to it.

   **Do not try to play a ceiling out.** Measuring at a high tier fails
   because the *rival's* target is reachable even when the player's is
   not: the rival wins and ends the match before the cap, so the reading
   is "what the player scored before losing", not a ceiling, and matches
   of different lengths are not comparable. Blocking the rival is worse —
   it measures a counterfactual game, and it removes the trailing
   condition the ninth turn depends on.

   **CORRECTION, 2026-09-03. The version of this requirement dated
   2026-09-02 contained a false sentence, and the correction is why the
   unreachable-target harness is load-bearing rather than convenient.**

   What that draft said: *"`myTotal`, `oppTotal` and `target` are passed
   to `simTurn` but never consulted by it (45819–23)."* The cited lines
   are the **closure**, and about the closure it is true — `bankFn` reads
   `(turnPoints, diceLeft)` and nothing else. `simTurn` itself is a
   different matter, and it reads all three:

   ```js
   /* 45808 */ if((myTotal+turn+bankAdd)>=target)return bank();
   /* 45810 */ if(oppDone){ if(myTotal+turn+bankAdd>oppTotal)return bank();
   ```

   45808 is a **target-aware stopping rule that fires before `bankFn` is
   ever asked**. I verified a claim about the closure and attached it to
   the enclosing function. (Note also that `turn` in this file is the
   *running turn score*, not a turn index — `var turn=0` then `turn+=gain`
   at 45803. `bank500` means bank at 500 points. The policies carry no
   clock at all, which is a stronger memorylessness than I claimed, and
   it is the half of the original argument that survives.)

   **The consequence: per-turn yield is stationary only when 45808 is
   disabled.** Under a reachable target the last turns of a match are
   truncated — a turn that would have run to 900 stops at 620 because 620
   is enough — so mean per-turn yield is depressed by an amount that
   depends on how close the total is to the target. `mean × budget` is
   then an approximation with an unknown sign. Put the shared `G.target`
   out of reach and 45808 never fires, `oppDone` never fires, the policy
   is the only stopping rule, and per-turn yield is stationary for real.

   > **envelope = mean per-turn yield × turn budget** — exact *under the
   > unreachable-target harness*, an approximation without it.

   So the harness is not a way of avoiding the rival ending the match; it
   is what makes the estimator valid. Both facts are true, and only the
   second one is a reason.

   **What the envelope measures is a ceiling, not a forecast.** With
   truncation disabled, the number is "what this cell scores when nothing
   stops it" — which is the right quantity for *can this cell reach T*
   and the wrong one for *what will a real match look like*. Do not reuse
   it as the latter.

   Busted turns still belong in the mean; a zero is a turn's yield.

4c. **Report reach probability, not a ceiling. Code's finding, and it
   replaces the estimator rather than tuning it.** A ceiling is a max of
   n, which can only rise with n, so a cell measured at n=4 gets a
   systematically lower "ceiling" than the same cell at n=10 and the two
   are not comparable — which is fatal, because pruning compares cells.
   It also carries no confidence. Asked instead as *P(match total ≥ T)*
   from the same matches, the answer is a probability with an interval,
   at roughly a quarter of the matches. Measured for band 1 / bank500 at
   n=10: mean 4970, sd 1602, CV 32%, and tier 7's 9500 is z=2.83.

   **Three things bound how far that number can be trusted, in
   descending order of size. Two of them are not the one that was
   flagged.**

   - **The sd is estimated from n=10.** Its own standard error is
     `sd/√(2(n−1))` ≈ 378, about 24% relative. One SE either way moves
     P(reach 9500) between roughly 0.01% and 1.1% — two orders of
     magnitude, from sampling noise alone. This is the largest term and
     the one a turn-level resample actually fixes, because ~85 turns
     estimate a variance far better than 10 matches do.
   - **The normal fit's tail.** A match total is a sum of 8–9
     right-skewed turn outcomes, so the true tail is likely fatter than
     normal and the fit **understates** reach — the dangerous direction
     for pruning. Real, but smaller than the sd term.
   - **Exchangeability, and the control for it must be two-sided.** The
     resample assumes turns are iid draws from one pool. Two failures are
     possible and **they have opposite signs**: consumable charges
     (`cs.charges.double_or_nothing--` and friends persist across turns)
     make later turns systematically different, and pooling
     heterogeneous turns makes the resampled match SD **larger** than
     observed; cross-turn coupling (a mark armed on one turn firing on
     another) makes observed **larger** than resampled. A check that only
     asks *"do matches vary more than independent turns can explain"*
     sees one of these and is blind to the other — and because the signs
     oppose, both can be present and cancel into a false pass. Check the
     ratio in both directions, and when the resample runs hot, the
     diagnosis is heterogeneity and the repair is to **stratify: resample
     turn i from turn i's own bag** rather than from the pool.

4d. **The unit of independence is the MATCH, not the turn — and using the
   per-turn CV to size a run in matches is the error to watch for.** A
   match carries per-match random draws that apply to every turn in it:
   the rival's card set (`reduce_first_roll` / POCKET SAND fires at 0.7
   and cuts the player to five dice), the dealt loadout, the rung. Those
   shift a whole match's yield at once, so turns inside a match are not
   independent draws however memoryless the policy is.

   **The arithmetic says so plainly.** If turns were independent, a
   match's mean per-turn yield would have CV = per-turn CV / √(turns per
   match) ≈ 42%/3 ≈ 14%. The silver run's reported 95% interval
   (−48%…+65%, half-width ~56.5pp at n=6/arm) implies a match-level CV
   near **50%** — 3.5× the independent prediction, a variance ratio over
   12. That is not a subtle over-dispersion.

   Two consequences:

   - **Size from the match-level CV.** `n_per_arm = 2(z+z)²·CV_match²/δ²`
     — at CV 50%, **16 per arm** separates parity from 1.5×, and 63 per
     arm resolves 25%. Sizing off the per-turn CV understates it.
     **The 50% is back-calculated from a reported CI half-width, not
     measured.** Compute it from the per-arm match-level SDs before
     sizing on it; a number derived from a summary statistic must not be
     promoted to a measured one, which is the Grog's Flask error in a
     different costume.
   - **RETRACTED — I was wrong and the source settles it.** I claimed
     "exactly" that the original sizing error was the missing factor of 2.
     The source reads `nreq = 2*(1.96*sd/d)**2`: the 2 was **present** and
     `z_β` was **absent**, so the original description ("dropped the power
     term") was right. The integers could never have decided it —
     `2z_{α/2}²` = 7.683 and `(z_{α/2}+z_β)²` = 7.849 differ by 2.2%, and
     which of 13/36/80 each yields turns on CV precision and rounding
     convention. **I read a numerical match as an identification**, which
     is the error this brief spends its length naming, in my own work.
     A formula cannot be back-identified from rounded outputs; read the
     source.

     **What the original formula actually was, stated properly:** a
     two-sample sizing at **50% power**. `2z_{α/2}²sd²/d²` is the n at
     which a real effect of size `d` is detected half the time. It was
     not a term dropped by accident so much as a coin flip specified as a
     design point. The live figure uses `2(z_{α/2}+z_β)²` = 15.698.
   - **The exchangeability control should refuse the pooled resample,
     and refusing is the correct answer, not a failure.** When it does,
     resample whole matches. That is always valid, and the precision it
     costs is precisely the sd-conditioning problem — which is real, and
     is the price of the coupling being real.

5. ~~**Reload the page between matches.**~~ **Not needed — answered.**
   Six consecutive matches via `launchSeat(seatIdx)`, zero failures,
   across two nights. `launchBossMatch()` was simply the wrong entry
   between matches; `launchSeat` is the player's own path with the click
   removed. Chained beats boot-per-match, 6.75 h against 7.48 h at a
   measured 101 s median.

**1b. P922's carry makes `_famPeekVals` mutable, and two copies of it are
shallow.** `saveMatchState` stores `famPeekVals:G._famPeekVals.slice()`
(12152) and the restore reads it back the same way (40589). The elements
are `{lane,val}` objects (17944), so `.slice()` copies references. That
was safe while nothing wrote `p.lane` after mint; **P922's carry writes
it.** If the carry mutates in place rather than replacing the object, a
saved snapshot now aliases live records and moves with the reorder. The
file's own neighbours show the intended pattern — `_oIllOmen` and
`_famIllOmen`, one line either side, both use
`JSON.parse(JSON.stringify(...))`. And the window is not exotic: the
comment at 12139 says `saveMatchState` is the last statement of
`startPTurn`, so it lands every turn boundary. **Check which P922 does;
if it mutates, deep-copy both sites.**

**1c. The lane-stamped census — I looked, and found nothing P922 missed.**
`G._fairTrade.lane`, `_tradeSwaps[].lane`, `_famPeekVals[].lane`, and the
`dataset.lane` on `_pkGhosts` / `_htMarks` are the player-side set, all
now carried. `_fog` / `_snuff` / `_snare` carry rival lanes and correctly
do not move (P531's rule). `G._famHoneyVal` is a bare value with no lane,
and its payload lands on `free[0]` (17580) while its marks decorate the
*source* pair (18118–24) — disjoint by design, not a half-applied fix.
**But a grep cannot certify this and neither can a roster.** The durable
form is an invariant, not a list: snapshot every `lane`-bearing record's
lane→die mapping before the reorder and assert it is preserved after.
That catches the record nobody enrolled, which is the failure P922 was.

**And the invariant has to live in the reorder, not in a probe.** The
census built for this found **10 lane-bearing records on one run and 14
on the next** — the count depends on which cards have fired by the time
it walks `G`, because most of these records are minted by a card and
cleared at the roll tail. A probe therefore samples one state; it cannot
enumerate. A record minted only under some card pairing is invisible to
any single run of it, and that is exactly the shape of the thing P922
missed. Wire the same walk into the reorder path under a dev flag and
every reorder in every playtest becomes a census, so coverage accrues
over play instead of over one probe — the same move P927 makes for the
`numDice` rebuild, and there is no reason the two hazards get different
treatment.

**1. ~~`_famRefloatGhosts` (17514) — a comment that disagrees with its
code.~~ Ruled, 3.8 — and it was never an open design question.** The
P844 comment already said the floats follow their dice; the reorder
renumbers `d.lane` (45415) and leaves `dataset.lane` stamped, so
`byLane[+g.dataset.lane]` (17520) finds the wrong die and 45459 runs
after the renumbering, every time. **I filed this as undecided when it
was decided and broken** — the comment stated the intent plainly and I
read it as an open choice. The fix is a third entry in the
`_carry.forEach` that already carries `_fairTrade` and `_tradeSwaps`;
see 3.8.2 for the snapshot discipline it inherits.

**2. ~~What did P876 change to fix the cardmark hole?~~ Answered.**
`cardmark` was added beside `selected` in the wake condition; the
selection test stays. 27085's cost bound survives — see the amendment at
the head of Part Six for the form the reason has to take.

**3. Snuff's two gates still disagree.** The announce and `left--` are
gated on `left>1` (35916); the seat is actually removed under
`_rungMats.length>1` (36049). Code made the spend follow the announce —
the half the player is told about — and left the mismatch, correctly,
since reconciling them moves behaviour. **Recorded as residual, not
fixed:** in the window where the gates disagree, the original bug
survives.

**4. The silver bust-save contaminates every stored sim finding, not just
the ladder.** `simTurn` granted a free bust save to any loadout containing
a silver die — seeded from the *full* loadout rather than the shrinking
one, so it did not need the die still in hand — while Silver's own
definition says the save was retired and its `effect` is null. Fixed in
`c2134d6`; measured at 91 busts with bone against 0 with silver before,
and bone 0.78 / silver 0.62 / clone 0.58 after.

The reach is wider than the fix. Silver appears in G2-mid and G3-late —
half the default gear table — and `npcTurn` seeds from `rung.dice`, so
**both seats** were affected. Every recorded balance conclusion drawn
through a silver-bearing loadout needs re-deriving, and one of them is a
claim *about silver*: **"full-silver stacking is a trap"** was measured on
a sim where silver was immortal. Re-run it before it is relied on again.
Same for anything comparative that used G2 or G3 as a baseline.

**The pricing consequence is now ruled — 3.9, cut the price.** The number
comes out of requirement 4b's per-turn-yield instrument (two silver
against two iron, same policy, same band), not out of a separate
experiment. This item stays open only for the re-derivations above.

**MEASURED, 2026-09-03. 14 matches per arm, zero discards: iron 4543,
silver 4508 mean per-turn yield, difference −0.8%, 95% CI [−29%, +28%].**

**State it as the interval, not the point.** "Parity" is the midpoint;
what the data supports is *not a multiple* — anywhere in roughly
[0.71×, 1.28×] iron. 1.5× needs +2272 against an upper bound near +1272,
so it is excluded. That every point in the interval prices silver near
iron is what makes the finding decisive; the midpoint is not.

**The between-batch sign flip is a null, not corroboration.** +192 then
−205 are both well inside one batch SE (≈1005), so there is no evidence
of a batch effect — which licenses pooling and does nothing else. Reading
an undetectable difference as support for the hypothesis is the same move
as "the outcome fell" at 2/10 versus 0/10.

**And a caveat that is mine, because I specified the harness.** The
unreachable target makes turns stationary by removing the end-game — but
bust-avoidance is worth most *near* the target, where a bust costs the
match rather than some points. So this instrument systematically
undervalues defensive dice, and silver is a defensive die (0.62 bust
against bone's 0.78). It cannot rescue a 5.8× premium. It does argue
against pricing silver *at* iron: see 3.9's amendment.

**Sizing that run: it is a two-sample comparison, so n doubles.** At
CV=32%, `n_per_arm = 2(z_{α/2}+z_β)²·CV²/δ²` — with α=0.05 and 80% power
that is **26 per arm for a 25% effect, 72 for 15%, 163 for 10%.** The
formula without the leading 2 gives 13 / 36 / 80, which is the n for
testing one arm against a *known* mean; silver-versus-iron measures both
arms, so the 2 belongs. And CV itself is an n=10 estimate carrying ~24%
relative error, and n scales as CV² — so treat every figure as ±50%.
**The precision worth buying is much coarser than these tiers suggest:**
silver at 580g must earn ~5.8× iron to be priced right and is measuring
about 1×, so the live question is "≈iron" versus "≈1.5× iron", which is a
50% effect — **7 per arm, about 35 minutes.** Resolving 10% would
distinguish a 250g price from a 275g one, which no player can feel.

**5. ~~`window.G` is undefined.~~ All three sites fixed in P886.** Kept
here for the reason rather than the fix: `G` is a `let` (29965), and a
`let` never becomes a window property.** Three live sites outside this workstream,
each a one-word fix, and two of them are player-facing rather than
cosmetic:

- **12561 — the bank sound has never pitched up.** `SFX.bank()` scales
  its pitch with how close the player is to target (1.15× at 65%, 1.3× at
  85%, 1.5× at 95%, plus an extra harmonic when hot). The guard is
  `window.G`, so `r` is permanently 1: every bank in the game plays the
  same flat 520/660/900 chord. This is the audio half of *tell the player
  they are close*, and it belongs to this workstream by subject even
  though it is not in the build order.
- **45945 — tap-to-fast-forward a rival turn has never worked.** P5's
  affordance (tap the board during the rival's turn to run it at 0.15×)
  guards on `window.G` and therefore always returns.
- **45697/45920 — the sim's isolation of `oppShouldBank` does not happen,
  by two independent mechanisms.** `var _savedG=window.G; window.G=null;`
  cannot neutralise anything, *and* `oppShouldBank` guards on bare `G`
  (`typeof G!=='undefined'&&G`), so it would read the live binding even if
  the window property existed. Severity is conditional: run from a fresh
  page `G` is null anyway and nothing is contaminated. **Settle this
  before the outstanding ladder re-run**, since that is the measurement
  the path exists to serve.

The file documents this trap at 30101, a few lines from where it bites.

**6. Two-brand support — scheduled after step 7 (Denis, 2026-09-03), and
its seams are narrower than first written.** The ordering is deliberate:
two brands take the brand-landing rate from ~17% to ~33% of rolls, so
moment 2 and the per-enchant ink stop being polish and start being how
the build reads. Building the model while `STATE_FORMS` is still inert
would mean landing per-face `brand-spent` and a paired UV cache key with
nothing on screen to check them against — and a display that vouches for
a bug in either direction is a defect class this brief already names
twice. The logic seam is one — `_dieIsIcon` — because
`_brandSpent` (23846) already tests enchant-*object* identity against
`G._castEnch`, so it becomes per-brand for free once `d.ench` is two
objects. The visual seam is one: `brand-spent` (23947) and `_spentLook`
(27594) are per-die, and a spent 1 must not grey out a die showing its
live 5. Plus `_iconFaceRoll` (41961) needs the slot so it can skip a taken
face, and the sale guard at 42285 must refuse per-face rather than
per-die. `_wardOwned` (41973) generalises into whatever the solo rule
becomes.
