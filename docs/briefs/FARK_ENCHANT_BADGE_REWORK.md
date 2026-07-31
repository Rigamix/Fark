# FARK — ENCHANT / SILVER / BADGE REWORK BRIEF

For Claude Code. This SUPERSEDES the master brief's sections on enchants,
the Silver family, and four of the eight boss badges. Everything else in
the master brief (families other than Silver, cards other than Silver's,
the badge mechanic itself, relics, the run loop) is UNCHANGED — this is a
targeted rework of three interlocking systems that were found, through
design iteration and simulation, to be overlapping and under-specified.
Sits alongside FARK_MASTER_BRIEF.md, FARK_MATCH_BRIEF.md,
FARK_UI_SCREENS_BRIEF.md. Where this document gives a number, it is a
PROPOSAL validated only by the clean-room sim described inline — same
discipline as every other numeric claim in this project: trust the
harness, not the prose, before it ships.

## 0. THE LAW THIS ENTIRE REWORK ENFORCES

Every collision this rework fixes had the same shape: two systems
competing to do the same job. The rule that prevents it recurring:

**A FAMILY effect touches ALL SIX faces of a die, statistically, always.
An ENCHANT effect touches exactly ONE face, and only fires when that
exact face lands and is kept.**

If a proposed enchant would be true regardless of which face showed, it
is not an enchant — it is a family trait wearing a costume, and it must
be rejected or redesigned. This test is retroactive: it is WHY Amber
Cast, Tempering, and Loaded are cut below, and it is the acceptance
gate for anything anyone proposes to add to this system in future.

## 1. SILVER — FULL REWORK

**DELETE:** Silver's old identity (guaranteed or limited bust-forgiveness
on the die itself). Confirmed by simulation to be a structural break, not
a balance issue: any unconditionally-available safe keep in a 6-die hand
makes a turn's last roll effectively bust-proof, which defeats the
push-your-luck core and makes every bust-reactive card (Retort, Reprisal)
meaningless. This is not tunable by changing numbers — the OPTION being
free is the problem, not its size.

**NEW Silver identity: reliability, not safety.** Silver dice roll on a
weighted face table instead of a fair 1-6: values `[1,5,1,5,2,3,4,6]`
(1 and 5 each at 2x the weight of 2/3/4/6). A silver-heavy hand busts
LESS OFTEN on average — it never removes the zero, every roll stays a
real roll.
- Sim result: an all-bone hand busts ~49-50% of turns. An all-silver hand
  (this table) busts ~26%. This is the locked value — an earlier, heavier
  skew (3x weight) tested at 14%, judged too safe, rejected.
- This is a FAMILY trait (touches the whole die's distribution), so it is
  exempt from the enchant face-restriction in section 2 — it's not an
  icon face, it's the die's base geometry.

**Silver's card suite:** Ward-the-card and Insurance-the-card are
RETIRED — their job (bust mitigation) moved to the Ward enchant
(section 2). Silver keeps Retort and Reprisal unchanged. Two new cards
fill the retired slots:
- **Steady Hand** — reroll a single die of your choice, keep the new
  result even if it's worse. Precision over luck; does not touch bust
  odds at all.
- **Fair Trade** — before rolling, swap one of your six dice with
  another from your own pool. TIER I lasts for that one roll only;
  TIER II extends the loan for the rest of the turn — the two must
  behave differently, tier I is the deliberately weaker version.
  Build-flexibility, no overlap with any other system.
  **REVISED — if the borrowed die is destroyed mid-loan** (Obsidian's
  natural shatter, Break, or any future death effect): **the player
  loses the die they lent, permanently, exactly as if it had died in
  its own home lane.** No exception for cause. This reverses an
  earlier ruling (void the loan, nothing lost) that turned out to be
  a live exploit: it let a player borrow their own Obsidian die,
  Break it for the guaranteed +1000, and have Fair Trade erase the
  loss entirely — bypassing the whole point of section 4's timing
  finding with zero cost. The corrected reasoning: natural shatter
  and Break are EQUALLY permanent (confirmed against the Break sim
  work — shatter is a one-time, whole-match event, not "gone for a
  turn, comes back"), so there was never a real "soft cause" to
  protect against. A die's death belongs to the die, not to whichever
  lane it's temporarily visiting. This does not make Fair Trade a
  stake — the card's actual value (repositioning a die into a
  different lane) is untouched; what's removed is an accidental
  bonus immunity the card was never designed to grant. If the loan's
  duration simply expires without the die dying, nothing changes:
  the player's own die returns to its home lane as normal.
  **CLARIFIED — a brand belongs to the die, never the seat/lane.** A
  code audit found the shipped game leaves a die's enchant behind when
  Fair Trade swaps it, so a borrowed die wears whatever brand its
  temporary lane happens to carry instead of its own. This contradicts
  an already-locked rule (match brief: enchants live on the die, a
  lane is just wherever that die currently sits, which is what makes
  pre-match reordering meaningful at all) — not a fresh question, the
  code needs to catch up to the existing spec. The brand travels with
  the physical die wherever it goes, always.
  **CLARIFIED — mixed selections never get poisoned by an icon.** The
  universal rule (an icon face banks zero and fires its effect) means
  zero is the CORRECT value for that component, not an error state. A
  keep containing real scorers plus one icon-face die should commit
  and score the non-icon part normally while the icon fires — a
  branded die must never invalidate an otherwise-legal selection.

**RESOLVED** (was an open item; a code audit found it still contradicting
section 1's "doesn't exist anywhere" claim, since it was never actually
closed out): Brutus's relic ("2 bust saves," from the old spoils system)
becomes a die that PERMANENTLY carries the Ward enchant, pre-applied —
no branding needed, no separate mechanic invented. It counts against
the one-Ward-per-loadout hard cap exactly like a player-branded Ward
die; the cap exists specifically to stop stacked safety nets, and a
relic that bypassed it through a side door would quietly undo the
reason the cap exists.
**FACE: 5, not 1.** The "brand the most expensive face" logic that
governs PLAYER-chosen brands (discourage picking the cheap option)
doesn't apply to a single, fixed, developer-authored relic property —
nobody is choosing here. A 100-point toll to arm a half-save risks the
relic's signature ability going unused in practice; face 5's gentler
cost is what makes it something a player actually reaches for.
**INHERITS SILVER'S WEIGHTED TABLE** (`[1,5,1,5,2,3,4,6]`) — it is
tagged Silver family and should behave like Silver family; rolling a
fair 1-6 instead was an oversight, not a design choice, and this fix
is unconditional regardless of the face-5 call above.
Fits Brutus's character as a bonus: a soldier who is simply always
prepared needs no flashy new rule. Old text superseded by the
relic-vs-badge architecture question (open item, section 5) is
settled.

## 2. ENCHANTS — FULL REWORK

**CUT, with reasons Code should retain in comments/commit messages:**
- **Amber Cast** (copy one face onto another) — duplicated Jade's entire
  reason for existing (face manipulation is Jade's family identity).
- **Tempering** (coin-flip: +100 all scores / lose highest face) — a
  flat scoring-math adjustment, not a distinct verb. Same species of
  problem as Loaded below.
- **Loaded** (one face rolls ~2x as often) — mechanically identical to
  just owning two copies of that face. No player-visible difference
  from a family trait tweak. Failed the section-0 test on inspection.

**KEPT UNCHANGED:**
- **Quicksilver** (~250g) — free solo reroll on this die, once per turn.
  Architecturally DIFFERENT from the seven below: it is a whole-die
  passive ability, not tied to any specific face. NOT subject to the
  face-restriction rule in this section — there is no face to restrict.

**NEW roster — seven icon-face enchants, ALL governed by one universal
rule, stated once so the whole system is learnable in a single sentence:**

> **An icon face, when kept, always banks ZERO points and fires its
> effect instead. Never both.**

And one universal restriction, closing a real exploit (see sim below):

> **An icon can only be branded onto a die's natural 1 or 5 face.**
> Never onto 2/3/4/6, never onto a Jade wild-6, never onto a face a
> relic has already altered.

**Why the restriction exists (sim, not opinion):** without it, branding
a 2/3/4/6 face is nearly free, because those faces rarely contribute to
scoring alone (~8% of rolls) while 1 and 5 contribute constantly (~66%
of rolls). Measured average EV forfeited per turn by branding each face
on an otherwise-fair hand: face 2 ≈ 32, face 3 ≈ 39, face 4 ≈ 41, face 6
≈ 54, **face 5 ≈ 73, face 1 ≈ 125**. Restricting to 1/5 raises the floor
~2.3x. NOTE: a residual gap remains even inside the restriction — 5 is
still cheaper to give up than 1 (73 vs 125) — so "always brand the 5, not
the 1" is a smaller, secondary cheese that per-face pricing should close
(price branding a 1-face higher than branding a 5-face). Not fully
resolved; see open items.

**The seven, full specs:**

- **Tithe** (~150g) — coin icon. Kept: banks 0, pays flat +15g. No
  tension by design — the quiet, cheap one.
- **Ward** (~350g) — shield icon. Kept: banks 0, ARMS a bust-insurance
  for the rest of this turn only. If the turn busts afterward, that
  turn's bank is HALVED instead of zeroed (never a full save — that was
  the old, broken Silver behaviour). **ONLY THE FIRST WARD KEPT IN A
  TURN COUNTS** — a second Ward-icon keep that same turn does nothing
  extra. **HARD CAP: a loadout may contain at most ONE Ward-branded die
  at a time.** This second constraint is NOT optional flavor — sim
  found that even with the single-save cap, 2 Ward dice measurably
  outperform 1 (28% vs 17% save rate under a greedy policy) because a
  second Ward die is a second CHANCE TO ARM, which the save-cap alone
  doesn't restrict. The loadout-level cap is what actually closes it.
- **Snare** (~400g) — banks 0. Marks the PLAYER's own die's LANE — a
  fixed table position for the whole match, per the match brief's
  six-fixed-lanes system, not just an abstract index. Firing it paints
  a visible trap marker onto that lane's spot on the table, which the
  player watches persist until it resolves. Resolves against the
  OPPONENT's VERY NEXT TURN ONLY:
  if their die occupying that same lane scores during that one turn,
  it's halved once; the mark then clears regardless of whether it fired.
  **This "next turn only" window is a correction, not the original
  design** — an earlier version left the mark armed "until it fires or
  the match ends," which sim showed fires 97.7% of the time within 6
  turns, i.e. not a real bet. The shortened window is what makes it an
  actual wager.
- **Break** (~300g) — skull icon. Kept: banks 0. Destroys ONE OTHER
  LIVE die of the player's choice for the REST OF THIS MATCH ONLY —
  the die returns, fully restored, at the start of the player's next
  match. Same bound as Trade above, stated explicitly here because the
  earlier "permanently... for the rest of the match" phrasing reads
  ambiguously between match-scoped and run-scoped, and the section 4
  timing finding was always about turns remaining WITHIN a match, not
  matches remaining in the run — that finding holds unchanged under
  this clarification, it was never testing the harsher reading.
  (A PRESERVED die, per the match brief, is explicitly INERT and is
  therefore never a legal Break target — stated outright here so it
  never has to be inferred from the two words being opposites.)
  (loadout drops to 5 dice for all remaining turns). WIDENED (supersedes
  the earlier "Obsidian-only" decision): every family now has its own
  death-trigger, so Break has a real partner in every build, not one
  solved answer:

  | Family    | Death-trigger, fires guaranteed when Break-destroyed |
  |-----------|--------------------------------------------------------|
  | Obsidian  | +1000 flat to the current turn's bank (this is the ONLY sim-validated row — section 4) |
  | Amber     | The current turn becomes bust-immune for its remainder — you may keep pushing without risk until you choose to bank |
  | Starstone | Grants one immediate extra turn, right after this one ends |
  | Silver    | Immediately banks the current turn's total as-is, ending the turn, guaranteed (a safe cash-out) |
  | Jade      | Immediately grants one free full reroll of every currently-live die, no cost |
  | Vagabond  | Steals an amount equal to the OPPONENT's current unbanked turn total (0 if they haven't banked anything yet this turn) |
  | Bone / mundane (iron, flint, lead, plain bone) | No trigger. Banks 0, die gone, nothing else — confirmed worst Break target, matching mundane dice being baseline-weak everywhere else in this game. |

  Each row is a distinct VERB (flat value / temporary invincibility /
  extra turn / safe lock-in / free reroll / opponent theft), chosen to
  match that family's existing identity rather than being a reskinned
  copy of Obsidian's. **Only the Obsidian row has real sim numbers
  behind it** (section 4) — the other five follow the same design
  logic but are unvalidated proposals and need their own harness pass
  before anyone trusts their power level. See section 4 for the timing
  nuance that applies to ALL SEVEN rows equally, not just Obsidian's,
  and must not be smoothed away in implementation.
- **Trade** (~350g) — crossed-arrows icon. Kept: banks 0, POST-ROLL.
  PERMANENTLY swaps the MATERIAL occupying the player's lane with the
  opponent's material in that same fixed lane, for the rest of the
  match (the lane position itself never moves — only what's in it
  changes). Not a hidden-information gamble — landing order is
  loadout order and the peek already shows the opponent's dice before
  the match starts, so this is a commitment risk (you know exactly
  what you're trading for) not a blind one. Visible on the table: the
  swap animates at both lane positions when it fires.
  **CLARIFIED, then corrected — MATCH-SCOPED, reverts fully after.**
  "For the rest of the match" is a bound, not a permanence claim — an
  earlier pass here over-read it as crossing between matches and
  invented an "enchants never cross" carve-out to guard against that.
  Wrong scope: nothing here ever persists past the match it's used
  in, so there is nothing to guard. The WHOLE die swaps — material
  AND whatever enchant it carries — for the duration of THIS match
  only; the instant the match ends (win or lose), both sides' true
  owned loadouts are fully restored, no exceptions, no residue. This
  is simpler than the earlier ruling, needs no special case, and is
  the more exciting version besides — you're borrowing the opponent's
  whole capability for one fight, not just their base material.
- **Snuff** (~300g) — banks 0, POST-ROLL. A candle-snuffer marker
  appears at the OPPONENT's same fixed lane; their die there is
  removed from their pool for their NEXT TURN ONLY, then returns
  automatically (marker clears with it). Sim: pulling one die from a
  6-die hand drops that turn's average value ~36% — a strong
  single-use effect; the real NPC-facing power level needs
  re-confirming once opponent AI can choose when to play around it
  (this sim assumed a static hand, not an adapting one).
- **Fog** (~250g) — cloud icon. Kept: banks 0, POST-ROLL. A visible
  fog-cloud marker settles onto the OPPONENT's same fixed lane and
  stays there through the turn boundary. On their next roll, their die
  in that lane has its value excluded from whatever the NPC's EXISTING
  bank/keep heuristic can see, forcing that specific die into an
  effectively random keep/reroll outcome from the AI's own math.
  Deliberately does NOT require the opponent to be "smart enough to be
  fooled" (an earlier concept, Whisper, was cut for exactly that flaw)
  — Fog corrupts the input to logic that already exists, rather than
  assuming threat-assessment sophistication that doesn't. The marker
  clears when their lane-roll resolves.

All seven gold prices above are PLACEHOLDERS ordered by estimated
power/complexity, not yet run through a pricing-specific sim pass — flag
this to whoever tunes the economy next.

**Shop flow — SUPERSEDES the earlier "add a face-picker" plan below.**
A code audit found the shipped game never built the picker at all — it
ships a random draw across ALL SIX faces, which reopens the exact
"free bust insurance" exploit the 1/5 restriction exists to close (a
branded 2/3/4/6 face gives a would-be-bust roll a guaranteed non-bust
alternative it otherwise wouldn't have; measured at a 25% flat cut in
single-roll bust rate, zero effect on 1/5 — the same unconditional
safe-keep shape section 1 deleted Silver's original identity to
remove, walking back in through a different door). RULING, final:
- Restrict the random draw to [1, 5] only. No picker screen, ever —
  every die always has both a 1 and a 5, so a picker would only ever
  offer the same two buttons, forever; not worth the extra tap or the
  art for a choice that narrow (73 vs 125 EV forfeited, a minor tuning
  knob, not a strategic fork).
  Shop flow stays TWO taps: pick service → pick your die → confirm.
  The face is assigned automatically, randomly, from {1, 5}.
- Per-face pricing (was open item 2) is now MOOT — it only mattered if
  players were choosing between faces. Consider that item closed.
- Existing brands sitting on an illegal face (2/3/4/6) at the moment
  this ships: REFUND AND CLEAR, not silently moved to the die's 1.
  Matches the game's own existing precedent for retired mechanics;
  silently rewriting a purchase to a face the player didn't choose is
  worse than an honest refund.

## 3. BADGES — FOUR OF EIGHT BOSSES REMAPPED

Four new badge-rule concepts were designed and sim-tested specifically
to synergize with the new enchant system (something the original eight
tells, designed before enchants existed, could not do). They REPLACE
four existing tells — chosen deliberately to avoid touching the two
tells that already tested well (Drill Order and Pickpocket both
confirmed +4-5 win-rate points in the run-level sim earlier in this
project) and instead replace the weakest-tested or entirely-untested
four.

**IMPORTANT FOR ART/CODE:** per the one-object-one-look law, a badge's
PHYSICAL IDENTITY belongs to its boss, not to the rule it currently
carries. The Boot, The Serpent, The Antler Crown, and The Tipped Scales
need NO new art — only the game-logic rule ID bound to each badge
changes. Do not commission new badge paintings for this rework.

- **Grog: Last Call → Zero Hour.** (Badge stays The Boot.) Last Call
  tested as the weakest-performing tell in the roster (neutral-negative
  in prior sim). Zero Hour: while worn, keeping any icon-enchant face
  immediately ends the acting side's turn (no further rolls after).
  Sim: ~14% average turn-bank tax on a 2-enchant hand; the early-end
  fires on ~32% of icon keeps. Real bite, not a shutdown — same theme
  as Last Call (urgency, time running out) but now interacts with a
  system that exists.
- **Whisper: Counterfeit → Kindred.** (Badge stays The Serpent.)
  Counterfeit was never validated in prior sim passes. **RESCOPED —
  a code audit found the engine has no opponent-side enchants at all,
  making the original "either side" wording structurally unreachable**
  (the opponent-side half of the check can never be true). Kindred
  now reads: while worn, if the PLAYER has 2+ enchanted dice in their
  loadout, icon effects trigger at DOUBLE STRENGTH for the match. This
  loses the mutual "read whether you're more enchanted than them"
  tension the original wording implied, but survives intact as a
  build-commitment reward (Whisper rewards a player who's leaned into
  enchants) — still a good badge, just honestly scoped to what the
  engine can evaluate. Sim (Tithe only, the clean case): gold income
  5.9 → 11.9/turn, an exact 2x, confirmed no leakage. **OPEN ITEM:**
  "double strength" is only cleanly defined for additive-numeric
  effects (Tithe's gold). Ward's halved-consolation, and Snare/Break/
  Trade/Snuff/Fog's structural effects, do NOT have an obvious "2x" —
  doubling a die-destruction or a one-time swap doesn't mean anything
  as written. THIS NEEDS A DESIGN DECISION before Code implements
  Kindred for anything but Tithe. Do not guess a default per-enchant;
  ask.
- **Aldric: Confession → Still Waters.** (Badge stays The Antler Crown.)
  Confession was never validated. Still Waters: while worn, an
  enchanted die's underlying FAMILY TRAIT is suppressed for the match
  (it behaves as a plain die except for its enchant, which still fires
  normally). Sim (Obsidian case only): strips ~644 points, ~14.5% of
  that build's match value — a real, appropriately-scoped bite, same
  severity tier as Zero Hour. NOTE: only the Obsidian case was
  sim-tested; suppressing Jade wilds, Amber's triple bonus, Starstone's
  bank bonus, or Silver's odds-skew under this badge is inferred, not
  validated — re-test each before trusting the number in a live build.
  **CLARIFIED — Break vs Still Waters:** a code audit found Break's
  guaranteed Obsidian trigger (section 2/4) was surviving Still Waters
  because it dispatches off material family, not the die's specific
  effect. RULING: it should NOT survive. Section 0's law is explicit —
  a family death-trigger fires regardless of which face shows, which
  is the definition of a family trait; Break doesn't invent a new
  mechanism, its own spec says it forces the SAME shatter, just
  guaranteed. Suppressing the passive version but exempting the
  guaranteed one is an inconsistent carve-out the law doesn't support.
  This makes Still Waters a hard counter to the best-validated Break
  partner — intentional, not a flaw; Snare/Trade/Fog already exist to
  reward reading the table and countering a build, this is the same
  shape. Applies identically to Grog's Tooth (the Obsidian relic
  shares this mechanic) — relics are NOT badge-proof, no principled
  reason to exempt them. UNVALIDATED, needs its own sim pass before
  trusting it live — and Grog's Tooth's magnitude (10%/+1500) is a
  meaningfully different number to strip than plain Obsidian's
  (6%/+1000), so it needs its OWN measurement, not an extrapolation
  from the Obsidian figure above.
- **Corvus: In Arrears → First Strike.** (Badge stays The Tipped
  Scales.) In Arrears was untested. **REDESIGNED, not just rescoped —
  a code audit found no opponent-side enchants exist, and unlike
  Kindred this one can't survive a simple rescope:** the original
  "whichever side triggers first" was a RACE, and with the opponent
  structurally unable to ever trigger, the player always wins it
  trivially — the race collapses into a guaranteed freebie, which was
  never the design. New wording: while worn, the FIRST TIME the player
  fires a lane-targeting icon (Snare, Trade, Snuff, or Fog) this match,
  reveal the opponent's full six-lane material layout. **Flag this
  plainly:** this is weaker and less interesting than the original
  race concept — worth a real decision on whether it's still worth
  keeping in this reduced form or should retire back toward something
  else, rather than quietly shipping a downgrade nobody signed off on.
  **NOT numerically sim-tested** either version — pure information
  effect, no scoring-math signature to measure; validated qualitatively
  only. **REAL COST, still stands:** Corvus's In Arrears was the ONLY
  pure-economy tell (gold-drain) in the entire eight-badge roster.
  Removing it means no badge taxes gold anymore. If missed in
  playtest, needs a new home — not solved by this rework.

**UNCHANGED:** Mabel (Steeped), Finnick (Pickpocket), Brutus (Drill
Order), Ambrose (Reckoning) — the last one stays specifically because
it's structurally load-bearing as the final-boss escalation, not because
it tested well (it remains untestable pre-night-8 in any sim, same as
before this rework).

## 4. THE BREAK TIMING FINDING — READ THIS BEFORE IMPLEMENTING BREAK
(Obsidian is the only row with numbers; the shape of the finding — not
the specific figures — applies to every family in the table above.)

This is the centerpiece result of the whole rework and the clearest
proof the family/enchant split can produce real tactical depth, not
just bigger numbers. Two sim results that must BOTH ship, not just one:

- **Across a whole match**, using Break on an Obsidian die immediately
  whenever available is a NET LOSS: ~3,471 vs ~4,425 average total match
  bank. Permanently losing a sixth die costs more, across many future
  turns, than the guaranteed 1,000 is worth.
- **On a single turn with no future turn to protect** (the actual last
  turn of a match, or any turn where subsequent turns won't happen),
  the trade flips hard positive: 1,140 vs 409 average bank for that
  turn, AND bust rate drops from 46% to 8% (removing the die also
  removes it from that turn's bust-risk pool).

The correct play is a TIMING READ — "do I have a future turn to lose" —
not a build-time checkbox. **Do not balance this by averaging the two
numbers, and do not "fix" it by making Break net-positive across a whole
match** — that would destroy the exact skill expression that makes it
interesting. If playtest data suggests players never discover the
late-turn timing on their own, the fix is a UI/telegraph hint (e.g. the
match brief's turn counter already pulses amber at 2 turns remaining —
that's a natural moment to make Break's icon glow harder), not a
numbers change.

## 4b. MATCH-SCOPING IMPLEMENTATION RULINGS (Round 2 — closes gaps
Code found while actually building the correction in section 4/above)

**THE LANE PERSISTS, ONLY THE DIE IS DESTROYED — this is the one that
actually matters.** When Break destroys a die that is currently
occupying a lane via a Fair Trade loan, the player's OWN die (benched
by the loan, never itself destroyed) returns to that lane IMMEDIATELY.
The player stays at 6 dice for the rest of the match. The cost of
breaking a borrowed die is exactly the cost of breaking any die — one
die gone for the match — never inflated to a whole seat because of
which physical die happened to be sitting there. Follows directly from
the lane/die distinction already established ("the lane position
itself never moves, only what's in it changes") — Code's conservative
seat-loss implementation was a reasonable read of an under-specified
ruling, not a wrong one; this closes the gap explicitly so it isn't
inferred differently a third time.

**LEGACY SAVE MIGRATION, both Break and Trade.** No record exists of
what was destroyed/swapped under the old (run-scoped) behavior, so
exact restoration is impossible for either — refund is the only honest
repair, matching the existing `_enchV=2` precedent for retired
enchants:
- Break: refund a flat ~450g (no exact price recoverable; this
  approximates the average family-die cost).
- Trade: refund exactly 350g — the enchant's own known price, more
  precise than Break's case since the data allows it.

**MISSING-DIE VISIBILITY.** A die that's gone until the player's next
match must be shown as such in the loadout/peek UI — never silently
absent. Same "state must never lie" principle that already required
the visible swap-back fix below; an invisible gap is the same failure
in the opposite direction.

**FAIR TRADE'S OWN LOAN CLOCK IS UNCHANGED BY MATCH-SCOPING.** The
match-scoping correction resolved ambiguity specifically in Break's
and Trade's "for the rest of the match" phrasing. Fair Trade the CARD
was never worded that way — "this roll" (tier I) and "the turn"
(tier II/III) stay exactly as designed, genuinely different durations,
no text changes. Only the DEATH clock (what happens if the borrowed
die is destroyed mid-loan) inherits match-scoped treatment, per the
ruling above and the earlier reversed Fair Trade ruling (section 2).

**TRADE'S SWAP STAYS ONE-WAY.** No opponent-side enchant array exists
in the engine — the exact same structural gap already found and
accepted for Kindred and First Strike. Same resolution for
consistency: the player's material + enchant crosses to the opponent's
lane; only material returns, since there was never an enchant on the
other side to cross back. Deferred, not a bug — same status already
given to the NPC-Preserve visibility gap (both wait on the same future
"real opponent-side enchant support" work, not solved reactively here).

**TRADE IS CORRECTLY SELF-CONSUMING — confirmed wanted, not a nerf to
patch around.** Falls directly out of "the whole die swaps": once the
enchant physically leaves with the die, nothing remains in that lane
capable of firing Trade again this match. One use per match, by
construction. Thematically right (commitment, no take-backs). Price
(~350g) should be revisited whenever the full enchant pricing pass
happens, factoring this in — not resolved now.

**VISIBLE SWAP-BACK EXTENDS TO TRADE.** Same engineering the ruling
already bought for Fair Trade (a die that visually reads stale after
its material/brand has actually changed is the state-lies-about-truth
problem) — applies identically to Trade's swapped dice. Not a new
decision, precedent applied to its second occurrence.

**PRESERVE GUARD FIELD NAME:** `d._preserved`, a boolean directly on
the die object — consistent with how curse marks and other per-die
state already travel with the persistent die object elsewhere in this
system.

**NOT ADDRESSED HERE, confirmed as a separate outstanding task:**
Break's own "returns fully restored at the start of the player's next
match" mechanism still needs building — `_removeDieAt(lane,
{permanent:true})` still splices permanently as of this patch. Real,
separate, still needed; not assumed covered by the Trade-scoping work.

## 5. OPEN ITEMS — NOT RESOLVED, DO NOT GUESS DEFAULTS

1. Kindred's "double strength" definition for Ward/Snare/Break/Trade/
   Snuff/Fog (section 3) — needs a design decision, not an assumption.
2. Per-face pricing for the residual 1-vs-5 enchant cheese (section 2)
   — exact multiplier untested.
3. All seven new enchant gold prices are placeholders, need a dedicated
   pricing pass.
4. RESOLVED — Break is widened to all six families (section 2 table).
   Remaining sub-item: only Obsidian's row is sim-validated; the other
   five (Amber, Starstone, Silver, Jade, Vagabond) need their own
   harness pass before their power level is trusted in a live build.
5. Corvus's lost economy-tax flavor (In Arrears) — needs a new home if
   missed in playtest.
6. RESOLVED — see the Silver section above (Brutus's relic now carries
   a permanent Ward enchant, counted against the loadout cap). The
   broader relic-vs-badge architecture question (should relics be
   physical dice competing for loadout slots, or fold into some other
   delivery) remains open independent of this specific fix.
8. NO OPPONENT-SIDE ENCHANTS EXIST IN THE ENGINE. This was found to be
   the root cause of THREE structurally-unreachable clauses in this
   document, all now resolved: Kindred (rescoped to player-only, above),
   First Strike (redesigned, above), and the "occasional enchanted
   patron/boss die" flavor idea floated in earlier design discussion —
   that one is DEFERRED outright, not fixed, since it was always a
   stretch-goal riding on infrastructure that doesn't exist and nothing
   else in this document depends on it. Building real opponent-side
   enchant support (NPCs owning and triggering enchanted dice, an AI
   keep-policy for icon faces) would let Kindred and First Strike
   recover their original, richer designs — a real future option, not
   attempted here.
7. Snuff and Fog's real power level against an ADAPTING opponent (this
   document's sim used static hands; re-run once opponent AI logic for
   these two exists).

## 6. MIGRATION CHECKLIST FOR CODE

DELETE:
- Silver's bust-forgiveness logic (however currently implemented).
- Ward-the-card, Insurance-the-card.
- Amber Cast, Tempering, Loaded (enchant definitions, shop plaques,
  their die-face-modification code paths).
- Grog/Whisper/Aldric/Corvus's OLD tell logic (Last Call, Counterfeit,
  Confession, In Arrears) — but NOT their badge art/identity.

REPLACE:
- Silver's face-generation: fair 1-6 → weighted table
  `[1,5,1,5,2,3,4,6]`.
- Grog/Whisper/Aldric/Corvus's tell RULE bound to their existing badge
  object with Zero Hour / Kindred / Still Waters / First Strike
  respectively.

ADD:
- Tithe, Ward(enchant), Snare, Break, Trade, Snuff, Fog — full effect
  logic per section 2, INCLUDING all seven Break death-trigger rows
  (Obsidian, Amber, Starstone, Silver, Jade, Vagabond, and the
  no-op for mundane materials) — implement all seven together, not
  Obsidian alone, since the whole point of widening was to avoid a
  single dominant partner.
- Steady Hand, Fair Trade (Silver's two new cards).
- Face-restriction validation (1/5 only) in the enchant shop flow, plus
  the new face-picker UI step.
- The universal icon-resolution rule (banks 0, fires effect, never
  both) as shared logic all seven icon enchants call into — implement
  once, not seven times, so the section-0 law stays enforced by
  construction rather than by convention.

KEEP UNCHANGED: Quicksilver (all logic as-is), Retort, Reprisal (Silver
cards), Mabel/Finnick/Brutus/Ambrose's tells, all other families, all
other badges' art, the badge mechanic itself (worn/wagered/lost), cards
outside Silver's suite.

## 7. TEST CHECKLIST ADDITIONS

- An icon-face keep NEVER also banks its natural number — verify across
  all seven icon enchants, zero exceptions.
- Enchant face-picker rejects any face except 1 or 5; rejects Jade
  wild-6 and any relic-altered face even if that die shows on 1 or 5
  naturally elsewhere.
- A loadout with 2 Ward-branded dice is impossible to construct (hard
  cap enforced at the shop/loadout level, not just at resolution time).
- A Snare mark clears after exactly one opposing turn, hit or miss —
  verify it cannot persist into a second opposing turn under any
  sequencing (mid-turn cap crossings, sudden death, etc).
- Breaking a die of each family fires exactly that family's row from
  the section 2 table and no other — verify all six family triggers
  plus the mundane no-op, seven cases total, no cross-contamination
  (e.g. breaking Jade must never also pay Obsidian's +1000).
- Silver hand bust rate lands at ~26% over a large sample (regression
  target from section 1's sim).
- Still Waters correctly suppresses Obsidian's shatter check specifically
  (the only sim-validated case) — flag other families' suppression for
  manual review before trusting in a live build.
