# -*- coding: utf-8 -*-
"""P444 - Phase 3, part 1: the lane-marker lifetime, named and enforced.

WHAT THE MEASUREMENT FOUND (docs/EFFECT_LIFETIME.md). Snare, Snuff and Fog are
armed with one idiom - {lane, live, turn:(oppTurnCount||0)+1} - where `turn` IS
the window. Snare and Fog gate on `turn===oppTurnCount`. Snuff sets the field
twice and never reads it.

THE PRIMITIVE IS THREE FUNCTIONS, and the gate is inside one of them so it
cannot be skipped:

    _lmArm(key,lane,turns,extra)   place a marker on a lane for N opponent turns
    _lmDue(key)                    is it armed for THIS opponent turn?
    _lmSpend(key)                  spend one turn: re-arm for the next, or retire

THIS RATIFIES SNUFF'S WINDOW rather than guessing it. Denis's ruling was that
the question - what IS Snuff's window meant to be - belongs with the framework
that answers it, not with a drive-by fix. The framework's answer is that a lane
marker is armed for a specific opponent turn, because that is what two of the
three already do and what the field was put there for. Snuff now gates.

AND IT IS BEHAVIOUR-IDENTICAL TODAY, which is measured, not assumed:
G.oppTurnCount increments at line ~26944, BEFORE Snuff's check at ~26956, and
placement always arms for +1 - so `live` alone already lands on exactly the turn
the gate selects. The gate changes what happens on paths that do not currently
occur (a resumed save, a placement made mid-opponent-turn), which is the point.

WHAT THE PRIMITIVE DELIBERATELY DOES NOT ABSORB. Retirement policy differs and
that difference is real:
  * SNARE is one turn and consumed on the bite - it clears `live` inside the
    branch where it actually halved something, and its one-turn window is
    enforced BY THE GATE rather than by clearing. Its own comment says the
    window is what makes it a wager: "until it fires tested at 97.7% inside six
    turns, which is not a bet."
  * FOG and SNUFF run for `turns` opponent turns and re-arm.
So `_lmSpend` handles the counter, and Snare does not call it. Folding Snare's
"consumed on the bite" into a shared spend would have quietly given it a second
turn, which is the exact wager the comment says it must not have.

TRADE IS NOT MIGRATED AND MUST NOT BE. It has no `live`, no `turn` and no
window; it is a swap log unwound newest-first. The plan's own sentence groups it
with these three, so the exclusion is written at the primitive itself where
anyone extending this will read it.
"""
import io, os, re

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   'fark_proto.html')
with io.open(SRC, encoding='utf-8') as f:
    s = f.read()
orig = s

# ── the primitive, declared just above the first thing that arms a marker ──
ANCHOR = u"      G._snare={lane:c.lane,live:true,turn:(G.oppTurnCount||0)+1,x2:(c&&c.mult===2)||false};"
assert s.count(ANCHOR) == 1, 'snare placement matched %d' % s.count(ANCHOR)
s = s.replace(ANCHOR,
  u"""      _lmArm('_snare',c.lane,1,{x2:(c&&c.mult===2)||false});""")

FOG_OLD = u"""      G._fog={lane:c.lane,live:true,turn:(G.oppTurnCount||0)+1,
        turns:((c&&c.mult===2)?2:1)};/* see the note on _snare */"""
assert s.count(FOG_OLD) == 1, 'fog placement matched %d' % s.count(FOG_OLD)
s = s.replace(FOG_OLD, u"""      _lmArm('_fog',c.lane,((c&&c.mult===2)?2:1));""")

SNUFF_OLD = u"""      G._snuff={lane:c.lane,live:true,turn:(G.oppTurnCount||0)+1,
        turns:((c&&c.mult===2)?2:1)};/* see the note on _snare */"""
assert s.count(SNUFF_OLD) == 1, 'snuff placement matched %d' % s.count(SNUFF_OLD)
s = s.replace(SNUFF_OLD, u"""      _lmArm('_snuff',c.lane,((c&&c.mult===2)?2:1));""")

# ── the gates ──
SNARE_GATE = u"      if(G._snare&&G._snare.live&&G._snare.turn===G.oppTurnCount){"
assert s.count(SNARE_GATE) == 1
s = s.replace(SNARE_GATE, u"      if(_lmDue('_snare')){")

FOG_GATE = u"      if(G._fog&&G._fog.live&&G._fog.turn===G.oppTurnCount){"
assert s.count(FOG_GATE) == 1
s = s.replace(FOG_GATE, u"      if(_lmDue('_fog')){")

# SNUFF'S GATE IS THE ONE THAT CHANGES. It read `live` alone.
SNUFF_GATE = u"  if(G._snuff&&G._snuff.live){"
assert s.count(SNUFF_GATE) == 1
s = s.replace(SNUFF_GATE, u"  if(_lmDue('_snuff')){")

# ── the spends ──
FOG_SPEND = u"""        /* KINDRED holds it for a second opponent turn (#32) */
        G._fog.turns=(G._fog.turns||1)-1;
        if(G._fog.turns>0)G._fog.turn=(G.oppTurnCount||0)+1;
        else G._fog.live=false;"""
assert s.count(FOG_SPEND) == 1, 'fog spend matched %d' % s.count(FOG_SPEND)
s = s.replace(FOG_SPEND,
  u"""        /* KINDRED holds it for a second opponent turn (#32) */
        _lmSpend('_fog');""")

# SNARE'S RETIREMENT IS A FOURTH VERB, not an omission. It is CONSUMED on the
# bite, which is not "spent a turn" - it never comes back regardless of how many
# turns it had. Leaving it as a raw `G._snare.live=false` would have left one
# field-poke outside the primitive, and a primitive with one exception is how
# the next person justifies a second.
SNARE_RETIRE = u"          G._snare.live=false;"
assert s.count(SNARE_RETIRE) == 1, 'snare retire matched %d' % s.count(SNARE_RETIRE)
s = s.replace(SNARE_RETIRE, u"          _lmRetire('_snare');")

SNUFF_SPEND = u"""    /* KINDRED holds it for a second turn: spend one, and re-arm for the next
       opponent turn rather than clearing */
    G._snuff.turns=(G._snuff.turns||1)-1;
    if(G._snuff.turns>0)G._snuff.turn=(G.oppTurnCount||0)+1;
    else G._snuff.live=false;"""
assert s.count(SNUFF_SPEND) == 1, 'snuff spend matched %d' % s.count(SNUFF_SPEND)
s = s.replace(SNUFF_SPEND,
  u"""    /* KINDRED holds it for a second turn: spend one, and re-arm for the next
       opponent turn rather than clearing */
    _lmSpend('_snuff');""")

# ── declare the primitive above the arming site ──
DECL_ANCHOR = u"function _firstStrike("
assert s.count(DECL_ANCHOR) >= 1, '_firstStrike anchor missing'
i = s.index(DECL_ANCHOR)
s = s[:i] + u"""/* == LANE-MARKER LIFETIME (Phase 3) ====================================
   Snare, Snuff and Fog each put a mark on ONE LANE of the opponent's row, for
   a SPECIFIC opponent turn, and then retire. That is a lifetime: a placement,
   a window and an expiry. Before this it was an idiom copied three times -
   {lane, live, turn} - and copied idioms drift. It had: Snare and Fog gated on
   `turn===G.oppTurnCount`; SNUFF SET THAT FIELD TWICE AND NEVER READ IT, so its
   window was "the next time this check runs" rather than a turn it named.

   THE GATE LIVES IN _lmDue SO IT CANNOT BE SKIPPED. That is the whole point of
   the primitive - not that the three become shorter, but that a fourth marker
   cannot be written without a window, and this one cannot lose its window to a
   later edit.

   Snuff's gate is a real behaviour decision, taken here rather than guessed
   earlier: a lane marker is armed for a NAMED opponent turn. Identical on
   today's paths - oppTurnCount increments before every one of these checks and
   placement always arms for +1, measured, not assumed - and different on the
   paths where the count and the mark disagree, which is what a window is for.

   RETIREMENT IS NOT SHARED, deliberately. Snare is ONE turn and is consumed on
   the bite: it clears inside the branch where it actually halved something, and
   its one-turn window is enforced by the gate rather than by clearing. Fog and
   Snuff run for `turns` turns and re-arm. Giving Snare a shared _lmSpend would
   hand it a second turn - the exact wager its own comment says it must not
   have ("until it fires tested at 97.7% inside six turns, which is not a bet").

   TRADE IS NOT ONE OF THESE and must not be migrated onto it. The effect-system
   plan's own sentence groups Trade with these three; measured, G._tradeSwaps is
   an ARRAY of swap records unwound newest-first, with no live, no turn and no
   window, and it snapshots across a save. It has an undo, not an expiry. */
function _lmArm(key,lane,turns,extra){
  if(!G)return;
  var m={lane:lane,live:true,turn:(G.oppTurnCount||0)+1,turns:turns||1};
  if(extra)for(var k in extra)if(extra.hasOwnProperty(k))m[k]=extra[k];
  G[key]=m;
}
/* THE WINDOW GATE. Every read of a lane marker goes through this. */
function _lmDue(key){
  var m=G&&G[key];
  return !!(m&&m.live&&m.turn===G.oppTurnCount);
}
/* CONSUMED. Distinct from _lmSpend on purpose: a marker that fired is gone
   whatever its turn count said, whereas spending a turn may re-arm. Snare is
   the only consumer today - it retires inside the branch where it actually
   halved something. */
function _lmRetire(key){var m=G&&G[key];if(m)m.live=false;}
/* Spend one turn of the window: re-arm for the next opponent turn, or retire.
   Snare does not call this - see the note above. */
function _lmSpend(key){
  var m=G&&G[key];if(!m)return;
  m.turns=(m.turns||1)-1;
  if(m.turns>0)m.turn=(G.oppTurnCount||0)+1;
  else m.live=false;
}
""" + s[i:]

assert s != orig, 'nothing changed'
# EXACT: three arms, three gates, two spends. A floor would pass a run where one
# replacement silently failed and left a marker on the old hand-rolled shape.
for name, want in [('_lmArm(', 3), ("_lmDue('", 3), ("_lmSpend('", 2),
                   ("_lmRetire('", 1)]:
    got = s.count(name) - (1 if name.endswith('(') else 0)  # minus declaration
    assert got == want, '%s appears %d times (want %d)' % (name, got, want)
# and no hand-rolled gate survives
code = re.sub(r'/\*.*?\*/', '', s, flags=re.S)
for v in ('_snare', '_snuff', '_fog'):
    bad = re.findall(r'G\.' + v + r'\.(live|turn)\b', code)
    assert not bad, '%s still touched directly: %r' % (v, bad)
with io.open(SRC, 'w', encoding='utf-8', newline='') as f:
    f.write(s)
print('P444 applied: 3 arms, 3 gates, 2 spends on the lane-marker primitive')
