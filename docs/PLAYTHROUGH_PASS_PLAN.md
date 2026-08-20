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

## Step 2 — functional audit of ALL cards (the actions, not the text)

P776 audited words; this audits WIRES. A harness drives every family
card's player route AND rival route through the real seams and asserts
the observable effect (state delta, not log lines). Ground truth:
CARD_EFFECT_SPECS_FULL.md. Deliverable: a per-card verdict table;
fixes for every break. (Denis: "You need to check card actions are
actually connected to the game.")

## Step 3 — boss dialogue silent (Grog)

No dialogue during his match. Reachability first: do DLG triggers fire
in boss matches at all (OPP_BIG_BANK etc. exist in code); find where
the boss-match path fails to arm them.

## Step 4 — small UI correctness

- BANK button does not consistently become "BANK TO WIN".
- The boss win screen must show the card draft like a regular win.

## Step 5 — dice feel

- Busted dice must SETTLE ON A FACE - no edge-standing "no gravity"
  poses. (Suspect: the bust kick rides on a phys pose frozen before
  the settle finished.)
- Scatter wider and FASTER; break the lane look at the bust moment if
  cheap, ignore if risky (Denis's own risk call).
- Rolled dice minimum spacing (some land nearly touching).
- RECORDED, not acted (Denis: "don't act on it"): group the dice at
  the throw's start so they read as coming from a hand or goblet.

## Step 6 — patron leveling (PATRON_LEVELING_BRIEF.md)

The spec exists in the master doc; verify before building:
does loadout generation read the trait->family bias at all; does card
count key off the actual night; do the three six-way taxonomies'
literal keys line up (strong-vs-bullish class of bug). Then: cards 0-1
early -> 3 late with the player's tier night-locks, die family bias by
persona. Growth dialogue mechanism (band-4/band-7 pools + the rare
recognition beat) after the mechanics; the LINES exist in
PATRON_GROWTH_LINES.md.

## Step 7 — presentation pass

- Enchant descriptions pass (Fog first).
- Fog's lingering table visual until it fires.
- The 24-card visual spec pass (CARD_EFFECT_SPECS_FULL.md) - the long
  arc: arm markers, re-roll beats, score-breakdown attributions.

## Standing rules for this pass

- Verify before fixing; the probe IS the verification.
- One step ships (commit + deploy) before the next opens.
- Look values move only at Denis's request.
- Resume/save survives every touched flag (famPeekVals shape!).
