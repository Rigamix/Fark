# -*- coding: utf-8 -*-
u"""P917: the turn cap is soft in three ways, so an envelope has to say which
turns it counted.

THE CAP IS NOT A CAP. _handBackOrCap (36784) ends the match only when BOTH sides
are at cap AND both are below target, and three separate mechanisms add turns
past it:

  1. STARSTONE GRANTS A TURN, not just points. 24867 fires
     G._extraTurn=(G._extraTurn||0)+1 and 36945 spends it while both sides are
     under target. So a starstone loadout is not "+500 a turn over eight turns"
     - it is (base+500) x (8+extras), and the two multiply. That is invisible
     from TURN_CAP and bankAdd alone, which is why an arithmetic table built on
     those two understates band 3.

  2. THE TRAILING PLAYER ALWAYS GETS THE FINAL ANSWER TURN. Same function:
     "brief 1: the trailing player always gets the final answer turn", gated on
     G._finalAnswerUsed. This one matters MOST for an envelope, and neither of
     us named it: an envelope is measured at a tier the player cannot reach, so
     the player is behind in every single match, so every single match collects
     it. That is systematic inflation of the ceiling, not occasional.

  3. A DEAD-EVEN MATCH TAKES ANOTHER ROUND, repeating until broken.

SO THE PROBE STOPS REPORTING ONE CEILING. Matches are classified by what
actually happened - G._endReason is set explicitly at the cap branch, so it is
read rather than inferred - and the ceiling at EXACTLY the cap is reported apart
from the overrun ones. Otherwise the band-3 number quietly absorbs a few
sudden-death turns and the pruning gets built on it.

AND IT EXPLAINS turnNum:10 ON A CAP-8 MATCH without the handover-increment
having to carry all of it. Both are true, and the soft cap means 10 was not
necessarily a miscount - which is worth saying, because I recorded pTurns to fix
a discrepancy that was partly not a fault.
"""
import io, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
edits = []


def sub(path, old, new, label):
    s = io.open(path, encoding='utf-8', newline='').read()
    if s.count(old) != 1:
        sys.exit('ANCHOR x%d for %s (nothing written)' % (s.count(old), label))
    io.open(path, 'w', encoding='utf-8', newline='').write(s.replace(old, new))
    edits.append(label)


DRV = os.path.join(ROOT, 'tools', 'fark_driver.js')
PRB = os.path.join(ROOT, 'tools', 'apv_envelope_bands.js')

# ── 1. the driver reports why the match ended and what added turns ──
sub(DRV,
    u"""      pTurns: (function(){ try { return G ? (G.pTurns || 0) : null; } catch(e){ return null; } })(),""",
    u"""      /* P917: WHY IT ENDED, and what added turns past the cap. The cap is soft -
         starstone grants a turn (24867/36945), the trailing player always gets
         a final answer turn, and a dead-even match takes another round. An
         envelope that does not separate those is measuring a longer match than
         it claims. _endReason is set at the cap branch itself, so it is read
         rather than inferred. */
      endReason: (function(){ try { return G ? (G._endReason || null) : null; } catch(e){ return null; } })(),
      finalAnswerUsed: (function(){ try { return G ? !!G._finalAnswerUsed : null; } catch(e){ return null; } })(),
      extraTurnsLeft: (function(){ try { return G ? (G._extraTurn || 0) : null; } catch(e){ return null; } })(),
      pTurns: (function(){ try { return G ? (G.pTurns || 0) : null; } catch(e){ return null; } })(),""",
    '1 the driver reports the ending')

# ── 2. the probe separates the exactly-at-cap ceiling ───────────────
sub(PRB,
    u"""    rows.push(r && r.err ? {err: r.err}
      : {pPts: r.pPts, oPts: r.oPts, target: r.target, dealt,
         pTurns: r.pTurns, turnCap: r.turnCap, hitTheCap: r.hitTheCap,
         banks: r.banks, busts: r.busts, stalled: r.stalled});""",
    u"""    rows.push(r && r.err ? {err: r.err}
      : {pPts: r.pPts, oPts: r.oPts, target: r.target, dealt,
         pTurns: r.pTurns, turnCap: r.turnCap, hitTheCap: r.hitTheCap,
         endReason: r.endReason, finalAnswerUsed: r.finalAnswerUsed,
         extraTurnsLeft: r.extraTurnsLeft,
         overran: (r.pTurns != null && r.turnCap) ? (r.pTurns > r.turnCap) : null,
         banks: r.banks, busts: r.busts, stalled: r.stalled});""",
    '2a the probe records the overrun')

sub(PRB,
    u"""  const good = rows.filter(r => r && !r.err && !r.stalled);
  const totals = good.map(r => r.pPts);
  return {
    rows, matches: good.length,
    ranToTheCap: good.filter(r => r.hitTheCap).length,
    dealt: good.length ? good[0].dealt : null,
    pTurns: good.map(r => r.pTurns),
    totals,
    max: totals.length ? Math.max.apply(null, totals) : null,
    mean: totals.length ? Math.round(totals.reduce((a, b) => a + b, 0) / totals.length) : null,
  };""",
    u"""  const good = rows.filter(r => r && !r.err && !r.stalled);
  const totals = good.map(r => r.pPts);
  /* THE CEILING AT EXACTLY THE CAP, apart from the overrun ones. The cap is
     soft three ways and an envelope that mixes them is measuring a longer match
     than it claims - and the trailing-player final answer turn fires in EVERY
     match here, because an envelope is taken where the player cannot win. */
  const atCap = good.filter(r => r.pTurns != null && r.turnCap &&
                                 r.pTurns === r.turnCap);
  const over = good.filter(r => r.overran === true);
  const maxOf = a => a.length ? Math.max.apply(null, a.map(r => r.pPts)) : null;
  return {
    rows, matches: good.length,
    ranToTheCap: good.filter(r => r.hitTheCap).length,
    exactlyAtCap: atCap.length, overran: over.length,
    endedEarly: good.length - atCap.length - over.length,
    endReasons: good.map(r => r.endReason),
    finalAnswerUsed: good.filter(r => r.finalAnswerUsed).length,
    dealt: good.length ? good[0].dealt : null,
    pTurns: good.map(r => r.pTurns),
    totals,
    /* the honest ceiling: exactly-at-cap only. maxAny is reported beside it so
       the inflation is visible rather than absorbed. */
    ceilingAtCap: maxOf(atCap),
    ceilingOverran: maxOf(over),
    max: totals.length ? Math.max.apply(null, totals) : null,
    mean: totals.length ? Math.round(totals.reduce((a, b) => a + b, 0) / totals.length) : null,
  };""",
    '2b the probe separates the two ceilings')

sub(PRB,
    u"""Object.keys(out.cells).forEach(key => {
  const c = out.cells[key];
  if (c.max == null) return;
  const bossCeil = Math.round(c.max * (out.caps.boss / out.caps.patron));""",
    u"""Object.keys(out.cells).forEach(key => {
  const c = out.cells[key];
  /* THE TABLE USES THE AT-CAP CEILING, falling back to the overall max only
     when no match landed exactly on the cap - and saying which, because a
     pruning decision built on an overrun ceiling would strike off fewer cells
     than it should and look conservative while being wrong. */
  const ceil = (c.ceilingAtCap != null) ? c.ceilingAtCap : c.max;
  const ceilFrom = (c.ceilingAtCap != null) ? 'at-cap' : 'any';
  if (ceil == null) return;
  const bossCeil = Math.round(ceil * (out.caps.boss / out.caps.patron));""",
    '2c the table uses the at-cap ceiling')

sub(PRB,
    u"""    out.table.push({cell: key, tier: t.tier,
      patronTarget: t.patronMax, patronCeiling: c.max,
      patronReachable: c.max >= t.patronMax,""",
    u"""    out.table.push({cell: key, tier: t.tier, ceilFrom,
      patronTarget: t.patronMax, patronCeiling: ceil,
      patronReachable: ceil >= t.patronMax,""",
    '2d the table row carries its provenance')

sub(PRB,
    u"""  /* and the matches must have spent their turns, or these are not ceilings */
  mostRanToTheCap: Object.keys(out.cells)
    .every(k => out.cells[k].ranToTheCap >= Math.max(1, out.cells[k].matches - 1)),""",
    u"""  /* and the matches must have spent their turns, or these are not ceilings */
  mostRanToTheCap: Object.keys(out.cells)
    .every(k => out.cells[k].ranToTheCap >= Math.max(1, out.cells[k].matches - 1)),
  /* the finding this patch exists for: an envelope taken where the player
     cannot win collects the trailing-player final answer turn every time, so
     if NOTHING overran, the soft cap is not doing what the code says */
  theSoftCapIsVisible: Object.keys(out.cells)
    .some(k => out.cells[k].overran > 0 || out.cells[k].finalAnswerUsed > 0),""",
    '2e the soft cap must be visible')

print('done: %d edits (%s)' % (len(edits), ', '.join(edits)))
