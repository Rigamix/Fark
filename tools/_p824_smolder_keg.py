# -*- coding: utf-8 -*-
"""P824: short_fuse's mandated tray smolder + powder_keg's detonation.

Census items 1 and 5. The short_fuse card text ITSELF specifies the
visual ("Tray smolders from roll three: the warning state must be
unmissable") and state.lit had no renderer at all - the game's
harshest hidden downside was invisible. The smolder rides the same
band the bust-red flinch proved visible (#matchBustRed's layer), an
ember radial pulsing under the dice, toggled exactly where lit is
written: on at the lit commit, off at turnStart / the bust burn / the
bank.

Powder keg's spec: "every die - including kept ones - visibly
detonates; the burst is the signal that locked dice are back in play."
It fired with zero dice-visuals. spawnShards per die (the same helper
sacrifice's shatter proved visible over the 3D dice) at the reroll.
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


# 1) the overlay element, beside the proven bust flinch
sub("""<div id="matchBustRed"></div><!-- P733: the bust flinch, same band -->""",
    """<div id="matchBustRed"></div><!-- P733: the bust flinch, same band -->
<div id="fuseSmolder"></div><!-- P824: short_fuse's lit-tray warning, same band -->""",
    'smolder element')

# 2) the CSS, after the flinch rules
sub("""#matchBustRed.on{opacity:1}""",
    """#matchBustRed.on{opacity:1}
/* P824: SHORT FUSE - the tray smolders while lit (the card's own text
   mandates the warning state). Same band as the bust flinch, which
   proved this layer paints under the dice and over the table. */
#fuseSmolder{position:absolute;inset:0;z-index:0;pointer-events:none;opacity:0;transition:opacity .8s ease;
  background:radial-gradient(ellipse 75% 45% at 50% 58%,rgba(214,92,34,.22),rgba(150,50,18,.11) 55%,transparent 75%);
  mix-blend-mode:screen}
#fuseSmolder.on{opacity:1;animation:fuseSmolderPulse 1.6s ease-in-out infinite}
@keyframes fuseSmolderPulse{0%,100%{filter:brightness(.85)}50%{filter:brightness(1.3)}}""",
    'smolder CSS')

# 3) toggled exactly where lit is written
sub("""    ev.mul(2);ev.me.state.lit=true;
    if(ev.owner==='p')_famPop('x2 SHORT FUSE');
    else setStatusMsg('THEIR FUSE BURNS — x2','red');},
  turnStart:function(ev){if(ev.mine)ev.me.state.lit=false;},""",
    """    ev.mul(2);ev.me.state.lit=true;
    if(ev.owner==='p'){_famPop('x2 SHORT FUSE');
      try{document.getElementById('fuseSmolder').classList.add('on');}catch(e){}/* P824 */}
    else setStatusMsg('THEIR FUSE BURNS — x2','red');},
  turnStart:function(ev){if(ev.mine){ev.me.state.lit=false;
    if(ev.owner==='p')try{document.getElementById('fuseSmolder').classList.remove('on');}catch(e){}}},
  bank:function(ev){if(ev.mine&&ev.owner==='p'){
    try{document.getElementById('fuseSmolder').classList.remove('on');}catch(e){}}},""",
    'smolder toggled at the lit writes')

sub("""      if(ev.owner==='p'){G.pPts=Math.max(0,G.pPts-burn);famLog('THE FIRE SPREADS — '+burn+' BURNS OFF YOUR BANK');}
      else{G.oPts=Math.max(0,G.oPts-burn);setStatusMsg('THE FIRE SPREADS — '+burn+' BURNS OFF THEIR BANK','gold');}
      try{updHUD();}catch(e){}}
    ev.me.state.lit=false;}""",
    """      if(ev.owner==='p'){G.pPts=Math.max(0,G.pPts-burn);famLog('THE FIRE SPREADS — '+burn+' BURNS OFF YOUR BANK');}
      else{G.oPts=Math.max(0,G.oPts-burn);setStatusMsg('THE FIRE SPREADS — '+burn+' BURNS OFF THEIR BANK','gold');}
      try{updHUD();}catch(e){}}
    ev.me.state.lit=false;
    if(ev.owner==='p')try{document.getElementById('fuseSmolder').classList.remove('on');}catch(e){}}""",
    'smolder dies with the burn')

# 4) the keg detonates its dice
sub("""    G.pool.forEach(function(d){
      d.committed=false;d._frozen=false;d.sel=false;
      d.val=_rollD(d);
      if(d.el){d.el.classList.remove('committed','selected','die-frozen');try{reDrawDieFace(d);}catch(e){}}
    });""",
    """    G.pool.forEach(function(d){
      d.committed=false;d._frozen=false;d.sel=false;
      d.val=_rollD(d);
      /* P824: the spec's one demand - every die VISIBLY detonates, the
         signal that kept dice are back in play. Same shards sacrifice's
         shatter proved visible over the 3D dice. */
      if(d.el)try{spawnShards(d.el,'#7a2f1a');}catch(e){}
      if(d.el){d.el.classList.remove('committed','selected','die-frozen');try{reDrawDieFace(d);}catch(e){}}
    });""",
    'the keg detonates')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d (%s)' % (len(edits), ', '.join(edits)))
