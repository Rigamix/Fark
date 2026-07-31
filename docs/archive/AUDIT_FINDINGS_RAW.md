# Soak audit — raw findings (2026-07-30)

All 72 findings from the ten-agent soak, flattened and sorted by severity.
Kept verbatim because the repro lines are the expensive part: each one is the
shortest reliable way somebody found to make the thing happen.

Generated from the workflow journal at
`.claude/projects/<project>/<session>/subagents/workflows/wf_bb861320-51b/journal.jsonl`
which is SESSION-SCOPED and will not survive. This file is the durable copy.

Nine of ten agents reported; the rival-soak agent died on a server 500, so
rival-specific behaviour over many turns is the one slice with no coverage.

See AUDIT_BACKLOG.md for what is fixed, what is open, and the order to take it.

TOTAL FINDINGS: 72
---
SEV: breaks-the-game | CONF: certain
WHAT: ENCORE played a second time while its first 500 ms resolve timer is still pending runs the whole bust sequence twice: doBust ×2, famFire('bust') ×2, _featBusts 0→2, and the player's turn counter jumps from TURN 1/8 to TURN 3/8 while the rival's oTurns stays 0. RETORT III fired twice off the one bust — the rival went 5,000 → 3,000 instead of 4,000.
REPRO: Deck ENCORE III. Roll a scoring hand. Play ENCORE (card → sheet → PLAY), then play ENCORE again within ~400 ms, and let the second reroll be a dead hand (e.g. 2,2,3,4,4,6). Both pending checks fire.
CAUSE: fark_proto.html:12059 (CFX.encore schedules its bust check on setTimeout 500 ms and never sets G.phase away from 'choosing', so the card stays playable during its own resolve) + fark_proto.html:22355 
---
SEV: breaks-the-game | CONF: certain
WHAT: Break onto a Jade die hard-locks the match. Jade's death trigger ("JADE SCATTERS — EVERYTHING ROLLS AGAIN") re-rolls every free die but never runs a bust check, so a scatter into a dead row leaves the turn with no legal keep, no bust, ROLL disabled, BANK disabled and phase stuck on 'choosing'. Still frozen 5s later. The only way out is to abandon the match.
REPRO: Loadout ['bone','amber','jade','bone','bone','bone'] with {t:'break',face:2} on lane 0. Roll so the row is [2,3,4,6,3,4] (only the branded 2 is keepable). Select the branded die alone -> BANK reads CAST -> tap it -> targeting arms -> tap the jade. Jade scatter
CAUSE: fark_proto.html:16204 — BREAK_TRIGGERS.jade.fire() does `free.forEach(d=>{d.val=_rollD(d)...}); refreshSelUI();` with no anyScoring / _tryBustSave / _delayedDoBust, unlike famQuicksilver (fark_proto.h
---
SEV: wrong | CONF: certain
WHAT: PRESERVE (Amber active) is completely inert. It takes the charge, prints "PRESERVED — A 1 WAITS IN AMBER FOR NEXT TURN", prints "THE AMBER CRACKS — A 1 ALREADY KEPT (+100)" at the start of the next turn, and then the promised kept die and its 200 points are deleted in the same function. numDice is restored to 6 too, so the die reduction never happens either.
REPRO: Deck PRESERVE III. Roll, keep a 1, ROLL again so it lands in G.kept, play PRESERVE, BANK. Next turn: kept tray empty, 6 dice, no points.
CAUSE: fark_proto.html:20948 — startPTurn does `G.kept=[];G.numDice=G.matchDice.length` unconditionally, six lines after :20937-20942 set exactly those two fields from G._famPreserve
---
SEV: wrong | CONF: certain
WHAT: The rival's TAR PIT — the only family card the NPC AI can actually arm — is wiped by the same line. The charge is spent, the game announces "TAR PIT — YOU ROLL 5", and the player still rolls 6 dice.
REPRO: Deal the patron tar_pit via night.roster[i].fcards, bank 800+ so _npcArmActives triggers it, then take your next turn.
CAUSE: fark_proto.html:20934 sets G.numDice=min(numDice,5); fark_proto.html:20948 resets G.numDice=G.matchDice.length in the same call
---
SEV: wrong | CONF: certain
WHAT: The player's card row is drawn on top of the ROLL button and swallows its taps. The cards occupy y725–796; ROLL is y773–880. document.elementFromPoint(215,784) — a point well inside ROLL — returns the card's <img>. Tapping there does not roll (phase idle→idle, turnRollCount 0→0); it opens the card's info sheet instead.
REPRO: Any match with 1–3 family cards equipped. Tap the top edge of ROLL anywhere under a card (roughly the middle 150 px of its 252 px width, top 23 px).
CAUSE: fark_proto.html:1041 — #famRowP{bottom:11.6%;z-index:41} places the row over the controls bar
---
SEV: wrong | CONF: certain
WHAT: FAIR TRADE III used twice in one turn permanently keeps the first borrowed die. The card stores one G._fairTrade record and the second use overwrites it, so only the second lane is ever repaid. It also borrows the SAME stash die twice — the die ends up in two lanes at once and is still in the stash afterwards.
REPRO: Deck FAIR TRADE III (2 charges), put one good die in S.run.diceInv, play it twice before rolling, then finish the turn.
CAUSE: fark_proto.html:12020 — G._fairTrade={lane,was,borrowed} is a single slot, overwritten on the second use; restore at fark_proto.html:20956 only handles that one lane
---
SEV: wrong | CONF: certain
WHAT: STEADY HAND spends its charge on ARM, not on the reroll, and arming it again while already armed silently burns another charge for nothing. Three charges went to one reroll.
REPRO: Deck STEADY HAND III. In the choosing phase play it twice without tapping a die in between, then tap a die. Charges go 3→2→1; exactly one die rerolls. Same loss if you arm it and then hit ROLL or BANK instead of tapping a die — there is no way to cancel.
CAUSE: fark_proto.html:11980 — CFX.steady_hand.use() only sets G._steadyArmed and returns true, and famUse (fark_proto.html:12153) decrements on that true; canUse never checks G._steadyArmed
---
SEV: wrong | CONF: certain
WHAT: Rival family cards are nearly all inert, but they are dealt and shown face-down all match. Every CFX hook returns immediately unless owner==='p', and the AI only ever arms tar_pit / sleight / ill_omen — while patrons draw from the whole FAM_LIVE set (~26 ids). A rival holding PICKPOCKET III + RETORT III banked 1,000 then 3,000 across two turns and never lifted a single point from me.
REPRO: Deal a patron pickpocket/retort/preserve/steady_hand via night.roster[i].fcards and play several rival turns; watch their score move and yours not.
CAUSE: fark_proto.html:11966, 12027, 12031, 12038, 12043, 12072, 12704, 12739 (all gated `ev.owner!=='p'`) vs fark_proto.html:23767 _npcArmActives, which handles only tar_pit, sleight, ill_omen
---
SEV: wrong | CONF: certain
WHAT: ZERO HOUR does not end the turn when the branded die is the only thing kept. The status line says "ZERO HOUR — NO MORE ROLLS" and then the turn just carries on with ROLL fully enabled. This is the tell's most natural trigger: a brand banks nothing, so keeping it alone is the normal way to fire an icon.
REPRO: Grog / a Zero Hour seat, dieEnch[0]={t:'tithe',face:1}. Roll until lane 0 shows its branded 1. Select ONLY that die (BANK reads CAST, turn points 0). Press ROLL. Gold +15 fires, "ZERO HOUR — NO MORE ROLLS" prints, and then nothing: phase stays 'choosing', turn
CAUSE: fark_proto.html:22993 — handleBank's `if(total<=0)return;` bails out of the bank that fark_proto.html:21401 schedules (`setTimeout(function(){handleBank();},700)`) after clearing G._zeroHourEnds. The 
---
SEV: wrong | CONF: certain
WHAT: Drill Order's badge promises "Hot Dice rolls free" and it never does. Two separate reasons: (a) at the 3/3 cap the ROLL plate is pointer-events:none and handleRoll returns at the drill guard BEFORE the hot-dice branch, so a full-row keep can never be committed; (b) when hot dice does fire below the cap, the free auto-roll still increments turnRollCount, so it costs a roll rather than being free.
REPRO: (a) Drill Order seat. Roll 1: keep a 1. Roll 2: keep a 5. Roll 3: land 1,1,1,5 on the last four dice and select all four (1,200 pts, a full-row keep = Hot Dice). rc=3, ROLL has pointer-events:none, elementFromPoint at the button centre returns 'controls' so a 
CAUSE: fark_proto.html:21219 — the drill guard returns before the hot-dice branch at fark_proto.html:21350; the auto-roll then runs afterRoll which does G.turnRollCount++ at fark_proto.html:21529. The dev co
---
SEV: wrong | CONF: certain
WHAT: The status line that explains the Drill Order lock runs off BOTH edges of the screen. It is the only thing telling the player why ROLL is dead, and it is unreadable: the leading D and the trailing E are cut off.
REPRO: Any Drill Order turn, reach 3/3 and press ROLL. "DRILL ORDER — ROLL LOCKED. BANK YOUR SCORE." renders at x=-7.9 to right=437.9 in a 430px viewport (445.8px wide). .status-msg is white-space:nowrap with no overflow handling, so any message past roughly 41 chara
CAUSE: fark_proto.html:3180 — .status-msg sets font-size:5cqw and white-space:nowrap with no max-width, ellipsis or wrap.
---
SEV: wrong | CONF: certain
WHAT: When Drill Order arrives as the player's SLEEVE on a seat that is already sealed with a different rule, the cap is enforced but completely invisible: no 0/3 counter anywhere, and the ROLL button stays bright with pointer-events:auto. The player taps a button that looks live and gets only the clipped red line back.
REPRO: Set the sleeve to drill_order (famSleeveSet('drill_order') — it is a normal loadout choice) and sit at the night's sealed seat when its rule is anything else (I used STEEPED). Roll three times. _ruleActive('drill_order','p') is true and the 4th roll is refused
CAUSE: fark_proto.html:20081 — _updateDrillLock tests `G._tell.id==='drill_order'` instead of `_ruleActive('drill_order','p')`; fark_proto.html:10700 gates the 0/3 counter on the same `t.id==='drill_order'`.
---
SEV: wrong | CONF: certain
WHAT: The end-of-match overlay draws each side's score under the OTHER side's name. On a rival win I saw "YOU 9,100 vs PATRON 1,000" when the player had 1,000 and PATRON had 9,100.
REPRO: Finish any match (win or lose) and look at the score row on the result overlay. Measured on a player win, 8,500 vs 0: #resPScore rect x=282..324 sits over the "PATRON" label (x=241..320); #resOScore rect x=105..147 sits over the "YOU" label (x=110..149).
CAUSE: fark_proto.html:1501
---
SEV: wrong | CONF: unsure
WHAT: The hot-dice +250 goes straight onto the banked score, so busting on the very next roll cannot take it back. The rules card says a bust loses all turn points.
REPRO: Force six 1s, keep all six, ROLL → HOT DICE (pPts 0 → 250, turnPts 8,000). Force 2,3,4,6,2,3 on the fresh six → bust. Result: turnPts 0, kept [], pPts still 250. Two sweeps in a row leaves 500 banked the same way. Same shape for the Iron Crown bonus on the lin
CAUSE: fark_proto.html:21371
---
SEV: wrong | CONF: certain
WHAT: The six-dice throwing line is 97% of the screen width, so a die (and its score tag) is sliced off by the left or right screen edge on most throws — at EVERY viewport size, including the design 430x900.
REPRO: NEW RUN -> take the die -> pick a patron -> SIT DOWN -> ROLL. Look at the ends of the dice line. Happened on most throws at 360x800, 390x844, 430x740, 430x900 and 430x932. Measured excursions: 430x932 play left -5px AND right -5px; 390x844 opp right -10px; 360
CAUSE: fark_proto.html:1578 (#screen-match .die{width:13cqw}) + fark_proto.html:1581 (.player-dice-row{gap:3.8cqw}) — 6x13 + 5x3.8 = 97cqw, and #screen-match is the container (fark_proto.html:1383), so the r
---
SEV: wrong | CONF: certain
WHAT: On a short screen (430x740) the dialogue bubble sits exactly where the rival's status line is placed, and the opaque parchment covers it completely — you never see "PATRON HOLDS 250".
REPRO: 430x740. Play a turn, BANK, and let the rival roll while a dialogue line is up (they bark constantly during their turn). The rival's status text is in the DOM but invisible. Two clean runs: #topStrip at y160-186 and y185-210, bubble text at y171-209.
CAUSE: fark_proto.html:1359 (#screen-match .dlg-box{--dlg-y:25cqw}) pins the bubble to 25% of the WIDTH below the HUD, so on a wide-but-short phone it lands mid-table; the max-height:700px breakpoint at fark
---
SEV: wrong | CONF: certain
WHAT: When a card fires while a dialogue line is up, the dialogue parchment lands on top of the card chip and hides its name — you see only the chip's top sliver and half its gold badge.
REPRO: 430x900. Enter a match with a card that fires on turn 1 and wait for the opening dialogue line. Seen unprompted during a normal match open.
---
SEV: wrong | CONF: certain
WHAT: Three card arts 404: assets/Card_ART/one_more_round.png, grogs_bump.png, her_lucky_coin.png. The card renders as a flat blank rectangle with a diamond in the opponent's card bar.
REPRO: Start runs until a patron holds one of those cards; the blank card is visible top-left through the whole match. Reproduced in 6 of my runs.
---
SEV: wrong | CONF: unsure
WHAT: Possible score inflation on bank, twice at 430x740: the player banked +300 and the player banner then read 800 while the rival held 250. The same script banked 300 at 390x844 and 430x932 and the banner read 300. I could not tell whether a patron or card effect accounts for the extra 500, and it is outside my slice.
REPRO: 430x740, mode opp: roll 1,1,5,5,2,3, select the four scorers (+300), BANK. Player banner shows 800.
---
SEV: wrong | CONF: certain
WHAT: The "only move on the table" pulse never fires when the brand sits on a 1 or a 5. _markLoneCast decides the row is dead by scoring the raw face values, which counts the branded die's own 1 as 100, so `lone` is false and no die pulses — even though the branded face is the single legal keep and everything else scores nothing. The player is left with six ordinary-looking dice and both buttons greyed.
REPRO: One die with {t:'tithe',face:1}, five plain bone. Force the row to [1,2,3,4,6,2]. Raw scoreRoll = 100, but with the icon split out (which is what every commit path does) the row scores 0. Measured: loneCast=false on all six, rollDisabled=true, bankDisabled=tru
CAUSE: fark_proto.html:21892 — `lone=scoreRoll(free.map(d=>d.val),...).total<=0` is computed over ALL free dice; it needs the _splitIcons split the roll/bank/preview paths use. Note fark_proto.html:22902 sta
---
SEV: wrong | CONF: certain
WHAT: After a CAST the button keeps saying CAST and stays enabled, and the enchant's name stays on the table. Pressing it again does nothing. Worse, the zero-point kept entry the cast pushes leaves BANK enabled for the rest of the turn with nothing to bank — a live-looking button that silently returns.
REPRO: Cast a lone brand (Tithe). Immediately after: bankVerb still 'CAST', bank-cast class still on, btnBank not disabled, #selTotal still reads 'TITHE'. Press it again — gold unchanged (105 -> 105), nothing happens. Then ROLL: the verb resets to BANK but btnBank is
CAUSE: fark_proto.html:22971 — handleBank does `if(total<=0)return;` after committing the icon, without a setBtns()/refreshSelUI() to clear the selection UI; and the {pts:0} entry pushed at 22962 makes G.kep
---
SEV: wrong | CONF: certain
WHAT: Every branded die leaks brand textures. _dress only resets material.map for materials that ship a painted skin; for the others (silver, amber, jade, obsidian, starstone) the map is left as the previous branded texture, so _brandedMap is fed its own output, misses the cache on a new uuid, and allocates a fresh 960x640 CanvasTexture — branded on top of an already-branded face. Same for the emissive 
REPRO: Loadout bone/silver/amber/jade/obsidian/starstone, one icon each. After a single roll D3X._brandCache and D3X._glowCache already hold 32 entries each (should be 6). Every subsequent D3X._reskin() — which is exactly the callback an icon image decode fires — add
CAUSE: fark_proto.html:16755 _dress assigns m.map only inside `if(sk&&sk.map)`; fark_proto.html:16711 (_rebrand) and 16737 (_reskin) then do `o.material.map=self._brandedMap(o.material.map,...)`, feeding the
---
SEV: wrong | CONF: certain
WHAT: A Jade die's 6 stops being a 6. scoreSelection() replaces the face with the wild marker -1 and never lets it fall back to its natural value, so a Jade 6 can only ever be spent as a wild — it can no longer be counted as a plain 6. Four 6s on Jade is worth 600 (the triple only; selecting all four returns -1, i.e. not a legal keep) where four 6s on Bone is 1200. Six 6s: Jade 1000, Bone 4800 — I banke
REPRO: Loadout of six jade. Force the roll to 1,2,3,4,5,6. The straight sits on the table and cannot be taken — only the 1 and the 5 score, 150 instead of 1500. Or force 6,6,6,6,2,3: no selection of the four 6s scores; the best available keep is 600. Direct check: sc
CAUSE: fark_proto.html:15419-15422
---
SEV: wrong | CONF: certain
WHAT: When a match ends the result panel is laid over the live match screen without hiding the match HUD, so HUD text prints straight through it. The target plate ("2,800", .hud-target, z-index 6) lands on top of the VICTORY title (.res-title, z-index 1), the turn counter ("TURN 1/8") lands on "vs", and the two score pennants land on the YOU and PATRON labels. Because the left pennant is the opponent's 
REPRO: Win any match. I reached it two different ways and both show it: (a) six starstone, force all 1s, select all six, BANK — 8000 + 6x500 starstone bonus = 11,000, over the 2,800 target; (b) six obsidian with effect.chance=1, one roll, 6x1000 shatter bonus. In bot
---
SEV: wrong | CONF: certain
WHAT: Three NPC card art files 404 on every match against Grog: assets/Card_ART/grogs_bump.png, one_more_round.png and her_lucky_coin.png. All three ids are in the first rung's cardPool with cardChance 1, and none of the three files exists in assets/Card_ART (149 files there; only grogs_flask.png is present). shoot.js logged the 404s on essentially every run I made.
REPRO: Start any run and sit down at the first seat; the network log shows 404 for assets/Card_ART/grogs_bump.png?v=art1 and one_more_round.png?v=art1 (her_lucky_coin.png when that one is drawn).
CAUSE: fark_proto.html:10202
---
SEV: wrong | CONF: certain
WHAT: The end screen shows each side the OTHER side's score, drawn on top of the name. Lost the boss 1,050 vs 5,000 and the screen reads "YOU 5,000 … GROG 1,050"; won 8,500 vs 0 and it reads "YOU 0 … GROG 8,500". #end-ov lives inside #screen-match, so the match-HUD rule at fark_proto.html:1501-1506 (`#screen-match .hud-score{position:absolute;top:78%;width:20%;height:0}` + `.o{left:-2.1%}` / `.p{left:81
REPRO: Finish any match (boss or patron) and look at the score row under VICTORY / DEFEAT.
CAUSE: fark_proto.html:1501-1506 (+ markup 8697-8707)
---
SEV: wrong | CONF: certain
WHAT: Every boss fights with zero cards. _famInitOpp decides "is this a boss" with BOSS_FAM[rung.key], but BOSS_FAM is keyed by boss NAME (grog, mabel, finnick…) while rung.key holds the legacy character key (drunkard, peasant, commoner…). The lookup misses, isBoss stays false, it falls through to rung.fcards which bosses don't have, and G.oF comes back empty. Grog's side of the table is blank in every 
REPRO: Reach any boss and look at #famRowO / G.oF. In-page: _famInitOpp(TIERS[0].boss).length === 0.
CAUSE: fark_proto.html:11903 (BOSS_FAM) + 11909-11921 (_famInitOpp), consumed at 19711
---
SEV: wrong | CONF: certain
WHAT: Boss spoils: "HIS DIE" is an empty card, and taking it silently pays you gold instead. _spRelic is looked up as {grog:'grogs_tooth',…}[G.rung.key] — same name-vs-key mismatch — so window._spoils comes out as {tell, purse, tellName, tellDesc} with NO relic key. The relic card renders with a blank name and blank description, and famSpoilsPick('relic') fails its `sp.relic` guard and falls into the el
REPRO: Beat Grog, tap the first (gold-bordered) spoil, tap TAKE.
CAUSE: fark_proto.html:25800-25802 (_spRelic) and 12464-12470 (famSpoilsPick); the same map is used in _gbBossPeek at 13530 so the peek's "relic on display" row never renders either
---
SEV: wrong | CONF: certain
WHAT: The boss's house rule never shows during his own reveal. _showBossSplash deliberately exempts #tellBadge from the .has-splash blackout (7679-7680) and both comments say the tell reads under the boss — but #tellBadge is z-index 20 while .handicap-splash is z-index 10000 with an opaque black .hs-bg, so the badge is 'visible' and painted underneath. The whole bottom half of the boss splash is black.
REPRO: Challenge any boss and watch the 2.8s splash.
CAUSE: fark_proto.html:1372 (#tellBadge z-index:20) vs 7666/7673 (.handicap-splash z-index:10000 + opaque .hs-bg)
---
SEV: wrong | CONF: certain
WHAT: G.isBoss is never assigned anywhere — the field the match actually sets is G._isBoss — so two boss-only behaviours are dead code. (a) `if(G.isBoss)badge.classList.add('bossbind')` never fires, so the boss tell badge keeps the patron's gold dot instead of the red boss-bind one it has CSS for. (b) G._bossFirstEnc is only ever assigned inside `if(G.isBoss…)`, so it stays undefined and `!(G._bossFirst
REPRO: grep: G.isBoss appears only at 10704 and 23800, never on the left of an assignment. Visually: the boss tell badge's dot is gold, same as a patron's.
CAUSE: fark_proto.html:10704 and 23800 (should be G._isBoss); badge CSS at 1376, pacing read at 23760, settings copy at 8885
---
SEV: wrong | CONF: certain
WHAT: After a force-close mid-match there is no way back into the match. S.pendingMatch is written correctly and resumeMatch() restores the match perfectly when invoked — but the only UI that offers RESUME MATCH / ABANDON MATCH lives in #settingsSheet, which is opened solely by openSettings(), whose solitary caller is the .menu-btn at fark_proto.html:8206 inside #menuButtons. The home-screen builder rep
REPRO: Sit down at a patron, roll once, then force-close the app (a real page reload). Reopen: the menu offers NEW RUN / CONTINUE / book / cog. Open the cog — only the five audio-ish toggles. There is no resume or abandon anywhere. Calling openSettings() by hand imme
CAUSE: fark_proto.html:8206 (only caller of openSettings, inside the #menuButtons block wiped by the home-screen rebuild at ~13625); the replacement cog goes to _gbSettings at 13847
---
SEV: wrong | CONF: certain
WHAT: A match that is level at the 8-turn cap never ends. When both sides reach turnCap with equal scores, _handBackOrCap prints "DEAD EVEN AT THE CAP — ONE MORE ROUND" and simply starts another round, with no round limit, no tiebreak and no escalation. I played 26 player turns (turns 9-26 all labelled OVERTIME, 0-0 the whole way) and the game had no exit — I stopped it with my own loop guard, not the g
REPRO: Wrap window.rollFace and window._enchRollM to return a cycling [2,3,4,6,2,3] so neither side can ever score, then play. Both sides bust every turn, hit pTurns/oTurns 8 at 0-0, and the match loops OVERTIME indefinitely. Command: node tools/shoot.js --url "http:
CAUSE: fark_proto.html:23560
---
SEV: wrong | CONF: likely
WHAT: handleRoll() has no _endMatchFired guard, and G.phase is left at 'choosing' after the match ends. Dispatching a roll after VICTORY rolls six fresh dice into the finished match: G.pool went 0 -> 6 and #playerDiceRow .die went 0 -> 6 with the end overlay still up. handleRoll explicitly guards phase opp/rolling/yielding, _rollLocked and _palmAnimating, but not "the match is over". Honest limit: a fin
REPRO: Win a match, wait for the VICTORY overlay, then call handleRoll() from the console (or let a queued auto-roll timer fire). Command: node tools/shoot.js --url "http://localhost:8084/fark_proto.html#p=rollafterend&obust=1&timid=1&stingy=1&seed=2024" --eval-file 
CAUSE: fark_proto.html:21147
---
SEV: ugly | CONF: certain
WHAT: STEADY HAND and FAIR TRADE have no card art. assets/cards/steady_hand.webp and assets/cards/fair_trade.webp both 404 (every other FAM_CARDS id has a .webp on disk). Both are in FAM_LIVE, so both are offered in drafts and equippable — they render as an empty white box with a broken-image glyph in the table row, and as a full-size blank rectangle in the card sheet.
REPRO: Equip either card (they are draftable in normal play — famOffer draws from FAM_LIVE, fark_proto.html:12198) and look at the table row, or tap the card to open its sheet.
CAUSE: fark_proto.html:12296 — famCardArt points at assets/cards/<id>.webp; the two files are absent from the repo
---
SEV: ugly | CONF: certain
WHAT: The retired ACTIVATE drop zone is still painted on the table in every match — a 258×78 dashed rounded rectangle mid-board — with nothing that can ever be dropped into it, because G.pCards is hard-coded empty so no draggable .mcard is ever built.
REPRO: Open any match and look at the middle of the table.
CAUSE: fark_proto.html:2165 (.activate-zone .az-border rect stroke is always visible) with fark_proto.html:28070 `const pCards=[]`
---
SEV: ugly | CONF: certain
WHAT: DEFEAT screen layout collides: the patron's flavour quote is printed straight across the middle of the DEFEAT title, and each score number is printed on top of its own label (the gold number sits over "YOU", the red one over "PATRON"). Not an animation frame — still like this ~7 s after the screen opened, across burst frames 1.2 s apart.
REPRO: Lose a patron match.
---
SEV: ugly | CONF: certain
WHAT: FIRST STRIKE's reveal — the panel showing both six-seat loadouts, which the source itself calls "the reveal IS the effect" — is drawn underneath the TURN scroll and underneath the tell badge. Most of the YOU row is hidden behind the turn banner; only the row labels and a couple of chips at the right are legible.
REPRO: Corvus / a First Strike seat, dieEnch[0]={t:'snare',face:1}. Keep the branded 1 and commit. #fsReveal appears at x 134-296, y 99-146; the TURN banner occupies y 94-129 and #tellBadge y 135-184 (z-index 20 vs the reveal's 14). The reveal is sandwiched between t
CAUSE: fark_proto.html:2587 — #fsReveal is position:absolute; top:11%; z-index:14, which puts it exactly on the turn banner and under the badge. Contents are also two-letter material codes on identical swatc
---
SEV: ugly | CONF: certain
WHAT: The patron's speech scroll paints over the bottom of the tell badge — exactly the strip that holds every tell's live number (DRILL ORDER's 3/3, STEEPED's +N, FIRST STRIKE's −0g, THE RECKONING's ≥N). It happens on the very first line of the match, right after the splash closes.
REPRO: Sit at any tell seat and wait for the opening patron line. A one-line scroll occupies y 172.1-206.9 against a badge of y 135.4-183.9 — 11.8px of overlap across the badge's full width. A two-line greeting (the game has plenty, e.g. "I'll pinch yer luck if I can
CAUSE: fark_proto.html:2533 (.dlg-box z-index:90) vs the badge mounted at fark_proto.html:10714; #screen-match .dlg-box{--dlg-y:25cqw} at fark_proto.html:1359 puts the scroll's top inside the badge's box.
---
SEV: ugly | CONF: certain
WHAT: With six dice on the table the last die is drawn past the right edge of the phone. Not tell-specific, but it happened in every tell match I played.
REPRO: Any match, any tell, look at a full six-die throw. #playerDiceRow is 417px of content in a 417px box (scrollWidth 435 vs clientWidth 417) — six 55.9px dice plus five 3.8cqw gaps exactly fills it — so the per-die scatter jitter pushes the end dice out. Measured
---
SEV: ugly | CONF: certain
WHAT: At the exact frame the BUST! overlay flashes, the status strip still says "ROLLING…". The code assumes the overlay hides it; it does not — both are legible at once, one above the other.
REPRO: Roll a hand that cannot score (I forced 2,3,4,6,2,3). Sampled at the frame where #bust-ov has class 'flash': statusBot.textContent === "ROLLING...". It stays that way for the whole ~1.9s bust beat until the row clears. Rival side is identical: statusTop reads 
CAUSE: fark_proto.html:22794
---
SEV: ugly | CONF: certain
WHAT: On the DEFEAT screen the exit-quote parchment is drawn straight through the word DEFEAT.
REPRO: Lose a match. Measured rects: #resTitle {x:104,y:36,w:222,h:48}; #exitParchment {x:135,y:46,w:161,h:33} — a near-total overlap.
CAUSE: fark_proto.html:3736
---
SEV: ugly | CONF: certain
WHAT: The NPC dialogue bubble is drawn on top of the tell chip, cutting the tell's name in half.
REPRO: Start any match with a tell (PICKPOCKET here) and wait for the first patron line. The bubble's top edge overlaps the chip's lower half.
---
SEV: ugly | CONF: likely
WHAT: Thrown dice land intersecting each other — one cube's corner pushed through its neighbour, with a visible seam.
REPRO: ROLL repeatedly at any size. Seen at 430x740 (two leftmost dice merged), 360x800 (middle pair), and 430x900 in the very first shot I took.
---
SEV: ugly | CONF: certain
WHAT: The gold coin badge on a card-fired chip hangs over the chip's left edge and covers the first letter of the card's name.
REPRO: Any size, any match where a card fires. Seen on FIRST STRIKE (390x844), ZERO HOUR (390x844), THE RECKONING (430x932), PICKPOCKET (430x740), DRILL ORDER (360x800).
---
SEV: ugly | CONF: certain
WHAT: The brand is painted into the face's UV island with no regard for how that face is oriented, so the same icon lands at a different rotation depending on the face and on how the die physically landed. Ward's shield reads upright on some faces and lying on its side or upside down on others; the same Snuff candle came up upright on one roll and flat on its side on another.
REPRO: Six bone dice, Ward on faces 1,2,3,4,5,6 (one per die), force each to land on its brand. Photograph the row: face 3 and face 6 draw the shield point-down, faces 1/2/4/5 draw it rotated 90 or 180 degrees. Repeat with the same brand across two runs and the rotat
CAUSE: fark_proto.html:16575 _brandedMap draws the icon axis-aligned into the island at col=(v-1)%3,row=(v-1)/3 with no per-face rotation, and fark_proto.html:16966 _relabel spins the die by a cube symmetry 
---
SEV: ugly | CONF: certain
WHAT: The settle scatter regularly throws the end dice past the screen edge, and on a branded die that means the icon — the entire point of the enchant — is off-screen and part of its tap target is unreachable.
REPRO: Any six-die roll at 430x900. Measured DOM boxes across runs: lane 0 at left=-12 and left=-8 (die is 56px wide), lane 5 at left=384 with a right edge of 440 on a 430px viewport. elementFromPoint on the two left sample points of lane 0 returns null — those pixel
CAUSE: fark_proto.html:16497 D3X.SETTLE {x:7,y:4} scatter is applied without clamping the row to the viewport.
---
SEV: ugly | CONF: certain
WHAT: Break's targeting outlines are axis-aligned CSS boxes on the DOM hosts, so they sit visibly off the tilted, scattered 3D dice they are supposed to mark — some boxes overlap each other, some are offset up and left of their die, and the rightmost die pokes out of its own box. The selection glow (drawn by D3X on the mesh) registers correctly, which makes the mismatch obvious side by side.
REPRO: Cast Break with 5 other dice live. Screenshot the 'BREAK — TAP A DIE TO DESTROY IT' state.
CAUSE: fark_proto.html:16230 adds .break-target to d.el (the DOM host); the outline is styled at fark_proto.html:2611 as a plain CSS outline on that box.
---
SEV: ugly | CONF: certain
WHAT: Two card arts 404 and the card renders as a blank grey placeholder in the match HUD. Outside my slice but it shows in half my shots.
REPRO: Start any run; the gauntlet/tell HUD asks for assets/Card_ART/one_more_round.png?v=art1 and assets/Card_ART/grogs_bump.png?v=art1, both 404.
---
SEV: ugly | CONF: certain
WHAT: Dice regularly come to rest partly off the side of the screen. Over an 8-roll hot-dice census (48 landings on the 430px design phone) 6 landings had a die outside the viewport: starstone 2-4px past the right edge on four rolls, bone 10-12px past the left edge on two. In separate runs I measured a die box at x=-14. The die is then cut in half — its top face, its pips and (on jade) its wild ring are
REPRO: Any six-die roll; watch the outer two. Roll repeatedly and read the .die bounding boxes: about one landing in eight puts left < 0 or right > innerWidth.
---
SEV: ugly | CONF: likely
WHAT: None of the seven materials has a readable shadow on the table — they read as stickers on the wood. The layer is not missing: #dsCanvas holds ~71,000 device-pixels of shadow ink whose bounding box is [0,396,420,88], i.e. exactly the dice row, in six clusters. But the silhouette is painted at essentially die size with almost no offset, so only a ~2px fringe escapes from behind the die, and in the s
REPRO: Roll six dice and look at where they meet the table — no contact shadow. To see the layer: set window.DICE_SHADOW_COL='#ff00ff' before the roll (magenta still shows nothing composited), then set document.getElementById('dsCanvas').style.mixBlendMode='normal' —
---
SEV: ugly | CONF: certain
WHAT: Four of the seven materials do not read as their material in 3D. Only bone and amber have painted skins loaded (D3X._sk === ['bone','amber']); the other five fall back to the stock cream texture with a colour multiply, and the results measured off the frame are: silver (196,174,146) — the same warm cream as bone (208,186,141), so in a mixed hand silver and bone are one material; starstone (136,140
REPRO: One match with bone, amber, silver, jade, obsidian, starstone side by side; sample the centre of each die's top face.
---
SEV: ugly | CONF: likely
WHAT: Starstone's ink outline renders as a bright cyan ring, the only one of the seven that reads as a highlight rather than as ink. The hull material colour is genuinely near-black (measured 0x001325 from the mesh), but it composites far brighter — dark sRGB values on this hull come out lifted. Silver gets the same treatment more mildly (hull 0x0b0f13 renders slate blue). Bone, amber, jade, obsidian an
REPRO: Put starstone in any hand and look at the die at rest. Hiding the hull (d.obj.userData.out.visible=false) removes the ring, so it is the outline and not a selection glow or a DOM border.
CAUSE: fark_proto.html:17551
---
SEV: ugly | CONF: certain
WHAT: The boss splash shows a different character than the room. The room paints the current Grog (painted ferret in a green vest, Art/Assets/Backgrounds/MAIN/GROG/Grog_env_Foreground_ready.png); one tap later the splash loads GAUNTLET_PORTRAITS['drunkard'] = assets/Characters_ART/Drunkard.png, the legacy pixel-art hunched otter in a purple cloak with a goblet. Different character, different art style, 
REPRO: Win the crowd, tap READY, tap CHALLENGE — compare the room you just left with the splash.
CAUSE: fark_proto.html:10469 (portrait=GAUNTLET_PORTRAITS[bossKey]) + 28433-28443
---
SEV: ugly | CONF: likely
WHAT: The boss has no face at his own table. _matchDress blanks the rival portrait token for bosses — tok.style.backgroundImage is set to 'none' and the colour to #3f3a34 whenever isBoss — so Grog's HUD circle is an empty dark disc, while a random no-name patron gets a painted portrait in the same slot.
REPRO: Compare the top-left HUD circle in a boss match with the same circle in a patron match.
CAUSE: fark_proto.html:15116 and 15125 (_matchDress)
---
SEV: ugly | CONF: certain
WHAT: The boss spoils row overflows the phone on both sides. #resCard measures 13,406 404x304 but the block it contains is -58,406 547x304: the three option cards land at x=-52, 129 and 310, each 173 wide. Option 1 hangs 52px off the left — its "RELIC / HIS DIE" heading is off-screen, which is why it reads as a blank gold box — and option 3 runs 53px past the right edge. The heading loses its first word
REPRO: Beat any boss at 430x900 and look at the spoils row.
CAUSE: fark_proto.html:25806-25822 — 3 grid columns of aspect-ratio:2/3 inside the flex .res-card, so min-content width (535px) beats the 404px container
---
SEV: ugly | CONF: certain
WHAT: Three NPC card arts 404 on every match load — assets/Card_ART/one_more_round.png, grogs_bump.png and her_lucky_coin.png. That is Grog's entire patron card pool (cardPool:['her_lucky_coin','one_more_round','grogs_bump'] at fark_proto.html:10202); only grogs_flask.png exists in assets/Card_ART/. Chromium broken-image placeholder glyphs were visible sitting on the felt in three of my match screenshot
REPRO: Load fark_proto.html and enter any match — the shooter's 404 list carries one_more_round.png and one of grogs_bump.png / her_lucky_coin.png on essentially every run.
CAUSE: fark_proto.html:10202 (Grog's cardPool) — the three PNGs are absent from assets/Card_ART/
---
SEV: ugly | CONF: certain
WHAT: The rival's speech balloon paints on top of the tell badge and cuts it in half. The badge is position:fixed at a hard-coded y (top:calc(var(--hud-h) + var(--tell-badge-y)), z-index 10050) while the balloon sits in the dice-area flow just below the HUD, so as soon as the rival says anything the badge's lower lines disappear behind it. Reproduced on two different tells in two independent runs: DRILL
REPRO: Sit at any seat whose patron carries a tell and play until the rival speaks (their first bust or bank). The balloon appears directly over the badge. Seen at turn 5 (DRILL ORDER) and turn 14 (THE RECKONING).
CAUSE: fark_proto.html:7869
---
SEV: ugly | CONF: certain
WHAT: On the FEATS OF THE NIGHT overlay the gauntlet screen underneath shows through the scrim: the line "You need 1 more win" reads clearly through and collides with the top edge of the PIN THEM button, so the button's parchment has legible foreign text bleeding across it.
REPRO: Win any match, take or decline the card draft, press CONTINUE. The feats overlay comes up over the gauntlet screen with the underlying line showing through. Seen on every win I walked through (4 separate runs, 3 different seeds).
---
SEV: ugly | CONF: certain
WHAT: Three of Grog's NPC cards have no art file, so the game 404s on them 2-3 times in every single match. cardPool for rung 0 (GROG) lists her_lucky_coin, one_more_round and grogs_bump, and all three are defined as real npcOnly cards, but assets/Card_ART/ (149 files) contains none of them. I confirmed with a direct HTTP probe: all three return 404 while a control asset returns 200.
REPRO: Load http://localhost:8084/fark_proto.html and start any run — the requests fire on the gauntlet screen and again per match. Direct check: GET /assets/Card_ART/grogs_bump.png -> 404, /assets/Card_ART/her_lucky_coin.png -> 404, /assets/Card_ART/one_more_round.p
CAUSE: fark_proto.html:10202
---
SEV: nitpick | CONF: unsure
WHAT: famCardArt writes '<\span>' where '</span>' was meant, so a badged card emits an extra opening <span> and never closes the badge. Only fires on draft offers that carry the UPGRADE badge.
REPRO: Reach a card draft that offers an upgrade of a card you already own.
CAUSE: fark_proto.html:12298
---
SEV: nitpick | CONF: certain
WHAT: The FIRST STRIKE badge carries a gold-drain counter that can never move. It permanently reads "−0g" next to the tell name.
REPRO: Sit at a First Strike seat. The badge renders "📒 FIRST STRIKE −0g". Roll as many times as you like — S.run.gold never changes and the counter never leaves −0g, because the per-roll gold cost it reports was dead-coded when In Arrears was replaced by First Strik
CAUSE: fark_proto.html:10696 still emits `<span id="arrearsVal">−0g</span>` for t.id==='in_arrears', but the drain that used to feed it at fark_proto.html:21546 is now behind `if(false&&S&&S.run)`.
---
SEV: nitpick | CONF: certain
WHAT: STILL WATERS is the only tell absent from the sealed-seat pool, so it can never appear on a sealed seat — it only ever reaches a player on Aldric's boss table.
REPRO: Read _SEAL_POOL: ['last_call','steeped','pickpocket','in_arrears','drill_order','counterfeit','reckoning'] — seven of the eight tells. _rollSealTell can never return 'confession'. I forced it into the seal to test it (that seat state is harness-made, not somet
CAUSE: fark_proto.html:10572 — _SEAL_POOL omits 'confession'.
---
SEV: nitpick | CONF: certain
WHAT: The rival's hot dice is completely silent — no banner, no status line, no sound cue. Their six dice are swept and replaced with a fresh six and nothing on screen says why.
REPRO: Force the rival's first roll to six 1s. Status goes "PATRON HOLDS 8,000" → "PATRON IS ROLLING…" and a fresh six lands. #hot-ov never gets .flash for the rival. The player's hot dice gets a full-screen 🔥 HOT DICE overlay plus a status line.
CAUSE: fark_proto.html:22016
---
SEV: nitpick | CONF: certain
WHAT: All three of Grog's NPC cards 404 their art on every match where his pool is drawn.
REPRO: Any match; shoot.js reports the failed requests. assets/Card_ART/her_lucky_coin.png, grogs_bump.png and one_more_round.png return 404 (confirmed with curl and by listing the directory — the files are not there).
CAUSE: fark_proto.html:10202
---
SEV: nitpick | CONF: likely
WHAT: A free card's cost is rendered as "-0g" on the fired-card chip.
REPRO: 390x844, card chip for FIRST STRIKE.
---
SEV: nitpick | CONF: certain
WHAT: Adjacent dice boxes overlap after the scatter, so a tap near the edge of one die selects its neighbour.
REPRO: bone6 roll: lane 2 box [166,412,57,57] (right edge 223) against lane 3 box [216,420,57,57] (left edge 216) — a 7px overlap. document.elementFromPoint at lane 2's bottom-right corner returns lane 3's element ('die d3on dtype-bone die-branded lone-cast').
CAUSE: fark_proto.html:16497 — the neighbour shove keeps the meshes apart but the DOM hit boxes still overlap.
---
SEV: nitpick | CONF: unsure
WHAT: On the first branded roll of a session the icons are not on the dice at the moment the row becomes tappable — the icon Images have not even been requested yet, so the dice show plain pips for a beat and then the brands pop in.
REPRO: First roll after entering a match with icons equipped. At the moment G.phase flipped to 'choosing' and the dice had onclick handlers, D3X._iconImgs was {} and D3X._brandCache was {} — nothing branded had been built. ~1.6s later four of six brands had appeared.
CAUSE: fark_proto.html:16510 _iconImg returns null on first call and relies on img.onload -> _reskin to put the brand on.
---
SEV: nitpick | CONF: unsure
WHAT: I never managed to photograph an obsidian die actually breaking. The shatter fires synchronously inside handleRoll — before/while the dice are in the air — and the host chip is removed 420ms later, so the 300ms D3X burst plays during the throw. In three attempts the obsidian dice were already gone and the bonus already banked by my first readable frame after the roll.
REPRO: getDie('obsidian').effect.chance = 1 with obsidian in the loadout, then roll. The dice vanish; +1000 each lands on the score.
CAUSE: fark_proto.html:21572
---
SEV: nitpick | CONF: certain
WHAT: Grog's three signature NPC cards 404 their art every time the boss is on screen: assets/Card_ART/her_lucky_coin.png, one_more_round.png and grogs_bump.png are all absent from disk (149 other card PNGs are there). The <img> carries onerror="this.remove()" so nothing visually breaks — the flat colour swatch shows instead — but it is three failed requests on the boss path. Related: generateOppCards r
REPRO: Open the night-1 room or any Grog screen and watch the network log.
CAUSE: fark_proto.html:10202 (Grog cardPool) + 19287 (_cardArtImg); files missing from assets/Card_ART/
---
SEV: nitpick | CONF: certain
WHAT: Nights 2-8 show Grog's portrait under the next boss's name. The room builds its art path from the boss name (Art/Assets/Backgrounds/MAIN/<NAME>/) and only GROG exists, so every later night falls back to assets/_mockups/new_main/bg3.png + fg3.png — and fg3.png is the Grog painting. After beating Grog the night-2 room reads MABEL over a picture of Grog.
REPRO: Beat Grog, continue to the night-2 room.
CAUSE: fark_proto.html:14024-14026 + the onerror fallback at 14070/14076; only Art/Assets/Backgrounds/MAIN/GROG exists
---
SEV: nitpick | CONF: certain
WHAT: handleRoll's commit marks dice committed but never clears their sel flag, so a committed die stays selected in the model while its .selected class is stripped. handleBank's equivalent commit (fark_proto.html:22941) does set d.sel=false, so the two commit paths disagree. Nothing miscounts today only because every consumer happens to pre-filter !d.committed — _markLoneCast (21890) and activateFinnic
REPRO: Roll, select any scoring die, tap ROLL to commit it, then read the pool: the die has committed===true AND sel===true while el.classList no longer contains 'selected'. My 90s endurance mash flagged it as 'a committed die is selected' during normal play.
CAUSE: fark_proto.html:21326 — selDice.forEach(d=>{d.committed=true;d._frozen=false;d.el.classList.remove('selected','die-frozen');...}) with no d.sel=false
---
SEV: nitpick | CONF: likely
WHAT: Dice become selectable and the score preview goes live ~40ms before the 3D dice stop tumbling, so a fast player can commit a die whose face is still spinning and unreadable. handleRoll settles the model on a 480ms timer (_rollDur=480, fark_proto.html:21498/21503 -> afterRoll sets phase='choosing') while the 3D throw is kicked off with D3.roll(..., {dur:520}) at fark_proto.html:21438. Values are al
REPRO: Roll, then poll: G.phase reads 'choosing' and dice taps register while D3X.dice.some(d => d.roll) is still true.
CAUSE: fark_proto.html:21498 (_rollDur=480) vs fark_proto.html:21438 (D3.roll dur:520)
