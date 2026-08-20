# -*- coding: utf-8 -*-
"""P811: Stargazer's promise is per-die, and now it actually holds.

Denis: "Does stargazer doesn't actually predict the next roll.. Are
they random numbers? It's EXACTLY the type of stuff I want you to fix
when I ask you to do card audits."

He is right, and the mechanism is structural: the player's peek
pre-rolled values for the CURRENT free dice and stored them as a bare
index array; famApplyRollForces applied them only when the next roll's
free count matched EXACTLY. But rolling requires keeping at least one
scorer first, so the next roll almost always has fewer free dice - the
gate failed, the peek was silently discarded, and the 'predicted' roll
was a fresh random draw. The rival's own stargazer (P766) already
predicts per-seat and plays with the knowledge; the player's could
essentially never fire on a real path.

The fix is the same contract the rival has: the promise is PER DIE
(lane-keyed). Whichever of the peeked dice actually roll next take
their promised face; a die the player keeps simply never consumes its
promise. Legacy index-array saves (numbers) keep the old exact-count
behaviour so a mid-match resume from an older build cannot misapply
values to the wrong dice.
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
    hits = re.findall(pat, s)
    if len(hits) != 1:
        sys.exit('ANCHOR x%d for %s (nothing written)' % (len(hits), label))
    s = re.sub(pat, lambda m: new, s, count=1)
    edits.append(label)


# ── the peek stores lane-keyed promises ──
sub("""    var free=G.pool.filter(function(d){return !d.committed&&!d._frozen;});
    if(!free.length)return false;
    G._famPeekVals=free.map(function(d){return _rollD(d);});
    famLog('STARGAZER — NEXT ROLL: '+G._famPeekVals.join(' · '));/* P708: only Ill Omen says OMEN */
    return true;""",
    """    var free=G.pool.filter(function(d){return !d.committed&&!d._frozen;});
    if(!free.length)return false;
    /* P811: the promise is PER DIE (lane-keyed), not an index array.
       The old array only applied when the next roll's free count
       matched exactly - and rolling requires keeping a scorer first,
       so it almost never did: the peek was silently discarded and the
       'prediction' was a fresh random roll (Denis caught it live).
       Same contract as the rival's per-seat peek: whichever of these
       dice roll next take their promised face; a kept die's promise
       goes unused. */
    G._famPeekVals=free.map(function(d){return {lane:d.lane,val:_rollD(d)};});
    famLog('STARGAZER — NEXT ROLL: '+G._famPeekVals.map(function(p){return p.val;}).join(' · '));/* P708: only Ill Omen says OMEN */
    return true;""",
    'the peek is lane-keyed')

# ── the consume applies per lane ──
sub("""  if(G._famPeekVals&&G._famPeekVals.length===free.length){
    free.forEach(function(d,i){d.val=G._famPeekVals[i];try{reDrawDieFace(d);}catch(e){}});
    famLog('THE STARS HOLD');/* P708 */
  }""",
    """  if(G._famPeekVals&&G._famPeekVals.length){
    /* P811: lane-keyed consume - every rolling die takes its promised
       face. Legacy index-array saves (bare numbers) keep the old
       exact-count contract so an old mid-match resume cannot misapply
       promises to the wrong dice. */
    if(typeof G._famPeekVals[0]==='number'){
      if(G._famPeekVals.length===free.length){
        free.forEach(function(d,i){d.val=G._famPeekVals[i];try{reDrawDieFace(d);}catch(e){}});
        famLog('THE STARS HOLD');/* P708 */
      }
    }else{
      var _pk={};G._famPeekVals.forEach(function(p){if(p&&p.lane!==undefined)_pk[p.lane]=p.val;});
      var _pkHit=0;
      free.forEach(function(d){
        if(_pk[d.lane]!==undefined){d.val=_pk[d.lane];_pkHit++;try{reDrawDieFace(d);}catch(e){}}
      });
      if(_pkHit)famLog('THE STARS HOLD');/* P708 */
    }
  }""",
    'the consume is lane-keyed')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d (%s)' % (len(edits), ', '.join(edits)))
