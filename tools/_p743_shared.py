# -*- coding: utf-8 -*-
"""P743: ONE bust beat for both sides, gentler; the arm is a gradient;
spent cards grey; the tooltip title's outline is its own colour.

Denis, and he is right to keep saying it: 'FIX THE ROOT NOT THE END. The
dice mechanic should be shared between me and the NPC - if you apply the
bust visual for me it should apply to the NPC. Same for card and enchant
effects. Just upside down.'

- THE BUST BEAT IS ONE FUNCTION NOW. `_bustBeat(side)` scatters that
  side's row, flares the rig and breathes the red - the player's
  _bustImpact calls it, and so does the rival's _oppBustOut, which had
  no visual at all. The row selector is the only thing that differs.
- AND IT STAYS ON THE TABLE. The kick was measured in die-widths with no
  ceiling, so a hard hit could carry a die off screen. Each die's kick is
  now clamped to the distance that keeps it inside the row's span, and
  a die that would pass the edge bounces off it instead.
- THE ARM IS A GRADIENT. The drag exposes its progress toward the line
  as --arm (0..1) on the card; the glow, the lift and the grey all ride
  that, so nothing switches on in one frame. The reason line fades in on
  the same value.
- A CARD WITH NO USES LEFT reads spent in the hand: the row already
  baked .spent, but the drag's own filters could outrank it mid-gesture,
  so spent now wins and a spent card cannot be dragged at all.
- The tooltip title's outline is a darker, more saturated version of the
  title's own colour rather than black, and thinner.
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


# ── 1. the scatter: gentler, clamped, and side-agnostic ──
sub(u"  KICK:{ms:620,dist:1.5,spin:4.5},",
    u"  /* P743: dist 1.5 -> 0.85 (Denis: 'too strong - dice should not\n"
    u"     leave the screen but they can bounce off it') and every kick is\n"
    u"     clamped below so a hard hit cannot carry a die past the row's\n"
    u"     own span; a die that would pass the edge bounces off it. */\n"
    u"  KICK:{ms:620,dist:0.85,spin:4.5,edge:2.6},",
    'gentler kick')

sub(u"""    hit.forEach(function(d,i){
      /* outward from the row's middle, then thrown off by up to 42 degrees */
      var base=Math.atan2((Math.random()-0.5)*0.6,(d.phys.x>=0?1:-1));
      var ang=base+(Math.random()-0.5)*1.47;
      var mag=(hard[i]?1.5+Math.random()*0.6:0.65+Math.random()*0.8)*self.KICK.dist;
      d.kick={t0:t0,
        vx:Math.cos(ang)*mag,
        vz:Math.sin(ang)*mag*0.7-0.1*self.KICK.dist,
        sp:(Math.random()<0.5?-1:1)*(hard[i]?4+Math.random()*3:1.5+Math.random()*3)};
    });""",
    u"""    hit.forEach(function(d,i){
      /* outward from the row's middle, then thrown off by up to 42 degrees */
      var base=Math.atan2((Math.random()-0.5)*0.6,(d.phys.x>=0?1:-1));
      var ang=base+(Math.random()-0.5)*1.47;
      var mag=(hard[i]?1.5+Math.random()*0.6:0.65+Math.random()*0.8)*self.KICK.dist;
      var vx=Math.cos(ang)*mag,vz=Math.sin(ang)*mag*0.7-0.1*self.KICK.dist;
      /* P743: THE TABLE HAS EDGES. The kick was unbounded, so a hard hit
         carried a die off screen. Anything that would end past the edge
         bounces off it - the sign flips and the overshoot is what is
         left of the travel, which is what a wall does. */
      var edge=self.KICK.edge||2.6,endX=d.phys.x+vx;
      if(endX>edge)vx=(edge-d.phys.x)-(endX-edge)*0.45;
      else if(endX<-edge)vx=(-edge-d.phys.x)-(endX+edge)*0.45;
      if(Math.abs(vz)>edge*0.5)vz=(vz>0?1:-1)*edge*0.5;
      d.kick={t0:t0,vx:vx,vz:vz,
        sp:(Math.random()<0.5?-1:1)*(hard[i]?4+Math.random()*3:1.5+Math.random()*3)};
    });""",
    'kick clamped to the table')

# ── 2. ONE bust beat, both sides ──
sub(u"""  /* P733: THE ROOM FLINCHES.""",
    u"""  /* P743: THE BUST BEAT, ONE FUNCTION, EITHER SIDE. Denis: 'it should
     happen the same exact way for the NPC - the dice mechanic should be
     shared'. The row is the only thing that differs; the scatter, the
     flare and the red are identical, so the rival's bust can never drift
     from the player's or be forgotten again. */
  bustBeat:function(side){
    var row=(side==='o')?'#oppDiceRow':'#playerDiceRow';
    var kicked=0;
    try{kicked=this.scatterRow(row);}catch(e){}
    try{this.bustFlare();}catch(e){}
    try{
      var br=document.getElementById('matchBustRed');
      if(br){
        br.style.transition='none';br.classList.add('on');
        setTimeout(function(){
          br.style.transition='opacity .9s ease-in';br.classList.remove('on');
        },380);
      }
    }catch(e){}
    return kicked;
  },
  /* P733: THE ROOM FLINCHES.""",
    'bustBeat shared')

sub(u"""  try{if(window.D3X)D3X.scatterRow('#playerDiceRow');}catch(e){}
  /* P733: and the room flinches red - the rig's lights and the art's
     wash together, so dice and table agree about what just happened. */
  try{if(window.D3X&&D3X.bustFlare)D3X.bustFlare();}catch(e){}
  try{
    var _br=document.getElementById('matchBustRed');
    if(_br){
      _br.style.transition='none';/* the flash is instant; only the fade eases */
      _br.classList.add('on');
      setTimeout(function(){
        _br.style.transition='opacity .9s ease-in';
        _br.classList.remove('on');
      },380);
    }
  }catch(e){}
}""",
    u"""  /* P743: the shared beat - the rival's bust runs the identical one */
  try{if(window.D3X&&D3X.bustBeat)D3X.bustBeat('p');}catch(e){}
}""",
    'player uses the shared beat')

sub(u"""        try{famFire('bust',{actor:'o'});}catch(e){}""",
    u"""        try{famFire('bust',{actor:'o'});}catch(e){}
        /* P743: THE RIVAL'S BUST LOOKS LIKE A BUST. It had no visual at
           all - the scatter and the flinch were wired to the player's
           path only. Same function, their row. */
        try{if(window.D3X&&D3X.bustBeat)D3X.bustBeat('o');}catch(e){}""",
    'rival uses the shared beat')

# ── 3. the arm is a gradient ──
sub(u"""    var past=(_famDrag.cy0+dy)<_famDrag.line;""",
    u"""    /* P743: PROGRESS, not a switch. 0 at rest, 1 at the line - the
       glow, the lift, the grey and the reason all ride this one value,
       so nothing appears in a single frame. */
    var _span=Math.max(40,_famDrag.cy0-_famDrag.line);
    var _k=(_famDrag.cy0-(_famDrag.cy0+dy)-0)/_span;
    if(_k<0)_k=0;if(_k>1)_k=1;
    el.style.setProperty('--arm',_k.toFixed(3));
    var past=(_famDrag.cy0+dy)<_famDrag.line;""",
    'drag exposes progress')

sub(u"""#famRowP .fcv.armed,#screen-match #famRowO .fcv.armed{""",
    u"""/* P743: the gradient arm - the halo grows with --arm while the card is
   in hand, so the glow is already visible on the way up rather than
   arriving in one frame at the line. .armed below is the full state. */
#famRowP .fcv.fcv-drag{--arm:0}
#famRowP .fcv.fcv-drag:not(.fcv-blocked):not(.spent){
  scale:calc(1 + 0.09*var(--arm));
  filter:drop-shadow(0 0 calc(0.8cqw*var(--arm)) rgba(255,236,170,var(--arm)))
    drop-shadow(0 0 calc(3.4cqw*var(--arm)) rgba(255,200,85,calc(0.95*var(--arm))))
    drop-shadow(0 0.9cqw 1.3cqw rgba(10,6,2,.5))
    brightness(calc(1 + 0.22*var(--arm)))}
/* blocked greys IN, on the same value */
#famRowP .fcv.fcv-drag.fcv-blocked{
  filter:saturate(calc(1 - 0.82*var(--arm))) brightness(calc(1 - 0.5*var(--arm)))
    drop-shadow(0 0.25cqw 0.3cqw rgba(10,6,2,.5))}
#famWhyNot{transition:opacity .22s ease}
#famRowP .fcv.armed,#screen-match #famRowO .fcv.armed{""",
    'gradient CSS')

# ── 4. a spent card is spent, mid-drag included ──
sub(u"""#famRowP .fcv.spent{filter:saturate(.25) brightness(.55)""",
    u"""/* P743: spent WINS over the drag's own filters - a card with no uses
   left must read spent in the hand at all times (Denis) */
#famRowP .fcv.spent,#famRowP .fcv.spent.fcv-drag{filter:saturate(.18) brightness(.48)""",
    'spent wins')

sub(u"""function _famCanPlay(i){
  if(!G||!G.pF||!G.pF[i])return false;""",
    u"""function _famCanPlay(i){
  if(!G||!G.pF||!G.pF[i])return false;
  /* P743: a spent card cannot even start a drag - it is out of uses and
     the hand says so */
  if(G.pF[i].charges<=0)return false;""",
    'spent cannot drag')

# ── 5. the title's outline is its own colour ──
sub(u"""  /* P741: brighter, with the ink outline the game's own headings wear -
     stroke first so the letterform stays crisp on the dark wood */
  -webkit-text-stroke:0.55cqw #1a1008;paint-order:stroke fill;
  text-shadow:0 0.35cqw 0.5cqw rgba(8,4,2,.85);""",
    u"""  /* P741/P743: thinner, and the outline is the TITLE'S OWN colour taken
     darker and more saturated rather than black (Denis) - so a jade card
     is outlined in deep jade, an amber one in burnt amber. */
  -webkit-text-stroke:0.3cqw color-mix(in srgb,var(--cft-a,#f0c860) 62%,#1a0d02);
  paint-order:stroke fill;
  text-shadow:0 0.3cqw 0.45cqw rgba(8,4,2,.8);""",
    'title outline takes its colour')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d edits' % n)
