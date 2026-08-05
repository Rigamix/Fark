# FARK — MASTER REWRITE BRIEF

For: Claude Code, one-shot handoff. Where it conflicts with
FARK_LOOP_BRIEF.md or FARK_UI_ADDENDUM.md, THIS DOC WINS. Two sections of
the addendum remain fully valid and are referenced, not repeated: the dice
renderer spec (port dice_playground21.html verbatim) and the motion/
animation rules.

**PRECEDENCE, STATED EXPLICITLY — this was missing entirely until a sim
pass found real, live contradictions caused by its absence.** This is the
FOUNDATIONAL document, not the final word on everything in it. Five later
documents have since superseded specific sections below; on any topic
they cover, THEY WIN, not this file:
- `FARK_ENCHANT_BADGE_REWORK.md` — supersedes this doc's Silver family,
  its original four-enchant menu (Amber Cast/Quicksilver/Tempering/
  Loaded), and four of the eight badge tells (Grog, Whisper, Aldric,
  Corvus). The Silver-die pricing and old enchant list still written
  below are STALE — read that document for the current state, not this
  section.
- `FARK_MATCH_BRIEF.md` — supersedes anything below about match-screen
  layout, card visibility, the telegraph mechanic, and in-match opponent
  presence.
- `FARK_UI_SCREENS_BRIEF.md` — supersedes screen-by-screen UI specifics.
- `FARK_PATRON_LORE.md` — wholly additive (a new system), not a
  supersession, but its Cursed Seat naming supersedes this doc's SEALED
  SEAT language specifically (see the cursed-seat section below, already
  patched).
- `FARK_AUDIT_RESOLUTIONS.md`, `FARK_ANSWERS_2026-07-31.md`, and this
  session's sim-findings patches — supersede anything they directly
  address, including Renown (deleted, see below), the Vanguard/Anchor/
  Bookends collapse, and specific numeric rulings scattered through this
  document that predate later corrections.

**A full line-by-line pass to mark or strike the stale content this
implies (the old enchant menu, old Silver pricing, Renown's mechanical
perks, dead boss-tell UI references, the Bookends feat) is NOT done as
of this note — flagged as real, owed follow-up work, not silently
assumed complete.** Recency wins on overlapping ground going forward;
that rule alone doesn't fix text already sitting here that hasn't been
marked yet.

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
6. SYMMETRY BY DEFAULT. Whatever applies to the player applies to the NPC,
   and whatever applies to the NPC applies to the player. A rule that reads
   differently from the two seats needs a STATED reason — in the code and
   here. **Asymmetry is a design choice, never a silence.**
   THE NAMED EXCEPTION IS `challenge`: the player's terms are frozen when it
   is declared, because it spans a turn; the rival resolves immediately and
   reads them live. That is deliberate and documented. `bust_survive` is the
   second: an unconditional save for the player, a chance-based half-save for
   the boss, kept apart as a personality lever.
   Anything else that diverges is a bug until ruled otherwise. Five were
   found in one night — `challenge`, `ill_omen`, `gain_when_ahead`,
   `gain_pts`/`punish_busts`, `bust_immune_turns` — and not one was a
   decision.

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
- One random seat per night is the CURSED SEAT (renamed from "sealed
  seat" — the shipped visual is a purple smoke effect wreathing the
  patron's portrait, not a worn badge or a wax seal; the name now
  matches what's actually on screen, no wax, no ribbons, no visible
  badge object). Its rule: the match runs under ONE RANDOM TELL from
  the boss tell pool, symmetric, announced on tap of the smoke effect.
  Win it for 2 chalk circles and double gold; lose it and a circle is
  erased (floor 0). This REPLACES the legacy HANDICAPS system entirely
  (delete it); handicaps and tells are now one rules engine with two
  entry points, and the cursed seat teaches tells before the first
  boss. The player's own worn badge may stack on top (two rules max, same
  badge limit as boss fights).
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
plus the BADGE CASE (badges, section 7). Cards are equipment, not a
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
- Vanguard (passive; COLLAPSES the old Vanguard/Anchor/Bookends trio
  into one card whose tiers expand WHERE it applies): I: a scorer in
  the FIRST spot scores +200. II: both END spots live, +350 each.
  III: full bookends — when BOTH end spots score, +1200 total.
  Marked spots glow BEFORE the roll: the player aims. Vagabond is
  back to four draftable cards like every family; legacy Anchor/
  Bookends cards migrate to Vanguard at the same tier.
- For Keeps (CONSUMABLE, no tiers, drafts from night 4+ only): Play as
  you sit down: this match is for dice. Win, take one of theirs (your
  pick, including their lucky die). Lose, they take one of yours (THEIR
  pick). Patron tables only. The card burns on use, win or lose.

CONSUMABLE RULE: family cards never burn EXCEPT explicitly marked
consumables; tavern cards split into standing and consumable per their
copy. A burned card visibly crumples/is tossed to the innkeep (a slot
silently emptying reads as a bug) and leaves the slot empty until the
next draft. Debts and escrows outlive their cards: a chalk LEDGER strip
on the bar in the Room tracks them (e.g. "OWED 400 - LOCKBOX 220").
Loss-reward cap: at most ONE shipped tavern card may reward losing.

ENCHANTS (innkeep services, NOT cards): at the bar, pay gold to
permanently transform one die. This is the deliberate late-run gold sink.
Rules: one enchant per die, ever; enchants travel with the die (For Keeps
can steal your work); an enchant may NEVER replicate a purchasable die's
power (no wilds, no bank bonuses); every enchant must be a transformation
you can point at (a new face, a new behavior, a new mark - never a quiet
+X); each enchant is a small overlay layer composable on any die material
(art: 4-5 overlay sets readable at 42px, including on obsidian black).
First-pass menu, prices sim-tuned:
- Amber Cast (~200g): trap one face in amber and replace another of its
  faces with the copy.
- Quicksilver (~250g): coat a die; once per turn you may reroll it alone,
  free.
- Tempering (~150g): hold a die to the fire. Half the time it hardens
  (+100 to all its scores, for good), half the time it cracks and loses
  its highest face.
- Loaded (~400g): shave a die; pick a face, it rolls that face twice as
  often. LOUDEST sim flag in the game.
(Graft and Constellation from earlier drafts are CUT: one replicated
Jade, one failed the pointable-transformation rule.)

CUT (do not migrate): Ballast, Sure Thing, Heavy Hand, Counterweight,
Anvil, Dead Weight, Gilding, Hoard, Perfect Set, Collector, Hot Streak,
Second Wind, Rally, Alchemy. The old bespoke CARDS pool is replaced
wholesale except the positional three and boss content per section 6.

TAVERN CARDS (neutral, parchment-brown framing, NO tiers, max pool of
five ever). Their domain is the RUN (gold, seats, pots, the night), never
the dice table; they add zero in-match tracking. They compete for the
same three card slots. Ship this copy:
- Double Stakes: Before sitting down, double the buy-in AND the pot.
- The Tab: Borrow 250 gold from the innkeep right now. Owe 400 by last
  orders, or it costs a chalk circle.
- Hair of the Dog: Lose a match, and your first bank next match is
  doubled.
- Cursed Table: The cursed seat pays THREE circles instead of two.
- High Table: When you sit down, raise the match target by 500 for both
  sides. Win: the pot pays half again more, and GREEDY or BULLISH patrons
  pay double.
Sim flags: The Tab (forcing-function bend), High Table (must not push
patron matches past the 8-turn cap into cap-decision territory). If any
tavern card lets players farm around LAST ORDERS, it dies.

## 4. CARD ACQUISITION AND PROGRESSION LOCKS

- Run start: STARTER DIE DRAFT, not a card draft. The innkeep offers three
  family dice (randomized from Amber, Silver, Obsidian, Starstone,
  Vagabond; Jade excluded, it stays the family you save for). Take one,
  free, "with your first ale". This is the run's first screen after the
  title and the identity seed the 60/40 weighting grips from seat one.
  Presentation beat: three dice on the bar, colours doing the talking.
- Every patron win: draft 1 of 3, or decline for gold (5 + night*5).
  Offer sampling is FAMILY-FIRST: pick the family by the 60/40
  owned/outside weighting, THEN a card within that family — never
  uniform over the total card pool, so family sizes can never skew
  draft rates.
  Weighting: 60% families the player owns dice or cards in, 40% outside
  (tavern cards occupy 10-15% of all offers, inside the 40%). Nights 1-2
  run 50/50 so the starter die seeds identity without locking it.
  Known ceiling, accepted: tier III only via upgrading a II means late
  pivots cap at tier II; III is a commitment badge by design.
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
  by scouting). On the MATCH screen they render as colour-coded card
  BACKS (family colour only) that flip face-up when played; full faces
  are readable in the peek panel. TELEGRAPH RULE: every NPC targeted
  active (Sleight, Tar Pit, Ill Omen, Tamper mid-match) telegraphs ONE
  ROLL ahead - the patron visibly fingers the card - so the player gets
  one bank-or-push decision under threat before it fires. No untelegraphed
  targeted actives, ever: agency-less punishment is banned. Patrons carry
  at most ONE active card before night 5; bosses are exempt from the cap
  but not the telegraph.
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
  BADGE-WEARING side rewritten: each of their rolls adds 5g to the pot you win.
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
the OWN THE NIGHT feat — its wall pin is a miniature of his die.
There is no trophy shelf; the feats wall is the only meta surface.

RELIC DICE (unique, family-tagged, count for all per-family scaling;
first-pass stats, all sim-flagged). SIDE-GRADE RULE: relics must be
quirky and storied but tuned BELOW same-band shop dice in raw power -
never strictly best - or they kill the late shop and make the purse
spoil a joke. Aldric's Square is the known offender (near-free Jade II):
its wilds are capped at triples-only until the sim proves otherwise. The
sim tracks SHOP PURCHASE RATE PER NIGHT as a health metric; if night 6+
purchases approach zero, relics are overtuned.
- Grog's Tooth (obsidian): 10% shatter, +1500 on shatter, no 2 face.
- Mabel's Thimble (amber): triples using it +400.
- Finnick's Palm (vagabond): reorders like Vagabond; kept dice adjacent
  to it score +100.
- Corvus's Ledger (starstone): +300 per bank and +5g per bank.
- Brutus's Shield (silver): two bust saves per match.
- Aldric's Square (jade): 6s wild for triples only (side-grade rule; sim may relax).
- Whisper's Fang (vagabond): its scores are doubled; bust while holding
  it kept and lose an extra 200.
- Ambrose's Weight (amber): any bank that beats your previous bank +500.

## 7. BADGES (tells made physical) — REPLACES the badge/scroll system

- The whole mechanic in one line: a boss WEARS their tell as a badge;
  beat them to take it; WEAR one badge into a match to invoke its rule;
  lose a match while wearing it and the badge is GONE.
- Badges are the only physical form of tells. There are exactly eight,
  one per boss, worn visibly on the boss in their art and peek. The
  CURSED SEAT's rule is announced by its smoke effect, not by a worn
  badge — the badge system and the cursed-seat system are two separate
  visual languages now, not one. The Tankard (the ninth badge painted
  in the original sheet, "the house's own mark") is RETIRED from this
  role — it is no longer the cursed-seat marker — but the art survives
  as reusable tavern flavor/set-dressing (see FARK_PATRON_LORE.md for
  a proposed use: displayed behind the bar, with its own small piece
  of house folklore, unconnected to any mechanic).
- Wearing: exactly ONE badge per match, chosen at the boss peek or
  loadout (badge case). A worn badge is a SYMMETRIC house rule for the
  whole match: binds both sides, constant, no charges, no activation.
- THE WAGER (bet law compliance the old badge lacked): lose any match
  while wearing a badge and it is lost for the run. A worn badge is
  always a stake, never a free option. A lost badge is GONE — no
  shelf echo, no memorial, no reclaim. Badges exist in exactly one
  place: the badge case (and pinned on their boss until won).
- Boss fights: the boss is the house. His worn badge binds only the
  player; the player's worn badge binds both. Boss matches can run two
  rules. A boss whose badge you already took fights bare (his tell is
  gone with the badge — beating him again yields other spoils).
- Semiotics, locked: WAX SEALS mean patron traits and nothing else.
  BADGES mean rules — worn = in force, in the case = owned. No scrolls,
  no notes, no ribbons, no colour codes; binding direction is stated in
  words on the badge tooltip and by a tiny one-arrow / both-arrows
  glyph.
- Balance lever, UPDATED per run-sim findings: the auto-wear fear is
  dead for every testable tell (STEEPED badge-worn runs at-or-below base -
  symmetric feeds the NPC too). The badge is a marginal edge plus
  flavor, which is the intended shape. Watch DRILL ORDER (the one
  consistently positive badge, +4-5 points) and RECKONING (untestable
  pre-night-8 in sim, flag stays open). If a gold cost per badge is
  ever needed, those two justify it. Never convert tells to charges;
  rules stay rules.
- Engineering note, costed: symmetric tells require the NPC bank/roll
  policy to adapt on the RECEIVING side of all eight rules (LAST CALL
  changes whether they bank, DRILL ORDER when, COUNTERFEIT what a bank is
  worth, etc). Eight policy adaptations, not one table row.
- NPC banking/rolling policy must respect any active rule from either
  side (min-bank, roll caps, curses, etc.).

## 8. FEATS (replaces renown/titles entirely)

- There is NO renown counter, NO title ladder, NO threshold
  cosmetics, and the player's form of address never changes. NPC
  period titles (Goodman/Master/Sir by night band) remain — they are
  worldbuilding for patrons, not player progression.
- FEATS are direct, visible achievements: do the thing, a small
  pinned marker appears on the player's wall (loadout corner) with
  the feat's name on tap. No levels, no tiers, no unlock currency.
  Persistent across runs. A small tally (e.g. 12 / 24) is the only
  meta-progress display in the game. There is NO trophy shelf — any
  "trophy" moment (night-8 win) is expressed as that feat's pin.
- Starter feat list (~24; names final, conditions playtest-tunable;
  each advertises a build or a story):
  FAMILY STUNTS (two per family):
  jade: GREEN THUMB (bank a straight completed by a jade wild),
    FULL BLOOM (Bloom fires three times in one match);
  amber: SLOW BOILED (a single turn of six or more rolls),
    STICKY FINGERS (win a match with Tar Pit active on the opponent
    twice);
  silver: TWICE SAVED (two bust-saves in one match, then win),
    NO CLAIM (win a match holding Insurance without ever busting);
  obsidian: POWDER MONKEY (bank a shatter's +1000),
    THREE TORCHES (win a night fielding three obsidian dice);
  starstone: WISH GRANTED (chain two Falling Star extra turns),
    OMENS TRUE (win the pot on a correct Ill Omen call);
  vagabond: FOR KEEPS (win a dice stake), BOOKKEEPER (Bookends pays
    three times in one match);
  TABLE STORIES (general):
  FIRST BLOOD (first boss badge taken), HIS OWN MEDICINE (beat a
  boss on rematch wearing the badge you took from him), CLEAN NIGHT
  (clear a night with zero seat losses), THE LONG ROAD (win a match
  from 2,000+ behind), DEATH AND TAXES (beat Ambrose), LAST MAN
  SITTING (win a sudden-death turn), HIGH ROLLER (a single bank of
  2,500+), TEETOTALLER (win a match without ever banking under 500),
  SECOND WIND (win the night after LAST ORDERS takes a heart),
  BARE HANDS (beat a boss with all-bone dice), THE COLLECTOR (hold
  four badges at once), OWN THE NIGHT (win the run).
- Design guard: feats must never grant power — the wall is the whole
  reward. If a feat's condition encourages degenerate play in sim or
  playtest, retire the feat, don't tune the game around it.

## 9. BALANCE SIM (extend FARK_LOOP_BRIEF P6)

Same harness requirements (reuse real scoring and NPC policy, headless,
debug-triggered). Additional acceptance work for this rewrite:
- Card sim coverage for the deterministic passives and the flagged set:
  Double or Nothing, Short Fuse burn, Falling Star thresholds, Preserve
  III, Honeytrap+family stacking, Fool's Gold burn, Reprisal, Ill Omen
  numbers vs real persona bust rates, cross-family bust-immunity stacks (run-sim verdict: full silver
   stacking is a TRAP at 4% run wins, not a menace - low priority; the
   real risk is defense-only builds lacking any win condition)
  (Silver die + Ward + Insurance), For Keeps economy impact, every relic,
  RECKONING badge dominance.
- Targets: patron win rate 60-70% at intended gear, boss 45-55%, median
  match 5-7 banked turns per side inside the caps. RUN-level target:
  25-35% full-run wins for a competent build-focused player (run-sim:
  family-builders hit ~60% with partial NPC card coverage; expect
  ~45-55% at symmetric coverage, then tune the last step with hearts or
  late targets). Tune TARGETS down before inflating player scoring.
- Design guard from run-sim finding 7: the skill ceiling lives in
  drafting and build decisions (~45 points of win rate); banking micro
  is compressed (~2 points). This is the intended cosy-with-a-high-
  ceiling shape. Protect draft meaningfulness; never add banking-
  execution punishments to widen skill spread.
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
   row (v21 renderer), THREE card slots + badge badge, kept tray, ROLL/
   BANK. NEW: family actives are tappable cards; opponent active
   callouts; Ward shimmer layer; Short Fuse smolder state; Preserve amber
   casing on a die; positional glow spots; ghost dice for Stargazer.
6. Victory overlay: pot payout, draft (3 cards or decline-gold, upgrades
   shown as such), feat toasts.
7. Return-to-room chalking beat (stepped chalk frames).
8. Defeat overlay: exit line, coins away, BACK TO THE ROOM.
9. NEW SPOILS overlay (boss win): his table with three objects: relic
   die, the boss's BADGE, purse. Pick one, final. The centrepiece reward
   screen; make it the best-looking overlay in the game.
10. LAST ORDERS overlay (as specced).
11. Dice store: rotating stock, SOLD tags, family dice visually magic vs
    mundane, tier variants glance-readable. NEW: enchant service counter
    (menu, price, pick-a-die flow, overlay applied on the spot).
11b. NEW Starter draft panel (run start): three family dice on the bar,
    innkeep line, pick one. Reuses the store bar plate.
11c. NEW Ledger strip in the Room: chalk record of debts/escrows/pawns
    that outlive consumed cards.
12. Innkeep's Book panel (unchanged mechanics).
13. Loadout: six dice (reorder), THREE card slots, NEW badge case +
    shelf (claimed tells, trophies, cosmetics), card sell, opponent-
    aware wearing a badge happens here.
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
  badge symmetric application both sides; boss double-rule fight;
  Tamper vs Confession coexistence; For Keeps win and loss paths
  including losing a relic and the flaunt/reclaim seat; grudge trigger;
  NPC actives firing per policy table; economy pass output.
- Build order: (1) families data + acquisition + 3-slot loadout, old
  cards migrated; (2) night/seat loop from the loop brief if not already
  landed; (3) tells v2 + badge symmetric engine; (4) spoils + relics +
  shelf; (5) NPC families/AI policy + visible opponent cards; (6) For
  Keeps + lucky dice + grudges; (7) renown v2/titles/feats; (8) sim
  extension and economy pass; (9) juice per the addendum's motion rules.
