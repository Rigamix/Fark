# docs/ — what is live

Everything in this folder is current. Anything superseded, answered or built is
in `archive/`, with a line in `archive/README.md` saying why it went there.
Nothing is ever deleted — a decision should be traceable back to what it was
made against.

**Denis reads one file: `OPEN.md`** — questions and blockers, each carrying a
recommendation so "yours" is a valid answer. Nothing else here is written for
him.

**Whoever picks up the work starts with `NEXT_SESSION.md`** — the current task,
open decisions, and the gotchas that have already cost time.

## The working set

| File | What it is |
|---|---|
| `OPEN.md` | **Denis's file.** Every open question and blocker, with a recommendation on each. Answered items are deleted, not marked — it has to stay short enough to read in one go. |
| `NEXT_SESSION.md` | The handover: next task, open decisions, gotchas. |
| `PHASE_REPORTS.md` | One entry per completed phase, fixed format, written to be circulated. |
| `AUDIT_BACKLOG.md` | The long-running backlog: what is done, what is queued. |
| `AUDIT_RESOLUTIONS.md` | The creative director's answers, kept as the decision record. |

## Plans in flight

| File | Status |
|---|---|
| `EFFECT_SYSTEM_PLAN.md` | Phase 1 done. Phases 3 and 4 **re-scoped and ruled** — the superseded text is kept under each banner so the change is traceable. |
| `EFFECT_INVENTORY.md` | Phase 1's output: all 69 pieces of content decomposed, the rows that do not fit, and the 69-exists / ~65-reachable split. |
| `VISUAL_INTEGRITY_PLAN.md` | Phases 1–5 complete. |

## Reference

| File | What it is |
|---|---|
| `PROTO_NOTES.md` | Geometry and layout notes. **`fark_proto.html` references this file by name** — it is not archivable. |
| `ART_TODO.md` | Missing artwork, measured against `Art/`. |
| `card_visuals.md` | Art concepts for all 133 cards. |
| `briefs/` | **The authoritative design set** — see below. |
| `tools/` | Two art-baking scripts. Not documentation; they live here for historical reasons. |

## briefs/ — the design set

**`briefs/` is the only place a brief lives.** That rule exists because it was
broken twice: `FARK_MATCH_BRIEF.md` and `FARK_MASTER_BRIEF.md` each had two
copies with *different content* in two folders, and nothing said which was real.
The master brief's `docs/` copy was **eight days out of date and still being
read**. Both stale copies are now in `archive/`.

- `FARK_MASTER_BRIEF.md` — the authoritative design doc.
- `FARK_MATCH_BRIEF.md` — the match layer.
- `FARK_ENCHANT_BADGE_REWORK.md` — supersedes the master brief on enchants,
  Silver, and four of the eight badges.
- `FARK_EFFECT_SYSTEM_PROPOSAL.md` — the trigger/condition/effect proposal.
- `FARK_SIM_BRIEF.md` · `FARK_PATRON_LORE.md`
- `FARK_LOOP_BRIEF.md` · `FARK_UI_SCREENS_BRIEF.md` · `FARK_UI_ADDENDUM.md` —
  the standing set the rework briefs sit under.

**Where two briefs disagree, the rework brief wins on its own subject and the
master brief wins everywhere else.**

---

*This file is UTF-8. It was UTF-16LE until 2026-08-02 — a one-line `# Fark`
stub that rendered as mojibake and that grep, python and every other text tool
silently failed to read. If an edit here ever throws a decode error, that is
what came back.*
