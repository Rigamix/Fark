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

### Phase 3 — CSSOM presence for load-bearing selectors

`tools/apv_css_dropped.js` already does this — it walks `document.styleSheets`
and asserts named selectors are actually present, and it caught the `.lwho` bug
*and* my re-break of it. It needs a real list, not the six I hard-coded.

Plus the raw scan for an unbalanced comment marker, which is already in it.

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
| Would have caught today's bugs | The 5 logic ones | **8 of the 10 visual ones** |
| Rollback risk | Real | None |

It's additive, incremental, and every phase is independently useful. It's also
**the prerequisite that makes the effect migration safe** — Phase 1 is the same
runner both plans need, so building it serves both.

---

## What it does *not* fix

Taste. None of this would have told me the board text sat above the board, that
the panel should hang behind the hands, or that the score font was wrong for the
game. Those need eyes, and they needed Denis's.

What it fixes is the other kind: the bug that renders cleanly, errors nowhere,
and survives three attempts at fixing it because nothing ever said the rule
wasn't running.

**Recommendation:** Phase 1 and 2 are worth doing regardless of what happens with
the effect system — a few hours, no risk, and they'd have saved most of a day.
