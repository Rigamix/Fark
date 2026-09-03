# THE FX AUDIT — dice, cards, enchants, and the pipeline that is half built

*2026-08-30. Every line number and every count here is read from the live
`fark_proto.html`, not estimated. Denis: "selection outline when rerolling
a die with a card will not follow the die rotation, it's a misaligned
square… a simple, sturdy and fully lined up with Balatro-like efficient
pipeline (which should already be implemented, right?)"*

---

## 0. THE VERDICT

**Denis is half right, and the half he is right about is the important
half.** Two canonical pipelines exist and both are good:

- **`FX.emit`** (30993–31120) — pooled particles, hard cap of 300, sleeps
  when idle, dpr clamped to 2, dt clamped to 32 ms, respects
  `reducedMotion`, shared shape table so a canvas particle and a DOM
  sparkle are the same silhouette. **Six named spawners plus four inline
  emitters, all through one `emit`.** It also already does sprite-sheet
  playback, which is the thing Denis asked the enchant lab to prepare
  for.
- **`_hullOf` + `_paintHalo`** (26645, 26712) — the die's eight corners
  projected through the camera and gift-wrapped into a real convex hull,
  repainted every frame. This is the correct answer to "follow the die's
  actual shape" and it already exists.

**The gap is that the second one is used for two effects out of roughly
twenty.** `selected` and `cardmark` go through the hull painter. Everything
else — card reroll, the four `eff-glow` colours, frozen, blind, dampened,
kindred, and the three enchant seat marks — paints a CSS box on a DOM
element that is invisible, axis-aligned, and *in the wrong place*.

So this is not "build an FX system". It is **finish routing to the one
that is already there, and add the one layer it is missing.** That is a
much smaller job than it looks, and it is why the basics can be fixed
first without throwing anything away.

---

## 1. THE LAYER MAP — read this before anything else

Everything below follows from these five z-indices. They are the reason
the same bug keeps coming back under different names.

| z | element | where | knows where the die actually is? |
|---|---|---|---|
| in-flow | `.die` DOM chips | inside `#playerDiceRow` / `#oppDiceRow` | **no** — it knows the *slot* |
| 3 | `#dgCanvas` (hull painter) | `#screen-match` (26637) | **yes**, per frame |
| 41 | `#d3xCanvas` (the WebGL dice) | `#screen-match` (2893) | yes |
| 60 | `.fog-float`, `.peek-float`, `.honey-float`, `.vang-float` | `document.body`, fixed (4448–4463) | one rect read, then never again |
| 9500 | `#fxLayer` (particles) | `document.body`, fixed (31003) | one rect read, then never again |

Three consequences, and every symptom in this document is one of them:

**1. A DOM chip in a match is invisible.** `#d3xCanvas` is at z-index 41
and covers the row. The file already knows this and says so at 36240:
*"Chip overlays are invisible under the 3D canvas (screenshot-proven)"*.
Anything painted on `.die` in a match either hides behind the dice or —
if it extends past the chip's box, like a `box-shadow` — leaks out around
the edges as a halo of the wrong shape.

**2. A DOM chip is not where the die is.** On the table a settled die
holds the pose *physics* gave it: `d.obj.position.set(d.phys.x,d.phys.y,
d.phys.z)` at 28888. The chip stays at its flex slot. The die is offset
from its chip **and** rotated. So a CSS effect on the chip is wrong twice
over — wrong shape and wrong place.

**3. The hull painter is under the dice.** `#dgCanvas` is z-index 3,
`#d3xCanvas` is 41. That is right for a rim (the glow reads as a halo
around the silhouette, which is why the selection glow looks good) but it
means **nothing painted there can ever cover a die face.** There is no
per-die layer above the dice today. That single missing canvas is what
fog, snuff, snare, blind and dampen all need, and it is why each of them
was solved with a different hack.

---

## 2. THE BUG DENIS NAMED, root-caused

The card is **Grog's Flask** (39577–39582) and the class is
`card-reroll` (4200). Also reached by Encore (15299, plus `crr-blue`),
Sleight (36167) and the adopted-dice re-throw (32826).

```css
/* 2811 */ .die.d3on{background:none!important;border-color:transparent!important;box-shadow:none!important}
...
/* 4200 */ .die.card-reroll{
             box-shadow:0 0 14px 4px rgba(255,180,40,.7),...!important;
             filter:brightness(1.25)!important;
             animation:dRoll .4s linear infinite,cardRerollPulse .6s ease-in-out infinite!important;
```

Both selectors are specificity `(0,2,0)`. Both use `!important`. **4200
comes after 2811, so `card-reroll` wins**, and the suppression that makes
3D dice invisible chips is simply overridden. What the player sees is a
glowing rounded rectangle around an invisible box, sitting at the die's
flex slot while the real die sits at `d.phys` a few pixels away, rotated.

That is Denis's "misaligned square", exactly, and it is not a tuning
problem — a `box-shadow` is drawn around the border box **by CSS spec**.
No value can make it follow a rotation.

There is a second, quieter defect in the same rule: `animation:dRoll` is
`rotate(0deg) → rotate(360deg)` on the chip (4132), and D3X reads
`d.chip.getBoundingClientRect()` every frame (28951). A rotating square's
axis-aligned bounding box grows to √2× at 45°. On the table the scale is
taken from `d.w0` (captured once) so this is currently harmless; **in the
tray the scale is taken from the live `cr.width`** (28950), so a
`card-reroll` on a tray die would pulse it. Don't fix that by adding a
guard — deleting the rule removes both problems at once.

### The file already solved this once, correctly

P856 hit the identical bug on the card mark and fixed it the right way.
The comment at 3940 is worth quoting because it is the whole design in
four lines:

> *"NO OUTLINE HERE. A CSS outline is an axis-aligned box around the
> border box, so on a die that settles rotated it can only ever be a
> square around a tilted thing. The mark is painted from the die's real
> hull by D3X's halo painter."*

`.die.cardmark` was reduced to `cursor:pointer` and the paint moved to
27104. **`card-reroll` is the same bug, one class over, that the sweep
missed.** So is every entry in §3.

---

## 3. THE CENSUS — what is still painting boxes

Classes added to a match die in JS, whose CSS paints geometry, with no
3D suppression. "adds" is the number of `classList.add` sites.

| class | adds | what it paints | line |
|---|---|---|---|
| `card-reroll` | 4 | box-shadow ring + chip spin | 4200 |
| `crr-blue` | 1 | box-shadow ring (blue) | 4213 |
| `card-reroll-settle` | 1 | box-shadow fade | 4221 |
| `eff-glow-red` | 7 | box-shadow ring | 4156 |
| `eff-glow-gold` | 3 | box-shadow ring | 4154 |
| `eff-glow-blue` | 1 | box-shadow ring | 4157 |
| `eff-glow-green` | 1 | box-shadow ring | 4155 |
| `die-frozen` | 2 | box-shadow + border + `::before{content:'❄'}` | 4305 |
| `die-blind` | 2 | opaque `background` + border + `::after{content:'?'}` | 4298 |
| `die-dampened` | 2 | `::before` radial gradient, `inset:0` | 4170 |
| `die-dampened-fresh` | 2 | `::after` poof, `inset:-5px` | 4184 |
| `die-kindred` | 0* | `::after{content:'💀'}` + `::before` smoke | 10083 |
| `combo-glow` | 1 | `::after` sheen across the chip | 4003 |

\* `die-kindred` has CSS and no `classList.add` anywhere — either dead
code or a wiring that was lost. Decide which; do not leave it.

**Two more strays found while counting, unrelated to the boxes but in
the same neighbourhood:**

- `function spawnBankPop(total){}` (31430) is **empty**, and it is called
  three times on live bank paths (34035, 35251, 35270). Every bank in the
  game calls a function that does nothing. Either the celebration was
  meant to live there or the calls should go.
- Four `FX.emit` callers are inline rather than named spawners
  (`_bustShieldFX`, `showHot`, `refreshSelUI`, `_chalkDust`). Not a
  defect — noting it so the spawner count in §0 is not mistaken for the
  emitter count.

**That is 13 classes and 27 call sites all making the same mistake**, and
four of them (`die-frozen`, `die-blind`, `die-kindred`, plus fog below)
also use an emoji glyph in a pseudo-element pinned to a corner of the
invisible chip — which is the "little cloud emoji that doesn't even cover
the die" Denis reported, in four more places than he has noticed yet.

### What is already right, and should be the template

- **`selected`** — CSS carries no geometry for 3D dice (2815–2818), the
  hull painter draws it (27110).
- **`cardmark`** — same, since P856 (3946, 27104).
- **`die-shatter`** — all four sites pair the class with `D3X.shatter`
  (17850, 24777, 32912, 36211), and 24776 says why: *"the class alone
  animates a box nobody can see"*. The CSS is a vestigial 2D fallback.

**Shatter is the pattern.** The 3D layer does the visible work; the CSS
class survives only for the `D3_MATCH===false` flat path.

---

## 4. THE ENCHANTS — the lifetime hole, and where it belongs

Denis, earlier: *"the fog effect should apply as soon as I keep the die
and activate the enchant and remain on the spot there all the way until
it affects the npc. Same for all other enchants."*

Three enchants arm a lane marker and pay out on the rival's turn:
`snare` (23468), `snuff` (23578), `fog` (23591). All three go through one
function:

```js
/* 24072 */ function _lmArm(key,lane,turns,extra){
  if(!G)return;
  var m={lane:lane,live:true,turn:(G.oppTurnCount||0)+1,turns:turns||1};
  ...
  G[key]=m;
}
```

**`_lmArm` paints nothing.** It is pure state. So the arm is invisible,
the wait is invisible, and the only feedback in the entire lifetime is at
the moment of firing — a 30 px `☁` in a `position:fixed` div appended to
`document.body`, positioned from one rect read and removed after 3200 ms
(36255–36259). It does not cover the die, does not follow it, and cannot,
because nothing updates it after the frame it was created.

The lifetime the lab modelled is *arm → hold → fire*. The game implements
*(nothing) → (nothing) → 3.2 s of emoji*.

**The fix has an obvious home, and it is the point of this section.**
`_lmArm` / `_lmSpend` / `_lmRetire` are already the single seam every lane
marker passes through — the same role `_setDieVal` plays for die values
and `_removeDieAt` plays for removal. Give the seam a paint call and all
three enchants get their full lifetime from one place. Sprinkling a mark
into each `fire:` handler is the version that rots, because the fourth
enchant will not remember.

---

## 5. THREE CLEANUP LISTS, EACH HAND-MAINTAINED

This is the same defect the project keeps finding: a fact living in more
than one place. Three sweeps clear die effect classes, each with its own
literal list:

| line | clears |
|---|---|
| 32614 | `scatter`, `bust`, `break-target`, `cardmark` |
| 33328 | the four `eff-glow-*` |
| 34295 | `selected`, `combo-glow`, the four `eff-glow-*` |

The lists overlap, disagree, and **none of them clears `card-reroll`,
`card-reroll-settle`, `crr-blue`, `die-dampened`, `dampen-fade`,
`die-blind`, `die-frozen` or `die-kindred`.** Those rely entirely on their
own `setTimeout` (18 such timers). A die destroyed, re-thrown or swept
into the tray mid-timer keeps its class, and the timer then fires against
an element that has moved.

Deleting the CSS deletes this problem too: with no class to clear, there
is no list to maintain. **That is the strongest argument for doing §3 and
§5 as one job rather than two.**

---

## 6. `reducedMotion` is honoured by the good pipeline and ignored by the bad one

`FX.emit` skips emission under `reducedMotion` (30998). `body.reduced-motion`
gates exactly two CSS rules in the file (1346, and the retired idle-breath
at 4014). **None of the 13 effect classes in §3 respects it.** A player who
turns the setting on still gets every pulse, spin, sheen and poof.

Not a separate chore. Route the effects through the pipeline and the
setting starts working on its own.

---

## 7. THE PIPELINE — one seam, one new layer

Nothing here is a new system. It is one canvas, one function, and a table.

### 7.1 The missing layer

`#dgCanvas` at z-index 3 can only draw *behind* the dice. Add its twin:

```js
/* the OVER layer. Same construction as _glowCv (26632), same _hullOf
   geometry, one number different - it sits above #d3xCanvas (41) so a
   mark can cover a die face instead of only rimming it. Two canvases
   rather than one because the rim wants to be UNDER the die (that is
   what makes the selection glow read as a halo and not a sticker) and
   fog wants to be OVER it. Which side an effect wants is the only
   thing that decides which canvas it goes on. */
_glowCvOver:function(){ ... cv.id='dgCanvasOver'; ... 'z-index:42' ... }
```

### 7.2 The seam

One function, called from the same per-frame pass that already paints the
selection halo (27073–27128), driven by a table rather than by branches:

```js
/* DIE MARKS: the one place a die gets a visual that is not the die.
   Each row says WHAT it looks like, WHEN it is on, and WHICH SIDE of
   the dice it paints on. Adding an effect is a row. There is no second
   place to register it, no class to remember to clear, and no CSS. */
D3X.MARKS=[
  /* id          layer    ink        style     live(d) */
  {id:'sel',     l:'under', ink:'SEL',  s:'rim',  on:function(d){return d.chip.classList.contains('selected');}},
  {id:'card',    l:'under', ink:'#c66058', s:'rim',  on:function(d){return d.chip.classList.contains('cardmark');}},
  {id:'reroll',  l:'under', ink:'#ffb428', s:'rim-pulse', on:function(d){return !!d._reroll;}},
  {id:'frozen',  l:'over',  ink:'#64b4ff', s:'frost', on:function(d){return !!d._frozen;}},
  {id:'fog',     l:'over',  ink:'#a8b0b8', s:'disc',  on:function(d){return _lmMarks(d,'_fog');}},
  ...
];
```

Three things this buys, and they are the whole point:

- **The condition is read from game state, not from a CSS class.** No
  `classList.add`, no `setTimeout` to remove it, no sweep list. A mark is
  on exactly while the state that causes it is true — which is also what
  makes the enchant lifetime correct for free: `_lmArm` sets the state,
  the painter sees it the next frame, `_lmRetire` clears it.
- **Every mark is the die's real hull**, because there is one geometry
  source and it is `_hullOf`.
- **`s:` is a style name, not a shape.** `rim`, `disc`, `frost`, `dark`
  are four small painters in one object. Denis's lab exports feed this
  table's values; the lab's four lifetime classes map onto `on:`
  (instant/self = a transient flag, lane/match = a state read).

### 7.3 Particles need the die's position, not the chip's

Every spawner reads `el.getBoundingClientRect()` — `spawnPixelSparks`
(31250), `spawnShards` (31346), `spawnObsidianBurst` (31365),
`spawnSawdust` (31389), `_fxSpray` (15708). On a match die that is the
**slot**, not the die (see §1.2). Sparks come off where the die would
have been if physics had not moved it.

One helper closes it:

```js
/* screen-space centre of the die as DRAWN, falling back to the chip
   for flat dice and non-match surfaces. The spawners keep their
   signatures; only what `r` means changes. */
function _fxAnchor(el){ ... D3X centre if el._d3 && match ... else rect ... }
```

Do this **after** §3 and §7.2, not before. It is the smallest of the
three and it is the one most likely to be mistaken for the whole job.

---

## 8. BUILD ORDER

1. **Delete the geometry from the 13 classes in §3.** Leave the class
   names and any `cursor`/hit-testing they carry, exactly as P856 left
   `.die.cardmark`. Keep the flat-path CSS alive behind
   `html:not(.fk3d)` if the 2D path still needs it — check whether
   `D3_MATCH===false` is reachable before assuming it is.
2. **Build the over-canvas (§7.1)** and move `fog`, `snuff`, `snare`,
   `die-blind` and `die-frozen` onto it. These are the ones that must
   cover a face.
3. **Build `D3X.MARKS` (§7.2)** and move `sel` and `card` onto it
   unchanged — they already work, so they are the control: if the table
   changes how they look, the table is wrong.
4. **Paint the lane markers from `_lmArm` state.** Arm-to-fire, both
   sides, no timers.
5. **Delete the three sweep lists (§5).** They should have nothing left
   to clear. If one does, that class was missed in step 1.
6. **`_fxAnchor` (§7.3).**
7. **Resolve `die-kindred`** — wire it or delete it.

Steps 1 and 5 are net deletions. Step 3 is ~40 lines. The whole thing
should make the file smaller, which is the test of whether it was done
the right way.

---

## 9. VERIFICATION

The measurements, not the readings. Each one fails today.

- **No die effect paints an axis-aligned box.** Static, and the strongest
  check available: grep the stylesheet for `box-shadow|outline:|border:`
  inside any rule whose selector matches `.die` and is not `:not(.d3on)`
  or a shop/loadout scope. The count must be zero, and it must **stay**
  zero — this is the assertion that stops the thirteenth class becoming
  the fourteenth.
- **A mark tracks a moving die.** Drive it: arm fog, capture the mark's
  painted centroid, run a re-throw, capture again. The centroid must
  equal the die's projected centre in *both* frames. Measuring only the
  settled frame passes on a mark nailed to the slot, which is the bug.
- **Enchant lifetime is continuous.** Keep a fogged face, then sample
  every frame until the rival's turn resolves. There must be **no frame**
  between arm and fire where the mark is absent. Assert on the gap, not
  on "the mark appeared" — a 3.2 s emoji also makes it appear.
- **Nothing survives its cause.** Bust, hot-dice clear and destroy a die
  mid-effect, then assert no mark is painted for any die whose state is
  false. Today this is carried by 18 timers; after step 5 it should be
  impossible by construction.
- **Particle origin.** Fire `spawnShards` on a die physics has offset,
  assert the emission centre is within a few px of the die's projected
  centre. Do not assert it is inside the *chip* — that is the check that
  passes on the broken version.
- **`reducedMotion` actually reduces.** Turn it on, run a match with a
  reroll, a freeze and a fog, count animation frames on the mark layers.

---

## 10. WHAT NOT TO DO

- **Do not add `:not(.d3on)` to the 13 rules.** It works and it is the
  wrong fix: it leaves the box in the file, keeps the effect invisible in
  3D rather than correct, and adds a fourteenth thing to remember. The
  reason P856 stuck is that it *deleted* the box.
- **Do not fix this by raising `#dgCanvas` above the dice.** The rim
  wants to be underneath — that is what makes the selection glow read as
  a halo. Two canvases, one number apart.
- **Do not fold the lane marks into each enchant's `fire:` handler.**
  `fire:` runs at the wrong end of the lifetime. The arm is `_lmArm`.
- **Do not touch `FX.emit`'s pool, cap or sleep behaviour.** It is the
  best-behaved thing in this area of the file.
- **Do not start with §7.3.** Anchoring particles correctly on top of a
  broken mark layer looks like progress and fixes nothing Denis reported.

---

## 11. THE ONE ANSWER TO DENIS'S QUESTION

*"a Balatro-like efficient pipeline — which should already be
implemented, right?"*

Half of it is, and it is the half that is hard: pooled particles that
sleep, and a real projected hull that follows a tumbling die. What is
missing is not a system. It is **one canvas above the dice, one table
that says which effect paints where, and the deletion of thirteen CSS
rules that predate both.**
