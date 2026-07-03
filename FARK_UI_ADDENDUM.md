# FARK — addendum: screens, wording, and UI reconcept

Companion to FARK_LOOP_BRIEF.md. That doc is the mechanics; this one is the
screens and copy as finalised AFTER it was written. Where the two conflict,
THIS DOC WINS. Conflicts are flagged inline as SUPERSEDES.

## Global copy principles

- The game explains itself in tavern language, never in game-system language.
  No "points", no "marks", no "seats", no "tier" in player-facing text.
- The boss does the counting, not a HUD stat. Cause and effect must be
  literally drawn on screen (see chalkboard below).
- Animal flavour stays light: species and one prop per character, plus the
  occasional "lad" in dialogue. No Zootopia-style species lore or puns.
- Text is sentence case except carved/stamped labels which are caps.

## Screen: the Room (replaces the tier screen)

SUPERSEDES the P1 tier screen description in the main brief.

- The tier screen is themed as the tavern room for the current night, on a
  painted tavern plate (see P9 layer rules).
- Patrons appear as portrait frames hung like tavern signs, roster of
  pointsNeeded+2, generated at night start (mechanics unchanged from P1).
- Each frame: portrait sprite, name, one stamped trait word (persona-derived,
  e.g. RECKLESS, HOARD, CAREFUL), the patron's six dice as small chips, a
  parchment stake tag (buy-in, e.g. 15g).
- SUPERSEDES "WON/LOST stamps on spent seats": a played patron GOES HOME.
  Their frame empties to a vacant stool silhouette with a small handwritten
  tag reading GONE HOME. Win or lose, same visual; the room drains over the
  night. No seat counters, no spent labels anywhere.
- One random frame carries a purple wax seal = the handicap offer seat
  (mechanics per main brief P1).
- The shop and the Innkeep's Book are IN the room (the innkeep at the bar is
  the tap target for both), not separate menu buttons. Boss sits at the back.

### The chalkboard (replaces points UI)

SUPERSEDES all "0 / 2 MARKS" or points-tally UI.

- A chalkboard beside the boss reads: [BOSS NAME] PLAYS WINNERS.
- Below the line: N chalk circles where N = pointsNeeded for the tier.
- Beating a patron chalks that patron's face into the next empty circle
  (small sketched portrait, can be a generic chalk face variant per species).
- Handicap wins fill two circles (chalk the face plus a crown or double
  stroke on the second).
- All circles filled: the board text swaps to [BOSS NAME] WILL PLAY YOU NOW
  and the boss frame lights up. Remaining patrons stay playable (bounded
  greed, per main brief).
- This board IS the progression UI. No numeric points appear anywhere.

## Interaction: the peek card (sit-down flow)

- Tapping a patron frame slides up a bottom-sheet peek card: portrait, name,
  trait word, their six dice chips, target score, stake (buy-in), pot
  (what a win pays). One button: SIT DOWN.
- The peek is the misclick guard and the scouting moment. It must be fast:
  instant or near-instant animation; a second tap on an already-peeked
  patron can sit immediately.
- Tap count parity note: end overlay folds the draft in (already the case),
  so the loop is end overlay > room > tap frame > SIT DOWN > match.

## Screen: match HUD additions

Per main brief P3, plus final presentation decisions:

- Turn counter reads TURN 5 / 8 in the HUD strip. Always visible.
- The pot (buy-in stakes) sits ON the table as a coin pile sprite with a
  small tag (POT 45g), not in the HUD. Pot pile scales with amount.
- Opponent presence at the top edge of the table plate: head plus
  hands/hooves over the table lip, their dice row, speech scraps as
  parchment sprites. Per P9 layering.

## Screen: victory overlay

- Title, both scores, then the pot payout presented as a single pot number
  (buy-in returned + reward together), coins visually sliding to the
  player's edge.
- Draft row of three cards, plus a fourth smaller parchment option reading
  SKIP +Xg (amount per main brief P7).
- Card design language: heraldic. Flat medieval shield-style compositions,
  two or three colours per card, one bold central symbol, rarity as border
  material (tin/silver/gold as now). Extremely readable at thumbnail size.
- One CONTINUE button returns to the room, where the beaten patron's frame
  is now GONE HOME and their face gets chalked onto the board (animate the
  chalking on return, it is the reward beat).

## Screen: defeat overlay

SUPERSEDES any BUY-IN LOST / SEAT SPENT labels.

- Title, both scores. The patron is shown leaving: coat on, mocking
  farewell (sprite pose or reuse portrait with an exit line).
- One handwritten exit line on parchment, drawn from a per-persona line
  pool (e.g. BETTER LUCK TOMORROW, LAD). Add a small line pool per persona
  to OPP_DIALOGUE or a new EXIT_LINES const.
- The gold loss shows as coins sliding off the table edge with a small -15g
  tag. No system wording.
- Button: BACK TO THE ROOM. On return, their frame is GONE HOME. No other
  penalty messaging (the drained room is the message).

## Screen: LAST ORDERS (night fail)

As per main brief P1, presentation locked:

- Near-dark room plate, stools up on tables, innkeep wiping a mug.
- Title LAST ORDERS. One heart visibly breaking out of the three.
- Copy: THE ROOM EMPTIES. A NEW CROWD TOMORROW.
- Button: NEXT NIGHT (re-rolls the roster, resets the chalkboard).
- Must be impossible to misread as a win or a neutral event.

## Screen: dice store

- Framed as the innkeep's bar: innkeep sprite behind the counter, dice on
  shelves with hanging price tags, SOLD tag on empty shelf slots.
- Player's current six dice in a tray at the bottom (tap to compare/swap,
  existing loadout mechanics unchanged).
- Same layer rules: shelf plate, dice rendered programmatically or as
  sprites consistent with the match dice, prices in HTML.

## Hearts reframe

- Hearts are presented as the innkeep's patience, not abstract lives.
  Losing the last one = barred from the tavern (game over screen copy:
  BARRED. Existing run-death flow otherwise unchanged).
- No mechanical change; copy and iconography only.

## Asset dependencies (coordinates with P9 in the main brief)

New assets this addendum implies, beyond the P9 list: vacant-stool frame
state, GONE HOME tag, chalkboard blank plus chalk face variants (per species
or generic), wax seal, peek card sheet blank, exit-pose or reuse of portraits
for defeat, innkeep bar plate for the store, night-fail room plate.
Everything textless; all copy above is HTML.

## Build order suggestion

1. Chalkboard + GONE HOME frame states (pure UI over existing mechanics).
2. Peek card flow.
3. Victory/defeat overlay rework with the copy above.
4. LAST ORDERS overlay (needs P1 night-fail mechanics in place).
5. Store and room reskin last; they work visually rough in the meantime.
