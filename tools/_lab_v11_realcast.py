# -*- coding: utf-8 -*-
"""Lab v11: the studio can fire the REAL effect, not just the look.

Denis: 'if I select a die and click test on the table it plays the
effect but doesn't change my die. Is it cosmetic only?' Yes - and now
there are two buttons, honestly labelled: TEST THE LOOK (recipe only)
and CAST FOR REAL (the game's own famUse/_iconFire/mechanic runs first,
then the recipe plays on top, so the two are seen together). Materials
dress the picked die through the dresser path."""
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


sub(u"""        <div class="row">
          <button onclick="studioPlay()">▶ test on the table</button>
          <button onclick="studioSave()">save this moment</button>
          <span id="wsState" style="font-size:11px;color:#8a7a5a"></span>
        </div>""",
    u"""        <div class="row">
          <button onclick="studioPlay()">▶ test the look</button>
          <button onclick="studioCast()">⚡ cast for REAL (effect + look)</button>
          <button onclick="studioSave()">save this moment</button>
          <span id="wsState" style="font-size:11px;color:#8a7a5a"></span>
        </div>
        <div class="row" style="font-size:10px;color:#8a7a5a">
          the look is cosmetic; CAST runs the game's own mechanic first, then plays it
        </div>""",
    'two buttons in the studio')

sub(u"""function studioPlay(){""",
    u"""function studioCast(){
  /* THE GAME'S OWN EFFECT, then the look on top. Cards go through
     famUse (charges, canUse, the real mechanic); enchant brands through
     _iconFire; materials dress the picked die. */
  var id=_studioId;if(!id)return log('open a card first');
  var g=E('G');
  if(id.indexOf(':')<0){
    if(!g)return log('no match');
    var ix=(g.pF||[]).findIndex(function(x){return x.id===id;});
    if(ix<0){document.getElementById('cardPick').value=id;addCard();
      g=E('G');ix=(g.pF||[]).findIndex(function(x){return x.id===id;});}
    if(ix<0)return log('could not deal '+id);
    var before=JSON.stringify({
      pool:(g.pool||[]).map(function(d){return {v:d.val,c:!!d.committed,m:d.mat};}),
      kept:(g.kept||[]).length,turnPts:g.turnPts,numDice:g.numDice});
    try{E('famUse('+ix+')');}catch(e){log('cast threw: '+e);}
    var g2=E('G');
    var after=JSON.stringify({
      pool:(g2.pool||[]).map(function(d){return {v:d.val,c:!!d.committed,m:d.mat};}),
      kept:(g2.kept||[]).length,turnPts:g2.turnPts,numDice:g2.numDice});
    log(before===after
      ? 'CAST: the mechanic ran but changed nothing here - it likely needs a different game state (a kept pair, a scoring die, the rival to have rolled)'
      : 'CAST: the game state CHANGED - the mechanic is live');
  }else if(id.slice(0,5)==='ench:'){
    var k=id.slice(5);
    if(!target||target.k!=='die')return log('pick a DIE target, then cast');
    document.getElementById('dressEnch').value=k;applyEnch();
    try{E('ENCH_ICONS['+JSON.stringify(k)+']&&ENCH_ICONS['+JSON.stringify(k)+'].fire&&ENCH_ICONS['+JSON.stringify(k)+'].fire({mult:1})');
      log('brand applied AND fired');}catch(e){log('brand applied (no fire): '+e);}
  }else{
    var m=id.slice(4);
    if(!target||target.k!=='die')return log('pick a DIE target, then cast');
    document.getElementById('dressMat').value=m;applyMat();
  }
  setTimeout(studioPlay,220);/* the look, over the real thing */
}
function studioPlay(){""",
    'studioCast')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d edits' % n)
