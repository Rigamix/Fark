# NEXT SESSION — start here

Tree is clean. Worktree, root `fark` and `origin/fark` are all at **28ebaea**.
Everything below is deployed and verified live by grepping a marker on the
served file, never by a green build.

---

## THE PLAYTHROUGH NOTES ARE DONE — 6 fixed, 1 is yours

| # | note | outcome |
|---|---|---|
| 1 | roll button jitters sideways | **P634** — 131px, and it was never the pivot |
| 2 | win screen's bottom UI is slow | **P635** — a hard-coded 3.2s wait, now 2.4s |
| 3 | boss cards mirrored + degradation | **P633** — the row was rotated 180° |
| 4 | what IS First Strike? | **answered — needs your ruling**, `docs/OPEN.md` §11 |
| 5 | dialogue in two places | **P632** — one cause with 6 |
| 6 | dialogue never stops talking | **P632** — same cause |
| 7 | shelf cards ignore the perspective | **P636** — measured off your painting |

Three of the six were regressions from the session before this one. Each is
named as such in its own commit message.

---

## WHAT THE FIXES ACTUALLY WERE — the short version

**P632 (notes 5+6).** P628's hesitation beat called `setStatusMsg` — the "PATRON
IS ROLLING…" channel — which also skipped `DLG.trigger`, where every other beat
gets both its surface and its spacing. And the `agg` band that justified it does
not measure what it claimed: measured over a real match, `agg` was **0.53 on all
seven calls**, because it starts as `rung.agg` and for an ordinary patron nothing
moves it. So the band selected OPPONENTS, not decisions — one patron hesitated on
every single roll, another never (24 calls, 0 lines, in a separate run). Deleted
the helper, the band and the `G._oppAgg` stash; the beat is two ordinary
`_DLG_MOMENT` entries now. **No new pacing system was built. One existed.**

**P633 (note 3).** `#famRowO` carried `rotate(180deg)`, written when the row held
flat `.mcBack` rectangles — its own comment said reversing their order was
"meaningless for identical backs". P591 put painted faces in that row. The
degradation Denis wanted removed had *already stopped painting* for the same
reason: `.mcBack.broken` had nothing left to match. Same edit also restored the
rival's ARMED telegraph, which had been invisible since P591.

**P634 (note 1).** `@keyframes rollBounce` declared `translateX(-50%)` at both 0%
and 100% — the other half of a `left:50%` centring `#btnRoll` stopped using long
ago. 125.859px is exactly half its 251.7px width. **Intermittent** because
`#btnRoll.disabled{transform:none !important}` outranks an animation, so whether
you see it depends on whether something re-disables the button inside those
150ms. That is why two sessions of transform-origin work never touched it.

**P635 (note 2).** One hard-coded `setTimeout`. The reveal's last moving part is
`coinSheen .6s` starting at 1600ms, so everything stops at 2200ms; the patron win
held the lower half until 3200ms while the boss win beside it already used 2400.

**P636 (note 7).** Measured off `shelf_bg.png`: the middle slot's width runs
402.9 → 494.2 (ratio 1.2266) with its centre on the image centre — one ground
plane, vanishing point above the middle slot. `rotateX` from the slot's height
against the card's, `perspective` from the taper. Two measurements, neither
fitted to the other, both exact on the back-check.

---

## THE LESSON THIS SESSION KEEPS EARNING: a clean number is not a finding

Four times, and each cost real time:

1. A whole-match run reported the hesitation firing 24 times and saying nothing.
   True — for that opponent. A second run said 7 for 7. **The contradiction was
   the finding**, not either number.
2. The roll-button repro measured **0px of travel across 151 samples of a real
   bank** and was completely wrong. The positive control — call the same function
   directly — showed 131px. Without that arm the bug would have been closed as
   "not reproducible".
3. The win-screen probe reported the screen still animating six seconds in,
   because `getAnimations()` returns FINISHED animations that hold their end
   state via `forwards`, and the table's ambient loops never stop.
4. A grep for `.mcBack.broken` on the live file came back with one hit after the
   rule was deleted. It was my own comment quoting the rule.

**Every probe here now carries a `control` block, and any zero without one should
be treated as an instrument failure until proven otherwise.**

---

## HARD-WON FACTS — do not re-derive these

* **`agg` is a per-opponent constant, not a per-decision one.** It starts as
  `rung.agg` and only `chaotic`, `adaptive` and the desperate-play branch move it
  — none of which most patron matches reach. Do not build anything on "how close
  was that call" without measuring it first.
* **`DLG.trigger` is the only front door for a dialogue beat.** It carries the
  per-category probability, the `busyUntil + gap` spacing and the `_priority`
  interrupt list. `triggerCard` bypasses both gates by design (the teach moment);
  everything else must not.
* **`.mcBack` is gone.** The rival's cards are `.fcv` through `famCardArt`. Any
  rule still keyed to `.mcBack` matches nothing.
* **`.in-zone` is gone.** `usedCards[cardId]` is the only source of truth for a
  card being spent.
* **The card activation threshold** is `--card-arm-lift` (16cqw), resolved
  through a hidden strut (`#armLiftStrut`) so the CSS engine handles the unit.
  `parseFloat` on the var is WRONG — it drops the unit and fails open.
* **The dice throw has no rise.** `y[0]` IS the peak.
* **`PERSONAS` ≠ the dialogue traits.** Two six-way lowercase taxonomies. Dialogue
  traits are cunning/greedy/orderly/reckless/steady/**strong** — `strong` is what
  other docs call BULLISH.
* **`_dlgSay` tries `patron:<key>` FIRST**, and a patron's stage-0 lines are a
  floor that never empties, so a thread pool placed after it is unreachable for
  anyone with personal lines. This bit twice.
* **The last row of `PATRON_LINES` has no trailing comma.**
* **The FSIM harness calls `oppShouldBank` too** (~40145). Hooks belong on the
  in-match call only.
* **A transform makes a stacking context.** `.loCard.zoom{z-index:60}` means
  nothing outside `#loCardPlane`; that is why P636 lifts the plane, and it is the
  same bug P594 shipped on the leader's flag.
* **First Strike is a sealed-seat tell, not a card or a handicap**, and it only
  fires when the player casts Snare, Trade, Snuff or Fog. See `docs/OPEN.md` §11.

## INSTRUMENT TRAPS THAT COST REAL TIME

* `getAnimations()` returns FINISHED `forwards` animations and infinite ambient
  loops. Filter on `playState === 'running'` AND finite iterations AND scope to
  the subtree you mean.
* `G.phase === 'idle'` never becomes true. Gate on the element you need.
* Timers throttle to ~7fps headless — but that only matters for sampling a
  *curve*. A constant offset (like rollBounce's) lands in any single sample.
* The player's dice are tapped through a hidden `<i class="die-hit">` pad; a
  click on the `.die` itself selects nothing. Drive selection through
  `toggleDie(d)` on `G.pool` instead.
* `FAM_CARDS` is an ARRAY of definitions, not a keyed map.
* `window.G = {}` does NOT rebind a `let`-declared `G` — but a top-level
  `function foo(){}` IS a global-object property and CAN be overridden that way.
* Bash heredocs mangle `\uXXXX`. Patch through a Write-tool `.py` script whose
  anchors assert an exact match count.
* **Always dedupe new dialogue against the WHOLE existing table**, not just
  against itself.

## VERIFICATION STANDARD THIS PROJECT NOW EXPECTS

Every check needs a control that FAILS. Reachability before correctness: three
times in the previous session the code was correct and simply never reached.
`tools/apv_loadout_reaches_table.js` exists specifically because its absence let
`const pCards=[]` survive review.

---

## State as of 2026-08-13 (deployed: c734cef)

Shipped and marker-verified live: P666-668 (card FX vocabulary: cardFx
hit/gain/steal/churn, four cards wired, broken-card grey), P667 (one spark
band), P669 (status line wraps + Last Call/Reckoning refusals no longer
overwritten), P670 (ONE rival hand - G.oCards folded into #famRowO as .fcv,
buildCBar opp bar retired, _npcCardSpent one exhaustion truth, triggerCard
repointed), P671/b (card sheet parchment variant, scoped by 'fam-sheet'),
P672 (rival arch mirrors player, match-screen tap = grow+word-stagger text,
PLAY button gone - drag is the only activation).

Suite: 63 pass / 0 fail / 0 error. Triage of not-greens, all measured:
- 5 skips were transient (pass on individual re-run)
- ench_align + drill_cap setup flake is PRE-EXISTING (reproduced a skip on
  the pre-fold build via the root 8084 server) - their patron-intro wait is
  the weak part, not the game
- apv_selglow_size FAILS on the deployed site too -> pre-existing regression
  (glow strength grew back); chip spawned for it
- suite BASELINE IS STALE (7 probes "new, not in baseline") - run
  `node tools/run_probes.js --record` on a quiet build to reset it

Known deliberate gap: Whisper's hidden_cards still shows cards on the table
row (it never hid the old bar either) - P670 docstring records it.

---

## State as of 2026-08-13 late (deployed: ea50567)

The seventeen-notes batch, complete and live: P681 (five quick items), P682/683
(eleven investigated fixes - boss dialogue leak, music dead-air duck removed,
D3X warm boot, draft delay 500ms, bubble anim/padding, short-line rounding,
strip anchoring, score de-double, dice-over-rival-cards z, row perspective
19/-9deg), P684 (legacy FX sweep - four spawners reborn on FX.emit
diamonds/stars with material colours, Break's missing burst, enchant-fire
sprays via _iconFire, hot-dice fountain instead of the amber wash, six-kind
through the pooled engine), P685-687 (one lighting for all matches; the
dice-shadow lifecycle on one _dsDirty mark - keep/remove/shatter verified by
band-area deltas 14583->11754->9241; late table-image repaint).

OPEN with Denis: the enchant-page crash (OPEN.md #12 - five probes, two
builds, zero exceptions; need his save or console text). The pre-existing
selglow regression has its own spawned task chip.

Headless quirk worth knowing: under SwiftShader the PATRON leg's settle
shadows sometimes never paint (D3X match-dice adoption race; boss legs and
all screenshot runs paint fine, devices unaffected). If a shadow probe reads
zero, check `D3X.dice.filter(d=>d.match).length` before believing it - the
instrument note is in _diag_shadows.js.

Suite baseline still stale (run `node tools/run_probes.js --record` on a
quiet build). Dev server: worktree on 8085 (python http.server, restart if
dead); probes need FARK_URL=http://localhost:8085/fark_proto.html.

---

## 2026-08-13, third stretch (deployed: ba0cc35)

Book + trophy shelf REMOVED (P690 - book had zero callers; shelf contradicted
the brief's no-shelf ruling, TO THE SHELF button gone with it). The dice-lane
defect list is CLOSED: nine parallel re-derivations, three real fixes shipped
(P691 - D25 seventh-seat push -> P522-style swap; D10b dead-loans by stash
index; D6a the amber preserves the SEAT), the rest confirmed closed at their
recorded patches; the plan doc's status tables now match their own entries.

SAVE SYSTEM (P692, from a measured audit - report in the agent transcript,
probes tools/apv_save_cost*.js): saving costs 0.03ms on a 5.3KB payload =
free. Fixes: a second snapshot boundary at endPTurn (a bank can never be
lost), the resume banner is back on the room screen, and launching over a
pending match asks first (RESUME IT / PLAY THIS ONE INSTEAD). Full
per-action saving NOT done deliberately: it flips the resume-replay contract
that every rollback (P511/P536/P537/P539) depends on - see the audit before
attempting.

PROBE-BREAKING CHANGE: relaunching a match over a live S.pendingMatch now
opens the confirm modal. Probes must set window._fkDiscardOk=true before a
mid-state relaunch, or finish/exit the match first.

STILL WITH DENIS: phone shows no dice shadows while the live build measures
full ink in emulation (patron 108 / boss 118-130, lifecycle deltas correct)
- need a full phone screenshot or a clear-site-data reload to split stale
cache from device-specific. Enchant-crash save/console text still wanted
(OPEN.md #12). The launch-to-idle headless stall remains a probe-environment
flake (it also manufactured tonight's false "adoption race"): if a probe
reports no idle, retry the launch once before believing anything.

---

## 2026-08-13, fourth stretch

ONE-TAP RETURN (P693+P695, Denis's ask): a waiting match now takes you
straight back. Tapping any seat resumes it instead of asking - the P692
confirm modal lived exactly one stretch, _confirmDiscardPending is deleted -
and OPENING THE APP boots directly into the pending match, menu only as the
no-match/failed-resume fallback. Verified: seat-tap over a pending boss match
lands back in that same match; a scheduled location.reload landed on the
match screen with zero taps (the screenshot is the proof - a probe cannot
return a value across a reload).

PROBE CONTRACT CHANGE (supersedes the modal note in the stretch above):
relaunching over a live S.pendingMatch now RESUMES silently. A probe that
wants a genuine relaunch must set window._fkDiscardOk=true.

PHONE SHADOWS, the real split (P694): pre-Safari-18 has no ctx.filter, so
the fallback drew the hull fully OFF-canvas and let only its cast shadow
land in place - and WebKit's accelerated canvas culls offscreen primitives
WITH their shadows. Chromium paints the detached shadow (hence "full ink in
emulation"), the iPhone paints nothing. Exactly the reported split. Replaced
with three concentric hull fills (scale 1.0/1.14/1.30, alpha .55/.30/.15 of
base) - nothing offscreen, no cast shadows, rasterised identically
everywhere. Forced-fallback probe (window.__cfBlur=false):
ink 14090 / 95 paints / 0 errors - tools/apv_p694_fallback.js. DENIS MUST
CONFIRM ON THE PHONE: no local instrument runs real WebKit.

THE BREATHING LOOP COULD DIE AT LAUNCH (P696 - found by P694's control leg
reading zero): _candleLoop's tick exits whenever it runs before matchPlate
is ready, and the plate waits on the table image. On a slow first load BOTH
of _matchDress's restarts (+0ms, +900ms) hit that window and nothing ever
revived the loop - candle static, prop shadows frozen, dice shadows only on
discrete dirty marks (and the first roll's mid-fade marks all abort at the
not-yet-adopted D3X._tbl gate, so: no shadows until the first keep).
Measured: settled patron match, painter called 0 times in 2.8s. Two one-line
revivals through the loop's own _candleOn guard (D3X's dirty consumer + the
P687 image-load listener); the same control now reads 23 calls / ink 11887.

INSTRUMENT NOTE, refined: a STRAIGHT-TO-BOSS headless launch can reach idle,
roll 6 dice, and still never adopt 3D match dice (D3X._tbl false, the three
'loose' draft dice only) - three runs in a row did this. Patron-first is the
reliable probe path for anything that needs the shadow painter
(tools/apv_p694_fallback.js is the template).

STILL WITH DENIS: dice shadows on the actual iPhone, post-deploy. Enchant
crash save/console (OPEN.md #12). Suite baseline still stale
(node tools/run_probes.js --record on a quiet build).

---

## 2026-08-13, fifth stretch

SHADOWS CONFIRMED ON DEVICE (P694 worked). P699 raises the base band
0.45 -> 0.58, both blur and concentric paths.

WIN-SCREEN CARD FOCUS = THE SHELF TREATMENT (P697b/c/d). First shipped as
the match grow+stagger; Denis: that state is MATCH-ONLY - "other focus
states should all match the same style between dice, cards, etc." So the
match-focus extensions were reverted verbatim and the win screen got the
FIFTH near-copy of the shop/shelf focus by the P609 ruling (fly to centre +
scrim + #foFocusPanel joining the grouped panel selectors). Offer panel
carries CLAIM (the shop BUY plaque relabelled); deck row inspect-only;
drag-to-slot untouched, guarded against starting under an open focus.
Scrim lives INSIDE .res-card (giant-inset #loFocusScrim trick) because the
overlay chrome above z1 (win-board z3, skip z6) is instead hidden
instantly by .fo-focus rules.

P698: the offer block gets a floor as well as a ceiling - res-card top
49.5% + bottom above the SKIP pill, .fo-wrap flexes across the span,
.fo-deck margin-top:auto pins the slots to the bottom. The tall-phone dead
band is spent on every device; P643's 5vh counterweight retired.

INSTRUMENT TRAP, NEW AND NASTY: on a STATIC surface this headless browser
produces no frames on demand, so a CSS transition never resolves its start
time - computed value pinned at the FROM state, playState 'running',
currentTime 0 forever, and it OUTRANKS !important (transitions sit above
everything in the cascade). An injected opacity:1 !important could not move
the scrim. The shelf only measures clean because its dice canvas demands
frames continuously. Probe pattern: inject transition:none on the pieces
under test (apv_p697_698.js header), and treat screenshots - which force
BeginFrames - as the visual truth.

P700: a RESUMED PATRON KEEPS FACE AND VOICE. The seat identity is three
window globals (_lastSeatArt/_lastSeatTrait/_lastSeatColor); only
launchSeat wrote them, and P693's guard returns into resumeMatch before the
stamping lines - so every resume dressed a faceless, silent patron (the bug
Denis hit). One stamper (_stampSeatIdentity), three callers; resume
restamps from the snapshot's deep-cloned rung. Verified: wipe globals,
resumeMatch -> art matches launch, portrait url back, _dlgSay(art) works.

P701: THE BUBBLE STOPS MOVING. #dlgBox lived inside #diceArea; the bust
shake's transform made #diceArea its containing block (the documented
#tellBadge mechanism, never applied to the bubble) and overflow:hidden
clipped it mid-shake. Now a direct child of #screen-match,
position:absolute, z 9500 (over focus 9000/9001, under #end-ov by DOM
order). The second mover: height:0 box + centred content = top edge moved
with the bubble's own line count; a fixed 24cqw .dlg-inner centres 1-line
and 3-line bubbles identically, --dlg-y 25 -> 13cqw keeps the old centre.
Measured: centre drift 0.0 short vs long vs mid-shake.

P702: SCORING FACE BRIGHT, SIDES IN SHADOW (Denis's ask). Not lights - one
scene serves shelf and table, ambient floors the dark, and the 42deg tilt
misaligns any down-light. _dimMap bakes the composed atlas with every cell
multiplied by SIDEDIM ('#5a3d24', the one tunable) except the scoring
value's; hard-swapped while d.phys holds (tray swap-don't-fade rule),
restored in the air and at table changes BEFORE _trayTint can cache a
dimmed base. Value rides d.roll.val -> d.phys.v. Cache keys on the
composed map object + value, so {mat, ench} travel together. Verified: 6/6
settled dice dimmed, phys.v === chip._trueVal; A/B with near-black SIDEDIM
shows every top lit, every side black, enchanted die included.
KNOWN SCOPES: a resumed never-rolled die rests bright (no phys.v - mixed
look after resume, accepted for now); an enchant brand on a side face keeps
its emissive glow through the dim (reads as glowing in shadow, deliberate).
If Denis wants the dim stronger: D3X.SIDEDIM, one line.

P703 (Denis: "50% too strong... appears in one frame... jarring"): the dim
halves (SIDEDIM_MAX 0.5) and ARRIVES on a smoothstepped ramp of QUANTIZED
BAKES - 8 steps over 700ms after a 150ms hold, ~4% a swap, each cached per
composed map + value + step (Lambert still cannot crossfade two maps).
Tunables in one block: SIDEDIM / SIDEDIM_MAX / SIDEDIM_RAMP.

P703b, found by the probe's 'no settle' being really 'settled without v':
settling has TWO writers - _physPose's done branch and the overdue-tape
watchdog that snaps a die to its last frame. P702 taught only the first to
carry {v,t}; a watchdog-settled die (any hitch, and most headless runs)
silently never dimmed. Both exits carry the same payload now. One exit
path, one payload - the standing lesson caught it again.

INSTRUMENT NOTE: headless frame starvation is now measured, not suspected -
runs with fc deltas of 4-30 frames per 12s stall the time-indexed playback
(pc:0) or route it through the watchdog. apv_p703_ramp.js carries
frame/physPose counters and a >=3-distinct-maps criterion (a one-frame pop
reads exactly 2; devices at 60fps render all 8 steps). The full ramp was
observed green in a frame-healthy run; the watchdog path verified by v
riding through a starved one.

STILL WITH DENIS: enchant crash save/console (OPEN.md #12); suite baseline
re-record; ramp feel + halved SIDEDIM on device; the resumed-dice bright
rest.

---

## 2026-08-14, the playthrough-notes + load-pass batch (P704-P713)

Denis's eleven notes, plus his HAR trace. Everything below is applied,
gated, and verified by ONE consolidated probe (tools/apv_p704_713.js -
every assert green) + the post-reload title screenshot. CPU DISCIPLINE IS
NOW A CONSTRAINT: no parallel agent fleets, one probe run per batch, sweep
orphaned headless browsers after every run (the harness leaked 30 - Denis's
machine crawled; a spawned task hardens shoot.js cleanup separately).

P704 win-focus panel: the flown card's caption yields while zoomed (the
doubled ENCORE), fname band -46cqh, K 1.9 @ 0.34.
P705 Denis REVERSED P695: boot lands on the TITLE; CONTINUE resumes a
pending match (_hsContinueTap). Verified by planted-snapshot reload.
P706 bubble: fit slack on the RETURNED width (scrollWidth rounds short -
'Fine, fine.' measured 1 line now), padding 4.7/5.3 bottom-heavy for the
iOS hhea metric sink, Raritas Regular registered + weight 400, metric
overrides pinned, strokeW 1.5.
P707 _rowMid refuses partial populations (the rival-reroll sideways
glitch - kept-dice span used to centre the whole settled group).
P708 Ill Omen: right call pays the FULL tier reward over any board (the
capped transfer was Denis's 'no points'), unread omen refunds its charge
at endMatch, activation line + card text name THEIR NEXT TURN, Stargazer
renamed out of the OMEN namespace. Verified: 800 paid over an empty board.
P709/P710 a survived boss loss = LAST ORDERS beat + _heartLossReset (one
reset for all four heart sites: points 0 relocks the derived boss gate,
chalk wiped, night re-rolled immediately). Verified: coins-1, points 0,
flag set, fresh roster.
P711 a resumed boss match replays the boss splash (the 'grog picture' -
and the boss MUSIC starts inside it, so resumes also kept tavern music).
P712 THE LOAD PASS: dead parse-time fetches removed (main_04 962K,
settings.png 767K, Loadout FAB icon, hidden Innkeeper portrait, menu
gauntlet icon); title masters -> existing optimized copies (bg 758K,
logo 875K, buttons, book, cog - also Last Orders + gameover buttons);
matchPlate joins the ?v=1 URL (the table loaded TWICE as two cache
entries); levelUp_opt.webp (461K->18K) + iOS_icon_180.png (373K->54K)
generated and swapped. HAR false alarms, checked: win/ and loss/ share
banner/hands/panel FILENAMES (different files, no dup); bg.png-vs-bg.webp
was Homescreen-vs-win (different assets); table_commoner.webp is the live
body backdrop. The 25s/44s HAR gaps are BY-DESIGN lazy loads (3D engine on
first need, audio on first tap) - menu-browsing time, not stalls.
P713 armed glow doubles up (hot core + wide halo + brightness - the old
single soft shadow read as nothing under a card in hand); spent cards stop
bobbing and take no tap-scale. NOT probe-verified (night-1 run holds no
family cards - the probe's card block skipped); cascade reviewed instead.

STILL OPEN at the time: bust scatter + shield and the Fair Trade ruling -
both landed below.

---

## 2026-08-14, second stretch (P714-P717)

P714 THE LEGACY-ART PURGE (Denis: nothing in assets/ should ever load).
Measured first: the live room is ENTIRELY the new pt-stage painting - every
old-layer piece invisible beneath it, still fetching at parse or on room
entry. All removed: 4 room statics + 4 nav icons, five dead CSS urls, the
8 per-boss ::before match skins, both legacy portrait maps (bosses resolve
through their OLD keys - GROG is 'drunkard' - to previous-game busts; maps
emptied, readers guard), the hidden roster renderer + innkeep builder. JMH
Beda moved out of assets/_mockups. Kept and named: cards/, win/, loss/,
Audio/, vendor/, models/, Macondo, table_commoner.webp (current art, old
folder). Room verified pixel-identical.

P715 per Denis: boss SPLASH removed (its boss-music cue moved to both
launch and resume paths - it lived inside the splash); the POUCH removed
entirely (not part of the new system, even with renown) - the last legacy
image load went with it; the shop-door note withdrawn.

P716 BUST SCATTER + SHIELD (the last playthrough note). Scatter =
D3X.scatterRow: a planar kick per settled die - outward slide + tabletop
spin over the frozen phys pose (the burst idiom), dice END displaced, the
wipe collects them; kick clears wherever the pose clears. The CSS .scatter
class stays as the 3D dim + no-physics fallback. Shield = _bustShieldFX:
row-rect bloom ring (the orphaned Silver shieldFire look re-homed, no
emoji) + FX diamond ring + SFX.shield, coloured per saver (amber / ward
ink / card gold). Wired at: the _runSave funnel, Amber, Ward, Fool's Gold
claim, Second Wind + Mabel's Stitch (shield at trigger), Thick Skin + Last
Stitch (full bust THEN shield at the +1s save beat, per the B1 ruling).
Verified: 6/6 dice kicked and displaced >0.3 die-widths, displacement
holds, ring mounts/leaves; screenshot shows the thrown-apart table.

P717 Fair Trade wears the stopgap wording from OPEN.md #13's rec (no
stash, no false one-roll promise, no implied choice). The deeper ruling -
reword-only vs retire vs surface-the-reserve - is still Denis's.

INSTRUMENT NOTE: CSS ANIMATIONS freeze like transitions do in starved
headless (the shield ring measured opacity 0 mid-animation; the end-of-run
screenshot rendered it fine). Probes should assert mount/geometry/removal
and leave animated opacity to screenshots.

PROCESS NOTE, again and enforced: the bash-heredoc backslash trap struck a
THIRD time writing a patch tail - \\n collapsed to a real newline inside a
python source string. Patch scripts are written by the Write/Edit tools
ONLY, never assembled through a heredoc.

STILL WITH DENIS at the time: most landed below.

---

## 2026-08-14, third stretch (P718-P720b)

P718 FAIR TRADE RETIRED (Denis's ruling a) - For Keeps seats its prize on
the spot: the taken die asks WHICH SEAT it takes on the win-card surface,
the outgoing die retires WITH its brand, or leave it on their table. The
invisible reserve is dead; relic spoils still feed it - OPEN.md #13 asks
seats-or-trophies (rec: trophies).
P719 the LUCKY-DIE TAKE retired (census first: the die itself is every
patron's first die and STAYS; what went is the collecting - off the For
Keeps table, luckyNames + three_lucky with it).
P720 five notes: (1) the grudge SPEAKS - _DLG_MOMENT 'grudge', two lines
per trait, fired 2s into a rematch vs a grudge patron; the seat-screen
caption is gone. Grudge now plants on SEATING any For Keeps die. (2) the
first-night draft: dice gap 10%, labels drop lower and FADE IN at final
position after their die lands. (3) the side-face dim lands WITH the die -
the tape's end is a known moment and the value rides it, ramp 350ms.
(4) the jelly edge: per-die cocked dice earn their tip after ten still
frames of their own (the old gate waited for the whole pile - the tape
recorded the wait), and a tipping die is exempt from the heavy settle
damping. (5) resumeMatch warms D3X.boot + cannon so the resumed turn's
first roll stops paying script-load + first-solve mid-tap.
P720b the P718 migration's missing half: roster patrons and pending
snapshots dealt fair_trade before P718 are scrubbed at load.

INSTRUMENT LESSONS, two: the 'Cannot read text of null' page-crash chased
across three runs WAS THE PROBE - apv_p716_scatter still asserted the
P717-era famDef('fair_trade').text after P718 retired the card (assert
against the code as it IS, not as the probe remembers). And the draft
label-fade probe measured after the animation delay had passed - subEarly
must be sampled <1.5s from the draft appearing.

STILL WITH DENIS: enchant crash (OPEN.md #12); relic spoils destination
(#13); boss-peek/end-screen busts or name-only (#15); git-rm of the dead
legacy files; suite baseline re-record; ON DEVICE: the resume unlock feel
(the warm shipped - if it still sticks, the next suspect is the first
synchronous solve itself), the dim-lands-with-the-die look, the edge-tip
speed, grudge barks at a rematch.
