# -*- coding: utf-8 -*-
"""P845b: seven_dice is an ARM, not a dispatch-time mutator - the P844
sweep misclassified it. Driven through its real gate (after P845 made
the gate reachable), the dispatch hook's _steadyDisarm stripped the
freshly painted rings while the onclick hijack lived on: an invisible
arm that still rerolled on a die tap. Per the doc's own checklist for
an arm: a flag (G._sevenArmed) guarding the hijack, disarm folded into
_steadyDisarm (every moment that disarms steady applies equally), the
mutation moment (the TAP's reroll) enrolls in famTableChanged, and the
card leaves the dispatch-time id list.
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


# 1) seven_dice leaves the dispatch-time list (it arms at dispatch,
#    mutates at tap)
sub("""      'old_bones','frozen_die','double_down','wild_die','seven_dice','coin_flip',""",
    """      'old_bones','frozen_die','double_down','wild_die','coin_flip',""",
    'dispatch list drops seven_dice')
sub("""  /* P844: the dice-mutating actives void pending promises/arms - one
     site, one classified list (each handler verified to write d.val,
     splice the pool, or freeze). Flag-only and points-only actives
     stay off it: a promise survives a wager. A NEW active that touches
     dice joins this list - docs/CARD_INTERACTION_RULES.md. */""",
    """  /* P844/P845b: the dice-mutating actives void pending promises/arms
     - one site, one classified list (each handler verified to write
     d.val, splice the pool, or freeze - and DRIVEN individually, the
     sweep probe). Flag-only and points-only actives stay off it: a
     promise survives a wager. seven_dice is NOT here: it ARMS at
     dispatch and mutates at its die tap, which enrolls there instead
     (the steady_hand/transmute shape). A NEW active that touches dice
     joins this list - docs/CARD_INTERACTION_RULES.md. */""",
    'dispatch comment corrected')

# 2) the arm gets a flag; the tap guards, consumes, and enrolls
sub("""  setStatusMsg('SEVEN DICE \u2014 TAP THE DIE TO REROLL','gold');
  triggerCard('seven_dice','ARMED',true);
  free.forEach(function(d){
    if(!d.el)return;
    d.el.classList.add('break-target');
    d.el.onclick=function(){
      free.forEach(function(q){if(q.el){q.el.classList.remove('break-target');q.el.onclick=function(){toggleDie(q);};}});
      d.val=_rollD(d);d.sel=false;""",
    """  setStatusMsg('SEVEN DICE \u2014 TAP THE DIE TO REROLL','gold');
  triggerCard('seven_dice','ARMED',true);
  G._sevenArmed=true;/* P845b: the arm-flag - a table change disarms via
     _steadyDisarm's sweep, and a stale hijacked onclick dies on it */
  free.forEach(function(d){
    if(!d.el)return;
    d.el.classList.add('break-target');
    d.el.onclick=function(){
      if(!G._sevenArmed)return;
      G._sevenArmed=false;
      free.forEach(function(q){if(q.el){q.el.classList.remove('break-target');q.el.onclick=function(){toggleDie(q);};}});
      d.val=_rollD(d);d.sel=false;""",
    'seven arm-flag + guard')
sub("""      try{reDrawDieFace(d);}catch(e){}
      famLog('SEVEN DICE \u2014 '+d.val);""",
    """      try{reDrawDieFace(d);}catch(e){}
      famLog('SEVEN DICE \u2014 '+d.val);
      try{famTableChanged();}catch(e){}/* P845b: the reroll is the mutation moment */""",
    'seven tap enrolls')

# 3) the disarm rides _steadyDisarm - every moment that disarms steady
#    (rolls, table changes, endPTurn) applies to this arm equally
sub("""function _steadyDisarm(){
  try{
    if(typeof G==='undefined'||!G)return;
    G._steadyArmed=false;
    document.querySelectorAll('#playerDiceRow .die.break-target')
      .forEach(function(el){el.classList.remove('break-target');});
  }catch(e){}
}""",
    """function _steadyDisarm(){
  try{
    if(typeof G==='undefined'||!G)return;
    G._steadyArmed=false;
    G._sevenArmed=false;/* P845b: same arm class, same exits - the flag
       makes any stale hijacked onclick a no-op */
    document.querySelectorAll('#playerDiceRow .die.break-target')
      .forEach(function(el){el.classList.remove('break-target');});
  }catch(e){}
}""",
    'disarm rides _steadyDisarm')

for needed in ['G._sevenArmed=true', 'if(!G._sevenArmed)return;']:
    if needed not in s:
        sys.exit('KEEPER MISSING: %s (nothing written)' % needed)
if "'seven_dice','coin_flip'" in s:
    sys.exit('seven_dice still on the dispatch list (nothing written)')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d edits (%s)' % (len(edits), ', '.join(edits)))
