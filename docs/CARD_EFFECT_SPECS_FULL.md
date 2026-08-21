# Card effect specs — all 24, complete

Same format as Sleight and Stargazer: mechanical sequence, then the
visual treatment at each step. Text quoted at the top of each card is
the verified, exact wording from the master brief — not paraphrased,
so there's a ground truth to check any implementation against.

---

## JADE — rewrite fate, at a price (green)

### Transmute (active)
*"Tap a rolled die and turn it into any face you want."*

1. Player drags Transmute past the threshold during an active roll
   (dice already on the table, not yet all kept).
2. Table dice become tappable — a visible highlight or glow on each
   eligible die so the player knows selection mode is live.
3. Player taps one die.
4. A six-option face picker appears (1 through 6).
5. Player selects a face. The die visibly morphs to it — a green
   shimmer across the die's faces as the pips change, not an instant
   swap, so the transformation itself is watchable.
6. Card spends.

### Fool's Gold (active)
*"Rolled nothing? Reroll everything. But if the second roll fails
too, the bust burns your turn AND the same amount from your banked
points."*

1. Card is only draggable when the current roll scored nothing — this
   needs a distinct "conditionally unavailable" visual state, separate
   from "already spent," so the player can tell why it's greyed out.
2. Once played: every die on the table rerolls together.
3. If the second roll also busts: this needs a genuinely severe,
   unmissable visual, since it's not just losing the turn — banked
   points burn too. The banked-points counter should visibly drain by
   the matching amount on screen, not just update silently to a lower
   number.

### Cultivate (passive)
*"Each time a jade wild fires, that die grows: +50 to its scores for
the rest of the match. Stacks."*

1. No player action — triggers automatically whenever a jade die's 6
   resolves as a wild completing a triple.
2. That specific die gains a small, permanent visual marker (a leaf or
   vine motif fits the name) the moment it happens.
3. Each additional stack adds to the same marker rather than replacing
   it — the die should visibly show *how much* it's grown, not just
   that it has, since stacking is the whole point of the card.

### Bloom (passive, numbers)
*"Straights and triples that use a jade die score +300."*

1. Fully automatic, no activation. The only requirement is that the
   score breakdown clearly labels this bonus separately (e.g. "+300
   bloom") rather than folding it silently into the total — a numbers
   passive the player can't see working is a numbers passive that
   feels like nothing happened.

---

## AMBER — trap everything, even them (warm gold)

### Preserve (active)
*"Trap one scoring die in amber at the end of your turn. It is still
there next turn, already kept and scored."*

Denis's own spec, exact: covers the saved die in a thick amber layer,
moves it down the row while the opponent is rolling, brings it back
up when it's the player's turn again.

1. At the end of the player's turn, with a scoring die selected, drag
   Preserve to trap it.
2. The die is visibly coated in a thick amber layer right where it
   sits.
3. As the opponent's turn begins, the trapped die animates downward,
   out of the active row — it's clearly "stepping aside" rather than
   vanishing.
4. It stays lowered, visibly amber-coated, for the entire opponent
   turn.
5. When the player's turn returns, it animates back up into the row,
   already kept and already scored — the player shouldn't need to
   re-select or re-confirm anything with it.

### Honeytrap (active)
*"Tap a kept pair. Your next roll pulls one die into matching it.
Guaranteed triple."*

1. Player has a kept pair already locked this turn. Drag Honeytrap,
   then tap that pair to target it.
2. A visible honey/amber marker sits on the targeted pair, signaling
   the trap is set for the next roll.
3. On the next roll, one of the newly-rolled dice visibly gets pulled
   or dragged toward the pair's value as it settles — not an instant
   snap to the matching face, but a settle animation that reads as
   being drawn in.

### Tar Pit (active, targets opponent)
*"Trap one of the opponent's dice for their next turn. They roll
five."*

1. On the player's own turn, drag Tar Pit and tap one of the
   opponent's visible dice to target it. Requires the opponent's dice
   to be visible and individually selectable — worth confirming that
   visibility already exists before this card can function at all.
2. A black, tar-like splotch visibly covers the targeted die.
3. On the opponent's next turn, that die visibly sits out — stuck in
   the tar, not participating — while they roll only the remaining
   five.

### Slow Cook (passive, numbers)
*"Every roll past your second adds +150 to your turn total. Bust and
it all spills."*

1. Automatic from the third roll of a turn onward.
2. A visible, accumulating indicator — a simmering pot or ember that
   grows warmer/brighter with each qualifying roll — so the player can
   track how much is riding on the turn before deciding whether to
   keep pushing.

---

## SILVER — defense is an attack (white)

### Ward (active-armed)
*"A visible shield over your dice. Absorbs your next bust, or the
opponent's next trick."*

1. Player arms Ward at any point by dragging it past the threshold.
2. A persistent shield or glow effect surrounds the dice tray,
   visible for as long as it's armed.
3. The moment either trigger condition fires (the player busts, or the
   opponent plays a targeted card against them), the shield visibly
   absorbs it — a clear "blocked" beat, distinct from the shield's
   idle glow, so the save itself is unmistakable rather than inferred
   from the bad thing simply not happening.

### Retort (passive)
*"When you bust or are hit by an opponent card, they lose 400."*

1. Fully automatic on either trigger.
2. A clear callout when it fires, showing the opponent's loss
   explicitly — this is the one passive where the player's own bad
   luck needs to visibly convert into their benefit, so it should
   never read as silent.

### Reprisal (passive)
*"While trailing by 1000 or more, your banks TAKE their points instead
of just gaining. 25% of each bank is stolen from them."*

1. Conditional — only live while the trailing threshold is actually
   met. The card itself should visibly change state (glow or highlight
   when active, dim when not) so the player always knows whether it's
   currently doing anything without checking the score difference by
   hand.
2. When a bank happens while active, the score breakdown should show
   the stolen portion distinctly from the player's own earned points.

### Insurance (passive, numbers)
*"When you bust, keep a quarter of the points you would have lost."*

1. Fully automatic on bust.
2. The bust display should show the full loss with the insured
   portion visibly subtracted or struck through, rather than just
   presenting the already-reduced number — the player should see what
   they kept, not just what's left.

---

## OBSIDIAN — burn it all (black/ember)

### Powder Keg (active)
*"Blow up your whole roll: every die rerolls, kept ones included."*

1. Drag past the threshold at any point mid-turn.
2. Every die — including anything already kept earlier this turn —
   visibly detonates together. A real burst/explosion beat fits the
   family's theme directly and also gives the player an unmistakable
   signal that previously-locked dice are back in play, which is the
   one thing about this card most likely to surprise someone if it's
   silent.
3. Everything resettles as a fresh roll.

### Double or Nothing (active)
*"After banking, flip for it: double the bank or lose half."*

> **RULED (P816, 2026-08-20): the PRE-bank arm is the design.** The
> card is armed before the bank and resolves against it; the in-game
> text now reads "Arm it, then bank." Item 1 below is the superseded
> original spec, kept for the record.

1. Only available in the window immediately after a bank — not
   mid-roll.
2. A clear flip or gamble animation (a coin or die flip fits the name)
   plays out the decision rather than resolving instantly.
3. The just-banked total visibly updates to match the outcome on
   screen — doubled or halved, shown as a clear transition from the
   original banked number, not a silent overwrite.

### Sacrifice (active)
*"Shatter one of your own dice, gone for the match, for +800 right
now."*

1. Drag past the threshold, then tap one of the player's own dice to
   target it.
2. That die visibly shatters or cracks apart — permanent for the rest
   of the match, so the visual needs to read as final, not a temporary
   state.
3. +800 adds immediately to the current turn total, with a clear
   causal link on screen between the shatter and the point gain.
   *(RULED P816: no instant pay — the value rides `_turnBonusPot`,
   collected at the bank, burned entirely on a bust. The causal-link
   visual requirement stands.)*

### Short Fuse (passive)
*"From your third roll each turn, everything scores double. But bust
after that and the fire spreads to your banked points. Tray smolders
from roll three: the warning state must be unmissable."*

The card's own text already specifies the visual requirement — worth
building to that literally rather than inventing something softer.

1. Automatic from the third roll onward.
2. The dice tray visibly smolders — ember glow, rising heat — starting
   exactly at roll three, escalating for as long as the state holds.
3. This isn't optional polish: the text calls it out directly as
   needing to be unmissable, since the downside (banked points
   burning, not just the turn) is severe enough that an unaware player
   pushing past it is a real design failure, not bad luck.

---

## STARSTONE — omens: bet on what happens next (night blue)

### Encore (active)
*"Do not like a roll? Roll it again."*

Distinct from Powder Keg despite the surface similarity — this only
touches the current, uncommitted roll. Anything already kept this
turn stays kept.

1. Drag past the threshold after an unwanted roll lands.
2. Only the dice from the current roll reset — a softer, blue-tinted
   shimmer rather than an explosion, visually distinguishing it from
   Powder Keg's "everything, violently" treatment.
3. Previously-kept dice from earlier this turn are untouched and
   should visibly stay put through the animation, not flicker or
   reset alongside the rest.

### Stargazer (active)
*Full spec already written — see the earlier document. Peeks and
locks the actual next-roll values as ghost dice; the preview and the
real roll must be the same computed values, read twice, not two
independent random draws.*

### Ill Omen (active, targets opponent)
*"At your turn's end, declare they will bust this turn. Right: take
800 from them. Wrong: they gain 400."*

1. Only available at the specific end-of-turn window, not mid-roll.
2. Playing it produces a visible "declared" marker, telegraphed to
   both sides — matching the established rule that every targeted
   active gives the opponent one visible warning before it resolves.
3. When the opponent's following turn resolves, the prediction
   visibly pays off in whichever direction: correct shows points
   transferring from the opponent, wrong shows the opponent visibly
   gaining instead. Both outcomes need equally clear presentation —
   this is a real two-way bet, not a one-sided card with a rare
   downside.

### Falling Star (passive)
*"Bank 1500 or more in a single turn and take another full turn
immediately, opponent skipped."*

Already ruled tonight as needing a loud, unmissable announcement given
the difficulty impact of an extra turn.

1. Automatic trigger the moment a qualifying bank lands.
2. A clear, celebratory beat — a star or streak effect matches the
   name directly — followed by an explicit "go again" state so there's
   no ambiguity that the turn is continuing rather than a new one
   starting.

---

## VAGABOND — cheat politely (red)

### Sleight (active, targets opponent)
*Full spec already written — see the earlier document. Arms on the
player's turn, fires on the opponent's next roll, needs a visible arm
marker and a visible re-roll beat when it fires.*

### Pickpocket (passive)
*"Every time you bank, lift 100 of the opponent's unbanked points."*

1. Fully automatic on every bank.
2. A quick, small coin-lift animation — a few coins visibly moving
   from the opponent's current unbanked total to the player's
   just-banked amount — makes the theft legible in the moment rather
   than just a number quietly changing on the opponent's side.

### Tamper (active, pre-match)
*"Break one of the opponent's cards for the night."*

1. Fires before the match starts, at the boss peek or pre-match
   screen — not during play.
2. Player selects one visible opponent card to target.
3. That card shows a persistent broken/disabled state for the rest of
   the night — a crack overlay and greyed treatment, distinct enough
   that glancing at the opponent's cards mid-match still shows which
   one is inert.

### Vanguard (passive)
*"A scorer in the first spot scores +200... marked spots glow before
the roll: the player aims."*

The card's own text already specifies the core visual — worth taking
it literally.

1. At the appropriate tier, specific lane positions are eligible for
   the bonus.
2. Those positions visibly glow *before* the roll happens, not after
   a die lands there — the whole point is letting the player aim for
   it, which requires knowing where the bonus lives in advance.
3. When a scoring die actually lands in a marked spot, the bonus
   should be clearly attributed in the score breakdown, not folded
   silently into the total.

### For Keeps (consumable, no tiers)
*"Play as you sit down: this match is for dice. Win, take one of
theirs. Lose, they take one of yours."*

1. Played before the match starts, same timing window as Tamper.
2. A persistent, unmissable stakes indicator should stay visible for
   the entire match — given the permanence of what's at risk (a real
   die, gone for good on a loss), this needs a constant reminder, not
   a one-time notice at the start that's easy to forget by turn six.
3. On match end, resolution follows the same win-screen swap-picker
   already established for how a won die gets chosen into the
   winner's six.

---

## Coverage note

24 of 24 family cards specified. Not covered here: the ~8-9 enchants
(Amber Cast, Quicksilver, Tempering, Loaded, and others referenced
elsewhere but not fully quoted in what's been read tonight), the
consumables (Double Stakes, The Tab, Hair of the Dog, Cursed Table,
High Table), and the eight boss badges (Last Call, Steeped, Pickpocket
the badge, In Arrears, Drill Order, Confession, Counterfeit Coin, The
Reckoning) — those are mechanically simpler (mostly automatic match
modifiers, not player-activated cards) but haven't been written up to
this same step-by-step depth. Say if those are wanted too.
