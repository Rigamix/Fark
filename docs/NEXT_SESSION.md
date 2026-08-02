# Handover — start here

Written before a context compaction. Everything needed to pick up cleanly.

**Deployed HEAD: `7a4ad60` on branch `fark`. Backup tag: `pre-effect-system`
(`a0aed7d`) — the last commit before the plan work began.**

---

## 1. THE NEXT TASK — the feat roster migration

**Ruled by Denis. Sized. Deliberately not started** because it's a content change
across the whole feat list and beginning it without room to finish is how a
half-migration happens. Full detail in `docs/FEAT_DISCREPANCIES.md`.

**The finding:** `Art/Assets/Feats/` holds **24 paintings**. The code ships **32
feats**. `FEAT_ART` maps 12 — and **six of those twelve point at the wrong
thing** (`Death&Taxes`, which the brief defines as *beat Ambrose*, currently
awards for beating **Corvus**; `Teetotaller`, *never bank under 500*, awards for
beating **Grog**).

**The ruling:** restore the brief's §8 list of 24. The 32 in code is **drift**,
not a decision anyone made. Feats are permanently non-power-granting wall
decoration, so there's no gameplay argument for more — only an art-budget one,
and the art budget already said 24.

**The work:**
1. Replace `FEATS` (32 rows) with the brief's list — **23 live + 1 parked**.
2. Remap `FEAT_ART`. Becomes near-total *by construction* once the paintings and
   the roster describe the same set.
3. **BOOKKEEPER stays retired** — Bookends' collapse into Vanguard was a
   deliberate simplification, already ruled. Its painting is the orphan.
4. **NO CLAIM: rewrite the condition against Ward**, don't cut it. It referenced
   Insurance-the-card (retired), but what it rewarded — bust-averse play — still
   exists via Ward.
5. **The six `beat_<boss>` feats are cut.** Real content loss, named on purpose.
   If per-boss recognition matters it wants its own category with its own art
   ask — not a reason to keep the drifted 32.
6. Rerun `node tools/run_probes.js`. **`FEAT_ART` should go 12/32 → 23/23** and
   the baseline will prove it.

**Then write the Phase report** — Denis wants one after every phase, in
`docs/PHASE_REPORTS.md`, same fixed format.

---

## 2. AFTER THAT

- **Visual plan Phase 5** — the asset registry. One table mapping logical name →
  path, so the previous game's `assets/` folder is unreachable by accident. This
  is the highest-value remaining item and the only non-probe one.
- **Effect plan Phase 1** — the inventory: decompose ~50 cards/enchants/badges
  into trigger/condition/effect. The *misfits* are the valuable output.
- Fix the three Phase 2 reds: relic `.dtype-` blocks (8), `MATCOL`'s 4 retired
  materials (defence-in-depth — **not reachable**, migration converts them on
  load before any render), `FEAT_ART` (handled by §1).

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

- **Suite:** 13 probes — 12 pass, 1 known red (relic `.dtype-`). Baseline in
  `tools/probe_baseline.json`. Full run ≈ 8–12 min.
- **Phases done:** 1 (runner), 2 (totality), 3 (CSS live). Reports in
  `docs/PHASE_REPORTS.md`.
- **Plans:** `docs/EFFECT_SYSTEM_PLAN.md`, `docs/VISUAL_INTEGRITY_PLAN.md`.
- **Sim numbers are stale** — every figure in `SIM_RESULTS_2026-07-31.md`
  predates the sweep removal, the Trade harness fix and today's five rulings.
  Directions hold; magnitudes don't. Re-run before tuning.
- **Win screen** is built and matches the mockup. Two open notes: the deck
  spread reads faint against the wood, and "DOUBLE OR NOTHING" wraps to two
  lines while the others don't.
