# CARD VFX — per-card effect designs (C15)

Written 2026-08-15. Every recipe below composes EXISTING primitives — the
announce queue (`famLog`), the card beats (`cardFx`: hit/pulse/churn/steal +
`_fxSpray`), `spawnCardBurst`, the bust shield (`_bustShieldFX`), the spark
band (`_sparkBand`), D3X's die-level machinery (`_settleDim`, dim maps, kick,
`_isoQ` lay pose) and the existing keyframes (`card-fired`, `fx-shake`,
`fx-pulse`, `pin-land`). No new systems; a recipe that seems to need one goes
back to the drawing board.

**Test them in `fark_lab.html`** (repo root, served like the game). The lab
drives the REAL game in an iframe — every recipe runs the game's own
functions, so what you approve in the lab is what ships, minus wiring.

**The clarity rule**: each cast reads in three beats — (1) THE HAND ACTS
(something leaves or transforms at the card), (2) THE TABLE ANSWERS
(the affected die/lane/row visibly changes state), (3) THE LEDGER SPEAKS
(the announce line + any score movement). A player who missed beat 1 must
still understand the outcome from beats 2+3.

---

## AMBER (traps, patience)

### Preserve — the amber shield (Denis's spec, A1b)
1. **Cast** (drag past line): `card-fired` flash + `SFX.cardFire` (exists).
2. **The trap closes**: the chosen die gets an AMBER OVERLAY — a rounded-corner
   radial gradient div in the die-wrap (`rgba(232,162,60,…)` core, darker rim),
   scaling in at 1.3→1.0 over 250ms + one `_fxSpray(die, '#e8a23c', 12)`.
   Audio: a low glassy *set* (reuse `SFX.bank`'s tail or the amber
   break-trigger cue).
3. **On bank**: the ambered die slides STRAIGHT DOWN ITS LANE (translate only,
   no arc — it is set, not thrown) to a rest band below the throw line,
   staying visible at ~0.8 scale. NOT greyed — ambered (the overlay carries
   the state).
4. **Opponent's turn**: it sits there; NPC dice never enter that band.
5. **Player's next roll**: thrown dice settle FIRST; then the preserved die
   slides back up its own lane, scales 0.8→1.0, the amber overlay cracks —
   two-frame split sprite or a scale+fade pop + `_fxSpray('#ffd98a')` — and
   the announce: `THE AMBER CRACKS — A 1 ALREADY KEPT`.
   Resume-safe: the record already carries `{val,mat,ench,lane}` (P726).

### Honeytrap
1. Cast → the card fires; the chosen kept PAIR gets a honey glaze (amber
   overlay at 40% + slow drip keyframe on the two chips).
2. On the next roll, when the pulled die settles into the match: a short
   golden thread FX from pair to die (`_fxSpray` with `dir` aimed, the
   'steal' beat pattern reversed) + `fx-pulse` on all three.
3. Announce: `THE HONEY HOLDS — A THIRD X JOINS THE PAIR`.

### Slow Cook (passive)
Passive glint only: when its trigger pays, `cardFx('gain', card)` — no new
work; verify the glint reaches the fcv row.

---

## The rest of the live set — one line each (full steps in the lab)

- **Transmute**: the die's material VISIBLY re-dresses (D3X `_rebrand` is the
  effect); add `churn` beat on the card + spray in the NEW material's SPARK
  colour at the die.
- **Fool's Gold**: the fake die glints gold (`fx-pulse` + gold spray), then
  desaturates over 400ms when it turns out false (CSS filter ramp on the chip).
- **Bloom**: jade spray (`SPARK.jade`) rising (negative g) from the die that
  bloomed; announce carries the new face.
- **Powder Keg**: the keg card SHAKES (`fx-shake`) each roll it charges;
  at 3, a red-orange `_sparkBand` burst + the candle flicker (C14's red
  candle, reused) before the payout announce.
- **Sacrifice**: the chosen die's chip does the bust-wipe darken (k>1 dim
  ramp — `_trayTint` past 1) then lifts off the table (translateY + fade);
  `steal` beat carries its value INTO the card.
- **Short Fuse**: a burning-down underline on the card (width 100→0 over the
  turns left, CSS transition) — state, not just a moment.
- **Stargazer**: the three preview dice get the `lay` rest pose in a small
  strip over the card (same `_isoQ(v,TILT,true)` the table now uses) —
  fading in staggered like the draft labels.
- **Ill Omen / Sleight (rival)**: keep the red ARMED rise (exists) and add
  the fire moment: `fx-shake` + red spray on the VICTIM surface, so cause
  and effect share a frame.
- **Vanguard/Anchor/Bookends (positional)**: on cast, the LANE(S) the card
  cares about get a brief gold floor-glow (inset box-shadow on the lane
  band, 600ms fade) — teaches the positional rule by pointing at the felt.
- **For Keeps / Double Stakes (run-scoped arms)**: the armed state is the
  P727 pop + halo on the ROOM card surface; on the match that consumes it,
  one announce + `gain` beat when the wager pays.
- **The Tab / Hair of the Dog / Marked Table / High Table**: ledger cards —
  their moment IS the announce; give each a distinct accent colour on the
  status line (the `_statusCls` colour argument, already supported).

---

## C14 — bust scatter + the red candle (direction)

Scatter: the impulse field is centre-out (dice part in the middle). Vary per
die: random direction ±35° off outward, magnitude 0.7–1.4×, spin sign random,
2 of 6 dice get a stronger kick — chaos reads from VARIANCE, not force.
Candle: on bust, lerp the D3X key light + ambient toward `#c03818`/`#5a1408`
over 250ms, hold 400ms, lerp back over 900ms — the whole table flinches.
(The same rig drives A3b's "darker room" if adopted.)

## A3b — the accidental look (from the legacy engine)

What Denis saw was D3's face-ramp: shading `0.55+0.55*max(0,N·L)` per face,
painted per-face shadows (sharp at contact, soft above), no specular. D3X
equivalents to try in the lab: drop key light intensity ~15%, raise SIDEDIM_MAX
toward 0.6 with a longer in-flight ramp, and a two-layer 2D shadow (tight
dark ellipse + wide faint one). Environment darkening toward the target
score: multiply the env painting's brightness 1.0→0.82 as pPts/target →1
(CSS filter on the room/table bg, stepped per bank so it never distracts
mid-roll).
