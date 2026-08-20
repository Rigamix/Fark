# -*- coding: utf-8 -*-
"""P825: passive live-states on the cards + standing aux chips.

Census items: reprisal's card should read LIVE while the trailing gate
is open (spec: glow when active, dim when not); the player's ill_omen
declaration had no marker while the rival's does (asymmetric); and
slow_cook / for_keeps carry standing stakes nothing on screen showed.

- reprisal + ill_omen borrow the ARMED state (lift + warmth - the same
  presentation double_or_nothing's arm already wears on the player row).
- slow_cook gets a simmer chip in #famAux (the quicksilver chip's
  wholesale-rebuild idiom) showing the riding accumulator, re-rendered
  at each accrual.
- for_keeps gets a standing stakes chip.
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


# 1) live-states read as armed
sub("""    var spent=d.kind==='active'&&inst.charges<=0;
    var cls=(spent?' spent':'')+(inst.state.armed?' armed':'');""",
    """    var spent=d.kind==='active'&&inst.charges<=0;
    /* P825: PASSIVE LIVE-STATES read as armed - the same lift+warmth the
       arm state already wears on this row. reprisal while the trailing
       gate is open; ill_omen while the declaration is out (the rival's
       declaration already marks THEIR card - this closes the asymmetry). */
    var _live=(inst.id==='reprisal'&&G&&((G.oPts||0)-(G.pPts||0))>=1000)
      ||(inst.id==='ill_omen'&&G&&!!G._famIllOmen);
    var cls=(spent?' spent':'')+((inst.state.armed||_live)?' armed':'');""",
    'reprisal + ill_omen live-states')

# 2) the standing chips, before the wholesale innerHTML
sub("""  hostA.innerHTML=ha;
}""",
    """  /* P825: STANDING CHIPS - stakes riding right now that the card art
     cannot say. Same wholesale-rebuild idiom as the quicksilver chip. */
  try{
    (G&&G.pF||[]).forEach(function(inst){
      if(inst.id==='slow_cook'&&inst.state&&inst.state.acc>0)
        ha+='<div style="padding:2px 7px;background:#181008;color:#e8a23c;border:1px dashed #a66">SLOW COOK — +'+inst.state.acc+' SIMMERING</div>';
    });
    if(G&&G._forKeeps)
      ha+='<div style="padding:2px 7px;background:#141014;color:#c8a45c;border:1px dashed #875">FOR KEEPS — A DIE RIDES ON THIS MATCH</div>';
  }catch(e){}
  hostA.innerHTML=ha;
}""",
    'simmer + for-keeps chips')

# 3) the simmer chip re-renders at each accrual
sub("""    if(rc>=3){ev.me.state.acc=(ev.me.state.acc||0)+ev.P;""",
    """    if(rc>=3){ev.me.state.acc=(ev.me.state.acc||0)+ev.P;
      try{famRenderRow();}catch(e){}/* P825: the simmer chip tracks live */""",
    'accrual re-renders the chip')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d (%s)' % (len(edits), ', '.join(edits)))
