# NEXT SESSION — die renderer unification

# DENIS'S DECISIONS — all seven answered, build to these

**New art landed:** `Art/Assets/Dice/Bone/texture/1..6.png`, 120x120, **pips
REMOVED**. Verified all six blank (0 dark pixels). This is now the ONLY die art.
Every other material is bone + a tint. Do NOT use the amber texture or anything
else from the old 3D dice.

1. **Pips are drawn in CODE.** Match the old look exactly for now - near-black
   flat circles with a faint ring. Build the drawing so shape is a PARAMETER:
   Denis wants pip-shape customization later.
2. **Pips do NOT tint.** The face tints with the material; the pips stay dark on
   every die. No exceptions requested.
3. **Texture-to-face is RANDOM.** The six are wear/marble variants, not numbers.
   Any face may take any of the six; randomise per die so no two look alike.
4. **Flatten all six to RGB.** None of them use transparency - drop the alpha
   channel, which also makes them lighter. (Five ship RGBA today, `6.png` RGB.)
   Optimize into `Art/Assets/Dice/Bone/texture/optimized/` - masters untouched.
5. **Chirality: standard Western convention** (1-2-3 counter-clockwise around a
   corner). One renderer means one die; this is the one.
6. **DO NOT TOUCH THE FACE LISTS. This is GAMEPLAY, not rendering.**
   Denis, verbatim in substance: iron missing a 3, flint leaning toward 4s, lead
   loaded with extra 1s are what make those dice MEAN something. Reordering any
   of them to force opposite-faces-sum-to-7 would change WHAT THOSE DICE ROLL,
   not just how the cube looks.
   So the tooltip/zoom cube showing an "impossible" die is ACCEPTED and closed -
   not a bug, and not to be fixed by pairing in the renderer either. Leave it.
7. **Build a REAL WebGL fallback with deliberate detection.** An old phone must
   silently get a working table - never a "3D unavailable" message. And the
   detection must be ON PURPOSE: today it works only because
   `new THREE.WebGLRenderer()` throws out of a script onload handler, leaving
   `ready` false, `fail` FALSE and `loading` true forever. Catch the failure,
   set `fail` properly, and make D3 the chosen path rather than the leftover one.
   That is the entire point - see the landmine section below.

Already settled earlier: the draft KEEPS its rise-and-settle; `skins.js` loses
BOTH bone and amber (everything is bone + tint now).

## What this changes about the atlas

`tools/make_cube_glb.py` currently bakes `Art/Assets/Dice/bone_N.png` (WITH
pips) into a 3x2 atlas. It must now bake the six BLANK textures instead, and the
pips move to a code pass. Note the brand/wild compositors index the sheet as
`col=(v-1)%3, row=floor((v-1)/3)` with `cw=W/3, ch=H/2` - keep the 3x2 shape or
they break.


**Ruling (Denis):** every surface shows the same die. Camera framing may differ
per surface; geometry, material, lighting and orientation may not. Lighting is
decided: flat, one multiplier per face, no specular, matching `D3.draw`'s
constant. Part of DONE is proving nothing still reaches the old renderers.

## DONE and live on `fark`

| | |
|---|---|
| P545 `5e0fae1` | `die_glb.js` wraps `die_cube.glb`. 24 verts, 12 tris, 840-byte mesh; wrapper 398KB -> 179KB. No code change needed - it is oriented to `D3X.FACE`. |
| P545 | Light rig IS `D3.draw`'s ramp: white ambient 0.55 + one white directional 0.55 along `D3.LIGHT`. Lambert under that outputs `0.55+0.55*max(0,N.L)` - the same expression, not an approximation. |
| P546 `603b412` | The GLTF fallback branch pointed at the OLD bevelled `die.glb`. Repointed. `grep "assets/models/die.glb"` is now 0. |
| P546 | D3 no longer repaints dice D3X owns. Measured 3174 -> 0 draw calls in a 2.2s window, 6/6 chips flagged. |

Tools: `make_cube_glb.py` (builds it), `check_cube_faces.py` (pixel-matches every
face against the real art), `make_cube_check.py` / `cube_check.html` (renders each
value under the game's own `FACE` table), `probe_p546_drawcount.js`.

## THE SIZE OF WHAT REMAINS — this is a CONTAINED job

Runtime-measured across 24 die-drawing sites: **15 live, 9 dead. 14 of the 15
live ones already draw through D3X.** Exactly **ONE** live surface needs a port:

**The first-night draft** (`famRunDraftShow`, `#nrDice .d3host`). It builds a
`.d3host` and calls `D3.make` directly, so `_liveChips` (which queries `.d3chip`
only) cannot see it. `#nrStage` is ALREADY in D3X's host list - the plumbing was
laid and the registration never landed.

Why it is the awkward one: the chip path builds a STILL die
(`mkDie(...,still=true)`), and the draft drives its own rise-and-settle
(`turns:0, spinMax:20`, `group:null` - not physics). It is also **the only
surface in the game where `hover` is visible at all** (on every chip surface the
DOM die is `visibility:hidden` and `D3.draw` bails on `_d3xOwned`, so the hover
breathe is a no-op), and the only live contact shadow outside the match table.
Decide whether the port keeps the animation or accepts a still die.
*(Both since settled: the animation was kept, and the shadow was measured never
to have been VISIBLE and then removed by ruling - P554. The claim above was
about the DOM, not the screen.)*

**Three surfaces I previously called stragglers are DEAD CODE:** `_renderRewardDice`
(only reachable via `showScreen('bossreward')`, which appears twice - the div and
the switch case), `#tierLoDice` and `#tierBossLoDice` (CSS `display:none
!important` under Room V2, measured width 0). Do not port them; delete or leave.

## DRAFT PORT - DONE (P553 / P553b)

Done since: pips in code (P548), per-material ink + "?" (P549/P550), chirality
verified Western (triple product +1, no change needed), skins.js retired,
the DELIBERATE WebGL fallback (P551), the unified face pass (P552), and now
the draft. **There is no die surface left on D3.**

**It was not a conversion, it was new code**, and the earlier survey undersold
it: `frame()` branches on `d.match` and EVERY tween lived inside that branch,
so a chip die was posed once at adoption by `_isoQ` and then held still. D3X
had no animation path for a non-match die at all. What landed:

| | |
|---|---|
| `D3X.chipAnim(el,opts)` | a surface asks for an intro. Stores an ABSOLUTE timestamp, so a late boot shows a die already settled rather than tumbling a second time |
| `D3X._chipAnim` | the settle (slerp from a random attitude to `rollZ * rest`, D3.easeOut) then the hover breathe. Every constant carried from the `D3.roll` call it replaces and from `D3.start`'s hover branch |
| ~~`D3X._chipShadow`~~ | built to drive `.d3shadow`, then deleted in P554 when the shadow was ruled off — see below |
| `data-anim` on the chip | hold it off screen until armed - adoption happens on frame one, arming 950ms later |
| `data-val` on the chip | `sync` reads the face at adoption, 950ms before the draft used to pick it. Drawn from the die's OWN faces list so a loaded die never shows a "?" hero face |
| CSS | `html.fk3d #nrDice .d3die` - the CUBE only. Plus `#nrDice .d3shadow{display:none}` (P554) and `#nrStage #d3xCanvas{z-index:3}` + `#famRunDraft.focus{z-index:7}` so the canvas rides with the dice |

**THE RISE CAME FOR FREE and that is why the port stayed small.** It is
`nrFloat` on the `.nrdie` TILE, and `frame()` reads the chip's rect every frame,
so the 3D die inherits the tile's scale and translate exactly. Only the SETTLE
needed writing.

**P553b exists because I asked P551's question of my own patch**: does the hold
end because something ENDS it, or because the thing that would strand it happens
not to occur? It was the second. Adoption is also the moment `sync` adds
`fk3d` and hides the DOM cube, so an arming call that never arrives means
nothing draws the die - the empty-sockets failure this file warned about, newly
reachable. The hold now has a 2500ms deadline and an unarmed chip falls through
to a still die. Found by reasoning, not by seeing it.

**P553c came out of the probe, not out of reading.** Letting go of a focused die
flicked it: the 450ms return ease slerps to `rest`, but an animated die holds
`rest` PLUS the settle's permanent in-plane roll, so the frame after the ease
finished moved it the rest of the way in one step. Sampled at 40ms:
`.0703 .0961 .0335 .0210 .0100 .0052 .0000` then **`.0485`** at 521ms, against
`.0004` for the breathe either side. The ease now targets the held pose.

And the first version of that probe was wrong in my favour - it took the largest
step anywhere and found `.1034` at 160ms, which was the ease legitimately moving
fast. Right conclusion, wrong evidence; a threshold that fires on a working
animation would have gone on firing after the fix.

Three probes, all green, all driving the real screen:
* `probe_p553_draft_port.js` - adoption on `#nrStage`, DOM cube hidden while its
  shadow is kept and `_d3xOwned` set, both renderers agreeing on the face, and
  the quaternion + Y still moving 3.5s in. Stable over three runs.
* `probe_p553_draft_degrade.js` - the two ways it can lose the 3D die. Arm B
  stubs `chipAnim` to a no-op: held 3/3 at 1.5s, then all three drawn and STILL
  past the deadline. Arm A denies `getContext('webgl')`: `fail` set, `fk3d` off,
  three visible DOM cubes, 0 owned, all three animating - the `D3.roll` call was
  deliberately kept beside the D3X one for exactly this.
* `probe_p553_draft_focus.js` - the interactive half. Tap: one die drawn, 2.36x,
  turning. Layers: canvas z7 over scrim z5, panel z8 over the canvas. Let go:
  smooth to `.0014`. Take: the overlay goes.
* `probe_p553_draft_real_entry.js` - **the one that reaches the screen the way a
  player does**, `startNewRun()` then `showScreen('gauntlet')`, letting
  `renderTier` open the draft. The other three call `famRunDraftShow()` by hand
  and therefore never put the tier screen underneath. That matters because
  `sync` lets `chips[0]` - the first live chip in DOCUMENT ORDER - choose the
  host for all of them, skips every chip outside it, and adds `fk3d`
  unconditionally. One sized `.d3chip` on the tier screen sorting before the
  overlay would hide the draft's cubes with nobody drawing them.
  **Measured on the real path: 3 live chips on the page, all three the draft's,
  `foreign: []`.** So the hazard is not live - and this probe is now the guard,
  failing with the competing chips named rather than leaving it to be noticed.

**The contact shadow is GONE (P554), and that closed one of the three things
this file said a port had to preserve.** It was measured never to have reached
a player - entirely behind the die on both renderers, −1.1px clear at best
before the port and −5.5px after, each using its own renderer's silhouette.
Offered to Denis as move-it-or-drop-it; **ruled: drop it.**

The rule is `#nrDice .d3shadow{display:none}` and it is CSS **on purpose**:
there are two renderers on this screen, and D3X simply not drawing a shadow
would have left the DOM die's ellipse showing on a WebGL-less device - the one
device this screen must not look broken on. `_chipShadow` was deleted with it.

Carry the lesson, not just the fact: *live in the DOM* is not *visible*, and
this file had asserted the second from the first.

**One visible change worth knowing about:** the die is now 0.80 of its host box,
not 0.72, because that is D3X's chip factor everywhere else and the DOM shadow
has to sit under whichever renderer is drawing. About 11% bigger than before.

## THE ONE THING THAT MUST BE READ BEFORE DELETING D3

**D3 IS THE FALLBACK ON PURPOSE NOW (P551), AND THAT IS WHY IT STAYS.** It used
to be the fallback BY ACCIDENT, through a hang: `_init` built a WebGLRenderer on
its first line outside any try/catch, so on a device where that threw, `ready`
stayed false, **`fail` stayed FALSE**, `loading` stayed true forever, and
`html.fk3d` was never added - the CSS die stayed visible and the game worked
because the exception stopped the code before it could hide anything.

`_giveUp` is now the single exit, `boot` refuses to retry after a real failure,
and `webglcontextlost` routes into the same place. **The historical warning
still applies to anything NEW: a patch that adds a `fail` check to `mkDie`, or
that "tidies" `_giveUp` into a plain catch that lets `sync` run, turns a
WebGL-less device into a blank table.** The draft is now the sharpest case -
`probe_p553_draft_degrade.js` arm A is the test that says so.

## THE DRAFT HAZARD - CLOSED TWICE (P547 scoped it, P553 ported the surface)

The original rule was `html.fk3d .d3chip .die, html.fk3d .nrdie .d3host .die` -
a hide clause written for a port that never landed, so under `fk3d` the draft's
dice were hidden with nothing drawing them. It was safe only because `fk3d`
happened to be OFF on that screen. **Correct by coincidence, not by design**, and
anything that left `fk3d` on while the draft was up - a surface that failed to
detach, a future screen keeping a chip alive - showed three empty sockets on the
first screen of a new run.

P547 scoped the rule to `.d3chip`. P553 ported the surface and put a clause back,
narrower: `html.fk3d #nrDice .d3die`, the CUBE only. P554 then took the shadow
off this surface entirely, so `.d3shadow` there is `display:none` rather than
merely unhidden.

**Worth recording: the old `.nrdie .d3host .die` clause matched NOTHING.** This
surface has never had a `.die` element - `D3.make` appends a `.d3slot`. So the
hazard as originally written was not live, and `probe_p547_draft_hide.js` passed
by reading `.d3slot` visibility, which no rule has ever touched. The shape of the
danger was real and the specific mechanism was not; both halves are true and the
doc said only the first.

That probe is now superseded - it asserts the draft's dice stay visible under
`fk3d`, which is deliberately half-false since P553. `probe_p553_draft_port.js`
is the one that means something.

## CARD-SLOT SWEEP (P555) — the resume loses what the rival paid for

The integrity plan's largest named gap, closed. **It found a defect, and not the
one the item predicted** — worth saying plainly, because the predicted half was
checked and is clean.

**Index desync: CLEAN, verified not assumed.** `famRenderRow` emits
`famCardTap(i)` with the SOURCE-ARRAY index from its `forEach` over `G.pF`, not
a count of rendered cards, so its two skipping `return`s cannot shift it.
`famUse(i)` reads `G.pF[i]`. The positional-index smell the plan named is not a
bug.

**The desync is in TIME.** P511 taught the snapshot to carry `pF`/`oF` — the
CHARGES — and never carried the FLAGS those charges buy. That is worse than
carrying neither: before P511 the charge came back with the effect, so the two
at least agreed. Driven through `_npcArmActives`, then the RESUME MATCH button:
sleight and ill_omen both went `2 → 1` with their flags set, and came back with
charge `1` and **no flag**. Two controls on the same reload — spent charges
stayed spent, `_oGrudgeStack` came back at 3 — so it is not a broken restore.

The window is not exotic: `saveMatchState()` is the **last statement of
`startPTurn`**, and both flags are armed in the rival's preceding turn and
consumed after it. Every ordinary turn boundary lands inside it.

**SCOPE CORRECTION, made after the fact.** P555's commit message implies nine
live losses. It is **six**, and the difference is reachability: the snapshot has
**one writer and one call site** — the last statement of `startPTurn` — so a
field only matters here if it can be non-default at that instant.

| field | reachable at snapshot time? |
|---|---|
| `_oSleight`, `_oIllOmen` | **yes** — armed in the rival's preceding turn. Driven. |
| `_famBankCount`, `_famMinBank` | **yes** — accumulate, never reset mid-match |
| `_famSleight`, `_famKegTriple` | **yes** — once-per-match latches with *no clear site at all* |
| `_famPeekVals`, `_famHoneyVal` | no — armed mid-turn, and P556 now clears them at both turn boundaries, so they are provably null here |
| `_famIllOmen` | no — armed in the player's turn, consumed in the rival's, so null by the next `startPTurn` |

The two latches are worth their own line: `_famSleight`'s `canUse` gates on
`!G._famSleight` and nothing ever clears it, so losing it on resume **re-enabled
a spent Sleight** — a second savescum in the player's favour, found only by
asking the reachability question of my own patch. `_famKegTriple` is the
`keg_triple` feat's latch; losing it dropped earned progress.

Nine fields cross a resume. Restored with `!==undefined`, **not `||`** —
`_famBankCount` and `_famMinBank` are numbers that are legitimately 0, and the
count seeds "is this your FIRST bank" (Hair of the Dog). The probe's falsy arm
poisons them to 99 before reloading and asserts they come back **0**, because
every other check arms something first and would pass on a `||` restore too.

`tools/card_state_census.py` is the instrument and is worth re-running after any
card work: it derives turn-scope from **each write's enclosing function** rather
than from a hand list of turn functions. Its first version hard-coded
`startPTurn`/`_turnTableClear`/`doBust`, missed `runOppTurn`, and reported 37 of
48 fields at risk. The real number was 8. A hand list of "the functions I
thought of" is the same instrument class this sweep exists to catch.

**Still open in this area:** `CFX.tamper` mutating opponent card instances, and
`S.run.cards` / the equip and tier UIs.

## {mat, ench} IS A NEAR-INVARIANT — census, not discovery (P560)

Three defects have been the same omission (D6b's preserve capture, D11's four
swaps, D10a's Fair Trade loan), so the rest were **enumerated instead of waited
for**. A die's identity in this file is *material and brand together* — the sites
that get it right say so: kept-group dice entries are `{val,mat,ench}`,
`_removeDieAt`'s `_diceOut` is `{lane,mat,ench}`, Trade ledgers the brand.

Two sweeps. `mat:` literals with no `ench:` — 24 hits, **22 correctly not bugs**:
shop catalogue rows (price/stock/label — a listing, not a die), renderer option
bags, `G.oppDice` (no opponent-side enchants, documented), and payout rows
carrying `dice:[]`. And `mkDie` arity — 17 sites, **6 already pass the enchant**,
one correctly does not.

Two real, both fixed:

* **Last Stand** built its kept group from a live pool die and dropped `d.ench`.
  Behavioural — the kept group is what `_keptScorers`, `CFX.preserve.use` and
  every icon check read. Its own gate is `!_dieIsIcon(free[0])`, so the die is
  branded on a face it is *not* showing: exactly D6(b)'s case, second site.
* **The kept tray** called `mkDie(val, mat, 'sm', true)` — four arguments, so a
  branded kept die was drawn with no brand while `dd.ench` sat right there. Same
  hardcoded-fifth-argument shape P559 fixed in the preserve restore.

**One non-finding worth keeping**, because it looks identical and is not: the
tray's `k.vals.map(v => ({val:v, mat:k.mat}))` fallback has no `ench` either —
but `vals` carries no per-die data at all, so nothing was dropped. The field was
never there.

**Deliberately not touched:** the shop, loadout-panel and tier-roster previews
(31808, 31866, 34960, 34998, 35918, 36511) also call `mkDie` with four
arguments. They render from a *material alone* — a purchasable, a roster entry —
so showing a brand needs `S.run.dieEnch` plumbed in. That is a design question
about what roster views show, not this defect.

## SUITE STATE — 47 pass, 2 fail, 0 error, 1 skip, 1 indet

First full run in a while. **Neither failure came from the die work**, and both
were the same shape, so it is worth naming rather than just fixing:

`apv_ench_align :: allSitesFixed` and
`apv_lane_integrity :: everySpliceSiteSyncsNumDiceInSource` both guarded "a die
removal keeps its parallel arrays in step" by **counting `G.matchDice.splice(`
sites and checking each one**. Written when there were four. Removal was later
consolidated into `_removeDieAt` (PR5), so both counters found **zero** sites in
the functions they searched, and both were phrased `sites.length > 0 && every()`
— zero fails. The second also required `G.numDice =` near the splice, and that
assignment had been deliberately replaced by `_dropLanes(1)` (P516: assigning
`matchDice.length` refunded every per-turn dice penalty).

**The refactor that made the property structural is what blinded the probes
guarding it.** Both now ask the stronger question the consolidation makes
askable — *is there only one site* — and then RUN it: `_removeDieAt` on a
branded board leaves the brand on `amber` with lengths `[5,5]`, and on the live
match takes `numDice` and `matchDice` 6→5 together. The old excuse for being
structural ("firing four removal mechanics live is a much bigger harness") died
with the fourth mechanic.

The skip (`apv_break_doublepush`) and the indet (`apv_pturn_value ::
liveBankReal=null`) are setup-dependence under CPU contention — `apv_pturn_value`
is green standalone (`turnPtsBeforeBank:450`). A skip measured nothing; neither
is a regression.

## STILL OPEN

- **The retirement checklist is now the live question.** D3 no longer draws any
  surface, but it is still (a) the WebGL-failure fallback, deliberately, and
  (b) the animator the draft falls back to. R3, the grid-pip CSS cube, is still
  live via the die tooltip. So D3 is not deletable and R3 is the next renderer
  to look at, not D3.
- **D3X keeps its die records after a chip surface closes.** Found while
  probing the draft, then checked against the loadout on the same page so it
  would not be blamed on the port: **loadout 6 open / 6 after close, draft 3 /
  3.** It is D3X's lifecycle, not the draft's. `tick`'s no-live-chips branch
  falls into `syncMatch`, which returns early without detaching when `_matchOn`
  is already false, so the records survive until the next `sync` filters them.
  Bounded - three undisposed materials and a detached canvas until the next
  chip surface opens, and `frame()` bails on `!mount.isConnected` meanwhile -
  but it is a parallel exit path on a lifecycle op, which is the shape that has
  bitten before. One canonical teardown, or an explicit detach in that branch.
- `.dtype-*` face pairing: both grid-pip builders index `dice.faces` by array
  POSITION, so opposite faces never sum to 7. Largest-with-smallest fixes the 14
  materials whose multiset is {1..6}; for the other 10 no arrangement can. Design
  call. **Do NOT reorder `DICE_TYPES.faces`** - seven display sites join it in
  stored order and rely on ascending.
- `skins.js` bone and amber are baked for the 16% bevel at 87% island coverage.
  On a hard cube that paints a flat frame around each face. Re-bake, or delete
  the two entries and let them fall through to the atlas + MATCOL tint.
- `D3.TINT` (12 materials) vs `MATCOL` (22): brass, crystal and the eight relics
  render untinted wherever D3 draws. Reachability still unestablished.
- Retirement checklist is NOT satisfied. D3 still draws the draft and is the
  fallback; R3 (grid-pip cube) is live via the die tooltip.


---

# Previous

# Handover — start here

Written before a context compaction. Everything needed to pick up cleanly.

**Deployed HEAD: `ec6d569` on branch `fark`. Backup tag: `pre-effect-system`
(`a0aed7d`) — the last commit before the plan work began.**

---

## 0. READ THIS FIRST - the state, and what is waiting on you

**The patron card layer is LIVE.** `generateOppCards` used to begin
`return [];` - a P1-cutover stub that made `G.oCards` permanently empty. **P473
lifted it**, so all 41 pooled patron cards are dealt for the first time since
that cutover.

**Measured on its own** (`OPPCARDS_LIFT_MEASURED.md`), five seeds, same-seed
before/after: win rate falls 0.8-3.8 points at every tier that draws cards, and
**tier 0 is identical to the decimal** - it is the one tier whose patrons have no
card pool, so it is the control, and it held. Bosses are genuinely stronger.
The `spread` column moved too and is **not** reportable - see `SPREAD_AUDIT.md`.

**Still two different systems, and the doc below blurs them:**

| layer | state |
|---|---|
| **family cards** - `G.oF`, CFX, `_famInitOpp` | works |
| **NPC cards** - `G.oCards`, `mechanic===` | **now works too** (P473) |

### Waiting on a ruling - nothing is blocked

- **`OPEN.md` §8** - `blessed_dice` / `crown_authority` say "reroll", the code
  wipes the kept dice and turn points. Text or code, both defensible.
- **`commit`** - the last ungated seam, 7 of 8 raise. Its payload describes the
  shape of a *selection*, and the rival scores a roll and banks instead.
  `SEAM_TWO_LEFT.md`.

### Done since this doc was written

The **effect-system plan is finished** - all six phases, re-planned at its own
checkpoint (`EFFECT_PLAN_REPLAN.md`). Phase 5 (Observers) measured and pinned by
`apv_observers`. Five mechanic tables shipped and the remaining 13 single-site
mechanics **deliberately not** tabulated (`TABLE_BAR.md` - the bar is *removes a
copy*). Law 6 (symmetry by default) is in the brief with its two named
exceptions. The **card audit is complete** - six passes, one finding
(`CARD_AUDIT.md`).

### The habit worth carrying in

Instruments were wrong more than a dozen times last session and **every one
measured something adjacent to the question** - timing delays read as rule
parameters, lines as statements, a captured block missing the condition that
gated it, a regex holding a literal backspace byte. Standing checks:

- **a unanimous result or a zero delta is a tell, not a finding** - three
  identical sim runs are what uncovered the P1 stub
- **ask what a checker can SEE before trusting what it says** - three separate
  coverage gaps were found that way, one of them inside the tool written to
  catch coverage gaps
- **before changing a stub or guard, grep what references it**, not only what it
  references

**Two different systems, and the doc below blurs them:**

| layer | state |
|---|---|
| **family cards** — `G.oF`, CFX, `_famInitOpp` | **works.** A boss really does hold 1–3 |
| **NPC cards** — `G.oCards`, `mechanic===` branches | **off.** The list is never populated |

So every `mechanic===` branch inside a `G.oCards` loop is unreachable today.
`G.pCards` branches are live once the player holds cards. **Before calling any
`mechanic` branch a live bug, check which list gates it** —
`tools/reach_audit.py` answers it per site.

### Phase 5 (Observers) is DONE

Measured, not assumed: 23 feat checks all invoked through `_featView`, none
reading a field it does not carry; `DLG` reads two fields, writes `G` zero
times, and is push-based. Both halves already held — what was missing was that
**nothing asserted them**. `apv_observers` now pins six properties including a
real runtime write test. See `P5_OBSERVERS.md`.

### What last session built

**Live now:** Law 6 (symmetry by default) in the brief with its two named
exceptions; five mechanic tables (`WILD_LEVEL`, `BANK_FX`, `BANK_TAKE`/
`SCORE_DRAIN`, `BUST_FX`); the `challenge` double-charge fixed on both seats;
`ill_omen` migrated to one site reading "scored nothing"; the `rivalTurn` seam
mirrored with a real turn value.

**Built, waiting on the stub:** `_oppFxOwnA/B/Player/Drain` extracted from
`finOpp` and wired into `tools/sim_harness.js`, plus a real latent fix — the
harness read `rung.cards`, a field **no rung has**. All correct; none of it
moves a number until the `return [];` lifts.

### Three docs that save re-deriving anything

- **`REACH_AUDIT.md`** — which of last session's fixes change a match today (8 of 10), per site
- **`OCARDS_STUBBED.md`** — the stub, and what it means for the mirror-pair work
- **`SPREAD_AUDIT.md`** — where the `spread` statistic holds and where it structurally cannot

### The one habit worth carrying in

Eight instruments were wrong last session and **every one measured something
adjacent to the question** — timing delays read as rule parameters, field names
as behaviour, lines as statements, a captured block missing the condition that
gated it. Standing check on any new tool: *does what it measures share a name
with the real thing, or is it the real thing?* And **a unanimous result or a
zero delta is a tell, not a finding** — three identical sim runs are what
uncovered the stub above.

---

## 1. THE NEXT TASK — Phase 5, and nothing is blocking

Phase 4 is done: the nine read by hand, three seams built (`commit`,
`deadRoll`, `rivalTurn`), the run-scoped domain measured and built
(`matchArmed` + `_rs*`), and the suite is fully green for the first time.
`docs/PHASE4_MIGRATION.md` and `docs/RUNSCOPE_SEAMS.md` carry the reasoning,
including three findings that were argued DOWN by reading the actual lines.

**Phase 5 — Observers** is next in `EFFECT_SYSTEM_PLAN.md`, and it is also
where NPC family cards land. **Not** because `G.oF` is empty — an older comment
said so and it is wrong; `_famInitOpp` already deals a boss 1–3 cards. The gap
is that the opponent's turn raises only three of eight CFX seams, so most of
those cards have no moment to fire at. `docs/P5_NPC_CARDS.md`.

**Before starting it, read `docs/PHASE4_MIGRATION.md`'s instrument notes.**
Phase 4 spent more time correcting its own tools than writing game code, and
every one of those corrections is a trap Phase 5 can walk into unchanged.

---

## 1z. SUPERSEDED — Phase 4: read the nine by hand

**Start here, and read them one at a time.** `docs/PHASE4_MIGRATION.md` carries
a retraction: the "group 1 is clean" result was wrong, `short_fuse` is half-on,
and two automated passes in a row produced numbers that did not hold.

**The nine cards with unexplained sites** (after `_npcFamCard` opponent-side and
`_SEAL_POOL` name-collision sites were separated, both eye-verified):
`fools_gold_f`, `slow_cook`, `retort`, `double_or_nothing`, `short_fuse`,
`encore`, `ill_omen`, `sleight`, `pickpocket`.

**Do NOT reach for a third classifier pass.** The instrument has been wrong in
both directions on this exact question; the sites are few enough to read.
`tools/cfx_bespoke.py` locates them, and that is all it should be trusted for.

**Then the five-card build**, which is confirmed and unstarted: `bloom`,
`cultivate` and `vanguard_f` all live in `famCommitBonus` and need a `commit`
hook — which `short_fuse`'s x2 wants too, so resolving the retraction and
designing that hook are the same job. `for_keeps` is a seat-launch wager with no
match-scoped effect, and `tar_pit` has no implementation and is off `FAM_LIVE`;
both need reading before they are assumed migratable.

**And name the five tavern cards off-bus IN CODE, with the reason** — run-scoped,
not match-scoped — so a later pass does not read "not migrated yet" and try to
finish the job. Ruled 2026-08-03.

---

## 1a. DONE — Effect Phase 3 (lane markers BUILT; see EFFECT_LIFETIME.md)

**BUILT (`P444`):** the lane-marker lifetime — `_lmArm` / `_lmDue` / `_lmSpend`
/ `_lmRetire`, with the window gate inside `_lmDue` so it cannot be skipped.
Snare, Snuff and Fog migrated. `apv_lane_lifetime.js`, 10 checks.

**Snuff now gates on its armed turn.** Building the primitive forced the
decision the measurement deliberately left open. Verified behaviour-identical
on the live path (`dueOnArmedTurn`) and different only where `live`-alone would
wrongly have fired (`notDueOnLaterTurn`).

**Snare keeps a separate verb.** `_lmRetire` ≠ `_lmSpend`: Snare is consumed on
the bite, and folding it into the turn counter would have handed it a second
turn — the exact wager its own comment says it must not have.

**STILL OPEN: Trade.** Excluded in writing at the primitive. Nothing to build.

**The measurement is done and it corrected the plan.** `docs/EFFECT_LIFETIME.md`
+ `tools/effect_lifetime.py`. Three findings that change what Phase 3 builds:

- **Trade is NOT a lane marker.** The plan groups it with Snare/Snuff/Fog; it is
  an array of swap records with an undo, no `live`, no `turn`, no window, and it
  snapshots across a save. A primitive built from the lane markers and applied
  to it would impose a window on something designed not to have one.
- **Snuff writes a window field it never reads.** All three lane markers arm
  `{lane, live, turn}`; snare and fog gate on `turn===oppTurnCount`, snuff gates
  on `live` alone. Not a demonstrable live bug — `oppTurnCount` increments
  before the check, so the paths coincide today. Left unfixed ON PURPOSE: it is
  a behaviour change on Kindred's two-turn hold and belongs with the primitive.
- **Ward: I got this one wrong, then corrected it.** The audit grouped by name
  prefix and reported Ward's retirement as scattered. `_ward` is a prefix shared
  by THREE unrelated features — the enchant (`_wardArmed`/`_wardBoost`, one
  turn), the `warded` card's persistent charge pool (`_wardCharges`), and a
  bank counter (`_wardBanks`). The enchant's two expiry sites are both correct:
  `doBust` is CONSUMED, `startPTurn` is EXPIRED. Nothing distributed to fix;
  Phase 3 item 2 is **withdrawn**, and the naming it actually needed is done.

---

## 1y. SUPERSEDED — Effect Phase 3, the original framing

**The whole queue cleared.** famLog, rules audit, props brief, Preserve,
cap-endings, the sim re-run, the Break rows, and Effect Phase 2 in both halves.
Reports in `docs/PHASE_REPORTS.md`; the measurement docs are
`SIM_RERUN_2026-08-03.md`, `BREAK_ROWS_2026-08-03.md`,
`EFFECT_PHASE2_GUARDS.md`, `TURNSTATE_CLEARING.md`.

**Phase 3 is the resolver and the ordering rule** — re-scoped by Phase 1's
ruling, so read `EFFECT_SYSTEM_PLAN.md`'s banner before starting:

- **It does NOT settle a multiplier rule.** Nothing multiplies. Kindred is five
  hand-authored alternate definitions sharing a name.
- **It settles EFFECT LIFETIME instead** — Ward's armed window, and Snare /
  Snuff / Fog / Trade, which are lane markers with a placement, a window and an
  expiry rather than effects with a moment.
- **Two constraints are already discovered and must survive it:** guards may
  have side effects (`powder_keg.use` spends a bust save, so nothing may be
  evaluated speculatively or shared), and a restore into a fresh turn belongs
  after `_turnTableClear()` — a boundary found twice, independently.

### What Phase 2 actually delivered, including what it declined to build

`_fxMine(ev)` across 9 sites — and **three inline `ev.owner==='p'` checks left
alone**, because that form omits `ev.mine` and therefore also fires when the
RIVAL is the actor. Whether that is intended is an open BEHAVIOUR question,
named at the site rather than resolved by tidying.

**No `_fxFreeDice()`, deliberately.** `!free.length` looked like a shared query;
the sets are four different things, and folding them would have taken Powder
Keg's "kept dice included" away from it.

**Two named clear phases**, not the single `endTurnState(reason)` that was
proposed before the branch trace. Nine paths clear in two stages with the path's
own work in the gap, so a single wrapper could not express it.

---

## 1c. HOW FAR ALONG — say it in units, never as one number

Two strands, two different questions. **Do not blend them and do not put two
percentages next to each other** — a table of percentages is what produced a
blended "70%" that matched none of its own rows.

> **85% of the behaviour is built. The shared machinery it runs on is two
> phases into five, with one condition lifted and no effect application yet.**

- **Behaviour** — the enchant/badge rework's own §6 checklist: Silver reworked,
  Ward/Insurance retired, three enchants cut, seven icon enchants firing through
  one rule, Break's death rows, four badge remaps, the face restriction, the
  feat roster. Enumerable, mostly shipped, **~20% validated** — only Obsidian's
  Break row has sim numbers and almost nothing has been played.
- **Machinery** — the effect system. **2 of 5 phases.** Phase 1 mapped it;
  Phase 2 built the one condition the content actually asks for (`_fxMine`) and
  named the two clear phases. Still no shared EFFECT APPLICATION, and Phase 3
  (lifetime) is where the lane-markers get a model. Say "2 of 5 phases, one
  shared condition, no shared application" rather than a percentage.

**Denominators:** 69 items exist, ~65 are player-reachable. Totality assertions
use 69; migration progress uses 65. See `EFFECT_INVENTORY.md` §1.

---

## 2. AFTER THAT

- ~~Fix the two remaining Phase 2 reds~~ **DONE, and this entry was right in a
  way I then contradicted.** The 8 relic `.dtype-` blocks are added (derived
  from each relic's MATCOL tint). `MATCOL` gained brass and crystal, and the
  probe's domain now excludes `dep:true` dice (jade3, ruby) by the game's own
  retirement flag.
  **But I claimed brass/crystal were reachable via patron `dieBias` and they
  are not** — `dieBias` filters `ps.dicePool`, and no patron pool contains
  either. This file said "still not reachable" and was correct; I contradicted
  it without reconciling first. The entries stay (a tint costs nothing, and is
  right the moment either enters a pool), but they are not a live-bug fix.
  **Still open:** whether the SHOP can sell them. Unverified either way.
  **And a real find in passing:** the `ones` persona's `dieBias` names brass
  and crystal and the `hoard` persona names crystal — none of which is in any
  `dicePool`, so those bias entries select nothing.
- ~~superseded~~ The original note read: I said migration converts them on load before any render. The real
  reason, measured: `brass` and `crystal` are handed out only by
  `generateDiceLoadout`, which is called only by `initBossRewardScreen`, and
  **nothing calls `showScreen('bossreward')`** — that screen has no entry point.
  The conclusion held; the justification did not, and a right answer resting on
  a wrong reason breaks silently the moment someone wires that screen back up.
- **The two stale asset paths** Phase 5 named and did not touch:
  `Environment_ART/gameover.png` (its only twin is a `.psd`) and
  `Menu_Art/Settings.png` (twin at `Art/Assets/Panels/Settings/settings.png`).
  Swapping them is a look change, so it's Denis's call.
- **`assets/` has no owner.** 47 live dependencies with no replacement in the
  current tree — every font, all audio, nine character portraits, eight match
  frames, the Night_Art UI set. Whether those get redrawn is an art decision
  nobody has made.

---

## 1b. DONE — the feat roster migration (`d6772fc`)

Ruled, built, deployed. `FEAT_ART` is **23/23**, measured both directions.
Full write-up in `docs/PHASE_REPORTS.md` Phase 4; `archive/FEAT_DISCREPANCIES.md` now
carries a correction header.

**What it turned up that the discrepancy doc had missed:** there were **four**
rosters, not two. `_famFeats` was granting five feats with no art — invisible,
forever — and `FTEXT` held twelve authored descriptions that outranked the live
condition on the wall. Also `first_blood` awarded for the first **match** of a
run rather than the first **boss**, so its painting hung for beating a drunk.

**All five decisions ruled**, one changed code (`37eff42`): STICKY FINGERS
moved off amber and back to **Vagabond's break-row steal** — the name is a
thief, not something that holds. NO CLAIM shipped as written. The
Death&Taxes / Own the Night overlap stands. Bookkeeper's painting stays unused.

**One is settled only halfway and is worth carrying forward.** The early-run
drip-feed: ruled that **nothing goes back into the feat list** — that would be
the same drift this migration removed. But the underlying tension (design law
says feats are rare and never for sale; prior playtest feedback said
progression was too slow) is unresolved, and the answer, if there is one,
belongs in circles / gold / first-badge progress, not in loosening feat
scarcity.

**And the parse gate was not gating.** Its default argument pointed at an
untracked scratch build frozen since 31 July, so every bare invocation reported
PASS on a file none of the session's patches touched. Fixed in `37eff42` —
default is the game, missing file exits 1, and the file read is printed with
its mtime. Nothing was damaged; the live file compiles clean.

---

## 3. BLOCKED ON DENIS

**Nothing blocks the next task.** All four items that used to sit here were
answered and are now built — the enchant/badge brief arrived, Zero Hour went to
Mabel, Last Call was retuned to 800, boss counters and greetings are per-run.
See Phase 4b in `docs/PHASE_REPORTS.md`.

What is genuinely open, none of it blocking:

1. **The early-run drip-feed.** Ruled that nothing goes back into the feat list.
   Where the early signal comes from instead is unresolved — the proposal is
   that dialogue beats (greeting tiers, first backstory unlocks, the King
   thread's intro) already do that job, flagged as needing a real playtest
   reaction rather than reasoning.
2. **The two stale asset paths** and **`assets/` having no owner** — see §2.
3. **Three recycled ids are gone, but the pattern isn't.** All eight badge ids
   now match their rules. The thing to keep in mind: a `_RETIRED_RULES` entry
   naming an old rule silently kills the NEW rule wearing its id, everywhere
   except the boss's own badge. That table is empty now. Keep it that way unless
   the replacement genuinely does not exist yet.
4. **Numbers that are unplayed:** Last Call's 800, and most of the restored feat
   conditions. They read real state and the wall renders, but only HIGH ROLLER
   has fired through a live match.

---

## 4. GOTCHAS THAT COST TIME TODAY — do not relearn these

**Deploy:** commit in the worktree → `cd` to root → `git merge --ff-only
claude/zen-chatterjee-f04c42` → `git push origin fark`. If the merge aborts on
untracked files, hash-compare them first (`git hash-object` vs `git rev-parse
BRANCH:path`), then remove and re-merge. **Never push to `main`.**

**Never `git add -A`.** Denis generates art into `Art/` mid-session. Stage
explicit paths only.

**USE `FK_ART`. It is the answer to "where does X live", and it exists because
this exact question kept being answered wrong.** One table near the top of the
script: 21 entries, both trees, with the old-tree ones marked deliberate. Add to
it rather than writing a raw path — `apv_asset_registry` fetches every entry, so
a rotted one fails on the next run.

**`assets/` is NOT dead**, and the flat rule I wrote here myself was wrong.
Measured: 47 live references into it have **no replacement anywhere** in the
current tree — every font, all audio, nine character portraits, eight match
frames, the Night_Art UI set. `'JMH Beda'` loads from
`assets/_mockups/new_main/`. "Never look in `assets/`" would break the page.

The true rule is narrower: **new art goes in `Art/Assets/`.** The three mistakes
that produced the flat rule (font, coin, diamond) were about *art*, not the
folder. `--font-px` is still the old pixel font and still the wrong reach —
`FK_ART.font` is the right one.

**WRITE THE PATCH AS THE VERIFICATION STEP.** Three findings on 2026-08-03
were disqualified at exactly one moment, and it was the same moment each time:

  endMatch      ranked first as a seam by touch-count (4 cards). Writing the
                patch meant reading the positions - 6% to 98% across 619 lines.
                A shared FUNCTION, not a shared moment.
  the classifier `` through a heredoc became a backspace byte. Fixing the
                file meant looking at the bytes.
  seatCommit    3 cards, tight by percentage. Writing the patch meant reading
                the lines between them, which turned out to be load-bearing.

**This is not "patch-writing is a lucky place to catch bugs."** It is the one
step where a description gets tested against the literal text instead of a
summary of it. Everything upstream - the ranking, the percentages, the counts,
the seam-count assumption - is reasoning ABOUT the code. Writing the patch is
reading it.

So: **do not treat a measurement as settled until a patch has been written
against it.** If the patch is not going to be written yet, the finding is
provisional and says so. Percentages and counts are a way of deciding WHERE to
read, never a substitute for reading.

**AND seatCommit's dependency chain is why the stakes are not just tidiness.**
`S.run.gold -= buy` must run after Double Stakes doubles the buy-in because it
READS a value that instruction produces. A hook firing all three cards at one
point would not have been merely imprecise - it would have silently broken a
real dependency. The failure mode was "wrong answer", not "wrong grouping".
Same as the two-stage turn clear, where the gap between phases is where each
path does its own work.

**THE SIM ROSTER IS NOT A NEUTRAL MEASURING STICK.** Measured 2026-08-03: the
live game's NPC personas are `{tags, dieBias, behavior}` records driving
parameterised `patronStats`, while `F.POLICIES.*` in the sim harness are
`mkPolicy({name, thresh, keep:function(){...}})` - each agent's personality is a
HAND-WRITTEN function.

So on the tunability axis the sim is the LESS structured of the two systems, and
a sim agent cannot currently express a persona the live game already can. When
sim numbers and live behaviour disagree about how an opponent plays, that gap is
a candidate cause before either side is called wrong.

**A ONE-SEED SIM RUN IS A ONE-SAMPLE MEASUREMENT.** Measured 2026-08-03 while
raising aggression: `spread` in the tier sweep is `max(win%) - min(win%)` over
four agents - a max-minus-min on four samples - and it carries **+/-3 to 6 of
seed-to-seed noise per tier**, with about **10 points** on the t0->t7 trend
statistic.

That is a fact about the INSTRUMENT, not the game, and it is retrospective: the
published headline "agent spread narrows 60.9 -> 23.6" is ONE SEED presented as
the finding. The underlying claim survives - a ~30 point fall clears a +/-10
band comfortably - but the numbers in it were never a range and were read as
one.

**So: run at least two seeds before believing any sim delta, and say how many
when quoting one.** Tonight's +0.06 aggression bump moved the trend by 6.2,
which is inside a band the same statistic wanders by 10.5 on its own. Nothing
about the change is knowable from a single before/after pair.

**The fix for that is more seeds, not a bigger change.** More seeds narrows the
band; a bigger bump commits to a magnitude that has to be walked back if the
mechanism turns out wrong.

**SCRUTINISE CLEAN RESULTS HARDER THAN DIRTY ONES.** Six instrument artifacts
in one day invented findings; the seventh HID one, and it was by far the most
expensive. `cfx_bespoke` reported all 20 cards fully migrated. `short_fuse` was
not — its x2 is hardcoded in `famCommitBonus` while it sits on `CFX`.

**The two failure directions need opposite habits and only one of them prompts
you.** A surprising finding gets checked because it is surprising. A clean
result is precisely where checking stops — there is nothing on the page asking
to be verified, and the work appears finished.

**Worse: that zero had been NARROWED to, from 18, through four corrections.**
Every one of those corrections was real, which made the process look rigorous
and made the final answer the most trusted number of the whole phase. Visible
refinement earns trust that the endpoint has not separately earned. Looking
corrected is not being correct.

**So: when a check comes back clean, go and find one instance by hand.** Not to
confirm the answer — to confirm the instrument can still SEE. This one was
caught only because building on the result ran into code that contradicted it,
which is luck, and late.

**A STANDING RULE IS WEAKEST EXACTLY WHERE IT MATTERS MOST.** Separately from
the above, and not a footnote to it: a `str.replace` inside a bash heredoc
silently no-op'd while the replacement next to it applied, and I read the
resulting numbers before checking the edit had landed. There is a standing rule
in this file about asserting on every replacement, written after this exact
failure. It got skipped.

The conditions are the point: late in a long session, mid-correction, moving
fast to reach a clean answer after a retraction. That is when a rule is most
needed and least likely to be honoured, because the pressure that makes it
necessary is the same pressure that makes it feel skippable. It was caught by
grepping for the inserted text — a five-second check that only happens if you
do it every time, including the times it seems unnecessary.

**A NAMING CONVENTION IS NOT A SHARED-STRUCTURE CLAIM.** The Ward withdrawal
was not a measurement error inside a correct question - it was the wrong
question. `_wardArmed`, `_wardBoost`, `_wardCharges` and `_wardBanks` share a
prefix; the audit grouped by prefix and concluded they shared a LIFETIME, then
recommended restructuring three unrelated features into one. Three of them have
no lifetime at all.

That is the identical surface-resemblance mistake this session kept finding in
the game's own code - `.gcard` "from main game", the four `_fxFreeDice` sets,
Trade grouped with the lane markers - caught this time in the audit that was
hunting for it. It is also the most expensive kind that has come up: the other
instrument errors made things look LESS coherent than they were, which invites
a second look. This one made three coherent things look like one broken thing
and proposed a fix, which invites a rewrite.

**Before grouping N things by a shared name, check they answer the same
question.** If the tool groups by prefix, the report must say "these share a
prefix" and nothing more until each is read.

**EVERY PROBE MUST JUSTIFY WHICH DOM SURFACE IS AUTHORITATIVE** before it
asserts anything — not that a plausible selector exists, but that the one it
reads is the one the live build actually paints. FIVE instances in one session
of a check verifying against the wrong surface, each of which reported success
having tested nothing real:

- `apv_bust_settle` scored a STRING verdict with `=== false` and passed.
- `apv_css_live` failed rules whose specificity was raised on purpose, by
  matching selector text exactly instead of by token.
- `apv_prop_overlap` reported zero overlaps having found two buttons and no
  dice, because the roll had not landed.
- The same probe then computed prop boxes from template data with the wrong
  origin (`left:x%` means x is the LEFT EDGE) and no rotation.
- `apv_preserve` asserted `G.kept` only — green while the table stayed empty —
  then measured `#keptTray`, which is the **2D fallback**: `refreshKeptTray`
  returns early on a `.fk3d` build and `#keptRow` is live.

**Queued item: audit every probe in the suite for this once, deliberately.**
For each, name the surface it asserts on and confirm it is the one the shipped
build renders. Cheaper as a single pass than rediscovered one accident at a
time.

**CHECK A SURFACE IS REACHABLE BEFORE AUDITING WHAT IT SAYS.** Three-for-three
this session, and in every case reading the code would have confirmed the wrong
thing: `#rulesOverlay` (six false claims, no visible entry point),
`#screen-bossreward` (nothing calls `showScreen('bossreward')`, and it decided
whether a Phase 2 red was live), `body::before` (a real stretch bug in a rule
that computes to `display:none`). Ask "can a player see this" first — it is the
cheaper question and it decides whether the accuracy work is worth doing.

**And when DELETING dead content, test the behaviour AROUND the deletion**, not
just that the target lines are gone. Cutting the rules overlay left a
`renderRulesScroll()` call in the BOOT resize handler — every window resize
would have thrown. A cleanup that introduces a crash is worse than what it
removed. *(Worth building: a probe that enumerates `showScreen` cases with no
caller, and overlays with no visible entry point. Three found by hand is enough
to justify automating the fourth.)*

**ASSERT EXACT, NEVER A FLOOR** — unless you can say why a floor is right. `>=`
is satisfied by less than it was meant to verify. `assert n >= 7` passed a run
where a replacement had silently failed and left two sites half-converted;
`assert n == 8` caught it. Same family as a probe passing having tested nothing.

**CONTROL FLOW BEFORE POSITION.** In one pass over `doBust`, position misled
three times at three granularities: nearest-preceding-`function NAME` is not
lexical scope (26 sites misattributed), a three-line adjacency window
undercounted clears that were deliberately two stages apart, and a search
anchored from position zero hit the wrong function twice. Walk the branches
first; check position against them, never the reverse.

**Patches with backslashes go through a Write-tool `.py` file, never a bash
heredoc.** Heredocs mangled a regex twice.

**Run the parse gate after every edit:** `node tools/zv_trade_parsegate.js`. It
now prints the file it read and its mtime — **look at that line.** Its default
used to be an untracked scratch build and it passed vacuously for a whole
session. A gate that cannot fail is worse than no gate, because it is credited.

**Run probes through `node tools/run_probes.js`, never `shoot.js` directly** —
the runner has the pre-flight. The dev server dies often; when it does, every
probe "fails" identically. Restart with `preview_start` name `gambit-worktree`
(port 8084).

**Never write `/*` or `*/` inside a CSS comment in `fark_proto.html`.** CSS
comments don't nest; a close-marker inside a sentence *about* markers ends the
block early and error-recovery eats the **next rule**. This cost four rounds on
the patron busts, then bit again in the comment explaining it.

**Verify computed, never authored** — and recursively. Written CSS is not live
CSS; check the CSSOM. A feature test must perform the operation and measure the
result, never read a property back. I broke this rule three times on the FEAT_ART
question alone before counting the folder.

---

## 5. STATE

- **Suite: 29 probes, FULLY GREEN** — 28 pass, 0 fail, 0 error (one probe,
  `apv_break_borrowed`, skips by design when the roll gives it nothing).
  Baseline re-recorded at `f431bb9`. Full run ≈ 12–18 min.
  Every run appends to `tools/probe_history.jsonl`, so an intermittent failure
  arrives with its own evidence instead of dying with the scrollback.
- **Phases done:** 1 (runner), 2 (totality), 3 (CSS live), 4 (feat roster),
  4b (badge remap), 5 (asset registry). Reports in `docs/PHASE_REPORTS.md`.
- **Deployed HEAD is `f431bb9` on `fark`.** This file used to carry TWO
  different HEADs — the header said one, this line said another — which is the
  contradiction-is-a-stop case sitting inside the handover itself. One value,
  here and at the top, and they are updated together or not at all.
- **Plans:** `docs/EFFECT_SYSTEM_PLAN.md`, `docs/VISUAL_INTEGRITY_PLAN.md`.
- **Sim numbers are stale** — every figure in `archive/SIM_RESULTS_2026-07-31.md`
  predates the sweep removal, the Trade harness fix and today's five rulings.
  Directions hold; magnitudes don't. Re-run before tuning.
- **Win screen** is built and matches the mockup. Two open notes: the deck
  spread reads faint against the wood, and "DOUBLE OR NOTHING" wraps to two
  lines while the others don't.
