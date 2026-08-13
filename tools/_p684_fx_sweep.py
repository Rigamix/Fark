# -*- coding: utf-8 -*-
"""P684: the legacy-FX sweep - every effect through the new engine.

Denis: "Are all effects using the new engine? ... There should be NOTHING
remaining from last game... (don't forget the stuff like shattering dice,
enchant effects, etc)."

The census (two independent passes) found the new vocabulary - FX.emit with
the game's diamond/star shapes, _fxSpray, spawnCardBurst, _sparkBand - used
by exactly SEVEN call sites, every one a card. Everything else drew squares in
hardcoded gold, bespoke DOM spawners, or nothing at all.

ONE-BUILDER STRATEGY: the four old spawners keep their signatures and get new
BODIES, so ~40 call sites modernise in four edits and no caller changes:

  spawnPixelSparks  35 sites (selection sparks, effect glows, NPC rewrites)
                    -> diamonds/stars in the DIE'S OWN material colour
                       (D3.SPARK - the same identity the offer sparkles use)
  spawnShards       heavy shatter - large tumbling diamonds, caller's colour
  spawnObsidianBurst same palette (glass darks + ember) as diamonds and stars
  spawnSawdust      fine brown diamond dust, sinking

AND THE HOLES GET FILLED:
  - Break destroyed a die with NO burst at all (the flagship enchant) - it
    shatters properly now, in the die's material colour.
  - _iconFire: 6 of 7 icon enchants fired with zero visual. One spray at the
    resolver, in the enchant's own ink from ENCH_ICONS - one edit, all seven.
  - Quicksilver's free reroll: silver spray on the die.
  - Branding a face in the shop: a spray in the enchant's ink as the icon
    lands mid-spin.
  - HOT DICE: the full-screen amber DOM wash (the old game's idiom) is gone;
    the word stays and a fountain of gold diamonds rises off the dice row.
  - The six-of-a-kind .perf-spark DOM-node spawner - the last per-particle
    DOM loop in the file - goes through FX.emit stars.
  - .spop drops its steps(5) pixel-era animation for a smooth rise; .px-spark
    (a rule with no caller) is deleted.
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
        sys.exit('ANCHOR x%d (need 1) for %s:\n  %r' % (c, label, old[:130]))
    s = s.replace(old, new)
    n += 1
    print('  ok  %s' % label)


# ── the material-colour helper + the four new bodies ────────────────────
OLD_PIX = s[s.index('function spawnPixelSparks(el,count){'):]
OLD_PIX = OLD_PIX[:OLD_PIX.index('\n}\n') + 3]

NEW_PIX = u"""/* P684: THE DIE'S OWN COLOUR. The offer and shop sparkles already know every
   material's spark identity (D3.SPARK); the in-match sparks were hardcoded
   #c8a050 squares. One lookup shares that identity everywhere. */
function _dieSparkCol(el){
  try{
    var w=el&&el.closest?el.closest('.die-wrap,.die'):null;
    var rec=(typeof G!=='undefined'&&G&&G.pool)?G.pool.find(function(d){return d.el===w||d.el===el||(w&&d.el===w);}):null;
    var mat=rec&&rec.mat;
    if(mat&&typeof D3!=='undefined'&&D3.SPARK&&D3.SPARK[mat])return D3.SPARK[mat].c;
  }catch(e){}
  return '#ffd98a';
}
/* P684: NEW BODY, OLD SIGNATURE - all ~35 call sites modernise at once. Was 8
   flat 4px #c8a050 squares; now the game's diamonds (a star now and then) in
   the die's material colour, rotating - the same silhouettes as everywhere
   else in the new engine. */
function spawnPixelSparks(el,count){
  if(!el||!count)return;
  var rect=el.getBoundingClientRect();
  if(!(rect.width>0))return;
  var cx=rect.left+rect.width/2, cy=rect.top+rect.height/2;
  var col=_dieSparkCol(el);
  var nOut=Math.max(4,Math.min(count,16));
  for(var i=0;i<nOut;i++){
    var a=Math.random()*Math.PI*2;
    var sp=55+Math.random()*70;
    FX.emit({x:cx+Math.cos(a)*rect.width*0.38, y:cy+Math.sin(a)*rect.height*0.38,
      vx:Math.cos(a)*sp, vy:Math.sin(a)*sp-25, g:120,
      life:0.35+Math.random()*0.35, size:5+Math.random()*4,
      rot:Math.random()*Math.PI, vr:(Math.random()-0.5)*7,
      shape:(Math.random()<0.15?'star':'diamond'), color:col});
  }
}
"""
if s.count(OLD_PIX) != 1:
    sys.exit('spawnPixelSparks body not unique')
s = s.replace(OLD_PIX, NEW_PIX)
n += 1
print('  ok  P684 pixel sparks reborn (35 sites)')


def replace_fn(name, new_body):
    global s, n
    i = s.index('function %s(' % name)
    j = s.index('\n}\n', i) + 3
    s = s[:i] + new_body + s[j:]
    n += 1
    print('  ok  P684 %s reborn' % name)


replace_fn('spawnShards',
 u"""/* P684: the heavy shatter - large tumbling diamonds in the caller's colour,
   the weight the old 11 grey squares never had. */
function spawnShards(el,color){
  if(!el)return;
  var r=el.getBoundingClientRect();if(!(r.width>0))return;
  var cx=r.left+r.width/2, cy=r.top+r.height/2;
  for(var i=0;i<13;i++){
    var a=Math.random()*Math.PI*2, sp=90+Math.random()*140;
    FX.emit({x:cx+(Math.random()-0.5)*r.width*0.5, y:cy+(Math.random()-0.5)*r.height*0.5,
      vx:Math.cos(a)*sp, vy:Math.sin(a)*sp-60, g:260,
      life:0.5+Math.random()*0.5, size:7+Math.random()*7,
      rot:Math.random()*Math.PI, vr:(Math.random()-0.5)*10,
      shape:'diamond', color:color||'#8a8aa8'});
  }
}
""")

replace_fn('spawnObsidianBurst',
 u"""/* P684: same glass-and-ember palette, the game's shapes - dark diamonds with
   ember stars in them instead of 32 flat squares. */
function spawnObsidianBurst(el){
  if(!el)return;
  var r=el.getBoundingClientRect();if(!(r.width>0))return;
  var cx=r.left+r.width/2, cy=r.top+r.height/2;
  var glass=['#1a1a28','#0a0a14','#7a7aa0'];
  for(var i=0;i<14;i++){
    var a=Math.random()*Math.PI*2, sp=100+Math.random()*130;
    FX.emit({x:cx, y:cy, vx:Math.cos(a)*sp, vy:Math.sin(a)*sp-70, g:280,
      life:0.45+Math.random()*0.5, size:6+Math.random()*7,
      rot:Math.random()*Math.PI, vr:(Math.random()-0.5)*11,
      shape:'diamond', color:glass[i%3]});
  }
  for(var k=0;k<6;k++){
    var a2=Math.random()*Math.PI*2;
    FX.emit({x:cx, y:cy, vx:Math.cos(a2)*70, vy:Math.sin(a2)*70-90, g:180,
      life:0.6+Math.random()*0.5, size:6+Math.random()*4,
      rot:Math.random()*Math.PI, vr:(Math.random()-0.5)*8,
      shape:'star', color:'#d4552f'});
  }
}
""")

replace_fn('spawnSawdust',
 u"""/* P684: fine dust that sinks - tiny brown diamonds now, same motion. */
function spawnSawdust(el,count){
  if(!el)return;
  var r=el.getBoundingClientRect();if(!(r.width>0))return;
  var cx=r.left+r.width/2, cy=r.top+r.height/2;
  for(var i=0;i<(count||10);i++){
    FX.emit({x:cx+(Math.random()-0.5)*r.width*0.8, y:cy+(Math.random()-0.5)*r.height*0.4,
      vx:(Math.random()-0.5)*36, vy:16+Math.random()*30, g:60,
      life:0.5+Math.random()*0.5, size:3+Math.random()*3,
      rot:Math.random()*Math.PI, vr:(Math.random()-0.5)*4,
      shape:'diamond', color:['#8a6a42','#6a5232','#a5825a'][i%3]});
  }
}
""")

# ── Break finally bursts ────────────────────────────────────────────────
sub(u"    /* the class alone animates a box nobody can see - see D3X.shatter */\n"
    u"    try{if(window.D3X&&D3X.shatter)D3X.shatter(d.el);}catch(e2){}",
    u"    /* the class alone animates a box nobody can see - see D3X.shatter */\n"
    u"    try{if(window.D3X&&D3X.shatter)D3X.shatter(d.el);}catch(e2){}\n"
    u"    /* P684: the flagship enchant destroyed a die with NO burst at all -\n"
    u"       counted in the census: obsidian shatter had one, Sacrifice had one,\n"
    u"       Break had nothing. The die's own material colour. */\n"
    u"    try{spawnShards(d.el,_dieSparkCol(d.el));}catch(e3){}",
    'P684 Break bursts at last')

# ── every enchant fire shows itself ─────────────────────────────────────
sub(u"  var mult=(def.doubles&&_kindredActive())?2:1;",
    u"  /* P684: 6 of 7 icon enchants fired with ZERO visual (census). One spray\n"
    u"     at the shared resolver covers them all, in the enchant's own ink. */\n"
    u"  try{if(d&&d.el&&typeof _fxSpray==='function')_fxSpray(d.el,def.ink||'#ffd98a',12,{speed:85,g:70,size:7,spread:2.4});}catch(eV){}\n"
    u"  var mult=(def.doubles&&_kindredActive())?2:1;",
    'P684 enchant fires show')

sub(u"  d.val=_rollD(d);d.sel=false;try{reDrawDieFace(d);}catch(e){}",
    u"  d.val=_rollD(d);d.sel=false;try{reDrawDieFace(d);}catch(e){}\n"
    u"  /* P684: the free reroll was invisible - the face just changed */\n"
    u"  try{if(d.el&&typeof _fxSpray==='function')_fxSpray(d.el,'#eef4fb',10,{speed:75,g:50,size:6,spread:2.6});}catch(eQ){}",
    'P684 quicksilver shows')

# ── branding a face in the shop ─────────────────────────────────────────
sub(u"    ov.classList.add('flash');",
    u"    ov.classList.add('flash');/* P684 marker: see hot-dice edit below */",
    'P684 disambiguate flash sites') if False else None
# the rebrand moment: _rebrand call inside the enchant spin
c = s.count(u"D3X._rebrand(d)")
if c < 1:
    sys.exit('rebrand site missing')
s = s.replace(u"D3X._rebrand(d)",
              u"D3X._rebrand(d);try{if(d&&d.el&&typeof _fxSpray==='function'){var _bi=(typeof ENCH_ICONS!=='undefined'&&typeof _stEnchK!=='undefined'&&ENCH_ICONS[_stEnchK]&&ENCH_ICONS[_stEnchK].ink)||'#ffd98a';_fxSpray(d.el,_bi,14,{speed:95,g:90,size:8,spread:2.4});}}catch(eB){}",
              1)
n += 1
print('  ok  P684 brand lands with a spray (ink from _stEnchK)')

# ── hot dice: the wash goes, a fountain rises ───────────────────────────
sub(u"@keyframes hFlash{0%{background:rgba(180,140,30,.5);opacity:1}50%{background:rgba(140,105,20,.25);opacity:1}100%{background:transparent;opacity:0}}",
    u"/* P684: the full-screen amber wash was the old game's idiom - the word\n"
    u"   stays, the background never paints, and the celebration is the diamond\n"
    u"   fountain showHot now emits. */\n"
    u"@keyframes hFlash{0%{background:transparent;opacity:1}100%{background:transparent;opacity:0}}",
    'P684 the wash goes')

sub(u"  _alignOverlayWord(ov.querySelector('.hot-word'));\n"
    u"  ov.classList.remove('flash');void ov.offsetWidth;ov.classList.add('flash');",
    u"  _alignOverlayWord(ov.querySelector('.hot-word'));\n"
    u"  ov.classList.remove('flash');void ov.offsetWidth;ov.classList.add('flash');\n"
    u"  /* P684: the new-engine celebration - a fountain of gold diamonds off the\n"
    u"     dice row, where the six scoring dice actually are */\n"
    u"  try{\n"
    u"    var _hr=document.getElementById('playerDiceRow')||document.getElementById('diceArea');\n"
    u"    if(_hr&&typeof FX!=='undefined'&&FX.emit){\n"
    u"      var _hb=_hr.getBoundingClientRect();\n"
    u"      for(var _hi=0;_hi<34;_hi++){\n"
    u"        var _ha=-Math.PI/2+(Math.random()-0.5)*1.1;\n"
    u"        var _hs=140+Math.random()*160;\n"
    u"        FX.emit({x:_hb.left+Math.random()*_hb.width, y:_hb.top+_hb.height*0.5,\n"
    u"          vx:Math.cos(_ha)*_hs, vy:Math.sin(_ha)*_hs, g:210,\n"
    u"          life:0.7+Math.random()*0.7, size:6+Math.random()*7,\n"
    u"          rot:Math.random()*Math.PI, vr:(Math.random()-0.5)*8,\n"
    u"          shape:(Math.random()<0.25?'star':'diamond'),\n"
    u"          color:['#ffd98a','#f0c860','#e1a755'][_hi%3]});\n"
    u"      }\n"
    u"    }\n"
    u"  }catch(eH){}",
    'P684 the fountain')

# ── six-of-a-kind: the last DOM particle loop ───────────────────────────
sub(u"      selD.forEach(function(d,di){const dr=d.el.getBoundingClientRect();\n"
    u"        const cx=dr.left+dr.width/2-areaRect.left;const cy=dr.top+dr.height/2-areaRect.top;\n"
    u"        for(let j=0;j<5;j++){const sp=document.createElement('div');sp.className='perf-spark';\n"
    u"          const angle=Math.random()*Math.PI*2;const dist=120+Math.random()*180;\n"
    u"          const dx=Math.cos(angle)*dist;const dy=Math.sin(angle)*dist;\n"
    u"          sp.style.left=cx+'px';sp.style.top=cy+'px';\n"
    u"          sp.style.setProperty('--dx',dx+'px');sp.style.setProperty('--dy',dy+'px');\n"
    u"          sp.style.animationDelay=(di*0.07+j*0.06)+'s';\n"
    u"          sp.style.width=sp.style.height=(2+Math.random()*3)+'px';\n"
    u"          area.appendChild(sp);setTimeout(function(){sp.remove();},2800);}\n"
    u"      });",
    u"      /* P684: was the last per-particle DOM-node spawner in the file - the\n"
    u"         exact pattern the FX header says it replaced. Stars, through the\n"
    u"         pooled engine. */\n"
    u"      selD.forEach(function(d,di){const dr=d.el.getBoundingClientRect();\n"
    u"        const cx=dr.left+dr.width/2;const cy=dr.top+dr.height/2;\n"
    u"        for(let j=0;j<5;j++){\n"
    u"          const angle=Math.random()*Math.PI*2;const sp2=90+Math.random()*130;\n"
    u"          FX.emit({x:cx,y:cy,vx:Math.cos(angle)*sp2,vy:Math.sin(angle)*sp2-40,g:130,\n"
    u"            life:0.8+Math.random()*0.8,size:5+Math.random()*5,\n"
    u"            rot:Math.random()*Math.PI,vr:(Math.random()-0.5)*7,\n"
    u"            shape:'star',color:['#ffe9b0','#ffd98a','#fff4d8'][j%3]});\n"
    u"        }\n"
    u"      });",
    'P684 six-kind through the engine')

# ── polish: spop smooths, the dead rule dies ────────────────────────────
sub(u"  animation:sPop .8s steps(5) forwards;",
    u"  animation:sPop .8s ease-out forwards;/* P684: steps(5) was the pixel era */",
    'P684 spop smooths')

sub(u".px-spark{",
    u".px-spark-dead{/* P684: no caller creates .px-spark any more */",
    'P684 dead rule retired') if s.count(u".px-spark{") == 1 else print('  (px-spark rule not found once - skipped)')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('\n%d edits' % n)
