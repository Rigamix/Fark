# Next session - start here

## Where things stand (2026-08-20, after the FULL card-actions audit)

Denis's playthrough plan is docs/PLAYTHROUGH_PASS_PLAN.md. Steps 1-2
are DONE: the four accusations driven and settled, then every family
card, tavern card and enchant audited by adversarial probe
(docs/CARD_AUDIT_2.md is the verdict table; tools/apv_audit_*.js
rerun against any build). Five real breaks found and FIXED + deployed:
- P811 stargazer (peek discarded on every real path -> lane-keyed)
- P812 double stakes room panel (economy was honest, display lied)
- P813 slow_cook (player roll seam fired a dead field -> accrual a
  roll late; seam now carries rollNum like the rival's)
- P814 retort's second trigger ("hit by an opponent card") was fully
  dead -> new famFire('cardHit') seam at the taking sites
- P815 tamper was cosmetic against passives -> the famFire bus now
  skips broken cards
Parked in docs/OPEN.md for Denis: sacrifice pays the BANK (spec says
turn total), double_or_nothing arms pre-bank (spec says post-bank
window), the cardHit taxonomy, and the preserve headless flake.
NEXT: plan Steps 3-7 (boss dialogue, BANK-TO-WIN + boss-win draft,
dice feel, patron leveling per docs/PATRON_LEVELING_BRIEF.md,
presentation pass incl. enchant descriptions + fog/sleight visuals).

## The state before that (2026-08-19, after the save/desc/glow fixes)

Read docs/NPC_AI_BRIEF.md sections 6-9 for the NPC arc. Short version:
- Decisions: EV floor + bank plan (P760). Pipe: famUse(i,actor), seven
  actives + nine symmetric passives, bespoke twins deleted (P761-766).
- Legacy roster clusters 1-4 done as tables (P767-771): NPC_RESCUES,
  NPC_BUST_SAVES, NPC_ARMS, _oppRescore, _playerKnock.
- Phase 2 done (P772-773): _npcDecide is the G-free core; the sim runs
  the REAL chooser; _runPersonaSim({turns:800}) is the calibration
  instrument. VERDICT: no persona weights needed at current numbers.
- Bank-seam rulings landed (P774); mirror_diff re-scoped to the P470
  extractions. The CHALLENGE telegraph asymmetry is REOPENED in
  docs/OPEN.md - the card's own eff and desc describe different
  mechanics and each seat implemented a different one. Denis rules.
- 2026-08-19 evening (P775-777, from Denis's phone session):
  - P775 the Grog resume bug: startNewRun left S.pendingMatch alive and
    the P693 gate hijacked every new-run launch. New runs discard the
    snapshot now (live + persisted, probe-verified both directions).
  - P776 card-text audit: FAM_SHORT (the tap-sheet at the table) held a
    cut design for fools_gold_f, vanguard's old rule on vanguard_f AND
    pickpocket, a curse ill_omen never casts, and tier-1 numbers at all
    tiers. Entries can be per-tier arrays now; _famWhyNot says the
    honest moment for auto-fire (fools_gold_f) and seat-played
    (for_keeps) cards. Authored d.text was already tier-correct.
  - P777 card glow: P756's noPunch had turned the authored tail-only
    halo into a 91%-alpha sticker, and the dice's sx/sy lean leaked
    into the card's soft pass. punchUnder (inward cut, tucks under the
    card) + opts-aware stretch. Dials untouched; measured before and
    after at 430x900 @dpr3.

## Waiting on Denis
- Night reports: Falling Star feel, patron table manners (retune input).
- Rulings: CHALLENGE telegraph (OPEN.md, reopened - dare vs trap),
  rescue-chain fall-through, seven_dice's dead 7th die,
  cluster 5 (two-seat re-audit of the rival roster).
- Backlog design calls: type:'once' decorative, block_low_bank undealt.
- Whether the new card-glow read on his phone matches what he wanted -
  if too faint, the dials are his in the lab (and see the DPR-quantized
  blur note in AUDIT_BACKLOG before chasing numbers).

## Next constructive arc (when taken up): the flow shells
handleBank vs finOpp as FLOWS. The mechanics layer is already converged
(BUST_FX/BANK_FX/BANK_TAKE + P470 extractions) - what remains twinned is
step order, guards and timers. Recorded inputs: the challenge telegraph
asymmetry, the mirror findings, and P774's latch placements.

## Standing traps (all bit recently)
- Patch scripts: Write-tool .py only, never bash heredocs. Anchors:
  regions mix per-line endings - match LF first, then the \r?\n regex
  fallback; re.escape escapes the newline char itself. Index cuts:
  compute lengths from the MATCHED variant.
- The ?sim=1 page has no live match: unguarded G.member reads throw and
  defensive try/catch turns that into silent fallback. Execution
  witnesses on anything the sim claims to test.
- Probes: wait ~3.5s after launch (startPTurn's init clear); rival
  effects fire in the roll RESOLUTION, seconds after the deal - watch
  for mutations, don't sample once.
- Probe ASSERTIONS vs rendered text: the tip renderer widow-joins the
  last two words with   - never assert a phrase across the final
  space of a rendered line.
- Port 8085 is Denis's server; probes use 8086 and sweep their python.
