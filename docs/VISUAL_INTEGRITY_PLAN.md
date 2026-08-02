# The visual bugs — the same argument, one level up

Companion to `EFFECT_SYSTEM_PLAN.md`. Denis asked whether the CSS and art bugs
have a similar plan. They do, and it's **cheaper**: no rewrite, no migration,
almost entirely additive.

---

## The pattern, from today's actual bugs

Ten visual bugs in one session. Every single one **failed silently** — the page
rendered, nothing errored, and the only symptom was that something looked wrong
in a way nobody could trace.

They fall into three shapes:

### A. A lookup table that doesn't cover its domain

| | |
|---|---|
| `ASPECT` | 15 entries for 38 props. Missing → `[1,1]` → shadows drawn **square**. |
| `MATCOL` | key `corvus_ledger`, die id `corvus_ledger_d`. That relic was never tinted. And 6 of 8 relics were byte-identical to their family colour. |
| `.end-draft-slots` | I styled a class that **doesn't exist on that screen**. Two attempts wasted. |
| `FEAT_ART` | 12 entries for 32 feats — the other 20 took the loud path. |

Same failure every time: **a table and its consumers drifted, and nothing
compared them.**

### B. A rule that never reached the parser, or never won

| | |
|---|---|
| `.ptcard .lwho` | A lost `/*` made CSS error-recovery swallow the whole rule. Four rounds of "the busts are too small" were this. |
| ...and again | My own comment explaining it wrote `*/` inside a comment and re-broke it. |
| `.win-art` | Collapsed to 0×0 — `#end-ov>*{position:relative}` outranked it. |

**Written CSS is not live CSS**, and nothing checked.

### C. Asking an API about itself instead of measuring the result

| | |
|---|---|
| `_cfBlur()` | Assigned `ctx.filter` and read it back. On engines without the attribute that creates a plain property — the test answered **true on exactly the iPhones it existed to catch.** Three rounds of "no glow on my phone." |
| the human version | I reached for `--font-px` and drew a coin by hand instead of checking `Art/Assets`. Same error: trusting a belief instead of measuring what's there. |

---

## The plan

The effect proposal's principle is *content is data, not code*. The visual
analogue is **assets and styles are a manifest, and the manifest is checked.**

Nothing here changes how anything renders. It adds assertions that run.

### Phase 1 — One runner *(the same Phase 0 as the effect plan)*

There are ~20 `tools/apv_*.js` probes now and no way to run them all. One runner,
one pass/fail report. This is shared infrastructure between both plans — build it
once, both benefit.

### Phase 2 — Totality assertions on every lookup table

Each is a few lines, and each would have caught a real bug today:

- `ASPECT` covers every file in `Props/` — *caught the square shadows*
- `MATCOL` covers every `DICE_TYPES` id — *caught the untinted Ledger*
- every `FAM_LIVE` id resolves to card art — *already written* (`shoot_cardart.js`)
- `PT_ART_POOL` resolves to real portrait files
- `FEAT_ART` vs `FEATS` — *caught the 20 loud feats*
- every relic id has a `.dtype-` block — **currently fails**, none do

**Rule going in:** a lookup table keyed by id must assert it is total over that
id's source of truth, in the same commit that adds it.

### Phase 3 — Does the rule exist, *and* does it hit anything?

**Two different checks, and conflating them is what made the first version of
this plan overstate its own coverage.**

**3a — presence in the CSSOM.** `tools/apv_css_dropped.js` already does this:
walks `document.styleSheets`, asserts named selectors are present. Caught the
`.lwho` bug *and* my re-break of it. Needs a real list, not the six I
hard-coded. Plus the raw unbalanced-comment-marker scan already in it.

**3b — the selector matches something, and that something has a box.** `.lwho`
was a rule that never parsed. `.end-draft-slots` was the opposite: **it parsed
perfectly and targeted a class that does not exist on that screen.** 3a passes
it. Only `querySelectorAll(sel).length > 0` on the screen the rule is *for*
catches it — and extending that to a non-zero rendered box also catches
`.win-art` collapsing to 0×0, which otherwise relies on someone thinking to
measure.

The distinction: **3a asks whether the browser has the rule. 3b asks whether the
rule found the thing.** Two of today's bugs sat on each side of that line.

### Phase 4 — Two standing rules, enforced not remembered

1. **Verify computed, never authored.** Read `getComputedStyle` and rendered
   geometry. This is already in my memory file; today it caught the `.win-art`
   collapse in one probe after I'd have guessed wrong twice.
2. **A feature test must perform the operation and measure the result.** Never
   read a property back. `apv_glow_gate.js` is the reference implementation —
   it deletes the accessor to simulate an old engine and proves the old test
   can't tell the difference.

### Phase 5 — One asset registry

The single highest-value item, and the one that isn't a probe.

`assets/` is the **previous game's** art. `Art/Assets/` is current. Nothing in
the code says so, so every lookup is a chance to reach into the wrong one — and I
did it three times today (font, coin, diamond), after reading a memory note that
says exactly this.

**A registry** — one table mapping logical name → path, with everything else
importing from it — makes the old folder unreachable by accident rather than
merely discouraged. It also gives Phase 2 something to assert against.

---

## Why this is the cheaper of the two plans

| | Effect system | This |
|---|---|---|
| Touches game logic | Yes, ~50 pieces | No |
| Needs a migration | Yes | No |
| Half-done state | Worse than not starting | Fine — each assertion stands alone |
| Would have caught today's bugs | The 5 logic ones | **7 of 10 automatically** (see below) |
| Rollback risk | Real | None |

It's additive, incremental, and every phase is independently useful. It's also
**the prerequisite that makes the effect migration safe** — Phase 1 is the same
runner both plans need, so building it serves both.

---

## The count, named rather than rounded

The first version of this plan claimed "8 of 10" without saying which two. That
was the same sin the plan is about — an unverified claim about coverage. Here is
every one, and what actually catches it:

| # | Bug | Caught by |
|---|---|---|
| 1 | `ASPECT` 15/38 → square shadows | **2** totality |
| 2 | `MATCOL` `corvus_ledger` vs `..._d` | **2** totality |
| 3 | `FEAT_ART` 12/32 → 20 loud feats | **2** totality |
| 4 | `.ptcard .lwho` swallowed by a lost `/*` | **3a** CSSOM presence |
| 5 | my comment re-breaking the same rule | **3a** CSSOM presence |
| 6 | `.end-draft-slots` — parsed, matched nothing | **3b** selector-matches |
| 7 | `.win-art` collapsed to 0×0 | **3b** non-zero box |
| 8 | `_cfBlur` fooled on iOS | **4** — a *rule*, not an assertion. Only holds if the next feature test is written the reference way. |
| 9 | `--font-px` instead of JMH Beda | **not caught.** Nothing can tell a wrong-but-valid font from a right one. |
| 10 | hand-drawn coin and diamond | **not caught.** Phase 5's registry makes the right asset findable; it can't force its use. |

**Seven caught by assertions that run.** One by a standing rule that depends on
being followed. Two not caught at all — and both of those are the same error:
*I didn't look.* Worth naming, because it's the failure mode the tooling can't
reach and the one I made most often today.

## The boundary with the effect plan — stated, so nobody builds it twice

**This plan checks WHICH asset or rule got selected. It does not check WHEN, and
it shouldn't.**

Once visuals fire off the effect system's resolved trigger output rather than
reading state independently, timing-class visual bugs are covered *for free* by
that pipeline's ordering guarantee — Tier 2 modifiers, then Tier 1 effects, then
Observers. A visual that reads a value before it finalises (the shape of the
double-count bug, and of the "cheerful line over a voided bank" risk the lore
brief flagged) is an ordering problem, and ordering is the other plan's job by
construction.

Left unstated this reads two bad ways: either someone builds a redundant
timing-check layer here, or a reader concludes timing bugs fall between the two
plans. Neither is true. **Selection is this plan. Sequencing is that one.**

## What it does *not* fix

Taste. None of this would have told me the board text sat above the board, that
the panel should hang behind the hands, or that the score font was wrong for the
game. Those need eyes, and they needed Denis's.

What it fixes is the other kind: the bug that renders cleanly, errors nowhere,
and survives three attempts at fixing it because nothing ever said the rule
wasn't running.

**Recommendation:** Phase 1 and 2 are worth doing regardless of what happens with
the effect system — a few hours, no risk, and they'd have saved most of a day.
