# FARK — MATCH SCREEN BUILD BRIEF

For Claude Code. Sits UNDER FARK_MASTER_BRIEF.md (rules/content) and
FARK_UI_ADDENDUM.md (dice renderer). This brief specifies the match
screen only: layout, layers, states, and interactions, as validated in
the greybox prototype (fark_greybox.html) and the painted mockups.
Where this conflicts with older match-screen code, this wins.

Baseline design frame: 390x844. All px values scale proportionally.
Safe-area padding at top (notch) and bottom (gesture bar) required.

## 1. LAYER STACK (bottom to top)

1. TABLE PLATE — one full-screen painted background per night band
   (rough / mid / fine; 2-3 total, NOT per patron). Near top-down
   camera, soft central light pool baked in, centre band clean.
   Boss matches instead use that boss's bespoke full plate (boss
   painted in, upper two thirds).
2. PROPS LAYER — individual PNG sprites (mug, candle, coins, cup,
   jug, cloth...) placed from HAND-AUTHORED TEMPLATES at match start.
   Each sprite has its own baked contact shadow.

   REVISED 2026-08-02 to match what shipped. The original spec below
   was written before the templates existed and is wrong on two counts;
   the art was ruled correct and this text is what changes.

   PLACEMENT IS AUTHORED, NOT PROCEDURAL. The spec called for fixed
   anchor slots with a per-match seeded shuffle filling 3-5 of ~8.
   Shipped: `FK_PROP_TEMPLATES`, hand-made sets (currently 2, of 11 and
   12 props), placed whole. No shuffle, no fill count. A human
   composing a table beats a scatter function, and the shipped system
   deliberately lets the template win.

   THE EXCLUSION ZONE WAS STATED ON THE WRONG AXIS. The spec banned a
   central VERTICAL band (x 15%-85%). Measured with six dice on the
   table, the dice occupy x 7.7%-97.6% — very nearly the full width —
   inside a narrow HORIZONTAL strip at y 43.3%-53.7%. A vertical-band
   rule cannot express "keep clear of the dice", because the dice are
   not in a vertical band. It is the wrong shape of constraint, so
   props were always going to violate it while looking correct: 10 of
   23 prop centres sit inside x 15-85 (clustered x 76-85, hugging the
   right margin) with painted extents reaching in to x 62, and the
   composition still reads clean.

   THE RULE THAT REPLACES IT is the one this section already stated as
   its intent, kept and promoted: PROPS NEVER OVERLAP DICE, TAGS, CARDS
   OR BUTTONS — expressed as an overlap test against live UI, never as
   a coordinate range.

   AND THE SHIPPED TEMPLATES CURRENTLY FAIL IT. Measured on a live table
   with six dice down: 9 bounding-box overlaps across 4 props — spoon,
   bottle, plateMetal, bag — all against dice. Showing the old rule was
   the wrong shape did NOT show the art was clear; both were true at
   once, and only running the new check separated them.

   What the box test cannot say is whether that matters. DICE PAINT
   ABOVE PROPS, so an overlap reads as a die resting on the table
   clutter rather than a die hidden behind a bottle — which is the
   composition working, not failing. So the open question is whether
   the invariant is OVERLAP or OCCLUSION, and that is an art call, not
   a correctness one. `tools/apv_prop_overlap.js` holds the check and
   is red against the stricter reading until it is settled.

   Props may hang off the stage edge (a prop centred at x -14.9 is
   intentional; half a spilled pile reads better than a whole one
   floating). Left/right need not be symmetric — the shipped pair runs
   9 left, 14 right.
3. OPPONENT PRESENCE — patron matches: paws + muzzle sliver entering
   from the top edge (one sprite set, tinted per patron fur colour if
   cheap; otherwise one generic dark set). Their face-down cards lie
   flat near the paws. Boss matches: the boss is already in the plate;
   no extra presence sprite.
4. DICE LAYER — playground 21 renderer, ported verbatim (addendum).
   Roll area is the central horizontal band. IMPORTANT: wrap the
   resting-state visual behind a single renderDieAtRest(die, faceUp,
   pos) abstraction. Currently it draws the CSS cube; a pending
   art decision (pre-rendered GLB sprites for resting dice) will swap
   that function's internals only. Do not scatter rest-state drawing
   logic around the codebase.
5. UI LAYER — everything below, plain DOM. No UI element is ever part
   of a painted plate.

## 2. LAYOUT BY ZONE (top to bottom)

TOP STRIP (status only, nothing frequent-tap; over the dark area
above the table edge):
- Race bar: horizontal parchment bar, centred, ~70% width. Two fills
  grow toward the CENTRE TARGET CREST (reads the target, e.g. 4800).
  Left fill = opponent (their accent colour), right fill = player.
  Fill length = total/target, capped at the crest.
- Left end: opponent portrait token (round, 44px) with their total in
  chalk beneath. Right end: player token (player crest/blank) with
  player total beneath. BOTH totals live here and only here.
- Under the bar, centred, small chalk: TURN X OF cap. At 2 turns
  remaining: amber tint + one gentle pulse per turn start. Never
  flashing continuously.
- Top-right corner: pause icon, 46px tap target. This is the ONLY
  interactive element in the top strip.
- NO gold, NO hearts in patron matches. Exceptions in §5 and §7.

OPPONENT EDGE (top of table):
- Opponent's face-down cards, small, lying flat near the paws. Backs:
  dark parchment + thick family-colour border + abstract motif. No
  wax seals on card backs (family = border colour, full stop).
- ACTIVE RULES = WORN BADGES: rules have no abstract indicator; the
  badge is shown ON its wearer. Boss/sealed patron: pinned in their
  art or on a small collar chip at their table edge. Player's worn
  badge: pinned at the player's edge beside the cards. Tap (44px+)
  opens a bottom sheet with rule name, full text, binding stated in
  words + a one-arrow / both-arrows glyph, and — for the player's
  badge — the stake reminder "lost if you lose this match". Max 2
  badges visible (boss + player). ZERO rules = zero badge pixels.
  No wax seals here ever (wax = patron traits only).

CENTRE BAND (the game):
- Rolled dice land in one loose horizontal spread with generous
  spacing (playground 21 handles final positions; constrain landing
  targets to this band).
- SELECTION: tapping a die toggles selection; selected dice get a
  warm gold glow (CSS drop-shadow, ~8px, no scale pop).
  - PER-DIE TAGS: each selected die shows its own contribution
    (+100, +50...) as a SMALL tag, ~65% the size of the total,
    offset clearly below the die with a visible gap (~10-12px) —
    never touching or overlapping the die art. Muted cream chalk.
  - TOTAL: one selection total, centred under the dice band, GOLD,
    the most prominent number on the table. Excitement scales with
    value, as one impulse PER VALUE CHANGE (never continuous):
    tier 1 (<300): gold text, soft 6px glow, no motion;
    tier 2 (300-749): glow 10px + quick scale pop 1.0->1.08->1.0;
    tier 3 (750-1499): glow 14px + pop + one short shake impulse
    (translate +-2px, ~250ms, ease-out);
    tier 4 (>=1500): glow 18px + stronger shake (+-3px) + brief
    spark/burst particle. Respect reduced-motion setting: glow
    tiers only, no shake.
  Invalid selections (no scoring subset): total dims to grey 0,
  per-die tags hidden; KEEP semantics disabled; never block the tap
  itself.
- Below the dice band: reserved empty wood. Card effect visuals
  (Ward shimmer, Preserve casing, Short Fuse smolder, positional
  glows, ghost dice) render HERE and on the dice themselves. Do not
  place persistent UI in this band.

KEPT PILE (bottom-left of the table area):
- Kept dice cluster together as one tidy group (rest-state renderer).
- Beside them, one small discreet chalk tag: "650 TURN" (turn bank).
  Small. Secondary. It never grows; the BANK button carries the
  prominent version of this number (§3).
- On bust: the pile's tag crumbles/wipes (0), dice grey momentarily,
  turn passes. Keep it under 600ms; losing must feel quick.

PLAYER CARDS (centred along the bottom table edge, above buttons):
- Three slots, card backs ~56x74px minimum tap target, family-colour
  borders + abstract motifs, tier shown by border metal trim
  (tin/silver/gold) not by numerals at this size.
- Tap a card: it raises and flips face-up in an inspect sheet with
  full text. Passive cards: sheet is info-only. Active cards: sheet
  carries a PLAY button (stake-labelled where relevant, e.g. "PLAY —
  costs your bank"). Targeted actives (Tar Pit, Sleight, Ill Omen,
  Tamper): after PLAY, enter target mode — legal targets highlight,
  everything else dims, one tap resolves, tap-outside cancels.
- Empty slots render as faint slot outlines, not fake cards.

BUTTON ZONE (bottom sixth, inside gesture-safe area):
- Two buttons: BANK (left, smaller) and ROLL (right, larger, primary
  styling). Height 64px minimum, full-width row with 8-12px gap.
- BANK is FIXED-FOOTPRINT with a two-line interior: constant verb
  line "BANK" (anchors muscle memory, never moves or resizes) over a
  small variable CAPTION line that absorbs all states: the amount
  ("650", counts up with a small caption-only pulse on each keep),
  rule truths ("banks 0 — under 500" under LAST CALL — still
  tappable, since a void bank equals a bust and taking the 0 is a
  legal choice; "need 1,200" under RECKONING, flipping to the amount
  once met), and "WINS THE MATCH" when banking crosses the target.
  A small amber pip on the button corner signals an armed bank-time
  sub-prompt (PRESERVE die pick). The button's geometry never
  changes in any state; reserve caption width for 5 digits. ROLL
  follows the same two-line pattern (caption usually empty; "hot
  dice — fresh six" when applicable).
- ROLL disabled during flight and during opponent turns (buttons stay
  visible, dimmed — layout never reflows).

## 3. STATE-AWARE BUTTON LOGIC

- BANK-TO-WIN: when banked total + turn bank >= target, BANK takes
  primary gold styling with one scale pulse (1.0->1.05->1.0) and the
  caption "WINS THE MATCH"; ROLL dims to secondary. GEOMETRY DOES
  NOT CHANGE — no width swap, no reflow; colour and glow do the
  spotlighting so the highest-stakes tap lands on a target that
  hasn't moved. Reverts instantly if a selection change drops below
  the threshold.
- RULE-AWARE BANK: under LAST CALL with turn bank < 500, BANK renders
  struck/void ("BANK — VOID UNDER 500") and banking yields 0 per
  rules; the button tells the truth before the tap. Under RECKONING,
  BANK shows the floor when unmet: "BANK — NEED 1200+".
- Opponent turn: both buttons dimmed; opponent plays out with the
  same dice renderer top-down; their banks tick their race fill.

## 4. TURN & MATCH FLOW STATES

idle -> rolling (flight, ~700ms + stagger) -> selecting (tags live)
-> [KEEP via selection + ROLL again | BANK] -> yield window ->
opponent turn -> ...

NO YIELD PHASE. The live build's post-bank YIELD button and its
'yielding' card-timing window are REMOVED in the redesign. Rationale:
against an AI opponent, the gap between the player's bank and the
opponent's turn contains no new information, so every card formerly
timed 'yielding' retimes to "playable anytime during your turn,
resolves at handover" with zero strategic loss (Ill Omen, Honeytrap,
Tar Pit). The turn hands over AUTOMATICALLY after the bank animation
(~1s, enough for bank dialogue), and after busts immediately.
Sub-case: PRESERVE needs a die choice at turn end — implemented as a
sub-prompt inside the BANK action (Preserve active + BANK -> quick
pick-a-die -> resolve), never as a separate phase. Migration note:
legacy cards with timing:'yielding' either retime or retire per the
master brief's card list; none may reintroduce a handover phase.

- Hot dice: all six used -> fresh six; brief "HOT" chalk flourish at
  the dice band, nothing modal.
- Target crossed by either side: banner strip slides under the race
  bar: "LAST TURN — beat 5120". Other side takes exactly one last
  turn. No modal.
- Turn cap reached both sides: if tied, "SUDDEN DEATH" banner, one
  more turn each until broken. If not tied, resolve.
- Match end: patron win -> victory/draft screen; patron loss ->
  defeat screen (fast). Boss win -> spoils; boss loss -> heart-loss
  modal. No end-of-match stats screen mid-run; keep the loop moving.

## 5. TELLS, RULES, AND CONTEXTUAL HUD

- All active rules render ONLY as the parchment notes at the
  opponent edge (§2). The engine's _ruleActive is the source of
  truth; the note list mirrors it exactly.
- IN ARREARS exception: when active, a small gold chip fades in at
  the top strip's right side and pulses -5g on each player roll.
  It exists only while the rule is live. This is the ONLY time gold
  appears in a match.
- STEEPED: +100 ticks fly to the roller's turn tag. PICKPOCKET: the
  palmed die visibly slides off-table to the opponent edge and
  returns at turn end. Every rule that changes numbers must show its
  change AT the number it changes.

## 6. NPC TELEGRAPH (mandatory, master brief)

Every NPC targeted active telegraphs exactly one roll ahead: the
opponent's relevant card back rises ~6px with a red-edge glow and a
soft sting. On resolution, the card flips face-up at the opponent
edge for ~1.2s with a short name label, then fades. No text walls
mid-match; tap the flipped card to freeze + read full text.

## 7. BOSS MATCH DELTAS

- Boss plate replaces table plate + presence (boss painted in).
- Mini hearts row appears top-left (16px hearts): a heart IS at
  stake. This is the only hearts appearance in matches.
- Turn cap 10. Race bar identical.
- Boss's worn badge binds player only; the player's worn badge binds
  both — each badge sits with its wearer, binding stated on tap.
- Pause menu forfeit reads "FORFEIT — COSTS A HEART".
- Entry comes only from boss peek (badge already pinned there).

## 8. PAUSE PANEL (modal) — merged menu + loadout glance

One hanging banner panel over a dark scrim. Top-to-bottom:
GLANCE LAYER (read-only): the player's six dice in loadout order,
their three card backs, and their worn badge if any — tap any
item for its tooltip sheet; nothing is editable mid-match.
ACTIONS: SCORING & RULES row (sheet: base scoring + the player's
actual dice effects + any active rules) · SETTINGS row.
EXIT PAIR: FORFEIT sits ABOVE resume — smaller, red-tinted,
stake-captioned ("costs your buy-in" / boss: "costs a heart"),
two-step — while RESUME is the large primary at the very bottom, so
reflex taps at the panel's base always land on the safe action.
Long-press any die mid-match opens the same scoring sheet. There is
no innkeep's book; this panel is the rules reference surface.

## 9. DICE ARE PERSISTENT OBJECTS (kept-pile compatibility)

Scoring combos form within a single roll only (Farkle rule), so the
kept pile hides no legal play — but dice must be implemented as
persistent objects whose state travels with them between the roll
band and the pile:
- Per-die markers follow the die everywhere: curse marks
  (COUNTERFEIT), PRESERVE's amber casing, family material, relic
  identity. Never redraw kept dice as anonymous white dice.
- Pile lifecycle: hot dice -> pile animates back to hand and a fresh
  six rolls; SLEIGHT -> pile visibly rewinds and the turn re-runs;
  bust -> pile greys + tag wipes (<600ms). A PRESERVED die SURVIVES
  turn end: it stays on the table in its casing through the pile
  reset and is excluded from the wipe. This holds even if the SAME
  turn later busts — Preserve's whole promise is protection, and a
  bust that also cracked the amber would defeat the card's one job
  exactly when it's supposed to matter. Confirmed intentional, not
  just current behavior. PLAYER CHOOSES which scoring die goes into
  the amber (a tap prompt, not an auto-pick of the first one found)
  — Preserve is scarce (1-2 charges across a whole run) and
  irreversible per use, so a wrong auto-pick costs a full future
  turn with no do-over; the one extra tap is cheap by comparison.
- Kept dice keep readable faces in the pile (max slight overlap):
  players track curses and Preserve choices by looking at them.
- POSITION = LEFT-TO-RIGHT. Landing order IS loadout order: slot 1
  lands leftmost. The landing solver guarantees ordering stays
  legible — vertical jitter free, horizontal jitter small, minimum
  x-gap between neighbours, and collision shoves may never swap two
  dice past each other. Positional cards need no order UI: while one
  is equipped, its scoring dice (Vanguard/Anchor/Bookends) carry the
  master brief's glow spot wherever they sit, including in the kept
  pile (a Bookend die scores from the pile — position is loadout
  slot, not table location). The Vagabond reorder action opens a
  temporary order-strip UI (six slots, drag), closes on confirm.
- SIX FIXED TABLE LANES, one per loadout slot, assigned at match
  start for BOTH sides and held for the whole match (barring a Trade
  swap of what occupies a lane — the lane itself never moves). Each
  lane owns a permanent spot inside the shared central roll band.
  This is what makes lane-targeting enchants (Snare, Trade, Snuff,
  Fog) VISIBLE rather than invisible engine bookkeeping: firing one
  paints a real marker (fog cloud, trap jaws, etc) onto that lane's
  fixed table spot, which stays there — through the turn boundary,
  through rerolls, through hot dice — until the opponent's next roll
  physically lands their lane die into that same marked spot and the
  effect resolves in front of the player. Nothing about this requires
  the die itself to stay put: dice reroll and get kept freely, the
  LANE'S POSITION is what's fixed, not any single die's residency in
  it. Empty lanes (die already kept) render dimmed/empty at their
  fixed spot; an active visual marker persists there regardless.
- KEPT-DICE TRAY may use any layout that reads clearly (keep-order,
  grouped-by-value, whatever) — it does NOT need to preserve loadout
  order, because by the time a die is in the tray its lane-relevant
  business (the roll-band moment where the player reads "which lane
  is this") is already behind it. Curse marks and Preserve's casing
  (section 9) travel with the die into the tray as before; lane
  markers do NOT travel with the die — they stay on the table, per
  the fixed-lane rule above.
- PRE-MATCH LANE PLANNING: dice reorder (drag, same interaction as
  loadout) is reachable INLINE at both the patron and boss peek
  sheets, not only from the standalone loadout screen — same pattern
  as badge-pinning already living at the boss peek. Free, standing,
  no cost, re-decidable before every single seat. This is what lets a
  player look at a known opponent's dice in the peek and deliberately
  arrange which of their own enchanted dice lines up against which of
  the opponent's — the enchant belongs to the die permanently, but the
  LANE it targets is just "wherever this die currently sits," checked
  fresh at match start. Do not confuse this with the existing
  "Vagabond reorder action" elsewhere in this document — that is a
  narrower, one-time, mid-match card-triggered reorder; this is a
  free standing pre-match capability. Keep the two named distinctly
  in implementation.

## 10. INTERACTION MINIMUMS

Tap targets >= 44px (dice sprites may render smaller but get a 48px
invisible hit area). Every tap gives feedback < 100ms (glow, tick, or
press state). No horizontal scrolling anywhere on this screen. All
sheets dismiss by scrim tap or downward swipe. Nothing interactive
above the race bar except pause.

## 11. ACCEPTANCE CHECKLIST

- A first-time player can identify: their total, opponent total,
  target, turns left, current selection value, and turn bank in one
  screenshot (playtest question set).
- Selection tag updates < 50ms after a die tap.
- BANK always displays the exact amount it would bank, including
  rule adjustments (LAST CALL void, RECKONING floor, COUNTERFEIT
  reduction if modelled).
- Zero active rules -> zero note objects; zero gold/heart pixels in
  a plain patron match.
- Rotating a patron's family/persona changes: paws tint (if built),
  card back colours, race fill accent — nothing else moves.
- Props never overlap dice, tags, cards or buttons in any shipped
  template (automated check — an overlap test against the live UI, NOT
  a coordinate range; see the props layer note above for why the
  original x 15-85 version tested the wrong axis). "100 seeded
  scatters" no longer applies: placement is authored, not scattered,
  so the check runs once per template rather than over random fills.
- Bust-to-opponent-turn transition completes < 600ms.
- Boss match shows hearts; patron match never does.
