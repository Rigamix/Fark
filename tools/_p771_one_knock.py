# -*- coding: utf-8 -*-
"""P771: legacy cluster 4 - one knock, two cards.

Quick Hands (scoring dice -> 2s) and Grog's Bump (-> 3s) were twin
blocks: same victim filter, same highest-value-first sort, same
two-victim cap, same announce shape, same rescore tail. The classic
'same block twice' - one parameterized _playerKnock now, the face and
the name being the only data that differs. Declared hoisted in step()
beside _oppRescore so it can write total/used in the same closure.
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


sub("""      if(G._playerQuickHandsArmed){
        G._playerQuickHandsArmed=false;
        var _qhScoring=G.oppDice.filter(function(d){return !d.kept&&(d.val===1||d.val===5);});
        if(_qhScoring.length>0){
          /* Highest-value first, take up to 2. */
          var _qhVics=_qhScoring.slice().sort(function(a,b){return(b.val===1?100:50)-(a.val===1?100:50);}).slice(0,2);
          _qhVics.forEach(function(_qhVic){_qhVic.val=2;reDrawDieFace(_qhVic);});
          triggerCard('quick_hands','QUICK HANDS → 2',true);
          setStatusMsg("QUICK HANDS — "+G.rung.name+"'S "+(_qhVics.length>1?_qhVics.length+" DICE → 2":"DIE → 2"),'gold');
          var _rrQ=_oppRescore();total=_rrQ.total;used=_rrQ.used;/* P770 */
        }
      }
      /* Player-armed Grog's Bump: knock the opp's TWO scoring dice (1s/5s) → 3s.
         Mirrors Quick Hands (which swaps to 2s); auto-fires here on the NPC roll
         so the player only had to arm it while yielding. */
      if(G._playerGrogsBumpArmed){
        G._playerGrogsBumpArmed=false;
        var _gbScoring=G.oppDice.filter(function(d){return !d.kept&&(d.val===1||d.val===5);});
        if(_gbScoring.length>0){
          var _gbVics=_gbScoring.slice().sort(function(a,b){return(b.val===1?100:50)-(a.val===1?100:50);}).slice(0,2);
          _gbVics.forEach(function(_gbVic){_gbVic.val=3;reDrawDieFace(_gbVic);});
          triggerCard('grogs_bump',"GROG'S BUMP → 3",true);
          setStatusMsg("GROG'S BUMP — "+G.rung.name+"'S "+(_gbVics.length>1?_gbVics.length+" DICE → 3":"DIE → 3"),'gold');
          var _rrG=_oppRescore();total=_rrG.total;used=_rrG.used;/* P770 */
        }
      }""",
    """      /* P771: ONE KNOCK, TWO CARDS. Quick Hands (→2) and Grog's Bump
         (→3) were twin blocks - same victims, same sort, same cap, same
         announce shape, same rescore. The face and the name are the
         only data. Both auto-fire here on the rival's roll; the player
         armed them while yielding. */
      function _playerKnock(cid,face,name){
        var _sc=G.oppDice.filter(function(d){return !d.kept&&(d.val===1||d.val===5);});
        if(!_sc.length)return;
        /* highest-value first, take up to 2 */
        var _v=_sc.slice().sort(function(a,b){return(b.val===1?100:50)-(a.val===1?100:50);}).slice(0,2);
        _v.forEach(function(d){d.val=face;reDrawDieFace(d);});
        triggerCard(cid,name+' → '+face,true);
        setStatusMsg(name+" — "+G.rung.name+"'S "+(_v.length>1?_v.length+" DICE → "+face:"DIE → "+face),'gold');
        var _rr=_oppRescore();total=_rr.total;used=_rr.used;
      }
      if(G._playerQuickHandsArmed){G._playerQuickHandsArmed=false;_playerKnock('quick_hands',2,'QUICK HANDS');}
      if(G._playerGrogsBumpArmed){G._playerGrogsBumpArmed=false;_playerKnock('grogs_bump',3,"GROG'S BUMP");}""",
    'one knock')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d (%s)' % (len(edits), ', '.join(edits)))
