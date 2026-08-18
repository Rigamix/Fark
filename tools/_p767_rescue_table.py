# -*- coding: utf-8 -*-
"""P767: legacy cluster 1a - the dead-roll rescue ladder becomes a table.

Eight cards (old_bones, ambrose_grace, wild_die, brutus_fist,
finnicks_palm, grogs_flask, coin_flip, the_nudge) were an if/else ladder
of near-identical blocks: mutate some blanks, label, then one shared
tail (charge, announce, rescore, persona re-pick). The table keeps each
card as DATA - a fix(blanks) that mutates and returns its label - and
ONE consumer walks it in the same priority order.

SEMANTICS PRESERVED EXACTLY, including the ladder's quirk: a card whose
CONDITION fails (grogs_flask under two blanks) passes to the next; a
card whose BODY was entered but found nothing useful (coin_flip with no
6 or 2 showing) STOPPED the chain - later rescues never ran. The table
reproduces that with a break, and flags it for a ruling rather than
silently 'improving' it - a refactor is not the place to change
behaviour.

npcCardState is untouched (it is saved - the resume boundary the map
drew). npcUseActive/triggerCard/rescore stay the shared tail they were.
"""
import io, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'fark_proto.html')
s = io.open(P, encoding='utf-8', newline='').read()
edits = []


def sub(old, new, label):
    global s
    c = s.count(old)
    if c != 1:
        o2 = old.replace('\n', '\r\n')
        if s.count(o2) == 1:
            old, new = o2, new.replace('\n', '\r\n')
        else:
            sys.exit('ANCHOR x%d for %s (nothing written)' % (c, label))
    s = s.replace(old, new)
    edits.append(label)


# ── 1. the table, defined beside the other npc-card helpers ──
sub("""function npcHasActive(cid){""",
    """/* P767: THE DEAD-ROLL RESCUE TABLE (legacy cluster 1a). Each entry is
   one card's answer to 'can you turn this dead roll into a scoring
   one?' - fix(blanks) mutates its dice and returns the announce label,
   or null when it found nothing useful. Priority is array order,
   biggest swing first - exactly the old ladder's order.
   QUIRK PRESERVED, FLAGGED FOR A RULING: in the old else-if ladder a
   card whose body ran but found nothing (coin_flip with no 6/2 showing)
   STOPPED the chain - later rescues never got tried. The consumer's
   break reproduces that. Whether fall-through would be better is a
   behaviour question, not a refactor's call. */
function _npcRescueSet(d,v){
  d.val=v;
  try{reDrawDieFace(d);}catch(e){}
  try{if(d.el)spawnPixelSparks(d.el,3);}catch(e){}
}
var NPC_RESCUES=[
  {id:'old_bones',fix:function(bl){
    bl.forEach(function(d){_npcRescueSet(d,1);});
    return 'OLD BONES — BLANKS → 1s';}},
  {id:'ambrose_grace',fix:function(bl){
    bl.slice(0,2).forEach(function(d){_npcRescueSet(d,5);});
    return 'AMBROSE GRACE — BLANKS → 5s';}},
  {id:'wild_die',fix:function(bl){
    _npcRescueSet(bl[0],1);return 'WILD DIE → 1';}},
  {id:'brutus_fist',fix:function(bl){
    _npcRescueSet(bl[0],1);return "BRUTUS'S FIST → 1";}},
  {id:'finnicks_palm',fix:function(bl){
    _npcRescueSet(bl[0],Math.random()<0.5?1:5);return "FINNICK'S PALM → 1/5";}},
  {id:'grogs_flask',need:function(bl){return bl.length>=2;},fix:function(bl){
    bl.slice(0,2).forEach(function(d){_npcRescueSet(d,rollFaceExclude(d.mat,d.val));});
    return "GROG'S FLASK — REROLLED";}},
  {id:'coin_flip',fix:function(bl){
    /* 6→1 (+100) first, then 2→5 (+50); anything else is a wasted charge */
    var M={1:6,2:5,3:4,4:3,5:2,6:1},p=null;
    bl.some(function(d){if(d.val===6){p=d;return true;}return false;});
    if(!p)bl.some(function(d){if(d.val===2){p=d;return true;}return false;});
    if(!p)return null;
    _npcRescueSet(p,M[p.val]);return 'COIN FLIP → '+p.val;}},
  {id:'the_nudge',fix:function(bl){
    /* +1 with 6→1 wrap: a 6 (+100) first, then a 4 (+50) */
    var p=null;
    bl.some(function(d){if(d.val===6){p=d;return true;}return false;});
    if(!p)bl.some(function(d){if(d.val===4){p=d;return true;}return false;});
    if(!p)return null;
    _npcRescueSet(p,p.val>=6?1:p.val+1);return 'THE NUDGE → '+p.val;}}
];
function npcHasActive(cid){""",
    'the rescue table')

# ── 2. the ladder becomes one consumer ──
sub("""          var _rescued=false;var _rescueCid=null;var _rescueLabel='';
          /* old_bones: all blanks → 1s (biggest swing) */
          if(!_rescued&&npcHasActive('old_bones')){
            _npcBlanks.forEach(function(d){d.val=1;reDrawDieFace(d);if(d.el)spawnPixelSparks(d.el,3);});
            _rescueCid='old_bones';_rescueLabel='OLD BONES — BLANKS → 1s';_rescued=true;
          }
          /* ambrose_grace: up to 2 blanks → 5s */
          else if(!_rescued&&npcHasActive('ambrose_grace')){
            _npcBlanks.slice(0,2).forEach(function(d){d.val=5;reDrawDieFace(d);if(d.el)spawnPixelSparks(d.el,3);});
            _rescueCid='ambrose_grace';_rescueLabel='AMBROSE GRACE — BLANKS → 5s';_rescued=true;
          }
          /* wild_die: pick best face (1) for one blank */
          else if(!_rescued&&npcHasActive('wild_die')){
            _npcBlanks[0].val=1;reDrawDieFace(_npcBlanks[0]);if(_npcBlanks[0].el)spawnPixelSparks(_npcBlanks[0].el,3);
            _rescueCid='wild_die';_rescueLabel='WILD DIE → 1';_rescued=true;
          }
          /* brutus_fist: force one blank to 1 */
          else if(!_rescued&&npcHasActive('brutus_fist')){
            _npcBlanks[0].val=1;reDrawDieFace(_npcBlanks[0]);if(_npcBlanks[0].el)spawnPixelSparks(_npcBlanks[0].el,3);
            _rescueCid='brutus_fist';_rescueLabel="BRUTUS'S FIST → 1";_rescued=true;
          }
          /* finnicks_palm: flip one blank to 1 or 5 */
          else if(!_rescued&&npcHasActive('finnicks_palm')){
            _npcBlanks[0].val=Math.random()<0.5?1:5;reDrawDieFace(_npcBlanks[0]);if(_npcBlanks[0].el)spawnPixelSparks(_npcBlanks[0].el,3);
            _rescueCid='finnicks_palm';_rescueLabel="FINNICK'S PALM → 1/5";_rescued=true;
          }
          /* grogs_flask: reroll up to 2 blanks */
          else if(!_rescued&&npcHasActive('grogs_flask')&&_npcBlanks.length>=2){
            _npcBlanks.slice(0,2).forEach(function(d){d.val=rollFaceExclude(d.mat,d.val);reDrawDieFace(d);if(d.el)spawnPixelSparks(d.el,3);});
            _rescueCid='grogs_flask';_rescueLabel="GROG'S FLASK — REROLLED";_rescued=true;
          }
          /* coin_flip (tin): flip ONE blank to its opposite face. Useful
             rescues: 6→1 (best, +100) or 2→5 (+50). Skip if no blank
             flips into a 1 or 5 — the card has only one charge so we
             don't waste it on a flip that still doesn't score. */
          else if(!_rescued&&npcHasActive('coin_flip')){
            var _cfMap={1:6,2:5,3:4,4:3,5:2,6:1};
            var _cfPick=null;
            /* Prefer a blank whose opposite is a 1 (val 6), then a 5 (val 2). */
            for(var _cfi=0;_cfi<_npcBlanks.length;_cfi++){if(_npcBlanks[_cfi].val===6){_cfPick=_npcBlanks[_cfi];break;}}
            if(!_cfPick){for(var _cfj=0;_cfj<_npcBlanks.length;_cfj++){if(_npcBlanks[_cfj].val===2){_cfPick=_npcBlanks[_cfj];break;}}}
            if(_cfPick){
              _cfPick.val=_cfMap[_cfPick.val];reDrawDieFace(_cfPick);if(_cfPick.el)spawnPixelSparks(_cfPick.el,3);
              _rescueCid='coin_flip';_rescueLabel='COIN FLIP → '+_cfPick.val;_rescued=true;
            }
          }
          /* the_nudge (tin): bump a blank by +1 (wraps 6→1). Useful
             rescues: 4→5 (+50) or 6→1 (+100). Two charges per match,
             but the rescue only consumes one charge here — same as
             coin_flip's single-die mutation. */
          else if(!_rescued&&npcHasActive('the_nudge')){
            var _tnPick=null;
            /* Prefer a 6 (wraps to 1, +100) then a 4 (bumps to 5, +50). */
            for(var _tni=0;_tni<_npcBlanks.length;_tni++){if(_npcBlanks[_tni].val===6){_tnPick=_npcBlanks[_tni];break;}}
            if(!_tnPick){for(var _tnj=0;_tnj<_npcBlanks.length;_tnj++){if(_npcBlanks[_tnj].val===4){_tnPick=_npcBlanks[_tnj];break;}}}
            if(_tnPick){
              _tnPick.val=_tnPick.val>=6?1:_tnPick.val+1;reDrawDieFace(_tnPick);if(_tnPick.el)spawnPixelSparks(_tnPick.el,3);
              _rescueCid='the_nudge';_rescueLabel='THE NUDGE → '+_tnPick.val;_rescued=true;
            }
          }""",
    """          /* P767: the ladder is a TABLE now (NPC_RESCUES, beside the
             other npc helpers) - one consumer, same priority order,
             same quirk (an entered-but-useless card breaks the chain;
             see the table's comment). */
          var _rescued=false;var _rescueCid=null;var _rescueLabel='';
          for(var _ri=0;_ri<NPC_RESCUES.length;_ri++){
            var _R=NPC_RESCUES[_ri];
            if(!npcHasActive(_R.id))continue;
            if(_R.need&&!_R.need(_npcBlanks))continue;
            var _rl=_R.fix(_npcBlanks);
            if(_rl){_rescueCid=_R.id;_rescueLabel=_rl;_rescued=true;}
            break;/* entered = decided, hit or miss - the ladder's rule */
          }""",
    'one consumer')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d (%s)' % (len(edits), ', '.join(edits)))
