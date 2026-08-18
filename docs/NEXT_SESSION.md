# Next session - start here

## Where things stand (2026-08-18, end of the parity sessions)

The NPC play rework and the one-pipe card parity program are live
through P766. Read docs/NPC_AI_BRIEF.md sections 6-8 for the full state;
the short version:

- Decisions: EV floor + bank plan + release block deleted (P760). The
  three reported idiocies are impossible by construction.
- The pipe: famUse(i, actor), NPC_FAM_READY registry. Seven actives
  (preserve, double_or_nothing, honeytrap, encore, sleight, stargazer,
  ill_omen) + nine symmetric passives through it, every bespoke twin
  deleted. Enchant thread live on the rival path.
- Two parity bugs fixed on the way: the rival bankBonus seam consumed no
  delta; the rival bust seam carried no `lost`.
- Falling Star's rival half is LIVE and retune-flagged - Denis is
  playing nights to feel it before numbers move.

## THE NEXT BATCH, ready to start: legacy roster cluster 1

docs/NPC_AI_BRIEF.md section 8 has the measured map (42 cards, 21
levers, 19 mechanics). Cluster 1 = the bust rescues (old_bones,
ambrose_grace, wild_die, brutus_fist, finnicks_palm, grogs_flask,
second_wind + bust_survive/bust_immune_turns/bust_bank_half +
mabels_stitch): one moment, one dispatch table, npcCardState UNTOUCHED
(it is saved - resume risk).

Before writing anything: read the full bust path (~34700-34900) cold.
Verification plan: stub rollFace in a probe to force a dead first roll,
assert exactly one rescue fires and the bespoke double-fire is gone;
then a resume check (save mid-match with uses spent, reload, verify
npcCardState survived).

## Standing traps (all bit this session)
- Patch scripts: Write-tool .py only, NEVER bash heredocs (backslash
  trap ate shader strings again). Index cuts: compute lengths from the
  MATCHED variant (CRLF cut left a stray brace - parse gate caught it).
- The ?sim=1 harness does NOT run the persona chooser (simTurn keeps
  maximal always) - drive the live functions.
- Probes: out-of-band runOppTurn during the match-init window loses
  state to startPTurn's row clear - wait ~3.5s after launch.
- Port 8085 is Denis's server; probes use 8086 and sweep their python
  after.
