# -*- coding: utf-8 -*-
"""P857: Denis's notes 1 and 5 - the bust verdict stops paying two
beats, and Grog's Bump waits for the dice.

NOTE 1 - "bust animation and red light happens half a second too late".
Measured, and it is 880ms, not 500: after the dice have visibly
stopped the player waits DEADROLL_BEAT_MS 260 + BUST_PAUSE_MS 600 +
doBust's 20ms hop. The two beats were written as ALTERNATIVES - the
comment at DEADROLL_BEAT_MS says the deadRoll beat is "deliberately
shorter than the bust's" - but on the ordinary bust route they are
SEQUENTIAL: the deadRoll seam waits for the settle, serves its 260,
then calls _delayedDoBust, which re-arms 600 on a row that is already
settled. Its _afterRowSettle is a no-op re-check there; only the
trailing timeout survives, and it lands on top of the beat already
paid.
Fixed by making the beat a PARAMETER of the one helper rather than a
constant baked into it: _delayedDoBust(dice, beatMs) defaults to
BUST_PAUSE_MS for the seven call sites that wait from scratch, and the
deadRoll seam - the only one that has already served a beat - passes
0. 880ms -> 280ms on the route Denis actually hits, with the other
seven untouched.
Recorded while here (NOT changed): the rival's bust visual fires
synchronously at its seam, so the player's was ~880ms later than the
rival's for the same event. This closes most of that gap; the
remaining 280 is the deliberate verdict pause.

NOTE 5 - "Grog bump needs to happen after the settle not during the
roll". The NPC card-effects loop is the one branch of _afterRollImpl
still running on handleRoll's fixed 480ms budget while the physics
tape plays to ~2000ms, so the swap rewrites and re-throws a die the
player has not seen land. P574 fixed exactly this for the two branches
either side of it (the deadRoll seam and the bust route) with
_afterRowSettle and left this loop on the old path. Its symptom is the
one P574's own comment quotes verbatim: "it rerolls dice even before
they land so you don't even understand what it's doing."
The loop is wrapped in the same helper, with the same guard. The
player-held copy of the card already waits correctly (_playerKnock
runs inside _afterOppSettle), so this brings the two implementations
of one card onto the same rule.
"""
import io, os, sys, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'fark_proto.html')
s = io.open(P, encoding='utf-8', newline='').read()
edits = []


def sub(old, new, label):
    global s
    if s.count(old) == 1:
        s = s.replace(old, new)
        edits.append(label)
        return
    pat = re.escape(old).replace('\\\n', '\n').replace('\n', '\\r?\n')
    ms = list(re.finditer(pat, s))
    if len(ms) != 1:
        sys.exit('ANCHOR x%d for %s (nothing written)' % (len(ms), label))
    m = ms[0]
    rep = new.replace('\n', '\r\n') if '\r\n' in m.group(0) else new
    s = s[:m.start()] + rep + s[m.end():]
    edits.append(label)


# ── NOTE 1: the beat becomes a parameter of the one helper ───────────
sub("""function _delayedDoBust(_freeArr){""",
    """/* P857: THE BEAT IS THE CALLER'S. Every route into the bust visual used
   to pay BUST_PAUSE_MS unconditionally, including the one route that had
   ALREADY served DEADROLL_BEAT_MS on the same settled row - so the
   ordinary bust cost 260+600+20 = 880ms after the dice stopped, which is
   Denis's "half a second too late". The seven from-scratch callers keep
   the default; the deadRoll seam passes 0 because its beat is spent. */
function _delayedDoBust(_freeArr,_beatMs){""",
    '1a beat parameter')

sub("""  _afterRowSettle('#playerDiceRow',BUST_PAUSE_MS,doBust);""",
    """  _afterRowSettle('#playerDiceRow',(_beatMs===undefined?BUST_PAUSE_MS:_beatMs),doBust);/* P857 */""",
    '1b beat used')

sub("""      if(_tryBustSave(free))return;
      _delayedDoBust(free);
    });
    return;""",
    """      if(_tryBustSave(free))return;
      /* P857: BEAT ALREADY SERVED. This callback only runs after
         _afterRowSettle waited for the row AND paid DEADROLL_BEAT_MS, so
         asking for BUST_PAUSE_MS again stacked a second pause on a table
         that stopped moving 260ms ago. */
      _delayedDoBust(free,0);
    });
    return;""",
    '1c deadRoll seam pays zero')

sub("""var DEADROLL_BEAT_MS=260;""",
    """var DEADROLL_BEAT_MS=260;
/* P857: these two are ALTERNATIVES, never a sum. Whichever route reaches
   the verdict serves exactly one of them - the deadRoll seam its own, or
   _delayedDoBust its default for callers that have waited for nothing
   yet. If a third route is ever added, give it one beat, not both. */""",
    '1d the rule written down')

# ── NOTE 5: the BUMP's mutation waits for the throw ──────────────────
# Scoped to the swap's own mutation, NOT the whole oCards loop: the
# re-check block after that loop reads `free` and carries its own
# `return`s out of _afterRollImpl, so wrapping the loop would turn those
# into callback-local returns and let code below run that used to be
# skipped. Changing control flow to fix a timing bug is the P833 trap.
sub("""        var _sbVictims=_sbSorted.slice(0,_sbN);
        _sbVictims.forEach(function(victim){
          victim.val=_sbTo;""",
    """        var _sbVictims=_sbSorted.slice(0,_sbN);
        /* P857 (Denis: "Grog bump need to happen after the settle not
           during the roll"): this was the last effect in _afterRollImpl
           still firing on handleRoll's fixed 480ms budget while the
           physics tape runs to ~2000ms - so it rewrote a face and
           re-threw the mesh ON TOP of a throw still in flight. P574
           wrapped the branches either side of this one and missed it;
           the symptom is the line P574's own comment quotes: "it rerolls
           dice even before they land so you don't even understand what
           it's doing." The player-held copy of this card already waits
           (via _afterOppSettle), so the two implementations of one card
           now obey one rule.
           WRAPPED HERE, NOT AROUND THE LOOP: the re-check below the loop
           returns out of _afterRollImpl, and moving it into a callback
           would silently turn those into callback-local returns. */
        _afterRowSettle('#playerDiceRow',0,function(){
        if(typeof G==='undefined'||!G||G._endMatchFired)return;
        _sbVictims.forEach(function(victim){
          victim.val=_sbTo;""",
    '5a bump waits for the settle')

sub("""            (function(_v){setTimeout(function(){if(_v.el)_v.el.classList.remove('eff-glow-red');},900);})(victim);
          }
        });
        /* Pulse the NPC card so it's obvious which card fired */
        triggerCard(cid,npc.name+'!',false);
        setStatusMsg(npc.name+(_sbN>1?' — '+_sbN+' DICE → '+_sbTo+'!':' — DIE → '+_sbTo+'!'),'red');
        try{SFX.err&&SFX.err();}catch(e){}
        try{Haptic.bust&&Haptic.bust();}catch(e){}""",
    """            (function(_v){setTimeout(function(){if(_v.el)_v.el.classList.remove('eff-glow-red');},900);})(victim);
          }
        });
        /* Pulse the NPC card so it's obvious which card fired - inside the
           settle callback with the swap, so the card and the dice speak
           at the same moment (P857) */
        triggerCard(cid,npc.name+'!',false);
        setStatusMsg(npc.name+(_sbN>1?' — '+_sbN+' DICE → '+_sbTo+'!':' — DIE → '+_sbTo+'!'),'red');
        try{SFX.err&&SFX.err();}catch(e){}
        try{Haptic.bust&&Haptic.bust();}catch(e){}
        });/* P857: closes the settle wrap */""",
    '5b bump wrap closes')

for needed in ['function _delayedDoBust(_freeArr,_beatMs){','_delayedDoBust(free,0);',
               "_afterRowSettle('#playerDiceRow',0,function(){"]:
    if needed not in s:
        sys.exit('KEEPER MISSING: %s (nothing written)' % needed)
io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d edits (%s)' % (len(edits), ', '.join(edits)))
