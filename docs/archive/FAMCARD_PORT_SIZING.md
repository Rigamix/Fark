{
  "summary": "Size the port of the rival family-card subsystem into the sim model",
  "agentCount": 9,
  "logs": [],
  "result": {
    "sizing": "# SIZING â porting the rival family-card subsystem into `F.oppTurn`

Target files: `C:/Users/Rigam/OneDrive/Documents/Work/Gambit/.claude/worktrees/zen-chatterjee-f04c42/tools/sim_harness.js` (harness, 1331 lines; `F.oppTurn` = 578â748) and `C:/Users/Rigam/OneDrive/Documents/Work/Gambit/.claude/worktrees/zen-chatterjee-f04c42/fark_proto.html` (game, 37016 lines).

---

## VERDICT UP FRONT

**No option in this sizing can pass the stated three-part test, and that is a measured result, not a hedge.** The test requires the gap to close at CORVUS, BRUTUS *and* WHISPER. Family cards can move rival bust rate at CORVUS only. At BRUTUS the entire silver pool (`steady_hand`, `retort`, `reprisal`, `fair_trade`) has **zero `_npcFamCard` call sites** â pool-wide, at every seed, so this is not a draw-luck statement. At WHISPER the only wired vagabond card is `sleight`, which rerolls the **player's** next roll (armed 27729, consumed 25082) and never touches rival dice.

The strongest single piece of evidence is internal: `BOSS_FAM` gives `finnick:'vagabond'` and `whisper:'vagabond'` â **the same four-card pool**. FINNICK matches the real rival (0.389 vs 0.390); WHISPER diverges 2.6Ã. Same pool, opposite outcomes.

If Denis funds this, he should fund it as a **fidelity fix with a CORVUS-shaped payoff**, priced accordingly â not as the fix for the bust divergence.

### Two premises in the brief do not survive

1. **"`oF` appears ZERO times in the harness: the model's rival never has family cards at all."** The grep is correct; the conclusion is false. `tools/sim_harness.js:319` calls the real `newG`, and `newG` (fark_proto.html:23049) does `pF:_famInit(),oF:_famInitOpp(rung)`. Two agents measured populated `G.oF` in harness boss matches independently. **The state is already there. The gap is 100% consumer-side.** This changes what the port *is*: not "deal the cards", only "read them".
2. **"`famFire` is never called in the harness."** One executable call: `tools/sim_harness.js:373`, `famFire('roll',{actor:'p',rolls:G.turnRollCount||0})`, inside `afterRollLite`. Lines 18/28/53/66 are header prose. The bus is already partly wired on the player side.

### Where I took the verifier over the map

- `famFire(â¦,{actor:'o'})` is **not** inert. Three CFX hooks gate on `ev.owner==='p'` alone (12879 `slow_cook.turnStart`, 12880 `slow_cook.bust`, 14144 `short_fuse.turnStart`), so they fire on rival-actor events for **player-owned** cards. Measured live: `{acc:999,lit:true}` â `{acc:0,lit:false}`. The source says so itself at 12871â12878.
- `preserve` is **not** points-only. Its consumption at 27769â27772 adds to `oppBank` *before roll 1*, and `oppShouldBank` (27572) opens `if((oppTotal+oppBank)>=target)return true;`. It moves the bank decision, therefore bust rate.
- The per-boss `G.oF` roster tables in two maps are **single random draws presented as content** â `_famInitOpp` draws with a bare `Math.random()` (12712). Only AMBROSE is deterministic (amber has 3 eligible cards, draws 3). All reasoning below is pool-wide.

---

## 1. WHAT THE PORT MUST DO â minimum behaviour set, ranked by plausible movement

Ranked by how much each can move **rival bust rate or points per turn**. Only nine `_npcFamCard` statements exist (27729, 27734, 27992, 28158, 28776, 28780, 28784, 28789, 28793) and three of them are dead in the real game.

| # | Behaviour | Source | Which bosses | Moves rival bust? | Moves rival points? |
|---|---|---|---|---|---|
| 1 | **encore / stargazer dead-roll rescue** â reroll free dice, rescore, re-choose | 28157â28175 | CORVUS only | **YES â the only family effect that can avert a rival bust** | yes |
| 2 | **honeytrap** â pull one non-modal fresh die to the modal face, pre-scoring | 27991â28002 | MABEL, AMBROSE | yes, **either direction** | yes |
| 3 | **preserve** â `G._oPreserve=100` â next turn opens with bank 100 | write 28777, read 27769â27772 | MABEL, AMBROSE | yes, indirectly (crosses `oppShouldBank` thresholds a roll earlier) | yes |
| 4 | **double_or_nothing** â Ã2 or Ã(1âp), gated `(G.pPtsâG.oPts)>=1000` | 28784â28788 | GROG only | no (fires inside `finOpp`, after the bank decision) | yes |
| 5 | **`famCommitBonus(_oSel,total,'o')`** â currently 0 calls in the harness | 28503 â 14083â14122 | all | no | **numerically inert**: the relic tail (14114â14120) needs `finnicks_palm`/`whispers_fang` in `matchOppDice`, and I checked all eight `RUNGS` dice arrays (10809/10830/10848/10858/10872/10878/10895/10913) â none carries one. Fidelity only. |
| 6 | **sleight** â rerolls the **player's** next roll | 27729â27730 â 25082 | FINNICK, WHISPER | no | changes the *player's* numbers |
| 7 | **ill_omen** â points transfer pPtsâoPts on the player's turn | 27734â27735 â 27469â27493 | CORVUS only | no | transfer only |
| 8 | **The 8 `actor:'o'` `famFire` seams** (27466, 27883, 27912, 28283, 28357, 29166, 29167, commit via 28503) | â | all | **zero** for rival-owned cards (all 18 CFX hooks reject `owner==='o'`) | **non-zero for the player** â see Risk R3 |
| 9 | `slow_cook` / `pickpocket` / `retort` | 28780, 28789, 28793 | â | **never fire in the real game either.** Passives carry no `charges` array in `FAM_CARDS`; `_famInitOpp:12720` deals them `charges:0`; `_npcFamCard:27717` filters `o.charges>0`. A faithful port transcribes three branches that never execute. | |

**Minimum set for the stated goal: item 1 alone.** Items 2â4 target tiers with no established gap (GROG/MABEL/AMBROSE are marked UNESTABLISHED in `docs/FINDINGS.md`). Items 5â8 are fidelity. Item 9 must be ported *inert* â note that 28780/28789/28793 **do not decrement `charges`**, so anyone who "fixes" them by granting a charge gets an unbounded per-turn effect.

---

## 2. THREE OPTIONS

Effort is stated as sessions plus concrete counts. **Calibration warning:** `docs/P5_NPC_CARDS.md` records two wrong size estimates on this exact area, both corrected by starting to write the code. Treat the bands as Â±1 session.

### (a) MINIMAL â encore/stargazer rescue only

**Work.** One structural change plus ~20 transcribed lines. Harness line 630 is the whole dead-roll branch:
```js
if(!total||total<=0){out.busted=true;out.rolls=rolls;bank=0;break;}
```
It becomes a cascade with a `continue`-shaped re-entry. `G.oppDice` does **not** need materialising: `encore` rerolls the free dice, rescores with `_scoreRollBest`, and re-chooses with `_oppChooseFrom` â all three already exist in the harness loop against the local `live` array. Only `_npcFamCard('encore')` needs `G.oF`, which is already populated. The fiddly part is the fog index bookkeeping (`fV`/`fM`/`fogIdx`, harness 606â613) surviving a mid-roll reroll.

**Band: 0.5â1 session.**

**Fixes.** CORVUS, partially. **Breaks.** Nothing on the rival side elsewhere â `_npcFamCard('encore')` returns `null` at every non-starstone boss, so the delta at BRUTUS/WHISPER/FINNICK is an *exact* zero, which doubles as a self-check.

**Stays wrong.** BRUTUS, WHISPER, and every item 2â9 above.

**Verification.** Model-side only, four tiers, ~1500 turns each in quiet mode (minutes â the real-side targets already exist and do not need re-running). Plus a fire counter: how many rescues were spent, and how many converted a bust into a scoring roll. Without the counter, "no change" and "never fired" are indistinguishable â `FSIM.quiet` stubs `setStatusMsg`/`famLog`/`triggerCard` (sim_harness.js:164), so every ported block is silent by construction.

### (b) MODERATE â run all seven live `_npcFamCard` sites + `famCommitBonus`

Note the name in the brief is misleading: **there is no "grant `G.oF`" step**; it already exists.

**Work.** Five insertion points, ~90 transcribed lines, two structural changes:
1. A **prologue** before harness 581 for `_npcArmActives()` (27719â27739) and the `G._oPreserve` carry-in (27769â27773).
2. **`finOpp` extraction** â the harness's epilogue (736â742) runs only on the not-busted path and has no `pts` variable a card can rewrite. `preserve` and `double_or_nothing` live inside `finOpp` (28745).
3. `honeytrap` after the throw (harness 602), against `live`.
4. `famCommitBonus` **after the chooser (648), before the release block (668)** â the real order is commit 28503 â release 28510 â accumulate 28696, and the harness's P508 release port runs *before* accumulation, so the obvious insertion point inverts the real ordering.
5. `G.oppDice` materialisation, required **only** by `famCommitBonus` (14088 `_cFam`, 14116â14117 `_cRow.indexOf`). This is the expensive item â see R2. It can be deferred, at the cost of item 5 in Â§1, which is numerically inert anyway.

**Band: 2â3 sessions** with `G.oppDice`; **1.5â2** without it.

**Fixes.** CORVUS same as (a). MABEL/AMBROSE get honeytrap + preserve; GROG gets double_or_nothing â all three tiers currently have no established gap to close, so these produce numbers with no target.

**Breaks / risks realised.** `sleight` and `ill_omen` reach across the seat boundary into the player's turn (25082, 27469). The harness drives the player through the real `startPTurn`/`rollPool`/`afterRollLite`, so 25082 is plausibly live â **unverified**, and if it is live this option changes the *player's* rolls at FINNICK, the control tier.

**Stays wrong.** BRUTUS: **exactly zero change**, bust and points. WHISPER: rival bust exactly zero change.

**Verification.** As (a), plus per-card fire counts per tier, plus a player-side arm (points/turn, bust rate) at FINNICK and WHISPER to detect `sleight` leakage.

### (c) FULL â route the model's turn through the real family-card event bus

**Work.** (b) plus: raise all eight `actor:'o'` seams; materialise `G.oppDice` as real row objects `{val,el,kept,mat,lane}`; replace the delete-on-keep representation (harness 718â724) with `d.kept=true`; supply `el` stubs or skip `_oppHoldKept`; initialise and write the turn-scoped trackers `G._oTurnDiceCommitted`, `G._oFirstRollKept`, `G._oTripleHunterFiredThisTurn`, `G._oTurnTriples`, `G._oTurnComboTypes`, `G._oTurnRollScored`, `G._oLastHotDice` (27779â27788, 28702â28725); set `G.phase='opp'`.

**Band: 4â6 sessions.**

**Fixes, on the rival side: nothing that (b) does not.** All 18 CFX hooks reject `owner==='o'` â 15 via `_fxMine` (12800), 3 via `ev.owner==='p'`. Enumerated three times independently, count agreed at 18 each time (one map said 20 by including three `RSX` entries at 13240/13243/13249, which `_rsFire` dispatches and which never touch `G.oF`).

**What it uniquely adds is a player-side change**, and it is the only option that can make the player's numbers wrong (R3).

**Verification.** As (b), plus a player-side before/after on `G.pF` state, because this is the only option that touches it.

---

## 3. THE VERIFICATION THAT DECIDES SUCCESS â and what each option predicts

Pre-register before any code is written. Targets from `docs/FINDINGS.md`; real side is already measured and is not re-run.

| tier | real rate (95% CI) | model now | (a) predicts | (b) predicts | (c) predicts |
|---|---|---|---|---|---|
| **4 CORVUS** | 0.037 (296t) [0.021, 0.065] | 0.140 | 0.07â0.11, **direction uncertain** | same as (a) | same as (b) |
| **5 BRUTUS** | 0.160 (300t) [0.123, 0.206] | 0.300 | **0.300, exactly unchanged** | 0.300 | 0.300 |
| **7 WHISPER** | 0.085 (188t) [0.053, 0.134] | 0.220 | **0.220, exactly unchanged** | 0.220 | 0.220 |
| **3 FINNICK (control)** | 0.389 (58/149) | 0.390 | 0.390 | 0.390, *player side may move* | 0.390, *player side may move* |

**All three options fail parts 2 and 3.** And part 4 passes *trivially* â a control the treatment cannot reach by construction is not a control. That distinction matters here: "FINNICK stayed matched" would be reported as a pass and would carry zero information.

**The CORVUS number, with its arithmetic exposed.** Starstone pool = `{encore, stargazer, ill_omen, falling_star}`, night 4 draws 2, tier 2. P(â¥1 rescue card) = 1 â C(2,2)/C(4,2) = **5/6**. Expected rescue charges per match = (4 + 2Â·4 + 0)/6 = **2.0**. The deep-sample instrument runs 12 turns per match, so at the model's 0.140 there are ~1.68 busts per match to spend them on. Charges are therefore *not* the binding constraint; conversion rate is, and conversion depends on how many free dice remain at the dead roll â **which nobody has measured on either side**. Hence the wide band and the explicit direction warning.

**Why the direction is genuinely uncertain:** a successful rescue continues the turn, adding roll opportunities and therefore later bust opportunities. That is the exact shape that made the P508 release-singles port move CORVUS bust **up** (0.140 â 0.163) against a pre-registered prediction of ~70% closure. Same trap, same tier, same subsystem.

---

## 4. RISKS SPECIFIC TO THIS CODEBASE

**R1 â RNG consumption shift (the most likely way to get a silently wrong number).** `F.installRng` (sim_harness.js:110â117) replaces the global `Math.random` with mulberry32; every roll, every patron draw and every NPC coin flip reads that one stream. `honeytrap` consumes a draw (27993), `double_or_nothing` consumes one (28786), `_famInitOpp` already consumes n at setup. **Adding any consumer re-phases every downstream roll**, so a same-seed before/after diff is no longer attributable to the effect. A private stream exists (`F.aux`, line 120) but using it diverges from the real game, where those flips come from the same stream. Either choice is a deliberate trade; making it accidentally is how this port produces a confident wrong number.

**R2 â Dice shape.** Harness seat = `{mat,lane,val}`; real row element = `{val,el,kept,mat,lane}`. "Kept" is encoded by **removing** the seat from `live` (718â724) â destroyed, not flagged. Three silent-failure modes, all no-error: `_oppHoldKept:25588` is `if(!d.el)return;` and then 25603 does `G.oppDice=[]` unconditionally, so an el-less kept die is erased from **both** arrays; `reDrawDieFace:30815` guards `if(!d.el)return;` so honeytrap/encore mutate `d.val` but draw nothing (harmless, but it means the visual channel cannot confirm a fire); `famCommitBonus`'s `finnicks_palm` block uses `_cRow.indexOf` with `_cRow=G.oppDice` â with `G.oppDice===[]`, `first`/`last` are `undefined` and both flags come back falsy, a no-op that reads as a correct answer.

**R3 â Shared gate reaches the player.** Measured live: `famFire('turnStart',{actor:'o'})` sets player-owned `slow_cook.state.acc=0` and `short_fuse.state.lit=false`; `famFire('bust',{actor:'o'})` zeroes `acc`. The harness's own gear presets deal the player exactly those cards â `tools/sim_harness.js:219` (`slow_cook` t1) and `:222` (`slow_cook` t3, `falling_star` t3, `pickpocket` t3). So option (c)'s seams change **player** points in the night-8 preset. It is a genuine fidelity fix (the real game *does* reset there) landing as a confound on the same run. Separate the arms or the result is uninterpretable â `OPEN.md` Â§6 already records two difficulty changes landing on one axis without separation.

**R4 â Cross-seat effects from a "rival-side" port.** `_npcArmActives` writes `G._oSleight` and `G._oIllOmen`; the consumers are on the **player's** path (25082, 27469). Whether 25082 is reachable in the harness is **unverified**. If it is, option (b) alters the control tier's player numbers while leaving its rival bust rate untouched â a change that looks like noise and isn't.

**R5 â Double application.** `docs/P5_NPC_CARDS.md` records it: `slow_cook`, `retort`, `double_or_nothing` and `pickpocket` have both a `_npcFamCard` branch and a CFX hook. A port that copies the hand-wired path is safe; a port that also ungates the bus fires `double_or_nothing` twice. This trap has already disqualified two attempts in this area.

**R6 â Ordering.** Real: `famCommitBonus` 28503 â release-singles 28510 â position adders 28630 â `oppBank+=total` 28696. Harness: release 668â714 â accumulate 715. Inserting the commit at 715 inverts it. Wrong order yields plausible numbers.

**R7 â Direction, not magnitude.** See Â§3. Register the direction, not just the size.

**R8 â Instrument blindness.** `FSIM.quiet` stubs `setStatusMsg`, `famLog`, `triggerCard` (sim_harness.js:164). Every ported family block is silent. Count fires at the branch; a zero delta with no fire count is not a result.

**R9 â Not a risk, worth knowing.** `_famInitOpp` re-rolls `G.oF` from scratch on every `newG`, and boss `oF` is not persisted by `saveMatchState` (10235â10318 â the map's 355xx line numbers are wrong by ~25,000, though its substantive claim holds). Any sim path that re-enters `setupMatch` mid-measurement re-draws the hand.

---

## 5. WHAT IS STILL UNKNOWN â and the one measurement

### The card-count correlation is a CORRELATION, not a measured mechanism. Say so out loud.

`n = 1 + (night>=4) + (night>=7)` is a **deterministic function of the night index**. The divergent tiers are nights 4, 5, 7 (n = 2, 2, 3); the matched control is night 3 (n = 1). Across the entire data set, "2â3 cards" and "night â¥ 4" are the *same variable*. Four data points, three on one side, and card count carries no information the tier index doesn't already carry.

It is confounded with everything else that steps at night 4: NPC `cardCount` (FINNICK 3 â CORVUS 3 â BRUTUS 3 â WHISPER 4, and `generateOppCards:32264` raises n further to match the player's hand), rung dice quality (10848 â 10858), per-tier `patronStats`, and the dealt family-card **tier** (`min(3,1+floor(night/3))`, stepping at nights 3 and 6).

**What upgrades it:** a manipulation that holds the night fixed and varies the card count â e.g. force `G.oF=[]` for the real rival at BRUTUS and re-measure with the existing deep-sample instrument. Static analysis predicts an exact zero. Confirming a predicted zero is weak evidence, which is why it is not my recommended measurement.

### Other open items

- **Whether `G._oSleight` reaches the harness's player turn** (25082). One probe, minutes.
- **Whether the model's 0.140 / 0.300 / 0.220 were taken with the same gear and `fcards`** as any post-port re-run. If not, R3 contaminates the comparison before the port is even written.
- **Dead-roll free-dice distribution** on both sides â needed to turn the CORVUS band into a real prediction.

### THE ONE MEASUREMENT

**At BRUTUS, in the real game, over ~300 rival turns, bucket every zero-scoring rival roll by the branch that absorbs it.** One counter wrapped at each branch in 28157â28345, not inferred from outcomes: encore/stargazer (28158); the eight `npcHasActive` rescues (`old_bones`, `ambrose_grace`, `wild_die`, `brutus_fist`, `finnicks_palm`, `grogs_flask`, `coin_flip`, `the_nudge`); `brutus_grit`; `bust_immune_turns`; `bust_survive`; `bust_bank_half` / `mabels_stitch`; `second_wind`; Aegis; and `_oppBustOut`.

Why this one:

- It measures **exactly what fraction of the BRUTUS gap family cards could ever address** â predicted 0, and a histogram is the difference between predicting zero and knowing it.
- It **ranks every competing mechanism by measured size** in the same run, instead of by code reading. The family-card branch is **one of roughly fifteen** in that cascade; the other fourteen are NPC-card saves the harness also lacks (`npcCardState`, `bust_immune`, `bust_survive`, `bust_bank_half`, `npcHasActive`, `npcUseActive` all appear **0 times** in `sim_harness.js`, while `oCards` appears 5 times and *is* populated via the real `generateOppCards`).
- There is a named candidate with a **matching disqualifier**: `hold_the_line` (12072â12075, `bust_immune_turns` turns:2, owner brutus) is BRUTUS's `cardPool[0]` and the signature guarantee at 32270 means it is dealt in **100%** of BRUTUS matches; `sundays_rest` (12129â12132, turns:3) is WHISPER's; FINNICK's pool (10853) contains no bust save, and FINNICK is the tier that matches. **Arithmetic, on the stated assumption that the deep probe's 12-turn matches make turns 1â2 unbustable:** measured BRUTUS rate = true rate Ã 10/12, so the model's 0.300 would read as 0.250 against the observed 0.160 â immunity accounts for roughly 36% of the BRUTUS gap on its own. Family cards account for 0%. **This is arithmetic under an assumption, not a measurement, and it is precisely what the histogram would settle.**
- It is **cheap and the rig already exists**: `tools/probe_bustrate_deep.js` completes 300 turns at BRUTUS without hanging (only WHISPER at 300 hung, and chunking works).
- The structural work it would justify â a dead-roll cascade with a re-entry path and a `finOpp` funnel â is **the same restructure option (a) needs**. Whichever branch wins, that scaffolding is shared, which is the strongest argument for funding *some* version of this.

**Decision rule for Denis:** run the histogram first. If family cards absorb ~0 dead rolls at BRUTUS, no option here passes the three-part test, option (a) is worth ~0.5â1 session as a CORVUS-only fidelity fix, and the budget belongs to whichever branch the histogram shows doing the absorbing.",
    "areas": [
      "state",
      "effects",
      "inventory",
      "modelgap"
    ]
  },
  "workflowProgress": [
    {
      "type": "workflow_phase",
      "index": 1,
      "title": "Map"
    },
    {
      "type": "workflow_phase",
      "index": 2,
      "title": "Verify"
    },
    {
      "type": "workflow_phase",
      "index": 3,
      "title": "Size"
    },
    {
      "type": "workflow_agent",
      "index": 1,
      "label": "map:state",
      "phaseIndex": 1,
      "phaseTitle": "Map",
      "agentId": "af5cce7ed44f53adf",
      "model": "claude-opus-5",
      "state": "done",
      "startedAt": 1786183428492,
      "queuedAt": 1786183423488,
      "attempt": 1,
      "lastToolName": "Bash",
      "lastToolSummary": "cd "C:/Users/Rigam/OneDrive/Documents/Work/Gambit/.claude/wâ¦",
      "promptPreview": "CONTEXT. Fark is a dice roguelite. C:/Users/Rigam/OneDrive/Documents/Work/Gambit/.claude/worktrees/zen-chatterjee-f04c42/fark_proto.html is the real game (~36k lines, single file).
C:/Users/Rigam/OneDrive/Documents/Work/Gambit/.claude/worktrees/zen-chatterjee-f04c42/tools/sim_harness.js is a simulation harness. The harness drives the REAL game for the player
(F.simTurn calls startPTurn/rollPool/afâ¦",
      "lastProgressAt": 1786183962346,
      "tokens": 130007,
      "toolCalls": 51,
      "durationMs": 533854,
      "resultPreview": "## G.oF â measured lifecycle map (`fark_proto.html`)

All line numbers are from `C:/Users/Rigam/OneDrive/Documents/Work/Gambit/.claude/worktrees/zen-chatterjee-f04c42/fark_proto.html`.
Where I state a distribution or a pool size I got it by extracting `FAM_CARDS` / `FAM_LIVE` / `BOSS_FAM` / `famDef` / `_bossKey` / `_famInitOpp` (lines 12562â12723 + 14400â14402) verbatim into node and running them â¦"
    },
    {
      "type": "workflow_agent",
      "index": 2,
      "label": "map:effects",
      "phaseIndex": 1,
      "phaseTitle": "Map",
      "agentId": "a6a3e24d8477922fc",
      "model": "claude-opus-5",
      "state": "done",
      "startedAt": 1786183428402,
      "queuedAt": 1786183423488,
      "attempt": 1,
      "lastToolName": "Bash",
      "lastToolSummary": "cd "C:/Users/Rigam/OneDrive/Documents/Work/Gambit/.claude/wâ¦",
      "promptPreview": "CONTEXT. Fark is a dice roguelite. C:/Users/Rigam/OneDrive/Documents/Work/Gambit/.claude/worktrees/zen-chatterjee-f04c42/fark_proto.html is the real game (~36k lines, single file).
C:/Users/Rigam/OneDrive/Documents/Work/Gambit/.claude/worktrees/zen-chatterjee-f04c42/tools/sim_harness.js is a simulation harness. The harness drives the REAL game for the player
(F.simTurn calls startPTurn/rollPool/afâ¦",
      "lastProgressAt": 1786183756210,
      "tokens": 110855,
      "toolCalls": 36,
      "durationMs": 327808,
      "resultPreview": "## AREA REPORT: where the RIVAL's family cards actually take effect

File: `C:/Users/Rigam/OneDrive/Documents/Work/Gambit/.claude/worktrees/zen-chatterjee-f04c42/fark_proto.html`

### 0. Structural finding that frames everything below

`famFire` (12737) walks **both** lists on every hook, regardless of actor â 12757-12758:
```js
['p','o'].forEach(function(owner){
    var list=owner==='p'?(G.pF||[]â¦"
    },
    {
      "type": "workflow_agent",
      "index": 3,
      "label": "map:inventory",
      "phaseIndex": 1,
      "phaseTitle": "Map",
      "agentId": "aedb17a5b9b164b31",
      "model": "claude-opus-5",
      "state": "done",
      "startedAt": 1786183429721,
      "queuedAt": 1786183423488,
      "attempt": 1,
      "lastToolName": "Bash",
      "lastToolSummary": "cd "C:/Users/Rigam/OneDrive/Documents/Work/Gambit/.claude/wâ¦",
      "promptPreview": "CONTEXT. Fark is a dice roguelite. C:/Users/Rigam/OneDrive/Documents/Work/Gambit/.claude/worktrees/zen-chatterjee-f04c42/fark_proto.html is the real game (~36k lines, single file).
C:/Users/Rigam/OneDrive/Documents/Work/Gambit/.claude/worktrees/zen-chatterjee-f04c42/tools/sim_harness.js is a simulation harness. The harness drives the REAL game for the player
(F.simTurn calls startPTurn/rollPool/afâ¦",
      "lastProgressAt": 1786184066882,
      "tokens": 145217,
      "toolCalls": 55,
      "durationMs": 637160,
      "resultPreview": "# FAMILY-CARD INVENTORY â ground truth

All numbers below are measured, either by evaluating the shipped literals in node or by running `tools/probe_famcards_inventory2.js` against the live page (`node tools/shoot.js --eval-file tools/probe_famcards_inventory2.js --url http://localhost:8084/fark_proto.html`). File is `C:/Users/Rigam/OneDrive/Documents/Work/Gambit/.claude/worktrees/zen-chatterjee-fâ¦"
    },
    {
      "type": "workflow_agent",
      "index": 4,
      "label": "map:modelgap",
      "phaseIndex": 1,
      "phaseTitle": "Map",
      "agentId": "a2c6cf0e791440b67",
      "model": "claude-opus-5",
      "state": "done",
      "startedAt": 1786183428010,
      "queuedAt": 1786183423488,
      "attempt": 1,
      "lastToolName": "Bash",
      "lastToolSummary": "cd "C:/Users/Rigam/OneDrive/Documents/Work/Gambit/.claude/wâ¦",
      "promptPreview": "CONTEXT. Fark is a dice roguelite. C:/Users/Rigam/OneDrive/Documents/Work/Gambit/.claude/worktrees/zen-chatterjee-f04c42/fark_proto.html is the real game (~36k lines, single file).
C:/Users/Rigam/OneDrive/Documents/Work/Gambit/.claude/worktrees/zen-chatterjee-f04c42/tools/sim_harness.js is a simulation harness. The harness drives the REAL game for the player
(F.simTurn calls startPTurn/rollPool/afâ¦",
      "lastProgressAt": 1786183989909,
      "tokens": 146295,
      "toolCalls": 39,
      "durationMs": 561899,
      "resultPreview": "## GAP ANALYSIS â F.oppTurn vs the real rival turn, for family cards

All line numbers verified. Harness = `C:/Users/Rigam/OneDrive/Documents/Work/Gambit/.claude/worktrees/zen-chatterjee-f04c42/tools/sim_harness.js`. Game = `C:/Users/Rigam/OneDrive/Documents/Work/Gambit/.claude/worktrees/zen-chatterjee-f04c42/fark_proto.html`. Live probe run through `tools/sim_run.js`, seed 20260731; probe file keâ¦"
    },
    {
      "type": "workflow_agent",
      "index": 5,
      "label": "verify:effects",
      "phaseIndex": 2,
      "phaseTitle": "Verify",
      "agentId": "ae325d61029d365a4",
      "model": "claude-opus-5",
      "state": "done",
      "startedAt": 1786183759484,
      "queuedAt": 1786183757679,
      "attempt": 1,
      "lastToolName": "Bash",
      "lastToolSummary": "cd "C:/Users/Rigam/OneDrive/Documents/Work/Gambit/.claude/wâ¦",
      "promptPreview": "CONTEXT. Fark is a dice roguelite. C:/Users/Rigam/OneDrive/Documents/Work/Gambit/.claude/worktrees/zen-chatterjee-f04c42/fark_proto.html is the real game (~36k lines, single file).
C:/Users/Rigam/OneDrive/Documents/Work/Gambit/.claude/worktrees/zen-chatterjee-f04c42/tools/sim_harness.js is a simulation harness. The harness drives the REAL game for the player
(F.simTurn calls startPTurn/rollPool/afâ¦",
      "lastProgressAt": 1786184339445,
      "tokens": 135690,
      "toolCalls": 35,
      "durationMs": 579961,
      "resultPreview": "# ADVERSARIAL VERIFICATION â "effects" area map

File verified: `C:/Users/Rigam/OneDrive/Documents/Work/Gambit/.claude/worktrees/zen-chatterjee-f04c42/fark_proto.html` (37016 lines)

---

## A. WRONG â claims the source contradicts

### A1. "All eight [actor-`'o'`] seams are **no-ops** for both card lists" â FALSE

Three CFX handlers gate on `ev.owner==='p'` **alone**, not `_fxMine`. `ev.owner` isâ¦"
    },
    {
      "type": "workflow_agent",
      "index": 6,
      "label": "verify:state",
      "phaseIndex": 2,
      "phaseTitle": "Verify",
      "agentId": "a7f214fd048a5a17a",
      "model": "claude-opus-5",
      "state": "done",
      "startedAt": 1786183965779,
      "queuedAt": 1786183963785,
      "attempt": 1,
      "lastToolName": "Bash",
      "lastToolSummary": "cd "C:/Users/Rigam/OneDrive/Documents/Work/Gambit/.claude/wâ¦",
      "promptPreview": "CONTEXT. Fark is a dice roguelite. C:/Users/Rigam/OneDrive/Documents/Work/Gambit/.claude/worktrees/zen-chatterjee-f04c42/fark_proto.html is the real game (~36k lines, single file).
C:/Users/Rigam/OneDrive/Documents/Work/Gambit/.claude/worktrees/zen-chatterjee-f04c42/tools/sim_harness.js is a simulation harness. The harness drives the REAL game for the player
(F.simTurn calls startPTurn/rollPool/afâ¦",
      "lastProgressAt": 1786184582924,
      "tokens": 122391,
      "toolCalls": 37,
      "durationMs": 617145,
      "resultPreview": "Verified against source. Findings below, ordered by severity.

---

## ERRORS

**1. `saveMatchState` line numbers are wrong by ~25,000 lines.** The map cites `saveMatchState (35595â35678)` and `JSON.parse(JSON.stringify(G.rung)) (35600)`. Actual: `function saveMatchState()` is at **10235**, ending 10318; the rung clone is at **10247**. Lines 35595â35678 are the tail of `launchSeat` + `launchPatronâ¦"
    },
    {
      "type": "workflow_agent",
      "index": 7,
      "label": "verify:modelgap",
      "phaseIndex": 2,
      "phaseTitle": "Verify",
      "agentId": "adb6a153f5ce92359",
      "model": "claude-opus-5",
      "state": "done",
      "startedAt": 1786183997294,
      "queuedAt": 1786183993621,
      "attempt": 1,
      "lastToolName": "Bash",
      "lastToolSummary": "cd "C:/Users/Rigam/OneDrive/Documents/Work/Gambit/.claude/wâ¦",
      "promptPreview": "CONTEXT. Fark is a dice roguelite. C:/Users/Rigam/OneDrive/Documents/Work/Gambit/.claude/worktrees/zen-chatterjee-f04c42/fark_proto.html is the real game (~36k lines, single file).
C:/Users/Rigam/OneDrive/Documents/Work/Gambit/.claude/worktrees/zen-chatterjee-f04c42/tools/sim_harness.js is a simulation harness. The harness drives the REAL game for the player
(F.simTurn calls startPTurn/rollPool/afâ¦",
      "lastProgressAt": 1786184762138,
      "tokens": 145150,
      "toolCalls": 52,
      "durationMs": 764844,
      "resultPreview": "## VERDICT

The map's line numbers are almost all exact and its identifier counts are all correct. Two things are wrong at the level that matters: **one count is inflated by a string that is not the thing being counted**, and **the ADJACENT note's central conclusion is measured false**. The Â§3 roster table also does not reproduce at its own stated seed.

Probe files: `C:\Users\Rigam\AppData\Local\â¦"
    },
    {
      "type": "workflow_agent",
      "index": 8,
      "label": "verify:inventory",
      "phaseIndex": 2,
      "phaseTitle": "Verify",
      "agentId": "a7e74220af13538c8",
      "model": "claude-opus-5",
      "state": "done",
      "startedAt": 1786184070540,
      "queuedAt": 1786184068463,
      "attempt": 1,
      "lastToolName": "Bash",
      "lastToolSummary": "cd "C:/Users/Rigam/OneDrive/Documents/Work/Gambit/.claude/wâ¦",
      "promptPreview": "CONTEXT. Fark is a dice roguelite. C:/Users/Rigam/OneDrive/Documents/Work/Gambit/.claude/worktrees/zen-chatterjee-f04c42/fark_proto.html is the real game (~36k lines, single file).
C:/Users/Rigam/OneDrive/Documents/Work/Gambit/.claude/worktrees/zen-chatterjee-f04c42/tools/sim_harness.js is a simulation harness. The harness drives the REAL game for the player
(F.simTurn calls startPTurn/rollPool/afâ¦",
      "lastProgressAt": 1786184656485,
      "tokens": 122125,
      "toolCalls": 35,
      "durationMs": 585945,
      "resultPreview": "# ADVERSARIAL VERIFICATION â "FAMILY-CARD INVENTORY" map

File: `C:/Users/Rigam/OneDrive/Documents/Work/Gambit/.claude/worktrees/zen-chatterjee-f04c42/fark_proto.html`
Harness: `C:/Users/Rigam/OneDrive/Documents/Work/Gambit/.claude/worktrees/zen-chatterjee-f04c42/tools/sim_harness.js`
Probe read: `C:/Users/Rigam/OneDrive/Documents/Work/Gambit/.claude/worktrees/zen-chatterjee-f04c42/tools/probe_famâ¦"
    },
    {
      "type": "workflow_agent",
      "index": 9,
      "label": "sizing",
      "phaseIndex": 3,
      "phaseTitle": "Size",
      "agentId": "acdd92b94cb0f6166",
      "model": "claude-opus-5",
      "state": "done",
      "startedAt": 1786184769556,
      "queuedAt": 1786184765966,
      "attempt": 1,
      "lastToolName": "Bash",
      "lastToolSummary": "cd "C:/Users/Rigam/OneDrive/Documents/Work/Gambit/.claude/wâ¦",
      "promptPreview": "CONTEXT. Fark is a dice roguelite. C:/Users/Rigam/OneDrive/Documents/Work/Gambit/.claude/worktrees/zen-chatterjee-f04c42/fark_proto.html is the real game (~36k lines, single file).
C:/Users/Rigam/OneDrive/Documents/Work/Gambit/.claude/worktrees/zen-chatterjee-f04c42/tools/sim_harness.js is a simulation harness. The harness drives the REAL game for the player
(F.simTurn calls startPTurn/rollPool/afâ¦",
      "lastProgressAt": 1786185318918,
      "tokens": 145643,
      "toolCalls": 30,
      "durationMs": 549362,
      "resultPreview": "# SIZING â porting the rival family-card subsystem into `F.oppTurn`

Target files: `C:/Users/Rigam/OneDrive/Documents/Work/Gambit/.claude/worktrees/zen-chatterjee-f04c42/tools/sim_harness.js` (harness, 1331 lines; `F.oppTurn` = 578â748) and `C:/Users/Rigam/OneDrive/Documents/Work/Gambit/.claude/worktrees/zen-chatterjee-f04c42/fark_proto.html` (game, 37016 lines).

---

## VERDICT UP FRONT

**No opâ¦"
    }
  ],
  "totalTokens": 1203373,
  "totalToolCalls": 370
}