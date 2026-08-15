# -*- coding: utf-8 -*-
"""P733 (C14): the bust scatters like chaos, and the room flinches red.

Denis: 'Dice part in the middle and bunch up rather than true chaos.
Try changing the candle light to red/orange when busting.'

SCATTER: the old kick took its direction from the die's SIGN (left of
centre goes left, right goes right) with only a small jitter - a parting,
by construction, and every die got nearly the same push. Now each die
gets its own ANGLE (outward bias, +/-42 degrees of spread), its own
MAGNITUDE (0.65-1.45x), and two dice in the row are picked for a hard
hit (1.5-2.1x) with a faster spin. Chaos reads from VARIANCE, not force
(docs/VFX_LANGUAGE.md section 10).

THE CANDLE: on impact the room flinches - the 3D rig's lights lerp
toward the bust red over 160ms, hold, and ease back over 900ms, while a
red multiply layer breathes over the ROOM ART ONLY (the same z:0 art
band the vignette lives in, so the HUD, dice and buttons stay clean).
This is the ONE non-L3 world response, logged as the explosion exception
in the language doc.
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


# 1) the scatter: variance, not a parting
sub(u"""  KICK:{ms:620,dist:1.5,spin:4.5},
  scatterRow:function(sel){
    if(!this.ready||this.fail||!this.PHYS||!this.PHYS.on)return 0;
    var self=this,n2=0,t0=performance.now();
    this.dice.forEach(function(d){
      if(!d.match||!d.phys||d.burst||d.kick)return;
      if(!d.chip||!d.chip.closest||!d.chip.closest(sel))return;
      d.kick={t0:t0,
        vx:((d.phys.x>=0?1:-1)*(0.55+Math.random()*0.9)+((Math.random()-0.5)*0.4))*self.KICK.dist,
        vz:(Math.random()-0.35)*self.KICK.dist*0.8,
        sp:(Math.random()<0.5?-1:1)*(2+Math.random()*3)};
      n2++;
    });
    if(n2)this._shDirty=true;
    return n2;
  },""",
    u"""  KICK:{ms:620,dist:1.5,spin:4.5},
  scatterRow:function(sel){
    if(!this.ready||this.fail||!this.PHYS||!this.PHYS.on)return 0;
    var self=this,t0=performance.now();
    /* P733: CHAOS IS VARIANCE. The old kick read its direction off the
       die's SIGN - left of centre went left, right went right, with a
       whisker of jitter - so the row PARTED and bunched, which is what
       Denis saw. Each die now gets its own angle (outward bias, wide
       spread), its own magnitude, and two of them are picked for a hard
       hit. Same one impulse, applied unevenly. */
    var hit=[];
    this.dice.forEach(function(d){
      if(!d.match||!d.phys||d.burst||d.kick)return;
      if(!d.chip||!d.chip.closest||!d.chip.closest(sel))return;
      hit.push(d);
    });
    if(!hit.length)return 0;
    /* the two unlucky ones */
    var hard={},picks=Math.min(2,hit.length);
    while(Object.keys(hard).length<picks)hard[Math.floor(Math.random()*hit.length)]=1;
    hit.forEach(function(d,i){
      /* outward from the row's middle, then thrown off by up to 42 degrees */
      var base=Math.atan2((Math.random()-0.5)*0.6,(d.phys.x>=0?1:-1));
      var ang=base+(Math.random()-0.5)*1.47;
      var mag=(hard[i]?1.5+Math.random()*0.6:0.65+Math.random()*0.8)*self.KICK.dist;
      d.kick={t0:t0,
        vx:Math.cos(ang)*mag,
        vz:Math.sin(ang)*mag*0.7-0.1*self.KICK.dist,
        sp:(Math.random()<0.5?-1:1)*(hard[i]?4+Math.random()*3:1.5+Math.random()*3)};
    });
    this._shDirty=true;
    return hit.length;
  },
  /* P733: THE ROOM FLINCHES. The rig's lights lerp toward the bust red
     and ease back; the art's red wash is done in _bustCandle beside it.
     Reserved for the bust - a world response that fires often means
     nothing (docs/VFX_LANGUAGE.md E1). */
  BUSTLIGHT:{col:0xc03818, mix:0.72, inMs:160, holdMs:220, outMs:900},
  bustFlare:function(){
    if(!this.ready||this.fail||!this.scene)return false;
    var B=this.BUSTLIGHT,ls=[];
    this.scene.traverse(function(o){if(o.isLight)ls.push(o);});
    if(!ls.length)return false;
    var red=new THREE.Color(B.col);
    ls.forEach(function(l){if(!l.userData._bcBase)l.userData._bcBase=l.color.clone();});
    var t0=performance.now();
    var step=function(){
      var t=performance.now()-t0,k;
      if(t<B.inMs)k=t/B.inMs;
      else if(t<B.inMs+B.holdMs)k=1;
      else k=Math.max(0,1-(t-B.inMs-B.holdMs)/B.outMs);
      var m=k*B.mix;
      ls.forEach(function(l){
        var b=l.userData._bcBase;
        l.color.setRGB(b.r*(1-m)+red.r*m,b.g*(1-m)+red.g*m,b.b*(1-m)+red.b*m);
      });
      if(t<B.inMs+B.holdMs+B.outMs)requestAnimationFrame(step);
      else ls.forEach(function(l){if(l.userData._bcBase)l.color.copy(l.userData._bcBase);});
    };
    requestAnimationFrame(step);
    return true;
  },""",
    'scatter chaos + bustFlare')

# 2) the art's red wash, in the same band as the look vignette
sub(u"#matchLookVig{position:absolute;inset:0;z-index:0;pointer-events:none;",
    u"/* P733: the bust's red breath over the ROOM ART - same z:0 band as\n"
    u"   the look vignette, so the dice, HUD and buttons stay clean. */\n"
    u"#matchBustRed{position:absolute;inset:0;z-index:0;pointer-events:none;\n"
    u"  mix-blend-mode:multiply;opacity:0;background:radial-gradient(ellipse at 50% 46%,\n"
    u"  rgba(192,56,24,.55) 0%, rgba(120,24,10,.85) 100%);\n"
    u"  transition:opacity .16s ease-out}\n"
    u"#matchBustRed.on{opacity:1}\n"
    u"#matchLookVig{position:absolute;inset:0;z-index:0;pointer-events:none;",
    'bust red CSS')

sub(u"""<div id="matchLookVig"></div><!-- P732: the approved look's vignette - art band, under everything interactive -->""",
    u"""<div id="matchLookVig"></div><!-- P732: the approved look's vignette - art band, under everything interactive -->
<div id="matchBustRed"></div><!-- P733: the bust flinch, same band -->""",
    'bust red element')

# 3) hook both into the impact
sub(u"""  /* P716: the REAL scatter - a physical kick across the table. The class
     above stays: it dims the 3D dice and pauses idles, and its CSS
     nudges are the no-physics fallback. */
  try{if(window.D3X)D3X.scatterRow('#playerDiceRow');}catch(e){}
}""",
    u"""  /* P716: the REAL scatter - a physical kick across the table. The class
     above stays: it dims the 3D dice and pauses idles, and its CSS
     nudges are the no-physics fallback. */
  try{if(window.D3X)D3X.scatterRow('#playerDiceRow');}catch(e){}
  /* P733: and the room flinches red - the rig's lights and the art's
     wash together, so dice and table agree about what just happened. */
  try{if(window.D3X&&D3X.bustFlare)D3X.bustFlare();}catch(e){}
  try{
    var _br=document.getElementById('matchBustRed');
    if(_br){
      _br.style.transition='opacity .16s ease-out';
      _br.classList.add('on');
      setTimeout(function(){
        _br.style.transition='opacity .9s ease-in';
        _br.classList.remove('on');
      },380);
    }
  }catch(e){}
}""",
    'impact fires both')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d edits' % n)
