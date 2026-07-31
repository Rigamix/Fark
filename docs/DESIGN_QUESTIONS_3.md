# Design questions — for the creative director

Raised by a 25-agent sweep of the whole open backlog (2026-07-30), plus what came
up while fixing the dice this session. **None of these block code.** Everything
answerable from the brief or from the code has already been decided and built;
what is left here is the set where two defensible answers exist and the choice is
yours. Where an agent picked one to keep moving, its pick is named — treat it as a
default to overrule, not a decision taken.

Companion docs: `DESIGN_QUESTIONS.md` (all five answered),
`DESIGN_QUESTIONS_2.md`, `AUDIT_BACKLOG.md`.

---

## From the dice work, this session

**1. Brutus's relic — which face carries the innate Ward?**
The relic becomes a die that permanently carries Ward. A branded face banks ZERO
when kept, so the brand's real price is the score you forfeit to arm it. The agent
chose **face 1** on the reasoning that the relic costs no gold, so it should pay in
face value on the most expensive face there is — brief §2 measures ~125 EV/turn
forfeited on a 1 against ~73 on a 5. One-token change if you'd rather it were a 5.

**2. Deleting Brutus's shield also deletes two other effects. Keep them?**
The shield branch in `doBust` is the ONLY place the rival's Ill Omen pays out and
the only place Whisper's Fang bites on a bust — they were written inside a branch
that only ran when a shield BLOCKED a bust, so they have effectively never fired.
Removing the shield removes them too. The proposed patch hoists both onto the real
bust path instead, which makes them fire for the first time. That is a balance
change, not a refactor: **do you want Ill Omen and Whisper's Fang live on every
bust, or should they stay dormant?**

**3. How fast should the rival's select-and-score beat be?**
The rival currently scores before its dice have settled, because scoring runs in
the same synchronous block that creates them. Fixing it means settle → select →
score, like yours. But yours is paced by a human hand. **How long should the rival
"think" between its dice stopping and its picks lighting up** — snappy (~200ms, it
reads as instant), or a deliberate beat (~600ms, it reads as a decision)?

**4. The victory headline still reads "LAST ORDERS RUNG".**
Wrong under either meaning now that LAST ORDERS is the night-end/run-death screen —
winning the final boss is announced with the name of the losing screen. Sub-label
is "you own the night". Your copy, so it wants your line.

---

## From the backlog sweep

### STILL WATERS (Aldric, tell id 'confession') vs OBSIDIAN's shatter — brief section 7

*(investigator returned `patch-ready`)*

- BREAK vs STILL WATERS. Breaking an ENCHANTED Obsidian die still pays BREAK_TRIGGERS.obsidian's guaranteed +1000 under the badge, because _breakDie dispatches off _matFam, not _dieEffect. Is a family DEATH-TRIGGER a 'family trait' the badge should hush, or is the badge only meant to hush what the die does on its own? Leaving it live gives a clean read ('Still Waters quiets the die, it does not stop you smashing it') and preserves section 4's whole timing trade. Suppressing it makes the badge a hard counter to the single best-validated Break partner. Not sim-tested either way. I did not touch it.
- GROG'S TOOTH. The obsidian relic shares the shatter_bonus mechanic, so P9 silently makes it go quiet too when enchanted. Intended, or should relics be badge-proof? Brief only validated the plain Obsidian row (6% / +1000), not the relic's (10% / +1500), and 14.5% of match value is a very different number at +1500.
- THE OTHER FOUR FAMILIES. Suppression of Jade's wilds, Amber's triple bonus and Starstone's bank bonus is ALREADY LIVE via scoreSelection's dieEff, and Silver's odds-skew via _rollTable — all shipped before this patch, all flagged INFERRED-not-validated in the brief and in the code comments. This patch does not change them. Do you want a harness pass on those four before Still Waters goes anywhere near a live build, or do they ride on the Obsidian number?
- BADGE ART / IDENTITY vs the id. The tell id stays 'confession' forever now (the badge object keeps it, per the brief's one-object-one-look law), which means every future reader of _ruleActive('confession',...) has to know that string means STILL WATERS. Worth a rename pass on the id with a save migration, or is the comment at the tell definition enough?
- P10's replacement barks are my draft in Aldric's knightly register ('Thy worked dice forget their breeding at mine table, sir'). Your call on the wording — the only requirement is that they stop announcing a card seal that no longer happens.

### (A) famCardArt has no missing-art fallback; (B) victory headline reads "LAST ORDERS RUNG"

*(investigator returned `patch-ready`)*

- Victory headline — my pick is in the patch, but this is your copy. THE HOUSE IS YOURS (in patch): the exact inverse of BARRED two lines below, and it reuses the game's own word for the establishment ('THE HOUSE REMEMBERS YOUR NAME' on the Ambrose match-end card, 'the house' as the boss fallback). Cost: it doubles up on possession with the sub-label 'you own the night' — headline claims the place, sub claims the time, which I read as reinforcement but you may read as repetition.
- Alternative A — EVERY TABLE BEATEN. Headline states the fact, sub-label supplies the feeling, no possession echo, and 'table' is the run's unit (you sit down at tables all night). Flatter and more reportorial than BARRED, which is the trade.
- Alternative B — THE HOUSE REMEMBERS YOUR NAME. Already yours: it is the line on the Ambrose victory card at line 26429, so the run-end screen would echo the moment it came from. Costs two lines in the 230x64 box and repeats a string the player read sixty seconds earlier, which is either a callback or a copy-paste depending on your taste. I avoided anything containing 'LAST' so the win never sits adjacent to the LAST ORDERS name again.
- The stand-in prints the card's NAME on the face, which brushes the art law in the famCardArt header ('tier is a roman chip — no baked text'). I read that law as governing the painted art, not a placeholder, and without the name Steady Hand and Fair Trade are two identical blank cards in the loadout row. Say the word and I will strip the text to a bare parchment-and-family-colour swatch.
- Placeholder look: parchment #f0e3c6 field with the family colour as a 3px inset edge, matching how .fcvTier already carries the family colour as a border. The alternative is the family colour as the whole field with dark ink on top — I rejected it because silver (#b9c2cc) and starstone (#4f74e3) sit at opposite ends of the legibility range and one rule cannot serve both.

### Rework brief §2's 1-OR-5 FACE RESTRICTION + shop face-picker step, vs the random-face-draw system the code deliberately ships. SCOPE ONLY — no patch.

*(investigator returned `design-call`)*

- Adopt the 1/5 restriction at all? The strongest reason is one neither document states: a brand on 2/3/4/6 is free bust insurance (measured: a flat 25% cut in single-roll bust rate at every free-dice count, 44.55%→33.41% on the last roll, zero effect on 1/5). That is the same 'free safe keep' shape §1 deleted Silver's identity to remove. Does that settle it, or is a 25% conditional bust cut an acceptable price for the random draw's virtues?
- Split the item — rule now, picker later? Phase A (swap three call sites to the already-written `_iconFaces`, keep the existing one-gesture spin, just draw from [1,5] instead of all six) is ~half a day and captures the whole mechanical benefit. Phase B (the picker screen) is ~a day plus an art ask and re-opens the 1-vs-5 cheese the random draw closed. Ship A alone, or hold for both?
- Is the face-picker screen worth it when the answer is always the same two buttons? No die in DICE_TYPES lacks both a 1 and a 5, so the step is a forced binary, every single time, for all seven icon enchants. Three taps instead of two, for a choice with two options.
- Save migration for the ~4-in-6 existing brands sitting on an illegal face: refund the enchant and clear it (precedented — `_enchInit`'s `_enchV=2` block does exactly this for the cut enchants), or silently move the brand to the die's 1? Refunding is honest but takes a permanent purchase away; moving is quiet but rewrites a purchase under the player.
- If the picker ships, per-face pricing for the reopened 1-vs-5 gap (brief open item 2)? Measured 1.39× on my per-roll metric, 2.4× on PROTO_NOTES'. Two numbers, no agreement, and the brief never resolved it.
- Anchor: fix the index mismatch now, or leave it dead? The card is currently unreachable (`effectiveCards()` hard-returns []; `pCards=[]`; `generateOppCards` returns []; `anchor_f` is aliased into `vanguard_f`). The three-site bug (21839 / 22788 / 23530) only matters when the position cards come back. Worth a guard now, or a note on the card's revival ticket?
- The lit-ROLL-then-NO-SCORE trap is live TODAY on any brand on any face, and this change does not touch it: the preview accepts a selection on `ok = pts>0 || _selHasIcon` that the commit then rejects on `pts<0`. Should the preview refuse the mixed selection, or should the commit accept it and score the non-icon part? That is a rules decision, not a bug fix — does a branded die dragged into a dead selection poison the whole keep, or just contribute nothing?

### Brutus's relic becomes a die that permanently carries the Ward enchant, pre-applied and counted against the one-Ward-per-loadout cap; the guaranteed full bust-save (shield path) is deleted.

*(investigator returned `patch-ready`)*

- WHICH FACE? I put the Ward on the relic's 1 (`face:1` in the die def). Reasoning: an icon face banks ZERO when kept, so the brand's real price is the score you forfeit to arm it, and a relic that costs no gold should pay in face value — the brief measures ~125 EV/turn forfeited on a 1 against ~73 on a 5. The counter-argument is just as real: on a 1 the player gives up 100 points every time they want the half-save, which may make the relic's whole ability something nobody ever chooses to use. Switching to `face:5` is a one-token change in patch 1 and nothing else moves.
- SFX.shield is deleted by patch 4 because its only call site went with the shield branch. It is a well-made 'shield up' ring-and-bell, and the Ward currently arms in complete silence (ENCH_ICONS.ward.fire only writes a famLog and a status message). Re-homing it into ward.fire is one line and would give the Ward the audio beat it lacks — but that is the Ward's item, not Brutus's, and I did not want to reach into a system another pass may be rewriting. Worth a separate ticket; say the word and I will supply the patch instead of the deletion.
- Patch 9 hoists Ill Omen and Whisper's Fang onto the live bust path. Confirm that is wanted. It is the only way to keep them at all, but it turns two effects that were silently inert into two that fire on every bust, which is a balance change nobody asked for in this item.
- Brutus's relic is family `silver` per _RELIC_FAM, but it has no `rollTable`, so it does NOT get Silver's weighted [1,5,1,5,2,3,4,6] geometry — it rolls a fair 1-6. That matters more now than it did: Silver's table doubles the frequency of exactly the face the Ward now sits on. Should the relic inherit its family's weighting? I left it alone as out of scope, but the two decisions interact.
- Not mine to fix, but it bears on the face choice: `_iconFacesAny` (L30138) lets a purchased brand land on 2/3/4/6, and the commit path at L21855 accepts an icon keep on any face — so brief section 2's '1 or 5 only' restriction is not what the code does (a deliberate swap to a random draw, per the comment at L30134). Branding a 3 is a nearly free Ward. The relic's hand-picked face sidesteps this, but the cheese the restriction existed to close is still open on every die the player pays to brand.

### Rename `_stakesRisingBonus` (docs/AUDIT_BACKLOG.md:365) — it is the shared turn-bonus pot, not Stakes Rising's private field

*(investigator returned `patch-ready`)*

- The NPC mirror `_oStakesRisingBonus` (6 occurrences) is genuinely Stakes-Rising-only today, so I left its name alone. But if the NPC ever gains Flintlock or hot-dice bonuses it becomes the same lie. Do you want it renamed to `_oTurnBonusPot` now for symmetry with the player side, accepting a name that is currently over-broad, or left accurate until the NPC actually shares the pot?
- The bank pop labels the entire pot '+N STAKES' even when most of N came from Flintlock or hot dice. Should that become a per-source breakdown ('+300 STAKES +200 FLINTLOCK'), or is one lumped number the intended feel at the bank moment?
- P04's comment now reads '_turnBonusPot is the shared pot for exactly this'. That sentence only works because the paragraph above it lists what 'this' is. If you would rather it stand alone, say so and I will rewrite it to name the four contributors explicitly - it just makes an already long comment longer.

### STEADY HAND — three remaining defects: (1) the reroll gives no feedback of its own, (2) an already-selected die shows no red target ring, (3) G._steadyArmed is never cleared at turn end

*(investigator returned `patch-ready`)*

- The pop reads `🔄 3` — a colour emoji plus the new face, copying Finnick's Palm's `spawnPop('✋ '+newVal, el)` exactly. That fits what the file already does (🔄 SWAPPED, 🛡️ SHIELD, 💀 −HALF, 🔥 all ship today) but a colour emoji sits oddly next to the gold/seal-red pencil-line direction. Measured alternatives that still fit above an edge die: `REROLL 3` (~88px) fits marginally; `STEADY HAND 3` (~143px) clips off the left edge on the leftmost die and is not an option. Keep the emoji, or go plain text?
- Should the pop name the card at all? Right now the die says what it became and the status line says STEADY HAND — but only on the bust path, where refreshSelUI never runs. On the normal path the player sees a face change and a glow and has to remember which card they just played. Naming it costs width the leftmost die does not have.
- Patch C puts the disarm in endPTurn. It could equally live in startPTurn beside the `G._wardArmed=false;G._bustImmuneTurn=false;...G._breakArmed=false;` block at 21473, where its sibling flag is already reset by name — arguably the more discoverable home. endPTurn covers the rival's turn as well, which startPTurn does not. Which reads better to you?
- Patch A also restores BREAK's targeting ring on a selected die (same class, same hole, 16565). Wanted, or should the rule be narrowed so only Steady Hand changes?
- Should the reroll spin the die at all in 3D? The WebGL die already tumbles for 420ms via reDrawDieFace -> D3.roll. Adding `.card-reroll` puts a second, DOM-box rotation over the same window. It is what five other cards do and it is what makes the effect visible in 2D, but if the 3D tumble is considered sufficient the glow could be dropped.

### FAIR TRADE (family card `fair_trade`): (A) tier I and tier II are mechanically identical because both unwind only in startPTurn; (B) canUse approves a trade use() then refuses in silence, and the shee

*(investigator returned `patch-ready`)*

- Tier I's borrowed die can still LOOK borrowed for the rest of the turn under the 3D renderer, even though it now rerolls and scores as the player's own die (see risk 2). Worth spending a D3 drop/re-register — or better, a die-element rebuild in the wrap — to make the swap-back visible? Or is the 'LOAN UP — BONE BACK' pop enough, given the same staleness already ships on the Trade brand?
- Where exactly does 'this roll' end for tier I? I ended it when the player presses ROLL again, not when the first roll's dice settle — so the borrowed die can still be COMMITTED during the choosing phase after the roll it paid for. That reads as the generous, honest interpretation of 'before you roll ... for this roll only', but the stricter reading (the loan dies the moment the dice stop) is a one-word change.
- The sheet's refusal lines are mine: 'lent out — yours comes back the moment you roll', 'too late — the dice are already thrown', 'nothing in the stash to trade for', 'nothing in the stash beats the six you are holding'. Lowercase to sit with 'uses left: 1'. Your voice, your call.
- Every other active card now falls back to a generic 'not right now' when it cannot fire. Should the live cards (Steady Hand, Encore, Double or Nothing) get their own `why` lines in a follow-up, or is the generic line acceptable for now?
- Fair Trade swaps the die but never the seat's ENCHANT — `G._enchArr[lane]` and `S.run.dieEnch` are untouched, so a borrowed die wears whatever brand the seat it visits is carrying, and the player's own die gets it back. Pre-existing and out of scope here, but it wants a ruling: does a brand belong to the seat or to the die?

### tools/shoot_throw_sweep.js reports nonsense and must be fixed or deleted

*(investigator returned `patch-ready`)*

- Overlap is back, and the tool now proves it: 18-27% of six-die opening throws leave a painted pair overlapping by up to 21px, and the live on-screen row overlapped for real in 4 of 10 runs. P349 closed this on 23 rolls that happened to show none. Is ~1 in 5 acceptable at this die size, or does the throw want another pass? That is a separate backlog item and a creative call, not a tooling one.
- docs/AUDIT_BACKLOG.md:329-342 and :368-371 both tell the next reader to 'trust the ground truth' of zero overlaps. That is no longer true after P366 removed the pen. Should I hand you replacement text for those two entries, or do you want to rewrite them once you have decided on the overlap question above?
- tools/shoot_lanes.js:84 `drawnBoxes()` reads `D3X.rend`, which does not exist (the property is `D3X.renderer`), so it has always returned null - and even working it projects a centre point, not an extent. Delete it, or point it at the same `_hullOf` the sweep now uses?
- fark_proto.html:17866 overwrites the relax/spread pass's output with the sim's own resting x (measured: slide identically 0 over 60 solves), which makes the drawnMid footprint model at 17708 and the whole `ext`/`node`/`relax` block dead for positioning. Delete it, or is it being kept as scaffolding for the next attempt at the throw?

### PRESERVE (Amber) must be a visible die, not points — relocate below the turn reset, put it on the table in its casing, make it unrollable/unselectable, drop G.numDice by one, and close the two confirm

*(investigator returned `patch-ready`)*

- BANK is greyed at turn open even though 200 points are already on the table; it lights the moment the player rolls. I left the existing setBtns(true,false) alone. Should the amber die be bankable BEFORE rolling — i.e. is it a head start you must gamble on, or points you already own?
- On HOT DICE the casing is swept with the rest of the row and a fresh six comes out (the points stay in G.kept). Every die on the table scored, so a clean table is consistent — but the card says the die is 'still there', and this is the one mid-turn event that takes it away. Should the casing survive a hot-dice re-throw?
- The casing is drawn as a pool of amber light UNDER the die (DOM wrap, behind the WebGL layer) plus a warm emissive on the mesh itself. It cannot be drawn OVER the die without either painting on the glow canvas (D3X._drawGlow, which currently early-outs unless something is .selected) or a real translucent resin shell in the mesh. Is 'lit from inside, sitting in its own light' the casing Denis wants, or does it need to read as a solid lump the die is embedded in?
- The rival's Preserve is still a flat +100 credited to their bank (G._oPreserve, ~24445). Now that the player's version is a die you look at, the two sides no longer read the same. Should the NPC's also put a visible die on their line, per the brief's 'players track curses and Preserve choices by looking at them'?
- A preserved die's MATERIAL now travels into the amber (it used to be hardcoded 'bone'). A preserved obsidian therefore comes back as an obsidian die on the table — but it is already scored, so its shatter/effect hooks never fire on it. Is a premium die in the casing meant to be inert, or should it still be able to do its thing?

---

_44 questions across 9 areas. Nothing here blocks work in progress._

---

## Round 2 — from the match-scoping work (Break / Trade / Fair Trade)

Raised while implementing the AUDIT_RESOLUTIONS ruling. **None block anything** —
Break shipped in P375 and the other two are re-cutting against it. These are the
places where the ruling admits two readings, or where implementing it forced a
balance change nobody signed off on.

### BREAK must become MATCH-SCOPED (plus the Fair Trade borrowed-die branch, plus the preserved-die Break guard)

- LEGACY SAVES: is a retro-repair wanted? A run already spliced by the old Break plays five-die matches until the player opens the shop or loadout, which then appends a plain BONE in the wrong seat - material, brand and lane position all silently lost. There is no record of what was destroyed, so the only honest repairs are (a) leave it and let the bone stand, or (b) refund the die's gold value. Currently doing neither.
- FAIR TRADE + BREAK: when the BORROWED die is broken, the player's own lent die (`_ft.was`) cannot come home this match - Break destroyed the seat it would return to, so the player finishes at five dice and the lent die reappears only at the next match. Is that the intent (Break costs a SEAT), or should `was` slot back in and Break instead cost the borrowed die only (player stays at six)? The current behaviour is the conservative reading of 'loadout drops to 5 dice for all remaining turns'.
- PRESERVE: the guard ships armed but inert because Preserve-as-a-visible-die does not exist. Whoever builds the amber casing must set `d._preserved` on the pool die, or give `G._famPreserve` a `die` or `lane` field - `_breakPreserved` already answers to any of the three. If the built version picks a fourth shape, this guard silently stops working. Worth naming the field in the brief.
- `opts.permanent` is now dead weight at both call sites. Delete the argument entirely (touching the Obsidian-shatter line at 22244, which may belong to another item), or leave it as documented-vestigial? Left as-is here to keep the blast radius small.
- The startPTurn loan-death branch (21538-21548) still splices the stash permanently. Same ruling applies to it; it belongs to the Fair Trade / Trade-enchant items rather than this one. Who takes it?

### Fair Trade card (`G._fairTrade`): revert P365's permanent deletion of a borrowed die that dies on loan, to a m

- Does the ruling's 'both sides' true owned loadouts fully restore the instant the match ends' reach the FAIR TRADE CARD, or only the TRADE ENCHANT? I read it as the enchant only -- the brief frames it as the opponent-side swap, and the card's own printed text sells roll/turn duration, not match duration. So I left the loan clock alone (roll for tier I, turn for II/III) and applied the ruling only to the death clock. If the intent was that a Fair Trade loan also runs to the end of the match, tier I and tier II collapse into each other and both card texts need rewriting -- flag it rather than let me pick.
- When a BORROWED die is broken, the player ends the match down one seat and holds their own benched die back in the stash-equivalent limbo until the next match. Should their own die instead return to a seat immediately, so the cost is 'you lose the borrowed die' rather than 'you lose a seat'? I implemented the seat loss, because that is what makes breaking a borrowed die cost exactly what breaking an owned one costs and is what stops Fair Trade erasing Break. But it does mean a passive, uncontrolled 6%/roll Obsidian shatter of a borrowed die costs the player a seat for the rest of the match -- which is the outcome the original brief's 'deliberately NOT a stake' language was written to avoid.
- A die that died on loan is unlendable for the rest of that match (G._ftDead). Should the player be TOLD which stash die is out, and why? Right now the only signal is a famLog line at the moment of death and the card quietly reaching for a different die next time. If a die can be conspicuously missing from the stash for half a match, the peek/loadout UI probably needs to show it as broken-until-next-match rather than absent.
- Resolution item 32 puts tier I's 'this roll' at the end of the CHOOSING phase. If a borrowed die is still on the table when its tier-I loan expires mid-turn, does the die vanish from the row it is sitting in, or does the loan hold until the row is committed? That decision belongs to the tier item, not this one, but whoever takes it should know the loan-end path is now in two places (startPTurn for expiry, _ftLendDied for death) and would want a third for the mid-turn case.

### TRADE ENCHANT (lane icon, ENCH_GRID ~30274) — make the whole-die swap match-scoped per AUDIT_RESOLUTIONS "Corr

- The rival's dice cannot carry brands — there is no opponent enchant array anywhere in the file. So the enchant half of the swap is one-way: the player's brand goes across and nothing comes back. Is that the intended reading of "the WHOLE die swaps", or should the rival get a brand slot so a rival-branded die can genuinely cross the other way? (Note resolution 43 already wants the NPC's Preserve to get a visible die — same asymmetry, same shape of answer.)
- Trade is now self-consuming: the brand leaves with the die, so that seat has no brand for the rest of the match and cannot trade again. The old carve-out kept the brand on the seat and let it re-fire. One-shot-per-match follows from the ruling but is a real nerf — confirm it is wanted before it ships.
- Should the visible swap-back get the same engineering the ruling bought for Fair Trade (resolution 31: "a die that visually still reads borrowed after it's mechanically the player's own again is exactly the state-lies-about-truth problem")? Today the traded die keeps its old material and brand in the kept tray until the next throw, because reDrawDieFace only does pips and the 3D mesh bakes the brand at creation.
- Runs saved before this patch already have a Trade baked permanently into S.run.dice, with no record of what was swapped. Let those runs ride, or is a coarse migration (e.g. refund the enchant's 350g the way _enchInit's _enchV=2 migration refunds retired enchants) worth it?
- Break's half of the same ruling — "the destroyed die returns fully restored at the start of the player's NEXT match" — is NOT addressed here. `_breakDie` -> `_removeDieAt(lane,{permanent:true})` (16612) still splices S.run.dice and S.run.dieEnch for good. That is a separate item and needs its own return-at-next-match hook; flagging it so it is not assumed covered by this patch.

_14 further questions. Nothing here blocks work in progress._

---

## Round 3 — raised while building, 2026-07-31

Everything below was decided-in-passing or flagged inline during the dice,
patron and lore work. None of it blocked anything: the work shipped under the
stated assumption, and each entry says what it would cost to reverse.

### Vagabond's Break row

- **Does "steals" take FROM the rival, or only give TO the player?** Today it
  only adds to the player's turn — `G.oPts` is untouched. The brief's single
  word "steals" does not settle it, and a deduction is a much bigger swing than
  the value fix. Left as a gain. Cheap to change (one line), so it is worth an
  answer before the harness pass rather than after.
- **The magnitude is still unvalidated.** P382 made the row mean something
  measurable — what the rival banked on their last turn, 0 if they busted — but
  the brief marks every row but Obsidian's a proposal and open item 5.4 asks for
  a harness pass. Do not read "it works now" as "the number is right".

### The lore system

- **The seed six cannot be seated.** Odo, Hollis, Peck, Ferrand, Fenn and Tam
  have no portraits, and a seat's name IS its portrait's filename. Their lines
  are written and in the table, inert. Three ways out: draw them portraits, let
  a named patron use a portrait that is not their own (breaks the name/file
  link, and the same face would carry two names on different nights), or leave
  them as authored-but-unused. Currently the third. Ferrand matters most of the
  six — his pair is the brief's own worked example of the condition system.
- **Scale target for the named cast.** The lore doc proposes 20-30 for launch
  and 24 have art. Do the seed six get art to reach 30, or is 24 the cast?
- **Full multi-stage ladders for all 24** are flagged in the doc as a separate
  pass. Patrons with no personal line currently fall through to the ambient
  pools, which reads fine — so this is a "when", not a "must".
- **The Tankard badge as tavern folklore** ("some say it's why nobody's robbed
  the till in forty years") is a proposal in the doc, not written. It would drop
  straight into the gossip pool as data if wanted.

### Residual tension in the rework brief

- **Section 2 still says a die killed on loan is lost "permanently"**, while 4b
  says the player's own die returns at once and they stay at 6. Both are
  satisfiable if "permanently" is read as match-scoped (which is how the whole
  Break/Trade correction reads it, and how P376/P377 implement it) — but the
  word is now the odd one out and will mislead the next reader.
- **4b's closing line says Break's next-match return "still needs building"**.
  It was built in P375, before 4b was written. Stale rather than wrong; worth
  striking so it is not treated as outstanding.
