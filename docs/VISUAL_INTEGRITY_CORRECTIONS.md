# Corrections to VISUAL_INTEGRITY_PLAN.md

Two fixes from a sanity check. Everything else in the plan held up.

## 1. The "8 of 10" claim needs the two named, or reduced

Nothing in the doc says which two of the ten bugs Phase 3 doesn't catch. One
likely candidate: `.end-draft-slots`. That bug wasn't a parse failure like
`.lwho` — the rule parsed fine, it just targeted a class that never existed
on that screen. CSSOM presence (walking `document.styleSheets` for named
selectors) checks that a rule made it into the parsed stylesheet, not that
its selector matches anything in the live DOM of the screen it's meant for.
Those are different checks. Only the second one catches this specific bug.

Fix: either name the two bugs explicitly, or add a fourth check — selector
actually matches an element on the target screen, not just present in some
stylesheet — and revise the count once that's in.

## 2. State the boundary with EFFECT_SYSTEM_PLAN.md directly

Once visuals fire off the effect system's resolved trigger output instead of
reading state independently, timing-class visual bugs get protection for
free from that pipeline's own ordering fix (Tier 2 before Tier 1 before
Observer). This plan's assertions check WHICH asset or rule got selected,
not WHEN — and shouldn't try to check when, because that's the other plan's
job by construction once the wiring is correct.

Add this as an explicit line in the plan. Left unstated, it reads two ways
that are both bad: either Code builds a redundant timing-check system here
that the effect plan already covers, or a reader assumes timing bugs aren't
covered by either plan and there's a real gap that doesn't actually exist.
