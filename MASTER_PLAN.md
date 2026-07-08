# FARK MASTER REWRITE — EXECUTION PLAN

Companion to FARK_MASTER_BRIEF.md (the authoritative design doc). This file
is HOW we build it; the brief is WHAT. Vehicle: `fark_nights.html` on branch
`claude/zen-chatterjee-f04c42` — the live game (index.html / main) stays
untouched until Denis calls the switch. `_mockups/main_screen_new.html`
remains the UI design lab; screens port into the game as their systems land.

## Where we already are (delta vs the brief)

DONE in fark_nights.html (M1/M2 of the loop brief):
- Night/seat loop: 8 nights, pointsNeeded [2,2,2,3,3,3,3,4], buy-ins
  [10,15,25,35,50,65,80,100] clamped to purse, atomic seat consume,
  roster persistence, GONE HOME, LAST ORDERS, BARRED, chalkboard
  progression, handicap seat (worth double), turn caps 8/10 + ledger,
  draft-or-decline gold, exit lines, sim harness (_runBalanceSim).
  → Brief build-order step (2) is essentially landed. Gaps to audit:
  seats==pointsNeeded+2 per night, trailing-player final answer turn,
  sudden-death on exact tie, handicap loss removing a circle.

NEW (everything else): families/effect engine, dice v2, sleeve/rules,
spoils/relics/shelf, NPC families+AI policy+visible cards, For Keeps/lucky
dice/grudges, renown v2/titles/feats, economy pass, new screens.

CONFLICTS with current dev copy (need migration or removal):
- Renown perk ladder gates slots today → brief kills it (3 slots baseline).
- Persona words (PENNY-WISE...) → brief trait set (STEADY/BULLISH/ORDERLY/
  RECKLESS/GREEDY/CUNNING) with single-colour dark-red wax seals.
- Old CARDS pool (~120 usage sites, bespoke ifs) → replaced wholesale
  except the positional trio.
- Brass/Crystal/Ruby dice → removed, gold-refund migration.

## The keystone decision: one effect engine, three consumers

Everything in the brief reduces to one architecture: a small **event/effect
engine** threaded through the existing turn state machine.

- **Events** emitted at fixed seams: match-start, turn-start, pre-roll,
  post-roll, keep, pre-bank, post-bank, bust, turn-end, match-end —
  each with side (player/opp) + payload (dice, totals).
- **Effects** are data, not code: CARD_DEFS / RELIC_DEFS / TELL_DEFS rows
  declare {family, tier, trigger, verb, magnitude, charges, target, ui}.
  A verb library (~20 verbs: transmute, reroll-all, trap-die, shield,
  steal-on-bank, double-after-roll-N, peek-next-roll, force-reroll, ...)
  implements them once.
- **Three consumers of the same defs**: the player's card UI, the NPC
  policy table (persona × verb tendencies from brief §5), and the RULES
  layer (tells + sleeve = permanent uncharged effects bound to one or
  both sides — same engine, no charges).

Why first: all six families, all 8 relics, all 8 tells, the sleeve, and
NPC AI sit on it. Retrofit ordering (engine before content) is what keeps
this clean instead of 72 new bespoke ifs. Safety: land the event seams in
**shadow mode** first (events fire, nothing listens) and prove sim parity
with the pre-engine baseline before any effect migrates.

## Phases (each: build → sim gate → manual smoke → commit → NIGHTS_NOTES)

**P0 — Audit & scaffolding** (small)
- Delta audit of §1 gaps (seats count, final-answer turn, sudden death,
  handicap circle-loss); fix inline — they're loop-brief-sized tweaks.
- Grep-map every CARDS/dice touchpoint → seam list for the engine.
- Save-migration skeleton at _getS(): version bump, fixture saves
  (old-run snapshots) kept in _mockups/fixtures/ for regression.
- Sim baseline snapshot committed for parity checks.

**P1 — Effect engine + card families** (biggest phase)
- Event seams in shadow mode → sim parity proof.
- FAMILIES + CARD_DEFS as data (24 cards × 3 tiers, brief copy verbatim,
  tavern register). Verb library. Positional trio migrated with new
  numbers. Old pool deleted behind migration (old cards → nearest family
  equivalent or sell value).
- 3 card slots baseline (perk gating removed), sleeve slot stubbed.
- Draft v2: 60/40 family weighting, duplicate→upgrade-in-place, tier
  locks (II from night 3, III upgrade-only), decline gold 5+night*5,
  sell 15g.
- Gate: per-card scripted scenario tests (seeded), sim with player cards
  on, zero console errors.

**P2 — Dice v2 + shop + lucky dice**
- DICE_DEFS: mundane four + seven family dice (+Jade II tier visual),
  Obsidian shatter state, Silver save, Vagabond long-press reorder.
  Brass/Crystal/Ruby removed + refund migration.
- Shop rotation seeded per night with SOLD slots (non-deterministic pool).
- Lucky dice: every patron carries one named, marked, slightly-better die
  (peek card shows it).
- Gate: buy/sell/refund paths, shatter+save engine events, econ smoke.

**P3 — Rules engine: tells v2 + the sleeve**
- Generalize tells into side-bindable RULES; sleeve = player-claimed rule
  bound to both sides; boss fights run up to two rules (two HUD badges).
- ALDRIC rotating-seal rework; CORVUS sleeved-side rewrite.
- NPC bank/roll policy respects active rules (min-bank, roll caps, curses).
- Gate: every tell sleeved in sim both sides; boss double-rule fight;
  Tamper × Confession coexistence; RECKONING dominance flag.

**P4 — Spoils + relics + shelf**
- SPOILS overlay (relic / tell / purse — pick one, final). 8 relic defs on
  the engine. Shelf on loadout (claimed tells, trophies). Night-8 renown
  payout stub.
- Gate: choice finality, each relic sim-checked, shelf persistence.

**P5 — Opponents v2** (second-biggest)
- Trait renames + seal mapping; trait→family bias matrix with night-3+
  off-diagonals; patron card counts/tiers by night; boss family pools.
- NPC card AI: ONE policy table persona × verb implementing exactly the
  brief's signature behaviours (no more). Opponent cards visible at their
  table edge + parchment callouts + ledger lines.
- Period titles by night band (one const, generator-prefixed).
- Gate: seeded scenario per persona proving its signature move; sim win
  rates rerun; readability pass in preview.

**P6 — For Keeps + grudges**
- For Keeps (unique, night 4+, patron-only): win/lose die transfer
  including lucky dice; loss path where THEY pick. Grudge flag on beaten
  bosses/archetypes whose die you hold: meaner dialogue pool, +1
  aggression tier.
- Gate: both transfer paths incl. relic loss, grudge trigger across nights.

**P7 — Renown v2 + feats**
- Perk ladder deleted (compensation cosmetic in migration). Invisible
  counter → title ladder (same period const as NPCs), NPCs address player
  by title. Cosmetics shelf thresholds. Feats retuned to family stunts,
  toasts on victory overlay.
- Gate: fixture-save migrations land clean, feats fire, no perk references
  remain.

**P8 — Sim extension + economy pass**
- Harness coverage for the flagged set (§9 list). Acceptance: patron
  60-70%, boss 45-55%, median 5-7 banked turns/side. Targets compressed
  BEFORE player scoring inflates. One economy pass across buy-ins/rewards/
  purses/prices/sell/decline.
- Gate: acceptance table green in NIGHTS_NOTES.

**P9 — Screens & juice** (continuous port + final polish batch)
- Port the mockup system per screen as its mechanics land: Room cards
  (live roster data + family dice chips + lucky marker), character panel
  (per-class art), boss peek, match HUD (rule badges, visible opp cards,
  family FX states), victory/defeat, SPOILS centrepiece, dice store
  rotation UI, loadout (reorder, sleeve, shelf), LAST ORDERS, BARRED,
  run-won. v21 dice renderer port. Motion rules from the addendum.
- CSS placeholders stand in wherever art isn't delivered; art swaps are
  one-line src changes.

## Art dependency list for Denis (gates P9 slices, not the engine)

- Panels re-exported **without baked text** (law 4 — current Krox panel
  bakes name + labels), one per class (commoner/noble/...).
- Trait seals: single-colour dark-red wax, symbol-only set (6). Black wax
  + ribbon handicap seal (distinct).
- Tier borders: tin/silver/gold + roman numerals (glance-readable).
- Dice art: 4 mundane + 7 family + Jade II variant + obsidian cracked
  state + 8 relics + lucky-die marker.
- Match FX layers: ward shimmer, amber casing, smolder tray, positional
  glow, ghost dice.
- SPOILS table overlay (the centrepiece), shelf art, sleeve slot frame
  (boss-dark-wood), boss-ready restage pieces, SIT DOWN/Close anim layers.

## Working method

- All code in fark_nights.html via assert-counted python patch scripts;
  commit per coherent slice; NIGHTS_NOTES.md is the running ledger
  (decisions, sim tables, checklist state).
- Sim before/after every phase; fixture saves regression-run at every
  migration-touching phase.
- Never push to main; share builds regenerated on request.

## Risk register

1. Engine retrofit breaks the match flow → shadow-mode seams + sim parity
   before any listener lands.
2. Single-file growth → section banners, data tables grouped, dead code
   deleted (not commented).
3. Art bottleneck → placeholders first; art is swap-in.
4. NPC AI scope creep → policy table implements the brief's listed
   tendencies only.
5. Rule interactions (Aldric × Tamper × sleeve) → explicit test matrix in
   P3 gate.
6. Migration data loss → fixture saves from day one; migrations pure
   functions testable in console.

## Open questions for Denis (answer before the relevant phase, not now)

1. P1: exact three starting cards / first-draft pool for night 1?
2. P2: shop rotation size (how many slots visible, how many SOLD)?
3. P4: purse amounts per boss band (brief says sim-tuned 500-700+; seed?)
4. P9: which screens keep mockup-first iteration vs direct in-game build?
