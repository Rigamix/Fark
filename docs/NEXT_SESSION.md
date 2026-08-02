# Handover — start here

Written before a context compaction. Everything needed to pick up cleanly.

**Deployed HEAD: `d6772fc` on branch `fark`. Backup tag: `pre-effect-system`
(`a0aed7d`) — the last commit before the plan work began.**

---

## 1. THE NEXT TASK — Visual plan Phase 5, the asset registry

One table mapping logical name → path, so the previous game's `assets/` folder
becomes unreachable by accident. **Highest-value remaining item and the only
non-probe one** — it's the fix for the failure that cost the most time
(reaching into `assets/` instead of `Art/Assets/`: the font, the coin, the
diamond, three times in one session).

**Then write the Phase report** — one after every phase, in
`docs/PHASE_REPORTS.md`, same fixed format.

---

## 2. AFTER THAT

- **Effect plan Phase 1** — the inventory: decompose ~50 cards/enchants/badges
  into trigger/condition/effect. The *misfits* are the valuable output.
- Fix the two remaining Phase 2 reds: relic `.dtype-` blocks (8), and `MATCOL`'s
  4 retired materials (defence-in-depth — **not reachable**, migration converts
  them on load before any render).
- **Harden or demote `apv_bust_settle`.** It flapped during Phase 4 — red in a
  full run, green twice in isolation, nothing changed between. A flapping probe
  is not a regression signal.

---

## 1b. DONE — the feat roster migration (`d6772fc`)

Ruled, built, deployed. `FEAT_ART` is **23/23**, measured both directions.
Full write-up in `docs/PHASE_REPORTS.md` Phase 4; `FEAT_DISCREPANCIES.md` now
carries a correction header.

**What it turned up that the discrepancy doc had missed:** there were **four**
rosters, not two. `_famFeats` was granting five feats with no art — invisible,
forever — and `FTEXT` held twelve authored descriptions that outranked the live
condition on the wall. Also `first_blood` awarded for the first **match** of a
run rather than the first **boss**, so its painting hung for beating a drunk.

**Five decisions are waiting on Denis** — see the Phase 4 report's *Decisions
needed*. The two that actually change content: **STICKY FINGERS' wording** (Tar
Pit is retired; written against amber's break-trigger as a first draft) and
**the early-run drip-feed**, which the restore removes entirely — a new
player's first hour now produces no wall at all.

---

## 3. BLOCKED ON DENIS

1. **The current `FARK_ENCHANT_BADGE_REWORK.md`.** He says Corvus's two problems
   were resolved in a prior round; my copy doesn't contain it. I'm a revision
   behind and will otherwise build against stale text.
2. **Where Kindred goes.** Zero Hour moves to "the last slot before Ambrose" =
   **Whisper**, who already carries Kindred. Three-cornered, not two. Kindred
   can't take Grog's vacated slot — it needs 2+ enchanted dice, the exact
   night-one no-op we just fixed.
3. **Retuned Last Call numbers** for Grog (it's dead code in an `if(false)`
   block, so reviving is cheap; the number is a design call).
4. Boss win/loss counters: per-run or cross-run. Greeting pool: named patrons
   only or everyone. Full list in `docs/QUESTIONS_2026-07-31b.md`.

---

## 4. GOTCHAS THAT COST TIME TODAY — do not relearn these

**Deploy:** commit in the worktree → `cd` to root → `git merge --ff-only
claude/zen-chatterjee-f04c42` → `git push origin fark`. If the merge aborts on
untracked files, hash-compare them first (`git hash-object` vs `git rev-parse
BRANCH:path`), then remove and re-merge. **Never push to `main`.**

**Never `git add -A`.** Denis generates art into `Art/` mid-session. Stage
explicit paths only.

**`Art/Assets/` is the source of truth. `assets/` is the PREVIOUS game's.** I
reached into the wrong one three times today — the font, the coin, the diamond.
The game's font is **`'JMH Beda'`** (56 uses); `--font-px` is the old pixel font.

**Patches with backslashes go through a Write-tool `.py` file, never a bash
heredoc.** Heredocs mangled a regex twice.

**Run the parse gate after every edit:** `node tools/zv_trade_parsegate.js`.

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

- **Suite:** 13 probes — 12 pass, 1 fail carrying two known reds (`MATCOL`'s
  retired materials, relic `.dtype-`). Baseline in `tools/probe_baseline.json`,
  re-recorded at `d6772fc`. Full run ≈ 8–12 min.
- **Phases done:** 1 (runner), 2 (totality), 3 (CSS live), 4 (feat roster).
  Reports in `docs/PHASE_REPORTS.md`.
- **Plans:** `docs/EFFECT_SYSTEM_PLAN.md`, `docs/VISUAL_INTEGRITY_PLAN.md`.
- **Sim numbers are stale** — every figure in `SIM_RESULTS_2026-07-31.md`
  predates the sweep removal, the Trade harness fix and today's five rulings.
  Directions hold; magnitudes don't. Re-run before tuning.
- **Win screen** is built and matches the mockup. Two open notes: the deck
  spread reads faint against the wood, and "DOUBLE OR NOTHING" wraps to two
  lines while the others don't.
