# fark_proto.html — mechanics prototype ledger

Vehicle for the MASTER_PLAN phases. Save key `gambit4_proto`. index.html,
fark_nights.html, and _mockups untouched. New-system UI = bare black/white,
color accents only (family colours), system fonts.

## P0 — audit + scaffolding (done)

Brief §1 vs code:
- seats = pointsNeeded+2 ✓ (_nightSeats; extraSeat perk dies in P7)
- handicap: win=2 circles ✓ double gold ✓ loss rubs a circle ✓
- cap: highest tally ends ✓, dead-even → extra round ✓
- ADDED: trailing player final answer turn at cap (_handBackOrCap +
  endPTurn short-circuit, G._finalAnswerUsed). Sim harness cap loop does
  NOT model final answer yet — align in P8.

Old card system map (for P1 cutover):
- const CARDS at ~9348, 116 ids. Consumers: pCards ~204 refs, oCards ~122,
  activeCard ~88. Effect code is inline throughout scoring/turn/opp AI.
- Engine seams (line refs at P0): scoreRoll 10070, startPTurn 12456,
  endPTurn 14560, runOppTurn 14736, finOpp 15508, endMatch 16031,
  launchSeat 21711, generatePatron 9256, generateOppCards 19318.
- P1 strategy: build EV engine + FAM_CARDS beside old system; cut over
  offer/generation first, then delete old effect sites in one sweep;
  keep positional trio (vanguard/anchor/bookends) migrating into Vagabond.

## Decisions

- Proto keeps existing Room/match UI as scaffolding; new systems render
  as plain overlays/panels until the loop is proven.

## P1a — family card engine (done)

- Engine before scoreRoll: FAMILIES, FAM_CARDS (27 defs, brief copy
  verbatim), CFX effect hooks (renamed from FX — old particle system owns
  that name), famFire event bus, famGive() dev helper, famRow B&W chips.
- Seams wired: match init (G.pF/G.oF), startPTurn, _afterRollImpl,
  handleBank (bankBonus delta + bank event), doBust, finOpp opp bank,
  endPTurn (Falling Star extra turn).
- Live effects (unit-tested, 10/10 pass): slow_cook, insurance, retort
  (bust half), reprisal, pickpocket, falling_star, encore, double_or_nothing
  (armed-style: arm during turn, next bank flips — flow never pauses).
- Interpretations flagged: pickpocket lifts from opp TOTAL (brief says
  unbanked, which is empty at player bank time); sacrifice will bank its
  points (safe), not add to turn.
- Sim parity holds (40%/5 vs 45%/5 baseline, n=60 noise).

NEXT (P1b): draft v2 + run-start draft, loadout equip/sell panel,
remaining actives (transmute, powder_keg, sacrifice, ward, stargazer,
ill_omen, sleight, tar_pit, preserve, honeytrap, fools_gold), scoring-
internal passives (bloom, short_fuse, positional trio), then old-pool
offer cutover.

## P1b — old cards OFF, full family set live (done)

- Old pool retired: effectiveCards()->[], match init pCards=[], 
  generateOppCards()->[] (NPC cards return in P5). ~330 old effect sites
  now inert; physical deletion deferred (dead code, no behavior).
- Old rarity draft + boss signature draft replaced. Patron win -> greybox
  family draft (3 offers + DECLINE 5+night*5g). Boss win -> no draft
  (spoils in P4). Run start -> forced 1-of-3 tier-I draft overlay.
- Draft rules verified live: duplicate->upgrade-in-place (transmute I->II
  in play test), tier II raw only night 3+, III never raw, 60/40 family
  weighting (measured 218 vs ~28 per family).
- 24/27 cards live. Not live: cultivate (needs jade wilds, P2), tamper
  (needs visible opp cards, P5), for_keeps (P6).
- Greybox UI: famRow chips in match (tap actives; transmute uses prompt()
  for die+face), CARDS button on Room -> equip/satchel/sell panel,
  run-draft + win-draft overlays. All monochrome + family colour stripe.
- Interpretations: sleight/tar_pit/ill_omen are armed on your turn,
  resolve on the rival's next turn. Preserve stores a kept 1 or 5.
  Stargazer prints the omen as text (ghost dice later).

TEST CHECKLIST P1 (all pass): run draft, seat launch, famRow render,
slow-cook/insurance/retort/reprisal/pickpocket/falling-star/DoN unit
tests, win draft, upgrade path, decline gold, continue to Room, points
chalk, cap final-answer code path present.

NEXT (P2): dice v2 — mundane four + family dice defs, Brass/Crystal/Ruby
removal + refunds, shop rotation with SOLD slots, lucky dice on patrons,
jade wilds (enables cultivate + bloom fully).

## P2-P8 — full brief implementation, greybox (done)

P2 dice: brief prices; brass/crystal/ruby retired w/ gold refunds at _getS;
  shop rotation per night (55% family availability, min 2, SOLD tags);
  lucky die on every patron (named, bone+extra-5, shown in Room);
  cultivate live (jade growth pays at commit). Greybox DICE STORE +
  LOADOUT (reorder arrows, stash/swap, satchel).
P3 rules: _ruleActive(id,side); sleeve = claimed tell bound to BOTH sides
  (S.run.sleeve; slot in loadout); patron matches: sleeve occupies the
  tell machinery player-side; boss matches run tell+sleeve (two badges in
  famRow). NPC-side enforcement for all 8 tells at their roll/bank seams.
  ALDRIC = rotating single seal on the 3 card slots. CORVUS sleeved side
  feeds +5g/roll into your winning pot. Known gap: player-side sleeve in
  BOSS fights only binds at the flat sites (nested tell-block sites take
  the boss tell) — full dual-rule needs the rules refactor.
P4 spoils: boss win -> pick ONE of relic/tell/purse (final). 8 relics
  wired (tooth shatter 10%/+1500 via generalized shatter, thimble +400
  triples, palm adjacency +100, ledger +300/bank +5g, shield x2 saves,
  square wild straights, fang +200/-200, weight +500 over-previous-bank).
P5 opponents: traits = STEADY/GREEDY/RECKLESS/BULLISH/ORDERLY/CUNNING
  (+symbols); trait->family loadouts by night (0-1 early, 3 late, II from
  n3, III from n6, off-diagonal 15% n3+); boss family pools; NPC cards
  VISIBLE in famRow (THEIRS chips); NPC AI: tar pit after your 800+ bank,
  sleight when trailing 800+, ill omen vs 3+ roll turns, DoN when behind,
  slow-cook/pickpocket/retort/insurance mirrors; Tamper live (breaks their
  best card, III steals 300); period titles Goodman->Sir by night band.
P6 For Keeps: drafts n4+ (25%), arm toggle in Room, patron-only; win =
  pick any of their dice incl the named lucky; loss = they take your best
  (relic>family>mundane); lucky steals seed grudges: that archetype
  returns meaner (agg+0.12, extra card, GRUDGE tag).
P7 renown v2: perk ladder wiped at load (slots/seats baseline); renown
  invisible; player title ladder (nobody/Goodman/Master/Sir/a Name) shown
  in Room header; 5 family feats grant renown w/ toast; cosmetics shelf
  stub + lucky-die trophies in loadout.
P8: targets compressed to brief bands (patron mids 3000->14000 by n8,
  bosses 4000->19000); T0 sim after compression: 51% patron / 5 med
  turns / 34% boss (n=80). Full acceptance pass still owed (boss rates
  low band-wide; economy knobs untouched pending playtest).

Not done (needs your call / later): NPC use of self-dice actives
  (encore/stargazer/preserve/honeytrap for NPCs), night-8 renown-payout
  ceremony, run-won screen, dialogue title address, old-code physical
  deletion sweep.

## P9 gaps closed (done)

- Dual rules for real: every player-side tell site converted to
  _ruleActive(id,'p') — a sleeved rule now binds the player even in boss
  fights (boss tell + sleeve = two live rules both sides). Thresholds/
  maxRolls resolve from _tellById when the boss tell differs.
- NPC self-dice actives: encore/stargazer = they reroll a dead roll
  instead of busting; honeytrap pulls a fresh die to their modal face
  (50% from roll 2); preserve banks 100 into their next turn's start.
- Night 8: Ambrose win pays renown (+150) + trophy, no spoils; RUN WON
  screen (title, gold, renown, feats, trophies, A NEW RUN).
- NPCs greet the player by title at match start.
- Tuning notch: T0 patrons 2400-3200, Grog 3700. Sim T0: 56% patron /
  5 med turns / 44% boss (bands: 60-70 / 45-55; sim plays cardless
  bank300 — real play sits higher, revisit after playtests).
- DEFERRED on purpose: physical deletion of the old card code (~330
  inert sites). Zero behavior now; deleting mid-proto risks breakage for
  no gain. Belongs in the final port to the real UI build.

## P10 — brief update (2026-07-09) implemented (done)

Sealed seat: handicaps deleted (offer machinery inert, _checkRenownPerks
  neutralized — a feat crossing an old threshold was still granting the
  +200g Known Face perk). One seat per night runs ONE random tell,
  symmetric via _ruleActive/_applySeal; player sleeve stacks (two rules).
  Win 2 circles + double gold, loss rubs a circle. Confession excluded
  from the seal pool (no NPC-receiving side).
Tavern cards (parchment #b09a72, no tiers): Double Stakes (arm in Room,
  2x buy-in + 2x pot), The Tab (consumable: +250g now, 400 due when the
  night ends — unpaid = circle rubbed BEFORE the last-orders check, so
  debt can tip the night; PAY IT button on the chalk ledger), Hair of the
  Dog (loss flags S.run._hotdNext, first bank next match x2), Marked
  Table (sealed win pays 3), High Table (target +500 at launch; pot x1.5,
  x2 from GREEDY/BULLISH). Drafts: tavern ~12% of offers, excluded from
  identity weighting; nights 1-2 in-family bias 50/50. Consumable rule:
  famBurn() logs + empties the slot (for_keeps burns at launch, win or
  lose). Tavern cards hidden from the match famRow (run-domain only).
Starter die draft: run start now offers 3 family dice (no jade), free,
  replaces the tier-I card draft. Picked die swaps a bone in the row.
Enchants (innkeep service in the dice store, prompt()-driven greybox):
  amber_cast (face copy), quicksilver (once/turn solo reroll, chip in
  famRow, busts if it kills the roll), tempering (50/50 permanent +100
  per scored die at commit / loses highest face), loaded (face weighted
  2x). One per die ever; S.run.dieEnch/dieEnchInv parallel arrays kept in
  sync through shift/stash/equip/buy/For-Keeps (enchant leaves with a
  stolen die). Pool dice carry .ench; _rollD/_enchRollM used at every
  player roll seam (main, hot dice, powder keg, fool's gold, encore,
  sleight-return, stargazer peek). NPC dice never enchanted.
Telegraph rule: NPC tar pit / sleight / ill omen arm messages are now
  "<name> FINGERS A CARD — ..." in red, one turn before resolving. NPC
  tamper doesn't exist (player-only) — noted, not needed. Patrons cap at
  ONE active card before night 5 (post-grudge filter).
Aldric's Square nerfed to wild_triple (side-grade rule).
Verified live: starter draft, seal roll+bind both sides (badge, 2-rule
  stack with sleeve), sealed win 2 circles/exact double gold, marked
  table 3 circles, DS buy-in x2, HT target +500, FK burn + loss takes
  best die with its enchant, tab take/pay/due paths (incl. tipping into
  LAST ORDERS), quicksilver once-per-turn, tavern offer rate 13%,
  active-cap 0 violations in 60 patrons, no console errors.
