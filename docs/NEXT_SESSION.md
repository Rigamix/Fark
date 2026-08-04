# Handover — start here

Written before a context compaction. Everything needed to pick up cleanly.

**Deployed HEAD: `f431bb9` on branch `fark`. Backup tag: `pre-effect-system`
(`a0aed7d`) — the last commit before the plan work began.**

---

## 1. THE NEXT TASK — Phase 5, and nothing is blocking

Phase 4 is done: the nine read by hand, three seams built (`commit`,
`deadRoll`, `rivalTurn`), the run-scoped domain measured and built
(`matchArmed` + `_rs*`), and the suite is fully green for the first time.
`docs/PHASE4_MIGRATION.md` and `docs/RUNSCOPE_SEAMS.md` carry the reasoning,
including three findings that were argued DOWN by reading the actual lines.

**Phase 5 — Observers** is next in `EFFECT_SYSTEM_PLAN.md`, and it is also
where NPC family cards land (`G.oF` is deliberately empty until then; `tamper`
and the boss card pools are both waiting on it).

**Before starting it, read `docs/PHASE4_MIGRATION.md`'s instrument notes.**
Phase 4 spent more time correcting its own tools than writing game code, and
every one of those corrections is a trap Phase 5 can walk into unchanged.

---

## 1z. SUPERSEDED — Phase 4: read the nine by hand

**Start here, and read them one at a time.** `docs/PHASE4_MIGRATION.md` carries
a retraction: the "group 1 is clean" result was wrong, `short_fuse` is half-on,
and two automated passes in a row produced numbers that did not hold.

**The nine cards with unexplained sites** (after `_npcFamCard` opponent-side and
`_SEAL_POOL` name-collision sites were separated, both eye-verified):
`fools_gold_f`, `slow_cook`, `retort`, `double_or_nothing`, `short_fuse`,
`encore`, `ill_omen`, `sleight`, `pickpocket`.

**Do NOT reach for a third classifier pass.** The instrument has been wrong in
both directions on this exact question; the sites are few enough to read.
`tools/cfx_bespoke.py` locates them, and that is all it should be trusted for.

**Then the five-card build**, which is confirmed and unstarted: `bloom`,
`cultivate` and `vanguard_f` all live in `famCommitBonus` and need a `commit`
hook — which `short_fuse`'s x2 wants too, so resolving the retraction and
designing that hook are the same job. `for_keeps` is a seat-launch wager with no
match-scoped effect, and `tar_pit` has no implementation and is off `FAM_LIVE`;
both need reading before they are assumed migratable.

**And name the five tavern cards off-bus IN CODE, with the reason** — run-scoped,
not match-scoped — so a later pass does not read "not migrated yet" and try to
finish the job. Ruled 2026-08-03.

---

## 1a. DONE — Effect Phase 3 (lane markers BUILT; see EFFECT_LIFETIME.md)

**BUILT (`P444`):** the lane-marker lifetime — `_lmArm` / `_lmDue` / `_lmSpend`
/ `_lmRetire`, with the window gate inside `_lmDue` so it cannot be skipped.
Snare, Snuff and Fog migrated. `apv_lane_lifetime.js`, 10 checks.

**Snuff now gates on its armed turn.** Building the primitive forced the
decision the measurement deliberately left open. Verified behaviour-identical
on the live path (`dueOnArmedTurn`) and different only where `live`-alone would
wrongly have fired (`notDueOnLaterTurn`).

**Snare keeps a separate verb.** `_lmRetire` ≠ `_lmSpend`: Snare is consumed on
the bite, and folding it into the turn counter would have handed it a second
turn — the exact wager its own comment says it must not have.

**STILL OPEN: Trade.** Excluded in writing at the primitive. Nothing to build.

**The measurement is done and it corrected the plan.** `docs/EFFECT_LIFETIME.md`
+ `tools/effect_lifetime.py`. Three findings that change what Phase 3 builds:

- **Trade is NOT a lane marker.** The plan groups it with Snare/Snuff/Fog; it is
  an array of swap records with an undo, no `live`, no `turn`, no window, and it
  snapshots across a save. A primitive built from the lane markers and applied
  to it would impose a window on something designed not to have one.
- **Snuff writes a window field it never reads.** All three lane markers arm
  `{lane, live, turn}`; snare and fog gate on `turn===oppTurnCount`, snuff gates
  on `live` alone. Not a demonstrable live bug — `oppTurnCount` increments
  before the check, so the paths coincide today. Left unfixed ON PURPOSE: it is
  a behaviour change on Kindred's two-turn hold and belongs with the primitive.
- **Ward: I got this one wrong, then corrected it.** The audit grouped by name
  prefix and reported Ward's retirement as scattered. `_ward` is a prefix shared
  by THREE unrelated features — the enchant (`_wardArmed`/`_wardBoost`, one
  turn), the `warded` card's persistent charge pool (`_wardCharges`), and a
  bank counter (`_wardBanks`). The enchant's two expiry sites are both correct:
  `doBust` is CONSUMED, `startPTurn` is EXPIRED. Nothing distributed to fix;
  Phase 3 item 2 is **withdrawn**, and the naming it actually needed is done.

---

## 1a. Effect Phase 3 — the original framing

**The whole queue cleared.** famLog, rules audit, props brief, Preserve,
cap-endings, the sim re-run, the Break rows, and Effect Phase 2 in both halves.
Reports in `docs/PHASE_REPORTS.md`; the measurement docs are
`SIM_RERUN_2026-08-03.md`, `BREAK_ROWS_2026-08-03.md`,
`EFFECT_PHASE2_GUARDS.md`, `TURNSTATE_CLEARING.md`.

**Phase 3 is the resolver and the ordering rule** — re-scoped by Phase 1's
ruling, so read `EFFECT_SYSTEM_PLAN.md`'s banner before starting:

- **It does NOT settle a multiplier rule.** Nothing multiplies. Kindred is five
  hand-authored alternate definitions sharing a name.
- **It settles EFFECT LIFETIME instead** — Ward's armed window, and Snare /
  Snuff / Fog / Trade, which are lane markers with a placement, a window and an
  expiry rather than effects with a moment.
- **Two constraints are already discovered and must survive it:** guards may
  have side effects (`powder_keg.use` spends a bust save, so nothing may be
  evaluated speculatively or shared), and a restore into a fresh turn belongs
  after `_turnTableClear()` — a boundary found twice, independently.

### What Phase 2 actually delivered, including what it declined to build

`_fxMine(ev)` across 9 sites — and **three inline `ev.owner==='p'` checks left
alone**, because that form omits `ev.mine` and therefore also fires when the
RIVAL is the actor. Whether that is intended is an open BEHAVIOUR question,
named at the site rather than resolved by tidying.

**No `_fxFreeDice()`, deliberately.** `!free.length` looked like a shared query;
the sets are four different things, and folding them would have taken Powder
Keg's "kept dice included" away from it.

**Two named clear phases**, not the single `endTurnState(reason)` that was
proposed before the branch trace. Nine paths clear in two stages with the path's
own work in the gap, so a single wrapper could not express it.

---

## 1c. HOW FAR ALONG — say it in units, never as one number

Two strands, two different questions. **Do not blend them and do not put two
percentages next to each other** — a table of percentages is what produced a
blended "70%" that matched none of its own rows.

> **85% of the behaviour is built. The shared machinery it runs on is two
> phases into five, with one condition lifted and no effect application yet.**

- **Behaviour** — the enchant/badge rework's own §6 checklist: Silver reworked,
  Ward/Insurance retired, three enchants cut, seven icon enchants firing through
  one rule, Break's death rows, four badge remaps, the face restriction, the
  feat roster. Enumerable, mostly shipped, **~20% validated** — only Obsidian's
  Break row has sim numbers and almost nothing has been played.
- **Machinery** — the effect system. **2 of 5 phases.** Phase 1 mapped it;
  Phase 2 built the one condition the content actually asks for (`_fxMine`) and
  named the two clear phases. Still no shared EFFECT APPLICATION, and Phase 3
  (lifetime) is where the lane-markers get a model. Say "2 of 5 phases, one
  shared condition, no shared application" rather than a percentage.

**Denominators:** 69 items exist, ~65 are player-reachable. Totality assertions
use 69; migration progress uses 65. See `EFFECT_INVENTORY.md` §1.

---

## 2. AFTER THAT

- ~~Fix the two remaining Phase 2 reds~~ **DONE, and this entry was right in a
  way I then contradicted.** The 8 relic `.dtype-` blocks are added (derived
  from each relic's MATCOL tint). `MATCOL` gained brass and crystal, and the
  probe's domain now excludes `dep:true` dice (jade3, ruby) by the game's own
  retirement flag.
  **But I claimed brass/crystal were reachable via patron `dieBias` and they
  are not** — `dieBias` filters `ps.dicePool`, and no patron pool contains
  either. This file said "still not reachable" and was correct; I contradicted
  it without reconciling first. The entries stay (a tint costs nothing, and is
  right the moment either enters a pool), but they are not a live-bug fix.
  **Still open:** whether the SHOP can sell them. Unverified either way.
  **And a real find in passing:** the `ones` persona's `dieBias` names brass
  and crystal and the `hoard` persona names crystal — none of which is in any
  `dicePool`, so those bias entries select nothing.
- ~~superseded~~ The original note read: I said migration converts them on load before any render. The real
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

**WRITE THE PATCH AS THE VERIFICATION STEP.** Three findings on 2026-08-03
were disqualified at exactly one moment, and it was the same moment each time:

  endMatch      ranked first as a seam by touch-count (4 cards). Writing the
                patch meant reading the positions - 6% to 98% across 619 lines.
                A shared FUNCTION, not a shared moment.
  the classifier `` through a heredoc became a backspace byte. Fixing the
                file meant looking at the bytes.
  seatCommit    3 cards, tight by percentage. Writing the patch meant reading
                the lines between them, which turned out to be load-bearing.

**This is not "patch-writing is a lucky place to catch bugs."** It is the one
step where a description gets tested against the literal text instead of a
summary of it. Everything upstream - the ranking, the percentages, the counts,
the seam-count assumption - is reasoning ABOUT the code. Writing the patch is
reading it.

So: **do not treat a measurement as settled until a patch has been written
against it.** If the patch is not going to be written yet, the finding is
provisional and says so. Percentages and counts are a way of deciding WHERE to
read, never a substitute for reading.

**AND seatCommit's dependency chain is why the stakes are not just tidiness.**
`S.run.gold -= buy` must run after Double Stakes doubles the buy-in because it
READS a value that instruction produces. A hook firing all three cards at one
point would not have been merely imprecise - it would have silently broken a
real dependency. The failure mode was "wrong answer", not "wrong grouping".
Same as the two-stage turn clear, where the gap between phases is where each
path does its own work.

**SCRUTINISE CLEAN RESULTS HARDER THAN DIRTY ONES.** Six instrument artifacts
in one day invented findings; the seventh HID one, and it was by far the most
expensive. `cfx_bespoke` reported all 20 cards fully migrated. `short_fuse` was
not — its x2 is hardcoded in `famCommitBonus` while it sits on `CFX`.

**The two failure directions need opposite habits and only one of them prompts
you.** A surprising finding gets checked because it is surprising. A clean
result is precisely where checking stops — there is nothing on the page asking
to be verified, and the work appears finished.

**Worse: that zero had been NARROWED to, from 18, through four corrections.**
Every one of those corrections was real, which made the process look rigorous
and made the final answer the most trusted number of the whole phase. Visible
refinement earns trust that the endpoint has not separately earned. Looking
corrected is not being correct.

**So: when a check comes back clean, go and find one instance by hand.** Not to
confirm the answer — to confirm the instrument can still SEE. This one was
caught only because building on the result ran into code that contradicted it,
which is luck, and late.

**A STANDING RULE IS WEAKEST EXACTLY WHERE IT MATTERS MOST.** Separately from
the above, and not a footnote to it: a `str.replace` inside a bash heredoc
silently no-op'd while the replacement next to it applied, and I read the
resulting numbers before checking the edit had landed. There is a standing rule
in this file about asserting on every replacement, written after this exact
failure. It got skipped.

The conditions are the point: late in a long session, mid-correction, moving
fast to reach a clean answer after a retraction. That is when a rule is most
needed and least likely to be honoured, because the pressure that makes it
necessary is the same pressure that makes it feel skippable. It was caught by
grepping for the inserted text — a five-second check that only happens if you
do it every time, including the times it seems unnecessary.

**A NAMING CONVENTION IS NOT A SHARED-STRUCTURE CLAIM.** The Ward withdrawal
was not a measurement error inside a correct question - it was the wrong
question. `_wardArmed`, `_wardBoost`, `_wardCharges` and `_wardBanks` share a
prefix; the audit grouped by prefix and concluded they shared a LIFETIME, then
recommended restructuring three unrelated features into one. Three of them have
no lifetime at all.

That is the identical surface-resemblance mistake this session kept finding in
the game's own code - `.gcard` "from main game", the four `_fxFreeDice` sets,
Trade grouped with the lane markers - caught this time in the audit that was
hunting for it. It is also the most expensive kind that has come up: the other
instrument errors made things look LESS coherent than they were, which invites
a second look. This one made three coherent things look like one broken thing
and proposed a fix, which invites a rewrite.

**Before grouping N things by a shared name, check they answer the same
question.** If the tool groups by prefix, the report must say "these share a
prefix" and nothing more until each is read.

**EVERY PROBE MUST JUSTIFY WHICH DOM SURFACE IS AUTHORITATIVE** before it
asserts anything — not that a plausible selector exists, but that the one it
reads is the one the live build actually paints. FIVE instances in one session
of a check verifying against the wrong surface, each of which reported success
having tested nothing real:

- `apv_bust_settle` scored a STRING verdict with `=== false` and passed.
- `apv_css_live` failed rules whose specificity was raised on purpose, by
  matching selector text exactly instead of by token.
- `apv_prop_overlap` reported zero overlaps having found two buttons and no
  dice, because the roll had not landed.
- The same probe then computed prop boxes from template data with the wrong
  origin (`left:x%` means x is the LEFT EDGE) and no rotation.
- `apv_preserve` asserted `G.kept` only — green while the table stayed empty —
  then measured `#keptTray`, which is the **2D fallback**: `refreshKeptTray`
  returns early on a `.fk3d` build and `#keptRow` is live.

**Queued item: audit every probe in the suite for this once, deliberately.**
For each, name the surface it asserts on and confirm it is the one the shipped
build renders. Cheaper as a single pass than rediscovered one accident at a
time.

**CHECK A SURFACE IS REACHABLE BEFORE AUDITING WHAT IT SAYS.** Three-for-three
this session, and in every case reading the code would have confirmed the wrong
thing: `#rulesOverlay` (six false claims, no visible entry point),
`#screen-bossreward` (nothing calls `showScreen('bossreward')`, and it decided
whether a Phase 2 red was live), `body::before` (a real stretch bug in a rule
that computes to `display:none`). Ask "can a player see this" first — it is the
cheaper question and it decides whether the accuracy work is worth doing.

**And when DELETING dead content, test the behaviour AROUND the deletion**, not
just that the target lines are gone. Cutting the rules overlay left a
`renderRulesScroll()` call in the BOOT resize handler — every window resize
would have thrown. A cleanup that introduces a crash is worse than what it
removed. *(Worth building: a probe that enumerates `showScreen` cases with no
caller, and overlays with no visible entry point. Three found by hand is enough
to justify automating the fourth.)*

**ASSERT EXACT, NEVER A FLOOR** — unless you can say why a floor is right. `>=`
is satisfied by less than it was meant to verify. `assert n >= 7` passed a run
where a replacement had silently failed and left two sites half-converted;
`assert n == 8` caught it. Same family as a probe passing having tested nothing.

**CONTROL FLOW BEFORE POSITION.** In one pass over `doBust`, position misled
three times at three granularities: nearest-preceding-`function NAME` is not
lexical scope (26 sites misattributed), a three-line adjacency window
undercounted clears that were deliberately two stages apart, and a search
anchored from position zero hit the wrong function twice. Walk the branches
first; check position against them, never the reverse.

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

- **Suite: 29 probes, FULLY GREEN** — 28 pass, 0 fail, 0 error (one probe,
  `apv_break_borrowed`, skips by design when the roll gives it nothing).
  Baseline re-recorded at `f431bb9`. Full run ≈ 12–18 min.
  Every run appends to `tools/probe_history.jsonl`, so an intermittent failure
  arrives with its own evidence instead of dying with the scrollback.
- **Phases done:** 1 (runner), 2 (totality), 3 (CSS live), 4 (feat roster),
  4b (badge remap), 5 (asset registry). Reports in `docs/PHASE_REPORTS.md`.
- **Deployed HEAD is `f431bb9` on `fark`.** This file used to carry TWO
  different HEADs — the header said one, this line said another — which is the
  contradiction-is-a-stop case sitting inside the handover itself. One value,
  here and at the top, and they are updated together or not at all.
- **Plans:** `docs/EFFECT_SYSTEM_PLAN.md`, `docs/VISUAL_INTEGRITY_PLAN.md`.
- **Sim numbers are stale** — every figure in `archive/SIM_RESULTS_2026-07-31.md`
  predates the sweep removal, the Trade harness fix and today's five rulings.
  Directions hold; magnitudes don't. Re-run before tuning.
- **Win screen** is built and matches the mockup. Two open notes: the deck
  spread reads faint against the wood, and "DOUBLE OR NOTHING" wraps to two
  lines while the others don't.
