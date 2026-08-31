# docs/archive — finished, superseded, or answered

Nothing in here is live. Kept for the record so a decision can be traced back
to what it was made against, not because anything still reads it.

| File | Why it is here |
|---|---|
| `DESIGN_QUESTIONS.md` | All five answered, long since built. |
| `DESIGN_QUESTIONS_2.md` | Superseded by the round-based doc below. |
| `DESIGN_QUESTIONS_3.md` | Rounds 1–4 in raw form. Round 1 answered in `AUDIT_RESOLUTIONS.md`; rounds 2–4 were rewritten as `QUESTIONS_OPEN_2026-07-31.md`, which is the live list. |
| `DESIGN_QUESTIONS_3.txt` | Plain-text export of the above, made for pasting into email. |
| `AUDIT_FINDINGS_RAW.md` | The 72 soak findings verbatim. `AUDIT_BACKLOG.md` is the worked version and is still live. |
| `NEXT_TWO.md` | Both items built in P374 — the rival now waits for its dice to settle before selecting and scoring, which fixed the kept-die angle as the same bug. |
| `DICE_BASELINE.md` | Pre-rework dice measurements. Superseded by the lane and throw work (P359–P373); nothing references it. |
| `FARK_MATCH_BRIEF.md` | **Stale duplicate.** `briefs/FARK_MATCH_BRIEF.md` is the live one — a strict superset, +46 lines. Two copies with different content in two folders is a trap, so the older one is out of the way. |

| `QUESTIONS_OPEN_2026-07-31.md` | Self-declared superseded by `QUESTIONS_2026-07-31b.md`, which is the live list. |
| `ANSWERS_2026-07-31.md` | Answers to the doc directly above; both sides of a closed round. |
| `ANSWERS_2026-07-31b.md` | Already patched into the briefs. |
| `DECISIONS_NEEDED_2026-07-31.md` | Self-declared answered — Denis replied by revising the briefs. |
| `FEEL_2026-07-31.md` | Self-declared answered, same way. |
| `VISUAL_INTEGRITY_CORRECTIONS.md` | Both corrections applied into `VISUAL_INTEGRITY_PLAN.md`. |
| `FEAT_DISCREPANCIES.md` | Migration done (`d6772fc`). Carries its own correction header — it counted two rosters and there were four. The live account is Phase 4 in `PHASE_REPORTS.md`. |
| `SIM_RESULTS_2026-07-31.md` | Still the best source on one thing: **Ruling #24's finding that the Silver:bone bust ratio is NOT policy-invariant** (0.126–0.864 across seventeen policy cells, monotone in push depth) is sound and was measured through FSIM, whose compat bust-save is off by default — so it is untouched by the defect P888 removed, and it explains any silver ratio that disagrees with the 0.54–0.58 anchor. Otherwise: **every figure is stale** — predates the sweep removal, the Trade harness fix and the 2026-08-02 rulings. Directions hold, magnitudes do not. Re-run before tuning anything against it. |
| `MASTER_PLAN.md` | Targets `fark_nights.html`, a vehicle that no longer exists — the nights rework landed in `fark_proto.html`. |
| `NIGHTS_NOTES.md` | Same dead vehicle. |
| `FARK_MASTER_BRIEF.md` | **Stale duplicate**, eight days behind `briefs/FARK_MASTER_BRIEF.md` and still being read from. Same trap as the match brief below, found the same way. **Its §9 still carries the full-silver "TRAP at 4% run wins" verdict, which is WITHDRAWN** — the sim that produced it hard-coded the bust immunity it was used to judge (fixed P888) and is match-level, so it could not have produced a run number at all. The live brief has the withdrawal and the re-measurement. |
| `QUESTIONS_2026-07-31b.md` | Folded into `docs/OPEN.md`, which is now the single questions file. Kept for the long-form reasoning behind each item — OPEN.md carries the question and the recommendation, not the derivation. |

## The 2026-08-21 sweep (54 files, ahead of a new reader joining)

Every file was audited for live content before moving; items tracked nowhere
else were quoted into `AUDIT_BACKLOG.md`'s RE-HOMED section first.

| File | Why it is here |
|---|---|
| `AGGRESSION_2026-08-03.md` | Two-seed working paper, self-declared inconclusive; refuted by the remeasure, superseded by the real-engine ladder (OPEN.md §1). |
| `AGGRESSION_REMEASURE.md` | The five-seed run that killed the sim as a difficulty instrument; carried forward in OPEN.md §1a. |
| `ART_TODO.md` | Art list filled; the two filename nits re-homed to the backlog. |
| `AUDIT_RESOLUTIONS.md` | The Jul-30 decision record, all executed; three residuals re-homed to the backlog. |
| `BREAK_ROWS_2026-08-03.md` | One-shot Break-row measurement; the heap-retention finding re-homed to the backlog. |
| `BUST_MIRRORS.md` | The bust-mirror convergence shipped (BUST_FX tables). |
| `CARD_ART_NEEDED.md` | List filled; the armed P505-stopgap deletion re-homed to the backlog. |
| `CARD_AUDIT.md` | The Aug-5 audit; `CARD_AUDIT_2.md` is current, its one live thread is in OPEN.md §1c. |
| `CARD_STATE_CENSUS.json` | Aug-10 instrument output; its line numbers and resume booleans must not be reread as current facts. |
| `CARD_VFX.md` | Shipped by the P825–P830 presentation pass; the unruled A3b room-darkening idea re-homed. |
| `DIALOGUE_BUBBLE_BRIEF.md` | Built; the residual perf-profiling note is mitigated by the seeded-render design. |
| `EFFECT_INVENTORY.md` | Phase-1 output, absorbed; the jade3 reachability question re-homed. |
| `EFFECT_LIFETIME.md` | Its primitive shipped (`_lmArm`/`_lmDue`); the decisions live as code comments at the site. |
| `EFFECT_PHASE2_GUARDS.md` | Fully absorbed (`_fxMine`, P439 deletions, code-comment constraints). |
| `EFFECT_PLAN_REPLAN.md` | The plan-finished checkpoint; its seams shipped, its open halves re-homed or mooted. |
| `EFFECT_SYSTEM_PLAN.md` | All phases done or re-scoped and ruled; the traceability text is inside. |
| `FAMCARD_PORT_SIZING.md` | Decision input for the dead port question; its headline (the sim's rival is unfaithful) lives in OPEN.md §1. |
| `FARK_BOSS_GREETING_LINES.md` | Denis's 80 lines, wired verbatim in P839 (state router); the game is now the source of truth. |
| `FINDINGS.md` | Aug-8 instrument findings; the shoot.js-watchdog ask re-homed to the backlog. |
| `FOG_INDEX_BUG.md` | Fixed and verified in P491; the reasoning lives as a comment at the site. |
| `ILL_OMEN_MIGRATION.md` | Migration shipped in P766 (one hook, both owners). |
| `KEEP_CONTROL.md` · `KEEP_WIRING_SIZE.md` · `NPC_KEEP_WIRING_SIZE.md` · `NPC_SELECTION_SIZE.md` | Sizing papers for the keep-wiring work, which shipped; superseded by the P772-773 chooser. |
| `MECHANIC_TABLE_SCOPE.md` | The table shipped; the `_oppHas` helper ask re-homed. |
| `MIRROR_DIFF.md` | Re-scoped onto the P470 extractions and completed. |
| `NOTES_2026-08-15.md` | Session notes; THE SETTLE DRAG (open, Denis-reported twice) re-homed to the backlog's top. |
| `NPC_AI_BRIEF.md` | The follow-on rework it briefed was DELETED by Denis's 2026-08-20 ruling; the shipped parts (P760-773) are recorded in code and OPEN.md. |
| `OCARDS_STUBBED.md` · `OPPCARDS_LIFT_MEASURED.md` · `OPPCARDS_LIFT_SIZE.md` | The oCards stub lift shipped (with the shared-gate patron lesson); block_low_bank's line is in the backlog. |
| `OPP_ENCHANTS_SIZE.md` | Sizing for a feature ruled out of existence; the sourcing design question re-homed. |
| `P5_NPC_CARDS.md` | The P5 port shipped; the seven-unarmed-actives gap re-homed. |
| `P5_OBSERVERS.md` | Observer census, absorbed by the port. |
| `PATRON_GROWTH_LINES.md` | Wired in P833; the seven excluded patrons re-homed as a content ask. |
| `PATRON_LEVELING_BRIEF.md` | Executed across P822/P833/P837; the flat-cap confirm re-homed. |
| `PHASE4_MIGRATION.md` | Migration done; the live account is PHASE_REPORTS (here too). |
| `PHASE_REPORTS.md` | The completed-phase record, closed out; nothing appends to it. |
| `PLAYTHROUGH_PASS_PLAN.md` | All seven steps DONE (P816-P830); the one deferred idea re-homed. |
| `PROBE_AUDIT.md` · `REACH_AUDIT.md` | One-shot instrument audits, acted on. |
| `REWORK_MEASURED_2026-08-03.md` · `SIM_OPPTURN_SIZE.md` · `SIM_RERUN_2026-08-03.md` · `SPREAD_AUDIT.md` | Sim-era measurements; the sim was retired as a difficulty instrument (OPEN.md §1a); the spread-comparability trap re-homed. |
| `RUNSCOPE_SEAMS.md` · `SEAM_TWO_LEFT.md` · `TURNSTATE_CLEARING.md` | Seam work, shipped. |
| `TABLE_BAR.md` | The recorded non-decision it exists to hold. |
| `VISUAL_INTEGRITY_PLAN.md` | Phases 1-5 complete. |
| `WILD_PARITY_FIX.md` · `WILD_SEAT_ASYMMETRY.md` | Both shipped. |
| `card_visuals.md` | June art concepts; the deck shipped, Higgsfield pipeline notes live in memory/OPEN as needed. |

## What is still live, in `docs/`

See `docs/README.md` — it is the index now, and it is kept current rather than
duplicated here. Two copies of a list of live documents is exactly the failure
this folder exists to record.
