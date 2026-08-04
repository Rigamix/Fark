# OPEN — questions and blockers

The only file you need to read. Everything has my recommendation, so **"yours"
is a valid answer.** Answered items are deleted, not marked — this stays short.

**One decision: §0.**

---

## 0. Seam coverage — measured, so you can size it without either of us guessing

The opponent's turn raises **one** of eight CFX seams (`bank`). Making boss
cards work means raising the other seven. I declined to estimate that after two
wrong sizes today, so I measured `runOppTurn` instead — same test that settled
`matchArmed` and disqualified `endMatch`/`seatCommit`.

**`runOppTurn` is 1,438 lines.** Per seam:

| seam | shape | what it costs |
|---|---|---|
| `roll` | **POINT** — 1 site | an added call |
| `turnStart` | near-point — 2 sites, 24 lines apart | probably one call |
| `bank` | POINT | **already done** |
| `commit` | **SPREAD** — 7 sites across 425 lines | a decision about *which* moment is the seam |
| `bust` | **SPREAD** — 7 sites across 229 lines | same |
| `bankBonus` | **SPREAD** — 12 sites across 885 lines | same |
| `deadRoll` | **ABSENT** | the opponent turn has no dead-roll concept at all |

**So it is three different jobs, not one:**

1. **Two seams are additions** (`roll`, `turnStart`) — small, and they'd let
   `slow_cook` and `short_fuse` work for a boss through the bus.
2. **Three are the `seatCommit` decision**, three times over, inside a
   1,438-line function: *which* of 7/7/12 sites is the moment. That is the
   decision that disqualified `seatCommit` at 30 lines; here it is at 425, 229
   and 885.
3. **One is impossible as things stand.** `deadRoll` has no counterpart — the
   opponent turn never asks "did this roll score nothing" the way the player's
   does. A card depending on it cannot work for a boss however it is gated.

**And that last row retro-justifies a deferral I made for the wrong reason.** I
held `fools_gold_f` back over sim pacing. The real blocker is that its seam does
not exist on the opponent's side at all.

*Still no time estimate from me — but the shape says this splits cleanly, and
(1) is separable from (2) and (3) if you want the small part first.*


---

## 1d. The sim re-run — deltas are in, and they are large

`docs/SIM_RERUN_2026-08-03.md`. Not acted on, per your ruling. The three that
matter:

**Win rate on an un-upgraded build collapsed ~4x.** Tiers 3–7 were
`30.8 / 33.0 / 36.4 / 33.9 / 32.3`; they are now `8.1 / 8.0 / 8.9 / 11.1 / 8.2`.

**Cap endings start much earlier** — 55.4% at tier 3, not the 0.3% reported.

**And the mechanism is now visible:** median turns pins to the cap from tier 3
and never moves, while player bank plateaus (1,971 → 1,933 across five tiers)
and opponent bank keeps climbing (5,727 → 6,436). The ladder scales; a held-still
player does not.

Also: **agent spread narrows as tiers rise** (60.9 → 23.6), so how well you play
matters *less* the higher you climb — the strongest support yet for "longer, not
harder".

**Aggression was ruled and shipped** (`8f04cc1`, +0.06 across all eight tiers,
capped at .95). Result **inconclusive** — see `docs/AGGRESSION_2026-08-03.md`.

**And the table above needs a caveat it did not have.** Every figure in it is
**one seed**. Measured since: `spread` carries ±3–6 of seed-to-seed noise per
tier and ~10 on the t0→t7 trend. The narrowing claim survives — a ~30-point
fall clears that comfortably — but the specific numbers were never a range.
Win rates and bank figures in the same table come from the same single run and
deserve the same caution.

**What is still yours:** whether to spend 5–6 seeds per side confirming the
aggression bump, and whether to pull either of the other two levers (lower late
targets, let player scoring grow). The brief's ordering instruction still
stands — *"tune TARGETS down before inflating player scoring"*.

---

## 1e. The old roster — answered by the file, and it was already ruled once

You were right that "unused on every path I drove" isn't "unreachable on every
path that exists." It's checkable, and the answer is **retired, deliberately,
and the same call you just made was made once already.**

`PROTO_NOTES.md`, P1b: *"~330 old effect sites now inert; physical deletion
deferred (dead code, no behavior)."*

**It's held dead by three one-line stubs** — a `return []` on the first line of
`effectiveCards`, `initMatchScreen`'s `pCards`, and `generateOppCards`. The
twenty lines below each stub still read the old pools and still work.

**Not legacy-by-omission.** Zero definitions added, removed or edited since the
family engine landed; `FAM_CARDS` moved 12 times over the same span.

**One correction to my own number:** it's **133** cards, not 233. I'd counted
`{id:` matches across the whole file, which swept in boss tells and NPC entries.

**Tagged, not deleted**, per your call — and the tag is enforced:
`apv_legacy_retired.js` *calls* all three stubs (a commented-out `return []`
still greps as a `return []`) and fails if any starts dealing again.

**The one thing that genuinely isn't deletable:** NPC cards come back in P5 as
*family* cards, so the authored boss pools are the design record of what each
boss's cards mean. `tamper` is already blocked on the same phase.

**Archived too**, on your call: 157 files now at `assets/_archive/Card_ART/`,
moved with `git mv` so it reverses in one command. Nothing open here.

---

## 2. Early-game signal — waiting on a playtest, not on reasoning

Restoring the brief's 24 feats removed every feat that fired in a new player's
first hour. Ruled: nothing goes back into the feat list. The proposal is that
dialogue beats already do that job — greeting tiers, first backstory unlocks.

**Needs someone to play it.** No further argument settles it.

---

## 3. `assets/` — an art-scope call, with the risk sorted

47 live references into the previous game's tree have no replacement. Your
framing, recorded so it isn't re-derived as an undifferentiated 47:

| Group | Count | Style-mismatch risk |
|---|---|---|
| Fonts | 8 | **Lowest** — no "previous game" visual signature |
| Audio | 3 | **Lowest** |
| Character portraits | 9 | **Highest** — a player looks straight at these |
| Match frames | 8 | **Highest** |
| Night_Art UI set | 10 | **Highest** |
| Environment / menu | 9 | mixed |

**If there's only room for a subset, it's the 27 in the high-risk rows.**

---

## 4. Unplayed numbers — flagged, not trusted

Last Call's 800, and most of the restored feat conditions. They read real state
and render, but only HIGH ROLLER has fired through a live match.

---

## Everything else you answered is now work, not a question

Tracked in `NEXT_SESSION.md` and being built. Nothing there needs you.
