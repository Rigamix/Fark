# docs/ — what is live

Everything at this level is current (last full audit: 2026-08-21, every
file's claims checked against the code before it stayed). Anything
superseded, answered or built is in `archive/`, with a line in
`archive/README.md` saying why it went there. Nothing is ever deleted —
a decision should be traceable back to what it was made against.

**Denis reads one file: `OPEN.md`** — questions and blockers, each
carrying a recommendation so "yours" is a valid answer. Nothing else
here is written for him.

**Whoever picks up the work starts with `NEXT_SESSION.md`** — the
current state, what's in flight, and the traps that have already cost
time.

## The working set

| File | What it is |
|---|---|
| `OPEN.md` | **Denis's file.** Every open question and blocker, with a recommendation on each. Answered items are deleted, not marked — it has to stay short enough to read in one go. |
| `NEXT_SESSION.md` | The handover: current state, in-flight work, standing traps. |
| `AUDIT_BACKLOG.md` | The long-running work queue. Its **RE-HOMED (2026-08-21)** section holds every live item rescued from the archived working papers — including the open settle-drag feel bug. |
| `CARD_INTERACTION_RULES.md` | **The card-interaction contract** (P844/P845): the four kinds of card state (promise / arm / lane record / flag), the rules R1-R6, the enforcement map, and the checklist every NEW card must answer in its patch header. |
| `ARCHITECTURE_AUDIT.md` | The 2026-08-20 systems audit: eleven systems judged, why each is genuinely separate (or was folded), and the standing route-through-existing habit. |
| `CARD_AUDIT_2.md` | The current card-behaviour audit (every family card, tavern card, enchant — adversarially probed; verdict table + flake ledger). |
| `CARD_EFFECT_SPECS_FULL.md` | Per-card presentation specs. Where a later ruling changed a spec (Double or Nothing, Sacrifice), the ruling is banner-noted in place. |
| `BANK_ORACLE_PLAN.md` | The planned (not started) bank-to-win oracle work — gated on its own session. |
| `DICE_LANE_INTEGRITY_PLAN.md` | The lane-integrity ledger (large; deep reference). Its status banner says which halves have since shipped. Two NOT-DRIVEN queues live only here. |
| `VFX_LANGUAGE.md` | The per-card VFX vocabulary and intent, including the unbuilt "fun list". |
| `PROTO_NOTES.md` | Geometry and layout notes. **`fark_proto.html` references this file by name** (3 sites, verified 2026-08-21) — not archivable. |
| `briefs/` | **The authoritative design set** — see below. |
| `tools/` | Two art-baking scripts. Not documentation; historical location. |

## briefs/ — the design set

**`briefs/` is the only place a brief lives.** That rule exists because
it was broken twice: two briefs each had two copies with *different
content* in two folders, and the stale copy was still being read. The
stale copies are in `archive/`.

- `FARK_MASTER_BRIEF.md` — the authoritative design doc. (Its header
  flags an owed stale-content pass — tracked in AUDIT_BACKLOG.)
- `FARK_MATCH_BRIEF.md` — the match layer.
- `FARK_ENCHANT_BADGE_REWORK.md` — supersedes the master brief on
  enchants, Silver, and four of the eight badges. Its §5 open items are
  pointered from AUDIT_BACKLOG.
- `FARK_EFFECT_SYSTEM_PROPOSAL.md` — the trigger/condition/effect
  proposal the CFX seams grew from.
- `FARK_SIM_BRIEF.md` — the sim method reference. Status banner: its
  receipts and numbers are outdated; difficulty now measures through
  `tools/ladder_real.js` (real engine, both seats).
- `FARK_PATRON_LORE.md` — the patron cast.
- `FARK_LOOP_BRIEF.md` · `FARK_UI_SCREENS_BRIEF.md` ·
  `FARK_UI_ADDENDUM.md` — the standing set the rework briefs sit under.

**Where two briefs disagree, the rework brief wins on its own subject
and the master brief wins everywhere else.**

## Orientation for a new reader

1. `NEXT_SESSION.md` — where things stand and the traps.
2. `CARD_INTERACTION_RULES.md` — the contract you must not break when
   touching cards, and the model for how rules get written here:
   measured, enforced at named sites, coverage stated honestly.
3. `ARCHITECTURE_AUDIT.md` — the map of what is deliberately separate.
4. `AUDIT_BACKLOG.md` — the queue, corrections first.
5. The game is ONE file: `fark_proto.html` (~45k lines). The probe
   harness is `tools/shoot.js` + the committed `tools/apv_*.js` probes;
   every patch lands via a `tools/_p###_*.py` script with
   fail-before-write anchors and must pass
   `node tools/zv_trade_parsegate.js fark_proto.html`.

---

*This file is UTF-8. It was UTF-16LE until 2026-08-02 — a one-line
stub that rendered as mojibake and that every text tool silently failed
to read. If an edit here ever throws a decode error, that is what came
back.*
