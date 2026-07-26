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

## P11 — FARK_PROTO_AUDIT.md pass (2026-07-09) (done)

Audit reconciliation notes:
- Part 1.1 (turn cap "not live") was STALE: the cap has been live since P0
  (TURN_CAP_PATRON=8 / BOSS=10, HUD TURN X/N, highest-tally, final answer,
  dead-even extra round). The auditor read the harness comment. Fixed the
  harness instead: _runBalanceSim now DEFAULTS to live caps (patron legs 8,
  boss legs 10; pass turnCap:0 to A/B uncapped) + pctCapEnd/bossPctCapEnd
  metrics; gear snapshots G2/G3 swap retired crystal for silver.
- Part 1.3: HANDICAPS const, _showHandicapSplash, the offer-roll machinery
  and all painted-room reads are physically deleted. Deep G._handicap
  branches remain (always-null, inert) for the final-port sweep.
- Part 1.2/1.4: slot gating deleted (_isSlotUnlocked=true, celebrate block
  gone), RENOWN_PERKS=[] (readers inert), getPouchCapacity()=0, startGold
  grant gone. _getS migrates any legacy equipped cards/pouch to 15g each —
  never a crash, never silent loss.
- Part 2 targets: T4-7 patron bands -> 6100-7500 / 7200-8800 / 7700-9300 /
  8700-10300; bosses -> 9500/10500/11250/12500. Late NPC quality raised:
  brass/crystal out of boss dice + patron pools; agg/minBank up (T4-7);
  STARSTONE PARITY — the +500-per-bank now credits NPC banks too (live
  finOpp + sim), and Aldric/Whisper carry one starstone, Ambrose one,
  T5-7 patron pools can roll it. Root cause of the G3 steamroll was the
  player's uncontested starstone adder (T7 pre-tells: 87% with it, 52%
  without). Post-tune, harness @400 iters, hot policy, G3:
  T5 pw71 mt6 / bw64 bmt8 · T6 pw74 mt7 / bw67 bmt9 · T7 pw67 mt7 cap21 /
  bw65 bmt10 bcap26. Majority target-crossing everywhere; boss ~65
  pre-tells leaves headroom for tells to pull into the 45-55 band. Early
  nights untouched (T0 G0 pw52/bw40, T2 G2 pw62/bw59).
- Part 3.1 economy run-sim: _runEconomySim (debug block) — gold curve,
  rotation luck, purse-1/3 spoils, median purchase policy. First verdict:
  pity 23% (>15% bar) -> PITY RULE ADDED to _shopRollNight (always stocks
  one unowned family die; sim re-verified 0-1%). Economy pass (brief §9):
  patron reward 15+t*10 -> 20+t*12. Final: P(G2 by n3) 51%, P(G3 by n6)
  26%, buys/night 0.5-0.8 (family die every 1-2 nights early, ~every
  night mid — brief bar met), shop health n6+ ~0.7 (relics not overtuned).
  STRUCTURAL FINDING for Denis: G3 by night 6 is a ~1-in-4 outcome for a
  median cardless policy — the gear cliff the audit flagged is economic,
  not target-based. Card power (unsimmed) is the intended filler; re-check
  after harness extension 2.
- DEFERRED (audit fix order 8): harness extensions 2-4 (deterministic card
  EV, RECKONING/STEEPED sleeve dominance, bust-immunity stack, For Keeps
  economy impact).
Verified live: migration (3 old cards -> +45g), no HANDICAPS/_showHandicapSplash
symbols, RENOWN_PERKS empty, pouch 0, slots free, handicap button hidden,
seal rolls, pity fires with 6/7 families owned, sim defaults return rows,
match boots with TURN 1/8 HUD, zero console errors.

## P12 — FARK_RUNSIM_FINDINGS.md pass (2026-07-09) (done)

- Finding 2 (night-3 wall): patron family-dice CAP by night in
  _generatePatronInner — nights 1-4 max 1, nights 5-6 max 2, nights 7-8
  max 3; extras revert to mundane (flint/iron). Lucky die uncapped
  (flavour bone). Verified: measured max over 80 gens = 1/1/2/3 at
  T2/T3/T5/T7. Night-4 patron at G2 gear: pw 49% -> 57%.
- Finding 4: seats = pointsNeeded+3 on nights 1-2 (5 seats), +2 from
  night 3. DELIBERATE DEVIATION from brief §1 (pointsNeeded+2), pending
  Denis's target run-win-rate decision (finding 1, recommended 25-35%).
  One-line revert in _nightSeats if he rules otherwise.
- Audit fixes 4-5 residue: stale "Slot 0: BOSS / fourthSlot perk" comment
  block replaced; SLOT_UNLOCK_TIER now a dead [0,0,0,0] shim with a
  deletion note. (Functional gating was already dead since P11.)
- NOT DONE (theirs/Denis's): target run-win rate is a design decision;
  finding 3 (cowardice dominates — bank-200 beats push) is BY THEIR OWN
  CALL the card layer's acceptance gate — re-test only when card effects
  land in the sim (audit Part 3.2 + agent card policies). Their agents.js
  harness lives in their container, not this repo.

## P13 — brief refresh + harness ext 2 (2026-07-09) (done)

- Brief updated in repo: RUN-LEVEL TARGET DECIDED = 25-35% full-run wins;
  sleeve auto-pick fear closed (watch DRILL ORDER +4-5 and RECKONING);
  silver-stack = trap not menace (low priority); design guard — skill
  lives in drafting (~45pts), banking micro (~2pts) is fine, never widen
  it with execution punishments.
- Harness ext 2 (audit 3.2): deterministic card layer in _runBalanceSim,
  BOTH sides. Modeled: bloom, slow_cook, short_fuse (+burn), insurance,
  retort, reprisal, pickpocket, falling_star (extra turn), double-or-
  nothing (flip when trailing 15%+), encore/stargazer/fool's-gold(+burn)/
  transmute as bust mitigation, ward + silver die as bust saves.
  Unmodeled ids in a loadout are inert. NPC cards: patron fcards as
  generated; bosses get 1-2 family-pool cards by night (bossCardsFor).
  Gear snapshots accept cards:[{id,tier}].
- COWARDICE GATE (_runCowardiceGate, runsim finding 3 acceptance):
  with push-reward cards (slow cook II, short fuse, falling star II) at
  G2, tiers 2-4: bank200=57%, push750=72% -> +15 MARGIN, GATE PASSES.
  The card layer does exactly what it was designed to do; no bank-
  incentive tuning needed.
- Carded acceptance snapshots: G2+2c nights 3-5: pw 58-59 (band),
  bw 53-70. G3+3c nights 6-8: pw 93-95 / bw 95-97 pre-tells — a stacked
  three-card push build steamrolls late matches, consistent with the
  brief's "family-builders ~60% run-wins at partial NPC coverage".
  Per the brief's own sequencing, the LAST tuning step (hearts or late
  targets) waits for symmetric NPC card coverage in the run-level
  harness — NOT tuned here on partial coverage.

## P14 — runsim v2 doc (card/sleeve/actives passes) reconciliation (done)

Their card-layer + sleeve + targeting-actives passes updated two calls I
had already shipped — both REVERTED to follow the newer data:
- Patron family-dice cap (P12) REVERTED: verdict 2 says the night-3 wall
  was card hunger, not gear ("do not change patron generation yet;
  re-measure after NPC cards land"). generatePatron is back to pre-P12.
- Seats+3 nights 1-2 (P12) REVERTED to brief §1 (pointsNeeded+2):
  finding 10 projects the full card layer landing ONE step ABOVE the
  25-35% run-win target — early softening now points the wrong way.
  Tuning (hearts or late targets) waits for live playtest.
- RENOWN_PERKS shim fully purged (their scanner kept flagging it): const
  deleted, 12 reader tokens neutralized, _checkRenownPerks a one-line
  no-op. typeof RENOWN_PERKS === 'undefined' now.
- No action needed on: sleeve verdicts (DRILL ORDER/PICKPOCKET watched,
  auto-sleeve fear dead), tell-spoils affordability, relic uptake
  (side-grade holding), Tamper/Confession coexistence, session length.
- Open flags they carry, noted: ILL OMEN numbers unvalidated (needs
  mid-turn interrupts), RECKONING sleeve untestable pre-night-8,
  bosses' bespoke legacy pools are dead data in this build.
Verified live: seats back to 4 on night 1, patron family dice uncapped
(max 5 seen at T3), match boots TURN 1/8, zero console errors.

## P15 — flow prototype connected (fark_greybox.html spec) (done)

Denis's phone-frame flow prototype is now the proto's live greybox skin,
driven by the real engine. Wireframe kit (.gbx-*) + bottom-sheet/scrim/
modal infra added; screens rebuilt to the spec's grammar (status up top,
primary actions in the thumb band, tap→inspect→act, no naked confirms):
- ROOM (two states): hearts/gold strip, chalk chip → Innkeep's Book
  sheet (schedule/rules/standing), conditional ledger+tavern chips, boss
  door with circle pips ("N more wins") → boss-ready restage: seats
  demote to a compact greed row, the door goes big. Patron tiles carry
  seal (black border) and grudge marks; bnav menu/loadout/shop.
- PEEK SHEET: portrait/trait/dice+lucky, their cards READABLE (brief §5
  peek shows faces), target/buy-in/pot, sealed-seat rule block, For
  Keeps banner, SIT DOWN — launches the real seat.
- BOSS PEEK: tell (binds you only), relic on display, heart warning,
  sleeve equip AT the decision point (famSleeveSet chips), CHALLENGE
  gated ("WIN N MORE SEATS FIRST" when short).
- SHOP: DICE/ENCHANTS tabs; rotation renders as empty pegs ("back
  another night"), unaffordable dimmed-but-inspectable, owned ✓;
  die inspect sheet with faces laid flat + BUY. Enchant flow is
  prompt()-free: service → pick your die → face pickers (amber cast /
  loaded) → confirm modal (permanent) → applied.
- LOADOUT: shelf (trophies/cosmetics/lucky names) top, sleeve chips,
  3 card slots + stash/sell + satchel, dice reorder lowest. famPanelShow
  retired (card mgmt lives here; move/sell re-render loadout).
- STARTER DRAFT: wireframe bar scene, tap die → inspect → TAKE IT.
- MATCH deltas: BANK button swaps to a weighted "BANK TO WIN" when the
  selection would cross the target (bank-to-win class + _selPts
  preview); rule badges are tappable ⓘ (inspect sheet); armed NPC
  targeted actives telegraph on their card chip (⚠ red, lifted).
- DRAFT: tap → inspect sheet → CLAIM (upgrades labeled). SPOILS: tap →
  "Take this? It's final." modal → TAKE / look again.
Not ported (deliberate): phone frame + thumb-zone overlay (dev-tool
chrome), race bar (existing HUD serves), title screen (painted menu
stays). Verified live end-to-end: starter→room→peek→match→win→claim,
boss-ready→challenge→spoils-confirm→take, shop tabs+enchant flow,
loadout, book — zero console errors. Screenshots blocked by the known
preview compositor freeze; DOM-verified.

## P16 — phone shell + audio defaults (done)

- Desktop phone frame: ≥520px viewports wrap the app in a centered
  390x844 #phoneShell (rounded, shadowed, flow-spec chrome). The shell's
  transform makes it the containing block for every position:fixed
  overlay, and body.appendChild is rerouted into it, so sheets/loadout/
  drafts stay framed. Phones (<520px) are untouched — fullscreen PWA.
- Audio OFF by default: _getS stamps S.settings._protoMuted once, zeroing
  music/ambience/sfx. Settings toggles still re-enable. Share build now
  swaps all three mp3 payloads for a silent WAV stub (~5MB smaller).
- Click audit: hit-tested every greybox control (elementFromPoint +
  synthetic MouseEvent) at mobile AND desktop widths — nothing blocked;
  peek opens from a real click event. The reported dead buttons trace to
  the PWA service worker serving a STALE build (unregister + cache wipe
  fixed it) and/or the tool-pane input quirk. If buttons die again:
  DevTools → Application → Service Workers → unregister, or bump ?v=.

## P17 — greybox title / settings / shelf / barred (flow spec 1, 13-15) (done)

Painted menu + gameover fully hidden (CSS, same host trick). New:
- TITLE: FARK logo box (shows earned title), CONTINUE NIGHT X (only when
  a night exists or tier>0), NEW RUN (confirm modal when a run is live),
  bnav: the shelf | settings. Hooked via initMenuScreen.
- SETTINGS overlay: music/ambience/sfx (toggleAudio), haptics/fast rival
  (toggleSetting), innkeep's book, abandon run (confirm modal → BARRED).
- SHELF overlay: trophies, renown keepsakes, title/feats line.
- BARRED/WON on screen-gameover: BARRED + who took the last heart + run
  stats + NEW RUN/title; tier≥8 renders LAST ORDERS RUNG + TO THE SHELF.
Verified: fresh save shows no CONTINUE; one seat in → CONTINUE NIGHT 1;
new-run confirm; starter draft chains from NEW RUN; barred + won states;
painted children computed display:none; zero console errors.

## P18 — Gambit folder housekeeping (done)

Root reorganized (Denis's ask): the Gambit root now holds ONLY the newest
game. fark_proto.html is THE game; index.html (old painted/GitHub build),
menu/match/gauntlet protos, every index_backup_*, gambit_stable_*, old
sims, build scripts and scratch txt files live in _old/. NEW/ (1.9GB art)
untouched. Root checkout moved off main onto local branch `fark`
(= claude/zen-chatterjee-f04c42); main itself untouched and unpushed.
sw.js is now a SELF-DESTRUCT stub: any browser holding the old painted
game's service worker wipes caches, unregisters and reloads — ends the
stale-build gotcha for playtesters. Kept at root: fark_proto/_nights/
_share, briefs + notes, manifest.json, card_visuals.md, art dirs,
_mockups. Denis's uncommitted local edits preserved (char_frames.psd,
pouch.png, Pyre09.png, .claude configs).
NOTE for future sessions: root branch `fark` must be fast-forwarded when
the worktree branch advances (git merge --ff-only), or work from root
directly once this worktree retires.

## P19 — housekeeping 2: minimal root (done)

Root is now: fark_proto.html + manifest.json + sw.js and four folders —
NEW/ (Denis's art, untouched), assets/ (Audio, Card_ART, Characters_ART,
Environment_ART, Fonts, Match_Art, Menu_Art, Night_Art, _mockups), docs/
(all briefs + notes + README + card_visuals), _old/ (everything legacy,
incl. fark_nights.html and the last share build; see _old/README.txt).
fark_proto.html asset references rewritten to assets/<dir>/ (63 refs);
manifest points at fark_proto.html with assets/ icons. Verified: game
boots from the new layout, zero 404s among live requests, old paths 404.
Denis's local edits preserved at their new homes (char_frames.psd,
pouch.png, Pyre09.png, .claude configs). Recovery note: the root
fast-forward aborted mid-cleanup (modified files inside moved dirs) —
resolved by backup → reset --hard to the branch → restore; nothing lost.

## P20 — DRESSING BEGINS: painted Room (done)

The main-screen mockup (assets/_mockups/new_main) is now the live Room:
- Stage: bg3/fg3 env layers, 9:16, per-card layered parallax + wiggle,
  entry/drop waves, the drag toy — all from the approved mockup.
- Cards = the real roster: name (canvas-baked JMH Beda), buy-in, frame
  colour rotates green/purple/blue/red by seat, trait seal by persona
  (steady/greedy/reckless/strong/orderly/cunning), portraits mapped
  persona→patron_fish/hog/lizard/toucan (placeholder until per-patron
  art), gone-home swaps the who layer, won bakes "won" on the card.
- Panel: panel_krox sheet (per-class art pending) with LIVE target /
  stake / pot; band = trait · dice · lucky die · card count · sealed
  rule · grudge · For Keeps armed. SIT DOWN launches the seat; close
  re-enters the crowd.
- Live top chips: hearts (heart_full/empty), gold plate. Sealed seat
  wears a placeholder black-wax dot (art pending).
- Temporary greybox overlays on the stage until art arrives: chalk chip
  (→ book sheet), boss door bar with pips (→ boss peek sheet, READY
  state), ledger/tavern chips, bottom nav (menu/loadout/shop).
- Fan layouts for 5-6 seats added (mockup had 4 positions).
Verified live: 4 cards == roster, canvas text baked, panel values real,
SIT DOWN → match, zero art 404s, zero console errors. Layouts for
5-6-seat nights are untested visually — check when night 4+ art lands.

## P21 — font pass + portrait registration (done)

- JMH Beda (the mockup's chosen body font) is now the UI font everywhere
  in the dressed/greybox layer: title, room overlays, sheets, modals,
  shop, loadout, settings, shelf, barred (11 font-stack swaps). The old
  match screen keeps its own type until it gets dressed.
- Portrait fix: who_*.png are full-card 443x802 transparent characters;
  the four patron_*.png are 460x495 WINDOW portraits with their own
  painted backdrop. They now render in the frame's picture window
  (inset:auto;left:5.5%;top:3.5%;w:89%;h:54.5%;object-fit:cover) instead
  of being contain-centered across the whole card. Gotcha: inset:auto
  must be declared BEFORE left/top — the shorthand resets them.

## P22 — portrait registration v2 + de-aliasing (done)

- Portraits: measured everything from pixels. All four patron_*.png share
  one backdrop rect (15/10.7 -> 88.3/86.1% of their 460x495 canvas); the
  frame's window hole is 6.1..93.9 x 4.5..60% of the card. The who-layer
  now maps backdrop->window exactly (left:-11.9%;top:-3.4%;width:119.8%;
  height:73.6%;object-fit:fill — ~3% aspect squeeze, imperceptible).
  Art-pipeline note for Denis's future exports: keep the same canvas +
  backdrop rect and everything self-registers.
- Aliasing root cause: the old game's `body{image-rendering:pixelated;
  -webkit-font-smoothing:none}` is inherited. The painted stage + every
  dressed host now override with auto/antialiased.
- Desktop phone shell no longer downsamples to a fixed 390px: it fills
  96vh at phone aspect (e.g. 501x1085 in the test pane; bigger on a real
  monitor), so painted art renders near source resolution.

## P23 — panel sheet contained (done)

The character panel no longer covers/crops the stage: its art (1080x1920)
now lives on #ptPanelSheet — centered, art-aspect, width:min(92cqw,
52.9cqh), drop-shadowed, all overlays (band/values/buttons) riding the
sheet so their % positions hold. Verified: exact 9:16 sheet, margins
~20px sides / ~132px top+bottom at test size, SIT DOWN inside the sheet.

## P24 — red trait seals from Art/Assets (done)

Art/Assets/ is Denis's live export tree (traits, Frames, Panels, Hearts,
Backgrounds, Bosses, Dice, NewRun...). Trait seals now load from
Art/Assets/traits/*.png — the updated always-red wax set (design law 5:
single-colour wax, symbol only). Persona map: ones→steady, hoard→greedy,
aggro→reckless, triples→strong, straights→orderly, combo→cunning;
lucky.png reserved (likely the lucky-die marker). Art/ is gitignored
(1.9GB, Denis-owned); the session worktree reaches it via an NTFS
junction (mklink /J) so the 8084 dev server resolves Art/ paths.

## P25 — starter draft dressed (Art/Assets/NewRun) (done)

Three full-screen layers on a 9:16 stage: bg (innkeep at the table,
coin-spotlight), shadow, hand (open palm). On entry the hand eases DOWN
4.5% over 1.25s (cubic ease-out) presenting the dice; the shadow rides
the same beat with a smaller, laterally-offset travel (1.2%,-2.6% -> 0)
for parallax. Reduced-motion disables both. Dice stay placeholder chits
(dark rounded boxes, family-colour base) moved up to 38% — above the
palm, inside the bg spotlight — fading in after the hand lands. Tap →
inspect → TAKE IT flow unchanged. Verified: all three layers load, anim
wired, pick lands a die and the painted Room follows. Zero errors.

## P26 — boss moods in the Room + sheet blur (done)

- Sheet blur: opening any bottom sheet (die inspect, boss peek, book)
  stamps body.gbSheetOn — the painted stage behind (NewRun layers, Room
  env/cards/chips) blurs 6px and dims to .55 with a .35s transition, on
  top of the scrim.
- Boss-driven environment, generic for all bosses:
  Art/Assets/Backgrounds/MAIN/<NAME>/<Name>_env_BG.png +
  <Name>_env_Foreground_{idle|curious|ready}.png replace the mockup
  bg3/fg3. Mood: ready when the board's full; curious from
  ceil(pointsNeeded/2) circles; idle below. Foreground fades in (.7s)
  when the mood changes; the other two moods preload so swaps never pop.
  Missing boss art falls back to bg3/fg3 via onerror (nights 2-8 until
  their layers land). Grog himself is a tap target (upper scene hotspot
  → boss peek); the greybox pips bar stays until chalkboard art exists.
Verified: idle at 0 circles, curious at 1, ready at 2 on night 1; layers
load; tap-to-peek works; blur class engages/clears. (Pane freezes CSS
transitions — verified by rule, not by eye; Denis to confirm visually.)

## P27 — proper patron cards (Art/Assets/Frames/Patrons) (done)

Cards rebuilt on the real layer set: bg_<color> / frame_bg_<color> /
<Character>.png (full 443x802 canvas) / frame_fg_<color>; GoneHome.png
for spent seats. Four characters (Krox, Eira, Nebb, Regis) are assigned
per seat ONCE per night (stored as roster[i]._art, unique while pool
lasts, repeats beyond 4 seats) and the banner NAME follows the image
name. Frame colours still rotate by seat; trait seal stays persona-red.
The old new_main who_/card_ layers and the patron_* window portraits are
retired from the Room (the .win window path stays for any future
window-format exports). Verified: layers load, four unique names, stable
across re-renders.

## P28 — painted home screen (done)

Homescreen folder held only homescreen.psd (no exports) — extracted via
psd-tools: Background → bg.png (downscaled 1080x1920), LOGO → logo.png
(native 1766x1372, placed at the PSD's own coords: left 10.1% top 15.3%
w 81.8%). Buttons: Button_thick_red/green plates at the PSD positions
(x 19%, w 62%, red y 60.7%, green y 73.3%), big centered JMH Beda text
with a dark drop. Logic: fresh save → single green NEW RUN; live run →
red NEW RUN (confirm modal) above green CONTINUE — NIGHT X. Icons:
pouch (shelf) bottom-left, cog (settings) bottom-right, 13.5% wide,
thick #100903 outline via 8-way drop-shadow stack. Verified: all art
loads, fresh/live button states, icons open shelf/settings, outline on.
NOTE: psd-tools (pip) now available for future layer extraction when
exports are missing.

## P29 — in-scene new-run confirm on the title (done)

No modal: tapping NEW RUN (red) with a live run blurs+dims the bg/logo,
hides the bottom icons, raises "Start a new run? / night X and
everything on the table is lost" big above the red button, slides
CONTINUE out left (.3s) and a blue KEEP DRINKING in from the right
(.38s, slight overshoot). Red tap #2 starts the run; KEEP DRINKING
reverses everything. Fresh saves keep the single green NEW RUN direct
path. _gbNewRun's modal remains for non-title callers.

## P31 — zdepth home screen: parallax + depth blur (done)

Denis painted Homescreen/zdepth.png (white=near). Baked four alpha-mask
PNGs from it with PIL (hs_mask_near/mid = feathered parallax bands,
hs_mask_depthNear/Far = raw + inverted depth for blur weighting) —
alpha-channel masks so plain mask-image works across browsers.
- Parallax: two bg clones masked near/mid drift on a lazy spring driven
  by pointer (desktop) and deviceorientation (phone; iOS permission
  requested on first tap). Near ±1.4%w, mid half; layers scale(1.05) to
  hide edges; paused while confirming; reduced-motion disables.
- Confirm blur is depth-weighted now: far clone blur(9px), near clone
  blur(2.5px), base picks up blur(1.5px) — nothing in focus, falloff
  follows the painted depth. Logo stays sharp.
- Button swap fully sequenced (leaver clears in .28s, arriver enters
  after .3s delay with overshoot — no overlap either direction).
- Ask text: lower (43.5%), sub is just "everything on the table is lost".
Masks regenerate via PIL if zdepth changes (script pattern in notes/
session scratch). Pane rAF freeze = parallax verified by state, not eye.

## P32 — depth layers canvas-baked (mask-image fallout) (done)

Denis saw no parallax and uniform blur: CSS mask-image on the layered
clones didn't take in his browser. Replaced with canvas baking at first
title render (_hsBake): draw bg at 768px, inject per-pixel alpha from
zdepth's red channel (near band (v-150)*4, mid band around v≈105, DoF
near=v, far=255-v with ctx.filter blur 2.5/9px pre-composited), export
four dataURL bitmaps, cache on window, feed the same layer <img>s
(hidden until .baked). Pixel-verified: far alley alpha 0, foreground
opaque, in the pane. hs_mask_*.png files are now unused leftovers.
Fallback: bake failure (file://taint etc.) leaves base env + uniform
confirm blur.

## P33 — depth layers pre-baked (file:// support) (done)

Denis double-clicks the file (file:// in Firefox) → canvas getImageData
is blocked (tainted) → the runtime bake failed silently. Layers are now
PRE-BAKED PNGs: hs_layer_{near,mid,dofNear,dofFar}.png in Homescreen/,
generated by docs/tools/bake_home_layers.py (PIL; rerun when bg.png or
zdepth.png change). Runtime canvas bake deleted; layer imgs point at
the files with onerror hiding. hs_mask_*.png leftovers removed.
LESSON: everything in this game must work from file:// — no runtime
canvas pixel-reads on art, no fetch-dependent features.

## P34 — parallax de-ghosted (done)

Feathered semi-transparent bands blended shifted copies over the base =
ghosting. Now: ONE hard-cutout near plate (depth>=213, 8-step edge —
raised from 150 because the cobblestone floor's depth gradient crossed
the old threshold and left a soft band), mid plate deleted, near travel
halved (±0.8%w) with a slight opposite counter-shift on the base
(±0.25%) so displacement splits across the cut. Plate audit: 1.3% semi-
transparent px (edge feather only), 9% opaque (barrels/sign/planters).
Remaining known artifact: a thin doubled edge at plate borders at full
tilt — the real cure is Denis exporting separated plates with painted
fill behind near objects (like the Grog room env layers) whenever he
wants this dialed to perfect.

## P35 — WebGL depth displacement (the real 3D) (done)

Plate parallax read as split/banded — replaced with a per-pixel
displacement shader: uv += offset * (depth - 0.30), depth resampled once
for stability; DoF is in-shader too (mix to a pre-blurred texture,
weight 0.45+0.8*(1-depth), scaled by the confirm mix which eases 0..1)
plus the 0.5 dim. Textures (bg 1080w jpg, blurred bg, 540w depth) ship
as data-URIs inside Art/Assets/Homescreen/hs_home_data.js (0.53MB,
script-loaded => file://-safe; canvas/WebGL image uploads from file://
are tainted, data: is not). Canvas #hsGL is a PERSISTENT node
(window._hsGLCanvas) re-attached on every title render — innerHTML
rebuilds must never recreate it or the context+textures die (that bug
cost one round). Fallback chain: no WebGL/data → DOM plates → static.
Knobs: strength ±0.016uv, focus plane 0.30, overscan 1.04.
Pixel-verified: renders, displaces (opposite offsets differ), glOn hides
plates, survives re-render. bake_home_layers.py v3 regenerates the pack.

## P39 — rules page + panel polish (done)

Innkeep's Book screen removed. The settings sheet now serves two pages:
_gbSettings('set') and _gbRules() (Scoring only — singles, triples with
the doubling note, straights 500/750/1500, three pairs 1500, two
triplets 2500, hot dice +250, bust). Book icon MOVED to the title's
bottom middle (pouch · book · cog, all 14.5%, Room-scale); the Room's
chalk chip also opens the rules. X on the sheet enlarged to character-
panel scale (consistency rule from Denis: similar elements keep the
same scale screen to screen). Abandon-run row already removed —
title-screen NEW RUN covers it.

## P45/P46 — 3D dice (dice_playground21 port) (done)

D3 engine appended before the family engine: CSS-3D cuboid, 6 face divs
each carrying the full transform chain (camera tilt > spin > pitch > yaw >
face placement), manual backface culling, per-face lighting
(brightness + shade overlay vs LIGHT vector), physics roll with tumble
turns + parabola bounce + neighbour shove within a group, hover-bob mode
for showcase dice. One shared rAF loop (D3.start) prunes disconnected
dice. Face textures live in Art/Assets/Dice/bone_1..6.png (extracted
from the playground's data-URIs); future sets drop in as <type>_N.png.
Placeholder material tints via CSS filter (D3.TINT: amber/jade/silver/
obsidian/starstone/vagabond/lucky...) until Denis paints real textures.

Surfaces converted:
- Starter offer (NewRun): 3 big hovering dice tumble in above the
  innkeep's palm at 950ms (after the hand descends), hover:true.
- Match (P46): mkDie now returns a .die.d3on host (keeps all selection/
  frozen classes + handlers; D3 renders inside). _d3InitHost defers
  D3.make until the host is connected+sized (setTimeout polling — the
  tool pane freezes rAF, don't use it for init). Guards at settleDie,
  reDrawDieFace, the reused-dice crossfade, and both NPC die-forcing
  sites (sawdust/iron gate) reroute dot-grid rewrites to short D3.rolls.
  window.D3_MATCH=false flips back to flat dice.

Verified in-match: 6 dice render on roll, faces == pool values, click
select works, reroll tumbles only uncommitted dice, banked 650 clean.

Still flat (next): loadout tiles, shop dice cards, peek-sheet chips —
plan is small fixed-pose D3 dice.

## P47/P48 — still-pose dice on every display surface (done)

P47: mkDie grew a 4th arg (still) — pose-only D3: no tumble on
re-render, no group shove, no cast shadow, deterministic small spin
jitter so rows look hand-placed. Applied to the kept row, the old
tier/boss loadout tiles, shop dice cards + strip, and reward dice.

P48: the greybox surfaces that drew dice as text boxes / colored
squares now show real still dice via .d3chip placeholders
(data-mat/data-val) + _d3ChipScan(root). _gbSheetOpen scans
automatically, so every sheet gets dice for free. Converted: shop
dice tab cards (42px), die inspect sheet (54px), enchant pick-your-die
boxes (26px), loadout equipped row (30px) + satchel (24px), patron
peek chips (24px, replaces the 18px colored squares). Type shown by
the placeholder tint (D3.TINT) until real textures land.

Verified live: shop 8/8, loadout 6/6, inspect 1/1, enchant 6/6,
peek 6/6 chips initialized; visible faces=3, per-face lighting and
tilt+spin transform chain correct; no console errors.

## P49 — starter offer rework (done)

Entrance: dice are born small in the palm (scale .30, +58% down) and
float up to full size over 1.5s, staggered 200ms — no tumble; D3.roll
grew gentle knobs (turns:0 exact tumble count, spinMax caps table spin,
flat kills the height parabola) so each die just settles onto its face
from a random orientation while rising. Hover untouched (Denis: hover
is fine, the initial spin was too strong). Row lowered 34% -> 41.5%,
name labels pulled tight under the dice (38% -> 10% margin), banner
bigger (1.9 -> 2.6cqh) and lower (2.6% -> 5.4%), wraps on two lines.

Tap-to-focus replaces the parchment sheet: the die flies to screen
center-top (translate+scale 2.05, back-out bezier) over a radial scrim;
env layers blur+dim, the other two dice ghost to 8%; pulsing gold glow
+ 12 rising spark particles (pure CSS, file://-safe); read-out beneath
in big white JMH Beda — name 5cqh, faces row gold 3.6cqh, desc 2.9cqh
with digits accented gold; painted green TAKE IT button (home-screen
plate); tap the scrim to put it back. The FIRST NIGHT banner stays
sharp and above the scrim during focus (z6, no filter). Taps are
ignored until a die's float-in completes (_floatDone).

## P50 — offer screen round 2 (done)

Entrance jitter fixed at the engine: flat rolls now rotate over the
FULL duration (krFull — before, kc=0 collapsed the rotation window to
the first 12%, a ~150ms snap), and hover height ramps in over 700ms
after a roll instead of popping (d.hoverT0). Banner: 3 lines, 3.5cqh,
dark plate removed (text-shadow carries it), fades out during focus.
Dice row 41.5% -> 47%, labels ride with it. Focus: die target y
0.27 -> 0.37 (hovers above her hand, closer to the text), panel
51%, faces row one line (3cqh, .12em), desc smaller (2.4cqh),
TAKE IT bigger (80% wide, native 1136/334 plate), painted thin-red
BACK button replaces the tap-elsewhere hint (scrim tap still works).

## P51 — offer round 3 + material outlines (done)

Banner: 4.2cqh, line-height 1.55, top 7.2%, FIRST NIGHT in gold
(.nrN accent — it's run-tracking info). Focus: the other two dice hide
completely (opacity 0), and the die's own name label now rides the
zoom (scales 2.05 with the tile) to become the focus-screen title —
no separate .fname, the panel starts with the faces row at 57%. Focus
translate math fixed to project the host centre through the scale
(scale is about the tile centre; the old direct-delta landed ~11%
high) — die now lands exactly at (50%, 37%), label ~50.7%.

Engine-wide: die outlines are no longer black. D3.OUT maps each
material to a darker, more saturated version of its own colour
(amber #7a3a08, jade #14501e, starstone #1c4a74, obsidian #2a0d0b,
silver #343c46, vagabond #571412, lucky #7a5408, ...; bone keeps the
warm near-black). Tint now applies BEFORE the drop-shadow outline in
the filter chain so the outline colour stays exact.

## P52 — per-material sparks + banner ellipsis (done)

D3.SPARK maps each material to a particle colour + shape: warm dots
(bone/amber/jade/flint/lead), white/blue/gold 4-point star glints
(silver/starstone/lucky), ember diamond shards (obsidian/vagabond/
iron). Shapes are clip-path polygons, glow via drop-shadow(var(--pc))
so it survives the clip; diamonds are elongated 1.5-2x for a shard
feel. _nrFocus builds the 12 sparks from the spec. Banner now ends
"a die with your ale..." (&hellip;).

## P53 — pencil-grain outlines (done)

Outlines thinned (cfg.ow 1.5 -> 1) and roughed up: D3.ensureFilters
injects an inline SVG (feTurbulence fractalNoise + feDisplacementMap)
and D3.draw appends url(#d3pencil) after tint+outline in the filter
chain, so the whole die render — outline included — gets a ~1.8px
hand-drawn wobble matching the painted art's pencil edges. Small
chips (<34px) use url(#d3pencilSm) so they don't smear. Inline SVG =
file://-safe. v2 (Denis: stronger/rougher): two displacement stages —
low-freq wobble (0.085, scale 4) so the line drifts like a hand
stroke, plus high-freq grain (0.95, scale 2.4) for the dry edge;
chips 0.14/2.2 + 1.1/1.3. Tune those four numbers for rougher or
cleaner; window.D3_PENCIL=false kills it if perf suffers on phone.

## P54 — phone testing via GitHub Pages (done)

Live at https://rigamix.github.io/Fark/ (redirects to fark_proto.html).
Pages source flipped main -> fark branch; main (old painted game) is
untouched and can be re-pointed anytime. .gitignore now ships
game-ready exports (Art/Assets minus *.psd and _old/, ~51MB) while PSD
sources stay local. Case audit ran clean (Pages is case-sensitive,
file:// is not) — 66 referenced paths, 0 mismatches. sw.js is the
self-destruct stub, so phones with the old PWA cached get wiped on
first visit. DEPLOY FLOW: commit in worktree -> ff-merge root ->
git push origin fark (root checkout is the fark branch).
BACK button on the offer focus: 46% -> 56% wide, lower, bigger text.

## P54b — Pages fixes after Denis's phone test (done)

Broken fonts/hearts/gold on the live build: GitHub Pages runs Jekyll
by default and Jekyll EXCLUDES underscore-prefixed dirs — everything
under assets/_mockups/ 404'd (JMH Beda.ttf, heart_full/empty, gold
plate, panel sheets, sit/close buttons). Fix: .nojekyll at branch
root. Dice-all-look-the-same on iPhone: Safari drops a CSS filter
chain that contains an SVG url() reference, killing tints+outlines —
the pencil grain now skips Safari (UA guard, D3._noUrlFilter); tint
and outline drop-shadows stay. Home-screen gyro parallax on iOS
already requests motion permission on first tap.

## P55 — under-the-notch + ambient depth (done)

viewport-fit=cover added (standalone iOS was letterboxing below the
status bar). Art now bleeds under the notch; HUD steps clear via
safe-area rules: ptHearts/ptGold/nrChalk top:max(orig, inset-top),
.hsIcon bottom:max(2.2%, inset-bottom), .gbx overlays pad top/bottom
with the insets (!important beats their inline padding). Home depth:
when no gyro/pointer input for 2.5s the parallax targets follow a slow
sine sway (0.33/0.27 rad/s, amp .45/.35) so the 3D effect is visible
on phones even if motion permission is denied or never granted.

## P56 — iOS round 2 (done)

Reduce Motion on the phone was killing the ENTIRE depth system (the
early return skipped the render loop, the ambient sway AND the
motion-permission prompt — why iOS "never asked"). It now only mutes
the self-running ambient sway; gyro/pointer input and the prompt are
user-driven and stay active. Permission is requested on both
DeviceOrientationEvent AND DeviceMotionEvent (iOS prompts
inconsistently between them). body gets height:100dvh (@supports
guard) against the standalone bottom dead-band. New remote debug:
open ...fark_proto.html?hsdebug for an on-screen metrics badge
(viewport/stage sizes, safe-area insets, standalone, rm/gyro/perm/gl).

## P57 — iOS round 3 (done)

Motion popup: WebKit doesn't grant user-activation to pointerdown, so
requestPermission silently no-oped — now asked on click+touchend
(badge also reports rpAPI presence and 'noAPI'/'thrown' states).
Safari-tab reality: the bottom toolbar band cannot be painted from a
tab; true fullscreen only in standalone (manifest already
display:standalone, start_url fark_proto.html, icon serves 200). When
the game runs in an iOS BROWSER tab it now shows a one-time title
hint: "for fullscreen: Share -> Add to Home Screen" (localStorage
fk_a2hs_seen, tap to dismiss).

## P57b — dice tints on iPhone (done)

The P54b Safari guard was a blocklist matching the "Safari" UA token —
but standalone/home-screen WebKit doesn't SAY Safari, so the pencil
url() stayed in the chain and WebKit dropped the whole filter: every
die rendered untinted bone. Now an ALLOWLIST: grain only on desktop
Gecko/Chromium (Firefox|Chrome|Chromium|Edg, and never on iP*);
everything else always gets tint + material outline.

## P58 — baked pencil outlines (cross-platform) (done)

Denis can't bake outlines into face art (they're engine-drawn), so the
grain moved into the ALPHA: docs/tools/bake_dice_pencil.py shrinks
each face 7% onto transparent margin and displaces the whole texture
with wobble+grain noise fields (240px out; pristine faces auto-
archived in Art/Assets/Dice/src/). The engine outline is a drop-shadow
of the faces' alpha silhouette, so it now traces the wobble on EVERY
engine — the SVG url() filter and its allowlist are deleted. Face
corner radius dropped (clipped the wobble); the shade overlay div
would have painted a square over the transparent margins, replaced by
a deeper brightness range (0.42+0.68*dot). Die size factors bumped
(match 0.88->0.94, offer 0.72->0.77) to compensate the margin.
Future material sets: drop <mat>_1..6.png in Dice/ and rerun the tool.

## P59 — clean outline + per-face filters (the real iOS tint fix) (done)

The baked wobble tore holes at strength — reverted to pristine faces
(Dice/src/ archive; bake tool kept for future tuning at lower
amplitudes). And the true reason iPhones showed all-bone dice even
with no url() in the chain: iOS WebKit IGNORES filters set on a
parent of 3D-transformed children (the cuboid container) while
per-face filters work (the dark side faces proved it). Tint + the
material-colored drop-shadow outline now compose with the lighting
brightness ON EACH FACE; the container filter is cleared. Shade
overlay, corner radius, original brightness curve and size factors
all restored. Rule of thumb recorded: on WebKit, filter anything with
3D-transformed children at the CHILD level.

## P59d-P60 — the iOS standalone bottom-band saga (done)

Installed PWAs on iOS (black-translucent + cover) get a render surface
clipped ~47px short at the bottom (innerHeight = screen - status bar,
anchored at the top). Everything below is a SYSTEM letterbox painted
in the manifest background_color — no CSS/JS can reach it. Failed
attempts (reverted): stretching body over the deficit + making body
the fixed-overlay containing block (only pushed content into the
clipped zone — icons got cut); manifest display:fullscreen (no
change). Final approach (P60): the game lives inside the real
viewport; in standalone (html.fkSA) the title/Room bottom vignettes
deepen to solid #060402 and manifest background_color is warm dark
#1a0f08, so the band reads as part of the fade. Viewport meta slimmed
to width+initial-scale+viewport-fit (maximum-scale/user-scalable
dropped — documented trigger for the short-viewport bug on some iOS
builds, ignored for pinch anyway). Badge (5-tap logo) tells the
truth: inner 390x844 = iOS fixed it someday; 390x797 = band blended.

## P61 — Room: boss text + new char panel (done)

Grog's image is no longer tappable (ptBossTap removed) — only the
BOSS — GROG text block opens the peek. The row lost its dark pill:
plateless JMH Beda in offer-screen style, boss name gold (#ffd98a),
progress circles now FILL gold with a soft glow (empty = dim cream),
caption under. Char panel rebuilt on Denis's new base
(Panels/Commoners/<art>.png, name + wax removed from the art;
fallback Krox for characters not yet painted): name plaque (title +
art-name, cream 3.4cqh) sits across the portrait's bottom edge, red
wax trait seal on the portrait's bottom-right corner (rotate -9deg),
and the purple band (measured 42.9-54.3%) holds the opponent's six
dice as still D3 chips (11.5% each) with a one-line persona/lucky/
cards caption inside the band's foot; sealed/grudge/for-keeps
callouts sit below on the parchment in seal-red. Values row
(target/stake/pot) unchanged.

## P61b — painted settings checks (done)

Denis's check_on/check_off icons (Icons/, 64x34) replace the on/off
text in the settings rows (incl. fast rival). 3.4cqh tall, off state
slightly dimmed, same tap-bounce on just the toggle.

## P62 — panel v3: mock name layout + reference iso dice (done)

Engine grew per-die camera params: d.tilt (overrides cfg.tilt) and
d.turn (rotateY between tilt and spin; rotv matches). Iso still chips
(.d3chip[data-iso]) pose every die identically — tilt -42 / turn -40 /
spin 0, value face on TOP (pitch=FACE_ROT+90; verified empirically,
the engine camera convention is inverted vs intuition) — with a tight
1px-blur shadow ellipse under each, die at 96% of chip. Panel: name
in the cream column right of the portrait (title small 3.3cqh over
name 4.8cqh, right-aligned, dark ink per mock), wax seal beneath with
the trait word in seal red #631c2a under it, dice span the full
purple band (15.6% chips), lucky/cards line + red callouts below the
band. ptvInfo removed.

## P63 — panel corrections (done)

The iso cube projects ~1.45x its face size — that's why the dice
overflowed the band and buried their own shadows. Iso chips now use
face=66% of chip; the shadow is 1.3x the face wide and sits below the
projected bottom. Verified: each die 11.5% of sheet width, fully
inside the band, row fills 95% of it, shadows visible, values on top.
Name up (title 4cqh, name 6.2cqh), seal down (13.5%), trait word up
(3.2cqh) hugging the seal. Sealed/grudge/FOR-KEEPS moved into the
band's foot as short cream/parchment tags (they were overlapping the
Target row); the tell's rule text joins the lucky/cards line below
the band.

## P64 — boss progress lozenges + sealed smoke (done)

Boss row much bigger (title 3.7cqh) and moved up over Grog (50.6%,
z6); patron cards dropped 4.2% (tops ~66-67.6%). Progress = Denis's
Icons/Wins lozenges (00 cold blue -> 03 red): one per required win,
earned slots wear the current heat (start->0, progressing->1, one
away->2, ready->3), empty slots dimmed cold; 4.8cqh tall. Text reads
"You need N more wins" with the count phrase accented in the exact
heat colour (HEAT map) — re-renders after every match, so it walks
blue->red as the night progresses. Ready: GROG IS WAITING, all
lozenges red, "a heart at stake" accented red.

Sealed seat: the black wax dot is gone. The card gets a smoke ring —
four blurred violet wisps drifting around the frame (inset -13%,
z-order behind the card layers) plus 7 rising dark sparks along the
edges — so the mark reads instantly without covering the portrait.

## P64c — the vanished patrons (all browsers) (done)

P64's smoke CSS added `.ptcard .cwrap{position:relative}` — but .cwrap
was intentionally UNSTYLED: the card layers (.ly, absolute inset:0)
anchor to .ptcard. Positioning .cwrap made it their containing block,
and since it has zero flow height every layer collapsed to 0px — only
the trait seal (own width + aspect-ratio) survived, which is why the
Room showed nothing but small red seals at the card spots on phone AND
Firefox. Rule deleted; the smoke ring now sits at z:-1 inside the
card's stacking context (z:3) instead. Lesson in the CSS comment:
never style .cwrap.

## P65 — GROG overhead + opaque smoke (done)

Boss name is now just GROG (rank line supported via tier.boss.title
if one ever exists), 8.4cqh gold, at the top of the room BETWEEN the
env bg and fg layers, so Grog's art overlaps the letters; still opens
the peek (env imgs are pointer-events:none). Progress block moved up
(47.8%) and grew (lozenges 6.2cqh, text 3cqh) with clear air between
it and the name. Dimmed lozenges: saturate(.3) brightness(.72), NO
transparency — Denis's art rule recorded: never semi-transparent
objects in this game. Sealed smoke v2: sharp opaque violet blobs
(#5e4d7a/#54446e/#493a61, no blur) with big wobble (morphing
border-radius + drift/rotate/scale keyframes), diamond sparks that
grow/shrink instead of alpha-fading.

## P65j — GROG-only peek + purple sealed frame (done)

The boss peek opens ONLY from tapping the GROG name (progress block is
pointer-events:none). Sealed seats always wear the PURPLE card set
(bg/frame_bg/frame_fg_purple regardless of seat index) plus a violet
glow (two stacked drop-shadows on .ptcard.sealedFx) matching the smoke
band. NIGHT chip is a plain label now — rules access is title-screen
book icon only.

## P66 — panel on the extended base (done)

Krox.png grew to 1080x2011 (extended bottom). Sheet aspect + width
clamp updated (50.3cqh), every anchor rescaled: band 41.0-51.8%, dice
41.5/7.8, xtra 49.2, luck 52.6, values bottoms 40.6/31.6/23.1. Name
CENTERED in the right column (3.8/6cqh), wax seal smaller (10.5%) at
the portrait's bottom-right corner, trait word 2.3cqh beside it. The
old full-sheet button overlays (btn_sit_full/btn_close_full) can't
align with the new aspect (contain letterboxing) and the buttons are
baked in the new art — overlays hidden, hit zones moved onto the baked
buttons (sit 14/81 72x9.5, X 78/87 18x8). Press-bounce feedback on
those buttons is gone for now (art is baked); revisit if Denis wants
it back via cropped button sprites.

## P67 — panel round 5 + sealed rework (done)

Room card: crisp outline now a border ELEMENT (.csout, 3px #3d2f52,
radius 7%) — the old 4-way drop-shadow filter wrapped the translucent
smoke and everything read blurry. Panel: SEALED label gone; a sealed
seat's PANEL wears the same treatment (#ptvOutline border rect +
#ptvSmoke band reusing the .csmoke classes, sheet.sealed toggles).
Seal bigger (15.5%) under the centred name, trait 3cqh under it.
Card count = fanned mini-card icons (#ptvFan) straddling the band's
bottom line. Lucky die: name text dropped; its chip glows gold
(.d3chip.lux::before). Dice centred in the band; shadows are now
DIE-SHAPED sharp offset silhouettes (d.dieShadow -> per-face
drop-shadow in D3.draw), ellipse hidden. Values re-anchored to the
art's rule lines (66.4/73.4/81.7% -> bottoms 34.2/27.2/18.9). SIT
DOWN painted green button restored (new base doesn't bake it), X at
the true bottom corner (80/90). Sheet sits lower (52.6%). Panel-open:
GROG + nav fade out; hearts/gold/NIGHT stay clean above the scrim
(z9); only bg/fg/bossbar/chips blur. Tell rule text lives below the
band (55%) pending Denis's placement pass.

## P68 — title + outline fit + panel round 6 (done)

Title: shelf/pouch icon removed, rules book takes the left slot.
Room card: outline hugs the VISIBLE art (frame alpha ends 97.1%
bottom -> insets .4/.4/.4/2.9), opacity .7 to match the smoke's
intensity, and the smoke band now ends AT the outline's top edge so
the two never stack into a darker seam. Panel: outline follows the
art's alpha bbox (1.6/.7/.9), smoke band deleted on the panel (sparks
stay); name in the frame olive #4b5527; seal 12% centred on the
column axis, shadow removed, trait tight under it (27.6%); tell name
(2.7cqh purple) + small rule text (1.7cqh brown) fill the new gap
between band and rows (53.6%); values re-anchored to the new rules
(68.4/75.5/82.5 -> bottoms 32/25.1/18.1) and shrunk to 3.3cqh;
SIT DOWN on the stretched 1430/334 plate (72% wide, shorter);
grudge/FK tags at 61.6%; die drop-shadows removed.

## P69 — sealed reward callout (done)

Sealed panels show, above the character name: N win-lozenges + "worth
N wins" (N=2, or 3 with Marked Table). The lozenges render in the heat
stage the run would REACH if you won this match (need 2, have 0 -> two
red 03s = "this puts you at the boss"), so the shortcut to the boss is
visible at a glance. Non-sealed panels show nothing there.

## P70 — match screen art, pass 1 (FARK_MATCH_BRIEF) (done)

Assets: Art/Assets/Match/ (Table plate 1080x2011, 15 props, ScoreBar
base/fill/overlay — the fill art is PRE-SPLIT red-left(opp)/
blue-right(player) racing to the overlay's centre crest, portrait
rings copper(opp)/iron(player), Bank/Roll plates, pause).
- Plate: #matchPlate behind patron matches; boss matches keep their
  bespoke ::before plates (_matchDress(isBoss) toggles; boss detection
  = the 8 known keys at the boss-class site).
- Props: 8 authored margin anchors (never the centre band), per-match
  mulberry32 seed (G._propSeed), 3-5 sprites, size jitter, ±8° rot.
- Race bar: raceWrap 70% centred; the engine's EXISTING width writes
  to #oProg/#pProg now reveal the fill halves (rbClip halves are
  size containers; fill img spans 200cqw anchored to the outer edge),
  target number sits on the crest, TURN X chalk beneath. Portrait
  tokens at the ends: opp gets a face crop of Frames/Patrons/<art>
  (window._lastSeatArt set in launchSeat), totals + labels beneath.
  ALL engine ids preserved — zero engine update-site changes.
- Buttons: BANK left (green plate) / ROLL right (gold, flex 1.55);
  BANK label carries the exact bankable amount ("BANK 650"),
  bank-to-win swaps BANK onto the gold plate; quit ✕ hidden, pause
  button top-right opens the same confirm.
Verified live: plate+3 seeded margin props, portrait token, roll,
select -> "BANK 50", bank -> fill 1.79%/score 50, boss toggle hides
plate+props. Next passes: kept-pile tag, selection chalk tag styling,
card backs + rule notes, paws, boss hearts row.

## P71 — match pass 2 (Denis's reference) (done)

Props: chunky corner-weighted authored clusters (12-24% wide, edge
crop welcome), not an even sprinkle. Buttons: the OLD layout
absolutely centred ROLL (left:50% translate) and pushed BANK right
with margin-left:auto — that's why order/flex had no effect and the
plates overlapped; overridden (position:relative, margin 0), plates
keep native aspect via width+aspect-ratio+contain, controls strip
transparent (brown bar gone), bank-to-win width-swap via :has, old
soft glow removed. Race bar narrowed clear of the tokens (17.5%).
Dice: clamp(58px,15vw,76px) (~76px) and raised to the centre band
(47%) via the #diceArea spacer vars (--sp-before 1.1/--sp-after 2.4).

## P72 — match pass 3 (done)

Aliasing killed: the body's image-rendering:pixelated was smearing
every scaled match asset — match plate/props/buttons/bar/tokens all
render auto/antialiased now. Props: anchors 12-26%, 5-6 per match,
ALWAYS >=1 coins prop + >=1 cup/vessel (guaranteed picks before the
rest). Race bar wider (14% margins); the target number sits IN the
crest badge hanging under the bar (top:108%, 17px ink). Patron token:
grey metal ring (ring_02), 72px, hangs BELOW the bar's left end,
portrait crop loosened (175% @ 50%/12%) so the face fits. Player side
is text only (total + YOU) — no player portrait.

## P73 — match pass 4: measured + rule-based (done)

Real cause of "texts too small": px sizes against a scaling shell —
#screen-match is a size container now and every dressed size is cqw
(texts, tokens, pause, dice 15cqw). Target number sits at the
MEASURED crest (a centre badge ON the bar, x44-56% — not hanging
below). Patron token crops come from per-character alpha
measurements (CROP map: Krox/Eira/Nebb/Regis). Props are RULES now:
intrinsic real-world sizes per sprite (coin 8 -> towel 20), two
diagonal corner clusters of two (big prop anchors the cluster,
smaller rides beside), 1-2 side singles, coin+cup guaranteed, 5-6
total, jitter everywhere, centre band never spawns.

## P74 — match pass 5: de-greybox the overlays (done)

The mid-table tell badge is now the brief's parchment RULE NOTE at
the opponent edge: compact cream note, wax dot on its left (gold =
binds both, red = boss/player-only), icon + name + live counters
(steepedVal/arrearsVal/drillVal ids intact), desc hidden, tap opens
the rule sheet. The duplicate green famRow "RULE:" chip is gone
(SLEEVED chip stays until notes support two side by side). POT chip
hidden in matches. Dialogue: square portrait frame hidden, strip is
a slim parchment quote under the HUD (14cqw). Prop zones: top
clusters start below the HUD (y>=16), bottom clusters capped (45)
clear of the kept pile.

## P75 — match pass 6 (done)

Props can no longer touch the dice band: top clusters y15-25 with the
partner stacked in the same margin column, bottom cluster is BR only
(partner below it), BL is a small edge single, the opposite-top single
sits above the band — verified zero prop centres within the rolled
dice band ±3%. Player token restored as the bronze ring placeholder,
same size/baseline as the patron token (names + totals aligned). Race
bar bigger (11% margins), number seated on the crest (top 55%).
Disabled buttons stay fully opaque (filter dim only). Pause sits
bottom-left, level with the loadout chest.

## P76 — match pass 7 (done)

Portrait crops recomputed eye-centred with the whole head width in
frame (S 106-118; comb/hat crops at the top when tall). MATCH dice:
per-die tilt 8 (flatter, matches the table's modest perspective —
offer/showcase dice keep 14), size 13cqw, 3cqw row gap. Selection is
now a warm gold SILHOUETTE glow drawn by the engine (per-face
drop-shadow appended when the host has .selected — the flag is read
inside D3.draw so every select/deselect path stays honest; explicit
redraws at the five toggle/clear sites). The old octagon box outline
and box-shadow are suppressed for 3D dice. Bank-history popover
anchors follow the new sides with a parchment look + THEIR/YOUR BANKS
header (P75d).

## P76b — selection concept + drastic angle (done)

The lingering box was a THIRD party: .die-wrap:has(.selected)::after
draws its own rectangle — suppressed for 3D dice. Match dice tilt
8 -> 3 (nearly straight-on). Selection now matches Denis's concept:
the die's outline flips to bright gold (#ffd061) at 1.8x width and a
double warm halo wraps the silhouette (0.14 + 0.32 die-size
drop-shadows) — all engine-drawn per face, iOS-safe.

## P77 — match pass 8 (done)

Dice: I had "less top down" inverted — the table camera is HIGH, so
match dice now rest VALUE-UP viewed from above (d.restTop lifts every
roll/settle target by +90 pitch through D3.roll/setFace; camera tilt
-30). Verified all six settle value-top. New narrower ScoreBar art
(3020x304): bar spans to 2% margins, number 5.2cqw at top 33%.
PATRON/YOU labels removed (Denis's parchment name plate to come).
Button STATE art wired: Roll/Bank default/pressed/inactive pngs (all
dim filters off — the art carries state; the mid-roll disabled swap
verified). Card activation area now wears the YIELD plate (zone
reshaped to the plate's 720/218 aspect, dashed border gone, hot ->
Yield_pressed, unavailable -> desaturate).

## P78 — match pass 9 (done)

Dice: back to the reference — value face FRONT, camera high (tilt
+32) so the value tips back readable (verified: the value face is
the largest projected face on every settled die). Selection glow
rebuilt SILHOUETTE-ONLY: two clone layers behind the die (crisp
#ffd061 rim at scale 1.06 + blurred halo at 1.16) built from the
visible faces' own transforms — internal cube edges stay clean, no
parent filters, iOS-safe; verified created on select, torn down on
deselect. Activation area: dashed border returns, shaped like the
plate (720/218, rounded ends); the YIELD art is a real button in that
slot (blue plate + pressed png, "YIELD" label) shown whenever the
player can act (roll OR bank), hidden during card drags, opening the
forfeit confirm. Scores moved INTO the bar over the fill ends
(o left 7%, p right 7%).

## P79 — concept scoring readout (done)

Selection scoring now matches Denis's concept: a medieval +N in cream
with a warm glow under EACH selected die (singles exact: 1->+100,
5->+50; combo groups — triples, straights, pairs specials — get ONE
tag under the group's middle die carrying the remainder so the tags
always sum to the true total), and the selection TOTAL centred on
screen beneath the row (bigger, same style). Invalid selections show
a grey 0 (the old status-bar '+N' / 'NO SCORE' texts are retired).
Verified: single +100, mixed 1/5/1 -> +100/+50/+100 with +250 total
centred below the row, invalid -> grey 0, full cleanup on deselect.

## P79b — yield gating + unified button text (done)

YIELD hides until the player's first roll of the match
(G._anyPlayerRoll set in handleRoll), then follows can-act as before.
It fills the dashed zone exactly (same box), and the dashes' corner
radius (18px) follows the plate's rounded ends. All three plates
share ONE text treatment now: cream #f7ecd2, identical two-step
emboss (0 2px ink + soft drop), seated 5% lower in the plate; the
old engraved-dark ROLL and green-shadow BANK looks are gone.
Verified: hidden before roll / shown after, box match, identical
computed color+shadow across all three.

## P80 — brief §9: dice as persistent objects (core) (done)

Kept groups now store PER-DIE records ({val,mat}) at all three commit
sites; the pile renders EVERY kept die through the rest-state renderer
with its own material (never one anonymous die per group), slight
overlap, readable faces. The per-group +pts labels are replaced by
ONE discreet "N TURN" chalk tag (BANK carries the prominent number).
Real busts (after all saves, on all three player-bust paths) grey the
pile and wipe the tag in <600ms at the impact beat. Ordering: match
dice already land in loadout order with homeX=0 (no drift) and the
engine shove can't swap DOM order. NOT yet implementable: curse
marks/PRESERVE casing/SLEIGHT rewind (those mechanics don't exist in
the engine yet) — the per-die record structure is ready for them.

## P80b — tag noise + labels (done)

BANK label back to plain BANK / BANK TO WIN (thousands wouldn't fit
the plate; the TURN tag and selection total carry the numbers). A
selection whose single tag equals the total (triple 3s, one lone 5)
shows only the centred total — per-die tags appear only when they add
information. YIELD text sized to exactly match ROLL's (6.2cqw;
verified identical computed size).

## P81 — patron frames v2 + gone-home rework (done)

Denis brightened the patron frame art and moved GONE HOME's lettering
down inside its file — all card layer srcs (+ the match token crop)
carry ?v=2 to force the reload. Gone-home cards drop the
character portrait entirely (P81b), darken+desaturate the whole card (saturate .5 /
brightness .55 on bg/back/who/frame/banner), and GoneHome.png stamps
on TOP (z4, object-fit contain, no positional overrides — its
placement lives in the art). Verified against a forced gone seat;
active cards stay unfiltered.

## P82 — scoring tags tuned + exciting totals + YIELD yields (done)

Per-die score tags: smaller (3.4cqw) with more air under the dice
(2.6cqw gap). The selection TOTAL is gold (#ffd98a) with a glow+shake
that ramps with the score — ~200 is calm, ~2000 is full double-glow
with a 2.4px jitter (selShake keyframes driven by --sh; shadow built
inline in JS, iOS-safe). Invalid stays grey and still.

YIELD bug: the art button had DUPLICATED the legacy #btnYield id (the
hidden post-bank handover button), so getElementById hit the art
button — which was wired to the flee confirm. One button now, and it
yields: mid-turn it forfeits unbanked points, clears the table and
hands over (yieldTurn); post-bank it is the normal handover
(handleYield → endPTurn). Flee stays on pause/X. showYieldButton /
restoreRollButton drive the .on class (no more inline display that
used to permanently hide the button after the first handover).

## P83 — candlelight + table-reveal shadows + prop rules v2 (done)

Light hangs above the table centre, off screen. TableLit.png sits on
the unlit plate behind a breathing radial mask (radial scale + sway,
6.4s ease loop, centre 50%/44%) — candle glow pools mid-table, edges
stay unlit. NOT the candle prop (that stays a normal prop).

Fake shadows: every prop gets a div masked by its own silhouette that
reveals the UNLIT Table.png (cover-geometry slice, aligned via
_alignPropShadows; settle timers, resize hook). The layer breathes in
sync with the light (scale about the light centre — shadows stretch
away radially). Match dice swap the blurry rgba ellipse for the same
sharp unlit-table ellipse, aligned per frame in D3.draw (class tblsh,
opaque; boss tables keep the old ellipse — no plate, _mLight.on=false).

Prop pass v2 (?v=2 art): perspective (bottom props up to ~1.14x, top
~0.92x), one extra edge anchor (7 anchors, 6-7 picks), coins NEVER
alone (pile scatters 1-2 singles, lone coin brings 2 friends), jug or
bottle always gets a mug beside it. bandY clamp accounts for prop
height. Audited 60 seeds: 0 rule violations, 7-10 props per table.

NOTE: pane screenshots timed out (capture-side); verified via DOM,
cover-math equality checks and canvas pixel sampling of both tables.

## P84 — candlelight reads now + shadows read + separation solver (done)

P83 post-mortem from Denis's phone shot: the mask box (212%) kept the
whole screen inside the opaque core (fully lit table, wobble
invisible); shadow offsets hid behind the props and the unlit reveal
was only ~25% darker; corner clusters buried each other.

- mask box now 140%x130%, stops 26->88, positions recomputed per
  keyframe (pool centre holds ~50/44 with a sway): centre pool bright,
  edges ~27%, corners dark. 5.6s loop + a brightness flicker on the
  lit layer (filter animates everywhere incl. iOS as a guaranteed
  visible movement fallback).
- shadows: offsets up (min 1.5%, 0.115/dist), scale 1.07, and the
  revealed slice dims to brightness .7 (dice ellipse .72) at FULL
  opacity — reads as shadow against both lit and unlit table.
- separation solver: perspective baked into widths first, then 7 relax
  iterations in width-pct space (min dist 0.42*(wA+wB), coins exempt —
  they pile), margins/band clamped each pass. Audit over 50 seeds:
  0 buried pairs, 0 band violations, worst ratio 0.96, 7-10 props.


## P84b — match screen never scrolls (done)

.screen ships overflow-y:auto by design (other screens can scroll);
the breathing shadow layer (scale about 50%/44%) started poking a few
px past the bottom, which made the match screen scrollable on phone.
#screen-match now forces overflow:hidden — everything lives in one
screen space, any sub-pixel animation overflow is clipped.

## P85 — LAST ORDERS safety net + light/shadow crank (done)

Denis hit a room with all four GONE HOME, 0 points, boss locked, and
nothing happening. The mechanic exists (_checkNightFail: all seats
spent + short of the boss = heart pays, roster re-rolls, LAST ORDERS
splash) and the live loss path does settle it (verified by repro) —
his run was stuck from stale state. Fix: _checkNightFail now ALSO runs
at room render (initTierScreen, right after _ensureNight), so any
stuck run settles the moment the room shows. Verified by forging the
exact stuck state: heart 3->2, night re-rolled, splash up.

Visual crank (both were too subtle on device):
- light pool: box 118%x112%, stops 18->66 — bright heart ~10% around
  centre, sides/corners properly dark; flicker brightness .93-1.09;
  positions per keyframe. shBreath up to 1.05.
- shadows: revealed slice at brightness .45 (dice ellipse .5), offset
  min 2.2% / 0.15*dist, silhouettes 1.10 — sharp and unmissable.

## P86 — candlelight + prop shadows rebuilt on canvas (done)

CSS masks never rendered on Denis's iPhone (two crank rounds changed
nothing) — both effects now run on canvas compositing, no masks:
- #matchPlate is the LIT table (base) with the brightness flicker
  (plain filter keyframes — safe everywhere).
- #matchDark canvas: UNLIT table drawn cover with a soft breathing
  ellipse punched out (destination-out radial gradient, centre ~50/44,
  sway + radial scale from layered sines). ~24fps rAF loop while the
  match screen is active; single static draw under reduced-motion;
  self-stops when the screen deactivates.
- #shCanvas (inside the breathing #matchShadows div): per prop,
  silhouette png -> source-in unlit slice -> source-atop dark tint,
  stamped rotated at its radial offset. Drawn at dress/resize.
Dice keep the CSS bg-reveal ellipse (no masks involved).
Pixel-verified via getImageData: pool centre alpha 0, edges unlit
opaque, 143 opaque shadow samples across 8 stamps.

## P87 — pool contrast + own-centre shadow wiggle (done)

- The pool never read because Table vs TableLit differ by only
  ~15-25%: the dark canvas now tints the unlit layer (source-atop
  rgba(10,6,3,.38)) before punching — real contrast. Pool is a soft
  screen-space CIRCLE (rx .58W / ry .30H) breathing on radial scale,
  sway trimmed.
- Shadow offsets reduced to hug the props (min 1.1%, .07*dist).
- The CSS scale on #matchShadows dragged the baked texture out of
  alignment — removed. The wiggle is in-canvas (~12fps, same rAF loop
  as the candle): each silhouette scales about its OWN fixed centre
  (1±3.5%) with intensity pulsing in sync (alpha .55±.09); the
  revealed slice is sampled in screen coords each frame so the texture
  never slides. Temp canvases cached per job.
Pixel-verified at two flicker phases: same-pixel texture constant,
boundary alpha 247->167, opaque count 227->215 (shape breathes).

## P88 — shadow texture pixel-aligned + painter's order (done)

- The stamp rotation was rotating the revealed table slice with the
  silhouette (plank lines tilted against the base). Rotation now lives
  in the MASK SHAPE only: silhouette drawn rotated into a square tmp,
  unlit slice composited axis-aligned in screen coords, tmp stamped
  unrotated. Verified: shadow pixel == tinted base pixel (delta <=1).
- Painter's order: props sorted by visual base line (y + height)
  before append — further/higher sits below closer/lower; shadows
  stamp in the same order.

## P89 — one flicker signal, physically linked + faster (done)

f = candle flare drives EVERYTHING now: pool radius (+/-16%), plate
brightness (+/-10%, set from the loop — the desynced CSS candleBreathe
is gone), shadow silhouette scale (+/-5%), shadow darkness (alpha
.60+/-.12) and a push (+/-0.8%) along each shadow's own offset
direction — flare = brighter light, bigger pool, bigger/darker/longer
shadows. Flicker ~1.75x faster; unlit tint deepened to .46 and pool
tightened (rx .52W / ry .27H) so the effect lives on the visible
table. Verified at opposite flare phases: ring alpha 88 vs 117,
shadow footprint 248 vs 230, avg darkness 42 vs 58.

## P90 — gentler pool, hugging shadows, radial blur (done)

- pool scale amplitude halved (+/-8%).
- shadow offsets down again (min 0.7%, 0.045*dist) — they hug the
  props.
- radial blur on shadow rims (Denis asked): solid core + 8 low-alpha
  ring stamps feather the silhouette edge; fringe radius grows with
  distance from the light (0.4+0.02*dist, cap 1.6%W) — nearer shadows
  crisper, far ones softer. Pure drawImage accumulation (ctx.filter
  blur is not iOS-safe). Verified: 170 fringe samples vs 575 solid,
  per-prop radii 1.34-1.6.

## P91 — props dim by the pool falloff (done)

Props now sit in the same light system: each one takes a brightness/
saturate dim from the SAME radial falloff as the table pool, evaluated
at its centre — on a BIGGER circle (rx .75W / ry .39H, cropped at the
sides) so only true edge/corner props go properly dark (floor .55).
Breathes with the flare (same f, updated with the shadow tick, .12s
filter transition smooths the steps). Verified: corner props ~.65-.68,
props nearest the pool ~.80.

## P92 — flicker dark-dips clamped + wider prop-light circle (done)

- Table flicker no longer dips dark: plate brightness clamps the dim
  side (1+0.08*max(f,-0.3) -> range .976-1.075, was down to .90) and
  the pool contracts less than it flares (f floored at -0.4 for radii).
- Prop-shadow circle cheated larger than the table's (rx .95W /
  ry .50H, was .75/.39): props now sit ~.74-.90 brightness — only true
  corner props read as shadowed.

## P93 — dice shadows match the props' look (done)

The match-dice shadow was a 0.9x0.29 ellipse hidden behind the die.
Table mode now swaps in a cube-sized footprint (1.02x0.88 of the die,
border-radius 26%) revealing the darkened table (brightness .5) with a
soft rim (plain blur(2.5px) — iOS-safe, no masks), nudged radially
away from the light centre (2-6px, distance-scaled + a small fixed
drop — subtle, dice live near the centre). Geometry restores to the
old ellipse off-table (offer screen unchanged). bg slice re-aligned to
the new rect per frame.

## P94 — dice shadows: true silhouette, breathing (done)

The DOM ellipse never matched the cube and sat frozen at rest (only
physics redraws touched it). Match dice now hide the DOM shadow; a
dedicated canvas (#dsCanvas, redrawn every candle tick ~25fps) stamps
each die's TRUE silhouette: the 8 cube corners projected through the
same rotation chain as the faces (D3.rotv; validated hull == rendered
face union exactly), convex hull filled as the mask -> unlit table
slice -> dark tint, small feather ring, radial nudge (2-6px, near the
light so barely spread) + flare push/scale/alpha from the shared f.
Follows rolls (redraws off D3.list each tick, shrinks with height);
offer-screen dice keep the original ellipse.

## P94b — dice shadow fringe widened (done)

The dice feather ring was 2.2px — too tight to read as the props'
two-layer handmade look. Ring radius now max(4, size*0.1) (~4.6px on
match dice): fringe/solid ratio 0.36, matching the props (~0.30).

## P94c — dice shadows tucked under, top-down (done)

Silhouette squashed vertically (y*0.72 — ground shadow seen from a
higher light), radial nudge halved (max 3.5px) and the base drop
trimmed (10px + 0.14*size) so the shadow sits directly underneath the
die, peeking out at the base instead of hanging low.

## P95 — yield gating per turn + no lingering totals (done)

- G._anyPlayerRoll was set on the first roll of the MATCH and never
  reset, so YIELD greeted every later turn before rolling. startPTurn
  now resets it — yield earns its place per turn.
- The floating +N selection total lives in .dice-area, which
  clearRow() never touches — it survived bank/yield into the NPC turn.
  _renderSelTags([],0,true) now fires at all three bank commit sites,
  in endPTurn and at startPTurn.

## P96 — patron colour system (done)

- Purple frames ONLY on the handicap/sealed seat; the other seats
  cycle green/blue/red distinctly (index skips the sealed slot; the
  card builder and launchSeat share the formula).
- The seat colour follows the patron into the match as --patCol on
  #screen-match (FRAME_COL sampled from the bg_ art: green #46503c,
  purple #503c46, blue #3c505a, red #6e463c):
  - NPC kept dice: green box outline replaced by the die-shaped
    silhouette glow (same engine path as the player's selection,
    .oppkeep recolours it via --patCol); all four un-keep paths
    updated.
  - the dark circle behind the patron portrait ring takes the colour.
  - match dialogue text takes the colour.
  Boss matches clear the var and keep the defaults.

## P97 — dice concept pass: top glow, side wash, grounding (done)

Match dice match Denis's concept:
- shadow flatter (squash .55) and lighter (alpha .45+.09f).
- the TOP face (most lit) gets brightness x1.1 + a tiny warm glow
  (drop-shadow, no url — iOS-safe).
- side faces get a faint wash of the base surface colour (#f0d8a8
  sampled from bone_1, opacity .24, inherits the material tint since
  it lives inside the tinted face) to tone down their pips, plus a
  from-below gradient in the shadow colour (rgba(30,18,10,.4) -> 0 at
  55%) that sits them on the table.
Two new per-face layers (.d3wash/.d3grnd) — zeroed outside match
dice (offer/chips/kept unchanged, verified).

## P98 — YIELD retired; bank auto-passes (FARK_UI_SCREENS_BRIEF in) (done)

New brief docs/FARK_UI_SCREENS_BRIEF.md (owns everything outside the
match screen; acceptance: the string "YIELD" appears nowhere in UI,
primary CTAs move to a two-line verb+caption pattern — Denis will
paint bigger button bodies with caption room; using existing art
until then).
For now: the YIELD button is gone (element, CSS, setBtns toggle,
yieldTurn). Banking hands the dice over automatically ~900ms after
the bank feedback (showYieldButton keeps the 'yielding' phase beat
and the DLG triggers via handleYield; guarded against stale G).
Mid-turn forfeit lives only on pause/X. Yield.png art unused for now.

## P99 — shadows unsqueezed, opaque dark kept/bust dice, BANK caption (done)

- dice shadows back to the full projected silhouette (vertical squeeze
  reverted), tucked a bit more under the die (drop 7px + 0.10size);
  top-face glow toned down (x1.06, glow .3 at 0.05size).
- kept (committed) and busting dice NEVER go translucent: engine dims
  per face (committed: saturate .6 brightness .62; bust/bust-wipe:
  saturate .25 brightness .55 — iOS-safe, host filters over 3D
  children are ignored there). Redraw triggers at all commit sites
  (x3), bust sites (x7) and the kept-tray wipe (x3). Opacity rules
  scoped to legacy non-d3 dice only.
- BANK follows the brief's two-line CTA: verb (BANK / BANK TO WIN) +
  caption "+N" showing the live turn total incl. selection; caption
  hides when there is nothing to bank. (Lesson: the P99 script died
  mid-run before its file write — P99b/P99c re-applied; always check
  the write happened.)

## P100 — NPC glow rim-only + last translucency holdouts (done)

- The NPC kept-dice halo (blurred patron-colour layer) read as a
  TINTED SHADOW under their dice — gone. The keep marker is now the
  crisp die-shaped rim only; the canvas shadow underneath is the same
  neutral one the player's dice get.
- Remaining translucent dice states converted to opaque darkening:
  .die.scatter (was opacity .6), .die.opp-scatter (was .6), kept-tray
  pile (was .65 + host filter). Engine dim now also covers
  scatter/opp-scatter (level 2) and .kept-tray/#keptTray ancestors
  (level 1), with redraws at the scatter sites and a sweep in
  refreshKeptTray. Legacy 2D dice keep the old opacity via :not(.d3on).

## P100b — BANK TO WIN fixed (done)

Denis never saw BANK TO WIN because _selPts() always returned 0: it
was written for an old scoreSelection API that returned
{valid,total}, but the current API returns a plain number — so the
winning check only counted COMMITTED points, and the common flow
(select dice, bank directly) never triggered it. _selPts now handles
the numeric return. Verified: selection alone crossing the target ->
verb BANK TO WIN, wide gold plate, caption +N.

## P101 — boss-ready dressing (done)

- activated win diamonds get a bright gold 4-way outline + warm glow
  (drop-shadows, iOS-safe).
- boss bar pulled lower (top 52.5%, was 47.8); ready text split into
  two lines: "GROG IS WAITING" / "a heart at stake".
- the boss name pulses a warm glow when ready (bossNmGlow 1.7s), on
  BOTH the bar line and the big screen title (#ptBossName.rdy).
- boss-ready radial vignette (#ptVign, z5 — under HUD z8, over room
  art + seats): ellipse centred on the boss face (50%/24%), eases in
  on screen entry (opacity+scale, 1.4s). Absent when not ready.


## P101b — waiting line: beige, no glow, no stake line (done)

"GROG IS WAITING" is now plain cream (#f0e3c6) with the standard
emboss shadow — no glow, no red (it fought readability). The
"a heart at stake" sub-line is gone (the stake still labels the
CHALLENGE CTA in the boss peek, per the brief). The big GROG title
keeps its ready pulse; diamonds keep their bright outlines.


## P101c — the waiting block launches the boss flow (done)

The CHALLENGE path existed only behind the small GROG title text; the
waiting bar swallowed no taps (pointer-events:none). When ready, the
whole block (diamonds + GROG IS WAITING) is now the tap target ->
boss peek -> CHALLENGE (2 taps, per the brief), with a press squash.
Verified: tap opens the peek with the CHALLENGE CTA.


## P101d — IS WAITING under the title, READY button (done)

"IS WAITING" now sits as a cream line under the big GROG title
(ready only). The diamond bar is back to non-interactive; below the
diamonds a READY button (Button_thick_red plate, 44cqw, press squash)
opens the boss peek -> CHALLENGE. Verified end-to-end.

## P102 — the painted STORE, dice tab (done)

Layer stack (Art/Assets/Store, all 1080x1920 pre-positioned):
Store_back full-bleed cover behind a width-fit bottom-anchored stage
(aspect locked, container-type:size) holding char -> mid -> tabs ->
front -> goods. The innkeep rises .8s ease on screen entry only
(_stFresh flag; buys re-render without replay).
- stock: family dice rolled in for the night claim the 4 stands first
  (mundane pad leftovers); iso value-up chips on the measured stand
  centres, prices inked on the baked parchment tags (slight per-tag
  tilts). Unaffordable: chip dims via engine stdim class + faded ink.
  Tap stand or tag -> existing inspect sheet -> BUY (stock/gold logic
  untouched).
- tabs DICE|ENCHANTS: active full size/brightness, inactive scale .85
  darkened, scaling about each tab's baked bottom-centre; labels are
  font-layer (no baked text). A pointer-capture strip across both
  supports tap AND thumb-slide, switching in place (the strip survives
  the flip, so one drag can cross back and forth). Enchants tab clears
  the counter — layers pending from Denis (enchant flow temporarily
  not reachable from the shop skin).
- HUD: painted hearts + gold plate (room kit); BACK / LOADOUT thin
  button plates bottom corners.

## P102b/c — store polish (done)

- stand dice up to 88% of the stand (was 60), with the engine's sharp
  offset silhouette shadow (data-shadow attr -> _d3Shadow -> dieShadow
  at chip creation — no post-scan race).
- prices: centred on their tag anchors (translate(-50%,-50%) before
  the tilt), bright cream ink with emboss, 3.9cqw.
- innkeep scaled 1.18 about (48.8%,44%) — grows up/out from behind the
  counter; entrance rise keeps the scale.


## P102d — price ink + innkeep size (done)

Prices lose their text shadow (flat ink per art rules); unaffordable
prices go dark brown (#4a3020) instead of faded cream. Innkeeper up
to 1.34x (same behind-counter origin, rise preserved).


## P102e — store never scrolls (done)

A legacy #gbShop rule later in the sheet (overflow:auto, grey #4a4a4a
background) was overriding the store rule — the scaled innkeep's
transform overflow made the screen scrollable and the grey band
showed below the stage. Legacy rule now carries the store values
(overflow:hidden, #120b06, container-type:size). The stage stays
locked 9:16 bottom-anchored; taller screens get the cover back-layer
above it, squarer windows clip.


## P102f — bottom band fixed (done)

Denis's Firefox top-anchored the store stage (bottom:0 with an
aspect-ratio-derived height did not resolve there; Chromium was
fine), leaving the 16:9 shortfall as a flat band at the BOTTOM. The
stage now sets BOTH dimensions explicitly (width min(100cqw,
56.25cqh), height min(177.78cqw,100cqh)) — no aspect-ratio
dependency, bottom anchor holds everywhere; the shortfall sits at
the top where Store_back covers it with matching shelf art.


## P102g — store tweaks (done)

Gold amounts drop the g suffix (HUD + price tags); stand-dice
silhouette shadows removed (did not render); nav buttons are icon
buttons now — Icons/back.png (left) and the room's Icons/pouch.png
(right, loadout), 13.5% wide.


## P103 — store die focus = the offer treatment (done)

Tapping a stand (or its price tag) now works like picking the first
die: the die spring-zooms to centre stage (same projection + easing,
K=2.3 to 50%/27%), the store dims behind a radial scrim (other
stands/prices fade), per-material sparks rise from the die, and the
focus panel shows name / faces / description with BUY (stake-labelled
per the brief; NOT ENOUGH state dimmed) and BACK. Buying re-renders
the shop (st-focus reset in render); BACK springs the die home. The
old bottom-sheet inspect (_gbDieInspect) is no longer wired from the
stands.


## P103b — focus polish (done)

- store blurs + darkens behind the focus (blur 6px brightness .5 on
  all stage layers + labels, .35s ease; scrim deepened .5/.88) — the
  zoomed die stays sharp (goods layer exempt).
- BUY text fits: 3cqh nowrap, NOT-ENOUGH state 2.5cqh.
- the focused die hovers like the offer dice: engine hover flag +
  ramp on focus (float bob + slow pitch/yaw drift via D3.start loop),
  restored to the exact iso pose on BACK.


## P103c — focus stacking + text room (done)

- the scrim lived on #gbShop while #stStage is its own stacking
  context (container-type layout containment) — the whole stage incl.
  the zoomed die rendered UNDER it, darkening the die. Scrim now
  mounts INSIDE the stage: zoom z60 > scrim z50.
- the focused die sheds the unaffordable stdim for the inspection
  (restored on BACK); stdim now rides onto the die host at chip
  creation so the engine dim actually applies on the stands.
- BUY plate 84% wide, text 2.9cqh (NOT-ENOUGH 2.1cqh) — label sits at
  under half the plate width.


## P103d — stand dice always bright (done)

The unaffordable engine dim (finally rendering after P103c) made the
whole counter read dark — dropped. Dice on the stands are always full
brightness; affordability lives in the price ink alone (cream vs dark
brown). The stdim plumbing stays dormant in the engine/scan for
future use.


## P103e — full-cover focus scrim + smaller coin (done)

- second scrim: full-screen flat rgba(10,6,2,.78) mounted on #gbShop
  UNDER the stage (covers the top strip the in-stage scrim missed);
  the in-stage scrim uses the same flat colour so there is no seam,
  and the zoomed die still stacks above (z60 in the stage context).
- gold chip coin: Icons/coin.png (the game coin), height 58% top 21%.


## P103f — one scrim, no double-darkening (done)

The two-scrim approach double-darkened the stage area (both layers
overlapped there) with a seam at the stage edge. Now a SINGLE scrim:
in-stage (so the zoomed die stays above it, z60>50) but oversized
(-60cqw sides / -100cqh top / -20cqh bottom, stage has no clip;
gbShop clips at the screen) — one flat rgba(10,6,2,.82) layer covers
the entire screen uniformly. Coin in the gold chip +10% (64% height).


## P103g — sparks emanate from the die (done)

Spark spawn offsets were the offer screen's fixed +/-46px — on the
tiny stand chip scaled 2.3x they scattered across the screen. Offsets
are now relative to the chip (+/-40% of stand width, drift 55% of
that): the particles rise from the die's own footprint and scale with
the zoom.


## P104 — Beda breathes + coloured die names (done)

- body-level letter-spacing .045em: every JMH Beda text without an
  explicit tighter/looser value inherits it (focus descriptions,
  tags, dialogue...). Store focus name .09em, prices .07em.
- die name in the store focus: first letter capitalized, coloured
  with the die's particle colour (D3.SPARK[mat].c — e.g. Amber in
  #ffb84d).


## P105 — focus polish + unified back arrow (done)

- hyphenated words never split across lines: focus descriptions wrap
  them in nowrap spans (store + offer), hyphens:none besides.
- store HUD (hearts/gold) and bottom nav icons hide while a die is
  focused, restore on back.
- name + faces higher (panel top 39.5%) with real air before the
  description (3.2cqh).
- ALL back actions use Icons/back.png: store focus + offer focus BACK
  plates replaced by the arrow icon (11% wide, press squash); the
  store screen nav already used it.


## P106 — one HUD everywhere (done)

Hearts + gold chip are now IDENTICAL on room and store (verified
pixel-identical rects): the store adopts the room geometry (hearts
left 3.6% top max(1.8%,env) width 27% img 30%; gold right 3.2% width
27.5%, amt 2.8cqh #f3dfa6), anchored to the full screen box (the old
#stHud strip had zero height so % offsets collapsed). The coin is the
STAR coin (Icons/coin.png) on BOTH — the room swapped off the mockup
coin — and both amounts are bare numbers.

## P107 — shop TRADE flow (brief 3.9 v2: six dice, no reserve) (done)

Buying is a trade now. The focus screen pins YOUR SIX as a slot row
at the bottom (iso chips, faint-outline slots, caption states the
stake: "BUY — N · drag onto the die it replaces"); drag the zoomed
shop die onto a slot — hover highlights it, the DROP is the purchase:
gold paid, stock down, the outgoing die AND its enchant mark gone for
good (no trade-in gold, bet law), the new die lands in that exact
loadout slot, back in the shop. Miss-drops spring the die back to the
focus pose; unaffordable keeps the NOT-ENOUGH plate with no dragging.
The old BUY-to-reserve path is no longer reachable from the shop
(diceInv/famDieStash remain for the loadout until the reserve is
retired wholesale). Updated FARK_UI_SCREENS_BRIEF filed in docs/.


## P109 — win diamonds on every patron panel (done)

The panel diamonds were sealed-only; now EVERY patron shows their win
value under the name: one diamond normally, two on the sealed seat
(three with Marked Table), heat-tinted by how close that win brings
you to the boss. Verified: normal panel 1, sealed panel 2.


## Brief update filed (2026-07-23): SHELF -> FEATS WALL

New revision of FARK_UI_SCREENS_BRIEF.md filed. Delta vs previous:
- The trophy SHELF is CUT. Replaced by the FEATS WALL: earned feats
  hang as small keepsake trinkets on iron nails (the nail = visual
  signature AND the code placement grid). Only earned feats render +
  a tiny tally (12/24). Tap a pin -> anchored tooltip popover (name +
  one-liner), tap-away dismiss. No list view, no locked entries.
  The game s only meta surface.
- Title bottom corner: the shelf -> the wall (feats).
- Barred/Run-won: feats earned this run get pinned LIVE one by one;
  button TO THE SHELF -> TO THE WALL.
- Assets: trophy sprites cut; instead feat pin markers (one generic
  pin + per-feat mini-emblems, batchable).
Not acted on yet — lands with the loadout/badge-case rework.

## P110 — painted SHELF/LOADOUT pass 1 (done)

famLoadoutShow rebuilt on Art/Assets/Shelf/shelf_bg.png (2160x3840,
store stage pattern: cover backdrop + width-fit bottom-anchored 9:16
stage, coords in art %). The greybox loadout (satchel/stash/sell +
trophy shelf) is retired per the brief.
- BADGES in the wooden case: claimed tells wear their tier-boss's
  brooch (mapped by boss NAME — TIERS[i].boss.key is the class name
  like 'drunkard', names are GROG/MABEL/...), spread across the blue
  felt base (y 53.6%). Tap -> anchored tooltip (#loTip: badge name +
  rule one-liner), tap-away dismiss. Debug flag lays out all nine.
- CARDS: equipped fcards as placeholder 3D cards (face + offset dark
  edge, family-colour trim, icon+name+tier pips) centred on the three
  marked slots (18.4/50.2/77.1 x 67%). Visual pass later.
- DICE: your six as iso chips over the painted rail (x 14.7..84.4,
  y 81%, 12% wide). Box art will be emptied later.
- unified HUD (shared CSS with #stHud) + back arrow. Feats wall wired
  when Denis's pin art lands.

## P111 — feats wall (done)

Earned feats hang as Denis's trinket sprites on the dark wall: 5-col
grid (x 12/31/50/69/88, rows y 7-29%), height 5.6% each, tap -> the
shared anchored tooltip (feat label + one-liner), tiny tally top-right
(N/24). 12 confident art->code mappings (Barehands=naked_run,
Bookkeeper=five_banker, CleanNight=no_busts, Death&Taxes=beat_corvus,
FirstBlood, HighRoller, LastManSitting=survivor, LongRoad=persistent,
SecondWind=comeback, Teetotaller=beat_grog, TheCollector=
card_collector, ThreeTorches=hot_storm); the other 12 images await
their feats (debug flag previews all 24 on the wall). Only earned
feats ever render live, per the brief.

## P112 — seamless wall + always six dice (done)

- the top-strip cover rendered the wall at a different crop/scale
  (visible seam + "weird wall"). Replaced by an in-stage mirrored
  extension: the same bg flipped vertically sitting flush above the
  stage — vertical plank columns continue through the join.
- Denis's save had a 4-entry dice array (older builds): _famDiceMigrate
  now pads short arrays back to SIX bones (dieEnch in step) on every
  run, famLoadoutShow runs the migration, and the rail render loops
  all six slots with a bone fallback. shelf_bg updated by Denis
  (empty rail) committed along.

## P113 — shelf remap for the extended art + debug showcase (done)

Denis extended shelf_bg himself (2160x4476): stage aspect updated
(48.26cqh / 207.22cqw), mirror extension kept for still-taller
screens. Remeasured: feats rows y 9-39, badge case fills BOTH felt
rows when >5 badges (lid 50.3 / base 59.3, up to 5+4), card slots
19.6/50.5/78.5 @ 71.5 (aspect 215/260), dice rail y 83.5
x 13.8-84.8. The 0/24 tally is REMOVED. Debug flag now ALWAYS shows
all 24 feats + all 9 badges (showcase); live players see earned only.
Also answered: the 4-dice save came from older builds — matches
always roll six (materials pad with bone), so play felt normal; the
P112 migration heals the save on shelf open.

## P114 — shelf feel + dice diagnostics (done)

- sharp offset silhouette shadows under feats and badges (drop-shadow
  0.7/0.9cqw, zero blur).
- feats bigger (6.2%) and hung by hand: deterministic jitter (+-3%
  x / +-1.6% y from index sines) + tilt (+-7deg) off the nail grid.
- badges bigger (5.4%) and centre-packed (12.5% step about the row
  centre; 5 lid + 4 base under debug).
- hsdebug badge now reports "dice save:N chips:M" — the pane renders
  6 chips from any save (P112 pads + 0..5 loop), and the committed
  shelf_bg rail is EMPTY, so if Denis still sees 4 painterly dice his
  local art copy has them painted in (OneDrive divergence suspected).

## P115 — consistent trinket scale + wall vignette (done)

- badges: 4 lid / 5 base; every badge AND feat renders at one common
  scale from its natural pixel size (baked size maps; height-
  normalizing had made wide pieces loom and tall ones shrink).
  Verified: implied scale uniform to rounding.
- very subtle top vignette over the wall (linear fade .38 -> 0 over
  the top 34%, above the trinkets) so they bed into the wood.
- hsdebug dice line fixed (S is lexical, not window.S) + reports
  converted chips: "dice save:N chips:M conv:K" — next screenshot
  settles whether Denis's 4 visible dice are painted into his local
  shelf_bg copy.

## P116 — shelf tune + chip-size heal (done)

- badges: step 14% (more air), base row raised to 58.9% and common
  scale eased to .0126 — tallest brooch bottoms out at 61.6%, inside
  the base felt (~61.8%).
- feats: brickwork stagger (rows alternate +-2.8%) + x jitter +-4.5
  on tighter columns (14..86) — no more vertical alignment or wide
  gutters.
- chips: scan runs post-layout (double rAF + 250ms fallback) and any
  chip converted at zero size is rebuilt — fixes Firefox's invisible
  conv:6. CONFIRMED via the debug badge: Denis's four visible dice
  are PAINTED IN HIS LOCAL shelf_bg (repo copy is empty; his side
  needs a re-export/flatten).

## P116b — THE FOUR-DICE MYSTERY SOLVED (done)

The art was innocent. .d3chip's own rule (later in the sheet, equal
specificity) beat .loDie's position:absolute with position:relative —
the six chips FLOWED INLINE, each 12% wide, PLUS their left offsets:
cumulative drift (13.8/40/66.2/92.4/118.6/144.8), dice 4-6 off
screen, four visible evenly spread. Chrome AND Firefox alike; my
earlier checks read style.left instead of RENDERED rects (lesson:
verify getBoundingClientRect, not intent). Fix: #loStage .loDie
{position:absolute !important;left:0;display:block}. Verified
rendered: 13.8/28/42.2/56.4/70.6/84.8, all on screen.

## P117 — shelf round 3 (done)

- rail dice 13.5% + engine silhouette shadow (data-shadow, per-face).
- wall vignette extends past the screen top (covers the mirrored
  strip; band .38 fading out by the bottom of the wall).
- badge base row up to 58.2; debug badge order = boss order
  (grog..ambrose, house Tankard last); real earns follow claim order.
- feats scaled up (FK .0155), tighter columns (step 17), and a
  two-axis separation: per-row horizontal + per-column vertical
  passes with REAL natural-px widths/heights, min margins 1.2%/0.7%,
  clamped to the wall band. Audited on rendered rects: 0 overlaps
  across all 24, lowest bottom 43.2% (above the case).


## P118 — bigger badges (mug boosted) + bigger higher dice (done)

Badge scale up (BK .0136) with a per-badge multiplier map — the ale
mug (smallest art) gets 1.28x so it holds its own (5.47% vs boot
5.82%); all badges stay inside the base felt (max bottom 61.1%).
Rail dice up to 15% wide and raised to 82.6%.


## P118b — grounded die shadows + softer vignette (done)

The engine dieShadow offsets were rim-like (dx .05 / dy .11): now
dx .04 / dy .22, alpha .5 — the silhouette sits clearly UNDER the
cube (verified on visible faces: 1.1px/6.2px at rail size). Wall
vignette halved (.38 -> .19).

## P118c/P119 — feats clear the case, vignette softer, die shadows done right (done)

- feats rows raised (7..38.2, clamp 41.2) — lowest bottom 41.4%,
  clear of the badge case.
- vignette down again (.19 -> .11).
- die shadows: per-face drop-shadows fundamentally bleed on a cube
  (each face shadows onto its neighbours — "passing through").
  Rebuilt as a SILHOUETTE CLONE layer (the selection-glow machinery):
  solid #241610 clones of the visible faces behind the die, offset
  (size*.05, size*.17), alpha .45 on the CONTAINER so overlapping
  clones never seam. iOS-safe (transforms+opacity). Verified: clone
  layer present, zero per-face shadow terms.

## P120 — parchment tooltips + real texts (done)

- #loTip wears Icons/tooltip_box.png (100% stretch), dark ink, name
  in warm brown, centred.
- badge texts: every brooch names its boss and quotes his rule from
  the tell data ("Grog's badge · LAST CALL — ..."); the Tankard
  explains the sealed seat. Same in debug and live.
- feat texts: 12 authored one-liners for the not-yet-coded images
  (For Keeps, Full Bloom, Green Thumb, His Own Medicine, No Claim,
  Omens True, Own the Night, Powder Monkey, Slow Boiled, Sticky
  Fingers, Twice Saved, Wish Granted) — doubling as the design hooks
  for those future feats; debug preview shows real text for all 24.


## P121 — one-line titles, Metamorphous body, helm boost (done)

- tooltip titles never wrap (nowrap; the plate grows to fit).
- tooltip BODY text set in Metamorphous (OFL, bundled locally at
  assets/fonts/Metamorphous.ttf — works file:// and on Pages; titles
  stay JMH Beda). One selector away from rolling it to other body
  texts if Denis likes it.
- BMUL: TheDentedHelm 1.15 joins the tankard boost.


## P122 — Macondo body + interleaved feat shapes (done)

- tooltip body font switched Metamorphous -> Macondo (bundled at
  assets/fonts/Macondo.ttf; both files kept so swapping back is one
  selector).
- feat display order hand-shuffled so similar silhouettes (the dangly
  spoon / chain die / cork trio, plus the narrow jar and lantern)
  never share a column; right-edge clamp tightened (94) so no gutter
  column forms. Verified: trio scattered across rows/columns, still 0
  overlaps.

## P124 — shelf die focus + store tray art (done)

- tapping a rail die on the shelf opens the shop-style focus,
  inspect-only: spring-zoom to centre (translate keeps the -50% base
  so the math holds), flat oversized scrim inside #loStage (under the
  z60 die), shared panel styles (#loFocusPanel comma-extends the
  store's), name in particle colour + faces + desc, hover float,
  BACK arrow; HUD/back/tooltip hidden during focus.
- store trade row wears Art/Assets/Store/dice_row.png (wooden tray,
  1200x274): slots are invisible 14% hit zones over the six notch
  bays (13.3..85.8), hot slot keeps the gold ring.

## P125 — tap-lift on trinkets + nudges (done)

Tapping a badge or feat lifts it toward the camera: scale 1.2 (feats
keep their tilt via --jt), the ground shadow slides further away and
fades (offset x2, alpha .45 -> .2) and a gold alpha-silhouette
outline appears (4-way 1.5px drop-shadows around the alpha, ordered
BEFORE the ground shadow so the outline hugs the art, not the bbox).
The lit state rides the tooltip (applied in _loTip, cleared on
tap-away/hide). Nudges: Bookkeeper +5, StickyFingers -5,
HisOwnMedecine -5.

## P126 — the feat ceremony (done)

When a feat with art unlocks (post-match drain) or waits unpinned on
shelf entry: full-screen scrim, the trinket huge (24cqh) with the
amber alpha outline + spring entrance, rising gold particles (nrSpark
reuse), feat name / flavour / +renown, and a PIN IT plate
(Button_thick_green). Tapping PIN flies the trinket (FLIP clone) onto
its exact wall spot — the hidden wall img then fades in — or, away
from the shelf, off toward the corner. One ceremony per feat ever
(S.featsPinned in the save). Artless feats keep the old golden
splash. FEAT_ART hoisted global. Gotcha found: the desktop phone
frame reroutes body.appendChild into #phoneShell whose transform is
the containing block for fixed — flight coords must subtract the
shell origin. Both the fade-in class and the flight destination have
timer fallbacks beside rAF.

## P127+P128 — multi-feat ceremony + wall wiring fixes (done)

P127: feats earned together share ONE ceremony — trinkets in a row
(smaller as count grows: 24/17/12.5cqh for 1/2/3+, staggered pop-in),
name captions under each, FEATS OF THE NIGHT heading, summed renown,
PIN THEM — and on pin they all fly to their wall spots in a 110ms
stagger, each wall img revealing as its flight lands. #fcOv is now
container-type:size so its cq units track the phone frame on desktop.

P128 (from adversarial review): (1) evaluateFeats now writes
S.featsDone (lifetime record) — before, only the five _famFeats
family ids ever landed there, so the wall was empty in production and
the ceremony always flew to the corner; this also arms the shelf
recovery net (app killed mid-ceremony -> re-offered on shelf entry).
(2) Repeat earns in later runs (feat already pinned) fall back to the
classic golden splash instead of silently nothing. (3) opacity joined
the base .loFeat transition list — the fade lived only on .unpinned,
whose list stops applying the moment the class is removed.

## P129 — debug: hearts tap seeds fresh feats (done)

With debug on, tapping the HEARTS in the room seeds three
just-won feats (First Blood, Untouchable, Comeback: featsDone set,
pins cleared) — open the shelf and the FEATS OF THE NIGHT ceremony
plays. Re-tap to re-arm and watch it again. The ceremony now also
runs under the debug flag: the 24-feat showcase wall carries real
unpinned state for earned ids, so the flights land properly there.

## P130 — painted cards, part 1 (done)

Denis delivered all 30 card faces (911x1298, family frame baked,
textless). assets/cards/<id>.webp = 456x650 derivatives (~60KB each,
1.7MB total; sources gitignored — Art/Assets/Cards/ stays local).
famCardArt(id,tier,opts) is THE painted card builder (face + roman
tier chip, tier I clean); famCardHtml wraps it with a name caption
(draft/panel upgraded for free). VANGUARD COLLAPSE per the updated
master brief: vanguard_f absorbs anchor_f/bookends_f (I first spot
+200 / II both ends +350 each / III both-ends 1200), _FAM_ALIAS
redirects stale ids everywhere, _famCardsV2 migrates owned copies
keeping the highest tier. Loadout slots wear the real cards; tap
gives the parchment tooltip (name+tier+rule).

## P131-P133 - painted cards everywhere + brief-v3 draft (done)

P131 draft: famOffer goes FAMILY-FIRST (pick the family by the 60/40
owned/outside weighting - dice and relics count as ownership via
famOwnedFams/_RELIC_FAM - then a card inside it; nights 1-2 50/50;
tavern ~12% of all offers). Offer tiles are painted; tapping one
opens famCardSheet (big painted card + rule + CLAIM). Slots full ->
_famReplacePick: painted replace picker, traded card gone, no
refund; cancellable before the tap. Satchel (finv) retired: the
migration equips into empty slots and sells the rest at 15g.

P132 match edges: player's three painted cards centred above the
buttons (spent = desaturated, Confession seal = dark veil, armed =
gold glow; tap -> sheet with uses-left + PLAY through famUse's
gating). Opponent cards are face-down CSS backs top-right (dark
parchment + family border + diamond motif - painted backs pending
art): telegraph = rise + red glow, Tamper-broken = grey + cross,
tap -> info sheet. Quicksilver/sleeve chips live in a small aux
stack bottom-left. The old #famRow monospace column is gone.

P133 peek: patron peek shows their painted cards (tap -> full
sheet). Boss peek unchanged - his hand is rolled at match start,
nothing to preview yet.

Gotcha relearned the hard way: bash heredocs eat backslashes even
with a quoted delimiter on this setup - the P133 first attempt broke
the parse gate; repaired via a Write-tool .py using &quot; entities
instead of escaped quotes in onclick attributes.

## P134 - patron panel wears their painted cards (done)

The room's character panel (#ptPanel) no longer shows blank cream
count-markers in #ptvFan: the patron's actual cards render as
painted minis (11.5% wide, same fan rotation math, tier chips),
tappable -> famCardSheet. When the seat is sealed and a fan is
present, the tell text drops to 59% so they never collide.

## P135 - the redone character panel (done)

New separate elements: SitDown_panel_bg (1117x2320, labels + row
icons + tray + divider baked), SitDown.png (blank gold plaque),
SitDown_coin/_diamond, close_x. Sheet re-tuned to aspect 1117/2320.
The shield window (#ptPort at 27.2/1.9/46/27.9) shows the SAME art
as the room tile - Frames/Patrons/<art>.png at 140% width over
bg_<color>.png cover - so the panel and frame are one object
(Commoners art retired). Rows: font-layer values at x57
(target 71.8 / stake 77.2 / pot 82.3 row centres), star-coin on
stake+pot. Dice ride the painted tray (19-81%, y61). SIT DOWN =
plaque + two gold diamonds + font label (dark ink on gold); X sits
on the bottom-right corner. Sealed: smoke hugs the shield top,
purple outline moves onto the patron inside the window. Fan/luck/
wins/trait re-zoned into the parchment (44.6/52.6/42.4/38.9).

## P136 - character panel round 2 (done)

Portrait + frame colour now truly BEHIND the plate (bg z2 > smoke z1
> port z0 - sealed particles rise over the colour, under the rim);
bg_<color> art is opaque only in its top 61%, so .pbg stretches 164%
tall to fill the shield. Trait seal + word are one centred row; name
6.2cqh. X hugs the corner (84.5/93.4/14.5). Dice 16.4% at top 60%
with the engine silhouette shadow and the shelf-style tap-to-focus
(_ptDieFocus: scrim + zoom K2.5 + shared focus panel; lucky die
shows its given name). Parchment stack moved up (tell text cleared
off the divider; fan-present drops it to 53.8). Quote/desc text =
Macondo. Row values right-aligned to the line ends. SIT DOWN wears a
solid #a77d53 drop shadow that flattens on press.

## P137 - character panel round 3 (done)

Shield colour stretched (110% x 180%, -3% top) so it reaches the
point - the art's transparent strip left a dark gap. Title + name on
ONE line (3.6/7cqh, nowrap, a touch lower); win diamonds moved to
the bottom of the portrait (27.4%, z3). Trait row gap 2.4cqh. Row
values #a95839 with fixed-width right-aligned amounts (8cqh) so the
coins stack vertically; coins 2.55cqh. SIT DOWN 3.6cqh #402d14 with
the diamonds flexed against the text (2.2cqh margins). Lucky-die
radial glow removed (read as a bigger die). Die focus stacking fixed:
.pt-focus lifts #ptvDice to z55 and dims the idle chips itself - the
scrim's stacking context was darkening the zoomed die.

## P138 - panel round 4 + the dice-size root cause (done)

Panel: name back to two stacked lines (small title), values #8a4630
nudged left, win diamonds 3.8cqh at 26.2%, single fan card stands
straight, NIGHT chalk to 4.4% (was touching the panel), debug chalk
tap seeds seat 0 sealed WITH cards (_fkSeedPanel). FOCUS LAW unified
across store/shelf/panel: object at 42% height, text panel top 53%,
scrim rgba(10,6,2,.9) full-bleed; idle chips/cards dim by brightness
(never transparency; the row lifts above the scrim and dims its own
idle members). Card focus in the fan (_ptCardFocus, K3.1, springy,
straightens the fan tilt, family-colour panel); shared _ptUnfocus.

THE DICE-SIZE BUG, root-caused: legacy .dtype-bone/iron/flint/lead
rules still put a 3px border-box border on a FRESH .die host; the
engine strips it later, but _d3InitHost measured clientWidth at init
=> classic materials sized 24/30 of their chip while borderless new
materials (lucky, starstone...) got the full width. Every d3chip
surface undersized classic dice. Fix: _d3InitHost sizes from the
enclosing .d3chip. Panel + shelf verified uniform.

## P139 - the new button kit (done)

Roles: GOLD (Panels/SitDown.png, ink #402d14) = primary CTA -
CONTINUE, KEEP DRINKING, TAKE IT (starter draft), PIN IT/THEM
(ceremony); RED (Button_new_01, cream text) = challenge/destructive
- READY, NEW RUN (both branches); CREAM (Button_new_02, ink
#6a5238) = neutral/disabled - the store's NOT-ENOUGH plate. Labels
framed by SitDown_diamond chips (.nbDmd). Aspect ratios per asset
(729/194, 936/265, 934/235). Button_thick_*/thin_* fully retired
from the painted screens; the character panel's bespoke plaque/X
untouched. Greybox sheet buttons (gbx) stay for their own dressing
passes.

## P140 - round 5 batch (done)

BUTTONS: gold plaque is panel-only again; everywhere else the two
new plates (red 01 destructive/challenge, cream 02 primary/neutral).
Title buttons 62% wide; all labels letterpress-embossed (no text
drop shadows). DICE: shelf chips 13.6%, store stand chips 80% (the
root fix had grown classics there); panel untouched. PANEL: values
#802c10; title line rides .5cqh lower; the name wears the portrait's
flat colour; win diamond off the frame (25%); patron -16% in the
shield; seal-word gap 1.5cqh; tell is one flowing line (title-case
small name + Macondo text); #ptPort is a SOLID colour now
(PT_BGCOL green #505c47 / blue #45555b / red #784a42 / purple
#5c4750). FOCUS LAW v2: all scrims rgba(8,5,2,.5) + backdrop
blur(6px) brightness(.55) (the starter-draft look); panel idle rows
dim brightness(.28)+blur(2px) to match. Card focus K3.6 with a
stable per-card wiggle; family word in family colour, rest muted
#cfc0a8; numbers get .num accents. GROG block to 8.4%. STORE:
prices straight, owned = engraved tally strokes under the tag
(.stTally, 4+diagonal for 5).

## P141 - family names + focus polish (done)

Patrons get a FAMILY NAME on the panel only (deterministic hash of
the given name over 24 cosy surnames: Thistledown, Bramblewick,
Copperpot...; name font auto-fits 7/5.4/4.4cqh by length; room tiles
keep the short name). Win diamond up to 23.8%. Card-focus wiggle is
now real (random each open, 1.6-4deg, never near zero, +-8px x);
the tier numeral left the meta line (the card's chip already shows
it). All three focus scrims darkened to rgba(8,5,2,.64); the panel's
lifted idle rows dim to brightness(.16)+blur(4px) to match the
backdrop.

## P142 - no titles, tell under name, focus text pass (done)

Panel: period titles removed from the panel; the win diamond(s) sit
where the title was (29.6%, above the name at 32.4%); the tell text
moved up under the name (38.6) with trait (43.6) and fan (47.8)
reflowed - the fan-dodge died with it. FOCUS SCREENS (store, shelf,
panel, starter): body text is Macondo bold (dropped the JMH override
that was shadowing it); the NAME renders ABOVE the object (-31cqh
off the text panel); the return arrow is the red X (close_x) on
focus returns only - screen-nav arrows untouched.

## P142e - one close icon everywhere (done)

Art/Assets/Icons/close.png (the round copper X, new) replaces every
close: the five focus returns, the character panel corner X, and the
rules/settings scroll X. close_x.png and the derived
close_focus.png are retired.

## P143 - wax seal rides the portrait corner (done)

The trait seal sits on the shield's bottom-right corner (64/26.4,
12.5% wide, tilted, solid offset shadow); the attached trait word is
gone from the flow - tapping the seal fades the word in beside it
(2.4s auto-hide, tap toggles, press scales the seal). The card fan
rose to 45.8 into the freed space.

## P144 - panel round 6 (done)

Seal 15.5% at 60.5/23.2, shadowless; trait word fades in UNDERNEATH
on tap. Diamonds 31.6 / name 36.4 (more air). The card spread always
shows THREE slots: real cards fill from the left, dotted #c49967
outlines mark the empties (no-card patrons show three). Win diamonds
locked to the red Wins/03. Row amounts measure themselves per open:
every .amt takes the widest amount's width, so coins hug the numbers
and still stack in one vertical line.

## P145 - round 7: seal cascade, centre slot, focus title + clarity (done)

Seal straight; trait word cascades in letter-by-letter (38ms
stagger, springy rise) under the seal. Name-to-tell air +1.3%.
Single-card spreads centre the card (2 cards fill left+middle).
FOCUS: title 5.4cqh at -38cqh with a travelling sheen (_fkSheen
duplicate-text gradient clip; on all four builders), X returns 19%,
scrims .78 everywhere; the focused CARD floats (fcvFloat: slow
rotation sway + rise on the inner img, so the zoom transform stays);
card centre 36.5%. Tier chip pokes out of the card corner
(-4.5/-3). CLARITY: _accG accents numbers AND core gameplay words
(bust/bank/reroll/triple/straight/wild/shatter/kept/once-per-match
...) in every focus panel, the card sheet, and tooltips (gold on
dark, bold brown on parchment). Deeper copy rewrite of card/die
texts stays open for a dedicated pass.

## P146 - focus polish round (done)

Card float restarts from rest (the old keyframes began at -1.3deg -
that was the landing snap) and is rotation-led (+-1.1deg, 1-2px bob,
4.4s). Tier chip re-attached to the corner (-2/-1.5) and smaller.
Die names keep ROMAN caps ("Jade II"). Focus names: 6.4cqh at
-41cqh, 4-way + diagonal outline in a darker saturated cut of the
text colour (_fkDarker in JS - no color-mix dependency), deeper
drop. Idle fan cards (and dotted empties) now VANISH during focus
like the dice - the dark blurred rectangles are gone.

## P146b/c - room vignette + split name colours (done)

The room's bottom vignette (#ptStage::after) dropped to z2, under
the patron tiles (z3) - portraits stay clean. Panel name: first name
very dark brown (#241505), surname keeps the portrait accent colour.

## P147 - straight landings, chip rides the float, clean sheen (done)

Card focus landing tilt reduced to +-0.6-1.6deg (mostly straight).
famCardArt wraps the face in .fcvIn - the float animates the wrapper
so the tier chip (and badge) sway WITH the card. Sheen keyframes
travel 170% -> -170% over a 300% canvas: the shine exits the
letters completely on both ends, so the loop restart is invisible.

## SIDE LAB v3 - die3d_lab.html (local only, gitignored)

Self-contained (three r128 + cannon.js + the GLB, all inline) 3D dice
sandbox. REAL rigid-body physics with the teal-dice deterministic
technique: all randomness up front -> hidden fixed-step sim to rest ->
read each die's natural up-face -> pre-rotate the MESH inside the body
so the wanted value shows -> reset and replay the identical sim
visibly. Dice collide with each other and invisible tray walls that
bound a fixed horizontal band (UI can never be hit). The LINE forms
inside the roll: per-die lane springs + soft mutual repulsion, both
scaled up as a die loses speed (chaos while fast, order as it dies) -
no tidy tween anywhere. Cocked dice are detected and re-thrown.
Selection = the game's look in 3D: inverted-hull shells (one opaque
#ffd98a outline at 1.035 + seven additive #ffb45e shells 1.06-1.36
whose overlap makes the outward falloff); the die itself is never
tinted. Long-press lifts a die (back-out spring + squash), dragging
swaps slots live (position IS loadout order - the next roll uses the
new lanes), drop lands with an ease-out-bounce and a landing squash.

SELECTION GLOW, final form (worth copying if this ever ships): the
camera never moves, so it is a 2D pass, not geometry. Selected dice
render alone into a full-res silhouette mask; a TIGHT gaussian blur
of that mask yields both an anti-aliased silhouette and the outline
band (smoothstep(.50,.63) minus smoothstep(.13,.48) - no hard
dilation anywhere, which is what made earlier versions stair-step);
a WIDE blur gives the falloff. Both composite in ONE gold with
NORMAL alpha blending - additive was saturating the band to white
and breaking the seam between outline and glow. Measured: die face
untouched, band peak at the edge, smooth tail to ~30px, hue constant
(G/R .77-.79) from band to tail, 0.5ms per frame. Dead ends worth
not repeating: inverted-hull shells (3D, wrong for a fixed camera,
and the emissive lift washed the die); ring-sampling for the blur
(only the arc facing the die ever hits it, so the falloff never
builds value); amplifying the blur BEFORE subtracting the mask
(glow bleeds over the die's own face).

PERF GOTCHA worth remembering: the settle loop originally ran until
'all stopped AND nothing too close', which deadlocked whenever a lane
spring balanced the separation force - 700-step caps, four retries,
~120ms of blocked main thread per roll (the ROLL button felt dead).
Fixed with a bounded 'overtime' phase (stronger separation for <=140
steps, then accept) and retries only for genuinely cocked dice: 7ms
average, 12ms worst, no caps, no retries across 16 rolls. The boost
schedule is recorded so the visible replay reproduces the hidden sim
exactly.

## SIDE LAB - die3d_test.html (not part of the game)

Standalone 3D-die ideation lab for Art/Assets/3D/die.glb (216 verts,
PBR, 219KB): three.js (unpkg CDN - lab only) with a candle rig (warm
flickering key, moon fill, ember bounce), orbit, tumble, ROLL with
springy settle, face-pose buttons 1-6 (tap again to cycle the
axis mapping until it lands right - the GLB's face layout is
discovered interactively), the game's iso rest pose, and BAKE:
renders the six posed faces to a transparent PNG strip + a 40px
game-size preview. Proves both the live-3D and the pre-baked-sprite
(renderDieAtRest swap, match brief 1.4) integration paths.

## P150 - REAL 3D DICE, phase 1 (rest dice) (done)

Denis's call: one 3D die asset everywhere dice are shown as objects,
so the shop/shelf/panel match the match table and the focus zoom can
actually rotate. Architecture, from the renderer mapping pass: every
dice surface is its own stacking context and only ONE is on screen at
a time, so D3X keeps a SINGLE WebGL canvas and re-parents it into the
live surface (#loStage / #ptPanelSheet / #stStage / #gbSheet /
#nrStage / #screen-match). Layout stays in the DOM: each .d3chip is
still the hit target and still defines the die's box; the canvas
draws the real die at that rect through an orthographic camera mapped
1:1 to CSS pixels. The CSS cube stays in the DOM but hidden
(html.fk3d .d3chip .die{visibility:hidden}) so every existing sizing,
state and hit path keeps working and one flag rolls the whole thing
back. three.js + GLTFLoader + die.glb are vendored under assets/ and
LAZY-loaded on first dice surface (no cost on the title screen).
Per-material colour/roughness replaces the CSS TINT filters (D3X.
MATCOL/ROUGH, relics mapped to their family colour). Hooked into
_d3ChipScan so every rebuild path (including the loadout zero-width
retry and the panel settle rebuild) re-syncs the 3D layer.

Verified on the shelf: canvas mounts in #loStage, six dice track
their chip rects, they render (opaque pixels at each die centre,
transparent elsewhere) and the CSS cubes are hidden.

TEST GOTCHA: the pane serves fark_proto.html from cache - a stale
copy had D3 but not D3X, which reads exactly like a scope bug. Add a
query string to bust it.

## P150b - the 3D dice never booted from file:// (fixed)

GLTFLoader.load() fetches over XHR, which browsers BLOCK for local
files - so opening fark_proto.html straight off disk left D3X.ready
false forever and the CSS cubes stayed visible ("still the old
dice"). The model now ships as assets/models/die_glb.js (base64 in a
script tag - script loading is allowed on file://) and D3X parses it
with GLTFLoader.parse(); it falls back to .load() if the script is
absent. Same trick the standalone lab uses.

## P151 - 3D dice: pose, size and lighting pass (done)

Denis: angle wrong, too big, no specular. (1) POSE - the tilt sign
was inverted, tipping each die AWAY from the camera, which is why
they read face-on. The rest pose is now built explicitly: value face
up, yaw 45deg, then tip +38deg toward the camera (D3X.TILT/YAW), so
the value sits on top with two side faces showing, like the painted
reference. (2) SIZE - a tipped cube's silhouette runs ~1.35x its edge
length, so scale went 0.92 -> 0.60 of the chip; measured silhouette
is now 0.78 of the chip box. (3) MATERIAL - MeshPhongMaterial with
specular black and shininess 0 = pure diffuse, keeping the GLB's
normal map for pip depth; tone mapping off; bone tints white so the
texture reads as painted. Rig is a soft warm key from above, a warm
side fill and warm ambient, so shadows stay warm (verified: top face
is the brightest, every face samples warm).

## P152 - 3D dice: pose to match the painted reference + focus (done)

POSE: the painted dice look nearly straight-on, so the rest pose is
no longer a steep three-quarter view. The value face now looks AT the
camera and TILT/YAW (15/20 deg) only reveal a sliver of the top and
one side - verified in a rendered silhouette dump (big flat face,
bright top edge, dark side edge). SIZE up to 0.80 of the chip (0.92
in focus); measured die height is now ~1.07 chip.
SHADOW: the game's sharp offset silhouette is back as a flat dark
clone of the die drawn behind it, nudged down-right (0.10/0.13 of
size), alpha .42 - the 3D twin of the old .d3dsl layer.
FOCUS: the zoomed die turns slowly on its own, can be DRAGGED to
rotate (document-level pointer handlers, ignored on the back button;
dragging cancels the idle spin), is rendered bigger, and every other
die simply disappears while a focus is open.

## P153 - the 3D dice were showing the WRONG FACES (fixed)

Root cause of "it's all broken": D3X's value->axis table was a guess
carried over from the lab (where it was calibrated by hand), and it
was wrong for this model - so every die pointed an arbitrary face at
the camera. Derived the real layout offline from the GLB itself:
group triangles by normal, take each face's UV island, count pips in
the baseColor texture. Result 1=-X, 6=+X, 2=+Y, 5=-Y, 3=-Z, 4=+Z -
cross-checked against the opposite-faces-sum-to-7 rule. Verified in
the browser by rendering values 1..6 dead-on and counting pips in the
rendered pixels: 1->1, 2->2 ... 6->6.
Also: pose calmed to TILT 11 / YAW 15 (just a sliver of top and
side), and the offset shadow is now a whisper (0.055/0.075 of size,
alpha .34), never rotates with the focus spin, and is hidden behind
the focused die so it can't read as a twin.

DEBUG NOTE: pip-counting from screen pixels needs a sample window
>= ~0.36 of the chip and a dead-on face, or 5s and 6s undercount
(their corner pips fall outside a tighter window) and the test lies.

## P154 - faces landed on their side; focus spin fixed (done)

Aligning a value's axis to the camera picks WHICH face you see but
leaves its roll free, so pips came out diagonal/sideways. Each face
now carries a full basis [right, up, normal] computed from the model's
own UV tangents, plus a global ROLL of 90deg because the UV islands
are authored a quarter-turn off. Verified by clustering pip centroids
in the rendered pixels: a 6 now reads 2 columns x 3 rows (it read
3x2 before), 5 reads five, 1 reads one.
FOCUS: grabbing the die no longer snaps it (the idle spin used to be
dropped on grab) and letting go no longer freezes it - the slow turn
runs continuously and the drag is an offset on top.

MEASURING GOTCHA: at rail size a die is only ~40px, so pip sampling
windows either clip the outer pips (undercount) or spill onto the
side faces (overcount). Scale one chip up (CSS transform) before
counting.

## die_texture_lab.html (local only, gitignored)

Standalone texture bench for the die: drag any PNG onto the page to
apply it (filenames containing "norm" load as the normal map, anything
else as the colour map), or use the file pickers. Shows the die big
(orbit + slow spin, pick which face is up) and/or as a rail of six in
the game's rest pose, under the game's exact lighting rig and face
table, so what you see is what the shelf will show. Buttons: stock
maps, UV guide (the wireframe overlay, to check island alignment),
normals off, tint (the game tints this one texture per material -
white shows it as painted), light level, background colour. Ships the
stock maps inline so reset always works; self-contained like the roll
lab, no server needed.

## P156 - more top-down pose, focus returns home (done)

Pose: TILT 11->21, YAW 15->7, so the dice are seen more from above
and much less from the side (verified: the value face sits square to
the camera at 0.93, the reveal is 21deg of top against 7deg of side).
NOTE when reading these numbers: the ROLL=90 correction swaps the
face basis's "up" and "right", so F[1] measures the SIDE reveal and
F[0] the TOP - easy to misread.
Focus: closing the panel now resets the die's dragged rotation and
re-poses it, so it drops back into the row at exactly the same angle
as its neighbours instead of keeping whatever angle it was spun to
(verified: 0.0deg difference from the rest pose after a 74deg spin).

## P157 - properly top-down, eased focus return (done)

TILT 21->32, YAW 7->3: the reveal is now 12x more top than side
(measured 0.53 vs 0.04 on the neighbouring faces), with the value
face still square to the camera. Focus close no longer snaps - the
die slerps from wherever it was spun back to the shared rest angle
over 420ms with an ease-out (sampled path: 36.5 -> 16.7 -> 7.3 ->
2.4 -> 0.2 -> 0 degrees).

## P158 - square-on top-down pose, return unwinds in flight (done)

TILT 32->42, YAW 3->0: the die is now square to the camera (side
reveal measures 0.000) and seen well from above (top reveal 0.669).
RETURN TIMING: a die was counted as focused while its .zoom class
lasted, but the focus code leaves that class on for ~470ms AFTER the
panel closes - so the angle only started unwinding once the die had
already landed. D3X now treats a die as focused only while the
PANEL is open (#gbLoadout.lo-focus / #gbShop.st-focus /
#ptPanelSheet.pt-focus / #famRunDraft.focus), so the rotation eases
home during the flight. Measured from the close: 68.8 -> 34.4 ->
13.8 -> 3.7 -> 0.3 degrees, square by the time it lands (450ms, the
same duration as the CSS travel).

## P159 — real perspective on the rest dice (no more reverse-perspective read)

Denis: *"is the view isometric? They look like the front of the die (closer)
is smaller than the back (further) somehow"*. Correct diagnosis — the D3X
camera was an **OrthographicCamera**, so near and far edges projected to
exactly the same width (measured: 24.3px / 24.3px). The eye expects the far
edge to be smaller, so equal edges read as *reverse* perspective.

- `THREE.OrthographicCamera` → `THREE.PerspectiveCamera`, `D3X.FOV = 40`.
  The lens is placed at `dist = (mountH/2) / tan(FOV/2)` so **one world unit
  is still one CSS pixel on the dice plane** — every existing size and
  position calculation keeps working untouched.
- New `D3X._aimQ(x,y)`: a wider lens would make dice away from screen centre
  read as seen-from-the-side (the thing Denis fought for four rounds). Each
  die is now turned to look straight down the lens, pre-multiplied onto its
  pose (and onto the shadow twin + the focus-return slerp target, so the
  flight home still lands square).

Verified by projecting all 8 cube corners per die:
- near/far taper **+4.1%** on every die (near edge 24.89 vs far 23.91) —
  physically what a real die photographed at table distance does.
- sideways skew across the row **≤0.07px** with the aim correction, vs up to
  **1.67px** (7% of the die) without it.

`D3X.FOV` is the single dial: higher = more taper, lower = flatter.

## P160-P161 — the dice stop reading as reverse-perspective

Denis, twice: *"the front of the die (closer) is smaller than the back
(further)"* / *"still gives the same effect"*, then the diagnosis that
cracked it: *"I think they all have a slight different angle, trying to face
camera. Just have one angle for all, all aligned."*

Two separate faults, both now fixed.

**1. Per-die aim (P159) gave every die its own angle.** Removed. `_aimQ` is
gone.

**2. The pose itself could never read right.** Measured off the actual
rendered pixels (silhouette width per row, alpha > 140), the die at TILT=42
came out **24 → 26 → 24 px**: widest in the middle. Tipping a die back makes
its NEAREST point the top-front edge, so the silhouette bulges at the centre
and the bottom (front) and top (back) land at the same width. No lens
strength fixes it — at TILT=42 the front-bottom and top-back edges sit within
0.074 die-widths of each other in depth, so they project the same size by
construction.

**The fix: a shift lens.** The die now stands upright and dead-on (TILT=0,
YAW=0) and the from-above look comes from a *raised but untilted* camera —
the film plane stays parallel to the value face, the way dice are drawn:

- per die: `dist = LENS * sz`, `rise = dist * tan(EL)`, camera at
  `(x, y + rise, dist)` with **no** `lookAt` (rotation stays zero), and
  `setViewOffset` takes an off-centre slice of a taller frustum.
- each die renders into its own scissored viewport, so all six are
  pixel-identical: **one angle, all aligned.**

Dials: `D3X.EL` (40) = how far above; `D3X.LENS` (7) = lens distance in
die-widths, lower = stronger taper; `D3X.PAD` (2.6) = viewport margin.

Verified from rendered pixels, not from intent:
- profile is now monotone — `20 21 23 23 … 25 25 25 … 25 23 20`: the top face
  narrows toward the back, the value face is a constant-width rectangle.
- bottom edge **6.9%** wider than the top edge (was 0%, and briefly a 4%
  taper at P159 that Denis correctly called as no change).
- **max row difference between the six dice: 0 px.**
- focus die and the eased return home still land exactly on the shared rest
  angle.

### Texture lab (local, not shipped)
Defaults are now what the work actually needs: **rail of six**, normal map
**off**, and the rail is drawn with the game's own rig (same EL/LENS/PAD,
same per-die shift lens) so a texture is judged in the shape it will ship in.
Added a **specular map** slot — file picker plus drag-drop on any name
containing spec/rough/gloss — with strength and gloss sliders. White in the
map = shiny. Strength is 0 (fully matte) until a map is loaded, then it
auto-lifts to 45 so the effect is visible immediately.

## P162 — one camera, one normal lens (supersedes P161's shift lens)

Denis: *"no now they're stretched and all their backs pointing in a different
direction... is it one camera per dice or something? Why is it so
complicated? Just need a slight wide angle, like a 50mm"*. Fair — P161 was
over-built. The whole per-die rig is gone.

- one `PerspectiveCamera` over the surface, `D3X.FOV = 40` (a ~50mm look),
  placed at `dist = (surfaceH/2)/tan(FOV/2)` so one world unit is still one
  CSS pixel on the dice plane. One `render()` call, no viewports, no
  scissors, no `setViewOffset`, no `_aimQ`.
- `D3X.TILT = 25` — a modest lean back. The point of P161's measurement still
  holds: at TILT≈45 the silhouette bulges in the middle (the near/far edges
  land at the same depth) and reads as reverse perspective. 25 keeps the top
  face a sliver and the silhouette clean.

Measured off the rendered pixels:
- die is **24 x 31 px**, stretch **1.29** (P161 was 1.68 — that was the
  "stretched" Denis saw).
- profile is flat: `21 22 24 24 … 24 24 23 21`. No bulge.
- outer dice are **2 px wider** than the middle pair: with one lens the outer
  dice sit 5.3 degrees off-axis and show a sliver of side. That is what one
  camera does; the only cure is a longer lens (lower `FOV`).

Dials: `D3X.FOV` (40) = lens; lower is longer/flatter and squares up the
outer dice. `D3X.TILT` (25) = how much top face shows.

Texture lab follows the same rig, holding the game's measured
camera-distance-to-die ratio (34.5 die-widths) so the dice show the same
perspective, just magnified — verified 110x135 px, outer dice 6.4% wider,
matching the game's proportions.

## P163 — real 3D dice on the match table

Match dice are not `.d3chip` placeholders: each is a `.die` host owning a
CSS-cube instance (`el._d3`) driven by the D3 engine — roll, hop, neighbour
shove, hover, settle, reroll, scatter. Rather than write a second animation
system, **D3X mirrors that engine**:

- `_cssQ(tilt,turn,spin,pitch,yaw)` rebuilds the engine's orientation as a
  quaternion. Its `rotv` applies yaw → pitch → spin → turn → tilt, and its y
  axis points DOWN the screen, so x and z rotations flip sign.
- `_deltaQ(e,val)` = how far the cube has turned from where it RESTS for that
  value. That same world-space turn is applied to the 3D die's rest pose, so
  a roll tumbles identically and lands on exactly the face the game says.
- position, hop and the hover scale are read straight off the engine
  (`x + ox`, `y - h*0.55*s`, `1 + h*0.004`).

Every existing roll/reroll/settle/scatter path therefore drives the 3D dice
with no new animation code, and the CSS cube is hidden per-die (its ground
shadow stays).

Surface arbitration is now one `tick()` per frame: a `.d3chip` only counts if
it actually has a box, so a CLOSED panel can no longer steal the canvas from
the table (that fought every frame). Dropping a die always restores the cube
it was covering.

Selection: the cube used to draw its own glow, so the game's gold outline
(`.die-wrap::after`) was switched off for cube dice. It is back on for 3D
dice — 3px `--gold`, inset -4px, octagon clip, z 5 over the canvas.

`D3X.FOV_MATCH = 55` — the table gets the wider lens Denis asked for (the
shelf stays at 40). `D3X.MSCALE = 0.86` sizes a die against its host box.

Verified in a live match, from rendered pixels:
- orientation mirror is **exact to 1.7e-15 across 1200 random poses** (every
  face normal, checked against `D3.rotv` itself).
- all six dice show the **correct face** (pip-counted off the canvas twice,
  after independent rolls: 3/1/4/1/6/2 and 4/6/4/3/2/1).
- hop/shove/scale mirror exact: dx 17 vs 17, dy 18.2 vs 18.2, scale 1.088 vs
  1.088; restoring the engine values returns the die to 0.00 degrees error.
- 25 consecutive ticks hold one state (`screen-match/6/true`) — no thrash.
- ~0.33 ms per tick+frame for six dice.

NOT yet exercised: a live roll animation (this pane freezes rAF, so the
tumble was verified mathematically rather than watched), and the kept-tray /
opponent rows, which take the same code path but were not reached in test.
Next: port the lab's silhouette outline+glow to replace the box ring.

## P164 — die re-unwrapped: six equal islands, seam on the middle of the curve

Denis, before handing the die to a texture artist: *"some of the faces are cut
short rather than all the faces having the same padding around. They should
all cut neatly in the middle of the curve between each face."*

What the old unwrap actually was, measured off the model:
- the bottom **27% of the sheet was empty** (v never went below 0.266)
- **two faces had 10% more resolution than the other four** — the ±Z islands
  were 0.294 wide against 0.244 for ±X/±Y, texel density 13.31 vs 12.11. The
  mesh is a *perfect* cube (all three axes equal to five decimals), so that was
  pure layout inconsistency: a pip at a given pixel size came out ~10% smaller
  on two faces.
- islands at irregular offsets, so there was no grid to paint against.

**The new unwrap.** The die is a cube of half-size h with a constant-radius
bevel r = h/4 (verified to 2.4e-9 across all 216 verts). So for any surface
point: `a = clamp(P,-c,c)` with `c = h-r`, and `dir = (P-a)/r` is the exact
outward normal. The island coordinate unfolds the bevel by ARC LENGTH:

    u = a·right + r·atan2(dir·right, dir·n)
    v = a·up    + r·atan2(dir·up,    dir·n)

On the plateau that is just the position; at the 45° midline it is `c + rπ/4`
on every side. So each island carries exactly half the bevel on all four
sides and the seam lands precisely on the middle of the curve — which is what
was asked for. Islands use each face's own right/up basis from the game's
FACE table, so every number sits upright, laid out 3×2 in value order 1..6.

Nothing had to be split: the bevel already has a vertex ring at exactly 45°
and **zero triangles cross a face boundary** (88 verts sit on a 2-face seam,
16 on 3-face corners). Vertices were unshared per triangle (216 → 900) since
a seam vertex needs a different UV per island.

Existing maps were rebaked onto the new layout — per triangle the old and new
UVs are both per-vertex, so a pixel's old UV is its barycentric coords in the
new UV triangle applied to the old ones. The normal map additionally has its
tangent frame rotated (decode with the old basis into object space, re-encode
with the new), and everything is dilated outward to fill the bleed margin.

Results:
- texel density spread across the six faces: **0.000%** (was 9.9%)
- sheet coverage **93.8%** (was 71.4%), 310px per face, all equal
- atlas reads 1‑2‑3 / 4‑5‑6 in order — pip-counted per island
- rendered die is unchanged: **100% silhouette overlap** with the old model,
  mean colour delta 3.1/255 (resampling at pip edges)
- all six values show the correct face in game

Shipped: `assets/models/die.glb` (292KB, 960×640 atlas) + `die_glb.js` base64,
and the texture lab re-embeds model, rebaked maps and the new guide.
`Art/Assets/3D/die.glb` was never written to.

For the artist: `assets/models/die_uv_guide.png` (1536×1024 transparent
overlay — island bounds, where the flat face ends, wireframe, numbers) and
`die_uv_guide_over_art.png`. Flat face is **79.3%** of the island; the curve
padding is **10.4% each side**. Authoring res is free — the layout is
normalised, so paint at whatever size and it downsamples.

## P165 — match dice line up; prop placement tool

**Dice alignment.** Measured off the rendered pixels: the row was already
perfectly level (bottom spread 0px, even 51px gaps) and all engine offsets
were zero. The fault was WIDTH — 42/39/37/37/39/42, the outer dice 13.5%
wider because at `FOV_MATCH = 55` they sit off-axis and show a sliver of
their side face. Note that in this rig FOV changes nothing about framing (one
world unit stays one CSS pixel at the dice plane) — it only sets how much the
outer dice turn. Swept it: spread is 5px at 55, 4px at 40, 3px at 32, and
bottoms out at 2px by 22. Set `FOV_MATCH = 24`: widths now 38/37/36/36/37/38,
identical heights, tops and bottoms dead level. 2px is the floor for one
shared camera; going below would need per-die aim, which was rejected in P162.

**prop_lab.html** (local, gitignored like the other labs) — place, move,
rotate and scale the table props by hand and save templates.
- the stage runs at the game's exact aspect (319x691) so every % matches
- guides for the dice band and the placer's margins; optional candle falloff
  and shadow offset previews using the game's own formulas
- drag to move, gold handle to scale about the centre, blue handle to rotate;
  arrows nudge, Shift+arrows rotate, Delete removes
- layer list + "sort by depth" (the painter's order the game uses)
- templates persist in localStorage; export writes `assets/prop_templates.js`

Game side: `window.FK_PROP_TEMPLATES` (loaded from `assets/prop_templates.js`,
shipped empty). If it holds any templates, `_matchDress` picks one per match
and uses it **exactly as saved** — the override lands after the procedural
sort, so nothing is nudged by the separation pass and array order is the draw
order. Empty = the procedural dressing as before. Verified end to end: placed
three props in the tool, exported, and the game rendered identical n/x/y/w/rot
in the same order.

Still open (Denis): scored dice leaving the line — he'd rather they stay put
and get a treatment instead; deferred.

## P166 — the dice settle FLAT

Denis: *"the dice still all have a different rotation when settling as if seen
by different cameras or just stopping when not fully flat on the surface"*.

Not the camera — the roll's landing. `D3.roll` lands the in-plane spin on
`r(cfg.rot)` with `cfg.rot = 75`, i.e. **a random roll of up to ±75° per
die**. On the flat CSS cube that read as a thrown die; on a real 3D die the
same roll reads as stopped mid-tumble, resting on an edge. Pitch and yaw were
never the problem — `iturns()` always returns whole turns, so those land
exactly on `FACE_ROT`.

Fix is one line in `D3.roll`: when the 3D layer has booted, snap the landing
spin to a whole turn. The die still spins the entire way there — only where
it stops changes. If D3X never boots, the CSS dice keep their thrown look.

Verified by simulating **240 roll landings** (6 dice x 40 rolls): residual
spin **0.0000°**, and the landing pose is **0.0000°** off the shared rest pose
for every one.

Testing note: this slipped through P163/P165 because the preview pane freezes
requestAnimationFrame, so a roll never actually animates to its landing —
every measurement was taken with the dice still at spin 0. Landing state has
to be checked against `d.to`, not against whatever the frozen dice show.

## P167 — the table dice sit higher, on a wider lens

Denis: *"all aligned now thanks. But they need to be seen more from the top to
match the table angle, and you can push the lens a bit wider"*.

"More from the top" is the die's own pitch, which the shelf shares — so the
match now has its own: `TILT_MATCH = 38` against the shelf's `TILT = 25`.
`_isoQ(val, tilt)` caches a pose per tilt value, so both dials stay live.
Lens: `FOV_MATCH = 24 -> 34`.

Measuring this needed a different instrument. A cube's SILHOUETTE barely
changes with pitch — 36px wide at both 25° and 45°, height only 44 -> 47 —
so the outline says nothing about how much top face shows. That lives in the
shading, so the boundary is found as the luminance step down a column beside
the pips. Top-face share then reads 16% / 22% / 24% / 26% / 26% across tilt
25 / 30 / 35 / 38 / 40 — climbing, and flattening by 38, which is where it
sits. That also stays clear of the ~45° trap from P159: at 45 the front and
top faces are equal and the shape reads as reverse perspective.

Final state on the table: widths 39/38/36/36/38/39 (spread 3px, up from 2 —
the cost of the wider lens), heights all 46, tops and bottoms dead level,
gaps even, max row-by-row difference between any two dice 3px.

## P168 — lift the lens instead of tipping the die further

*"more from the top please, wider lens"* — again. The die's own pitch was
nearly spent: past ~45° the top-back edge sits nearer than the bottom-front
one and the die reads inside-out (the P159 trap). At `TILT_MATCH = 38` the
separation is only 0.086 die-widths, so there was no room left there.

So the top-down now comes from the CAMERA, which has no such ceiling and is
what looking down at a table actually is. `RISE_MATCH` (degrees) lifts the
lens above the table while keeping the film plane upright: widen the frustum
by the rise and take the slice that still maps one world unit to one CSS
pixel, exactly the shift lens from P161 but ONE camera for the whole surface
rather than per die — so every die in a row gets the same vertical angle and
they stay identical. `RISE_MATCH = 20`, `FOV_MATCH = 34 -> 44`.

Measuring this needed the geometry, not the pixels. The silhouette is nearly
useless (a cube's outline barely moves with pitch) and a luminance-step
detector latches onto the bevel highlight once the top face gets big. So the
top-face share is now computed by projecting the three edges that bound it —
top-back, the shared edge, bottom-front — through the live camera. Note the
object's local axes are the MESH's, not the pose's, so this has to be done in
world space off the tilt quaternion.

Top-face share by rise, at tilt 38: **43% / 50% / 56% / 61% / 67% / 73%** for
rise 0 / 8 / 14 / 20 / 26 / 32. Shipped at 20 = **61%**, up from 43%.

Final: widths 41/39/37/37/39/41 (spread 4px, the cost of the wider lens),
heights all 48, tops and bottoms level, worst DOM-register error 1.1px.

Worth raising with Denis: the value is on the die's FRONT face, so the further
top-down we go the smaller the face carrying the number gets (39% of the
height now). Past this point the value really wants to move to the TOP face,
the way a die on a real table works — a bigger change, his call.

## P169 — SKIN: one painted texture on every die

Denis painted an amber set against the new unwrap (1536x1024, exactly the
guide sheet) and wanted it on all dice to look at.

`D3X.SKIN = {map, spec, specular, shininess}` puts one texture on every die
and bypasses the per-material tint (so a special die is amber too, which is
the point of the look). `SKIN:null` restores the tinted stock texture — that
is the whole revert.

The die material is `MeshPhongMaterial` with specular black, and **Phong's
specularMap takes white = shiny**, which is exactly how the texture lab
authors it. So the spec map ships as painted — no inversion. (First pass I
inverted it into a roughness map, which would have been right for a Standard
material and wrong here.) `specular: 0x736e66`, `shininess: 30` — the lab's
defaults, so the lab preview and the game agree.

Shipped as WebP next to the model: `die_amber.webp` 313KB, `die_amber_spec.webp`
59KB. Loaded through `TextureLoader` (an <img> under the hood, so file:// is
fine) with `flipY=false` to match the baked maps, and the skin resolves before
`ready` fires so no die is ever built with the wrong material.

Verified in a live match: both maps bound, material carries map + specularMap,
colour forced to white, and the rendered faces average RGB(238,132,39) with a
red:blue ratio of 3.3-7.8 across the six dice.

## P170-P171 — painted dice per material, and a rough settle

**Why every die went bone.** P169 gated `self.ready` on the skin finishing to
load. If a texture never resolved, D3X never became ready, no 3D dice were
ever built, and the whole game fell back to the CSS cubes — which are the
painted BONE die. So "still all bone" was not a texture problem at all, it
was the 3D layer never starting. Skins now load in the background and are
applied to dice already on screen when they arrive; a slow or broken texture
costs a texture, never the dice. Trial webp files dropped for jpg to take
that variable off the table too.

**Per-material texture sets.** Denis supplies the art per die material now, so
D3X stops colouring anything. `D3X.SKINS[mat] = {map, spec, normal}` is wired
straight through with a white base colour — as painted. A material with no
set keeps the old tinted stock texture until its art lands, so nothing else
regresses. `SKIN_ALL:'amber'` forces one material's art onto every die for a
look-see; set it to null for per-material behaviour.

Specular: the die material is `MeshPhongMaterial`, whose `specularMap` reads
white = shiny — the same convention the texture lab uses — so the map ships
exactly as painted. `SPEC:{color:0x736e66,shininess:30}` matches the lab's
defaults so the two agree.

`D3X.diag()` returns ready/failed/dice-count/mount/loaded-sets and the first
die's actual material, for when a browser is showing the wrong thing.

**Rough settle.** `D3X.SETTLE = {x:7, y:4, rot:0}` (in die-widths) scatters
where each die comes to rest, since dice that just bounced don't sit in a
ruler-straight row. The engine's existing neighbour shove keeps them from
overlapping. `rot` is in-plane roll and stays at 0 — that is the one that made
them read as stopped on an edge (P166), so the roughness is positional only.
Measured on the game's own roll path: x ±5.3px, y ±2.9px, and all 30 sampled
landings still exactly flat.

Verified in a live match: ready before textures resolve, amber bound with map
+ spec, base colour ffffff, rendered faces RGB ~(243,152,53) across all six.

## P172 — die skins ship embedded (the real reason no texture appeared)

Firefox gives every local file its own origin (`privacy.file_unique_origin`),
so an image fetched from `assets/` into a `file://` page is CROSS-ORIGIN and
**WebGL refuses to upload it as a texture**. The die's own maps come out of
the base64-embedded model, so those were fine — which is exactly why bone
rendered and the painted skin did not. Nothing to do with the file format.

Skins now ship the same way the model does: `assets/models/dice/skins.js`
defines `window.FK_DIE_SKINS = {name:{map,spec}}` as base64 data URIs, which
are same-origin everywhere. `_skinFor` prefers those and falls back to a URL
path, so a set can still be pointed at a loose file during development.

Sources stay as Denis's PNGs in `Art/Assets/3D/textures/<name>/`; the shipped
copy is JPEG at 960x640 (310px per face, against a die that never renders
above ~200px): amber diffuse 141KB, spec 76KB, 290KB as base64.

Verified: map source starts `data:image/jpeg;base64,`, and the dice render
RGB(209,117,24).

## P173 — physics roll, stage 1: the solve

Denis picked full physics for the match table: dice tumble, bounce off each
other and the rails, settle in a rough line, and **the number scored is the
face that lands up** — like `die3d_lab.html`. That is the fork that decides
everything else: today the match shows the value on the face turned toward
the camera and each die sits in a layout slot, which is exactly why it reads
as a row rather than as thrown dice.

Ported from the lab, unchanged in spirit: every random choice is made up
front, the sim runs HIDDEN at a fixed 1/60 step until the dice rest, the
natural up-face is read, and each die is then **relabelled by a cube
symmetry** so the face the GAME rolled is the one on top. The game still owns
the numbers; physics only owns the placement. Lane springs pull each die
toward its slot, a spring-MINUS-damper shove keeps them apart without buzzing,
and bounded overtime calms the table rather than shoving harder.

Two additions over the lab port:
- **flat-snap**: a die that stopped a few degrees off flat never reads clean,
  so the final orientation is tipped the minimum amount to sit square. It is
  built with `setFromUnitVectors` on the up-axis, which preserves the die's
  yaw — the row stays as randomly turned as it landed.
- `_relabel` snaps its matrix to an exact cube symmetry so faces stay axis
  aligned after the swap.

Measured over 40 rolls / 240 dice at the real row spacing (51px pitch on 37px
dice = 1.38 die-widths — an earlier run used 1.04 and produced dice landing
on top of each other, which was the test's fault, not the sim's):

- **wrong face: 0** — the relabel is exact
- **cocked at rest: 0** (was 2 before the flat-snap)
- hit the step cap: 0; gaps under 0.9 die-widths: 3/200, min 0.87
- 5.9 ms per roll, 71 steps average (1.2s), 203 worst (3.4s)
- yaw spread 358 degrees — they land every which way, which is the whole point

`_physSolve` is inert so far: nothing calls it, so the game is unchanged.

**Stage 2 (next)** is the bigger half — the match layer is 2.5D today (dice on
a plane facing the camera, one world unit = one CSS pixel). Physics needs a
real horizontal table: a camera looking down at a tray, dice projected from
world XZ onto the screen, and the DOM hosts slaved to those projected
positions so hit-testing and selection follow the dice where they land.

## P175 — physics roll, stage 2: the dice land on a table

The camera Denis tuned is untouched. Instead of rebuilding it, the match dice
now live in a GROUP tilted back about X (`TABLE.tilt = 58`): the table
recedes, dice lie flat on it with the value up and whatever yaw they landed
with, and the far side of the tray sits higher on screen. Much less invasive
than moving to a look-down camera, and the lens stays exactly as approved.

A roll is intercepted at `D3.roll`: match dice are queued and the whole batch
is solved together on the next tick (they are rolled in one loop, so a
zero-delay timeout catches them all), then the recorded frames play back off
the clock. The CSS cube keeps running underneath, hidden, so every existing
state path — selection, scoring, bust, reroll — still works untouched.

**The DOM box follows the die.** `_slaveHost` projects each die's world
position and translates its `.die` host so it stays clickable exactly where it
is drawn. Two bugs found doing it:
- `.die` carries `transition:transform .08s`, so the box lagged the die every
  frame AND the one-time "home" rect was read mid-transition. The transition
  is now disabled while physics owns the die, and restored when it lets go.
- `_slaveHost` projected through the table group before three had updated the
  group's world matrix, so the first frame's positions were a frame stale.

Verified at rest in a live match: **faces correct on all six**, worst
hit-box offset **0.0px**, yaw spread **253 degrees**, uneven gaps.

Testing note: an intermediate check reported wrong faces, which was the probe
being wrong, not the code — playback was at step 58 of 74, and mid-flight the
die is SUPPOSED to show its raw tumbling orientation; the relabel only lands
on the final frame. Force `P.t0` into the past to measure the settled state.

## P176 — the pile was depth, not scatter

*"it's all jumbled up"*. Measured over 180 dice, the physics was actually
healthy: no die ever stacked on another (max rest height 0.67 of a die), the
closest pair never came under 1.03 die-widths, and x held its lane (median
drift 0.13). The problem was **z** — depth wandered up to 1.05 die-widths,
and the table is seen from 58 degrees, so depth reads as VERTICAL jumble on
screen (z x 37px x sin58 = 31px per die-width) rather than as distance.

The lab could afford a loose depth lane because its camera sat much lower.
Here the depth lane is stiffened — `laneKZ 8 -> 28`, `laneCZ 2.4 -> 5` —
while x stays exactly as loose as it was, because x is where the rough line
lives. Swept it first; every setting held 0 wrong faces, the same ~73-step
settle and the same ~1.0 minimum separation, so the tightening is free:

    laneKZ    8      14     20     28     40
    z p90     0.87   0.68   0.46   0.35   0.25
    on screen ±27px  ±21px  ±14px  ±11px  ±8px

Verified in a live match at 28: faces correct, screen-Y spread **7.6px**
(was ~27), yaw spread 316 degrees, gaps still uneven.

## P177 — rerolls stop landing on the kept dice

**The reroll bug.** `_physStart` built its slots as a freshly CENTRED row of
however many dice were in the batch. Reroll 3 of 6 and those 3 were aimed
across the middle of the table — straight through the dice being kept, which
the sim did not know existed. Three fixes:

- every die now owns a **persistent pose** (`d.phys`), so a die that is not
  being rolled stays exactly where it landed;
- a throw targets **each die's own column**, measured off its DOM slot rather
  than a recentred row;
- dice staying put go into the sim as **static bodies**, so the thrown ones
  bounce off them instead of through them.

Scoped by row: the player line, the kept tray and the opponent line are
separate tables with their own centres, and mixing their dice into one sim
would have put obstacles at meaningless positions.

Measured over 30 rerolls (90 thrown dice against 3 kept each): **0 landed on
a kept die**, closest approach 1.02 die-widths, 0 wrong faces.

**Start timing.** The batch fires on a zero-delay timeout, which can beat the
tick that registers the new hosts — and the first retry scheme gave up after
600ms of wall clock. A parked throw is now picked up by `tick()` itself, so a
stalled frame loop delays the roll instead of dropping it.

**Angle.** `TABLE.tilt 58 -> 50`. Worth recording why 58 read as "too high"
even though it matched the old proportions: the top face's share of the
silhouette is `sin(t)/(sin(t)+cos(t))`, which at 58 is 62% — almost exactly
the 61% of P168. But back then that 62% was the *non-value* face and the
number sat on the front; now the number is ON the top face, so the same
proportion reads as looking down much harder. 50 gives 54%.

**Size.** `MSCALE 0.86 -> 0.77` — 10% smaller, more room to move.

Live match at these settings: 6 settled, faces correct, hit-box offset 0.0px,
vertical scatter 12.4px, gaps 48/40/55/68/54px — uneven, which is the point.

## P178 — the settle stops popping; lower table, wider lens

*"Dice seem to switch face in one frame when they settle"* — real bug, and an
obvious one in hindsight. `_physPose` applied the relabel ONLY on the final
frame, so the die tumbled showing whatever face physics gave it and then
snapped to the value the game rolled — a cube symmetry, so up to 180 degrees
in a single frame.

The relabel is a cube symmetry, which means it can ride along from frame ONE:
the silhouette is identical either way and only the painted faces move, which
is invisible while the die is tumbling. The `flat` correction (the small tip
that squares a die up) is separate and can't be applied early, so it eases in
over the last 10 frames with a cubic curve instead of snapping.

Measured over the last 24 frames of a live roll: **final-frame turn 0.0
degrees** on all six dice, with the settle moving 4-12 degrees per frame —
continuous the whole way in. Faces still correct.

`TABLE.tilt 50 -> 42` (top-face share 54% -> 47%) and `FOV_MATCH 44 -> 54`.
`TABLE.land` is the new dial for how many frames the squaring-up takes.

## P179 — dice keep their distance

`sepMin` was a CENTRE distance of 1.04, so two dice were 0.04 of a width
apart at the edges — kissing. And a die turned 45 degrees needs 1.414 between
centres just to not overlap, so the real requirement was never being met.

Raising the shove alone does not fix it: once the dice are resting, the lane
spring pulls them back and a "keep stepping until they spread" phase
deadlocks against it — measured, it burned its whole 70-step cap and doubled
the roll (145 steps against 73) while only getting the closest pair from 1.11
to 1.13.

So the resting positions are relaxed directly along the line instead, then
the correction is blended into the last 16 frames on a cubic curve — it plays
back as the die sliding its last few pixels home rather than teleporting.

Over 30 rolls: closest centres **1.50** (the target, exactly), worst-case
edge clearance **+0.09 with both dice at 45 degrees**, **0/450 pairs able to
touch**, max slide 0.4 die-widths (~13px), roll back to 69 steps, x drift
tighter than before (p90 0.25), 0 wrong faces.

Note the slot pitch is now 1.6 die-widths, not the 1.38 in `TABLE.pitch` —
the dice got 10% smaller in P177 while the DOM row kept its 51px spacing.
Slots are measured off the DOM, so that constant is now unused.

## P180 — real shadows for the physics dice

The old dice shadows are painted on a 2D canvas from the CSS cubes' SLOT
positions. Those cubes are hidden and no longer where the dice are, so the
blobs sat under the wrong places and never turned with a die.

Physics dice now cast a genuine shadow onto the table they are lying on:
`shadowMap` on with PCF soft filtering, the key light casts, dice cast, and a
`ShadowMaterial` plane lies flat in the table group as a catcher — invisible
except where a die darkens it, so the painted table shows through. The light
and the catcher are both CHILDREN of the table group, so they follow whatever
angle `TABLE.tilt` is set to and the shadow always falls across the table.

The legacy 2D pass now skips any die the 3D layer owns (`_d3xOwned`), which
would otherwise double the shadow at the wrong place and angle.

Verified in a live match: shadow map on, key casting, catcher present, dice
casting, legacy blob suppressed, and 128 semi-transparent pixels of cast
shadow around a die that previously had none of its own.

STILL OPEN: the selection outline+glow. The lab's is a screen-space pipeline
— a mask layer rendered to a target, two tight blur passes for the
anti-aliased silhouette and outline band, four wide passes for the falloff,
then an additive glow pass and an alpha line pass composited over the frame.
The game currently falls back to the DOM gold octagon ring from P163. That
port is the next job.

## P181 — contact shadows, per-type outlines, warm shading, own skins

**Shadows.** The P180 shadow-map catcher was there but unreadable, so it's
gone. Each die now drops a **sharp contact shadow**: one soft-edged quad
lying on the table, turned with the die, growing and fading as the die
leaves the table. Two things it needed:
- the colour is a warm brown (`SHADOW_COL 0x5a2c12`), not grey — measured
  R 104 / B 91 with 84% of its pixels warm-biased;
- straight underneath, it was **almost entirely hidden behind the die** at
  this camera angle (105 visible pixels), so it is nudged away from the
  candle, the same offset silhouette the painted dice use.

**Outlines.** Every die carries a silhouette in its own colour, drawn as a
back-face hull just behind it. `OUTCOL = {bone:'#291d11', amber:'#3f1000'}`,
falling back to the painted dice's `D3.OUT` for anything not listed.

Bug worth remembering: the outline rendered WHITE, because `_reskin` walks
the whole die group and re-dressed the hull with the die's texture. Outline
meshes are now tagged `userData.outline` and skipped by the skin pass.

**Shading.** The candle sits above the table, so the face turned up to it
takes the light and the sides fall away: key up to 1.5, ambient dropped to
0.58 and recoloured to a warm brown `0x8a4f22`. That keeps the shaded faces
dark but SATURATED — a grey ambient just washes them out. Measured face
luminance on a die: 87 in shade against 250 lit.

**Skins.** `SKIN_ALL` is off, so each material wears its own art again;
`bone` and `amber` are both embedded (bone 97KB, amber 216KB as JPEG).

## P182 — dice shadows use the game's own technique

Denis: shadows should work like the props — the UNLIT table png revealed
through the shape as a mask — they were overlapping the dice, one die still
had the old blob, and they wanted to be darker.

**Why they overlapped.** The contact quads were `transparent:true`, so three
put them in the TRANSPARENT queue, which draws after every opaque mesh.
`renderOrder` only sorts within that queue, so a die's shadow always painted
over the dice. Drawing on the 2D shadow canvas *underneath* the WebGL canvas
removes the problem by construction.

**The leftover blob** was a die the 3D layer draws but had never marked as
owned — ownership was only set on the physics paths. Every match die the
layer draws is now marked, so the legacy pass never doubles it.

**The technique.** The 3D quads are retired (`CONTACT3D:false`). Each die now
projects its eight corners through the LIVE camera, they are gift-wrapped
into a silhouette, and that hull masks the unlit table image — the same
`source-in` + feathered-ring approach `_drawPropShadows` uses, so dice and
props are lit by one idea. Darkened 25% over the prop pass on top.

Measured on the shadow canvas: **13,485 px** at average RGB(65,40,20) —
warm brown, not grey — alpha 206.

**Light.** The key was blowing out the top faces: intensity 1.5 -> 1.02 and
its colour warmed from 0xfff2dc to 0xffd9a2.

## P183 — the two real bugs behind "it's all very broken"

Both were mine, and both were structural rather than tuning.

**Half the dice never landed** (so half had no shadow — the shadow pass only
draws dice that are on the table). There was ONE global `_play`. Dice are
created one at a time, and `_d3InitHost` RETRIES on a timer when a die's box
is not measurable yet, so their rolls can land in two different ticks — two
batches — and the second **overwrote the first**. The orphaned dice never got
a resting pose. Playback is now stored **per die** (`d.roll`), so batching
only matters for the collision solve and nothing can be dropped. Verified:
6/6 settled, 0 left rolling, 0 in neither state.

**Jitter when selecting.** The table's origin was read from the ROW's
bounding box every frame — but that box is the union of the dice, which this
code moves. Dice move, row box moves, origin moves, dice move: a feedback
loop, and selecting a die perturbed it enough to show. The origin now comes
from the cached untransformed homes, which nothing downstream can disturb.
Verified: 0.00px drift over 10 frames, idle and with a die selected.

Also: no normal map anywhere (Denis), outlines darkened 0.72 and saturated
1.45 with a grain texture, and the shadow tucked in close under the die
(offset roughly a third of what it was, alpha down from 1.25x the prop pass
to 0.95x) so it reads as contact rather than a cast shadow.

## P184-P185 — review pass fixes, and a 3D selection outline

Two bugs found by MEASURING rather than reading, both from the review pass:

**Ghost dice.** `_drop` called `scene.remove(d.obj)` — but a die on the table
is parented to the TABLE GROUP, not the scene, so that was a no-op and every
destroyed die left a fully-rendering ghost. Measured: removing all six hosts
left `dice:0` but the table still holding 6 groups and 25 draw calls. The
game recreates dice hosts on every roll, so these accumulated for a whole
match. Now detaches from the real parent and disposes the per-die materials
(geometry is SHARED with the proto and must not be disposed). Table children
7 -> 1 after removal.

**78 THREE objects allocated per frame** (4,680/sec at 60fps): fresh
Vector3/Quaternion in `_slaveHost` and `_physPose`, which run per die per
frame, plus the landing pose being rebuilt every frame although it never
changes for a given roll. Scratch objects + the landing pose cached on the
solve. Measured after: **0 allocations per frame**, faces still correct.

Baseline for reference: 0.24 ms/frame, 13 draw calls, 13 rect reads, no
computed-style reads, no resource growth across repeated rolls.

**Selection outline.** Reuses the outline hull that already works: a second,
thicker copy at scale 1.15 (the material outline is 1.055) in gold #ffd98a,
no grain, shown only while the host carries `.selected`. It hugs the die
silhouette wherever physics left it, which the DOM ring never could now that
dice sit at angles — so that ring stays hidden and there is no double outline
(verified: wrap::after computes to display:none while selected).

## P186 — selection outline, the mass jitter, and dice leaving the frame

**Mass jitter on selecting.** `_measureHomes` CLEARED every match die's
transform in order to measure its untransformed box — so every die jumped for
a frame. And `_homeOf` calls it whenever any die lacks a cached home, which
can be every frame (a die that physics does not own has its home cleared each
pass). One homeless die therefore shook the whole row. It never needed to
touch the DOM: we know exactly what translate we applied, so the home is now
`rect - appliedTranslate` (`d.tx/d.ty`). No writes, no jump. Verified:
selecting a die moves **0 dice, 0.00px**, stable across frames.

**Two outlines.** The gold hull was at scale 1.15 against the material
outline's 1.055 — far enough out that it read as a second box rather than an
outline. Now 1.085. Colour was `#ffd98a`, which against a bone die reads as
white; now `#e1a755`. And every DOM selection decoration (ring, halo, box
shadow, both pseudos on the die and on its wrap) is switched off for a 3D
die — verified all five compute to none while selected. A DOM ring can only
ever be an upright box, which is exactly what was appearing around dice that
now sit at angles.

**Dice off the edge.** The relax pass could push an end die past the screen.
`_physSolve` now takes a `limitX` — how far from the row centre a die can sit
and still be fully visible, derived from the mount width — and clamps the
relaxed positions to it. Verified: 0 dice off either edge, nearest 11px in.

## P187 — review findings fixed: hit boxes stop drifting off the dice

A four-lens review (lifecycle / per-frame cost / physics correctness /
integration), each finding then attacked by a skeptic: 19 raised, 3 survived.
Both player-facing ones were confirmed against the code before fixing.

**1. The game animates `transform` on the very element we slave.**
`@keyframes pxDieTap{0%{transform:scale(.92)}...}` fires on EVERY tap, plus
die-sel-pop, die-pos-pulse, die-freeze-shake and die-shatter. A running
animation outranks inline style, so for its duration our translate was wiped
and the hit box snapped back to its flex slot while the die stayed where
physics put it — measured drift up to a third of a die.

Fixed by moving to the **`translate` property** instead of `transform`. They
are separate properties, so the two compose rather than fight: during a tap
the die now carries `transform: matrix(0.92,...)` AND `translate: 98.6px
-12.1px` at once. Also stopped deriving the table's scale from the live
(tap-scaled) box — a single tap was rescaling the whole table group — and
cached the untransformed width instead. The `transition:none` override is
gone too, since `transition:transform` never applied to `translate`; the
game's own tap feel is restored.

**2. A die leaving mid-turn shifted every survivor's hit box.**
`.die-wrap:not(:has(.die)){display:none}` collapses the emptied wrapper, so
the centred flex row re-centres and every cached home is stale by half a slot
(~25px measured). Live paths: obsidian/lucky shatter, the Sacrifice card, and
cutpurse — all during the choosing phase, while the survivors are clickable.
Homes are now re-measured when the row's die count changes. First attempt
counted the row's CHILD ELEMENTS, which never changes — the empty wrapper
stays — so it counts `.die` elements now.

**3. The shadow scratch canvas was rebuilt nearly every frame** mid-roll: its
cache key was the live projected extent of a tumbling cube, which sweeps
1.0-1.73x its width. Quantised to 32px steps.

Verified worst hit-box gap across all six dice: **0.06px idle, 2.47px during
a tap animation, 0.09px after a die is removed mid-turn** (was ~25px).

## P188 — the legacy engine stops animating match dice

The review's most useful finding was not a bug: the CSS-cube engine was still
fully animating every match die — integration, neighbour shove and ~24 style
writes per die per frame, measured at **0.5 ms/frame across 54 elements** —
on a subtree that is hidden. It could not simply be switched off, because
D3X CONSUMED its output: the mirror branch read `e.pitch/yaw/spin/h/x/ox` to
pose any die that had not been through physics. That entanglement was the
complexity, so the fix is a deletion rather than another guard.

The 3D path now owns it outright. A match die with no physics pose sits at
its DOM slot in the shared rest pose — no mirroring, no shove — and the
legacy engine skips owned dice in `D3.draw`, in the integration loop and in
the group shove. Its whole slot is hidden now rather than just the cube,
which also disposes of the old ellipse shadow.

Deleted with it:
- `_cssQ` + `_deltaQ` — the entire y-down-to-y-up mirror, the one piece of
  code that required the two engines to agree about anything
- `_contact`, `_mkShadowQuad`, `_shadowTex` and the `SHADOW_*` dials, dead
  since the 2D shadow pass took over in P182
- `_mkShadow` and the shadow-twin (`SHADOW:false` was hardcoded, so the twin
  had never been built)

D3X is 967 lines, down from 993, and does strictly less per frame. Verified
in a live match: 6/6 dice settled, faces correct, all six skipped by the
legacy loop (`D3.draw` for them costs 0.000 ms), all six slots hidden, frame
time 0.21 ms (was 0.24).

## P189 — tighter edges, no specular anywhere, dice stop bunching

**Tighter model.** The bevel was 25% of the half-size, which is what made the
die read soft. Now 8%. The mesh is not regenerated but RESHAPED: every vertex
sits at `P = a + r*dir` with `a` on the core box, so shrinking the round-over
is just recomputing that with a smaller r and a larger core. Topology, the
vertex ring at the seam and the six-island unwrap all survive. Overall size
is unchanged to six decimals.

The art is remapped rather than left to shift. The flat face now takes
**93.6%** of each island, up from 79.3%, so a straight copy would have left
the pips looking ~14% small. The remap is piecewise linear in island space —
flat to flat, curve to curve — so pips keep the size they were painted at.
Both bone and amber were rebuilt from Denis's PNG sources.

**No specular.** The die material is `MeshLambertMaterial` now, not Phong —
Lambert has no specular term at all, so there is nothing to leak back in.
`SPEC` and the spec-map plumbing are deleted with it.

**Bunching.** `spreadTo` 1.5 -> 1.75, but that alone made it worse: six dice
at 1.75 need 8.75 die-widths and the row only has 8.26, so the on-screen
clamp stacked them on top of each other (measured: two dice at an identical
x). Two fixes — the wanted spacing is now capped at what the row can actually
hold, `(2*limitX)/(N-1)`, and the clamp runs AFTER the centring shift instead
of before, since shifting a clamped row just pushed the end dice back off.

Measured over 20 rolls at each count, with the real screen limit:
- 6 dice: 0 wrong faces, **0 offscreen**, gaps 1.39-1.65 median
- 3 and 2 dice: 0 wrong, 0 offscreen, a clean 1.75 every time
- worst-case silhouette overlap 1 pair in 300, at 45 degrees to each other

## P190 — the magnet was a broken limit; the tap bounce was a shared scale

Two call-site bugs. My P189 test passed the screen limit in by hand, so it
verified the function and never saw what the game actually computes.

**"Pulled magnetically together."** The limit was

    limitX = Math.max(1, (mrw/2 - mid - sz*0.75)/sz)

but `mid` is ALREADY the row centre in mount space, so `mrw/2 - mid` is about
zero, the whole thing clamped to 1, and the adaptive spacing cap
`(2*limitX)/(N-1)` came out at **0.4 die-widths for six dice** — the relax was
actively pulling them into a pile. It is the distance from the row centre to
the nearer edge: `(Math.min(mid, mrw-mid) - sz*0.75)/sz`, which measures 4.25
in game where it used to give 1.

**Then they came out ruler-straight** — every gap exactly 1.70. `spreadTo` is
a FLOOR, and 1.75 sits above the row's natural pitch (~1.6), so every pair was
below it and every pair got pushed to precisely the floor. Now 1.45: below the
pitch, so only genuinely-close pairs are nudged, and still clear of the 1.414
two dice need when both are turned 45 degrees. Measured live over four rolls:
gaps 1.45 / 1.45 / 1.45 / 1.45 / 1.5 / 1.59 / 1.68 / 1.73 / 1.74 — six
distinct values, min 1.45.

**"Tap the amber and they all bounce."** The table is ONE shared group, and
its scale was being set per die from that die's box — so the last die
iterated won, and a die mid tap-animation (`pxDieTap` scales 0.92 to 1.04)
rescaled every die on the table. The scale is now computed once per frame
from a width captured when the die was first tracked, before any animation
can touch it. Verified: table scale 31.967 before and during a tap, and every
die's position identical.

## P191 — the settle shift hides in the tumble; shadows leave with the dice

**The shift when settling.** The spacing correction was blended into the LAST
16 frames — which is precisely when the dice are nearly still, so it read as
them sliding into place. It now blends between 22% and 62% of the flight, on
a smoothstep, while they are still bouncing: by the time they come down they
are already at the corrected positions and nothing moves afterwards.

Measured over 20 rolls: drift across the last 10% of the flight is **0.044
die-widths (1.4px)** — that is the dice's own settling, not the correction.
Gaps stay varied: 39 distinct values, 1.45 to 2.26.

**Shadow outliving the die.** The 2D shadow canvas is only repainted on the
candle timer, so when a die left (passing the turn, banking) its shadow stayed
behind. `_drop` now marks the pass dirty and it repaints immediately. Two
details mattered:
- it has to run in `tick()`, not at the end of `frame()` — `frame()` returns
  early once the last die is gone, which is exactly the case that matters;
- and AFTER the sync that drops the die, not before, or the repaint happens a
  frame ahead of the removal and you still get one stale frame.

Verified: 4772 shadow pixels with dice, **0 on the same frame** the dice are
removed.

## P192-P193 — real gaps, lower row and pool, rougher outlines, 2D glow

**Minimum gap, measured edge to edge.** A centre distance cannot express "a
finger of table between them": a die turned 45 degrees is 1.41 wide where a
square-on one is 1.0, so the same centre distance reads as touching or as
roomy depending purely on spin. Each die's footprint is now derived from the
yaw it actually landed on — `(|cos y| + |sin y|)/2` — and the relax enforces
`extA + extB + gap`. The squaring-up rotation had to move ahead of the relax,
since the yaws are its input. `PHYS.gap = 0.3` die-widths, shrunk only if the
row genuinely cannot hold it. Measured over 20 rolls: min gap 6px, median
9.6px, **none touching**, 0 wrong faces, 0 offscreen.

**Row and candlelight.** Dice row lowered (`--sp-before` 1.1 -> 1.75), and the
candle pool moved down with it (centre 0.44 -> 0.52 of the screen) and scaled
30% (rx 0.52 -> 0.676, ry 0.27 -> 0.351). The prop-darkening falloff uses the
same centre and radii, so props and dice stay lit by one light.

**Outlines** darkened hard (`OUT_DARK` 0.72 -> 0.42, saturation up to 1.6) and
roughened: the grain texture's contrast is doubled and each die's outline
weight varies +/-25%, so no two lines are the same.

**Selection glow, in 2D.** The 3D gold hull is gone. The die's eight corners
are projected and gift-wrapped into its real silhouette, then drawn on a
canvas above the dice: a wide blurred fill, a tighter brighter one, a gentle
wash over the die itself, and a crisp line — all in the same colour, which is
what the reference does. Screen space, so it reads identically whatever angle
the die landed at. Verified: 4107 lit pixels while selected, gold
RGB(226,167,85), 0 when deselected.

## P194 — the pips were a stale build; glow rebuilt as a real halo

**Pips vs code — Denis was right, and it was a stale asset.** Traced it
properly rather than guessing:

- his SOURCE `bone_diffuse.png`: islands hold 1,2,3,4,5,6 — correct
- the SHIPPED skin: 1,**4**,3,**5**,**2**,6 — a 2/4/5 three-cycle
- the atlas baked into the GLB: correct
- feeding the current source through the current remap: correct

So the remap was innocent (proved separately on a synthetic sheet where each
island is a solid colour — nothing moves between islands). `skins.js` was
simply built from an OLDER version of the PNG, before Denis repainted it, and
never rebuilt. Regenerated from the current sources; the shipped skin now
reads 1-6 in order.

Worth keeping: the first in-game probe reported wrong faces for a different
reason — it projected `d.obj`'s local +Y as "the top face", but the object's
local axes are the MESH's, not the pose's. The corrected probe finds the top
face by testing each painted face's normal against the table's up vector, and
confirmed `codeAgreesWithGame: true` — the up-face has always matched the
value the game rolled. Only the paint was stale.

**Selection glow.** It was filling the silhouette and blurring in place,
which put the glow INSIDE the die - hence the washed-out faces. It is now
built the right way round: blur the silhouettes on their own surface, then
PUNCH THE DICE BACK OUT (inset ~2.5px so the glow laps the edge), and
composite with `lighter` so it reads as light rather than paint. Three blur
passes, since the punch-out removes the inner half of every blur and without
a tight pass the rim never gets bright. Measured through the bottom edge:
0 inside the die, 253 at the edge, falling 79 / 47 / 20 / 2 outward.

**Kept-tray preview** above the row is hidden — the running total under the
row already says it.

## P195 — the glow finally sits outside; rounder die; weighted outline

**Why the glow kept landing on the face.** Two causes, both mine:
1. the halo was built from the die's GEOMETRIC hull (its cube corners), but
   the die is DRAWN with an outline hull around it at ~1.068 — so the painted
   edge was outside my glow boundary and the punch-out landed on the face.
   `_hullOf` now expands by the die's own recorded `outScale`.
2. `destination-out` only partially clears an ANTIALIASED boundary, and with
   the rim passes stacked that leftover read as glow on the die. The cut-out
   is widened 1.6px past the edge.

Rebuilt as: one wide soft pass for the falloff, four tight passes for the
rim (the punch throws away the inner half of every blur, so a single pass
never reads bright), cut the die out, composite with `lighter`. Measured
outward from the painted edge: **0 at 4/8/14px inside**, 255 at the edge,
then 179 / 102 / 53 / 28 / 12 / 3. The 255 exactly at 1px inside is the crisp
outline stroke, which is meant to sit on the edge.

Still to add, per Denis: a very subtle inner glow at the edges to fake bounce.

**Rounder again**: bevel 8% -> 12% of the half-size, same reshape-not-rebuild
approach, UVs rebuilt, and the art remapped **from Denis's sources in one
hop** (flat share 79.3% -> 90.3%) rather than remapping the already-remapped
copy, so nothing compounds.

**Weighted outline**: the outline hull is nudged toward screen-down each
frame, in the die's own local space, so the ink reads thin along the top edge
and heavy along the bottom whatever way the die is turned. Measured across
four dice: top band 2.75px, bottom band 4.75px.

## P196 — the lag, the leftover glow, and the outline weight

**The leftover glow (and probably the "vagabond glow").** The glow canvas was
only drawn from `frame()`, which returns early once the dice are gone — so
whatever was last painted stayed on screen with no dice under it. Denis saw
two glowing outlines floating on an empty table after passing his turn; the
"glow around the vagabond die" was almost certainly the same stale paint. It
is driven from `tick()` now, like the shadows, and clears itself whenever
there is no selection, no match, or the dice are mid-air.

**The lag.** Two real costs, both in the 2D passes rather than the 3D:
- `_diceShadowPaint` re-scaled the **1080x2011** table PNG for every die on
  every pass — six resamples of a 2Mpx source, 25 times a second. The unlit
  table is now pre-scaled ONCE per layout and blitted 1:1. Measured: the
  whole dice-shadow pass **1.37ms -> 0.30ms**, a 4x cut, and it is the kind
  of work Firefox is much slower at than Chromium.
- shadows and glow are now skipped entirely while any die is in the air
  (`_rolling()`), which is when the frame budget matters and when neither can
  be read anyway. The shadows repaint the moment the last die settles.

Verified: shadow ink 0 in the air, 14319 once landed, 0 after the dice leave;
glow 0 idle, 8003 selected, 0 deselected, **0 after the dice leave while
still selected** — the exact case Denis hit.

**Outline** base thinned (0.055 -> 0.040) with a gentler screen-down weight
(0.055 -> 0.022) so the heavy side lands back where it was and only the top
thins, and darkened again (`OUT_DARK` 0.42 -> 0.26, saturation 1.7).

**Glow brighter**: soft blur 16 -> 22 with two passes, rim 4 -> 6 with seven.

**Rounder still**: bevel 12% -> 16%, art remapped from Denis's sources in one
hop (flat share 87.0%).

## P197 — the red glow found, a brighter halo, shadows that fade in

**The vagabond's red glow.** Not the selection glow at all: premium materials
paint a coloured halo on their WRAPPER —
`:where(.die-wrap,...)[data-mat="vagabond"]::before` with
`rgba(255,80,100,.55)`. It is drawn at the DOM slot rather than where the die
landed, and 3D dice have their own glow, so both wrapper pseudos are switched
off for match dice. Verified: the wrap's ::before computes to
`background:none, box-shadow:none`.

**Glow brightness.** A mid gold on a warm table just blends. It is two-tone
now: the wide falloff spreads in gold (`SEL_SOFT #ffb552`) and the rim is
near off-white (`SEL_COL #ffeec2`), both composited additively. Measured:
peak alpha **255** at colour (255,238,194), average across the halo
(255,195,110).

**Shadows fade in, and early.** They were appearing in a single frame the
moment the last die stopped. `_settleK()` now ramps from 0 to 1 across the
last stretch of the flight (55% to 92%), the shadow alpha is multiplied by
it, and the pass keeps repainting while the ramp is mid-way. Measured across
a real solve: 0 / 0 / 0 / 0 / 0.12 / 0.40 / 0.66 / 0.81 / 0.94 / 1 / 1 at
flight progress 0 to 1 — starts at 60% of the flight, seven distinct steps.

**Outline wobble removed**: the per-die random weight is gone, every die's
outline is a uniform 1.04. The screen-space top/bottom weighting stays.


## P198 — the glow goes gold, the seam closes, the shadow softens

**Warmer.** `SEL_COL` `#ffeec2` → `#ffd98a`, `SEL_SOFT` `#ffb552` → `#ffa63a`.
The off-white rim read as a lamp, not as gold.

**The hairline between outline and halo.** Two causes, one fix each. The
stroke was painted on the MAIN canvas after the halo surface had already
been composited, so the two were separate layers with nothing guaranteeing
they met; and the `destination-out` punch cleared `clear:1.6` inward while
the stroke only reached `line/2 = 1.2` — a 0.4px ring of bare table between
them. The stroke now goes onto the SAME offscreen surface, after the punch,
so both composite as one additive layer; and `clear` is `0.7` against a
`line` of `2.8`, so the stroke covers the cut with room to spare.

Measured on a scan running outward from a selected die's centre: alpha
`0,0,…,0, 26, 228, 255, 254, 250, 245, 237, …, 4, 2, 0` — monotonic from the
rim out, no zero in the middle. Colour at the peak is exactly (255,217,138)
= `#ffd98a`, drifting to (255,166,58) = `#ffa63a` through the falloff, which
runs ~58px.

**Shadow fade earlier and longer**: `SHADOW_FADE` `{0.55, 0.92}` →
`{0.32, 1.0}`. It now starts a third of the way through the tumble and only
reaches full on the last frame.

**The drop shadow is blurred**: the hull mask in `_diceShadowPaint` is filled
through a `blur(max(1.5, size*0.05))` filter. Measured down through a die:
alpha `255 … 194, 106, 104, 65, 22, 0` — a five-pixel ramp at a 32px die,
scaling with the die.
