# FARK — SIM RESULTS, 2026-07-31

Four agents, four lenses, one seed. Run against the shipped build of
`fark_proto.html` on the dev server; **the game file was not edited — not one
character** (verified `git status` clean on that path before, during and after).

- **Seed: 20260731** everywhere. Every number below replays exactly via
  `node tools/sim_run.js tools/<file>.js --seed 20260731` from the worktree root.
- **~300,000 simulated matches + 500 full eight-night runs.**
- Intervals: Wilson 95% on rates, Newcombe hybrid-score on differences of
  independent proportions, McNemar discordant-pair intervals on paired designs.
  A number without an interval below is a deterministic single-fire observation
  and is labelled as such.
- Real shipped functions were driven throughout — `scoreRoll`, `scoreSelection`,
  `_iconFire`, `_breakDie`, `BREAK_TRIGGERS[*].fire`, `_tradeRestore`, `doBust`,
  `handleBank`, `endPTurn`, `_enchInit`, `_gbEnchantApply`, `generatePatron`,
  `_shopRollNight`, `_stTrade` and ~60 more. Where a path could not be driven it
  is named as a gap, never modelled and reported as a result.

---

## VERDICTS

| Lens | Verdict | One line |
|---|---|---|
| **1 — FUN** (no dominant, solved strategy) | **FAIL** | Two agent-independent dominant strategies exist (the zero-point icon sweep, and buying Starstone), and the enchant system punishes every player who does *not* know the sweep — so build investment is anti-correlated with winning for honest play. |
| **2 — SENSE OF POWER** | **MIXED** | The escalation is real and enormous (+44 to +63 win-rate points, night-1 vs night-8, every tier) — but it is delivered by dice and family cards, while the six briefed brands are an **18-point net downgrade** and the specced loadout costs 5,990g against a 5,921g perfect-run lifetime income. |
| **3 — ELEGANCE** | **MIXED** | All seven reconciled interactions hold in code (6 PASS, Preserve guard-verified-with-feature-absent) and all seven Break family rows fire exactly their own verb — but three surrounding *claims* do not survive measurement: Still Waters is not a hard counter to Break+Obsidian, ruling #24's Silver ratio is not policy-invariant, and the shared harness silently deletes every Trade brand. |
| **4 — NO CHEAT AROUND POSSIBLE** | **FAIL** | Six plain bone dice, one Amber die in the stash, Fair Trade and one Break brand wins **500/500** tier-3 patron matches and **299/300** boss matches in a single turn, at 2.04× ORACLE OTTO's fully-built honest ceiling. |

**Overall: FAIL.**

---

## IF YOU READ NOTHING ELSE — the five things that decide matches on their own

Each of these was found independently, each is reproducible from the source
alone, and each is larger than every legitimate decision in the game combined.
They are listed by size of effect.

1. **The zero-point icon sweep.** `fark_proto.html:23253` —
   `if(pts<0&&_iconSel.length)pts=0;` — converts an *illegal* non-icon selection
   into a *legal zero-point keep* whenever one branded die shows its icon face.
   That empties the pool, which is the game's own hot-dice condition
   (`fark_proto.html:23322`), so you get a fresh six and +250. Measured: wrapping
   an agent in the single extra rule "if a zero-point keep clears the table, take
   it" and changing nothing else is worth **+80.5 win-rate points [77.95, 82.69]**
   on a 900g loadout — and it works identically for a fully random agent
   (**RANDOM RANDY 1.3% → 80.3%**). With zero brands the delta is exactly 0.00,
   so the effect is the sweep and nothing else. *(Lens 1, blocker)*
2. **Amber's Break death-trigger never ends.** `doBust()` clears
   `G._bustImmuneTurn` only on its *failure* path; on success it rerolls, sets
   phase back to `choosing`, and returns with the flag still set. Only
   `startPTurn` ever resets it. So one Break on an Amber die makes the rest of
   the turn permanently bust-proof. Asked for 20,000 points, **98.5% [95.7, 99.5]
   of immune turns were still running** when the harness's own 60-roll guard
   stopped them. Match level, near-starting loadout: **35.7% → 98.7%** with one
   turn-1 Break. *(Lens 4, blocker)*
3. **Starstone is a flat +500 per die on every bank.** `fark_proto.html:25452`,
   inside `handleBank` — unconditional, stacks per die, not gated on scoring, on
   the die being rolled, or on anything the player does. Two Starstone + four bone
   at 1,400g: **carl 93.3%, ned 86.0%, RANDY 77.5%** against an all-bone baseline
   of 27.8 / 13.0 / 3.0. Roster spread collapses from 34.8 points at k=0 to
   **4.3 points at k=3**. It is a flat 700g in `DICE_STORE`, stock 3, offered on
   ~45% of nights. *(Lens 1, blocker)*
4. **Fair Trade → Break costs no die.** `_removeDieAt`'s Fair-Trade branch (per
   ruling #2 / §4b) hands the lane back to the player's benched die and returns
   early — `matchDice` is not spliced, `numDice` is not decremented. The
   guaranteed family payout is collected at **six dice, zero cost**. Whole
   matches, both arms firing Break ~0.95×/match: borrow-and-break **48.6%
   [44.2, 53.0]** at 6.00 dice; break-your-own **15.2% [12.3, 18.6]** at 5.00
   dice. *The implementation matches the ruling exactly — the ruling is the
   hole.* This is the exploit the brief asked to confirm was closed. It is not.
   *(Lens 4, blocker)*
5. **The briefed six-brand loadout is a net downgrade.** Night-8 dice + badge +
   3 tier-3 cards with **no brands** wins **99.0% [98.0, 99.5]**; the identical
   build with the six briefed brands wins **81.0% [78.1, 83.6]** — paired delta
   **−18.0 [−20.8, −15.2]**, 154 discordant pairs, n=800, tier 5. The system this
   whole rework exists for is the one layer that subtracts from the power fantasy.
   *(Lens 2, blocker)*

Points 1 and 5 are the same coin: the icon face banks zero, and the compensating
effect does not pay for itself — so a player who *doesn't* know the sweep is
punished for buying brands, and a player who *does* wins regardless of skill.

---

# LENS 1 — FUN

> **VERDICT: FAIL.** The intended shape is gone in both directions at once. Two
> dominant, agent-independent strategies exist — buying Starstone and the icon
> sweep — while the enchant system as shipped actively punishes every agent that
> does not know the sweep. Build investment is anti-correlated with winning for
> honest play.

Method: seed 20260731, ~196,000 matches. Files
`tools/sim_fun_draft.js`, `sim_fun_a.js`, `sim_fun_bc.js`, `sim_fun_d1.js`,
`sim_fun_d2.js`, `sim_fun_e.js`, `sim_fun_f.js`, `sim_fun_g.js`, `sim_fun_h.js`.
A build/draft phase was written (`sim_fun_draft.js`) because `FSIM` exposes
`draft()`/`enchant()` in its policy interface but nothing calls them; it drives
the game's own `DICE_STORE` and `ENCH_ICONS` prices and the game's own guards
(`_wardOwned`, `_iconFaceRoll`).

### A. Execution-only spread — identical loadout, tier-3 patron, n=2000/agent

Night-4 loadout amber/amber/silver/iron/bone/bone + tithe + ward.

| Agent | Win % | 95% CI |
|---|---|---|
| ORACLE OTTO | 88.35 | [86.9, 89.7] |
| CAUTIOUS CARL | 27.25 | [25.3, 29.2] |
| BALANCED BEA | 27.15 | [25.3, 29.1] |
| RUSHER RITA | 23.15 | [21.4, 25.1] |
| NEWBIE NED | 12.75 | [11.4, 14.3] |
| GAMBLER GREG (naive) | 12.35 | [11.0, 13.9] |
| GAMBLER GREG (informed) | 12.35 | — |
| RANDOM RANDY | 2.85 | [2.2, 3.7] |

The deliberate humanlike cluster spreads **4.1 points** and carl − bea = **0.1
[−2.7, 2.9]** (indistinguishable) — *that half of the intended shape is intact*.
But otto − bea = **+61.2 [58.7, 63.5]**, and the decomposition below shows
essentially all of it is the keep function exploiting the sweep, not banking.

### A2. Same roster at night-8 gear vs tier-7 — the spread has INVERTED

n=2000/agent. rita **92.70**, carl **92.65**, ned **78.75**, bea **78.60**,
randy **65.40**, greg-informed **59.35**, greg-naive **52.20**, otto **99.85**.

- **bea − ned = −0.1 [−2.7, 2.4]** — the near-random control ties the deliberate
  agent at n=2000.
- Win rate falls monotonically in icons-used-per-match for every agent except
  Otto: rita 2.30 icons → 92.7%; carl 3.78 → 92.65%; ned 5.85 → 78.75%; bea 7.02
  → 78.6%; randy 9.25 → 65.4%; greg 13.44 → 52.2%.

The two agents who *ignore their own brands* win most.

### C. The crossed design — 8 agents × 11 builds, n=500/cell, 44,000 matches

2000g purse, tier 3. Agent-effect sd **20.6**, build-effect sd **14.9**. Mean
Spearman ρ between agents' build rankings **0.48**. `jade + starstone + flint +
snare` is the best build for **6 of 8** agents and runner-up for the other two,
winning in every row (carl 80.0, bea 84.0, ned 63.4, rita 82.0, randy 32.4, otto
91.4) against 19.8 / 28.4 / 13.2 / 19.4 / 5.0 / 45.6 on the obsidian build.

**Carl on six FREE bone dice wins 27.0%. Carl on the 1,910g build he drafted
himself wins 19.8%.**

### D. The sweeps

Material sweep `[m,m,bone×4]`, tier 3, n=400 (carl / ned / otto):

| Material | carl | ned | otto |
|---|---|---|---|
| **starstone** | **93.3** | **86.0** | **95.5** |
| jade2 | 51.8 | 22.3 | 68.5 |
| obsidian | 28.3 | 13.3 | 28.3 |
| bone | 27.8 | 13.0 | 37.8 |
| *(all others)* | 27.8–51.8 | — | — |

Enchant sweep, 2 brands on fixed materials, n=400 (carl / ned / otto):

| Brand | carl | ned | otto |
|---|---|---|---|
| none | 45.8 | 20.8 | 59.8 |
| ward | 37.0 | 17.3 | 78.0 |
| snuff | 30.5 | 13.8 | 88.5 |
| snare | 30.0 | 15.0 | 86.8 |
| fog | 27.5 | 14.8 | 84.3 |
| tithe | 27.3 | 11.8 | 83.5 |
| **break** | **21.0** | **5.5** | 71.8 |

**Every functioning brand costs carl and ned 9–25 points and gains otto 12–29.**
That is the trap, stated numerically.

Starstone dose (roster spread excluding greg): k=0 → **34.8 pts**, k=1 (700g) →
53.8, k=2 (1400g) → **18.0**, k=3 (2100g) → **4.3**, k=6 → **0.5**. randy k0→k2
**+74.5 [69.6, 78.5]**. Holds unchanged at tier 5 and 7.

Badges vs no badge (otto, n=400): ZERO HOUR **−75.3**, STILL WATERS −12.0,
KINDRED +1.8, RECKONING +0.5. Zero Hour is the game's accidental hard counter to
the sweep — the rework brief predicts a "~14% average turn-bank tax"; against an
agent that actually uses its brands it removes **75 win-rate points**.

### E. Greg naive vs informed Break — the brief's centrepiece question

**Answers YES, but conditionally.**

- Night-8 loadout vs tier-7, n=2500 each: naive **53.36 [51.40, 55.31]**,
  informed **59.76 [57.82, 61.67]**, diff **−6.40 [−9.13, −3.65]** (intervals
  disjoint). Informed fires Break 1.081/match vs 2.362; 34.5% of his breaks land
  on the last turn vs 17.8%.
- Obsidian×2 + two BREAK brands vs tier-3: naive **4.68 [3.92, 5.58]**, informed
  **3.48 [2.83, 4.27]**, diff **+1.20 [0.10, 2.31]** — **the sign flips**.
- Control (same dice, tithe instead of break): both 4.12, diff **0.00 [−1.11,
  1.11]**, byte-identical — proving the Break filter is the only difference
  between the two Gregs.

So the mechanic teaches a **build-contingent** lesson, not a general one.

### E2. Where Otto's edge actually lives (n=2000, tier 3)

| Config | Win % |
|---|---|
| bea bank + bea keep | 26.80 |
| bea bank + **OTTO keep** | **78.35** |
| OTTO bank + bea keep | 31.70 |
| otto + otto | 85.80 |

On the **same materials with the brands removed**: 46.60 / 54.80 / 49.45 / 60.00.
**Otto's +59 collapses to +13 once the brands are gone.** Banking thresholds are
flat exactly as the brief expects; keep choice on a *branded* loadout is not.

### F/G/H. The sweep, isolated

Mechanism (n=300): rolls offering a table-clearing keep go **10.3% → 36.7%** with
two brands, of which 29.9% are icon-assisted. Otto took 1,848 clearing keeps vs
448; 1,482 contained an icon. Hot dice per match **1.36 → 5.90**. Carl took **0**
icon-clears out of 240.

The sweep wrapper (one extra rule, n=1200/cell):

| Brands | bea | carl | randy |
|---|---|---|---|
| 0 (control) | +0.00 | +0.00 | +0.00 |
| 1 tithe (150g) | +23.25 [19.32, 27.08] | +20.25 [16.32, 24.09] | +5.58 [3.90, 7.36] |
| 2 tithe (300g) | +37.17 [33.38, 40.79] | — | — |
| 6 tithe (900g) | **+80.50 [77.95, 82.69]** | **+81.08 [78.56, 83.24]** | **+78.92 [76.43, 81.13]** |

Mean turn bank **602 → 1,784**.

The line, isolated against the real `scoreSelection` (study H):
`scoreSelection([2,3,4,6,2]) = −1` (illegal alone). Add one branded die showing
its icon face and the shipped accept rule commits all six dice for 0 points; the
pool is empty; hot dice fires.

### Lens 1 findings

| Sev | Finding |
|---|---|
| **blocker** | A single icon-face die legalises committing every other die for zero points → hot dice. Dominant and agent-independent. |
| **blocker** | Starstone's unconditional +500/die/bank collapses the roster spread from 34.8 pts to 4.3 pts at 2,100g. |
| **blocker** | The enchant system is a trap for anyone who doesn't know the sweep: brand count is inversely correlated with win rate for honest play. |
| major | The spread has inverted at high gear — near-random ties deliberate (bea − ned = −0.1 [−2.7, 2.4]). |
| major | Execution is flat among humanlike policies (4.1 pts) as intended, but the EV-optimal ceiling sits +61.2 above them, essentially all of it the keep function. |
| major | The draft is close to solved — ρ 0.48 between agents' build orderings, one build best for 6 of 8. |
| minor | Break timing answers YES (−6.40 [−9.13, −3.65]) but reverses on an obsidian-heavy loadout. |
| minor | ZERO HOUR is −75.3 for an agent that uses its brands, vs a specced "~14% turn-bank tax". |

---

# LENS 2 — SENSE OF POWER

> **VERDICT: MIXED.** The escalation is real and enormous — night-8 beats night-1
> by +44 to +63 points at every tier and on every boss. But it is carried almost
> entirely by DICE and FAMILY CARDS. The two systems this rework is about make
> the player weaker or nothing, and the specced loadout is arithmetically
> unaffordable.

Method: seed 20260731, ~95,000 matches + 250 full runs ×2 shoppers. Files
`tools/sim_power_probe.js`, `sim_power_a.js` … `sim_power_g.js`. **Every
comparison is PAIRED**: for match *i* the same seed is installed twice, the rival
is generated twice by the real `generatePatron`, both sides move in the same
order — the only difference within a pair is the gear (or, in D1/G, one keep
rule). McNemar intervals cross-check against Newcombe to within 0.1pt everywhere.

Night-1 is not invented: `_freshRun()` returns six bone and 100g, and
`famRunDraftPick` replaces the last bone with one of
`['amber','silver','obsidian','starstone','vagabond']`.

### The headline delta (Bea, n=800/cell, paired)

| Tier | Night-1 | Night-8 | Paired delta |
|---|---|---|---|
| 0 | 63.4 [60.0, 66.6] | 96.8 [95.3, 97.8] | +33.4 [+29.8, +36.9] |
| 1 | 52.8 [49.3, 56.2] | 92.4 [90.3, 94.0] | +39.6 [+35.7, +43.5] |
| 2 | 41.9 [38.5, 45.3] | 90.0 [87.7, 91.9] | +48.1 [+44.2, +52.0] |
| 3 | 30.8 [27.7, 34.0] | 81.5 [78.7, 84.0] | +50.7 [+46.6, +54.9] |
| 4 | 33.0 | 79.0 | +46.0 [+41.7, +50.3] |
| 5 | 36.4 [33.1, 39.8] | 81.0 [78.1, 83.6] | +44.6 [+40.5, +48.8] |
| 6 | 33.9 | 81.5 | +47.6 [+43.4, +51.8] |
| 7 | 32.3 [29.1, 35.6] | 76.1 [73.1, 78.9] | +43.9 [+39.6, +48.2] |

Bosses (paired, n=420/cell): night-1 26.7–51.9%, night-8 **73.1–90.7%**, delta
+37.4 to +61.7, every interval clear of zero. Grog 51.9 → 90.7; Ambrose 30.5 →
78.3.

**The power fantasy lands.** Now where it comes from.

### Layer decomposition (paired, n=600, tier 5)

| Layer | Win % |
|---|---|
| night-1 | 36.4 [33.1, 39.8] |
| **+ night-8 DICE only** (no brand/badge/card) | **94.2 [92.0, 95.8]** |
| + the six BRANDS | 44.5–49.8 (**−41.7 [−46.3, −37.0]** at t3) |
| + the worn BADGE (Kindred) | +3.0 [+0.6, +5.4] at t3 |
| + 3 tier-3 FAMILY CARDS | +29.2 [+25.3, +33.0] |
| night-8 dice + cards + badge, **NO BRANDS** | **99.0 [98.0, 99.5]** |
| night-8 as specced (6 brands, naive Break) | 81.0 [78.1, 83.6] → **−18.0 [−20.8, −15.2]** |
| night-8, 6 brands, **INFORMED Break** | 97.0 [95.6, 98.0] → −2.0 [−3.3, −0.7] vs no brands |

The escalation is **the dice**, +56 to +61 points on its own. Cards add +29 (and
that is a *floor* — interactive actives never fire in the harness). Brands
subtract. Badges do essentially nothing.

### Per-brand isolation (one brand on night-8 dice, paired vs 94.2%, n=600, t5)

| Brand | Delta |
|---|---|
| **break** | **−29.0 [−33.1, −24.9]** |
| tithe | −3.3 [−6.1, −0.6] |
| ward | −3.3 [−6.1, −0.6] |
| snare | −2.8 [−5.7, 0.0] |
| trade | −2.0 [−4.7, +0.7] |
| fog | −1.7 [−4.4, +1.1] |
| snuff | −0.8 [−3.5, +1.9] |
| quicksilver | 0.0 — **UNMEASURED**, needs a tap the harness can't do |

Brand-count curve (cheapest first): 94.2, 91.7, 92.5, 90.3, then **62.3 the
moment Break is added**, 62.2, 52.7. Per-turn bust 7.2% → 29.2% at six brands —
Break destroying the player's *own* dice, not the icon faces.

**Break is a cliff, not a slope, and the timing read gives 22 of the 29 points
back.** Bea vs Bea-plus-one-rule ("hold the skull until no future turn remains"):
break-only build 65.2% → 87.5%, **+22.3 [+18.7, +26.0]**; full six-brand build
81.0 → 97.0, **+16.0 [+13.2, +18.8]**. On the unbranded control the same two
agents differ by **exactly 0.0 with zero discordant pairs**. This is §4's finding
landing correctly — and it is the *only* place in this report where the rework's
intended skill expression measurably works.

### Badges, worn, on the six-brand build (paired vs no badge, n=420, t5)

| Badge | Delta | Note |
|---|---|---|
| **STILL WATERS** | **−23.6 [−28.8, −18.3]** | bust/turn 29.4 → 41.6, bank 6,920 → 4,951 |
| KINDRED | +1.7 [−0.7, +4.0] | gold 20.6 → 39.8/match, exact 2×, Tithe-only |
| ZERO HOUR | −0.2 [−4.8, +4.3] | bust/turn 29.4 → 7.8 |
| RECKONING | 0.0 [−3.8, +3.8] | |

On an **unbranded** build every badge is exactly 0.0 with zero discordant pairs.
Still Waters costs 23.6 points because the sleeve binds both sides and the player
is the only side with enchanted dice to suppress.

### The gold curve — 250 full runs through the real progression and shop

- **Cost of the briefed night-8 loadout: 5,990g** (dice 4,190 + brands 1,800).
- **A flawless run — every seat, every boss, nothing lost — collects 5,921g in
  its entire life, and only 4,205g of it before night 8 begins.** The specced
  loadout is arithmetically unaffordable, not unlucky.
- Dice-first shopper: 132/250 reach night 8 holding 5.99 family dice and **2.01
  brands [1.72, 2.30]** (median 2; 0:28 1:25 2:43 3:14 4:8 5:4 6:10). **7.6% hold
  the full spec.** jade2 (1,800g) owned in **5 of 250 runs (2.0%)**. Median purse
  at the 344 shop visits *after* the dice are complete: **90g** — below the 150g
  cheapest brand.
- Brands-first shopper: 4.18 brands [3.80, 4.56] at night 8 and 39.3% reach the
  full spec, but **176 paid brands are destroyed by later die purchases**
  (`_stTrade` nulls the slot's enchant, no refund) and run-clear falls 52.0% →
  35.2%.
- Power against the loadout a run **really** arrives at (6 family dice, 0–2
  brands, badge, 3 cards, t5, n=600 paired): **35.3 → 99.3, delta +64.0 [+60.1,
  +67.9]**. The two brands cost exactly nothing (99.3 either way).

### Difficulty stops escalating after tier 3

Night-1 win rate at tiers 3–7: 30.8 / 33.0 / 36.4 / 33.9 / 32.3 — flat inside its
intervals. What changes instead is that matches stop being races and become
8-turn point comparisons: cap-decided endings go **0.3% (t0) → 85.5% (t7)**.
Opponent mean bank barely moves (4,473 at t2 → 6,220 at t7) while patron targets
climb 5,000 → 9,500.

### Lens 2 findings

| Sev | Finding |
|---|---|
| **blocker** | The briefed six-brand loadout is −18.0 [−20.8, −15.2] against the identical build with no brands. |
| **blocker** | The maxed loadout costs 5,990g; a perfect run earns 5,921g lifetime, 4,205g pre-night-8. |
| major | Break alone is the whole brand cost (−29.0) and the timing read returns +22.3 of it. |
| major | In practice a dedicated shopper reaches 2.0 of 6 brands; jade2 is bought in 2% of runs. |
| major | Buying a die destroys that slot's brand with no refund, so the correct order is dice-then-brands — which is the order that guarantees brands never get bought. |
| major | Difficulty is flat from tier 3 to tier 7 for an un-upgraded build. |
| major | No badge is a power gain; Still Waters is −23.6 on an enchanted build. |
| major | Both acceptance bands are badly overshot at intended gear (see decision section). |
| note | The enchant layer's value inverts by agent: carl −4.9, ned −16.0, otto +1.1, greg-informed +21.1. |
| note | The brand-face draw is clean — 4,000 draws × 13 materials, only {1,5}, split within 1,969–2,048 of even. |

---

# LENS 3 — ELEGANCE

> **VERDICT: MIXED.** All seven reconciled interactions hold in the shipped code
> — six PASS, Preserve guard-verified-with-feature-absent — and all seven Break
> family rows fire exactly their own verb with **zero cross-contamination**. But
> three surrounding claims do not survive measurement, and one of them
> invalidates every Trade number any agent has reported.

Method: seed 20260731. Files `tools/sim_l3_probe.js`, `sim_l3_elegance.js`,
`sim_l3_elegance2.js`, `sim_l3_elegance3.js`, `sim_l3_elegance4.js`. Function
ordering for the Zero Hour question was read off the **live**
`handleRoll.toString()`, not off the file on disk.

### The seven targeted checks

| # | Check | Result |
|---|---|---|
| E1 | **Break destroys for THIS match only, restored next match** | **PASS.** One driven `_breakDie` on lane 2: `matchDice` 6→5, `_enchArr` spliced (the lane's Trade brand went with the die), `numDice` 5, `_diceOut` recorded. `S.run.dice`/`dieEnch`/`diceInv`/`dieEnchInv` bit-identical. Still 5 after `startPTurn` and 3 further turns. Next match built by the real `newG`: all six materials and all three brands back, face numbers included. |
| E2 | **Trade swaps whole die, both loadouts restored bit-for-bit** | **PASS** (after patching a harness defect — see below). Ledger correct, `_enchArr[3]`→null (self-consuming), `S.run` and `rung.dice` untouched. `_tradeRestore()` returned 1 and made `matchDice`, `matchOppDice` and `_enchArr` all bit-identical; second call returned 0. **200 real matches, 123 Trades fired: 0 ledger residue, 0 loadout drift, 0 brand loss, 0 foreign material left live.** Break below a traded lane: materials correct via the `t.cnt` fallback. Break the borrowed die: down exactly one die for the match, opponent's die home at match end. |
| E3 | **Still Waters suppresses Break's GUARANTEED Obsidian payout** | **PASS for a worked die.** Worked obsidian + badge → breakPaid 0; badge off → 1000. Passive path likewise: 0 shatters/turn vs 0.685 (n=400 turns each). **But see the finding below — the surrounding design claim fails.** |
| E4 | **No loadout can contain two Ward-branded dice** | **PASS.** Eight purchase sequences driven through the real `_gbEnchantApply` / `famDieStash` / `famDieEquip` / `_stTrade` / `_enchInit`: buy-then-buy, buy-stash-buy, relic-then-buy, buy-then-win-relic (350g refunded, purchased ward cleared), equip-relic-over-ward, forged point-of-sale second ward (0g spent, refused), relic-traded-out-then-buy, ward+stashed-relic. Every one ends at ≤1 Ward in loadout and ≤1 in loadout+inventory. |
| E5 | **Branded faces only ever on natural 1 or 5** | **PASS.** **96,000** `_iconFaceRoll` draws across all 24 `DICE_TYPES`: 0 outside {1,5}, 0 outside the die's own natural faces. 1,504 brands on fresh match loadouts (all seven icons) + 1,959 brands audited after 200 real matches with a live Trade: 0 illegal faces, 0 brands on a material whose `_iconFaces` disallows them. Forged sales on 2/3/4/6 all refused, 0g spent. The v3 migration refunded 1,250g and left only legal faces. Only born brand in the catalogue: `brutus_shield` ward@5 — legal. |
| E6 | **A Preserved die is never a legal Break target** | **GUARD VERIFIED, FEATURE ABSENT.** All three shapes the guard reads (`d._preserved`, `G._famPreserve.die`, `G._famPreserve.lane`) are excluded from `_breakBegin`'s outline and click handlers and refused by `_breakDie` (matchDice stays 6, turnPts 0). Control die with no flag dies normally. `_breakBegin` returns false when every other die is guarded. **But the shipped file contains 0 assignments to `_preserved`, and both `_famPreserve` literals are `{val,pts,crack}` — no die, no lane.** Vacuously true, exactly as the brief's own note predicted. |
| E7 | **Zero Hour ends the turn on any icon keep, no hot-dice exception** | **PASS.** All seven icons each banked exactly 0 and set `G._zeroHourEnds`. No badge → no end. In the **live** `handleRoll`: `_zeroHourClose()` at char 15595, `G._lastHotDice=true` at 16101 — zero hour first. Behaviourally, with the whole row committed (the hot-dice condition), `_zeroHourClose()` returned true, hot dice were **not** awarded, `_rollLocked` set. `handleBank` carries the same call. |

### The seven Break family rows — PASS, no cross-contamination

| Family | Verb fired | Anything else? |
|---|---|---|
| obsidian | +1000, one kept row `obsidian:1000` | nothing |
| amber | `_bustImmuneTurn` only | nothing |
| starstone | `_extraTurn` 0→1 only | nothing |
| silver | `_breakBankNow` written true | nothing |
| jade | exactly 3 real `_rollD` calls on the 3 free dice, 0 points | nothing |
| vagabond | +450 to player, `G.oPts` 1200→750 | nothing |
| bone / iron / flint / lead | no verb, 0 points | nothing |

**Jade never paid obsidian's 1000.** Silver's row required a recording accessor
on `G._breakBankNow` because `_breakDie` consumes and clears it before returning;
jade's was distinguished by spying on `window._rollD`.

### Ruling #24 — the Silver:bone bust ratio is NOT policy-invariant

Roll tables read off the game: bone 2/6 scoring faces, silver `[1,5,1,5,2,3,4,6]`
4/8 — single-die ratio 0.75, falling as die count rises.

- At the policy that reproduces the brief's own bone figure (bone **52.18%
  [51.56, 52.79]** of turns busted, brief quotes ~49–50%): silver **29.81%
  [29.24, 30.38]** (brief quotes ~26%), ratio **0.571 [0.559, 0.584]** — inside
  the ruled 0.54–0.58 band. n=25,000 turns/side. **The ruling holds there.**
- Swept across **17 policy cells** at n=20,000–25,000 each, the ratio runs
  **0.126 → 0.864**, monotone in how deep the turn pushes: "bank at ≤4 free dice"
  0.126; "≤2" 0.308; "≤1" 0.517; leanest-keep "≤1" 0.584; "roll while turn<2500"
  0.844.
- **In matches actually played** (Bea, tier 3, n=250 matches/side, 1,875 bone
  turns / 1,749 silver turns): bone **16.59% [14.97, 18.34]**, silver **3.89%
  [3.08, 4.90]**, ratio **0.234 [0.182, 0.303]** — silver is roughly **twice as
  protective** as the ruling states. Same tier, same agent: silver's match win
  rate 54.4% vs bone's 26.8%.

### Lens 3 findings

| Sev | Finding |
|---|---|
| **major** | **The SHARED harness cannot put a Trade brand on a die.** `tools/sim_harness.js:249` writes `S.run._enchV=3;S.run._enchTradeV=2;`. The shipped `_enchInit` legacy-Trade migration fires on `_enchTradeV!==1`, nulls every `{t:'trade'}` and refunds 350g — and `newG` calls `_enchInit()` unconditionally (`fark_proto.html:21536`) right after `buildLoadout`. Every Trade measurement made with the shared harness — including anything using `FSIM.GEAR.night8`, which lists `trade` — measured an **empty lane** and an inflated gold curve. **Fix: write 1, not 2.** |
| **major** | **Still Waters is not a hard counter to Break+Obsidian.** `_famHushed(d)` returns `!!(d && d.ench && _stillWaters())` — a *plain* die keeps its family by construction, and Break needs only ONE branded die anywhere in the loadout. So the cheapest build (Break on one die, plain Obsidian everywhere else) pays in full **with the badge worn**. 200 driven breaks/arm: all-branded → 1000 without badge, 0 with; **Break-die-only-branded → 1000 both with and without**. Passive path: all-six-branded 0.685 → 0.000 shatters/turn; one-branded 0.520 → 0.445, a 14% dent rather than a shutdown. FARK_ENCHANT_BADGE_REWORK §3 states the opposite as an intentional design outcome. |
| **major** | **Ruling #24's Silver ratio is not a policy-invariant regression target** (0.126–0.864 across policies; 0.234 in matches actually played). |
| minor | **Zero Hour is the only one of the three rescoped badges that does nothing when SLEEVED into a boss match.** `_iconFire` reads `G._tell.id==='last_call'` directly instead of `_ruleActive`, and in a boss match `G._tell` is the boss's own tell. Sleeved Still Waters and sleeved Kindred both bind. The file's own comment above `_RETIRED_RULES` (~line 10865) already names this. |
| note | Break on Grog's Tooth pays the **Obsidian row's flat +1000**, never the Tooth's own 10%/+1500 — `BREAK_TRIGGERS` dispatches on `_matFam`, and `_RELIC_FAM` maps `grogs_tooth`→`obsidian`. The brief asks for the Tooth's magnitude under Still Waters; the guaranteed path has no distinct magnitude to measure. |
| note | When a Break shifts lane indices under a live Trade, `_tradeRestore` returns the borrowed die's *material* via the `t.cnt` fallback but not the player's brand to `_enchArr` (guarded deliberately at `fark_proto.html:17303-17306`). No consequence today. |
| note | The one-Ward cap lives entirely in purchase/migration paths, not in the die data — two `brutus_shield` dice produce two born Wards. Not reachable today (absent from `DICE_STORE`, exactly one Brutus seat) but there is no last-line defence. |
| note | `_faceAltered`'s jade-wild-6 clause is unreachable dead code — it returns true only for face 6, and `_iconFaces` has already filtered to {1,5}. The restriction is enforced by 1/5 alone. |

---

# LENS 4 — NO CHEAT AROUND POSSIBLE

> **VERDICT: FAIL.** The brief's own acceptance test — *"Scavenger's win
> rate/value-per-turn should NOT be a dramatic outlier next to Bea/Otto"* — fails
> outright. Six plain bone dice, one Amber die in the stash, the Fair Trade card
> and one Break brand wins every match in one turn at **zero die cost**, beating
> the honest skill ceiling by 2.04× off a starting-tier loadout.

Method: seed 20260731. Files `tools/sim_scav_a.js` … `sim_scav_f.js`. Two match
loops were used: `FSIM.simMatch` for the roster comparison, and a private loop
(`sim_scav_d/e/f`) that reproduces the **shipped** `endPTurn` behaviour where an
extra turn returns before `turnNum++`/`pTurns++`, because `FSIM.simMatch` counts
extra turns against the cap and the game does not.

### The outlier

| Build | Win % | Value/turn | Turns/match | Dice at end |
|---|---|---|---|---|
| **SCAVENGER** (6 bone + stash amber + Fair Trade + 1 Break), n=500 patron | **100% [99.2, 100]** | **6,983 [6,918, 7,047]** | **1.02** | **6.00** |
| Same chain vs a tier-3 BOSS, n=300 | **99.7% [98.1, 99.9]** | 9,418 [9,304, 9,532] | 1.05 | — |
| Its own control (identical build, no lend/break), n=500 | 34.4% [30.4, 38.7] | 634 [609, 659] | 7.44 | — |
| ORACLE OTTO, honest, fully-built night-8, n=700 | 100% | 3,420 [3,274, 3,566] | — | — |
| BALANCED BEA, night-8 | 86.7% [84.0, 89.0] | 1,106 [1,072, 1,140] | — | — |
| BALANCED BEA, night-4 | 25.5% | 593 | — | — |

**Scavenger is 2.04× Otto's fully-built honest ceiling, from a starting-tier
loadout. The intervals are ~30× apart. This is not noise.**

### The four mechanisms

**1. Amber's Break row is unbounded** (`sim_scav_c.js` C2, `sim_scav_e.js` E2):

| Pushed turn | Plain | Amber-immune |
|---|---|---|
| stop at 1,000 (n=400) | 107 banked [74, 141], bust 90.8%, reached 9.3% | 1,074 [1,051, 1,096], bust 1.75%, reached 98.3% |
| stop at 5,000 (n=400) | **0 banked, bust 100%, reached 0/400** | 5,065 [4,997, 5,134], bust 1.75%, reached 98.3%, 37.0 rolls |
| stop at 20,000 (n=200) | — | **98.5% [95.7, 99.5] still running at the 60-roll guard** |

Match level, 5 bone + 1 amber, no enchants, no badge (n=600): no Break 35.7%
[31.9, 39.6]; Break the amber on turn 1 → **98.7% [97.4, 99.3]**, 6,660/turn,
1.18 turns/match, 0.05 busts. Boss (n=300): 37.7% → **98.0% [95.7, 99.1]**.

*The other rows behave exactly as §4 predicts*: obsidian Break on turn 1 is 16.8%
[14.1, 20.0] vs 28.5% no-break; starstone 10.8% [8.6, 13.6] vs 79.3%. **Five of
seven rows are fine. Amber is the one.**

**2. Fair Trade → Break costs no die** (`sim_scav_b.js` B1, `sim_scav_f.js` F2):
break your own obsidian → +1000, matchDice 5, numDice 5. Fair-Trade one in from
the stash and break *that* → +1000, **matchDice 6, numDice 6**, next roll builds
6, run stash still holds it. n=500 each, both arms firing Break ~0.95×/match:
borrow-and-break **48.6% [44.2, 53.0]**, 782/turn, 6.00 dice, 1.26 busts;
break-your-own **15.2% [12.3, 18.6]**, 504/turn, 5.00 dice, 2.99 busts. On top of
ORACLE OTTO with a full exploit build the lend lever is worth **+318 value/turn**
(2,279 [2,202, 2,357] vs 1,962 [1,897, 2,026], n=700, disjoint).

**3. Vagabond re-steals the same bank** (`sim_scav_c.js` C1): `G._oLastBank` is
read and applied but never zeroed. Opponent on 3,000 with `_oLastBank`=900 —
break #1: player +900, opponent 2,100, `_oLastBank` **still 900**; break #2:
player +1,800, opponent 1,200, `_oLastBank` **still 900**. A 3,600-point swing
from one 900-point opponent turn. In played matches (3 vagabond + 3 Break, n=300):
339 fires, **176 (51.9%) on an already-stolen bank**, mean 721 points each.

**4. Starstone's extra turn escapes the cap** (`sim_scav_b.js` B4): `endPTurn`'s
`G._extraTurn` branch returns **before** `G.turnNum++` and `G.pTurns++`; the cap
gate reads `G.pTurns` and `famQuicksilver` gates on `G._qsTurn===G.turnNum`.
Control: pTurns 3→4, turnNum 3→4. With `_extraTurn=1`: pTurns 3→3, turnNum 3→3.
Six consecutive fire+endPTurn cycles left both at 0 every time. Five fires queue
five extra turns. **Falling Star's own extra turn sits AFTER the increment — the
two mechanics disagree, which is exactly the mismatch ruling #9 ruled against.**

### What held (all PASS — stated so they are not re-litigated)

- **1/5 brand restriction:** 24 materials × 3,000 shop draws = **72,000 draws,
  zero faces outside {1,5}**. Forged 2/3/4/6 pushed straight into
  `_gbEnchantApply` all refused with 0g charged; 1 and 5 landed for 150g.
- **One-Ward loadout cap:** held through a second sale on all five other lanes
  (0g spent, 0 landed), through stash-then-buy, through equip-back, and through
  the harness build. Relic after a bought Ward refunds 350g, leaves exactly one.
- **Kindred's doubling whitelist is exactly ruling #32** — tithe/ward/snare/
  snuff/fog true, break/trade false, no mismatches. Fired one at a time with
  Kindred live: Tithe 30g, Ward boost armed, Snare ×2, Snuff turns=2, Fog turns=2,
  Break/Trade unchanged. Tithe gold **18.83/turn [18.19, 19.47] → 37.66 [36.38,
  38.95]**, an exact 2.00×, n=300 each. **No guessed defaults found** — the open
  item is answered as ruled, not improvised. Re-firing Snuff/Fog/Snare before the
  rival moves does not stack the window.
- **Trade is match-scoped and clean:** run loadout and run brand array untouched
  after a fire; a Break below the traded lane shifts the index and `_tradeRestore`
  still repairs both sides bit-for-bit; **`S.run.dice` was `['bone'×6]` across all
  60 consecutive matches**. Self-consuming confirmed. "Acquire their enchanted
  die" is unreachable by construction — no opponent-side enchant exists.
- **Preserve vs Break:** the guard works, but nothing in the page ever assigns
  `_preserved` and `G._famPreserve` is `{val,pts,crack}`. Vacuously true.

### Lens 4 findings

| Sev | Finding |
|---|---|
| **blocker** | Amber's Break death-trigger makes the rest of the turn permanently bust-proof — the turn ends only when the player chooses to bank. |
| **blocker** | Fair Trade + Break on the same die costs no die at all. The implementation matches ruling #2/§4b exactly; the ruling is the hole. |
| **blocker** | The full chain wins 500/500 patron and 299/300 boss matches in ~1 turn at 2.04× the honest ceiling. |
| major | Vagabond's Break row pays out repeatedly on the same opponent bank (`_oLastBank` never zeroed). |
| major | Starstone's extra turn is invisible to the turn cap and to Quicksilver, violating both halves of ruling #9; extra turns stack without limit. |
| minor | The one-Ward cap has no enforcement against BORN wards (latent — no shipped path to a second relic). |
| minor | Harness defect other agents need: `FSIM.buildLoadout` sets `_enchTradeV=2` (independently confirmed by Lens 3). |
| note | 1/5 restriction, purchased-Ward cap, Kindred whitelist and Trade match-scoping all held under every attack constructed. |

---

# ACCEPTANCE TARGETS — measured against, decision required

The brief's targets were validated against a **pre-rework** build. Per the
brief's own instruction, these are stated as decisions, not pass/fail.

| Target | Band | Measured | In band? | Decision |
|---|---|---|---|---|
| **Patron win at intended gear** | 60–70% | **76.1–96.8%** (Bea, night-8 as specced, tiers 0–7); **98.4–99.0%** with brands removed; **100%** for Otto; **99.3%** against the loadout runs actually reach | **NO — high by 6 to 29 points** | The system, not the target. The band is met *somewhere in the middle of the run* (night-1 gear at tiers 1–2 is 41.9–52.8%), but "intended gear" as specced is unaffordable and, when reached, is not a fight. Fixing the blockers above will move this number a long way on its own; re-measure before touching the band. |
| **Boss win at intended gear** | 45–55% | **73.1–90.7%** across all eight bosses, night-8 as specced (Grog 90.7, Ambrose 78.3 [74.1, 82.0]) | **NO — high by 18 to 36 points** | Same call. Ambrose at 78.3% is the structurally load-bearing final boss, and even he is not close. Note Otto goes **450/450 at tier 5** — zero losses in 450 matches. |
| **Median banked turns per side** | 5–7 | **NOT DIRECTLY MEASURED as a median.** Nearest evidence: honest near-starting play runs **7.44 turns/match** (Lens 4 control, n=500); under any of the four blockers it collapses to **1.02–1.26** | **PARTIAL / BLOCKED** | Honest play sits at the top edge of the band or just outside it; the exploited arms are an order of magnitude below it. This needs a dedicated pass reporting a real median with an interval — nobody measured it as specified. |
| **Full-run win rate, competent build-focused player** | 25–35% | **52.0% [45.8, 58.1]** (dice-first shopper); **35.2% [29.5, 41.3]** (brands-first shopper), 250 runs each | **NO for dice-first (high by 17 pts); top-edge for brands-first** | Low confidence in both — the run loop lets a boss be re-challenged while hearts last and the family-card model is crude, both of which inflate the number. Treat 52% as an upper bound on a structurally generous loop, not as the run win rate. This is the number most in need of a second, stricter pass. |

**Summary of the decision:** three of the four bands are overshot, and the fourth
was not measured to spec. But the overshoot is not evidence that the targets are
stale — it is what you would expect from a build carrying two dominant strategies
(the sweep, Starstone) and two runaway combos (Amber-Break, Fair-Trade-Break). The
honest recommendation is: **fix the five blockers first, re-measure, and only then
decide whether the bands need moving.** Re-tuning targets against a build with
these holes in it would bake the holes into the spec.

---

# CROSS-LENS AGREEMENTS AND ONE OPEN CONFLICT

Findings that two independent agents reached separately carry more weight than
either alone. Recorded here so they are not treated as single-source.

**Independently confirmed by two lenses:**

- **The `FSIM.buildLoadout` Trade defect** (`_enchTradeV=2` re-arms the shipped
  legacy migration, deleting every Trade brand and refunding 350g). Found by
  Lens 3 and Lens 4 separately, same root cause, same fix. **Every Trade number
  produced by the shared harness before this fix measured an empty lane.**
  Lens 4 adds that it is *order-dependent* — a spec whose ward sits before its
  trade happens to disarm the migration harmlessly, which is why
  `FSIM.GEAR.night8` survives and a trade-only build does not.
- **Preserve is vacuously true** — the guard works, nothing ever sets the flag.
  Lens 3 and Lens 4, same conclusion from different probes.
- **The two-born-Ward gap is latent but real** — `_enchInit`'s cap pass only
  strips *purchased* wards. Lens 3 and Lens 4 agree it is unreachable today.
- **Break is the most expensive brand for honest play** — Lens 1 (D1: carl
  45.8→21.0, ned 20.8→5.5) and Lens 2 (−29.0 [−33.1, −24.9] isolated) agree.
- **The Break timing read pays** — Lens 1 (Greg, −6.40 [−9.13, −3.65]) and Lens 2
  (Bea + one rule, +22.3 [+18.7, +26.0]) agree in direction and both show the
  unbranded control at exactly zero difference.
- **Four badges are invisible to the harness, not proven inert** — Lens 1 and
  Lens 2 name the same four and the same cause.

**One open conflict, stated rather than reconciled:**

Lens 1 measures **every** functioning brand costing carl and ned 9–25 points on a
2-brand fixed base at tier 3 (ward −8.8, snuff −15.3, snare −15.8, fog −18.3,
tithe −18.5, break −24.8 for carl). Lens 2 measures only **Break** as materially
costly on night-8 dice at tier 5 (−29.0), with every other brand between −3.3 and
−0.8 and most straddling zero. Both are paired or well-powered; they disagree
about whether the non-Break brands are a real tax or noise.

The designs differ in base dice, agent, tier and brand count, any of which could
explain it — most plausibly that Lens 1's base is weak enough that forfeiting a
scoring face matters, while Lens 2's night-8 dice score so hard that one dead face
is absorbed. **This is not resolved. Do not price the brands off either number
until a single crossed design settles it.** What both agree on unambiguously:
Break is expensive, and no brand is a *gain* for a humanlike agent.

---

# WHAT THIS DOES NOT ESTABLISH

Every uncertainty from all four lenses, collected. Read this before quoting any
number above.

### Harness gaps — things measured as zero that are not proven zero

1. **Four of eight badges were never exercised.** Steeped, Pickpocket, Drill Order
   and In Arrears / First Strike returned bit-identical results with **zero
   discordant pairs**. Their player-side hooks live inside `_afterRollImpl`
   (`fark_proto.html` ~23520 steeped, ~23549/21958 drill_order, ~23551 pickpocket)
   and inside the roll-button lock, and the harness re-creates that function's
   control flow rather than calling it. **Do NOT read "0.0" as "inert in the
   game".** Only Kindred, Still Waters, Zero Hour and Reckoning were genuinely
   measured. Closing this needs a harness extension nobody has written.
2. **Quicksilver's 0.0 is unmeasured, not worthless.** Its free solo reroll needs
   a driver the harness does not have. It measured byte-identical to no enchant
   *by construction*.
3. **Interactive card actives never fire.** The family-card layer's +29 points is
   therefore a **floor**, which makes the "cards, not brands, carry the
   escalation" finding stronger, not weaker.
4. **The turn loop is the harness's, not the game's.** `handleRoll` /
   `_afterRollImpl` are animation-driven and FSIM re-creates their control flow.
   So "the Amber-immune turn never ends" is read off the shipped `doBust` plus 800
   measured turns plus the 60-roll guard data — it is an inference from source, not
   a measurement of the live UI. Drill Order's per-turn roll allowance would cap
   it; nothing else found would.
5. **The opponent turn loop is also harness code**, so Snuff/Fog/Snare's real bite
   is not measured — only their armed state, which is real. Nothing in any
   headline depends on them.
6. **The sweep was executed through `FSIM.legalKeeps`.** The shipped accept rule
   (`fark_proto.html:23252-23254`) was read line by line and reproduced against the
   real `scoreSelection` in study H, and the harness copy is character-equivalent
   modulo the Anchor card (not in play) — **but the shipped `handleRoll` DOM path
   was not driven end to end.** A human confirming "tap all six with one brand
   showing, press ROLL" would close the last gap. *This is the single most
   valuable five-minute check anyone can run on this report.*
7. **The Fair Trade CARD was never played** (it needs a tap). "A brand belongs to
   the die, never the seat" is verified for the Trade **enchant** only. The card is
   a separate code path (`_ftLendDied` / `startPTurn`'s expiry block).
8. **Zero Hour's 700ms close is read synchronously.** The hot-dice ordering was
   established from live function source plus a behavioural `_zeroHourClose` check,
   not by tapping a real commit.

### Modelled rather than driven

9. **The draft/shop offer cadence is invented** (4 visits, 3 dice + 3 enchants
   each, 2000g). Real prices and real legality guards, but **Break was never
   offered in the shared shop, so no agent drafted it.** Build-effect *magnitudes*
   in Lens 1 study C are budget- and offer-specific; the *ordering* (starstone
   first) is not — D1/D2 confirm it independently on hand-built loadouts.
10. **The gold award is modelled, not called** — `endMatch` is an animation chain,
    so patron win = `20 + tier*12 + buy-in` and boss win = `RUNGS[tier].gold` are
    reproduced from the shipped source (~27564 / ~27612), as is `draftSkip`'s
    `5 + tier*5`. Tithe's income is real. Bounties are dead code (handicap-gated).
11. **The card draft in the run loop is modelled** — equip a random live
    non-unique passive family card at tier 1 until three are held, then skip for
    gold. Tier upgrades, boss spoils and active cards are not modelled, so the
    sim's build is **weaker** than a real one's.
12. **The run-clear rate (35–52%) is not a run-win-rate answer.** The loop lets a
    boss be re-challenged while hearts last and the card model is crude. It is
    reported only as the substrate the gold curve sits on.

### Scope limits on specific numbers

13. **Lens 1 reports no run-level number at all** — everything there is a single
    patron match, mostly tier 3. Do not read any Lens 1 figure as a run win rate.
14. **Greg's absolute win rates are largely his policy, not the game.** The shared
    harness's Greg uses `leanest` keep + a 1000 threshold and busts 76–90% of
    turns. The naive-vs-informed *comparison* is clean (the control proves the
    Break filter is their only difference), but do not read greg 12.35% as "the
    gambler archetype's win rate".
15. **Agent-effect sd (20.6) exceeding build-effect sd (14.9) is
    budget-conditional** — at 2000g the top build is reachable by everyone, so the
    cross under-states build spread relative to a run where gold is scarce.
16. **Night-8 is one spec, not the spec.** `FSIM.GEAR.night8` was used verbatim so
    the numbers sit beside the harness author's. The realised-build comparison
    (`sim_power_f.js`) covers what runs actually reach.
17. **The Silver ratio figures** are per-turn bust rates from a bare six-die hand
    with no cards and no match around it, plus one 250-match batch under one agent
    at one tier. The real-match figure (0.234) is a single agent's number — a
    different bank policy moves it, which is exactly the finding.
18. **The Break-row checks have no confidence intervals** — they are deterministic
    single-fire observations, repeated once each. Cross-contamination could in
    principle be probabilistic in a path not exercised (e.g. a row firing
    differently when the pool is empty).
19. **The 45-point original finding is not directly comparable.** That figure came
    from a pre-rework build with a different harness; the execution/build
    decomposition here is a different cut (fixed-build spread vs crossed design)
    and should be read as a fresh measurement, not a regression.
20. **Break's forced firing in Lens 4's E2/F1** measures what one Break is *worth*,
    not how often you get one. Natural rate measured separately: three Break brands
    fired 1.42 icons/match, so one brand is roughly 0.5 fires/match. One fire wins
    the match, so the gate is soft — but the honest statement is "roughly every
    other match", not "every match".
21. **`sim_scav_e.js`'s E4 block is VOID** — its Fair-Trade charge counter was
    never reset per match, so its lend arm is really a no-break control (0.005
    breaks/match). `sim_scav_f.js` F2 is the corrected version; use that.
22. **`sim_power_e.js` is superseded by `sim_power_f.js`.** Lens 2's author found a
    defect in their own first pass — `FSIM.setupMatch` rebuilds its options object
    before calling `buildLoadout`, dropping a private flag, so `FSIM.mkEnch`
    wrapped each purchased ench as `{t:{...}}`, which `_isIcon` rejects; every
    brand in the first run loop was silently inert. `sim_power_f.js` detects the
    path by shape and carries a `titheLive` assertion so it cannot recur unnoticed.
    **Reported rather than quietly fixed.**
23. **Lens 3's Trade results depend on a harness patch made in its own files**
    (setting `_enchTradeV=1`, i.e. "this save is already migrated"). If the intended
    harness state is genuinely a *pre-migration* save, those Trade numbers describe
    a state the shared harness never produces.

### Explicitly not tested by anyone

24. **Run-level economics beyond the gold curve**, fleeing / force-quit
    exploitation, mirror matches, and resume-from-snapshot paths. Tithe writes
    `S.run.gold` and `save()`s mid-match, so gold earned is irreversible even on a
    loss — **nobody tested whether that is farmable by abandoning matches.**
25. **Whether a Snare mark can persist into a second opposing turn** — on the
    brief's checklist, not in any of the seven checks run. The opponent loop is
    harness code, so a Snare-window result from it would not be trustworthy without
    driving `runOppTurn` itself.
26. **Whether two `brutus_shield` dice can be obtained** — For Keeps, mirror
    matches and resume paths were not audited for a second award.
27. **The power level of the five unvalidated Break rows** (open item 5.4). Each
    was verified to fire its own verb and only its own verb; whether +1 extra turn,
    bust-immunity or a Jade scatter are correctly *sized* is a separate question —
    and Lens 4 answers half of it by accident: **Amber's is not.** The Jade row is
    worth nothing measurable (the shipped comment says the scatter is immediately
    overwritten by the roll it interrupted).
28. **Whether real players find the Break timing read.** That is a playtest
    question, not a sim one.

---

# REPRODUCTION

From the worktree root
`C:/Users/Rigam/OneDrive/Documents/Work/Gambit/.claude/worktrees/zen-chatterjee-f04c42`,
with the dev server on :8084:

```
node tools/sim_run.js tools/<file>.js --seed 20260731
```

| Lens | Files (all under `tools/`) |
|---|---|
| 1 — Fun | `sim_fun_draft.js`, `sim_fun_a.js`, `sim_fun_bc.js` (+`_full`, `_n`), `sim_fun_d1.js` (+`_full`), `sim_fun_d2.js`, `sim_fun_e.js`, `sim_fun_f.js`, `sim_fun_g.js`, `sim_fun_h.js`, `sim_fun_summary.js`, `sim_fun_show_e.js` |
| 2 — Power | `sim_power_probe.js`, `sim_power_a.js`, `sim_power_b.js`, `sim_power_c.js`, `sim_power_d.js`, `sim_power_e.js` *(superseded)*, `sim_power_f.js`, `sim_power_g.js` |
| 3 — Elegance | `sim_l3_probe.js`, `sim_l3_elegance.js`, `sim_l3_elegance2.js`, `sim_l3_elegance3.js`, `sim_l3_elegance4.js` |
| 4 — No-cheat | `sim_scav_a.js`, `sim_scav_b.js`, `sim_scav_c.js`, `sim_scav_d.js`, `sim_scav_e.js` *(E4 void)*, `sim_scav_f.js` |

**Before re-running anything Trade-related:** fix `tools/sim_harness.js:249` —
`S.run._enchTradeV` must be `1`, not `2`.

---

# SUGGESTED ORDER OF WORK

Not asked for, but the report is not actionable without it. Ordered by
effect size per unit of work, blockers first.

1. **`fark_proto.html:23253`** — the sweep. An illegal selection containing an
   icon should stay illegal; only the icon's *own* contribution should be zeroed.
   Worth ~80 win-rate points on its own.
2. **`doBust`** — clear `G._bustImmuneTurn` on the success path, or scope Amber's
   row to a fixed number of rolls. Currently one Break ends the match.
3. **Ruling #2 / `_removeDieAt`'s Fair-Trade branch** — this is a *design*
   decision, not a code bug. The ruling says breaking a borrowed die costs one die;
   the code delivers that by returning the lender's own die, which means the
   *borrowed* die's death costs nothing that match. Either the lender's die also
   goes, or Break cannot target a loaned die.
4. **`fark_proto.html:25452`** — Starstone's +500 is unconditional and per-die on
   every bank. Gate it, cap it, or price it.
5. **`G._oLastBank`** — zero it after Vagabond's row reads it.
6. **`endPTurn`** — move the `_extraTurn` branch after `turnNum++`/`pTurns++`, per
   ruling #9's explicit "align to Falling Star's ordering".
7. **`tools/sim_harness.js:249`** — `_enchTradeV = 1`. Cheap, and every future
   Trade measurement depends on it.
8. Then re-measure the acceptance bands. Not before.
