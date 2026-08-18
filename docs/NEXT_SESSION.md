# Next session - start here

## Where things stand (2026-08-19, end of the phase-2 sessions)

Read docs/NPC_AI_BRIEF.md sections 6-9. Short version:
- Decisions: EV floor + bank plan (P760). Pipe: famUse(i,actor), seven
  actives + nine symmetric passives, bespoke twins deleted (P761-766).
- Legacy roster clusters 1-4 done as tables (P767-771): NPC_RESCUES,
  NPC_BUST_SAVES, NPC_ARMS, _oppRescore, _playerKnock.
- Phase 2 done (P772-773): _npcDecide is the G-free core; the sim runs
  the REAL chooser; _runPersonaSim({turns:800}) is the calibration
  instrument. VERDICT: no persona weights needed at current numbers -
  the baseline table is in the brief section 9.
- Standing assertion: the harness voids any run with picks:0 (the
  execution-witness rule - see the P773 instrument note; the sim once
  produced plausible persona tables with the chooser never running).

## Waiting on Denis
- Night reports: Falling Star feel, patron table manners (retune input).
- Rulings: rescue-chain fall-through, seven_dice's dead 7th die,
  cluster 5 (two-seat re-audit of the rival roster).
- Backlog design calls: type:'once' decorative, block_low_bank undealt.

## Next constructive arc (when taken up): the flow shells
handleBank vs finOpp as FLOWS. The mechanics layer is already converged
(BUST_FX/BANK_FX/BANK_TAKE + P470 extractions) - what remains twinned is
step order, guards and timers. FIRST re-scope tools/mirror_diff.py to
follow the P470 extractions (it currently reports every mechanic 'one
side only', which is false - its scan boundary predates the extraction);
THEN audit the shells, THEN design. Do not act on current mirror_diff
output.

## Standing traps (all bit recently)
- Patch scripts: Write-tool .py only, never bash heredocs. Anchors:
  newline = ?
 (regions mix per-line endings); re.escape escapes the
  newline char itself. Index cuts: compute lengths from the MATCHED
  variant.
- The ?sim=1 page has no live match: unguarded G.member reads throw and
  defensive try/catch turns that into silent fallback. Execution
  witnesses on anything the sim claims to test.
- Probes: wait ~3.5s after launch (startPTurn's init clear); rival
  effects fire in the roll RESOLUTION, seconds after the deal - watch
  for mutations, don't sample once.
- Port 8085 is Denis's server; probes use 8086 and sweep their python.
