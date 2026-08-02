# Handover — start here

Written before a context compaction. Everything needed to pick up cleanly.

**Deployed HEAD: `d6772fc` on branch `fark`. Backup tag: `pre-effect-system`
(`a0aed7d`) — the last commit before the plan work began.**

---

## 1. THE NEXT TASK — Effect plan Phase 1, the inventory

Decompose ~50 cards, enchants and badges into **trigger / condition / effect**.
The *misfits* — the ones that don't fit the three-part shape — are the valuable
output, because they're where the architecture would have to bend.

Backup tag `pre-effect-system` (`a0aed7d`) exists for exactly this work.

**Then write the Phase report** — one after every phase, in
`docs/PHASE_REPORTS.md`, same fixed format.

---

## 2. AFTER THAT

- Fix the two remaining Phase 2 reds: relic `.dtype-` blocks (8), and `MATCOL`'s
  4 retired materials (defence-in-depth — **not reachable**, migration converts
  them on load before any render).
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
Full write-up in `docs/PHASE_REPORTS.md` Phase 4; `FEAT_DISCREPANCIES.md` now
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
- **Sim numbers are stale** — every figure in `SIM_RESULTS_2026-07-31.md`
  predates the sweep removal, the Trade harness fix and today's five rulings.
  Directions hold; magnitudes don't. Re-run before tuning.
- **Win screen** is built and matches the mockup. Two open notes: the deck
  spread reads faint against the wood, and "DOUBLE OR NOTHING" wraps to two
  lines while the others don't.
