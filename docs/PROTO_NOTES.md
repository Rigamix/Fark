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
