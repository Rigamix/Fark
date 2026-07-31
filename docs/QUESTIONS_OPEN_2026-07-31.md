# Fark — open questions

**Raised 2026-07-31. All UNANSWERED.** Grouped by subject, not by which
audit produced them — the round numbering in `DESIGN_QUESTIONS_3.md` got
confusing, so that file is now an archive and this is the live list.

Nothing here blocks work. Everything shipped under a stated assumption, and
each entry says what reversing it would cost. Where a default was picked to
keep moving, it is named as a default to overrule, not a decision taken.
Anything the brief itself marks unvalidated is flagged, so a ruling is not
mistaken for evidence.

Answers can go straight back as a doc like `AUDIT_RESOLUTIONS.md` — numbered
replies against the numbers below are ideal.

**53 open questions.**

---

## Break — the seven death-triggers

Break destroys one of your own dice for the match. Every family has its own trigger when broken; only Obsidian's is sim-validated.

**1.** LEGACY SAVES: is a retro-repair wanted? A run already spliced by the old Break plays five-die matches until the player opens the shop or loadout, which then appends a plain BONE in the wrong seat - material, brand and lane position all silently lost. There is no record of what was destroyed, so the only honest repairs are (a) leave it and let the bone stand, or (b) refund the die's gold value. Currently doing neither.

**2.** FAIR TRADE + BREAK: when the BORROWED die is broken, the player's own lent die (`_ft.was`) cannot come home this match - Break destroyed the seat it would return to, so the player finishes at five dice and the lent die reappears only at the next match. Is that the intent (Break costs a SEAT), or should `was` slot back in and Break instead cost the borrowed die only (player stays at six)? The current behaviour is the conservative reading of 'loadout drops to 5 dice for all remaining turns'.

**3.** PRESERVE: the guard ships armed but inert because Preserve-as-a-visible-die does not exist. Whoever builds the amber casing must set `d._preserved` on the pool die, or give `G._famPreserve` a `die` or `lane` field - `_breakPreserved` already answers to any of the three. If the built version picks a fourth shape, this guard silently stops working. Worth naming the field in the brief.

**4.** `opts.permanent` is now dead weight at both call sites. Delete the argument entirely (touching the Obsidian-shatter line at 22244, which may belong to another item), or leave it as documented-vestigial? Left as-is here to keep the blast radius small.

**5.** The startPTurn loan-death branch (21538-21548) still splices the stash permanently. Same ruling applies to it; it belongs to the Fair Trade / Trade-enchant items rather than this one. Who takes it?

**6.** **Does "steals" take FROM the rival, or only give TO the player?** Today it only adds to the player's turn — `G.oPts` is untouched. The brief's single word "steals" does not settle it, and a deduction is a much bigger swing than the value fix. Left as a gain. Cheap to change (one line), so it is worth an answer before the harness pass rather than after.

**7.** **The magnitude is still unvalidated.** P382 made the row mean something measurable — what the rival banked on their last turn, 0 if they busted — but the brief marks every row but Obsidian's a proposal and open item 5.4 asks for a harness pass. Do not read "it works now" as "the number is right".

**8.** Vagabond's row reads G._oUnbanked, which is written in exactly one place - `G._oUnbanked=oppBank;` inside runOppTurn's roll loop - and is never cleared when the rival banks or busts. Because turns strictly alternate, Break can only fire on the PLAYER's turn, when the rival's genuinely-unbanked total is 0 by construction, so the brief's literal wording would make this row always pay nothing. What ships instead is the rival's running total from their PREVIOUS turn, lagging one roll behind (oppBank is read before that roll's points are added) and paid even when the rival already banked those points safely or busted them away. I did not change it: making it literal makes the row vacuous, and the brief calls this row an unvalidated proposal (open item 5.4). Needs a ruling on what the number should be, and then a field written at the right moment to hold it. I have flagged this as a spawnable follow-up task.

**9.** Starstone's row returns from the top of endPTurn, before G.pTurns++, G.turnNum++, G._pLastRolls, G.flintlockFired's reset and the turn-cap / final-answer checks. Falling Star's extra turn (G._fExtraTurn) sits AFTER all of that and is additionally gated on neither side having crossed the target. So a Starstone extra turn does not count against the patron turn cap and does not advance turnNum, which among other things means Quicksilver's once-per-turn allowance does not refresh on it (famQuicksilver gates on G._qsTurn===G.turnNum). Both readings of 'one immediate extra turn' are defensible and the win check is safe either way (handleBank calls endMatch before endPTurn is ever reached), so I left it alone - but the two extra-turn mechanics in the file disagree with each other and one of them is wrong.

**10.** Brass and Crystal are priced, effect-carrying dice that _matFam resolves to null, so they take the mundane no-op row. The brief's mundane row names only 'iron, flint, lead, plain bone'. Ruby (retired), jade3 (retired, resolves to jade) and lucky are the same shape. If Brass and Crystal are meant to be mundane for Break purposes that is fine and already true; if they were overlooked when the table was written, they need rows.

**11.** Jade's row now claims the roll Break interrupted, which is what makes it non-vacuous, but it means the row's value is 'a fresh hand that costs no roll' rather than 'an extra roll on top of the one you were making'. The brief says 'immediately grants one free full reroll of every currently-live die, no cost', which is what I implemented; a reading where the scatter lands AFTER the pending roll resolves (a genuine second chance, and a bust escape) would be more powerful and would collide with Ward/Amber's verb. Worth confirming before the harness pass open item 5.4 asks for.

## The Trade enchant

Swaps your die with the opponent's in the same lane. Match-scoped per the 4b correction. **Its audit found Trade writing through to `S.run.dice` with a comment saying "for the rest of the RUN" — that contradicts the ruling and is not yet fixed.**

**12.** The rival's dice cannot carry brands — there is no opponent enchant array anywhere in the file. So the enchant half of the swap is one-way: the player's brand goes across and nothing comes back. Is that the intended reading of "the WHOLE die swaps", or should the rival get a brand slot so a rival-branded die can genuinely cross the other way? (Note resolution 43 already wants the NPC's Preserve to get a visible die — same asymmetry, same shape of answer.)

**13.** Trade is now self-consuming: the brand leaves with the die, so that seat has no brand for the rest of the match and cannot trade again. The old carve-out kept the brand on the seat and let it re-fire. One-shot-per-match follows from the ruling but is a real nerf — confirm it is wanted before it ships.

**14.** Should the visible swap-back get the same engineering the ruling bought for Fair Trade (resolution 31: "a die that visually still reads borrowed after it's mechanically the player's own again is exactly the state-lies-about-truth problem")? Today the traded die keeps its old material and brand in the kept tray until the next throw, because reDrawDieFace only does pips and the 3D mesh bakes the brand at creation.

**15.** Runs saved before this patch already have a Trade baked permanently into S.run.dice, with no record of what was swapped. Let those runs ride, or is a coarse migration (e.g. refund the enchant's 350g the way _enchInit's _enchV=2 migration refunds retired enchants) worth it?

**16.** Break's half of the same ruling — "the destroyed die returns fully restored at the start of the player's NEXT match" — is NOT addressed here. `_breakDie` -> `_removeDieAt(lane,{permanent:true})` (16612) still splices S.run.dice and S.run.dieEnch for good. That is a separate item and needs its own return-at-next-match hook; flagging it so it is not assumed covered by this patch.

**17.** VISIBLE SWAP-BACK, the one part of 4b I could not deliver literally. The swap is fully visible when it fires — the die is rebuilt at its lane and I verified the change down to the D3X mesh material. But endMatch clears both dice rows eight lines after the restore runs and drops the end overlay over the table, so there is no lane on screen to animate the revert at. It currently ships as corrected state plus a log line, with the post-match loadout screens showing the truth. Is that enough, or does the revert want a real beat — hold the rows for ~600ms after a match that had a live Trade and play the swap backwards at both lanes before the overlay? That is a UI change with a cost, and I would rather it were signed off than assumed.

**18.** TRADE'S PRICE. 4b already flags that ~350g should be revisited once self-consumption is real, and after this patch it genuinely is one use per match. It is also now strictly weaker than the shipped behaviour in a way the price never accounted for: you rent the rival's die for one fight instead of keeping it for the run. Worth naming in the pricing pass rather than left to be noticed later.

**19.** THE `naked_run` FEAT READS THE LIVE MATCH LOADOUT, not the owned one (`G.matchDice`, falling back to `S.run.dice`). My restore makes it honest for Trade, but Break and Obsidian's shatter also mutate `G.matchDice` mid-match, so the feat is evaluated against whatever survived the fight rather than against the six the player actually built. Is 'win using only plain dice' a statement about the build or about the match as played? If it is the build, the check should read `S.run.dice` and the whole class of interaction goes away.

## Fair Trade — the card

Borrows a die from your own stash. Its loan clock is explicitly unchanged by match-scoping; only the death clock inherits it.

**20.** Does the ruling's 'both sides' true owned loadouts fully restore the instant the match ends' reach the FAIR TRADE CARD, or only the TRADE ENCHANT? I read it as the enchant only -- the brief frames it as the opponent-side swap, and the card's own printed text sells roll/turn duration, not match duration. So I left the loan clock alone (roll for tier I, turn for II/III) and applied the ruling only to the death clock. If the intent was that a Fair Trade loan also runs to the end of the match, tier I and tier II collapse into each other and both card texts need rewriting -- flag it rather than let me pick.

**21.** When a BORROWED die is broken, the player ends the match down one seat and holds their own benched die back in the stash-equivalent limbo until the next match. Should their own die instead return to a seat immediately, so the cost is 'you lose the borrowed die' rather than 'you lose a seat'? I implemented the seat loss, because that is what makes breaking a borrowed die cost exactly what breaking an owned one costs and is what stops Fair Trade erasing Break. But it does mean a passive, uncontrolled 6%/roll Obsidian shatter of a borrowed die costs the player a seat for the rest of the match -- which is the outcome the original brief's 'deliberately NOT a stake' language was written to avoid.

**22.** A die that died on loan is unlendable for the rest of that match (G._ftDead). Should the player be TOLD which stash die is out, and why? Right now the only signal is a famLog line at the moment of death and the card quietly reaching for a different die next time. If a die can be conspicuously missing from the stash for half a match, the peek/loadout UI probably needs to show it as broken-until-next-match rather than absent.

**23.** Resolution item 32 puts tier I's 'this roll' at the end of the CHOOSING phase. If a borrowed die is still on the table when its tier-I loan expires mid-turn, does the die vanish from the row it is sitting in, or does the loan hold until the row is committed? That decision belongs to the tier item, not this one, but whoever takes it should know the loan-end path is now in two places (startPTurn for expiry, _ftLendDied for death) and would want a third for the mid-turn case.

## Brutus's relic, Silver, and the Ward cap

Built and shipped (P383). These are what it raised on the way.

**24.** Silver's bust-rate regression target has no policy attached. I measured 23.5% (max-keep, bank at 500), the in-file comment claims 28.2% at 'a 500-point banking policy', and the brief says ~26%. All three describe the same shipped table - the spread is entirely the keep policy. Should a canonical harness policy be written into the test checklist so the ~26% line is actually falsifiable, or should the checklist state the ratio (silver busts ~0.55x as often as bone, which held at 0.54-0.58 across every policy I tried) instead of an absolute?

**25.** Can Brutus's relic ever carry Quicksilver as well as its born Ward? The game's own rule is 'one enchant per die, ever', so the relic is now permanently unbrandable. That reads correct to me, but it is the one ability the relic can never have, and Quicksilver is architecturally a whole-die passive rather than a face brand - so 'one per die' may not have been written with a die that arrives pre-branded in mind.

**26.** If a player buys a Ward and THEN wins Brutus's relic, which one gives way? I refund the purchase (350g) and keep the relic's, on the reasoning that the born brand is what the die IS and the purchase is the reversible half. The alternative - the relic simply arrives unwarded - is defensible too and needs no refund. This case is not covered by the brief, which only says the relic 'counts against' the cap.

**27.** Kindred x Ward (brief open item 1) now also governs the relic: if 'double strength' is ever defined for Ward, Brutus's relic inherits it for free, and a Kindred build holding the relic gets the doubled version without ever buying a brand. Worth naming explicitly whenever that decision is made.

**28.** AUDIT_RESOLUTIONS #2 asks for a sim-check on Whisper's Fang now that it actually bites: it went from never paying its cost to paying -200 on every bust where it sits kept, and my patch widens the 'sits kept' test to catch Fangs kept second in a group (previously invisible), so the real-world rate is higher than a naive reading of the old code would suggest. That harness pass is not something I can do from inside this area.

## The 1-or-5 brand restriction

Adopted, Phase A only, picker skipped permanently. Not yet built.

**29.** Refund amount for an illegal-face brand: the patch pays the enchant's own current ENCH_ICONS price (tithe 150 / ward 350 / snare 400 / break 300 / trade 350 / snuff 300 / fog 250), which is the most precise figure available — the same reasoning §4b uses to give Trade an exact 350g against Break's estimated ~450g. Confirm that is wanted rather than a flat per-brand figure, since §5 open item 3 says all seven prices are still placeholders and a later pricing pass would silently change what old saves get back.

**30.** A refunded Ward frees the one-Ward-per-loadout cap, so a player whose only Ward sat on a 2 gets 350g back AND may immediately re-brand a Ward. That reads as correct (they never legally held one), but it is a state change the cap's owner (Area A) should sign off on.

**31.** The refund is announced only through famLog, which scrolls. Section 4b's "state must never lie" principle got missing dice a persistent visual; an illegal-face refund arriving as one scrolling line on next load may want the same treatment — a shop-visit notice or a loadout marker. Out of scope here, flagged rather than guessed.

## Badges — Kindred and Still Waters

Kindred is Tithe-only until "double strength" is defined for the non-numeric enchants. Still Waters suppresses family traits, unvalidated.

**32.** Kindred's 'double strength' for Ward / Snare / Break / Trade / Snuff / Fog is still undefined and is left deliberately unimplemented (`doubles` is now documented at the call site as an opt-in whitelist). This is the ask the brief instructed me to make rather than guess: what does a doubled Ward, Snare, Break, Trade, Snuff or Fog mean, if anything? Candidate shapes, not proposals: Ward -> two arms per turn, or a two-thirds save instead of a half; Snare -> the mark survives two opposing turns, or halves twice; Snuff/Fog -> two lanes, or two turns; Break/Trade -> nothing is coherent, so they may simply never double.

**33.** Should `'confession'` join `_SEAL_POOL` (line 10726)? It is the only one of the four rework badge ids not in it, so after this patch Still Waters can be sleeved but never sealed, while Kindred can be both. Adding it changes the sealed-seat difficulty distribution, so I did not do it unasked.

**34.** Kindred's bark. I changed "Marked dice sing louder here — for both of us." to "Marked dice sing louder at my table." because the old line promises the mutual rule the rescope removed and the engine cannot run. Confirm the replacement copy, or supply a better line — happy to take a different one.

**35.** Still Waters + Break is now a SILENT death: the player spends a Break on a worked die and gets nothing but a status line after the die is already gone. AUDIT_RESOLUTIONS #29 already extended the targeting-ring work to Break — should the ring also mark worked dice as hushed BEFORE the tap, so the cost is visible at the decision rather than after it? That is a UI change in Area C/F territory, so I have not built it.

**36.** Three sim passes this patch newly requires, all flagged UNVALIDATED in the code comments: (a) Still Waters vs Break, all seven rows, not just Obsidian's; (b) Still Waters vs the PASSIVE shatter — the ~644-point figure the brief quotes was never actually being paid, so it is a projection, not a measurement of the shipped build; (c) Grog's Tooth's own 10%/+1500 under the badge, which AUDIT_RESOLUTIONS #6 explicitly says must not be extrapolated from plain Obsidian's 6%/+1000.

## Legacy saves and missing-die visibility

Runs saved under the old run-scoped behaviour, and showing a die that is out until your next match.

**37.** Trade refund breadth: the save cannot distinguish a trade brand that FIRED under the old run-scoped rule from one bought and never used, so patch 3 clears and refunds all of them at 350g. Confirm that is the intended reading of brief 4b's 'refund exactly 350g', or should an unfired brand be left alone at the cost of leaving genuinely spoiled runs unrepaired?

**38.** Break refund arithmetic: brief 4b says 'a flat ~450g'. A legacy save can be short by more than one die (two Breaks in one run under the old rule). Patch 2 pays 450g PER missing die. Confirm that, versus a single flat 450g however many are gone.

**39.** Migration timing: _famDiceMigrate only runs from famLoadoutShow and _gbShop, so a legacy save still plays five-die matches until the player opens one of those screens. Should it be hoisted to run-load so the repair lands before the next match, or is the existing (unchanged) timing acceptable?

**40.** Placeholder label wording: Break and Obsidian's natural shatter share _removeDieAt, so the tag is cause-neutral ('OUT' / 'BACK NEXT MATCH'). If the CD wants them distinguished ('BROKEN' vs 'SHATTERED'), that needs an explicit cause threaded from both call sites (16766 and 22374) — I did not invent one, and specifically did not repurpose the vestigial opts.permanent flag for it, since brief 4b says that flag must not be wired back up.

**41.** Peek scope: openPeek/openBossPeek scout the OPPONENT's dice, so there is no player-side gap to show there. The only other renderer of the player's own live loadout mid-match is _firstStrikeRender's 'YOU' row (16524), which is gated on the Corvus badge and was not active in my probe. Should the out-dice appear there too, and if so at their original lane position (which reopens crossArea #2's renumbering problem) or appended at the end?

## Cut enchants and the universal icon rule

Confirming the cuts are complete and routing all seven icons through one shared resolution.

**42.** Patch 2/3 rule an icon+illegal-die keep as REJECTED, on the reading that the brief's clarification ("a branded die must never invalidate an otherwise-legal selection") runs one way only, and that handleRoll's existing NO SCORE is the correct half of the pre-existing disagreement. The other reading — a brand rescues the whole selection, letting a player dump unscoring dice — would instead mean patching handleRoll to accept. I took the narrow reading because the wide one hands every branded die a free discard, which is the same unconditional-safe-option shape section 1 deleted Silver's identity to remove. Worth a confirm.

**43.** When a mixed keep commits, the icon die is excluded from `vals` but included in `dice`, so it shows in the kept tray while contributing 0 to Half Measure's `totalCommitted` (which counts `k.vals.length`). Both commit paths already agree on this and I did not change it — but "does a cast die count as one of your three committed dice" is a real design question nobody appears to have answered.

**44.** Zero is the correct value for an icon component, and the preview says so by printing the enchant's NAME instead of a grey 0 — but only when the selection is icons-only (`selD.every(_dieIsIcon)` at :22926). A mixed keep prints just "+500" with no sign that a brand is about to fire. Should a mixed selection also name the enchant (e.g. "+500 · TITHE")? Out of scope for a correctness patch, but it is the one place the universal rule is invisible at the moment the player commits to it.

## The patron lore and dialogue system

Engine built and tested; 30 lines authored. Removed from the character sheet on your call, so nothing calls it right now.

**45.** **The seed six cannot be seated.** Odo, Hollis, Peck, Ferrand, Fenn and Tam have no portraits, and a seat's name IS its portrait's filename. Their lines are written and in the table, inert. Three ways out: draw them portraits, let a named patron use a portrait that is not their own (breaks the name/file link, and the same face would carry two names on different nights), or leave them as authored-but-unused. Currently the third. Ferrand matters most of the six — his pair is the brief's own worked example of the condition system.

**46.** **Scale target for the named cast.** The lore doc proposes 20-30 for launch and 24 have art. Do the seed six get art to reach 30, or is 24 the cast?

**47.** **Full multi-stage ladders for all 24** are flagged in the doc as a separate pass. Patrons with no personal line currently fall through to the ambient pools, which reads fine — so this is a "when", not a "must".

**48.** **The Tankard badge as tavern folklore** ("some say it's why nobody's robbed the till in forty years") is a proposal in the doc, not written. It would drop straight into the gossip pool as data if wanted.

**49.** In-match, through the existing `DLG` system (64 call sites, currently rival barks only) — a named patron would have a voice at the table they are playing at, and a reaction line has something to react to.

**50.** Somewhere on the night screen that reads as overheard room chatter rather than a character speaking to you.

**51.** Nowhere yet, until the full ladders are written.

## Brief housekeeping

Places the brief now contradicts itself or the code. Not gameplay calls.

**52.** **Section 2 still says a die killed on loan is lost "permanently"**, while 4b says the player's own die returns at once and they stay at 6. Both are satisfiable if "permanently" is read as match-scoped (which is how the whole Break/Trade correction reads it, and how P376/P377 implement it) — but the word is now the odd one out and will mislead the next reader.

**53.** **4b's closing line says Break's next-match return "still needs building"**. It was built in P375, before 4b was written. Stale rather than wrong; worth striking so it is not treated as outstanding.
