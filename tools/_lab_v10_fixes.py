# -*- coding: utf-8 -*-
"""Lab v10: two live bugs from Denis.

1. QUOTING CLASS: gallery/catalogue inline handlers were built with
   JSON.stringify inside double-quoted attributes - onclick="openStudio(
   "preserve")" is dead HTML. Clicking a card did nothing, and typing a
   catalogue note never saved. The probes never saw it because they
   called openStudio()/saveNote() directly - the untested route was the
   CLICK. All string args now use &quot; entities.

2. DRESSER REBUILD: _dress explains 'bones stay bones' - tint materials
   have their pip sheet baked AT CREATION for their original mat; a live
   mat change with no loaded skin falls back to the old baseMap forever.
   applyMat now goes through the creation path: retag the chip, DROP the
   3D die, remove its record - the next sync re-adopts the chip and
   builds materials for the new material properly. Run/lane writes now
   resolve the die's REAL lane from the pool instead of assuming the
   registration index."""
import io, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'fark_lab.html')
s = io.open(P, encoding='utf-8', newline='').read()
n = 0


def sub(old, new, label):
    global s, n
    c = s.count(old)
    if c != 1:
        sys.exit('ANCHOR x%d for %s' % (c, label))
    s = s.replace(old, new)
    n += 1
    print('  ok  ' + label)


# ── 1a. gallery clicks ──
sub(u"""    h+='<div class="gcard" onclick="openStudio('+JSON.stringify(id)+')">'""",
    u"""    h+='<div class="gcard" onclick="openStudio(&quot;'+id+'&quot;)">'""",
    'gallery card click')
sub(u"""    h+='<div class="gcard" onclick="openStudio('+JSON.stringify('mat:'+m)+')">'""",
    u"""    h+='<div class="gcard" onclick="openStudio(&quot;mat:'+m+'&quot;)">'""",
    'gallery mat click')
sub(u"""    h+='<div class="gcard" onclick="openStudio('+JSON.stringify('ench:'+e2)+')">'""",
    u"""    h+='<div class="gcard" onclick="openStudio(&quot;ench:'+e2+'&quot;)">'""",
    'gallery ench click')

# ── 1b. catalogue note typing (cards block + the _cat helper) ──
sub(u"""      +'<textarea placeholder="what must HAPPEN, step by step — timings, where the die goes, what the player must understand. Claude implements from THIS." '
      +'onchange="saveNote('+JSON.stringify(id)+',this.value)">'+(ns[id]||'')+'</textarea>'""",
    u"""      +'<textarea placeholder="what must HAPPEN, step by step — timings, where the die goes, what the player must understand. Claude implements from THIS." '
      +'onchange="saveNote(&quot;'+id+'&quot;,this.value)">'+(ns[id]||'')+'</textarea>'""",
    'card note onchange')
sub(u"""      +'<textarea placeholder="what must HAPPEN, step by step. Claude implements from THIS." '
      +'onchange="saveNote('+JSON.stringify(idp)+',this.value)">'+(ns[idp]||'')+'</textarea>'""",
    u"""      +'<textarea placeholder="what must HAPPEN, step by step. Claude implements from THIS." '
      +'onchange="saveNote(&quot;'+idp+'&quot;,this.value)">'+(ns[idp]||'')+'</textarea>'""",
    'mat/ench note onchange')

# ── 2. the dresser goes through the creation path ──
sub(u"""function applyMat(){
  var i=_dressSlot();if(i<0)return;
  var m=document.getElementById('dressMat').value;
  E('S.run.dice['+i+']='+JSON.stringify(m));
  E('G&&G.matchDice&&(G.matchDice['+i+']='+JSON.stringify(m)+')');
  var dx=E('window.D3X');var ds=dx.dice.filter(function(d){return d.match&&d.chip;});
  if(ds[i]){ds[i].mat=m;try{ds[i].chip._trueMat=m;}catch(e){}}
  E('D3X._reskin&&D3X._reskin()');
  log('die '+i+' is now '+m);
}""",
    u"""function applyMat(){
  var i=_dressSlot();if(i<0)return;
  var m=document.getElementById('dressMat').value;
  var dx=E('window.D3X');var ds=dx.dice.filter(function(d){return d.match&&d.chip;});
  var d=ds[i];if(!d)return log('no die '+i+' on the table');
  /* the REAL lane, from the pool die that owns this chip - the
     registration index is not the lane */
  var lane=(function(){
    var g=E('G');if(!g||!g.pool)return i;
    for(var p=0;p<g.pool.length;p++){var pd=g.pool[p];
      if(pd&&pd.el&&(pd.el===d.chip||pd.el.contains(d.chip)||d.chip.contains(pd.el)))
        return (typeof pd.lane==='number')?pd.lane:i;}
    return i;})();
  E('S.run.dice['+lane+']='+JSON.stringify(m));
  E('G&&G.matchDice&&(G.matchDice['+lane+']='+JSON.stringify(m)+')');
  E('G&&G.pool&&G.pool.forEach(function(pd){if(pd&&pd.lane==='+lane+')pd.mat='+JSON.stringify(m)+';})');
  /* tint materials bake their pip sheet AT CREATION - a live _reskin
     cannot rebuild it (bones stayed bones). Retag the chip, DROP the 3D
     die, remove its record: the next sync re-adopts the chip and builds
     the new material through the creation path. */
  d.chip._trueMat=m;
  d.chip.className=d.chip.className.replace(/dtype-[a-z0-9]+/,'dtype-'+m);
  var ix=dx.dice.indexOf(d);
  try{dx._drop(d);}catch(e){}
  if(ix>=0)dx.dice.splice(ix,1);
  log('die '+i+' (lane '+lane+') is now '+m+' - rebuilding\\u2026');
}""",
    'applyMat rebuilds through creation')

sub(u"""  E('S.run.dieEnch=S.run.dieEnch||[];S.run.dieEnch['+i+']='+JSON.stringify(ench));
  E('G&&(G._enchArr=G._enchArr||[null,null,null,null,null,null],G._enchArr['+i+']='+JSON.stringify(ench)+')');
  E('D3X._reskin&&D3X._reskin()');
  log('die '+i+' branded: '+k+(ench.face?(' on its '+face):''));""",
    u"""  E('S.run.dieEnch=S.run.dieEnch||[];S.run.dieEnch['+i+']='+JSON.stringify(ench));
  E('G&&(G._enchArr=G._enchArr||[null,null,null,null,null,null],G._enchArr['+i+']='+JSON.stringify(ench)+')');
  /* the brand rides _rebrand on THIS die (dress + faceLayers + settle
     dim), and the chip carries it for rebuild paths */
  var dx2=E('window.D3X');var ds2=dx2.dice.filter(function(d){return d.match&&d.chip;});
  if(ds2[i]){ds2[i].chip._ench=ench;
    try{dx2._rebrand(ds2[i]);}catch(e){E('D3X._reskin&&D3X._reskin()');}}
  log('die '+i+' branded: '+k+(ench.face?(' on its '+face):''));""",
    'applyEnch rebrands the one die')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d edits' % n)
