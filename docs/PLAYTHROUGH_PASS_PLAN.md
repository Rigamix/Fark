# Playthrough pass — the plan (2026-08-19, Denis's notes)

Denis: "Plan ahead, let's take it in steps. No mistakes." Every step
ships with an execution-witness probe; nothing closes on a grep or a
read alone. Source briefs live beside this file:
PATRON_LEVELING_BRIEF.md, PATRON_GROWTH_LINES.md,
CARD_EFFECT_SPECS_FULL.md (exact card texts = audit ground truth).

## Step 1 — the four named accusations (correctness first)

- **1a STARGAZER (player) — CONFIRMED BROKEN, fixing now.** The peek
  pre-rolls values for the current free dice and stores them BY INDEX;
  famApplyRollForces only applies them when the next roll's free count
  matches exactly. Rolling requires keeping a scorer first, so the
  count almost never matches: the peek is silently discarded and the
  roll is genuinely random. The rival's own version (per-seat) works.
  Fix: peek keyed by LANE, consumed per-die by whichever dice roll;
  kept dice simply never consume theirs. Probe: peek -> keep -> roll,
  every rolled die equals its lane's promise; resume shape migrated.
- **1b SLEIGHT (player) — connected but invisible.** The rival's first
  deal IS rerolled (flag consumed at their deal, values replaced) but
  it happens before anything renders, so the player sees only the
  final values: mechanically live, visually "did nothing". Verdict
  recorded; the visible re-roll beat (their dice land, pause, visibly
  come back different - the card spec's own requirement) lands with
  step 7's visual pass.
- **1c DOUBLE STAKES — display drift, two peek surfaces.** The launch
  settle doubles the buy-in correctly and the gauntlet sheet (_gbPeek)
  shows doubled numbers - but the ROOM's seat panel (_ptSeats), the
  surface Denis actually checks, never reads _dsArmed. Fix the panel;
  ALSO verify the WIN PAYOUT doubles in the settle (the display must
  not vouch for the pot).
- **1d FOG — implemented, invisible by construction.** Fog marks one
  opponent lane and blinds the NPC's chooser to that die (the effect
  lives inside their decision). Verify it truly reaches the chooser
  (execution witness), then step 7 gives it the lingering table visual
  Denis asked for + a clearer description.

## Step 2 — functional audit of ALL cards (the actions, not the text) — DONE 2026-08-20

Complete: all six families + tavern + all eight enchants, verdicts in
docs/CARD_AUDIT_2.md. Broken and fixed: stargazer (P811), double
stakes panel (P812), slow_cook roll ordinal (P813), retort's dead
second trigger (P814, new cardHit seam), tamper vs the bus (P815,
broken cards now silent). Two spec divergences parked in OPEN.md
(sacrifice pays the bank not the turn; double_or_nothing arms
pre-bank). Rival-route regression sweeps rerun clean.

P776 audited words; this audits WIRES. A harness drives every family
card's player route AND rival route through the real seams and asserts
the observable effect (state delta, not log lines). Ground truth:
CARD_EFFECT_SPECS_FULL.md. Deliverable: a per-card verdict table;
fixes for every break. (Denis: "You need to check card actions are
actually connected to the game.")

## Step 3 — boss dialogue silent (Grog) — DONE (P818, 2026-08-20)

Root: bosses were bypassed into the emptied OPP_DIALOGUE store and had
no seat identity. Fixed: bypass deleted, BOSS_TRAIT stamp (launch +
resume), ledger greetings revived. Probes: tools/apv_boss_dialogue*.js.
Content gaps (boss :open pools, triggerCard barks, trait remap) in
OPEN.md.

## Step 4 — small UI correctness — DONE (P819+P820, 2026-08-20)

- BANK TO WIN: winning-press latch restored, sealed LAST CALL and tab
  escrow modeled, slow_cook/hangover projected, label self-heals from
  updHUD. Probes: tools/apv_bank_label_*.js. The full dry-run bank
  oracle (card ×2 stack, short_fuse preview, rival deductions) is an
  OPEN.md question.
- Boss win draft: chains after the spoils pick, same offer/funnel,
  SKIP pays 75% of the BOSS purse. Ambrose keeps his renown-only final
  screen. Probe: tools/apv_boss_win_draft.js (screenshot verified).

## Step 5 — dice feel — DONE (P821, 2026-08-20)

- Busted dice settle FLAT: the kick's yaw was composed in the die's
  LOCAL frame (only faces 2/5 have their normal on mesh Y), so 1/3/4/6
  rolled over — measured 8/10 cocked pre-patch, 18/18 flat after
  (premultiply = world-up yaw). Probe: tools/apv_bust_dice_flat.js.
- Scatter wider + faster: KICK ms 620→460, dist 0.85→1.15 (P743's 1.5
  was too strong), stagger 70→55ms/die-width.
- Spacing: sim collider proxy 1.06→1.22 die-widths (was narrower than
  the painted die, allowing on-screen overlap; the old 'fights the
  pen' warning is obsolete — the slot pen is dead code).
- Hand/goblet gather at throw start: recorded, deliberately not acted.

## Step 6 — patron leveling — CORE SHIPPED (P822), rulings in OPEN.md

Recon: the brief's card ramp was already implemented and night-keyed;
the die-family bias was dead (P822 wires it: bias lists + tier pools,
probe-verified leans, nights 1-2 mundane). Parked for Denis: rival
obsidian shatter, tier-III lock semantics, persona↔name binding, the
band-lines resolver exclusivity — all in OPEN.md.

## Step 7 — presentation — TOP OF THE LIST SHIPPED (P823-P824); ranked backlog in OPEN.md

- Enchant descriptions pass (Fog first).
- Fog's lingering table visual until it fires.
- The 24-card visual spec pass (CARD_EFFECT_SPECS_FULL.md) - the long
  arc: arm markers, re-roll beats, score-breakdown attributions.

## Standing rules for this pass

- Verify before fixing; the probe IS the verification.
- One step ships (commit + deploy) before the next opens.
- Look values move only at Denis's request.
- Resume/save survives every touched flag (famPeekVals shape!).
