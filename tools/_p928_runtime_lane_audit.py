# -*- coding: utf-8 -*-
u"""P928: the lane census runs on every real reorder, and P927's guard stops whispering.

WHY THE PROBE WAS NOT ENOUGH. apv_lane_census walks live G for lane-bearing
records and asserts each still points at its own die after a reorder. It passed.
But it only ever found the records THE PROBE ITSELF SEEDED - four kinds plus a
planted canary - so "nothing unenrolled turned up" was a statement about the
state that one run was in, not about the game. A record minted only under some
card pairing is invisible to any single run, which is precisely the shape of the
thing P922 missed.

So the same walk moves into the reorder path under window._fkDbgOn. Every
reorder in every playtest becomes a census, and coverage accrues over play
instead of over one probe. The numDice hazard already got a permanent runtime
guard (P927) and the lane hazard got a one-off probe; there is no property of
the two that justifies the difference.

THE IGNORE LIST FAILS SAFE, and that is the whole reason it is an ignore list.
Rival-side records index the rival board, so a player reorder must not move them
and the audit would flag them forever. Naming them as exclusions means
FORGETTING one gives noise, not silence - the opposite failure direction from an
enrolment roster, which is what has been wrong four times. It starts empty:
nothing has been observed to need it, and a path only earns a place here after
being seen and classified.

AND P927 THROWS IN DEV NOW. It counted and printed a console line, and that
comment has failed three times precisely because the warning was passive. Two
fixes: the throw is raised OUTSIDE the try that detects the fault - inside, the
catch swallowed it, which would have made the loud version silently no-op - and
it fires only under _fkDbgOn, so a player never sees it.
"""
import io, os, sys, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'fark_proto.html')
s = io.open(P, encoding='utf-8', newline='').read()
edits = []


def sub(old, new, label):
    global s
    pat = re.escape(old).replace('\\\n', '\n').replace('\n', '\\r?\n')
    ms = list(re.finditer(pat, s))
    if len(ms) != 1:
        sys.exit('ANCHOR x%d for %s (nothing written)' % (len(ms), label))
    m = ms[0]
    rep = new.replace('\n', '\r\n') if '\r\n' in m.group(0) else new
    s = s[:m.start()] + rep + s[m.end():]
    edits.append(label)


# ── 1. the walk and the audit, beside the rosters they exist to distrust ──
sub(u"""function _famLaneRecords(){""",
    u"""/* P928: THE AUDIT THAT DOES NOT CONSULT THE ROSTER. _famLaneRecords and
   _famLaneGhosts both answer "what did somebody remember to enrol", which is
   the question that was wrong four times running - P520, P530, P531, P919, each
   finding the previous one's leftover. This walks the LIVE object graph for
   anything carrying a numeric lane, records which die it points at BY OBJECT
   IDENTITY, and checks after the reorder that it still points at the same one.
   A record nobody enrolled fails on its own, without being on a list.
   IT RUNS ON EVERY REORDER UNDER _fkDbgOn, not in a probe. A probe only ever
   sees the records that happened to exist in that run - one minted by a card
   pairing nobody triggered is invisible to it - so coverage has to accrue over
   play rather than over one invocation.
   THE IGNORE LIST FAILS SAFE. Rival-side records index the rival's board and a
   player reorder must not move them, so they would flag forever. Listing them
   as EXCLUSIONS means forgetting one produces noise, not silence - the opposite
   direction from an enrolment roster, which is the failure this exists to
   catch. It is empty until a path is actually observed and classified. */
var _LANE_AUDIT_IGNORE=[];
function _famLaneWalk(){
  var found=[],seen=(typeof Set!=='undefined')?new Set():null,seenArr=[];
  var pool=(typeof G!=='undefined'&&G&&G.pool)||[];
  function mark(o){ if(seen){ if(seen.has(o))return true; seen.add(o); return false; }
    if(seenArr.indexOf(o)>=0)return true; seenArr.push(o); return false; }
  function isDie(o){ for(var i=0;i<pool.length;i++)if(pool[i]===o)return true; return false; }
  (function walk(o,path,depth){
    if(!o||depth>4||typeof o!=='object')return;
    if(mark(o))return;
    if(typeof Node!=='undefined'&&o instanceof Node)return;
    if(Object.prototype.toString.call(o)==='[object Array]'){
      for(var i=0;i<o.length;i++)walk(o[i],path+'['+i+']',depth+1);return;}
    if(typeof o.lane==='number'&&isFinite(o.lane)&&!isDie(o)&&
       _LANE_AUDIT_IGNORE.indexOf(path)<0)found.push({path:path,obj:o});
    for(var k in o){
      if(k==='el'||k==='chip'||k==='phys')continue;
      var v;try{v=o[k];}catch(e){continue;}
      if(v&&typeof v==='object')walk(v,path+'.'+k,depth+1);}
  })(G,'G',0);
  return found;
}
function _famLaneDieAt(L){
  var pool=(typeof G!=='undefined'&&G&&G.pool)||[];
  for(var i=0;i<pool.length;i++)if(pool[i].lane===L&&!pool[i].committed)return pool[i];
  return null;
}
function _famLaneAuditBefore(){
  if(!window._fkDbgOn||typeof G==='undefined'||!G)return null;
  try{
    return _famLaneWalk().map(function(r){
      return {path:r.path,obj:r.obj,die:_famLaneDieAt(r.obj.lane)};});
  }catch(e){return null;}
}
function _famLaneAuditAfter(snap){
  if(!snap||!snap.length)return;
  try{
    var bad=snap.filter(function(x){
      return x.die&&_famLaneDieAt(x.obj.lane)!==x.die;});
    if(!bad.length)return;
    G._laneAuditViolations=(G._laneAuditViolations||0)+bad.length;
    G._laneAuditPaths=bad.map(function(x){return x.path;});
    if(window.console&&console.warn)console.warn(
      '[fark P928] a reorder moved the dice out from under '+bad.length+
      ' lane-stamped record(s): '+G._laneAuditPaths.join(', ')+
      '. Enrol them in _famLaneRecords, or add the path to _LANE_AUDIT_IGNORE '+
      'if it indexes the rival board.');
    try{famLog('DEV: '+bad.length+' LANE RECORD(S) LOST THEIR DIE');}catch(e){}
  }catch(e){}
}
function _famLaneRecords(){""",
    '1 the walk and the audit')

# ── 2. snapshot before the carry ────────────────────────────────────
sub(u"""          var _recs=(typeof _famLaneRecords==='function')?_famLaneRecords():[];""",
    u"""          /* P928: the roster-independent snapshot, dev only. It is taken
             here, before anything is written, and checked after the loop. */
          var _laneAudit=(typeof _famLaneAuditBefore==='function')?_famLaneAuditBefore():null;
          var _recs=(typeof _famLaneRecords==='function')?_famLaneRecords():[];""",
    '2 the audit snapshot')

# ── 3. and check after the whole carry has run ──────────────────────
sub(u"""            c.die.lane=L;
          });""",
    u"""            c.die.lane=L;
          });
          /* P928: every lane-stamped record must still point at its own die.
             Runs after the WHOLE loop - a check inside it would compare against
             a half-renumbered pool. */
          try{if(typeof _famLaneAuditAfter==='function')_famLaneAuditAfter(_laneAudit);}catch(e){}""",
    '3 the audit check')

# ── 4. P927 stops whispering ────────────────────────────────────────
sub(u"""  try{
    if(G&&G._ndAtTurnTop!==undefined&&G.numDice!==G._ndAtTurnTop){
      G._ndDiscarded=(G._ndDiscarded||0)+1;
      G._ndDiscardedVal=G.numDice;
      if(window.console&&console.warn)console.warn(
        '[fark P927] numDice was set to '+G.numDice+' above the turn rebuild '+
        '(was '+G._ndAtTurnTop+' on entry) and is being discarded. A dice-count '+
        'effect belongs BELOW the rebuild, beside Whisper\\'s Hex - see P923.');
    }
  }catch(e){}
  G.numDice=G.matchDice?G.matchDice.length:6;""",
    u"""  var _ndLost=null;
  try{
    if(G&&G._ndAtTurnTop!==undefined&&G.numDice!==G._ndAtTurnTop){
      _ndLost=G.numDice;
      G._ndDiscarded=(G._ndDiscarded||0)+1;
      G._ndDiscardedVal=_ndLost;
      if(window.console&&console.warn)console.warn(
        '[fark P927] numDice was set to '+_ndLost+' above the turn rebuild '+
        '(was '+G._ndAtTurnTop+' on entry) and is being discarded. A dice-count '+
        'effect belongs BELOW the rebuild, beside Whisper\\'s Hex - see P923.');
      try{famLog('DEV: A DICE-COUNT EFFECT WAS DISCARDED');}catch(e){}
    }
  }catch(e){}
  G.numDice=G.matchDice?G.matchDice.length:6;
  /* P928: AND IT THROWS IN DEV. A console line in a game is easy to miss, and
     this comment has failed three times precisely because the warning was
     passive. The throw is OUTSIDE the try above on purpose - inside it, the
     catch swallowed it and the loud version would have been a silent no-op. */
  if(_ndLost!==null&&window._fkDbgOn)
    throw new Error('[fark P927] a dice-count effect set numDice='+_ndLost+
      ' above the turn rebuild and it was discarded. Move the block BELOW the '+
      'rebuild, beside Whisper\\'s Hex - see P923 / Tar Pit / Preserve.');""",
    '4 the guard throws in dev')

# ── post-asserts ────────────────────────────────────────────────────
code = re.sub(r'/\*[\s\S]*?\*/', '', s)

for need in ('function _famLaneWalk(', 'function _famLaneAuditBefore(',
             'function _famLaneAuditAfter(', 'var _LANE_AUDIT_IGNORE='):
    if code.count(need) != 1:
        sys.exit('%s is not defined exactly once (nothing written)' % need)
# the audit is gated on the dev flag, not on nothing
if 'if(!window._fkDbgOn' not in code[code.index('function _famLaneAuditBefore('):
                                     code.index('function _famLaneAuditBefore(') + 260]:
    sys.exit('the audit is not gated on the dev flag (nothing written)')
# snapshot before the carry, check after it
_loop = code.index('_carry.forEach(function(c,i){')
_snap = code.rindex('_famLaneAuditBefore()', 0, _loop)
_after = code.index('_famLaneAuditAfter(_laneAudit)', _loop)
if not (_snap < _loop < _after):
    sys.exit('the audit does not bracket the carry loop (nothing written)')
# and the check is OUTSIDE the forEach, after c.die.lane=L
if _after < code.index('c.die.lane=L;', _loop):
    sys.exit('the audit check runs inside the carry loop (nothing written)')
# THE THROW IS OUTSIDE THE TRY THAT DETECTS IT - the whole point of the change
_guardTry = code.index('var _ndLost=null;')
_catch = code.index('}catch(e){}', _guardTry)
_throw = code.index("throw new Error('[fark P927]", _guardTry)
if _throw < _catch:
    sys.exit('the throw sits inside the try that would swallow it (nothing written)')
if code.count("window._fkDbgOn)\n    throw new Error('[fark P927]") != 1 and \
   'if(_ndLost!==null&&window._fkDbgOn)' not in code:
    sys.exit('the throw is not gated on the dev flag (nothing written)')
# the rebuild still happens, before the throw
if code.index('G.numDice=G.matchDice?G.matchDice.length:6', _guardTry) > _throw:
    sys.exit('the throw pre-empts the rebuild (nothing written)')
# and the existing rosters are untouched
for need in ('function _famLaneRecords(', 'function _famLaneGhosts('):
    if code.count(need) != 1:
        sys.exit('%s was disturbed (nothing written)' % need)

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d edits (%s)' % (len(edits), ', '.join(edits)))
