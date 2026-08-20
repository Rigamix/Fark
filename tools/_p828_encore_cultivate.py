# -*- coding: utf-8 -*-
"""P828: encore turns starstone-blue; cultivate's growth shows on the die.

Census: the spec wants encore's reroll visually DISTINCT from powder
keg's explosion - a soft blue shimmer on only the current roll's dice
- but .card-reroll is hard-coded gold, so the contrast ran backwards.
The keg got its detonation in P824; encore now rerolls in starstone
blue via a modifier class (the pulse keyframes must swap too - the
animation's own box-shadow values beat any static override).

Cultivate: the growth store per lane (G._cultArr) was invisible. Each
stacking commit now floats the die's accumulated bonus off the jade
that carries it (spawnPop's die anchor + a green spray).
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


# 1) the blue modifier - both the static state and the pulse animation
sub("""@keyframes cardRerollPulse{
  0%,100%{box-shadow:0 0 14px 4px rgba(255,180,40,.7),0 0 6px rgba(255,220,80,.4)}
  50%{box-shadow:0 0 20px 6px rgba(255,180,40,.9),0 0 10px rgba(255,220,80,.6)}
}""",
    """@keyframes cardRerollPulse{
  0%,100%{box-shadow:0 0 14px 4px rgba(255,180,40,.7),0 0 6px rgba(255,220,80,.4)}
  50%{box-shadow:0 0 20px 6px rgba(255,180,40,.9),0 0 10px rgba(255,220,80,.6)}
}
/* P828: encore's shimmer is STARSTONE BLUE - the spec's contrast with
   powder keg's explosion. The modifier swaps the animation, not just
   the static shadow: keyframe box-shadows beat any static override. */
.die.card-reroll.crr-blue{
  box-shadow:0 0 14px 4px rgba(143,168,255,.7),0 0 6px rgba(190,205,255,.4)!important;
  animation:dRoll .4s linear infinite,cardRerollPulseBlue .6s ease-in-out infinite!important;
}
@keyframes cardRerollPulseBlue{
  0%,100%{box-shadow:0 0 14px 4px rgba(143,168,255,.7),0 0 6px rgba(190,205,255,.4)}
  50%{box-shadow:0 0 20px 6px rgba(143,168,255,.9),0 0 10px rgba(190,205,255,.6)}
}""",
    'the blue shimmer class')

# 2) encore wears it (and cleans it up with the gold class)
sub("""    free.forEach(function(d){
      d.val=_rollD(d);d.sel=false;
      if(d.el){d.el.classList.remove('selected');d.el.classList.add('card-reroll');reDrawDieFace(d);
        setTimeout(function(){d.el.classList.remove('card-reroll');},400);}
    });""",
    """    free.forEach(function(d){
      d.val=_rollD(d);d.sel=false;
      if(d.el){d.el.classList.remove('selected');d.el.classList.add('card-reroll','crr-blue');reDrawDieFace(d);
        try{_fxSpray(d.el,'#8fa8ff',8,{speed:65,g:-20,size:5,spread:2.0});}catch(e){}/* P828: starstone motes */
        setTimeout(function(){d.el.classList.remove('card-reroll','crr-blue');},400);}
    });""",
    'encore rerolls in blue')

# 3) cultivate's growth floats off the die that carries it
sub("""    ev.jade.forEach(function(d){
      var L=d.lane;
      if(typeof L!=='number'||!(L>=0))return;/* NaN fails >=0, unlike <0 */
      grown+=(_arr[L]||0);
      _arr[L]=(_arr[L]||0)+50;
    });""",
    """    ev.jade.forEach(function(d){
      var L=d.lane;
      if(typeof L!=='number'||!(L>=0))return;/* NaN fails >=0, unlike <0 */
      grown+=(_arr[L]||0);
      _arr[L]=(_arr[L]||0)+50;
      /* P828: the stack is visible ON the die - its accumulated growth
         floats off the jade that carries it, with the family's green. */
      if(ev.owner==='p'&&d.el){
        try{spawnPop('\\u25B4 '+_arr[L],d.el);}catch(e){}
        try{_fxSpray(d.el,'#46c46e',8,{speed:60,g:-30,size:5,spread:1.4});}catch(e){}
      }
    });""",
    'cultivate growth on the die')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d (%s)' % (len(edits), ', '.join(edits)))
