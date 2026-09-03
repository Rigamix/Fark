# -*- coding: utf-8 -*-
u"""P936: state.lastTurn had two definitions, and the ladder's was the wrong one.

FOUND WHILE CHECKING THE LADDER HARNESS BEFORE A SIX-HOUR RUN. The same named
input is computed two ways by the two harnesses that feed it to the same persona
code:

  sim_harness.js:798   var lastTurn=(pTurns+1>=cap)||((G.oPts>=G.target));
  ladder_band.js:174   state.lastTurn = (G.turnNum || 1) >= (G.turnCap || 10);

Four persona bankAt bodies read state.lastTurn (890, 1014, 1141, documented at
494), so the personas play a DIFFERENT ENDGAME in the ladder than in the sim.
One fact, two homes - the defect this whole line of work has been about, sitting
on the input that decides how a persona finishes a match.

AND THE LADDER'S VERSION IS WRONG TWICE OVER:

  turnNum IS THE WRONG COUNTER. P917 established that the capped resource is
  G.pTurns - "a completed player turn (bank or bust)" - while turnNum increments
  at the handover to the rival and came back as 10 on patron matches whose cap
  is 8. So `turnNum>=turnCap` fires EARLIER than the real last turn, on every
  match, telling every persona to play its endgame before the endgame.

  AND IT DROPS THE RIVAL CLAUSE. sim_harness also treats "the rival has already
  reached the target" as a last turn, because it is one - there is no future
  turn worth saving for. The ladder omitted it entirely.

Either error alone shifts every win rate the ladder would have produced.

ONE DEFINITION, TWO CONSUMERS. F.lastTurnFlag(G, pTurns, cap) goes in
sim_harness beside the personas that read it; sim_harness's own site calls it,
and the ladder calls it instead of computing its own. Copying the corrected
expression into the ladder would have fixed today's divergence and left the next
one available.

ALSO: THE LADDER'S TWO SILENT FALLBACKS BECOME LOUD. `catch(e){bank=(G.turnPts
||0)>=300;}` silently substitutes a 300-threshold policy when a persona's bankAt
throws, and `if(!sel||!sel.length)sel=keeps[keeps.length-1].sel;` silently
substitutes a keep when policy.keep does. Over a six-hour run either would
measure a different policy than the one named in every line of output, with
nothing to say it had happened. They now record the substitution and the cell
reports it.
"""
import io, os, sys, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
edits = []


def patch(path, pairs, checks):
    s = io.open(path, encoding='utf-8', newline='').read()
    for i, (old, new) in enumerate(pairs):
        label = '%s #%d' % (os.path.basename(path), i + 1)
        pat = re.escape(old).replace('\\\n', '\n').replace('\n', '\\r?\n')
        ms = list(re.finditer(pat, s))
        if len(ms) != 1:
            sys.exit('ANCHOR x%d for %s (nothing written)' % (len(ms), label))
        m = ms[0]
        rep = new.replace('\n', '\r\n') if '\r\n' in m.group(0) else new
        s = s[:m.start()] + rep + s[m.end():]
        edits.append(label)
    code = re.sub(r'/\*[\s\S]*?\*/', '', s)
    for fn, msg in checks:
        if not fn(code, s):
            sys.exit('%s (nothing written)' % msg)
    io.open(path, 'w', encoding='utf-8', newline='').write(s)


# ── sim_harness: the single definition, and its own site uses it ────
H = os.path.join(ROOT, 'tools', 'sim_harness.js')
patch(H, [
    (u"""F.POLICIES={};""",
     u"""/* P936: THE ONE DEFINITION OF "THIS IS THE LAST TURN". Four persona bankAt
   bodies branch on state.lastTurn, and it was computed independently by this
   file and by ladder_band.js - differently. The ladder keyed it on G.turnNum
   against G.turnCap, but the capped resource is pTurns (P917: turnNum
   increments at the handover and read 10 on patron matches whose cap is 8), so
   it fired EARLY on every match; and it dropped the rival-reached-target
   clause. Personas therefore played a different endgame in the ladder than in
   the sim, on a value they both call by the same name.
   BOTH CLAUSES MATTER. There is no future turn worth saving for when the
   allowance is spent, and none when the rival has already crossed the target. */
F.lastTurnFlag=function(G,pTurns,cap){
  if(!G)return false;
  var c=cap||G.turnCap||8;
  return ((pTurns||0)+1>=c)||((G.oPts||0)>=(G.target||Infinity));
};

F.POLICIES={};"""),
    (u"""          var lastTurn=(pTurns+1>=cap)||((G.oPts>=G.target));""",
     u"""          var lastTurn=F.lastTurnFlag(G,pTurns,cap);/* P936: one definition */"""),
], [
    (lambda c, s: c.count('F.lastTurnFlag=function') == 1,
     'the flag is not defined exactly once'),
    (lambda c, s: c.count('F.lastTurnFlag(G,pTurns,cap)') == 1,
     "sim_harness's own site does not call it"),
    (lambda c, s: 'var lastTurn=(pTurns+1>=cap)' not in c,
     'the inline copy survives in sim_harness'),
])

# ── ladder_band: call it, and make the fallbacks loud ────────────────
L = os.path.join(ROOT, 'tools', 'ladder_band.js')
patch(L, [
    (u"""    state.oppTotal = G.oPts; state.lastTurn = (G.turnNum || 1) >= (G.turnCap || 10);""",
     u"""    state.oppTotal = G.oPts;
    /* P936: FROM THE ONE DEFINITION, not a second one. This used to read
       `(G.turnNum||1) >= (G.turnCap||10)`, which is wrong twice: the capped
       resource is pTurns, not turnNum (P917 - turnNum increments at the
       handover and read 10 on patron matches whose cap is 8), so it told every
       persona "last turn" before it was; and it dropped the rival-reached-
       target clause that sim_harness has. Four persona bankAt bodies branch on
       this, so the personas were playing a different endgame here than in the
       sim, on a value both call by the same name. */
    state.lastTurn = FSIM.lastTurnFlag(G, G.pTurns || 0, G.turnCap || 0);"""),
    (u"""    let sel = null;
    try { sel = policy.keep(free, {keeps: keeps, G: G, state: state, rolls: G.turnRollCount || 0}); } catch (e) {}
    if (!sel || !sel.length) sel = keeps[keeps.length - 1].sel;""",
     u"""    /* P936: A SUBSTITUTED KEEP IS RECORDED. policy.keep throwing used to fall
       through to "the last legal keep" in silence, so a persona that failed on
       some state was measured as a different one - under its own name, in every
       line of output. The fallback stays (a stalled cell is worse) but the cell
       now reports how often it fired. */
    let sel = null;
    try { sel = policy.keep(free, {keeps: keeps, G: G, state: state, rolls: G.turnRollCount || 0}); }
    catch (e) { subKeepErr = subKeepErr || String(e && e.message || e); }
    if (!sel || !sel.length) { subKeep++; sel = keeps[keeps.length - 1].sel; }"""),
    (u"""    let bank = false;
    try { bank = policy.bankAt({turnPts: G.turnPts || 0, diceLeft: free.length - sel.length,
      rolls: G.turnRollCount || 0, state: state, G: G}); } catch (e) { bank = (G.turnPts || 0) >= 300; }""",
     u"""    /* P936: AND A SUBSTITUTED BANK RULE IS RECORDED. This used to silently
       become "bank at 300" whenever a persona's bankAt threw - a policy
       substitution invisible in the output, on a run whose every line names the
       policy it believes it measured. */
    let bank = false;
    try { bank = policy.bankAt({turnPts: G.turnPts || 0, diceLeft: free.length - sel.length,
      rolls: G.turnRollCount || 0, state: state, G: G}); }
    catch (e) { subBank++; subBankErr = subBankErr || String(e && e.message || e);
                bank = (G.turnPts || 0) >= 300; }"""),
], [
    (lambda c, s: c.count('FSIM.lastTurnFlag(G, G.pTurns || 0, G.turnCap || 0)') == 1,
     'the ladder does not call the shared flag'),
    (lambda c, s: 'G.turnNum || 1) >= (G.turnCap' not in c,
     'the ladder still computes its own lastTurn'),
    (lambda c, s: c.count('subBank++') == 1 and c.count('subKeep++') == 1,
     'the substitution counters are not incremented once each'),
])

print('done: %d edits (%s)' % (len(edits), ', '.join(edits)))
