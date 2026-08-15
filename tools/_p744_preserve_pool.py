# -*- coding: utf-8 -*-
"""P744: the preserved die comes back as a REAL DIE in its own lane.

Denis: 'it becomes small and grey at the bottom, when I roll it scales
slightly but stays grey, doesn't move back to its lane or full colour,
I can't select it, and its lane must not be used by another die.'

ROOT: the payout minted a DECORATION. mkDie into #keptRow with class
`in-tray` IS the small dim tray styling - and under the 3D layer that
tray is retired entirely (refreshKeptTray returns early; kept dice live
on the throw line), so the thing had no lane, no pool entry and no click
handler. Nothing about it could ever be right; P734 animated a
decoration.

Now the payout only REMEMBERS (G._pvDie), and the deal - the one place
that builds dice for the throw line - creates it exactly like every
other die: same mkDie, same row, same pool entry, at its own lane, with
committed:true because it is already scored. It is full size, in
colour, on the throw line, and its lane cannot be taken because a die
genuinely occupies it (the lane reservation P691 built already reads
_pvLane). The amber shell rides the real die through the same
D3X.amberShell the cast uses, and cracks off when the throw settles.
"""
import io, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'fark_proto.html')
s = io.open(P, encoding='utf-8', newline='').read()
n = 0


def sub(old, new, label):
    global s, n
    c = s.count(old)
    if c != 1:
        old2 = old.replace('\n', '\r\n')
        if s.count(old2) == 1:
            old, new = old2, new.replace('\n', '\r\n')
        else:
            sys.exit('ANCHOR x%d for %s' % (c, label))
    s = s.replace(old, new)
    n += 1
    print('  ok  ' + label)


# 1) the payout remembers instead of minting a decoration
sub(u"""    try{
      var _kr=document.getElementById('keptRow');
      if(_kr&&typeof mkDie==='function'){""",
    u"""    /* P744: REMEMBER, do not decorate. The deal builds the real die at
       this lane on the throw line - see _pvDie there. The old mint into
       #keptRow made a chip on a surface the 3D layer retired: no lane,
       no pool entry, no click handler, small and grey by class. */
    G._pvDie={val:_fp.val,mat:_fp.mat||'bone',ench:_fp.ench||null,
      lane:(typeof _fp.lane==='number')?_fp.lane:null,crack:_fp.crack||0};
    try{
      var _kr=(!document.documentElement.classList.contains('fk3d'))
        ?document.getElementById('keptRow'):null;/* 2D fallback only */
      if(_kr&&typeof mkDie==='function'){""",
    'payout remembers')

# 2) the deal builds it for real
sub(u"""  G.pool=[...G.pool,...newEntries];""",
    u"""  /* P744: THE PRESERVED DIE, BUILT LIKE EVERY OTHER DIE. Its lane was
     already held free (P691's _occLane reservation), so it drops into
     its own seat on the throw line: same factory, same row, same pool
     entry - full size, in colour, and selectable by the same rules as
     the rest, except that it arrives already committed because it was
     scored last turn. The amber comes off when this throw settles. */
  try{
    var _pv=G._pvDie;
    if(_pv&&typeof _pv.lane==='number'
      &&!G.pool.some(function(d){return d.lane===_pv.lane;})
      &&!newEntries.some(function(d){return d.lane===_pv.lane;})){
      var _pel=mkDie(_pv.val,_pv.mat,null,true,_pv.ench);
      _pel.classList.add('committed');
      _pel.style.visibility='visible';_pel.style.opacity='1';
      _appendDie(row,_pel);
      newEntries.push({val:_pv.val,mat:_pv.mat,ench:_pv.ench,sel:false,
        committed:true,el:_pel,lane:_pv.lane,_preserved:true});
      /* the amber holds until this throw is done, then cracks */
      (function _shell(t){
        var dd=window.D3X&&D3X._dieOfChip&&D3X._dieOfChip(_pel);
        if(dd&&D3X.amberShell){
          D3X.amberShell(dd,true);
          window._fkAmberChip=_pel;window._fkAmberWrap=null;
          try{_amberReturnWhenSettled();}catch(e){}
          return;
        }
        if((t||0)<40)setTimeout(function(){_shell((t||0)+1);},60);
      })(0);
      G._pvDie=null;
    }
  }catch(e){}
  G.pool=[...G.pool,...newEntries];""",
    'deal builds the preserved die')

# 3) the return no longer moves a tray chip - it just cracks the amber
sub(u"""    /* it comes home: rise, pop, crack */
    try{
      if(wrap){wrap.style.transition='translate .45s cubic-bezier(.3,1.35,.4,1),scale .45s cubic-bezier(.3,1.35,.4,1)';
        wrap.style.translate='0 0';wrap.style.scale='1';}
    }catch(e){}""",
    u"""    /* P744: the die is a REAL die in its lane now - there is nothing to
       move back. The wrap branch stays for the 2D fallback's tray chip. */
    try{
      if(wrap){wrap.style.transition='translate .45s cubic-bezier(.3,1.35,.4,1),scale .45s cubic-bezier(.3,1.35,.4,1)';
        wrap.style.translate='0 0';wrap.style.scale='1';}
    }catch(e){}""",
    'return note')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d edits' % n)
