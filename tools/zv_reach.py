# -*- coding: utf-8 -*-
u"""zv_reach - the pruning question asked as a probability, from turn outcomes.

WHY NOT A CEILING. The envelope was specified as "measure the ceiling, strike
cells whose ceiling is below target". A ceiling is a max of n, and a max of n
only rises with n, so cells are comparable only at identical n and the number
carries no confidence. Concretely: one match was wrongly excluded from a pool of
eleven - discarded at the RUN level because a sibling match in the same
invocation was invalid, when the validity test is per-match - and putting it back
moved the cell's "ceiling" from 7100 to 7500. A 5.6% move in the headline number
from a sampling decision, with nothing about the cell having changed.

WHAT REPLACES IT. "Can this cell reach target T" is a probability, and it is
answerable from the per-turn outcomes the driver records. A match total is a sum
of TURN_CAP turn outcomes, so resampling turns gives the distribution of match
totals with its real shape - a bust is a hard zero, a hot streak has no ceiling,
so it is right-skewed and a normal fit understates the upper tail. For pruning
that is the dangerous direction: it strikes cells that were reachable.

THE BIGGER TAIL PROBLEM IS THE SD, NOT THE SHAPE. An SD from n match totals has
standard error sd/sqrt(2(n-1)) - about 24% at n=10. One SE either way moved
P(reach 9500) between roughly 0.01% and 1.1%: two orders of magnitude from
sampling noise alone, dwarfing the skew correction. This is the strongest reason
to work from turns rather than match totals: ~85 turns estimate a variance far
better than 10 matches do. The SD's own uncertainty is propagated below rather
than mentioned.

THE EXCHANGEABILITY CONTROL IS TWO-SIDED, AND THE TWO FAILURES HAVE OPPOSITE
SIGNS. Resampling assumes turns are interchangeable draws. Two things break that:

  HETEROGENEITY - turns differ systematically by position (per-match consumables
  are spent early, one-shot effects do not come back). Pooling non-homogeneous
  turns makes the RESAMPLED spread too large.

  COUPLING - turn N's outcome depends on turn N-1's. That makes the OBSERVED
  spread too large.

A single "do matches vary more than independent turns predict" catches only the
second, and because the signs oppose, BOTH can be present and cancel into a clean
pass. So the STRATIFIED resample - turn i drawn from turn i's own bag - is the
baseline, and each failure is measured against it separately:

  pooled_sd / stratified_sd  > 1  =>  HETEROGENEITY by position
  observed_sd / stratified_sd > 1  =>  COUPLING across positions

Two ratios against one baseline cannot cancel each other, because neither is
computed from the other. The reported reach probability comes from the
STRATIFIED resample, which already respects position; coupling is what triggers a
refusal.

Usage:  python tools/zv_reach.py <log-file> [target] [cap]
"""
import io, json, math, random, sys

random.seed(20260903)   # fixed, so a rerun on the same data gives the same answer
TRIALS = 200000
SD_TRIALS = 20000       # for propagating the SD's own sampling error


def load(path):
    txt = io.open(path, encoding='utf-8', errors='replace').read()
    for line in txt.splitlines():
        if line.startswith('setup:'):
            return json.loads(line[7:])
    sys.exit('no result line in %s' % path)


def sd(a):
    n = len(a)
    if n < 2:
        return 0.0
    m = sum(a) / float(n)
    return math.sqrt(sum((x - m) ** 2 for x in a) / (n - 1))


def mean(a):
    return sum(a) / float(len(a)) if a else 0.0


def pct(sorted_a, q):
    return sorted_a[min(len(sorted_a) - 1, int(len(sorted_a) * q))]


def resample_pooled(bag, cap, trials):
    return [sum(random.choice(bag) for _ in range(cap)) for _ in range(trials)]


def resample_stratified(bags, cap, trials):
    """turn i drawn from turn i's own bag; positions beyond the observed set
    fall back to the last bag that exists."""
    out = []
    for _ in range(trials):
        t = 0
        for i in range(cap):
            b = bags.get(i) or bags.get(max(bags))
            t += random.choice(b)
        out.append(t)
    return out


def report_cell(key, c, target, cap):
    print('\n=== %s ===' % key)
    if c.get('refusal'):
        print('  REFUSED: %s' % c['refusal'])
        return
    seqs = [r.get('turnSeq') for r in (c.get('rows') or [])
            if r and not r.get('err') and r.get('turnSeqComplete')]
    seqs = [s for s in seqs if s]
    totals = c.get('totals') or []
    if len(seqs) < 3:
        print('  REFUSED: only %d matches carry a complete ordered turn record; '
              'without position the stratified baseline cannot be built, and '
              'without it heterogeneity and coupling cannot be told apart'
              % len(seqs))
        return

    # THE IDENTITY THAT VALIDATES THE PER-TURN RECORD. A match total is the sum
    # of its turn values, and the two are collected by different routes - pPts
    # is the game's running score, turnSeq is a wrap reading turnPts once per
    # endPTurn. They share nothing but the game, so a mismatch says the turn
    # record is missing or inventing a turn, which no amount of resampling
    # would reveal. This is the check that would have caught the harness
    # reconstructing turn values from bank taps: amber's bank-out path banks
    # without a tap, so the reconstruction lost those points and the sum fell
    # short of pPts.
    rows_ok = [r for r in (c.get('rows') or [])
               if r and not r.get('err') and r.get('turnSeqComplete') and r.get('turnSeq')]
    mismatch = [(sum(r['turnSeq']), r.get('pPts')) for r in rows_ok
                if sum(r['turnSeq']) != r.get('pPts')]
    if mismatch:
        print('  TURN RECORD DISAGREES WITH THE MATCH TOTAL in %d of %d matches: '
              '%s (sum(turnSeq), pPts)'
              % (len(mismatch), len(rows_ok), mismatch[:6]))
        print('  REFUSED: the per-turn record does not add up to the score the '
              'game kept, so it is missing or inventing turns. Resampling it '
              'would produce a confident answer about the wrong distribution.')
        return
    print('  turn record checks out: sum(turnSeq) == pPts in all %d matches'
          % len(rows_ok))

    flat = [x for s in seqs for x in s]
    bags = {}
    for s in seqs:
        for i, x in enumerate(s):
            bags.setdefault(i, []).append(x)
    thin = [i for i in sorted(bags) if len(bags[i]) < 3]

    zeros = sum(1 for t in flat if t == 0)
    print('  %d matches, %d turns (%d busts, %d%%)  mean/turn %.0f  sd/turn %.0f'
          % (len(seqs), len(flat), zeros, round(100.0 * zeros / len(flat)),
             mean(flat), sd(flat)))
    print('  observed match totals: mean %.0f  sd %.0f  n=%d'
          % (mean(totals), sd(totals), len(totals)))
    print('  per-position means: %s'
          % ', '.join('t%d=%.0f(n%d)' % (i + 1, mean(bags[i]), len(bags[i]))
                      for i in sorted(bags)))
    if thin:
        print('  NOTE: positions %s have fewer than 3 observations; their bags '
              'are thin and the stratified draw there is nearly deterministic'
              % ', '.join('t%d' % (i + 1) for i in thin))

    pooled = resample_pooled(flat, cap, TRIALS)
    strat = resample_stratified(bags, cap, TRIALS)
    sd_pooled, sd_strat, sd_obs = sd(pooled), sd(strat), sd(totals)

    print('  resampled %d-turn totals:  pooled mean %.0f sd %.0f  |  '
          'stratified mean %.0f sd %.0f'
          % (cap, mean(pooled), sd_pooled, mean(strat), sd_strat))

    if not sd_strat:
        print('  REFUSED: the stratified resample has zero spread')
        return

    het = sd_pooled / sd_strat
    cpl = sd_obs / sd_strat
    print('  CONTROL (two-sided, one baseline):')
    print('    heterogeneity  pooled/stratified = %.2f  %s'
          % (het, 'positions differ - pooling would be wrong' if het > 1.15
             else 'positions look alike'))
    print('    coupling       observed/stratified = %.2f  %s'
          % (cpl, 'matches vary more than independent turns explain' if cpl > 1.35
             else ('matches vary LESS than independent turns explain' if cpl < 0.65
                   else 'within tolerance')))

    # THE OBSERVED SD IS ITSELF NOISY - do not refuse on a ratio the sample
    # cannot resolve. SE(sd) = sd/sqrt(2(n-1)).
    n_m = len(totals)
    se_sd = sd_obs / math.sqrt(2 * (n_m - 1)) if n_m > 1 else float('inf')
    cpl_lo = (sd_obs - 1.96 * se_sd) / sd_strat
    cpl_hi = (sd_obs + 1.96 * se_sd) / sd_strat
    print('    the coupling ratio itself is uncertain: 95%% CI %.2f-%.2f '
          '(observed sd %.0f +/- %.0f at n=%d)'
          % (cpl_lo, cpl_hi, sd_obs, 1.96 * se_sd, n_m))

    if cpl_lo > 1.35:
        print('  REFUSED: coupling is present even at the low end of its interval, '
              'so the tail below would be too thin. Reach is NOT reported.')
        return
    if cpl > 1.35:
        print('  WARNING: point estimate says coupling, but the interval includes '
              'the tolerance band - the sample cannot settle it. Reach below is '
              'provisional and likely UNDERSTATES the tail.')

    strat.sort()
    hits = sum(1 for s in strat if s >= target)
    p = hits / float(TRIALS)

    # PROPAGATE THE SD'S OWN ERROR. Bootstrap the matches themselves and redo
    # the stratified draw, so the reported interval carries the sampling noise
    # that moved the earlier normal-fit answer by two orders of magnitude.
    ps = []
    for _ in range(120):
        boot = [random.choice(seqs) for _ in range(len(seqs))]
        bb = {}
        for s in boot:
            for i, x in enumerate(s):
                bb.setdefault(i, []).append(x)
        sims = resample_stratified(bb, cap, 3000)
        ps.append(sum(1 for s in sims if s >= target) / 3000.0)
    ps.sort()
    lo, hi = ps[int(len(ps) * .025)], ps[int(len(ps) * .975)]

    z = (target - mean(strat)) / sd_strat
    pnorm = 0.5 * math.erfc(z / math.sqrt(2))
    print('  P(reach %d in %d turns) = %.3f%%   95%% CI %.3f%% - %.3f%%'
          % (target, cap, 100 * p, 100 * lo, 100 * hi))
    print('  a normal fit would have said %.3f%% - the resample is %s'
          % (100 * pnorm, 'FATTER, as the skew predicts' if p > pnorm else 'thinner'))
    print('  stratified percentiles: p50 %d  p90 %d  p99 %d  max %d'
          % (pct(strat, .5), pct(strat, .9), pct(strat, .99), strat[-1]))

    if hi < 0.001:
        v = 'STRIKE - unreachable even at the top of its interval'
    elif lo > 0.02:
        v = 'KEEP - reachable even at the bottom of its interval'
    else:
        v = ('MARGINAL - the interval spans the decision boundary, so this cell '
             'cannot be pruned on this much data')
    print('  VERDICT: %s' % v)


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    d = load(sys.argv[1])
    target = int(sys.argv[2]) if len(sys.argv) > 2 else 9500
    cap = int(sys.argv[3]) if len(sys.argv) > 3 else (d.get('caps', {}).get('patron') or 8)
    print('target %d, cap %d turns' % (target, cap))
    for key in sorted(d.get('cells', {})):
        report_cell(key, d['cells'][key], target, cap)


if __name__ == '__main__':
    main()
