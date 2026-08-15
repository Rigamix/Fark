# THE EFFECT LANGUAGE — cards, dice, enchants (C15c)

Written 2026-08-15, before the lab presets were coded, then read back
critically (the editor's pass at the bottom caught and fixed six
inconsistencies — they are marked ✎ where they changed a rule).

The executable data lives ONCE, in `fark_lab.html` (`ID_META` + the family
templates). This doc is the language and the reasoning; the lab is the
source of truth for numbers. When they disagree, the lab is right and this
doc gets corrected.

---

## 1. Principles (what the reading list actually says)

Distilled from Swink's game-feel model and the juice canon (Juice It or
Lose It; Vlambeer's Art of Screenshake) plus practical VFX/code guides:

1. **Response before juice.** The state change lands the same frame as the
   input; polish rides on top and never delays it. A card fires NOW; the
   pretty part explains it afterwards.
2. **Proportional impact.** The effect's size matches the event's weight.
   A 50-point keep does not shake the table. Going up in power adds
   LAYERS, not volume (see the ladder, §3).
3. **Readable at a glance.** Every effect answers "what just happened and
   to whom" even if you missed the first frame — the three-beat rule (§2).
4. **Ease everything; nothing constant.** Scale, alpha and position all
   ramp — ease-out for arrivals, back-out for pops, ease-in for exits.
   Particles shrink and fade over their lifetime.
5. **One layer at a time.** Build the core beat first, verify it reads,
   then add a layer. If a layer doesn't add meaning, cut it.
6. **Variety within identity.** Small random jitter (±15% speed, count,
   angle) so repeats don't look stamped — but the family signature
   (colour, verb, sound) never changes.
7. **Restraint is a feature.** This is a cosy tavern, not a slot machine.
   The table responds (candle, vignette) only for the biggest moments —
   if the room flinches at everything, it means nothing.
8. **Pool, don't allocate.** The existing `_fxSpray` particle pool is the
   only particle system; new effects parameterize it rather than adding
   engines.

## 2. The three beats (unchanged from CARD_VFX.md)

1. **The hand acts** — something happens at the card/die that was used.
2. **The table answers** — the affected thing visibly changes state.
3. **The ledger speaks** — the announce line + score movement.

A player who missed beat 1 still understands the outcome from 2+3.

## 3. The power ladder — layers, not volume

- **L1 (tier I / common moment):** one core FX + one sound. ~400ms.
- **L2 (tier II / strong moment):** L1 + one supporting layer (halo ring,
  echo particles, second sound voice one octave up). ~650ms.
- **L3 (tier III / boss-grade):** L2 + one WORLD response (candle tint,
  brief room dim, table vignette). ~900ms. World responses are RESERVED
  for L3, busts, and boss beats — nowhere else. ✎E1
- Sounds ladder the same way: same waveform family, added harmonic voices
  — never a different instrument at higher tiers.

## 4. Action families — the shared visual+sound vocabulary

| family | verb | palette | core visual | core sound (synth) |
|---|---|---|---|---|
| **SET** (trap) | enclose | amber `#d88a20` | 3D shell closes over target, corner-rounded | `set` — glide 440→220 + glass harmonic |
| **PAY** (gain) | rise | gold `#ffd98a` | rising sparks, negative gravity | `chime` — 2 staggered sines, warm |
| **COIN** (gold specifically) | drop | coin gold `#e8c874` | short arc sparks into the HUD | `coin` — triangle blip pair ✎E2 |
| **STRIKE** (disrupt) | hit | rust `#c05a3a` | shake + downward burst AT THE VICTIM | `thud` — 120→60Hz drop + noise |
| **TRANSFORM** | churn | jade `#46c46e` | swirl spray + material re-dress | `shimmer` — rising pentatonic stagger |
| **FATE** (reveal) | glimmer | starstone `#8fa8ff` | slow twinkle, lay-posed preview | `bell` — long-decay fifth |
| **BREAK** | shatter | obsidian `#e2582f` | crack flash, shards, die exits | `crack` — HP noise snap + thud tail |
| **ARM** (wager) | pulse | deep gold `#c8a45c` | heartbeat scale pulse ×2 | `drum` — 55Hz double pulse |
| **LEDGER** | note | parchment | announce line only, accent colour | `scratch` — bandpass tick |

Direction rule: STRIKE effects point AT the victim (spray `dir` aimed);
PAY effects point AT the beneficiary's HUD. Cause and effect share a
frame whenever both are on screen.

Announce colour rule: gold = for you, red = against you, green =
transform/growth. (The `famLog` colour argument already carries this.)

## 5. Card presets (family, layers, the fun bit)

Active AMBER — **Preserve** SET L1→L3: shell closes (rounded), die parks
down its lane at 0.8 scale. Fun: at tier III a tiny fly sits in the amber
(one dark pixel-sprite in the shell). Return = `clearShell` + PAY sparks.
**Honeytrap** SET: glaze on the kept pair (shell at 0.35 opacity, honey
colour), the pulled die gets a short golden thread (aimed spray) when it
joins. Fun: the two flies from the card art buzz one lap on cast (two
tiny dark particles orbiting once).
**Slow Cook** passive PAY glint on each payout tick, pot-bubble particle
(1-2 slow rising blobs).

Active OBSIDIAN — **Powder Keg** ARM while charging (pulse each roll,
fuse underline shortens), BREAK payoff (L2: shards + candle flicker —
the ONE non-L3 world touch, it is literally an explosion ✎E1 exception,
logged). **Sacrifice** BREAK→PAY sequence: the die darkens (bust-wipe
ramp), cracks, shards fly INTO the card, then PAY chime — two families
SEQUENCED, never blended ✎E3. **Short Fuse** passive: fuse underline on
the card, burns per turn; STRIKE thud when it fires.

Active JADE — **Transmute** TRANSFORM: churn swirl at the die, material
re-dress mid-swirl (the swap hides inside the peak, like the map-swap
trick), shimmer. **Bloom/Cultivate** passive TRANSFORM glints: a leaf
particle (jade spray, low count) when they pay.

Active STARSTONE — **Stargazer** FATE: three lay-posed preview dice fade
in staggered over the card with faint lines between them (a
constellation — the fun bit), bell. **Ill Omen** FATE→STRIKE: bell +
violet glow when armed; when it fires on the rival, the STRIKE beat
happens on THEIR row (direction rule).

Active VAGABOND — **Sleight/Tamper** STRIKE at the victim card/die +
red ARMED rise kept from today. **For Keeps** ARM on seating (drum), PAY
when the wager pays. **Fool's Gold** PAY glint that LIES: gold sparks,
then the die desaturates 400ms — the joke is the fade. **Vanguard /
Anchor / Bookends** positional passives: lane floor-glow (inset shadow
band) on cast/arm showing WHICH lanes, LEDGER when they pay ✎E4.

TAVERN (ledger cards) — **The Tab / Hair of the Dog / Cursed Table /
High Table / Double Stakes**: LEDGER family — announce with accent
colour + at most an ARM pulse when armed. Fun: The Tab gets chalk tally
strokes in the announce (│││ characters building up). No particles —
restraint ✎E5.

Any card not named here takes its family template unchanged — coverage
by construction, including future cards.

## 6. Die material presets (their SCORING moment)

L1 for commons, +1 layer per rarity band. The moment = "this die's
family trait pays":
- **bone/iron/flint/lead** — LEDGER only (they have no trait): a plain
  keep stays quiet. ✎E6: commons must NOT sparkle; silence is what makes
  amber's sparkle mean something.
- **amber (+triples)** — PAY chime + amber glint on the triple's three dice.
- **jade/jade2/jade3 (wilds)** — TRANSFORM shimmer on the wild face when
  it counts; jade2/3 add one voice each.
- **brass** — COIN blip (its trait is gold-ish); **silver** — FATE tick
  (bank save); **crystal** — FATE glass ring; **ruby** — STRIKE-red PAY
  (aggressive gain); **obsidian** — BREAK flash on its break-trigger;
  **starstone** — PAY at BANK time (its trait), sparks arc to the score;
  **vagabond** — STRIKE-flavoured steal beat; **lucky** — COIN + a tiny
  green four-leaf particle (fun bit).

## 7. Enchant presets (the brand fires)

Brands live on a face; the moment is `_iconFire`:
- **tithe** COIN: coin sparks arc from the die to the gold counter + blip.
- **ward** SET(defensive): a brief shield shell flash (silver-blue,
  rounded) over the WHOLE die + the existing bust-shield when it saves.
- **snare** SET(hostile): amber-family enclose but rust-tinted — it's a
  trap ON the rival ✎E3 direction.
- **trade** TRANSFORM: two dice swap-swirl.
- **snuff** BREAK(small): a pinch of dark shards, no candle.
- **quicksilver** TRANSFORM(liquid): mercury shimmer (silver palette,
  fast, low gravity) on the free reroll.

## 8. The sound bank (all synthesized, one AudioContext)

Nine families (§4 table) + params: `pitch` ×0.5–2, `layers` 1–3 (adds
octave voices), `dur` scale. Same-family actions share the waveform;
tiers add voices. Implemented in the lab as `SND.play(family,opts)`;
porting into the game means folding into the existing `SFX` object —
same synthesis, one owner. Master gain low (0.4): tavern, not arcade.

## 9. THE EDITOR'S PASS (read-back, caught before coding)

- ✎E1 First draft gave candle responses to five cards. That makes the
  room's flinch meaningless. RESERVED for L3/bust/boss; Powder Keg keeps
  one as the logged exception (it IS an explosion).
- ✎E2 Gold gains and point gains were one family; they read differently
  in play (gold goes to the pouch, points to the chalk). Split PAY/COIN,
  same warm palette, different pitch — related, distinguishable.
- ✎E3 Sacrifice first draft BLENDED break+gain (orange-gold mush).
  Sequenced instead: dark → crack → gold. Families never blend; they
  take turns. Same rule gives snare its rust tint rather than a new verb.
- ✎E4 The positional vagabond passives had no visual at all in draft 1
  ("they're just rules") — but positional rules are exactly what players
  misread. The lane floor-glow teaches WHERE by pointing at the felt.
- ✎E5 The tavern ledger cards were getting particles for symmetry.
  Symmetry is not a reason. They are bookkeeping; the announce IS their
  effect. Restraint kept.
- ✎E6 Draft 1 gave every material a scoring flourish. If bone sparkles,
  amber can't. Commons are silent by design.
- FUN LIST kept from the read-back: preserve's trapped fly (III),
  honeytrap's buzzing lap, fool's gold's lying glint, stargazer's
  constellation lines, the tab's chalk tallies, lucky's clover.

## 10. THE DESIGNER'S SECOND PASS (2026-08-15, after Denis's amber note)

"Encased, ok — but boring." Correct. The first pass proved the VERB;
this pass makes the MATERIAL. The method, per effect: name the physical
material the effect pretends to be, list what light does to that
material, then fake each behaviour with the cheapest trick that reads.

**Amber, the case study** (all five now in the lab, each with a slider):
- Amber is GLOSSY → a hard off-white specular hot-spot (Phong shell,
  `specular` slider). One highlight sells "polished surface" instantly.
- Amber is DEEP → light attenuates with path length. Real refraction is
  a shader; the fake is NESTED RIM SHELLS (1-3 layers): at grazing
  angles you see through more layers, so edges read denser — the classic
  cheap Fresnel. `rim layers` slider.
- Amber BLURS what it holds → a GHOST PASS: a 1.035-scale clone of the
  die's own textured mesh, amber-tinted, low opacity. The doubled faces
  read as refraction blur, one extra draw call. `ghost blur` slider.
- Amber has INCLUSIONS → 3-5 tiny pale bubbles drifting slowly inside.
  Bubbles also tell SCALE (small bubbles = big die). `bubbles` slider.
- Amber is VISCOUS → the outer particles become DRIPS: fewer, larger,
  slower, heavy gravity, narrow spread — sliding off, not popping.
- The trap SNAPS → a 200ms rotation jitter as the shell closes. A trap
  that doesn't twitch is a display case.

**The same interrogation, per family:**
- **STRIKE** — impacts are about the FIRST FRAME: a 60ms white flash on
  the victim before the shake (the hit-frame every fighting game uses),
  then dust: grey, large, slow, drifting UP. Force reads from the flash;
  weight reads from the dust.
- **BREAK** — destruction has an ORDER: flash → crack sound → shards
  OUT + smoke puff hanging. Smoke is what makes a break feel physical;
  shards alone are confetti.
- **PAY** — gold should HANG: sparks decelerate (low negative gravity)
  and linger at the top of their arc; at power 2+ a faint vertical light
  column lifts off the target. Money rises and pauses; it never pops.
- **TRANSFORM** — change needs an AFTERIMAGE: the die's tinted ghost
  lags 200ms behind the spin and fades — the eye keeps the old identity
  on screen while the new one arrives. Swap hidden at the spin peak.
- **FATE** — fate is SLOW: the bell, a faint beam rising off the target,
  then two delayed twinkles (250ms, 500ms). Nothing moves fast; that is
  what separates it from PAY.
- **ARM** — the heartbeat stays; at power 2+ a rim-light sweep crosses
  the card once (light moving across a surface = "charged", cheaply).
- **SET (ward variant)** — same shell language but a FLASH, not a hold:
  200ms specular ping in silver-blue. Defence is a reflex, not a home.
- **LEDGER** — pushed by NOT pushing. The scratch tick and the line.

Every new ingredient is a slider in the lab (Shell studio group), and
every one is built from the existing pool: Phong material on the same
rounded geometry, mesh clones, sphere primitives, `_fxSpray` params,
overlay divs. No new systems.

## Sources

- [How to Make Your Game Feel Good: A Guide to Game Feel and Juice](https://egmatic.com/blog/how-to-make-your-game-feel-good)
- [Squeezing more juice out of your game design (GameAnalytics)](https://www.gameanalytics.com/blog/squeezing-more-juice-out-of-your-game-design)
- [Juice in Game Design (Blood Moon Interactive)](https://www.bloodmooninteractive.com/articles/juice.html)
- [Satisfying player feedback with VFX and sound (itch.io)](https://itch.io/blog/1063213/satisfying-player-feedback-with-vfx-and-sound)
- [Particle Systems: stunning visual effects with code (Lumitree)](https://lumitree.art/blog/particle-system)
- [Game particle effects — complete visual guide (Gamine)](https://www.gamineai.com/blog/how-to-create-game-particle-effects-complete-visual-guide)
