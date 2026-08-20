# The bank oracle — plan (own session, not urgent)

Denis's ruling (2026-08-20): plan it as its own session. The failure
direction today is safe — the BANK caption under-promises and never
over-promises — so this is polish, gated behind everything live.

## What it closes

P819 left three classes of caption dishonesty, all "label says less
than the press pays":

1. **The player card bonus stack** (~30 sites in handleBank between
   the kept-sum and the tell hooks): ×2 cards (fortunes_wheel,
   greedy_hands, last_orders), ×1.5 prompt_hand, half_measure through
   ambrose_chalice, underdog/turncoat, the starstone row bonus,
   ambrose_weight's +500, corvus ledger.
2. **Commit-time multipliers in the preview**: short_fuse's ev.mul(2)
   applies at the BANK's commit (33518-region) but refreshSelUI's
   preview reads scoreSelection only — from roll 3 with a lit fuse the
   caption under-reads by half. Same gap for vanguard/sequence/palm
   commit adders on the selection preview.
3. **Rival deductions**: cowards_bell −10%, halve_big_bank, steal-low
   — a projected win can evaporate at the press (the near-target case
   P819 could not close without modeling the rival's cards).

Explicitly OUT of scope: double_or_nothing's flip (the caption must
not predict a coin), and rival cards whose fire is probabilistic at
press time.

## The shape

Extract handleBank's total pipeline — kept-sum → card bonuses → tells
→ post-refusal additions (bankBonus seam, weight, hangover) — into

    _computeBankTotal({dry:true|false, sel})

- **wet** (dry:false): exactly today's behavior — counters increment,
  flags consume, famLog/triggerCard fire, famFire seams run.
- **dry**: pure arithmetic — no counter writes, no flag consumption,
  no announcements, famFire('bankBonus') replaced by a dry sum of the
  deterministic handlers (slow_cook acc; skip flip-dependent).
  Returns {total, refused, escrowed, wouldWin}.

handleBank calls it wet; _projectedBank calls it dry. One oracle,
every surface (verb, caption, win test, both bank-to-win classes)
already reads _projectedBank, so no second label writer appears.

## The risk, and the guards

This is surgery on the game's most central function; the known trap is
wet/dry drift (a new bonus added to one path only) and double-count
(the P819-era comment records the selection being counted twice).

Guards, in order:
1. **Characterization first**: before touching anything, a probe bank
   matrix — N constructed turns (plain, ×2 card, short_fuse lit,
   slow_cook pot, cowards_bell, last_call seat, tab armed, weight,
   hangover) — recording handleBank's actual paid totals on the
   pre-refactor build. The refactor must reproduce every row wet, and
   dry must equal wet minus the excluded stochastic classes.
2. **The dry flag lives in ONE branch per side effect**, never
   sprinkled: each side-effectful line moves behind `if(!dry)`.
3. **Every new card bonus lands inside the oracle** — enforced by
   deleting the old inline block entirely so there is no second place
   to add one (the one-output-location lesson).
4. Preview coverage for commit-time multipliers = a dry call with the
   live selection passed in (sel), reusing _applyCommitBonuses'
   commit-event with a no-consume flag.
5. Rerun: apv_bank_label_lastcall, apv_bank_label_bonus_heal, the
   audit probes that bank (slow_cook, preserve, DoN, fuse), and the
   characterization matrix, all green before ship.

## Estimate

Half a session: ~2h extraction + guards, ~1h characterization matrix
and re-verification. Do not batch it with anything else that moves
scoring.
