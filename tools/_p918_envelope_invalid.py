# -*- coding: utf-8 -*-
u"""P918: the band envelope run was invalid, and one of my own guards passed it.

THE PREMISE WAS WRONG. The probe measures at tier 7 "where the target cannot be
reached, so every match spends its whole turn allowance". The PLAYER'S target
cannot be reached. THE RIVAL'S CAN - the rival reaches 8700-10300 and ends the
match long before the player's eighth turn. What was measured is "how much the
player scored before the rival won", which is not a ceiling and not comparable
between matches of different lengths.

The data says so: pTurns came back 5, 7, 8 and 9 across twelve matches, and
endReasons is mostly null - the cap branch never fired.

MY OWN ASSERTION SAID SO AND I PRINTED THE TABLE ANYWAY. mostRanToTheCap was
FALSE in both runs. It exists precisely to say "these are not ceilings". So it
stops being a reported field and becomes a hard stop: the table is not built
when it fails.

AND THE GUARD I WAS PROUDEST OF NEVER RAN. `dealt` reads the loadout back off
G.pool so a band label cannot lie - and it returned EMPTY every time, because it
is read at the idle phase, before any dice are on the table. Worse,
bandsAreDistinct PASSED: I wrote it to short-circuit to true when fewer than two
bands ran in one invocation, then split the run one band per invocation, which
made it vacuous in exactly the configuration I shipped. A guard that cannot fail
in the way it is actually run is not a guard.

THREE FIXES, so the same run cannot be reported again:

  the loadout is read from S.run.dice AND from the pool after the first roll,
  and asserted against BANDS[band] itself - checkable with one band, so it
  cannot be short-circuited away;

  a cell whose matches did not reach the cap returns a REFUSAL instead of a
  ceiling, and the table skips it rather than averaging it;

  and the per-turn yield is reported beside the total, because normalising by
  pTurns is the only thing the existing data could have supported and the next
  design has to choose deliberately between that and stopping the rival.

No pruning table is drawn from the invalid run. Its 17/22/23 unreachable counts
are computed from ceilings that are not ceilings.
"""
import io, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'tools', 'apv_envelope_bands.js')
s = io.open(P, encoding='utf-8', newline='').read()
edits = []


def sub(old, new, label):
    global s
    if s.count(old) != 1:
        sys.exit('ANCHOR x%d for %s (nothing written)' % (s.count(old), label))
    s = s.replace(old, new)
    edits.append(label)


# ── 1. the loadout is read where the dice exist, and checked against intent ──
sub(u"""    /* confirm the loadout actually took, or the band label is a lie */
    let dealt = null;
    try { dealt = (G.pool || []).map(d => d.mat).sort().join(','); } catch (e) {}""",
    u"""    /* CONFIRM THE LOADOUT AGAINST WHAT WAS ASKED FOR, not against the other
       bands. The first version read G.pool at the idle phase - before any dice
       are on the table - so it came back EMPTY every match, and the check that
       compared bands to each other short-circuited to true because only one
       band ran per invocation. A guard that cannot fail in the way it is
       actually run is not a guard.
       S.run.dice is readable now; the pool is read after the first roll below
       and both are reported. */
    const want = BANDS[band].slice().sort().join(',');
    let asked = null;
    try { asked = (S.run.dice || []).slice().sort().join(','); } catch (e) {}
    const loadoutTook = asked === want;""",
    '1a the loadout is checked against intent')

sub(u"""    const r = await FDRV.playMatch({policy, timeoutMs: 220000, alreadyStarted: true});
    rows.push(r && r.err ? {err: r.err}
      : {pPts: r.pPts, oPts: r.oPts, target: r.target, dealt,""",
    u"""    const r = await FDRV.playMatch({policy, timeoutMs: 220000, alreadyStarted: true});
    /* and the pool, read AFTER the match has actually dealt dice */
    let dealt = null;
    try { dealt = (G.pool || []).map(d => d.mat).sort().join(','); } catch (e) {}
    rows.push(r && r.err ? {err: r.err}
      : {pPts: r.pPts, oPts: r.oPts, target: r.target, dealt, asked, want,
         loadoutTook,""",
    '1b the pool is read after the deal')

# ── 2. a cell that did not reach the cap refuses ────────────────────
sub(u"""  return {
    rows, matches: good.length,
    ranToTheCap: good.filter(r => r.hitTheCap).length,""",
    u"""  /* A CELL THAT DID NOT REACH THE CAP HAS NO CEILING TO REPORT. This was a
     field before and the table was printed over it: mostRanToTheCap came back
     false in both band runs and the 17/22/23 unreachable counts were computed
     anyway. It refuses now. The reason it failed is worth stating - the RIVAL
     reaches its target and ends the match long before the player's eighth turn,
     so tier 7 does not produce a capped match, it produces a short one. */
  const capped = good.filter(r => r.hitTheCap).length;
  const refusal = (good.length && capped < good.length)
    ? ('only ' + capped + ' of ' + good.length + ' matches reached the cap ' +
       '(pTurns ' + JSON.stringify(good.map(r => r.pTurns)) + ') - the rival ' +
       'ended them first, so these totals are "what the player scored before ' +
       'losing", not a ceiling')
    : null;
  return {
    rows, matches: good.length, refusal,
    loadoutTook: good.length ? good.every(r => r.loadoutTook) : null,
    asked: good.length ? good[0].asked : null,
    want: good.length ? good[0].want : null,
    /* the only quantity the short matches could support, reported so the next
       design chooses deliberately between normalising and stopping the rival */
    perTurn: good.length ? good.map(r => r.pTurns ? Math.round(r.pPts / r.pTurns) : null) : [],
    ranToTheCap: capped,""",
    '2 a cell without capped matches refuses')

# ── 3. the table skips refused cells ────────────────────────────────
sub(u"""Object.keys(out.cells).forEach(key => {
  const c = out.cells[key];""",
    u"""Object.keys(out.cells).forEach(key => {
  const c = out.cells[key];
  /* skip a cell that refused - a table row built on a non-ceiling is worse
     than a missing row, because it looks like an answer */
  if (c.refusal) return;
  if (c.loadoutTook === false) return;""",
    '3 the table skips refused cells')

sub(u"""  everyCellRan: Object.keys(out.cells).every(k => out.cells[k].matches >= 2),""",
    u"""  everyCellRan: Object.keys(out.cells).every(k => out.cells[k].matches >= 2),
  /* the two that were vacuous or ignored last time */
  everyLoadoutTook: Object.keys(out.cells).every(k => out.cells[k].loadoutTook === true),
  noCellRefused: Object.keys(out.cells).every(k => !out.cells[k].refusal),""",
    '4 the verdict covers both')

sub(u"""  bandsAreDistinct: BAND_LIST.length < 2 ? true : (function () {
    const d = BAND_LIST.map(b => (out.cells['b' + b + '/bank500'] || {}).dealt);
    return d.every(Boolean) && new Set(d).size === d.length;
  })(),""",
    u"""  /* REPLACED, not repaired. Comparing bands to each other cannot be asked when
     one band runs per invocation, and short-circuiting to true made it vacuous
     in the configuration actually shipped. everyLoadoutTook above compares each
     cell to the loadout it ASKED FOR, which is answerable with one band. */""",
    '5 the vacuous guard is replaced')

sub(u"""  gearRaisesTheCeiling: BAND_LIST.length < 2 ? true : (function () {
    const a = (out.cells['b1/bank500'] || {}).max, b = (out.cells['b3/bank500'] || {}).max;
    return a != null && b != null && b > a;
  })(),""",
    u"""""",
    '6 the cross-band claim goes with it')

code = s
# the KEY, not the word - edit 5's replacement comment names it too, and
# counting the bare string called it twice. Third time this session an assert
# counted a mention instead of the thing.
if 'loadoutTook' not in code or code.count('everyLoadoutTook:') != 1:
    sys.exit('the loadout check is not wired (nothing written)')
if 'bandsAreDistinct' in code:
    sys.exit('the vacuous guard survives (nothing written)')
if code.count('if (c.refusal) return;') != 1:
    sys.exit('the table does not skip refused cells (nothing written)')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d edits (%s)' % (len(edits), ', '.join(edits)))
