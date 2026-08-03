# -*- coding: utf-8 -*-
"""P435 - the preserved die becomes visible.

P434 fixed the data: the die arrives in G.kept, keeps its material, carries its
points, costs a die. And the player could not see any of it - #keptRow was
display:flex, 0x0, no children, before and after the first roll. A turn that
starts with 100 points and five dice and nothing on the table to explain why.

THE SEAM, and it is why this is small rather than a dice-layer rewrite. D3X
does not need to be told about a new die: it ADOPTS chips. Its sync walks the
host for elements carrying data-mat/data-val and mints the THREE object itself.
And `mkDie(val, mat, sizeClass, still, ench)` is the one factory both the 3D and
2D paths already go through. So minting a preserved die is: build the chip the
normal path builds, wrap it the way the normal path wraps it, put it in
#keptRow. No new rendering code, and the 2D fallback comes free because mkDie
covers it.

`still:true` because a preserved die is at rest in its casing - it must not
tumble in like a fresh throw.
"""
import io, os

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   'fark_proto.html')
with io.open(SRC, encoding='utf-8') as f:
    s = f.read()
orig = s

OLD = u"""    G.numDice=Math.max(1,(G.matchDice?G.matchDice.length:6)-1);
    famLog('THE AMBER CRACKS — A '+_fp.val+' ALREADY KEPT'+(_fp.crack?' (+'+_fp.crack+')':''));
    try{refreshKeptTray();updHUD();}catch(e){}
"""
NEW = u"""    G.numDice=Math.max(1,(G.matchDice?G.matchDice.length:6)-1);
    /* AND PUT IT ON THE TABLE. The data above is invisible on its own: the
       player would start the turn a die short with points already banked and
       nothing to explain either. mkDie is the same factory the normal roll uses
       - it covers the 2D fallback too - and D3X needs no telling, because its
       sync ADOPTS any chip in the host carrying data-mat/data-val. still=true
       because a preserved die is at rest in its casing, not mid-throw. */
    try{
      var _kr=document.getElementById('keptRow');
      if(_kr&&typeof mkDie==='function'){
        var _pd=mkDie(_fp.val,_fp.mat||'bone',null,true,null);
        _pd.classList.add('in-tray');
        _kr.appendChild(typeof _wrapDie==='function'?_wrapDie(_pd):_pd);
      }
    }catch(e){}
    famLog('THE AMBER CRACKS — A '+_fp.val+' ALREADY KEPT'+(_fp.crack?' (+'+_fp.crack+')':''));
    try{refreshKeptTray();updHUD();}catch(e){}
"""
n = s.count(OLD)
assert n == 1, 'preserve restore anchor matched %d (want 1)' % n
s = s.replace(OLD, NEW)

assert s != orig, 'nothing changed'
assert u"mkDie(_fp.val" in s
with io.open(SRC, 'w', encoding='utf-8', newline='') as f:
    f.write(s)
print('P435 applied: the preserved die is minted into #keptRow')
