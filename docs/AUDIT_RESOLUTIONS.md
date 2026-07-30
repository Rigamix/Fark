# FARK — AUDIT RESOLUTIONS

Answers to the 25-agent backlog sweep and the dice-work questions. Mirrors
the source doc's own section order for easy cross-reference. Durable rules
are now written into FARK_ENCHANT_BADGE_REWORK.md and FARK_MATCH_BRIEF.md
directly — this doc points to where, rather than repeating full reasoning.
Pure engineering/tooling calls (naming, which file owns a reset, whether to
delete a redundant tool) are marked NOT MINE — those never belonged in a
design brief and aren't repeated here as if they were design decisions.

## Dice work, this session

1. Brutus's relic face: **5, not the agent's default of 1.** Inherits
   Silver's weighted table too (was rolling fair 1-6 despite being tagged
   Silver family — treated as an oversight, not a choice). See
   FARK_ENCHANT_BADGE_REWORK.md, Brutus's relic entry.
2. Ill Omen + Whisper's Fang hoisted onto the live bust path: **confirmed,
   do it.** Both were designed with these triggers as core identity; dead
   code kept them silently one-sided this whole time. Sim-check Fang
   specifically once live — going from "never pays its cost" to "actually
   pays it" is a real nerf worth confirming still feels worth taking.
3. Rival think-beat: **lean deliberate (~400-500ms), not snappy.** Matches
   the game's characterful-NPC design; exact number wants a feel-check on
   device, not a number from a text description.
4. Victory headline: **"THE HOUSE IS YOURS."** Reject the Ambrose-reuse
   option outright — same line twice in a row reads as copy-paste on the
   single biggest moment in the game, not a callback.

## STILL WATERS vs OBSIDIAN's shatter / BREAK

5. Suppress Break's guaranteed Obsidian trigger too, not just the passive
   6% check. **Confirmed: family death-trigger IS a family trait**, Break
   doesn't invent a new mechanism, it forces the same one deterministically.
   A badge hard-countering a specific build is fine, matches Snare/Trade/Fog
   already rewarding counter-play. UNVALIDATED, needs its own sim pass.
6. Grog's Tooth: **not badge-proof, same ruling applies.** It's Obsidian
   family sharing the same mechanic; no principled reason to exempt relics.
   Its magnitude (10%/+1500 vs plain 6%/+1000) needs its OWN measurement,
   don't extrapolate from the plain-Obsidian number.
7. The other four families' suppression (already live, unvalidated):
   **yes, needs a harness pass before Still Waters goes anywhere near a
   wider build.** Jade's case is qualitatively different from the other
   three — suppressing wilds changes which combos exist, not just a bonus
   amount — flag it as its own question in the sim brief, don't assume it
   scales like Obsidian's number.
8. Badge id staying `confession` forever: **NOT MINE.** Zero player-facing
   consequence, pure maintenance-cost call.
9. Aldric's bark ("forget their breeding"): **I like it**, the pun is
   sharp and correctly scoped as flavor not mechanical explanation. Lean
   toward trimming "at mine table, sir" for snap — taste, your call either
   way.

## Art fallback (steady_hand / fair_trade + famCardArt)

10. Both real art and the permanent fallback — **not either/or, do both.**
    The fallback is infrastructure, not a stopgap for these two cards.
11. Placeholder keeps the printed name — **confirmed.** The no-baked-text
    law protects shipped art; two identical blank swatches is a worse
    failure than a temporary legible label.
12. Parchment field + colour inset border — **confirmed**, matches
    existing `.fcvTier` precedent, silver/starstone legibility conflict is
    real and sufficient reason to reject the alternative.

## 1-OR-5 FACE RESTRICTION vs the shipped random-face-draw

13. Adopt the restriction: **not close.** A brand on 2/3/4/6 is free bust
    insurance — measured 25% flat cut in single-roll bust rate, zero
    effect on 1/5 — the exact "unconditional safe keep" shape Silver's
    original identity was deleted to remove, reopened through a different
    door. Close it.
14. **Ship Phase A now. Skip Phase B (the picker) permanently, don't just
    delay it.** Every die always has both a 1 and a 5 — the picker would
    forever offer the same two buttons. Not worth the extra tap or the art
    for a 73-vs-125 EV gap that's a tuning knob, not a strategic fork. Ship
    the random 1-or-5 draw as the permanent answer.
15. Per-face pricing (old open item): **moot**, only mattered if players
    chose between faces. Closed as a side effect of #14.
16. Save migration for existing illegal-face brands: **refund and clear**,
    matching the existing `_enchV=2` precedent for cut enchants. Silently
    moving a brand to a face the player didn't pick rewrites their
    purchase without telling them.
17. Anchor's dead index bug: **leave it, note on the revival ticket.**
    Deliberately unreachable post-Vanguard-collapse; fixing dead code that
    can't execute is solving a problem that doesn't exist yet.
18. Lit-ROLL-then-NO-SCORE mixed selection: **commit accepts and scores
    the non-icon part.** Zero is the CORRECT value for an icon component,
    not an error state; a branded die must never poison an otherwise-legal
    keep. See FARK_ENCHANT_BADGE_REWORK.md's mixed-selection note.

## Brutus's relic (full patch questions)

19. Ward face and Silver-table inheritance: **see item 1 above, both
    resolved the same way.**
20. `SFX.shield` re-homed into `ward.fire` instead of deleted: **yes,
    worth the ticket.** Ward currently arms in total silence; reusing a
    well-made existing cue is cheap and matches this project's repeated
    "make consequential moments audible/visible" pattern.
21. Patch 9 hoisting Ill Omen / Fang: **see item 2, confirmed.**
22. `_iconFacesAny` letting purchased brands land on 2/3/4/6: **this is
    the same bug as item 13 — the restriction needs to apply everywhere,
    not just to the relic's hand-picked face.** Not a separate question.

## Rename _stakesRisingBonus / bank pop breakdown

23. Internal rename for symmetry: **NOT MINE**, zero design stakes.
24. Bank pop as per-source breakdown, not one lumped number: **yes, per-
    source.** Matches the established "every rule that changes a number
    shows its change at that number" principle — one lumped total hides
    why a bank was big, same failure shape as an invisible lane effect,
    just smaller.
25. Comment wording: **NOT MINE.**

## STEADY HAND

26. Emoji pop vs plain text: **keep the emoji, don't fix in isolation.**
    Four other effects already use the convention; making this the one
    exception creates a worse, visible inconsistency. If the whole
    convention needs revisiting, that's one pass across all five, not a
    piecemeal fix here.
27. Naming the card in the pop: **don't force it given the real width
    constraint.** The player's own visible card row is a persistent
    reference; this doesn't carry the "no other way to track it" urgency
    that justified the lane-marker visibility work.
28. `endPTurn` vs `startPTurn` for the disarm reset: **`endPTurn`** —
    functional correctness (covers the rival's turn too) wins over
    adjacency-to-sibling-flag. Suggest a comment at the `startPTurn` block
    pointing to where the real reset lives, so discoverability doesn't
    cost correctness.
29. Extend the targeting-ring fix to Break too: **yes.** Same visual
    collision, same underlying tension; fixing one and leaving the
    near-identical bug live in the sibling mechanic is the inconsistency
    to avoid.
30. Drop the DOM-level spin for Steady Hand: **lean yes**, the 3D tumble
    is already a real, tuned physical reroll — a second, differently-
    behaving rotation risks muddying it rather than reinforcing it. Wants
    eyes on the actual rendered result before treating as final.

## FAIR TRADE

31. Visible swap-back when the loan ends: **spend the engineering cost.**
    A die that visually still reads "borrowed" after it's mechanically the
    player's own again is exactly the state-lies-about-truth problem this
    project has refused to ship elsewhere.
32. Where "this roll" ends for tier I: **keep the current (generous)
    reading** — the choosing phase after dice settle is part of using the
    roll, not just the physical tumble. Ending it before the player can
    act on what they see would read as a bait-and-switch.
33. Refusal-line copy: **good as written**, no notes.
34. Generic fallback for other live cards' refusals: **fine for now**,
    bespoke lines are worth doing eventually, not urgent.
35. Brand belongs to the die, not the seat: **this was already decided
    (match brief's pre-match lane-planning system) — the code needs to
    catch up, not a fresh question.** Now doubly relevant given the
    Trade match-scoping correction below — see that entry.

## The dice-throw sweep tooling

36. Overlap rate (1-in-5 visible on-screen): **not acceptable, wants
    another pass.** Too much now depends on dice reading as cleanly
    separated, individually legible objects — lane markers, tap targets,
    the whole fixed-lane system all assume this.
37. Backlog-doc "zero overlaps" claim: **hold the rewrite until the
    overlap pass actually lands**, don't document a moving target twice.
38. `shoot_lanes.js`'s broken `drawnBoxes()`: **lean toward consolidating
    onto the sweep's `_hullOf` approach if genuinely redundant** — NOT
    MINE to force without knowing if it serves a distinct purpose.
39. Dead relax/spread block at `fark_proto.html:17866`: **delete it.** No
    active revival plan; same logic as Anchor — pull from git history if
    ever wanted again rather than keeping inert code live.

## PRESERVE

40. Bankable before rolling: **yes.** Card's own text says "already kept
    and scored" — past tense, done. Gating it behind a roll would
    contradict its own promise.
41. Survives hot dice: **yes.** The card's promise is about the boundary
    between turns; hot dice is a mid-turn continuation of the same turn,
    not that boundary. One die staying while the row sweeps is a feature
    (signals "this die is under a different rule"), not a bug.
42. Casing look (glow-from-within vs solid resin shell): **genuinely your
    call.** Lean toward glow-from-within, matches the warm-candlelit mood
    everywhere else in this game — but this is pure art taste.
43. NPC's Preserve getting a visible die too: **yes, eventually, not
    blocking.** The brief's language was never player-only-scoped;
    asymmetric treatment reads as two different features. Lower priority
    than the player-side fixes.
44. Inert while preserved: **correct, not a gap.** A shatter check is
    fundamentally per-roll; a die that's done rolling has nothing left to
    check against.

## Corrections issued AFTER the first answer pass

**TRADE and BREAK are both MATCH-SCOPED, not run-scoped — this reverses
an over-correction in the first pass.** "For the rest of the match" is a
bound, not a permanence claim. Full ruling now in
FARK_ENCHANT_BADGE_REWORK.md:
- Trade: the WHOLE die swaps — material and any enchant it carries —
  for the current match only; both sides' true owned loadouts fully
  restore the instant the match ends, no exceptions. No special
  "enchants never cross" carve-out needed; the earlier version of this
  ruling is superseded.
- Break: the destroyed die returns fully restored at the start of the
  player's NEXT match, not gone for the rest of the run. The section 4
  timing finding is unaffected by this clarification — it was always
  about turns remaining within a match, never about matches remaining
  in the run.
- A PRESERVED die is explicitly INERT and therefore never a legal Break
  target — stated outright now rather than left to be inferred.
