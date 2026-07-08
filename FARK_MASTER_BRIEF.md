# FARK — MASTER REWRITE BRIEF

For: Claude Code, one-shot handoff. This is the authoritative design doc.
Where it conflicts with FARK_LOOP_BRIEF.md or FARK_UI_ADDENDUM.md, THIS DOC
WINS. Two sections of the addendum remain fully valid and are referenced,
not repeated: the dice renderer spec (port dice_playground21.html verbatim)
and the motion/animation rules. Everything else below is the game.

## Design laws (apply to every system, every card, every screen)

1. THE BET LAW. Every card, rule, and tell must be a wager: it opens a new
   gamble, triggers on an uncertain event (yours or the opponent's), or
   bends risk in BOTH directions. Pure passive advantage is banned. If an
   effect removes risk without adding a new one, it does not ship.
2. FELT NUMBERS. Any numeric effect must move at least ~10% of a match
   target or it does not exist. No +50s.
3. TAVERN LANGUAGE. No player-facing "points/marks/seats/tiers/slots".
   Tooltips read like bar bets (see card list, write in that register).
   Numerals only for die faces and point values; counts in words.
4. NO BAKED TEXT in image assets. All copy is HTML.
5. Colour belongs to FAMILIES exclusively. Trait seals are single-colour
   wax (dark red), distinguished by symbol only. Tier is border metal
   (tin/silver/gold) plus a roman numeral.

## 1. RUN STRUCTURE

- A run is 8 nights, one boss per night. 3 hearts (the innkeep's
  patience); 0 hearts = BARRED = run over.
- pointsNeeded per night: [2,2,2,3,3,3,3,4]. Seats per night =
  pointsNeeded + 2. Buy-in per seat by night: [10,15,25,35,50,65,80,100],
  clamped to available gold (broke players sit free; never soft-lock).
- Night flow: roster of patrons generated at night start (persist across
  restarts). Playing a seat consumes it win or lose. Patron win: +1 chalk
  circle, pot payout (buy-in back + reward: 15 + night*10 gold), card
  draft. Loss: buy-in gone, patron GONE HOME, no circle.
- Chalkboard beside the boss: "[BOSS] PLAYS WINNERS" + N circles; beating
  a patron chalks their face in (3 stepped frames). All filled: "[BOSS]
  WILL PLAY YOU NOW", boss-ready restage (see screens). Remaining seats
  stay playable (bounded greed).
- All seats spent, board unfilled: LAST ORDERS. Lose a heart, roster
  re-rolls, circles reset.
- Boss win: heart restored (cap 3), boss gold, SPOILS choice (section 6),
  next night. Boss loss: heart lost, boss remains, retry with whatever
  seats remain.
- One random seat per night carries the handicap offer (wax-sealed frame,
  black wax + ribbon, visually distinct from trait seals): accept its
  handicap to earn 2 circles and double gold; a handicap loss removes a
  circle (floor 0).
- Match format: first to target wins, OR highest total at the turn cap
  (patron 8 banked turns each, boss 10). Trailing player always gets the
  final answer turn. Exact tie at cap: sudden-death turns. Turn counter
  always visible (TURN 5 / 8).
- Targets: compress the current curve so the sim (section 9) hits median
  5-7 banked turns per side at intended gear. Expect roughly 2500-4000
  early, ~12000-16000 patron / ~18000-20000 boss at night 8; sim decides.

## 2. DICE

Six loadout slots. Two classes:

MUNDANE (plain stats, cheap, no card family):
- Bone: standard 1-6. Starter.
- Iron: no 3, extra 5. 100g.
- Flint: leans 4s and high. 150g.
- Lead: extra 1, no 6. 200g.

FAMILY DICE (each anchors a card family, carries its colour):
- Amber (warm gold), 180g: triples using it +200.
- Jade (green), 750g: 6s wild for triples, and attach to a triple to make
  four-of-a-kind (doubles the score).
- Jade II (gold-green), 1800g: as Jade, plus 6s fill any gap in a
  straight. Same silhouette as Jade, richer material. Tier visuals must be
  glance-readable.
- Silver (white), 580g: saves you from one bust per match.
- Obsidian (black, ember cracks), 500g: 6% per roll to shatter (lost for
  the match), shatter scores +1000. Cracked texture state on shatter.
- Starstone (night blue), 700g: every bank +500.
- Vagabond (red gem), 700g: long-press drag to reorder in the row.

REMOVE from shop/drops entirely: Brass, Crystal (identities folded into
families), Ruby, Jade III (already dep). Keep legacy-save fallbacks
functional; migration converts owned Brass/Crystal to gold refunds at
purchase price.

Shop stock ROTATES per night (partial pool + SOLD slots) so no family is
guaranteed available on demand. This is a primary anti-samey lever; do not
make stock deterministic.

RELIC DICE: 8 unique boss dice, section 6. LUCKY DICE: every generated
patron carries one visually marked, named die slightly better than its
material baseline (e.g. bone with an extra 5, named "Old Bess" in the peek
card). Lucky dice are what For Keeps and grudges are about.

## 3. CARD FAMILIES

Six families. Player holds THREE card slots (no renown gating, no slot 0)
plus one SLEEVE slot (tells only, section 7). Cards are equipment, not a
hand: all visible at the table edge, colour-chunked.

Every family: one marquee active, one nerdy passive (max one numbers card
per family), one chunky effect, one spicy/interactive. Tiers I/II/III.
NPCs draw from the same pool (section 5).

Full list, in tooltip register (ship this copy):

JADE - rewrite fate, at a price (green)
- Transmute (active): Tap a rolled die and turn it into any face you want.
  Once per match. (II: twice. III: three times.)
- Fool's Gold (active): Rolled nothing? Reroll everything. But if the
  second roll fails too, the bust burns your turn AND the same amount from
  your banked points. Once per match. (II: twice. III: three times.)
- Cultivate (passive): Each time a jade wild fires, that die grows: +50 to
  its scores for the rest of the match. Stacks.
- Bloom (passive, numbers): Straights and triples that use a jade die
  score +300. (II: +600. III: +1000.)

AMBER - trap everything, even them (warm gold)
- Preserve (active): Trap one scoring die in amber at the end of your
  turn. It is still there next turn, already kept and scored. Once per
  match. (II: twice. III: it cracks free with +100.)
- Honeytrap (active): Tap a kept pair. Your next roll pulls one die into
  matching it. Guaranteed triple. Once per match. (II: twice. III:
  stretches kept triples into four-of-a-kinds.)
- Tar Pit (active, targets opponent): Trap one of the opponent's dice for
  their next turn. They roll five. Once per match. (II: it holds for two
  turns. III: trap two dice for one turn.)
- Slow Cook (passive, numbers): Every roll past your second adds +150 to
  your turn total. Bust and it all spills. (II: +250. III: +400.)

SILVER - defense is an attack (white)
- Ward (active-armed): A visible shield over your dice. Absorbs your next
  bust, or the opponent's next trick. (II: two charges. III: absorbed
  tricks rebound: the attacker loses 300.)
- Retort (passive): When you bust or are hit by an opponent card, they
  lose 400. (II: 700. III: 1000.)
- Reprisal (passive): While trailing by 1000 or more, your banks TAKE
  their points instead of just gaining. 25% of each bank is stolen from
  them. (II: 40%. III: 60%.)
- Insurance (passive, numbers): When you bust, keep a quarter of the
  points you would have lost. (II: nearly half. III: most of them.)

OBSIDIAN - burn it all (black/ember)
- Powder Keg (active): Blow up your whole roll: every die rerolls, kept
  ones included. Once per match. (II: twice. III: detonations that land a
  triple score double.)
- Double or Nothing (active): After banking, flip for it: double the bank
  or lose half. (II: lose a third. III: lose a quarter.)
- Sacrifice (active): Shatter one of your own dice, gone for the match,
  for +800 right now. (II: +1200. III: +2000.)
- Short Fuse (passive): From your third roll each turn, everything scores
  double. But bust after that and the fire spreads to your banked points
  (burn = the doubled turn total). Tray smolders from roll three: the
  warning state must be unmissable.

STARSTONE - omens: bet on what happens next (night blue)
- Encore (active): Do not like a roll? Roll it again. Once per match.
  (II: twice. III: three times.)
- Stargazer (active): Peek at your next roll (ghost dice) before deciding
  to take it. Once per match. (II: twice. III: three times.)
- Ill Omen (active, targets opponent): At your turn's end, declare they
  will bust this turn. Right: take 800 from them. Wrong: they gain 400.
  (II: 1200/400. III: 1600/300.)
- Falling Star (passive): Bank 1500 or more in a single turn and take
  another full turn immediately, opponent skipped. (II: 1200. III: 1000.)

VAGABOND - cheat politely (red)
- Sleight (active, targets opponent): Force your opponent to reroll
  everything they just rolled. Once per match. (II: twice. III: also once
  whenever the table rule triggers.)
- Pickpocket (passive): Every time you bank, lift 100 of the opponent's
  unbanked points. (II: 200. III: 300.)
- Tamper (active, pre-match): Break one of the opponent's cards for the
  night. (II: also usable once mid-match. III: breaking it steals 300.)
  Requires opponent cards visible at the table: build that UI.
- Positional suite (passives, migrate from current CARDS with new
  numbers): Vanguard: a scorer in the FIRST spot scores +200/+350/+500.
  Anchor: same for the LAST spot. Bookends: scorers in BOTH end spots,
  +400/+700/+1200. Marked spots glow BEFORE the roll: the player aims.
- For Keeps (unique, no tiers, drafts from night 4+ only): Play as you sit
  down: this match is for dice. Win, take one of theirs (your pick,
  including their lucky die). Lose, they take one of yours (THEIR pick).
  Patron tables only: the house does not bet its dice.

CUT (do not migrate): Ballast, Sure Thing, Heavy Hand, Counterweight,
Anvil, Dead Weight, Gilding, Hoard, Perfect Set, Collector, Hot Streak,
Second Wind, Rally, Alchemy. The old bespoke CARDS pool is replaced
wholesale except the positional three and boss content per section 6.

## 4. CARD ACQUISITION AND PROGRESSION LOCKS

- Run start: draft 1 of 3 (tier I only) before the first seat.
- Every patron win: draft 1 of 3, or decline for gold (5 + night*5).
  Weighting: 60% families the player owns dice or cards in, 40% outside.
- Never offer a same-tier duplicate of an owned card: it appears as that
  card's next-tier upgrade instead, and taking it upgrades in place.
- Tier locks: tier II may appear raw from night 3. Tier III is NEVER
  offered raw, only reachable by upgrading an owned II.
- Boss wins grant no draft (spoils instead).
- Loadout between matches: swap freely; sell any card to the innkeep for
  15g.
- Progression is locked three ways, all in-run: gold paces dice, night
  number paces card tiers, boss order paces spoils. No meta-power gates.

## 5. OPPONENTS: PERSONAS x FAMILIES

- Trait = temperament (WHEN they bank/push). Family = tools (WHAT they can
  do). Keep both; they are orthogonal scouting reads.
- Trait seals: single-colour dark red wax, symbol only. Mapping: ones =
  STEADY (anchor), triples = BULLISH (fist), straights = ORDERLY (ladder),
  aggro = RECKLESS (crossed daggers), hoard = GREEDY (coin pouch), combo =
  CUNNING (mask).
- Patron loadout generation: trait biases family (aggro->obsidian,
  hoard->amber, combo->vagabond/starstone, straights->jade, ones->silver,
  triples->amber/jade), with off-diagonal patrons appearing occasionally
  from night 3+ as curveballs. Patron card count by night: 0-1 early, up
  to 3 late; card tiers follow the same night locks as the player.
- NPC card AI: one policy table, persona x verb. Tendencies to implement:
  RECKLESS detonates early and flips Double or Nothing when behind;
  GREEDY Tar-Pits when the player holds a kept pair, hoards Preserve;
  CUNNING sits on Sleight until the player's biggest visible turn, plays
  Tamper pre-match against the player's highest-tier card; STEADY holds
  Ward and Insurance, plays Ill Omen against RECKLESS-looking player
  behaviour (many rolls per turn); ORDERLY uses Encore/Stargazer to fish
  straights; BULLISH Honeytraps toward triples. Bosses use the same table
  with their family's full pool plus their tell natively.
- Opponent cards are VISIBLE at their table edge (required by Tamper and
  by scouting). Their actives firing must be readable events (parchment
  callout + the ledger line).
- NPC names get period titles by night band: nights 1-2 Goodman/Goodwife/
  Goody/Gaffer/Gammer/Widow/occupational ("Slink the Tanner"); 3-5
  Master/Mistress/Dame; 6-8 Sir/Lady/Squire/Father/His Grace. One const,
  prefixed by the generator.
- Grudges: if the player took a boss's relic die (or a patron archetype's
  lucky die via For Keeps) and faces them again, they run a grudge
  persona: meaner dialogue pool, +1 aggression tier. Cheap, memorable.

## 6. BOSSES, TELLS, SPOILS, RELICS

Boss family mapping (drives relic + card pool):
GROG obsidian, MABEL amber, FINNICK vagabond, CORVUS starstone, BRUTUS
silver, ALDRIC jade, WHISPER vagabond, AMBROSE amber.

TELLS v2 (mostly as existing, changes marked):
- GROG, LAST CALL: banks under 500 do not count. Unchanged.
- MABEL, STEEPED: each extra roll adds 100 to the bank, bust spills it
  all. Unchanged.
- FINNICK, PICKPOCKET: each roll, 30% one die is palmed for the turn.
  Clarify: palmed dice always return; never permanent.
- CORVUS, IN ARREARS: player-side unchanged (5g per roll, win it back).
  SLEEVED side rewritten: each of their rolls adds 5g to the pot you win.
- BRUTUS, DRILL ORDER: three rolls a turn, hot dice roll free. Unchanged.
- ALDRIC, CONFESSION: REWORKED. Rotating seal: one card locked at a time,
  moving each turn. (Old per-turn stacking seal is dead: it empties a
  3-slot loadout by turn three.)
- WHISPER, COUNTERFEIT COIN: cursed dice bank at half. Unchanged.
- AMBROSE, THE RECKONING: match the opponent's last bank or score
  nothing. Unchanged.

SPOILS: on a boss win, choose exactly ONE from his table, final, no
buyback: (a) his RELIC DIE, (b) his TELL (goes to the shelf), (c) his
PURSE (gold ~ a fancy die for that tier band, sim-tuned 500-700+).
His tell also displays on the shelf as claimed only if chosen; the die
and purse do not grant the tell. Night 8 (Ambrose) pays out in renown:
title jump + his die as a cosmetic trophy on the player's shelf.

RELIC DICE (unique, family-tagged, count for all per-family scaling;
first-pass stats, all sim-flagged):
- Grog's Tooth (obsidian): 10% shatter, +1500 on shatter, no 2 face.
- Mabel's Thimble (amber): triples using it +400.
- Finnick's Palm (vagabond): reorders like Vagabond; kept dice adjacent
  to it score +100.
- Corvus's Ledger (starstone): +300 per bank and +5g per bank.
- Brutus's Shield (silver): two bust saves per match.
- Aldric's Square (jade): 6s wild for triples AND straights.
- Whisper's Fang (vagabond): its scores are doubled; bust while holding
  it kept and lose an extra 200.
- Ambrose's Weight (amber): any bank that beats your previous bank +500.

## 7. THE SLEEVE (claimed tells)

- Claimed tells live on the shelf (loadout screen). Before any match the
  player may sleeve exactly ONE. Optional; empty until first boss kill.
- A sleeved tell is a SYMMETRIC house rule for the whole match: binds both
  sides, constant, no charges, no activation. The edge is the asymmetry
  between the rule and the two builds; sleeving is a wager on reading the
  table.
- Boss fights: the boss is the house. His tell binds only the player; the
  player's sleeved tell binds both. Boss matches can run two rules.
- UI: sleeve slot at loadout framed in boss-dark-wood (not family
  colours); active rules show as badges on the match HUD (reuse the tell
  badge component; two badges max).
- Balance lever if the sim shows one tell auto-sleeved everywhere
  (RECKONING is the suspect): add a small gold cost per sleeve. Never
  convert tells to charges; rules stay rules.
- NPC banking/rolling policy must respect any active rule from either
  side (min-bank, roll caps, curses, etc.).

## 8. RENOWN v2 AND FEATS

- Renown is an INVISIBLE counter. No panel, no perks, no power. Delete
  the perk ladder entirely; 3 card slots and full seats are baseline.
- Surfaces exactly two ways:
  1. TITLES: the player's honorific climbs the same period ladder as
     NPCs (nobody -> Goodman/Goodwife -> Master/Mistress -> Sir/Dame ->
     a Name). NPCs address the player by current title with per-persona
     flavour lines.
  2. CUSTOMIZATION SHELF: thresholds unlock cosmetics only: dice skins,
     a table mat, the player's tankard visible at their table edge,
     warmer innkeep greetings, and boss trophies (night-8 die). Shelf
     lives in the loadout screen.
- FEATS remain the renown source, retuned to family stunts that advertise
  builds (examples to implement: win a night fielding three obsidian
  dice; win a match without banking under 800; take a relic with For
  Keeps... no, For Keeps is patron-only: steal three lucky dice in one
  run; win under your own sleeved RECKONING; detonate Powder Keg into a
  triple). Old stat-grind feats migrate or die; feat completion toasts on
  the victory overlay.
- Migration: existing renown totals convert to title progress; players
  with old perk unlocks lose nothing functional (slots are free now,
  extra-seat perk retired; grant a cosmetic as compensation).

## 9. BALANCE SIM (extend FARK_LOOP_BRIEF P6)

Same harness requirements (reuse real scoring and NPC policy, headless,
debug-triggered). Additional acceptance work for this rewrite:
- Card sim coverage for the deterministic passives and the flagged set:
  Double or Nothing, Short Fuse burn, Falling Star thresholds, Preserve
  III, Honeytrap+family stacking, Fool's Gold burn, Reprisal, Ill Omen
  numbers vs real persona bust rates, cross-family bust-immunity stacks
  (Silver die + Ward + Insurance), For Keeps economy impact, every relic,
  RECKONING sleeve dominance.
- Targets: patron win rate 60-70% at intended gear, boss 45-55%, median
  match 5-7 banked turns per side inside the caps. Tune TARGETS down
  before inflating player scoring.
- Buy-ins, patron gold, boss purses, dice prices, sell value, decline-
  gold: one economy pass so a family die is purchasable roughly every 1-2
  nights early, every night mid-game.

## 10. SCREENS (full inventory, deltas from the addendum marked NEW)

1. Title/menu: continue, new run, settings. Player title shown.
2. THE ROOM (per addendum: frames on tavern plate, chalkboard, peek flow,
   GONE HOME, boss-ready restage where empty frames come down, boss goes
   big, remaining patrons demote to a compact row with stake tags).
   NEW: patron frames show family colour via their dice chips and a lucky
   die marker.
3. Peek card: portrait, name+title, trait seal, dice chips (family
   colours, lucky die named), stake, pot, target, their visible cards,
   SIT DOWN. NEW: For Keeps banner state when played.
4. Boss peek: dark wood variant, tell written out, heart warning,
   NEW: his relic die and cards visible.
5. Match: HUD (scores, target, TURN X/N, up to two rule badges), opponent
   at table edge with THEIR cards and dice visible, pot pile, player dice
   row (v21 renderer), THREE card slots + sleeve badge, kept tray, ROLL/
   BANK. NEW: family actives are tappable cards; opponent active
   callouts; Ward shimmer layer; Short Fuse smolder state; Preserve amber
   casing on a die; positional glow spots; ghost dice for Stargazer.
6. Victory overlay: pot payout, draft (3 cards or decline-gold, upgrades
   shown as such), feat toasts.
7. Return-to-room chalking beat (stepped chalk frames).
8. Defeat overlay: exit line, coins away, BACK TO THE ROOM.
9. NEW SPOILS overlay (boss win): his table with three objects: relic
   die, tell scroll, purse. Pick one, final. The centrepiece reward
   screen; make it the best-looking overlay in the game.
10. LAST ORDERS overlay (as specced).
11. Dice store: rotating stock, SOLD tags, family dice visually magic vs
    mundane, tier variants glance-readable.
12. Innkeep's Book panel (unchanged mechanics).
13. Loadout: six dice (reorder), THREE card slots, NEW sleeve slot +
    shelf (claimed tells, trophies, cosmetics), card sell, opponent-
    aware sleeving happens here.
14. BARRED (game over): run summary, title/renown earned.
15. Run won (night 8): celebration, trophy to shelf, summary.
16. Settings: rival speed etc.

## 11. MIGRATION, TESTS, BUILD ORDER

- Save migration through _getS(): old runs land on a valid night with
  converted loadouts (Brass/Crystal refunds, old cards -> nearest family
  equivalent or sell value, renown -> title). Never crash, never lose a
  run silently.
- Test checklist additions to the loop brief's list: draft weighting and
  duplicate-upgrade path; tier locks by night; spoils choice finality;
  sleeve symmetric application both sides; boss double-rule fight;
  Tamper vs Confession coexistence; For Keeps win and loss paths
  including losing a relic and the flaunt/reclaim seat; grudge trigger;
  NPC actives firing per policy table; economy pass output.
- Build order: (1) families data + acquisition + 3-slot loadout, old
  cards migrated; (2) night/seat loop from the loop brief if not already
  landed; (3) tells v2 + sleeve symmetric engine; (4) spoils + relics +
  shelf; (5) NPC families/AI policy + visible opponent cards; (6) For
  Keeps + lucky dice + grudges; (7) renown v2/titles/feats; (8) sim
  extension and economy pass; (9) juice per the addendum's motion rules.
