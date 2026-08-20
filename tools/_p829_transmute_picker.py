# -*- coding: utf-8 -*-
"""P829: transmute gets an in-world picker - window.prompt retires.

Census: the prompt() pair was placeholder UI (and unusable on a
phone). The replacement is the steady_hand shape verbatim: use() only
paints the free dice as tap targets and returns FALSE (famUse leaves
the charge), the die tap opens the face picker in the house modal
(_gbModalOpen, the spoils-confirm chrome), and the PICK spends the
charge. 'Leave it' walks away free; a roll voids the arm
(_clearRollForces, the roll-scope lifecycle point).
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


sub("""CFX.transmute={
  canUse:function(){return G&&G.phase==='choosing';},
  use:function(inst){
    var free=G.pool.filter(function(d){return !d.committed;});
    if(!free.length)return false;
    var pick=parseInt(prompt('Which die? 1..'+free.length+' (left to right, uncommitted)'),10);
    if(!(pick>=1&&pick<=free.length))return false;
    var face=parseInt(prompt('New face? 1-6'),10);
    if(!(face>=1&&face<=6))return false;
    var d=free[pick-1];d.val=face;try{reDrawDieFace(d);}catch(e){}
    famLog('TRANSMUTED TO '+face);
    try{refreshSelUI();}catch(e){}
    return true;
  }
};""",
    """CFX.transmute={
  canUse:function(){return G&&G.phase==='choosing';},
  /* P829: the prompt() picker was placeholder UI. Steady_hand's shape:
     use() paints the targets and returns FALSE (the charge stays), the
     die tap opens the face picker, the PICK bills. An arm the player
     walks away from costs nothing; a roll voids it (_clearRollForces). */
  use:function(inst){
    var free=G.pool.filter(function(d){return !d.committed&&!d._frozen;});
    if(!free.length)return false;
    G._transArmed=true;
    try{setStatusMsg('TRANSMUTE — TAP THE DIE TO CHANGE','gold');}catch(e){}
    free.forEach(function(d){
      if(!d.el)return;
      d.el.classList.add('break-target');
      d.el.onclick=function(){
        if(!G._transArmed)return;
        G._transArmed=false;
        free.forEach(function(q){if(q.el){q.el.classList.remove('break-target');q.el.onclick=function(){toggleDie(q);};}});
        if(inst.charges<=0)return;
        window._transDie=d;window._transInst=inst;
        var _bt='';
        for(var f=1;f<=6;f++)_bt+='<div class="gbx-btn primary" style="height:44px;font-size:19px" data-f="'+f+'" onclick="_gbModalClose();_transPick(this.dataset.f)">'+f+'</div>';
        _gbModalOpen('<b>Transmute to?</b>'
          +'<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px">'+_bt+'</div>'
          +'<div class="gbx-btn" style="height:40px" onclick="_gbModalClose()">leave it</div>');
      };
    });
    return false;
  }
};
function _transPick(f){
  var d=window._transDie,inst=window._transInst;
  window._transDie=null;window._transInst=null;
  f=parseInt(f,10);
  if(!d||!inst||!(f>=1&&f<=6)||inst.charges<=0)return;
  inst.charges--;
  d.val=f;d.sel=false;
  if(d.el)d.el.classList.remove('selected');
  try{reDrawDieFace(d);}catch(e){}
  try{_fxSpray(d.el,'#46c46e',12,{speed:70,g:-10,size:6,spread:2.0});}catch(e){}
  famLog('TRANSMUTED TO '+f);
  try{refreshSelUI();}catch(e){}try{famRenderRow();}catch(e){}
}""",
    'the in-world picker')

# a roll voids a stranded arm
sub("""function _clearRollForces(){
  if(!G)return;
  G._famPeekVals=null;G._famHoneyVal=null;""",
    """function _clearRollForces(){
  if(!G)return;
  G._famPeekVals=null;G._famHoneyVal=null;
  G._transArmed=false;/* P829: a roll voids a stranded transmute arm */""",
    'roll voids the arm')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d (%s)' % (len(edits), ', '.join(edits)))
