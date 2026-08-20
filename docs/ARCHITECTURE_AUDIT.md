# Architecture audit — system count vs. mechanical duplication (2026-08-20)

Per the brief: the question is NOT "is logic duplicated" (that war is
being won) but "has the number of genuinely separate mechanisms grown
— could any of these be rows/conditions on something that already
exists?" Verdicts below are driven: nine systems from this session's
own build-work, three verified by dedicated read passes (feats,
badge/seal family, CFX-vs-enchant dispatch). Candidates are FLAGGED,
not merged — each fold is its own design/risk decision.

## The table

| system | what it does | verdict |
|---|---|---|
| Dice/lanes (`_removeDieAt`, `_oRemoveOppDieAt`, `_lmArm` trio, trade ledger) | per-die identity that outlives the pool; the one exit path per side | **SEPARATE, confirmed.** The lane IS the identity (P565); the lane-mark trio is itself the generic primitive others ride — snuff/fog/snare are *data on it*. The file has litigated the adjacent folds and refused with stated reasons (Ward is not a lane marker 23063; Trade is an unwind ledger, not an expiry 23572). |
| CFX family engine (famFire seams, famUse) | owner-anchored card instances dispatched per lifecycle seam | **SEPARATE, confirmed** — see next row for the boundary. |
| Enchant engine (`ENCH_ICONS`, `_iconFire`, `_splitIcons`) | die-anchored brands; pre-commit legality (a zero-point keep made legal, bust redefined) | **SEPARATE from CFX, confirmed by read.** Different primitive: object-reference aliasing across three index-aligned arrays vs id+tier instances; its core job happens BEFORE any seam event exists; a fold manufactures the two-copies bug at every seat-repair site and scatters the single-site "banks zero, fires instead, never both" law. Sharing already happens where cheap (announce queue, fam-row chips, the lane-mark primitive). |
| NPC decision core (`_npcDecide`, personas, `oppShouldBank`) | the one G-free chooser; the sim drives the same core | **SEPARATE, confirmed by construction** (P772-773 built exactly this). Personas are WEIGHTS — data on the core, not systems. |
| Dialogue/traits (`_dlgPick`, `_DLG_COND`, trait pools) | one resolver, one condition vocabulary, pools as rows | **SEPARATE, confirmed — and it is the fold TARGET for others.** The `add:1` additive class (P833) is a resolver feature, not a new system. |
| cardHit taxonomy (P814/P836) | "an opponent card that takes dice or points is a hit" | **NOT a system — data on famFire.** One seam name on the existing bus; 28 fire-sites are single lines at docks; the consumer is an ordinary CFX handler. |
| Patron leveling bias (`_TRAIT_FAM`, `dieBias`, `S.run._artPersona`) | trait→family lean; the name-is-the-character registry | **NOT a system — lookup tables + a registry consumed by the existing generator.** The brief's own suspicion confirmed. |
| History-state greeting router (P839) | ledger state → which boss greeting pool | **CANDIDATE — the brief's suspicion is right.** The state→pool if/else in getLine is bespoke selection logic; three tiny `_DLG_COND` predicates (`boss_met`, `boss_wins:N`, `boss_wins_gte:N`) would express all four states as conditioned rows in ONE pool — the states are mutually exclusive, so no reliance on the specificity contest. Fold into: `_DLG_COND` + row data. Small, low-risk; awaiting the ruling. |
| Band lines + recognition beat (P833/P837) | growth dialogue by night band; first-meeting-since-band-change | **Band lines: already pure data** (`add:1` rows + `night_gte` conditions). **Recognition: separate-confirmed, minimal** — the band-state WRITE (compare-and-update on `S.run._artBand`) is genuinely new state logic (~12 lines); its line draw is already `_dlgPick`. Nothing worth folding. |
| Badges / tells / seals | the nine sealed-seat rules, eight boss tells, the badge | **ONE mechanism, three vocabularies — already consolidated.** `_tellById` one store, `_ruleActive` the one gate (verified: every effect read routes through it; the only effectful bypass is dead code), one badge renderer with per-rule CSS rows. The sealed seat and the sleeve are delivery routes, not systems. The six TRAIT seals are a word-collision: pure presentation + dialogue pool keys, no rule contact. |
| Feats | 23-row data table, one resolver, no-write proxy view | **SEPARATE, confirmed — it already has the shape this audit wants.** `evaluateFeats()` is the one resolver; `_featView`'s write-throwing proxy ("feats observe, they don't grant power") is an invariant no other system carries; award-every-passing-row semantics are incompatible with dialogue's pick-one contest. The ~14 inline `_feat*` accumulators are irreducible instrumentation, not duplicated resolution. |
| Relics/trophies | boss spoils on the shelf | **NOT a system — an array with two writers and one renderer**; relic defs are DICE_TYPES rows. Correctly trivial. |

**Count verdict:** of the eleven audited, seven are confirmed
genuinely separate with stated reasons, three are already data on
existing mechanisms (cardHit, leveling bias, relics), and exactly ONE
is a fold candidate (the P839 greeting router — built fresh the same
night the additive-resolver work proved the fold target could carry
it; the honest answer to "why not route through `_DLG_COND`" is "no
particular reason").

## Rot found in passing (bugs/debt, not folds — normal fix flow)

1. **The game-over FEATS stat counts 2 of 25 feats.** `_famFeats()`
   grants `own_reckoning` and `keg_triple` through raw ifs outside the
   FEATS roster (16428) and is the SOLE writer of
   `S.run._featsThisRun` — which the game-over screen displays (44587).
   All 23 mainline feats earned through `evaluateFeats` show as 0
   there. Fix shape: both conditions become FEATS rows; the stat reads
   the real award path.
2. **Eight orphan `_feat*` flags** written but read by no check
   (leftovers of the 32→24 roster restoration). CAUTION per flag:
   `_featMaxBank` has a non-feat consumer (npcLedger bestBank, 37548).
3. **Feat-accumulator resume gap:** the match snapshot carries no
   `_feat*` accumulator, so a mid-match reload zeroes progress toward
   the threshold feats (Slow Boiled, Full Bloom, Twice Saved, High
   Roller) — the standing resume-risk area again (12086).
4. **Stale comment** at 13144 claims `_iconFire` bypasses
   `_ruleActive` for last_call; the code reads
   `_ruleActive('zero_hour','p')` and `_RETIRED_RULES` is empty.
5. **Dead effectful bypass:** the first_strike win refund (36990) keys
   on `G._tell.id` + `totalRollCost>0`, and the drain feeding that
   state sits behind `if(false)` (32240) — dead In-Arrears economy
   still keyed to a renamed id.

## The standing habit (the going-forward piece)

Before any new feature: name the existing mechanism it could ride — a
`_dlgPick` pool + `_DLG_COND` condition, a CFX seam, an RSX flag, a
`famRenderRow` chip, an `_lmArm` marker, a FKFX meta row, a FEATS row
— and either route through it or state in the patch header why the
data shape genuinely differs. "Genuinely separate, here's why" is a
valid answer; forcing a merge to lower a count is not. (Saved to
standing memory; applies to every future feature brief.)
