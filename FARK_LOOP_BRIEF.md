# FARK — core loop redesign brief

For: Claude Code session on the Fark repo (single-file game, index.html, ~1.3MB).
From: design review session with Denis. Read this whole file before touching code.

## Context and diagnosis

The game is a Farkle roguelike: 8 tiers (TIERS), each with generated patron matches
(generatePatron) building points toward a tier boss (RUNGS), 3 hearts (S.run.coins)
lost only on boss defeats, gold for the dice store, post-win card drafts, persistent
renown with perks (RENOWN_PERKS), feats (FEATS).

Problems this brief fixes, in priority order:

1. Runs are far too long. pointsNeeded sums to 40 patron wins plus 8 bosses. Sim
   shows bone dice bank ~440/turn; tier 7 patron targets (~16k) mean 12+ banks per
   side even with gear. A full run is 4+ hours.
2. Patron matches carry zero stakes. launchPatronMatch always passes buyIn:0,
   effectiveWager:false. Losing costs nothing but time.
3. No forcing function. Patrons stay farmable after the boss unlocks and pay
   risk-free gold, so optimal play is safe grinding. The game rewards its most
   boring line.
4. New players get 1 regular card slot until 60 renown. The buildcraft layer is
   meta-gated exactly when we need to hook people.
5. NPC turns are dead time. No skip, ~700ms step delays, roughly half of match
   time is watching.
6. Late-tier scaling: targets grow 7x tier 0 to 7, player scoring boosts are mostly
   additive. Needs data, not guesses.
7. Dead systems in code: RUNGS wager/buyIn fields unused, gauntlet only reachable
   via the vagatest debug URL.

## Design principle (applies to everything)

Never let the player choose what they risk. A previous card-wager version failed
because players always staked their worst card. Every stake in this brief is
either fungible (gold, hearts, seats), chosen by the game, or chosen by the
opponent. When implementing, run every new system through this test: "what does
a min-maxing player do, and does the system still work?"

---

## P1 — The Night structure (seats)

Replace unlimited patron matches with a finite per-tier roster. Theme: each tier
is one night at the tavern.

### Data and state

- Add to TIERS per tier: `seats` = pointsNeeded + 2 (after the P3 pointsNeeded
  reduction below, so seats become: 4,4,4,5,5,5,5,6).
- Add to S.run (and _freshRun):
  - `night: { roster: [patronSnapshot, ...], seatsPlayed: [bool,...], failed: false }`
  - roster is generated once when the tier screen first renders for that tier,
    via N calls to generatePatron(S.run.tier). Persist the full patron objects
    (they're already plain data) so the roster is stable across app restarts.
    Strip any functions before save; regenerate derived bits on load if needed.
- Save migration in _getS(): if S.run exists without `night`, build a roster for
  the current tier and mark seats consumed equal to nothing (fresh roster,
  keep current S.run.points). Old mid-run saves must not break.

### Tier screen (initTierScreen)

- Replace the single "play patron" button with a seat roster UI: one row/card per
  patron showing name, portrait/icon, persona hint (one word, e.g. "reckless",
  "hoarder", derived from _personaKey), dice material chips, target, buy-in,
  gold reward, and whether the seat is spent. Spent seats stay visible but
  greyed with a WON or LOST stamp.
- Choosing which seat to play is meant to be a real decision. Show enough info
  to scout, not so much it's homework. Dice chips plus persona word plus target
  is the right amount.
- The handicap offer becomes a property of ONE random seat in the roster
  (visually marked) instead of a separate button. Playing that seat with the
  handicap active earns 2 points and doubles gold, exactly as now
  (pointsEarned logic in endMatch already handles it). Keep the existing
  handicap persistence rules (locked per tier).

### Rules

- Playing a seat consumes it, win or lose. Store in seatsPlayed.
- Patron win: +1 point (+2 handicap), gold reward as now (15 + tier*10 formula
  in endMatch stays, but see P2 buy-ins).
- Boss unlocks at pointsNeeded as now (_bossReady check). Remaining unplayed
  seats REMAIN playable after unlock. This is intentional: bounded greed, the
  player weighs extra gold and drafts against buy-in risk.
- If ALL seats are spent and points < pointsNeeded: the night fails.
  - Cost: one heart (same path as a boss loss in _settleEndRoute: decrement
    S.run.coins, death at 0).
  - Then re-roll the night: new roster, points reset to 0, seatsPlayed cleared.
  - Show a short "LAST ORDERS" fail overlay before the re-roll so the player
    understands what happened and why. This must be impossible to misread.
- Points now reset per night as they already do on boss win (S.run.points=0 in
  _settleEndRoute). No change needed there beyond the fail path.

### Degenerate-play checks (write tests or at least verify by hand)

- No path may regenerate or refill seats except night-fail (heart cost) and
  boss victory (new tier). Grep for every write to S.run.points and the new
  night state.
- Gold income per tier is now bounded: seats * reward + boss gold + innkeep
  book. Confirm the dice store economy still functions at these caps (see P6
  sim; expect dice prices to need a pass).

## P2 — Buy-ins on seats

- Wire the RUNGS-style buyIn values into generated patrons: add
  `buyIn = clamp(round((10 + tier*12)/5)*5, ...)` or simply reuse a per-tier
  table: [10,15,25,35,50,65,80,100]. Tune later via sim; put the table in one
  const.
- Paying: deducted when the seat starts. Win returns the buy-in PLUS the reward
  (net positive). Loss forfeits it.
- Broke rule: buy-in is clamped to available gold, floor 0. A player with 3g
  pays 3g. No seat is ever unplayable for lack of gold. Being broke is already
  the punishment; never soft-lock.
- Boss fights and night-fail have no buy-in. Hearts are the boss currency.
- UI: show the buy-in on each seat card and animate the deduction on seat
  start. On the victory overlay, present the payout as "pot" (buy-in returned +
  reward) so the win feels bigger than the old flat reward.
- The showScreen('match', {...buyIn, effectiveWager...}) plumbing already
  exists with dead values; repurpose it rather than adding parallel params.

## P3 — Match length: turn caps and pointsNeeded cuts

### pointsNeeded

Change TIERS pointsNeeded from [3,4,4,5,5,6,6,7] to [2,2,2,3,3,3,3,4].
Seats derive from these (+2). Expected run length: ~22 patron seats actually
needed plus 8 bosses plus optional greed seats. Target: a winning run in
roughly 90 to 120 minutes.

### Turn cap

- Add a banked-turn cap per match: patron matches capped at 8 banked turns per
  side, boss matches at 10. Put both in consts.
- A "banked turn" = a completed player or NPC turn (bank or bust both count).
  The existing _featBanks style counters show where turn completion is already
  tracked; add explicit G.pTurns / G.oTurns.
- If the cap is reached and neither side crossed the target: higher total wins.
  Exact tie: one sudden-death turn each, repeat until broken.
- Keep the existing last-licks behaviour (when one side crosses the target the
  other gets a final answer turn). This also neutralises stall-banking by a
  leader near the cap: the trailing side always gets the last word. Verify the
  interaction: cap reached on the leader's turn must still grant the trailing
  side their final turn before comparison.
- HUD: show turns remaining (e.g. small pip row or "TURN 5/8"). Must be visible
  at a glance; the cap changes bank-or-push math and the player needs it
  on-screen, not in memory.
- Tells and cards that reference turns (sudden_death handicap, per-roll tells
  like Steeped, The Tab's escrow) need an audit pass against the cap. List
  every card/tell touching turn structure and confirm behaviour at the cap
  boundary before shipping.

## P4 — Card slots and renown rework

- _freshRun cards stays [null,null,null,null] but slot unlock logic
  (_isSlotUnlocked) changes: slots 1 AND 2 always unlocked. Slot 0 remains the
  boss-signature slot, always unlocked.
- RENOWN_PERKS changes:
  - threshold 60 perk ('fourthSlot', label Trusted Hand): now unlocks slot 3
    (the true 4th). Update desc text.
  - threshold 160 perk ('secondBoss', label Lord of Dice): REPLACE with
    `extraSeat`: "+1 seat every night". Implement as seats+1 when rostering.
    Update label to something tavern-flavoured (e.g. "House Favourite").
  - All other perks unchanged.
- Migration: players with existing renownPerks keep everything; anyone past 160
  gets extraSeat granted on load. Nobody may LOSE a slot they had.
- Sanity: patrons at T1 have 2 cards, T2+ have 3 (generatePatron). Player at
  2 base slots plus signature is now roughly at parity instead of under-carded.

## P5 — NPC turn pacing

- Settings toggle: RIVAL SPEED, Normal / Fast. Fast multiplies every NPC-turn
  setTimeout delay by ~0.4. Centralise the delays in runOppTurn (and its
  step/finOpp chain) behind a single `_oppDelay(ms)` helper first, then apply
  the multiplier there. Do not scatter multipliers.
- Tap-to-fast-forward: during an NPC turn, a tap anywhere on the dice area
  accelerates the REMAINDER of that turn (multiplier ~0.15, not instant, so
  card triggers and tell events still visibly fire in sequence).
- End-of-NPC-turn ledger line: always show a compact one-line summary after
  their turn resolves ("MABEL rolled 4x, banked 650" or "GROG busted"). This is
  the safety net that makes fast-forwarding safe: the player can never end up
  confused about what happened.
- Bosses default to Normal speed regardless of the toggle on their FIRST
  encounter per run (tells deserve the theatre); after that the toggle applies.

## P6 — Balance sim harness, then retune targets

Build before retuning numbers. Do not hand-tune targets without it.

- Add a debug-only in-page harness `_runBalanceSim(cfg)` (callable from console,
  optionally a `?sim=1` URL trigger like the existing vagatest pattern).
- It must reuse the REAL scoring path (scoreRoll / scoreSelection) and the real
  NPC bank policy (oppShouldBank), not reimplementations.
- Player policies to include, parameterised: keep-all-scorers with bank
  thresholds {300, 500, push-to-hot-dice}, honouring diceStop analogues.
- Gear levels: define 4 snapshot loadouts (all bone; tier-2-ish mixed iron/lead
  plus 1 tin card; tier-4-ish amber/jade plus 2 cards; tier-6-ish premium plus
  3 cards). Cards in sim can be limited to the deterministic bank-bonus ones
  (starstone dice, flat bank adders); skip interactive actives.
- Output per (tier, gear, policy): win rate vs generated patrons and vs the
  boss, median banked turns per match, bust rate, gold delta per night.
- Acceptance targets after retune:
  - Median patron match: 5 to 7 banked turns per side at the intended gear
    level for that tier.
  - Patron win rate at intended gear: 60 to 70 percent. Boss: 45 to 55.
  - If tier 6 to 7 can't hit those inside the 8-turn cap, LOWER the targets
    (Aldric/Whisper/Ambrose targets and patron targetMin/Max) rather than
    inflating player scoring. Additive boosts vs 7x targets is the known
    structural gap; compressing the top of the curve is the cheap fix.
- Also use the sim to sanity-check the P2 buy-in table and dice prices against
  the new bounded per-night gold income. Dice should feel purchasable roughly
  every 1 to 2 nights early, every night mid-game.

## P7 — Draft decline value

- On the post-win draft, add a fourth option: decline for gold (amount = about
  half the tier buy-in, e.g. 5 + tier*5). Kills the dead-choice feel when all
  three cards are worse than the loadout.
- Degenerate check: with slots at 2 to 4 and bounded seats, decline-gold cannot
  be farmed. Amount must stay clearly below a seat reward so playing seats is
  never dominated by draft-declining.

## P8 — Optional, v2, do NOT build in this pass

Documented so the ideas aren't lost; skip unless explicitly asked.

- HIGH ROLLER seat: rare roster seat, no buy-in. Stakes: on a loss the PATRON
  takes a card, choosing the player's highest-rarity card (deterministic, so no
  sandbagging); on a win the player picks one of the patron's three cards. This
  is the corrected card-wager design: the opponent chooses the stake.
- GAUNTLET: currently dead (only the vagatest debug URL sets inGauntlet).
  Leave the code parked. Candidate future use: post-tier-7 endgame, a run of
  all 8 bosses back to back for a renown jackpot. Decision deferred.

## P9 — Visual architecture: layered plates, sprites, HTML text

The art direction moved away from the current pixel assets toward hand-painted
illustration (Midjourney-generated plates, style locked separately by Denis).
This changes how screens are BUILT, not just how they look. Rules:

### The layer stack (match screen and roster screen)

1. PLATE (bottom): a full-screen painted background image. For the match
   screen: a bare wooden tabletop, evenly/softly lit, NOTHING baked into it
   that changes, moves, or gets tapped. Possibly one plate variant per tier.
2. OPPONENT SPRITE: the patron/boss as its own transparent PNG positioned at
   the top edge of the table (head, hooves/hands visible over the table lip).
   Swapped per match. Never baked into the plate.
3. OBJECT SPRITES: candle (animated glow: CSS pulse or 2-frame swap), beer
   mug, coin pile (the pot: scales/steps with pot size), parchment speech
   scrap. Each a separate transparent PNG, absolutely positioned.
4. DICE: keep the existing programmatic dice renderer (PIP_LAYOUTS etc.) but
   restyle it to match the painted look (colour, corner rounding, pip style
   per material). Programmatic beats sprite sheets here: crisp at any size,
   materials already data-driven.
5. UI CHROME + TEXT (top): buttons, score band, tags are textless painted
   blanks (wood plank button, parchment tag, dark wood band) as images or
   9-slice, with ALL text rendered live in HTML/CSS on top. No text is ever
   baked into any image asset. Buttons get pressed/disabled states via CSS
   on the same blank.

### Rules of thumb

- If it changes, moves, or gets tapped: separate sprite or HTML. If it never
  changes: it can live in the plate.
- Denis maintains the asset folder locally; expect files for plate(s),
  opponent sprites, candle, mug, coins, chrome blanks. Agree a naming scheme
  with him before wiring (suggest: plate_match_t0.png, char_grog.png,
  obj_candle_a.png, ui_btn_plank.png, ui_tag_parchment.png, ui_band_dark.png).
- The existing DOM zone system (hud / opp / dice / controls) survives; this
  swaps what fills the zones. Audit absolute positions against the plate's
  composition on tall and short viewports; the plate must be designed with
  safe zones for the HUD band and the button row.
- Roster screen follows the same logic: tavern room plate, patron portrait
  sprites in frame positions, HTML tags and prices, chalkboard is a blank
  with HTML chalk text.

## Cross-cutting

- Save migration: every S.run shape change goes through _getS() detection.
  A corrupted or ambiguous mid-run save should degrade to a fresh night at the
  current tier, never a crash, never a lost run.
- The existing comments culture in this file is good (player-feedback notes,
  rationale). Continue it: every non-obvious rule from this brief gets a short
  comment naming the degenerate play it prevents.
- Copy/tone: all new UI text in the existing tavern register, short, no
  exclamation-mark spam. Sentence case in body copy, caps for labels, matching
  what's there.
- Test checklist before calling it done:
  1. Fresh run: roster renders, buy-in deducts, seat consumes on loss.
  2. Lose enough seats to fail a night: heart lost, LAST ORDERS overlay,
     roster re-rolls, points reset.
  3. Reach pointsNeeded with seats remaining: boss button live, leftover seats
     still playable, no new seats appear after these are spent.
  4. Turn cap reached both ways (player ahead, NPC ahead), tie path, last-licks
     interaction.
  5. Renown migration: save with 160+ renown loads with extraSeat and both base
     slots, nothing lost.
  6. Old-format save (no night state) loads into a valid night.
  7. Sim runs headless and prints the acceptance table.
