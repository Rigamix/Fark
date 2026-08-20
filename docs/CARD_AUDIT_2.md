# Card audit 2 — the ACTIONS audit (2026-08-19)

Denis: "You need to check card actions are actually connected to the
game. Check all cards. Again." P776 audited the words; this audits the
wires. Standard: every verdict comes from an adversarial probe — a
construction that produces a DIFFERENT answer when the mechanism is
dead — driven through the real UI seams (taps, rolls, banks), never
from a code-read. Ground truth: docs/CARD_EFFECT_SPECS_FULL.md.
Probes live at tools/apv_audit_*.js and rerun against any build.

Legend: PASS = all assertions green, no fix needed. FIXED = probe
found it broken, patch shipped, probe green after. VISUAL-DEBT =
mechanically proven, effect invisible to the player (queued for the
step-7 presentation pass).

## Verdicts

| Card | Route | Verdict | Probe / construction |
|---|---|---|---|
| stargazer | player | **FIXED (P811)** | peek→KEEP→roll: index-array peek was discarded on every real path (free-count gate); lane-keyed now; all rolled dice land on their promises |
| sleight | player→rival | PASS + VISUAL-DEBT | 12-value RNG stub: their final dice equal the REROLL batch (draws 7-12) index-for-index, not the deal batch |
| double_stakes | run | **FIXED (P812)** | measured gold: buy 10→20, payout 30→60 armed (economy honest); the ROOM seat panel never read the flag — display fixed |
| fog (enchant) | player→rival | PASS + VISUAL-DEBT | fogged lane held the table's BEST scorer; chooser kept only the visible lesser die; mark spent |
| transmute | player | PASS | die 2→5 via the real prompt flow; transmuted die selectable and SCORED (50), charge spent |
| fools_gold_f | player | PASS | keep 100 → dead roll → auto-reroll (all 5 reroll draws consumed) → dead again → bank burned exactly 100 (1000→900), charge spent |
| bloom | player | PASS | jade triple paid 800 (500+300); CONTROL triple without the jade paid exactly 500 (not always-on, not dead) |
| cultivate | player | PASS | jade triple grew lane 0 by 50 AND the grown die's next triple paid 850 (growth actually pays) |

## Queue

AMBER (preserve, honeytrap, slow_cook — tar_pit retired) → SILVER
(steady_hand, retort, reprisal) → OBSIDIAN (powder_keg,
double_or_nothing, sacrifice, short_fuse) → STARSTONE (encore,
ill_omen, falling_star) → VAGABOND (pickpocket, tamper, vanguard_f,
for_keeps) → TAVERN (the_tab, hair_of_the_dog, marked_table,
high_table). Rival routes ride the parity-era probes
(tools/_probe_actor_pipe.js and the P765 sweeps) — rerun, not retired.

## Notes for the presentation pass (step 7)

- sleight: the rival's reroll happens pre-render — needs the visible
  land-pause-reroll beat (spec doc's own requirement).
- fog: effect lives inside the AI's choice — needs the lingering
  table visual Denis asked for + a clearer description.
