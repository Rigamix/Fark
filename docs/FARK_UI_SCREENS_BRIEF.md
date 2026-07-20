# FARK — UI & SCREENS BUILD BRIEF

For Claude Code. Companion to FARK_MATCH_BRIEF.md (which owns the
match screen). This brief owns everything else: navigation, every
non-match screen, shop rules, and the layer/asset architecture.
Precedence: FARK_MASTER_BRIEF.md (rules/content) > this brief (UI) >
older screen code. Reference artifacts: fark_greybox.html (navigable
layout truth for all screens), fark_bank_button_mockup.html (button
state system), FARK_UI_ADDENDUM.md (dice renderer).

Baseline frame 390x844, proportional scaling, safe-area padding top
and bottom.

## 1. GLOBAL PRINCIPLES (apply to every screen)

- READING TOP, TAPPING BOTTOM. Headers, summaries, status live in the
  top third; every interactive element a player uses more than rarely
  sits in the lower ~55%. Rare/destructive actions (pause, abandon)
  deliberately go top-right.
- CONTEXTUAL MINIMALISM. Persistent HUD = hearts (top-left) + gold
  (top-right) on tavern screens ONLY. Matches: no gold, no hearts
  (exceptions owned by the match brief). Ledger strip renders only
  when non-empty. Rule notes render only when rules are active. Never
  show placeholder chrome for absent state.
- CTAs STATE THEIR STAKES. "SIT DOWN — 15g", "SIT DOWN — 15g ·
  sealed: win 2 circles / lose 1", "CHALLENGE — a heart at stake",
  "TAKE — final", "FORFEIT — costs a heart". A verb alone is a bug.
- FIXED-FOOTPRINT BUTTONS. All primary buttons use the two-line
  pattern (constant verb + variable caption) from the button mockup.
  Geometry never changes with state; colour/glow/caption do.
- ONE PICK-1-OF-3 PATTERN. Starter draft, victory draft, boss spoils
  share identical layout DNA: summary top, three equal choices in the
  thumb band, tap -> inspect sheet -> TAKE. Choices are equal size,
  no default bias.
- SHEETS, NOT SCREENS, for peeks and inspections: bottom sheets over
  the current screen, scrim tap or swipe-down dismiss, primary action
  at sheet bottom. The sheet's action button IS the confirm step;
  no naked confirm dialogs except the three irreversibles (spoils
  take, enchant purchase, card replacement on full slots).
- STATE-BESPOKE LAYOUTS. Screens re-rank real estate by the player's
  next best action per state (see Room). Dead taps are prevented, not
  disabled: unaffordable items dim but stay inspectable; owned items
  display as owned; locked actions show the unlock condition as
  static text, not a dead button.
- NO BAKED TEXT in any painted asset. All lettering is font-layer.
- Feedback < 100ms on every tap. Tap targets >= 44px (46px+ for
  icons). No horizontal scrolling anywhere.

## 2. NAVIGATION MAP & TAP BUDGETS

title -> room (1 tap, CONTINUE) | starter draft (NEW RUN)
room -> patron match: tile -> peek sheet -> SIT DOWN (2 taps to
  match; 3 to first roll). room -> boss match: door -> boss peek ->
  CHALLENGE (2). room -> shop / loadout / menu (1 each, bottom nav).
match win -> victory+draft -> room. match loss -> defeat -> room.
boss win -> spoils -> room (next night). boss loss -> heart modal ->
  room. hearts out -> barred. night 8 boss win -> run won.
Regressions on these counts fail review.

## 3. SCREENS

### 3.1 TITLE
Logo top (art, non-interactive). Bottom column: CONTINUE (primary,
labelled with run state: "CONTINUE NIGHT 3"), NEW RUN (junior; if a
run exists its caption warns "abandons night 3"). Bottom corners:
the shelf, settings. Nothing else — no news, no popups.

### 3.2 STARTER DRAFT (run start)
Pick-1-of-3 pattern. Three family dice from the master brief's
starter pool on the bar, header top, dice in the thumb band, tap ->
inspect sheet (die faces laid flat + effect) -> TAKE -> room.

### 3.3 THE ROOM (hub) — two layouts by state
State A, EARNING (circles < needed): top strip (hearts/gold),
chalkboard "NIGHT N" (status only, not tappable), ledger strip
(conditional), tavern scene art zone (non-interactive), BOSS DOOR
directly above the tiles carrying the CIRCLE PIPS ON THE DOOR
("BOSS — GROG / ooo + 1 more win to challenge") — progress and its
goal are one object; won circles animate flying INTO the door pips,
sealed losses crack one off. Door always peekable. Patron tiles fill
the bottom band (biggest targets in the game; sealed seat visually
distinct). Bottom nav: menu / loadout / shop.
State B, BOSS READY: door swells into the prime band ("GROG IS
WAITING / READY", stake caption), remaining seats demote to a
compact "gold runs" row above it. With zero seats left the door
fills the whole bottom half. Seats are never hidden while they
exist — greed seats are a real economic choice.
LAST ORDERS (seats exhausted, circles short): heart-crack modal over
the room, roster visibly rerolls behind, CONTINUE.

### 3.4 PATRON PEEK (bottom sheet)
Portrait, name+title, trait seal + word (the 2-second read), dice
chips with lucky marker, visible card backs (family colour borders),
target / buy-in / pot, sealed-seat tell text when applicable.
SIT DOWN with stake label at sheet bottom.

### 3.5 BOSS PEEK (bottom sheet, taller)
Boss art header + one flavour line (no cutscenes anywhere). Heart
warning chip. Tell in full (binds player only). Relic on display.
SLEEVE EQUIP INLINE — the claimed-tells row lives here at the
decision point (also editable in loadout). CHALLENGE with stake
label; when not ready, replaced by static "WIN N MORE SEATS FIRST".

### 3.6 VICTORY + DRAFT
Summary strip top ("WON · +Xg · +1 circle"). Pick-1-of-3 card fan in
the thumb band — the skill moment gets the biggest real estate AND
reach. Duplicates render as in-place upgrades. Slots full -> claim
opens the replace picker (one of the three irreversible confirms).
DECLINE FOR GOLD visible but visually junior. Claim/decline -> room.

### 3.7 DEFEAT
Fast. What was lost (buy-in; sealed: circle cracks off the door
icon), single CONTINUE. Under 2 seconds of forced viewing.

### 3.8 BOSS SPOILS
Pick-1-of-3: relic die / tell scroll / purse, equal size. Tap ->
inspect sheet -> TAKE -> "It's final" confirm. Hearts restore + gold
visible in top strip. This screen gets the art budget.

### 3.9 SHOP
Top strip persists. Innkeep (see §4 canon) behind the counter,
secondary to merchandise. Tabs DICE | ENCHANTS under her (rare
switch, top placement acceptable). FOUR rotating stands, gravity to
the lower half; empty stand = sold-out state with "back another
night" slate. Tap die -> sheet: six faces laid flat (from the dice
face textures — never repainted), effect text, BUY (stays in shop).
Unaffordable: dimmed, inspectable. Owned: owned treatment.
STOCK RULES (game logic, implement with the UI): all stock rotates
per night through the 4 stands; no commons barrel (decided against
for now). Weighting: at least 2 slots hold family dice the player
does NOT own; at least 1 slot is affordable early-game (price <=
current gold after night-1 buy-in); duplicates of owned family dice
are legal stock (they upgrade builds). Nights 6-8: stands grow to 5
(counter plate is painted with room for 5).
ENCHANTS tab: 4 service plaques (Amber Cast, Quicksilver, Tempering,
Loaded). Flow: pick service -> pick YOUR die (dice row appears) ->
irreversible confirm. One enchant per die ever: enchanted dice carry
a permanent seal mark and are excluded from the picker.

### 3.10 LOADOUT
Interactivity increases downward: SHELF (view-only trophies + titles
& feats progress) top; SLEEVE wallet (claimed tells, equip one) mid;
CARDS (exactly 3 slots, empty = faint outline) lower-mid; DICE RAIL
(six dice, hold-and-drag reorder — position IS loadout order, feeds
Vagabond positional scoring) lowest. BACK bottom.

### 3.11 BARRED / RUN WON
Centered summary (what ended the run / trophy ceremony), run stats
line, titles earned. Primary bottom: NEW RUN / TO THE SHELF.

### 3.12 SETTINGS & PAUSE
Settings: audio, haptics, text size, abandon run (stake-labelled,
two-step). Reachable from title and hub menu; back is contextual
(returns to caller). The pause menu (match brief §8) is the ONLY
rules-reference surface: "scoring & your dice" sheet — there is no
innkeep's book screen; do not rebuild one.

## 4. LAYER & ASSET ARCHITECTURE

- Every screen = painted PLATE(s) + sprite layers + DOM UI. UI is
  never painted into plates. Dice are never painted into anything:
  they come from the dice renderer (rest-state via renderDieAtRest —
  keep that abstraction; pending sprite-swap decision) or the face
  textures (shop faces-flat view).
- SHARED KITS (one source each, reused everywhere): HUD kit (hearts,
  gold chip), UI kit from the button/UI sheet (two-line ROLL/BANK
  bodies at ~2.4:1 with caption room, generic buttons, race bar,
  portrait rings, pause icon, parchment note+seal, sheet panel),
  props sheet (mug, candle, coins, cup, jug, cloth — each with baked
  contact shadow), card frame system (6 family colours x 3 metal
  trims + abstract motifs), wax seal set.
- ROOM: tavern plate per night band (rough/mid/fine, 3), boss door
  element with pip sockets, patron tile frames by night band.
- SHOP paintings (8): bar plate (room for 5 stands, no innkeep, no
  dice), innkeep sprite x2 poses (idle polishing, happy hand-over),
  display stand (x1 reused), blank price tag, chalk slate, tab pair
  (2 states), 4 enchant plaques, enchanted-die seal mark.
- LOADOUT: corner plate (wall+table, no objects), shelf sprite,
  sleeve wallet sprite (open), dice rail sprite, trophy sprites (per
  relic/tell as they're earned).
- MATCH: owned by the match brief (table plates, props anchors, boss
  plates with character painted in, opponent paws set).
- INNKEEP CANON: an older gentle lady frog — smooth green skin, kind
  heavy-lidded amber eyes, wide soft smile, age lines; cream linen
  chemise with rolled sleeves, laced brown kirtle bodice, fresh
  apron, simple white coif. She is the shop, the enchant counter,
  and the starter-die offer. One character, everywhere.

## 5. ACCEPTANCE CHECKLIST

- Tap budgets of §2 hold exactly; any regression fails.
- Screenshot test per screen: zero interactive elements above 45% of
  frame height except pause/settings-class rarities and shop tabs.
- Room state flip (earning <-> ready) moves the boss door and
  reflows seats correctly with 0 orphaned tap targets; circle-fly
  and circle-crack animations target the door pips.
- Shop: 100 seeded rotations all satisfy the stock rules (>=2
  unowned family dice, >=1 early-affordable); empty stands render
  the sold-out state; enchanted dice never appear in the enchant
  picker.
- Every CTA in the build carries its stake where one exists (audit
  list: sit down, challenge, take, forfeit, abandon, replace card,
  enchant confirm).
- No screen renders gold or hearts outside the rules in §1 and the
  match brief.
- The strings "innkeep's book" and "YIELD" appear nowhere in UI.
