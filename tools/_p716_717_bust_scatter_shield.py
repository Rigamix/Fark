# -*- coding: utf-8 -*-
"""P716 + P717.

P716 THE BUST SCATTER AND THE SHIELD (Denis: "When busting, dice should
scatter around the table. If a card or die protects you from a bust then
they don't scatter, instead have a protective layer/shield effect around
the dice row").

Scatter: D3X.scatterRow stamps a planar kick on every settled match die in
the row - outward from the lane centre, decaying ease-out slide with a
tabletop spin laid over the frozen phys pose, the burst's exact idiom. The
dice END displaced (the wipe collects them ~1.3s later); the kick clears
wherever the pose clears (throw assign, table change) - one exit path. The
old CSS .scatter class stays: it drives the 3D dim and pauses material
idles, and its nth-child nudges remain the no-physics fallback.

Shield: _bustShieldFX blooms a ring around the dice row (the orphaned
Silver shieldFire bloom re-homed row-wide, no emoji - P684's rule) + an
FX.emit diamond ring pushed outward + SFX.shield, in the saver's colour:
amber for Amber, ward-ink for Ward, gold for every card save (the _runSave
funnel covers Hold the Line / Sunday's Rest / Brutus's Grit / Martyr /
Iron Stomach / One More Round in one line). Second Wind and Mabel's Stitch
get the shield at their trigger (points survive - it reads as a save);
Thick Skin and The Last Stitch keep the FULL bust first per the B1 ruling,
then the shield at their save beat - the bust lands, the card catches it.

P717 FAIR TRADE, the stopgap reword from OPEN.md #13's rec: the text stops
naming a stash the player cannot see, stops promising an unimplemented
one-roll duration, and stops implying a choice the code does not offer.
"""
import io, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'fark_proto.html')
s = io.open(P, encoding='utf-8', newline='').read()
n = 0


def sub(old, new, label, count=1):
    global s, n
    c = s.count(old)
    if c != count and '\n' in old:
        old2 = old.replace('\n', '\r\n')
        if s.count(old2) == count:
            old, c = old2, count
            new = new.replace('\n', '\r\n')
    if c != count:
        sys.exit('ANCHOR x%d (need %d) for %s' % (c, count, label))
    s = s.replace(old, new)
    n += 1
    print('  ok  %s' % label)


# ── P716.1: the kick, beside the burst it copies ──
sub(u"    d.burst={t0:performance.now(),\n"
    u"      ax:new THREE.Vector3(Math.random()-0.5,Math.random()-0.5,Math.random()-0.5)\n"
    u"           .normalize()};\n"
    u"  },",
    u"    d.burst={t0:performance.now(),\n"
    u"      ax:new THREE.Vector3(Math.random()-0.5,Math.random()-0.5,Math.random()-0.5)\n"
    u"           .normalize()};\n"
    u"  },\n"
    u"  /* P716: THE BUST SCATTER. A planar kick on every settled die in the\n"
    u"     row - outward from the lane centre, decaying slide + tabletop spin\n"
    u"     over the frozen phys pose (the burst's idiom). The dice END\n"
    u"     displaced; the wipe collects them. dist is in die-widths. */\n"
    u"  KICK:{ms:620,dist:1.5,spin:4.5},\n"
    u"  scatterRow:function(sel){\n"
    u"    if(!this.ready||this.fail||!this.PHYS||!this.PHYS.on)return 0;\n"
    u"    var self=this,n2=0,t0=performance.now();\n"
    u"    this.dice.forEach(function(d){\n"
    u"      if(!d.match||!d.phys||d.burst||d.kick)return;\n"
    u"      if(!d.chip||!d.chip.closest||!d.chip.closest(sel))return;\n"
    u"      d.kick={t0:t0,\n"
    u"        vx:((d.phys.x>=0?1:-1)*(0.55+Math.random()*0.9)+((Math.random()-0.5)*0.4))*self.KICK.dist,\n"
    u"        vz:(Math.random()-0.35)*self.KICK.dist*0.8,\n"
    u"        sp:(Math.random()<0.5?-1:1)*(2+Math.random()*3)};\n"
    u"      n2++;\n"
    u"    });\n"
    u"    if(n2)this._shDirty=true;\n"
    u"    return n2;\n"
    u"  },",
    'P716 KICK + scatterRow')

# ── P716.2: the kick pose in the settled branch ──
sub(u"          d.obj.position.set(d.phys.x,d.phys.y,d.phys.z);\n"
    u"          d.obj.quaternion.copy(d.phys.q);\n"
    u"          /* P702: scoring face bright, sides in shadow - derived from",
    u"          d.obj.position.set(d.phys.x,d.phys.y,d.phys.z);\n"
    u"          d.obj.quaternion.copy(d.phys.q);\n"
    u"          /* P716: the bust kick rides ON TOP of the frozen pose - ease-out\n"
    u"             to its displaced rest, spinning about the die's own up axis so\n"
    u"             the scoring face stays up. Shadows track while it moves. */\n"
    u"          if(d.kick){\n"
    u"            var _kt2=(performance.now()-d.kick.t0)/D3X.KICK.ms;\n"
    u"            if(_kt2>1)_kt2=1;\n"
    u"            var _ke2=1-Math.pow(1-_kt2,2.4);\n"
    u"            d.obj.position.x+=d.kick.vx*_ke2;\n"
    u"            d.obj.position.z+=d.kick.vz*_ke2;\n"
    u"            var _kq2=(D3X._kq||(D3X._kq=new THREE.Quaternion()));\n"
    u"            _kq2.setFromAxisAngle(D3X._kup||(D3X._kup=new THREE.Vector3(0,1,0)),d.kick.sp*_ke2*0.3);\n"
    u"            d.obj.quaternion.multiply(_kq2);\n"
    u"            if(_kt2<1)D3X._shDirty=true;\n"
    u"          }\n"
    u"          /* P702: scoring face bright, sides in shadow - derived from",
    'P716 kick pose')

# ── P716.3: the kick clears with the pose - one exit path ──
sub(u"    mine.forEach(function(d,i){d.roll={sol:sol,i:i,t0:t0,val:b.vals[i]};d.phys=null;});/* P702: val rides along */",
    u"    mine.forEach(function(d,i){d.roll={sol:sol,i:i,t0:t0,val:b.vals[i]};d.phys=null;d.kick=null;});/* P702 val rides; P716 kick clears with the pose */",
    'P716 kick clears at throw')

sub(u"          d.rk=rkNow;d.phys=null;d.roll=null;\n",
    u"          d.rk=rkNow;d.phys=null;d.roll=null;d.kick=null;/* P716 */\n",
    'P716 kick clears at table change')

# ── P716.4: the shield helper + the real scatter call ──
sub(u"function _bustImpact(){\n"
    u"  const area=document.getElementById('diceArea');",
    u"/* P716: THE SHIELD. A save reads as protection AROUND THE ROW, not a\n"
    u"   bust: one bloom ring over the dice row (the orphaned Silver shieldFire\n"
    u"   look re-homed row-wide, no emoji - P684's rule), an FX diamond ring\n"
    u"   pushed outward, SFX.shield - in the saver's own colour. */\n"
    u"function _bustShieldFX(color){\n"
    u"  try{\n"
    u"    var row=document.getElementById('playerDiceRow');if(!row)return;\n"
    u"    var r=row.getBoundingClientRect();if(!r.width)return;\n"
    u"    var ms=document.getElementById('screen-match')||document.body;\n"
    u"    var sr=ms.getBoundingClientRect();\n"
    u"    var ov=document.createElement('div');ov.className='bust-shield-row';\n"
    u"    ov.style.setProperty('--shc',color||'#9ab0d0');\n"
    u"    ov.style.left=(r.left-sr.left-14)+'px';ov.style.top=(r.top-sr.top-16)+'px';\n"
    u"    ov.style.width=(r.width+28)+'px';ov.style.height=(r.height+32)+'px';\n"
    u"    ms.appendChild(ov);\n"
    u"    setTimeout(function(){try{ov.remove();}catch(e){}},1300);\n"
    u"    try{SFX.shield&&SFX.shield();}catch(e){}\n"
    u"    if(window.FX&&FX.emit){\n"
    u"      var cx=r.left+r.width/2,cy=r.top+r.height/2;\n"
    u"      for(var i2=0;i2<22;i2++){\n"
    u"        var an=(i2/22)*Math.PI*2;\n"
    u"        FX.emit({x:cx+Math.cos(an)*r.width*0.5,y:cy+Math.sin(an)*r.height*0.62,\n"
    u"          vx:Math.cos(an)*42,vy:Math.sin(an)*30-12,g:60,\n"
    u"          life:520+Math.random()*260,size:3+Math.random()*3,\n"
    u"          rot:Math.random()*6.28,vr:2,shape:(i2%3)?'diamond':'star',\n"
    u"          color:color||'#9ab0d0'});\n"
    u"      }\n"
    u"    }\n"
    u"  }catch(e){}\n"
    u"}\n"
    u"function _bustImpact(){\n"
    u"  const area=document.getElementById('diceArea');",
    'P716 _bustShieldFX')

sub(u"  const row=document.getElementById('playerDiceRow');\n"
    u"  if(row)row.querySelectorAll('.die').forEach(el=>{el.classList.add('scatter');if(el._d3)D3.draw(el._d3);});",
    u"  const row=document.getElementById('playerDiceRow');\n"
    u"  if(row)row.querySelectorAll('.die').forEach(el=>{el.classList.add('scatter');if(el._d3)D3.draw(el._d3);});\n"
    u"  /* P716: the REAL scatter - a physical kick across the table. The class\n"
    u"     above stays: it dims the 3D dice and pauses idles, and its CSS\n"
    u"     nudges are the no-physics fallback. */\n"
    u"  try{if(window.D3X)D3X.scatterRow('#playerDiceRow');}catch(e){}",
    'P716 scatter joins the impact')

# ── P716.5: the shield CSS, beside the bloom it re-homes ──
sub(u"@keyframes shieldEmojiBloom{\n"
    u"  0%   {transform:scale(.2);opacity:0}\n"
    u"  20%  {transform:scale(1.45);opacity:1}\n"
    u"  60%  {transform:scale(1);opacity:1}\n"
    u"  100% {transform:scale(.85);opacity:0}\n"
    u"}",
    u"@keyframes shieldEmojiBloom{\n"
    u"  0%   {transform:scale(.2);opacity:0}\n"
    u"  20%  {transform:scale(1.45);opacity:1}\n"
    u"  60%  {transform:scale(1);opacity:1}\n"
    u"  100% {transform:scale(.85);opacity:0}\n"
    u"}\n"
    u"/* P716: the row shield - one bloom around the dice row when a save eats\n"
    u"   a bust. Colour rides --shc: amber, ward ink, or card gold. */\n"
    u".bust-shield-row{position:absolute;z-index:95;pointer-events:none;\n"
    u"  border-radius:18px;border:2px solid var(--shc,#9ab0d0);\n"
    u"  animation:rowShield 1.25s ease-out forwards}\n"
    u"@keyframes rowShield{\n"
    u"  0%{opacity:0;box-shadow:0 0 0 0 var(--shc,#9ab0d0);transform:scale(.92)}\n"
    u"  22%{opacity:.95;box-shadow:0 0 34px 10px color-mix(in srgb,var(--shc,#9ab0d0) 55%,transparent)}\n"
    u"  70%{opacity:.6;box-shadow:0 0 20px 6px color-mix(in srgb,var(--shc,#9ab0d0) 35%,transparent)}\n"
    u"  100%{opacity:0;box-shadow:0 0 0 0 transparent;transform:scale(1.02)}}",
    'P716 shield CSS')

# ── P716.6: the shields at every save ──
sub(u"  function _runSave(label,text){\n"
    u"    free.forEach(d=>{",
    u"  function _runSave(label,text){\n"
    u"    try{_bustShieldFX('#ffd98a');}catch(e){}/* P716: every card save shields */\n"
    u"    free.forEach(d=>{",
    'P716 shield in the save funnel')

sub(u"    G._bustImmuneTurn=false;\n"
    u"    try{setStatusMsg('AMBER HOLDS — THAT SAVE IS SPENT','gold');famLog('AMBER HOLDS — ONE BUST EATEN, THE NEXT ONE LANDS');}catch(e){}",
    u"    G._bustImmuneTurn=false;\n"
    u"    try{setStatusMsg('AMBER HOLDS — THAT SAVE IS SPENT','gold');famLog('AMBER HOLDS — ONE BUST EATEN, THE NEXT ONE LANDS');}catch(e){}\n"
    u"    try{_bustShieldFX('#e8a23c');}catch(e){}/* P716: amber's shield */",
    'P716 amber shield')

sub(u"    try{setStatusMsg('WARD HOLDS — '+(_wardBoosted?'TWO-THIRDS':'HALF')+' SURVIVES: '+_half,'gold');\n"
    u"      famLog('WARD — '+(_wardBoosted?'TWO-THIRDS':'HALF')+' THE TURN SURVIVES ('+_half+')');}catch(e){}",
    u"    try{setStatusMsg('WARD HOLDS — '+(_wardBoosted?'TWO-THIRDS':'HALF')+' SURVIVES: '+_half,'gold');\n"
    u"      famLog('WARD — '+(_wardBoosted?'TWO-THIRDS':'HALF')+' THE TURN SURVIVES ('+_half+')');}catch(e){}\n"
    u"    try{_bustShieldFX('#9ab0d0');}catch(e){}/* P716: the ward's shield */",
    'P716 ward shield')

sub(u"    G.activeCardState.secondWindActive=false;clearCardLabel('second_wind');",
    u"    G.activeCardState.secondWindActive=false;clearCardLabel('second_wind');\n"
    u"    try{_bustShieldFX('#ffd98a');}catch(e){}/* P716: the points survive - it reads as a save */",
    'P716 second wind shield')

sub(u"    G.activeCardState.stitchActive=false;clearCardLabel('mabels_stitch');",
    u"    G.activeCardState.stitchActive=false;clearCardLabel('mabels_stitch');\n"
    u"    try{_bustShieldFX('#ffd98a');}catch(e){}/* P716 */",
    'P716 stitch shield')

sub(u"  if(anyScoring(fv,effectiveCards(),fm,free)){\n"
    u"    _steadyDisarm();/* these dice are new - the arm was about the old ones */",
    u"  if(anyScoring(fv,effectiveCards(),fm,free)){\n"
    u"    _steadyDisarm();/* these dice are new - the arm was about the old ones */\n"
    u"    try{_bustShieldFX('#ffd98a');}catch(e){}/* P716: the gamble held - shield, not bust */",
    'P716 fools gold shield')

sub(u"    _bustImpact();\n"
    u"    if(window.DLG)DLG.trigger('PLAYER_BUST');\n"
    u"    /* Save fires AFTER the bust beat (~1s) so the relief reads clearly */",
    u"    _bustImpact();\n"
    u"    if(window.DLG)DLG.trigger('PLAYER_BUST');\n"
    u"    setTimeout(function(){try{_bustShieldFX('#ffd98a');}catch(e){}},1000);/* P716: bust lands, the card catches it (B1) */\n"
    u"    /* Save fires AFTER the bust beat (~1s) so the relief reads clearly */",
    'P716 thick skin late shield')

sub(u"    setTimeout(function(){\n"
    u"      if(_lsSaved>0){G.pPts+=_lsSaved;spawnPop('+'+_lsSaved+' LAST STITCH');}",
    u"    setTimeout(function(){\n"
    u"      try{_bustShieldFX('#ffd98a');}catch(e){}/* P716: same beat as Thick Skin (B1) */\n"
    u"      if(_lsSaved>0){G.pPts+=_lsSaved;spawnPop('+'+_lsSaved+' LAST STITCH');}",
    'P716 last stitch late shield')

# P717: Fair Trade tells the truth
sub(u"'Before you roll, swap one of your six dice for another from your stash. For this roll only.'",
    u"'Before you roll, your weakest die makes way for the best die you have won off another table. For this turn only.'",
    'P717 fair trade T1')
sub(u"'Before you roll, swap one of your six dice for another from your stash. The swap lasts the whole turn.'",
    u"'Before you roll, your weakest die makes way for the best die you have won off another table. For this turn only.'",
    'P717 fair trade T2')
sub(u"'Before you roll, swap one of your six dice for another from your stash. The swap lasts the whole turn. Twice a match.'",
    u"'Before you roll, your weakest die makes way for the best die you have won off another table. For this turn only. Twice a match.'",
    'P717 fair trade T3')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d edits' % n)
