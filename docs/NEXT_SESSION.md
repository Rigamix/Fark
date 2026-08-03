# Handover — start here

Written before a context compaction. Everything needed to pick up cleanly.

**Deployed HEAD: `2c127cd` on branch `fark`. Backup tag: `pre-effect-system`
(`a0aed7d`) — the last commit before the plan work began.**

---

## 1. THE NEXT TASK — Denis's call on the effect re-plan

**Effect Phase 1 is done** (`1850e3c`) and it re-scopes two later phases, which
is a call for Denis, not for me. Full report in `docs/PHASE_REPORTS.md`, map in
`docs/EFFECT_INVENTORY.md`.

The three changes it recommends:

1. **Phase 3 loses the multiplier decision** — Kindred is not a multiplier, its
   "double" means something structurally different for each of five enchants, so
   there is nothing to multiply and nothing that will be. Phase 3 should settle
   **effect lifetime** instead: four enchants are lane markers with a placement,
   a window and an expiry, and the plan's vocabulary cannot express that.
2. **Phase 4's first group is wrong** — it says enchants first, but four of the
   seven are lifetime-markers and one is a permission, so that is the HARDEST
   group, not the easiest. The 20 cards already on `CFX` are the honest start.
3. **A group the plan does not list**: nine live cards are hardcoded at call
   sites with no `CFX` entry (`bloom`, `cultivate`, `vanguard_f`, `for_keeps`,
   the five tavern cards). A migration enumerating the effect table cannot see
   them.

**If Denis approves, the next build step is Phase 2** — shared conditions and
queries — on the re-scoped shape.

**Then write the Phase report** — one after every phase, in
`docs/PHASE_REPORTS.md`, same fixed format.

---

## 1c. HOW FAR ALONG — say it in units, never as one number

Two strands, two different questions. **Do not blend them and do not put two
percentages next to each other** — a table of percentages is what produced a
blended "70%" that matched none of its own rows.

> **85% of the behaviour is built. 0% of the shared machinery that behaviour
> runs on.**

- **Behaviour** — the enchant/badge rework's own §6 checklist: Silver reworked,
  Ward/Insurance retired, three enchants cut, seven icon enchants firing through
  one rule, Break's death rows, four badge remaps, the face restriction, the
  feat roster. Enumerable, mostly shipped, **~20% validated** — only Obsidian's
  Break row has sim numbers and almost nothing has been played.
- **Machinery** — the effect system. 1 of 5 phases (inventory only). `CFX`
  routes 20 of 29 cards, but routing is not the problem: there is **no shared
  condition layer and no shared effect application**, and that is where every
  bug this rework exists to stop actually happened.

**Denominators:** 69 items exist, ~65 are player-reachable. Totality assertions
use 69; migration progress uses 65. See `EFFECT_INVENTORY.md` §1.

---

## 2. AFTER THAT

- Fix the two remaining Phase 2 reds: relic `.dtype-` blocks (8), and `MATCOL`'s
  4 missing materials. **Still not reachable — but not for the reason I first
  gave.** I said migration converts them on load before any render. The real
  reason, measured: `brass` and `crystal` are handed out only by
  `generateDiceLoadout`, which is called only by `initBossRewardScreen`, and
  **nothing calls `showScreen('bossreward')`** — that screen has no entry point.
  The conclusion held; the justification did not, and a right answer resting on
  a wrong reason breaks silently the moment someone wires that screen back up.
- **The two stale asset paths** Phase 5 named and did not touch:
  `Environment_ART/gameover.png` (its only twin is a `.psd`) and
  `Menu_Art/Settings.png` (twin at `Art/Assets/Panels/Settings/settings.png`).
  Swapping them is a look change, so it's Denis's call.
- **`assets/` has no owner.** 47 live dependencies with no replacement in the
  current tree — every font, all audio, nine character portraits, eight match
  frames, the Night_Art UI set. Whether those get redrawn is an art decision
  nobody has made.

---

## 1b. DONE — the feat roster migration (`d6772fc`)

Ruled, built, deployed. `FEAT_ART` is **23/23**, measured both directions.
Full write-up in `docs/PHASE_REPORTS.md` Phase 4; `archive/FEAT_DISCREPANCIES.md` now
carries a correction header.

**What it turned up that the discrepancy doc had missed:** there were **four**
rosters, not two. `_famFeats` was granting five feats with no art — invisible,
forever — and `FTEXT` held twelve authored descriptions that outranked the live
condition on the wall. Also `first_blood` awarded for the first **match** of a
run rather than the first **boss**, so its painting hung for beating a drunk.

**All five decisions ruled**, one changed code (`37eff42`): STICKY FINGERS
moved off amber and back to **Vagabond's break-row steal** — the name is a
thief, not something that holds. NO CLAIM shipped as written. The
Death&Taxes / Own the Night overlap stands. Bookkeeper's painting stays unused.

**One is settled only halfway and is worth carrying forward.** The early-run
drip-feed: ruled that **nothing goes back into the feat list** — that would be
the same drift this migration removed. But the underlying tension (design law
says feats are rare and never for sale; prior playtest feedback said
progression was too slow) is unresolved, and the answer, if there is one,
belongs in circles / gold / first-badge progress, not in loosening feat
scarcity.

**And the parse gate was not gating.** Its default argument pointed at an
untracked scratch build frozen since 31 July, so every bare invocation reported
PASS on a file none of the session's patches touched. Fixed in `37eff42` —
default is the game, missing file exits 1, and the file read is printed with
its mtime. Nothing was damaged; the live file compiles clean.

---

## 3. BLOCKED ON DENIS

**Nothing blocks the next task.** All four items that used to sit here were
answered and are now built — the enchant/badge brief arrived, Zero Hour went to
Mabel, Last Call was retuned to 800, boss counters and greetings are per-run.
See Phase 4b in `docs/PHASE_REPORTS.md`.

What is genuinely open, none of it blocking:

1. **The early-run drip-feed.** Ruled that nothing goes back into the feat list.
   Where the early signal comes from instead is unresolved — the proposal is
   that dialogue beats (greeting tiers, first backstory unlocks, the King
   thread's intro) already do that job, flagged as needing a real playtest
   reaction rather than reasoning.
2. **The two stale asset paths** and **`assets/` having no owner** — see §2.
3. **Three recycled ids are gone, but the pattern isn't.** All eight badge ids
   now match their rules. The thing to keep in mind: a `_RETIRED_RULES` entry
   naming an old rule silently kills the NEW rule wearing its id, everywhere
   except the boss's own badge. That table is empty now. Keep it that way unless
   the replacement genuinely does not exist yet.
4. **Numbers that are unplayed:** Last Call's 800, and most of the restored feat
   conditions. They read real state and the wall renders, but only HIGH ROLLER
   has fired through a live match.

---

## 4. GOTCHAS THAT COST TIME TODAY — do not relearn these

**Deploy:** commit in the worktree → `cd` to root → `git merge --ff-only
claude/zen-chatterjee-f04c42` → `git push origin fark`. If the merge aborts on
untracked files, hash-compare them first (`git hash-object` vs `git rev-parse
BRANCH:path`), then remove and re-merge. **Never push to `main`.**

**Never `git add -A`.** Denis generates art into `Art/` mid-session. Stage
explicit paths only.

**USE `FK_ART`. It is the answer to "where does X live", and it exists because
this exact question kept being answered wrong.** One table near the top of the
script: 21 entries, both trees, with the old-tree ones marked deliberate. Add to
it rather than writing a raw path — `apv_asset_registry` fetches every entry, so
a rotted one fails on the next run.

**`assets/` is NOT dead**, and the flat rule I wrote here myself was wrong.
Measured: 47 live references into it have **no replacement anywhere** in the
current tree — every font, all audio, nine character portraits, eight match
frames, the Night_Art UI set. `'JMH Beda'` loads from
`assets/_mockups/new_main/`. "Never look in `assets/`" would break the page.

The true rule is narrower: **new art goes in `Art/Assets/`.** The three mistakes
that produced the flat rule (font, coin, diamond) were about *art*, not the
folder. `--font-px` is still the old pixel font and still the wrong reach —
`FK_ART.font` is the right one.

**Patches with backslashes go through a Write-tool `.py` file, never a bash
heredoc.** Heredocs mangled a regex twice.

**Run the parse gate after every edit:** `node tools/zv_trade_parsegate.js`. It
now prints the file it read and its mtime — **look at that line.** Its default
used to be an untracked scratch build and it passed vacuously for a whole
session. A gate that cannot fail is worse than no gate, because it is credited.

**Run probes through `node tools/run_probes.js`, never `shoot.js` directly** —
the runner has the pre-flight. The dev server dies often; when it does, every
probe "fails" identically. Restart with `preview_start` name `gambit-worktree`
(port 8084).

**Never write `/*` or `*/` inside a CSS comment in `fark_proto.html`.** CSS
comments don't nest; a close-marker inside a sentence *about* markers ends the
block early and error-recovery eats the **next rule**. This cost four rounds on
the patron busts, then bit again in the comment explaining it.

**Verify computed, never authored** — and recursively. Written CSS is not live
CSS; check the CSSOM. A feature test must perform the operation and measure the
result, never read a property back. I broke this rule three times on the FEAT_ART
question alone before counting the folder.

---

## 5. STATE

- **Suite:** 17 probes — 16 pass, 1 fail carrying two known reds (`MATCOL`'s
  retired materials, relic `.dtype-`). Baseline in `tools/probe_baseline.json`,
  re-recorded at `31adddd`. Full run ≈ 12–18 min.
- **Phases done:** 1 (runner), 2 (totality), 3 (CSS live), 4 (feat roster),
  4b (badge remap), 5 (asset registry). Reports in `docs/PHASE_REPORTS.md`.
- **Deployed HEAD is `31adddd` on `fark`** — the header at the top of this file
  names the older one; this line is the current truth.
- **Plans:** `docs/EFFECT_SYSTEM_PLAN.md`, `docs/VISUAL_INTEGRITY_PLAN.md`.
- **Sim numbers are stale** — every figure in `archive/SIM_RESULTS_2026-07-31.md`
  predates the sweep removal, the Trade harness fix and today's five rulings.
  Directions hold; magnitudes don't. Re-run before tuning.
- **Win screen** is built and matches the mockup. Two open notes: the deck
  spread reads faint against the wood, and "DOUBLE OR NOTHING" wraps to two
  lines while the others don't.
