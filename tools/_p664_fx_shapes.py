# -*- coding: utf-8 -*-
"""P664: the particle system learns the game's own diamond and star, and the
activation glow gets the strength Denis's reference has.

Denis: "The glow around the card being activated should be much stronger, the
particles should match the diamond shapes we have on the initial offered dice
(for example). This should all be possible in engine, find a way."

IT IS POSSIBLE IN ENGINE, and the shapes already exist - just not in this
engine. The night-roll offer, the shop stands and the focus overlay all draw
their sparkles as DOM spans with a clip-path polygon (.pdiamond, .pstar). FX
draws pooled canvas particles and only knew fillRect. So neither had to be
invented: the polygons below are the SAME coordinates as those clip-paths,
transcribed once into a canvas path.

  diamond  polygon(50% 0, 100% 50%, 50% 100%, 0 50%)
  star     polygon(50% 0, 61% 39%, 100% 50%, 61% 61%, 50% 100%, 39% 61%, 0 50%, 39% 39%)

ONE SHAPE FIELD, NOT A NEW EMITTER. FX.emit takes `shape:'diamond'|'star'` and
defaults to the square it always drew, so every existing caller is untouched and
nothing had to be forked. The draw path costs one switch per particle.

AND THE GLOW. spawnCardBurst threw 26 small motes at 3-4px. The reference is a
dense gold bloom with big slow diamonds turning in it, so: more particles,
bigger, most of them diamonds with a few stars, a longer life on the slow ones,
and rotation on all of them - a diamond that does not turn reads as a lozenge.
The numbers are one table at the top of the function rather than scattered
through three loops, because this is the thing Denis will want to tune.
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
        sys.exit('ANCHOR x%d (need 1) for %s:\n  %r' % (c, label, old[:120]))
    s = s.replace(old, new)
    n += 1
    print('  ok  %s' % label)


# ── 1. the shapes, drawn from the same polygons the CSS uses ─────────────
sub(u"      var k=p.fade?Math.max(0,p.life/p.max):1;\n"
    u"      ctx.globalAlpha=k;\n"
    u"      ctx.fillStyle=p.color;\n"
    u"      if(p.vr){\n"
    u"        p.rot+=p.vr*dt;\n"
    u"        ctx.save();\n"
    u"        ctx.translate(p.x,p.y);\n"
    u"        ctx.rotate(p.rot);\n"
    u"        ctx.fillRect(-p.size/2,-p.size/2,p.size,p.size);\n"
    u"        ctx.restore();\n"
    u"      } else {\n"
    u"        ctx.fillRect(p.x-p.size/2,p.y-p.size/2,p.size,p.size);\n"
    u"      }\n"
    u"      anyAlive=true;",
    u"      var k=p.fade?Math.max(0,p.life/p.max):1;\n"
    u"      ctx.globalAlpha=k;\n"
    u"      ctx.fillStyle=p.color;\n"
    u"      /* P664: SHAPES. The square is still the default, so every existing\n"
    u"         caller draws exactly what it drew before. */\n"
    u"      if(p.shape&&p.shape!=='square'){\n"
    u"        if(p.vr)p.rot+=p.vr*dt;\n"
    u"        ctx.save();\n"
    u"        ctx.translate(p.x,p.y);\n"
    u"        if(p.rot)ctx.rotate(p.rot);\n"
    u"        _fxPath(ctx,p.shape,p.size);\n"
    u"        ctx.fill();\n"
    u"        ctx.restore();\n"
    u"      } else if(p.vr){\n"
    u"        p.rot+=p.vr*dt;\n"
    u"        ctx.save();\n"
    u"        ctx.translate(p.x,p.y);\n"
    u"        ctx.rotate(p.rot);\n"
    u"        ctx.fillRect(-p.size/2,-p.size/2,p.size,p.size);\n"
    u"        ctx.restore();\n"
    u"      } else {\n"
    u"        ctx.fillRect(p.x-p.size/2,p.y-p.size/2,p.size,p.size);\n"
    u"      }\n"
    u"      anyAlive=true;",
    'P664 draw the shapes')

sub(u"  function _spawn(o){",
    u"  /* P664: THE GAME'S OWN SPARKLE SHAPES, transcribed from the clip-path\n"
    u"     polygons the DOM sparkles already use (.pdiamond and .pstar on the\n"
    u"     night-roll offer, the shop stands and the focus overlay) so a canvas\n"
    u"     particle and a DOM one are the same silhouette. Percentages there,\n"
    u"     unit coordinates here, one table either way. */\n"
    u"  var _FX_SHAPES={\n"
    u"    diamond:[[.5,0],[1,.5],[.5,1],[0,.5]],\n"
    u"    star:[[.5,0],[.61,.39],[1,.5],[.61,.61],[.5,1],[.39,.61],[0,.5],[.39,.39]]\n"
    u"  };\n"
    u"  function _fxPath(ctx,shape,size){\n"
    u"    var pts=_FX_SHAPES[shape];if(!pts)return;\n"
    u"    ctx.beginPath();\n"
    u"    for(var i=0;i<pts.length;i++){\n"
    u"      var x=(pts[i][0]-0.5)*size, y=(pts[i][1]-0.5)*size;\n"
    u"      if(i===0)ctx.moveTo(x,y);else ctx.lineTo(x,y);\n"
    u"    }\n"
    u"    ctx.closePath();\n"
    u"  }\n"
    u"  function _spawn(o){",
    'P664 the shape table')

sub(u"        p.rot=o.rot||0; p.vr=o.vr||0;\n"
    u"        p.fade=o.fade!==false;",
    u"        p.rot=o.rot||0; p.vr=o.vr||0;\n"
    u"        p.shape=o.shape||null;/* P664: null = the square it always drew */\n"
    u"        p.fade=o.fade!==false;",
    'P664 carry the shape')

# ── 2. the burst gets the reference's weight ─────────────────────────────
i = s.find('function spawnCardBurst(el,color){')
if i < 0:
    sys.exit('spawnCardBurst not found')
j = s.find('\nfunction ', i + 10)
if j < 0:
    sys.exit('could not find the end of spawnCardBurst')

NEW_BURST = u"""function spawnCardBurst(el,color){
  if(!el||typeof FX==='undefined'||!FX.emit)return;
  var r=el.getBoundingClientRect();
  if(!(r.width>0))return;
  var cx=r.left+r.width/2, cy=r.top+r.height*0.42;
  var col=color||_cardAccent(el);
  /* P664: ONE TABLE, because this is what Denis will tune. The old burst was 26
     motes at 3-4px, which read as dust; the reference is a dense gold bloom with
     big slow diamonds turning in it. Every particle rotates - a diamond that
     does not turn reads as a lozenge. */
  var B=spawnCardBurst.tune;
  var i,a,sp;
  for(i=0;i<B.plume;i++){
    a=-Math.PI/2+(Math.random()-0.5)*1.05;
    sp=B.speed[0]+Math.random()*(B.speed[1]-B.speed[0]);
    FX.emit({x:cx+(Math.random()-0.5)*r.width*0.78,
             y:cy+(Math.random()-0.5)*r.height*0.42,
             vx:Math.cos(a)*sp, vy:Math.sin(a)*sp,
             g:150+Math.random()*90,
             life:B.life[0]+Math.random()*(B.life[1]-B.life[0]),
             size:B.size[0]+Math.random()*(B.size[1]-B.size[0]),
             rot:Math.random()*Math.PI, vr:(Math.random()-0.5)*7,
             shape:(Math.random()<B.starShare?'star':'diamond'),
             color:col});
  }
  /* the slow motes that hang and drift - the ones that sell the bloom */
  for(i=0;i<B.motes;i++){
    a=-Math.PI/2+(Math.random()-0.5)*1.6;
    FX.emit({x:cx+(Math.random()-0.5)*r.width*0.9, y:cy,
             vx:Math.cos(a)*30, vy:Math.sin(a)*46, g:26,
             life:B.moteLife[0]+Math.random()*(B.moteLife[1]-B.moteLife[0]),
             size:B.moteSize[0]+Math.random()*(B.moteSize[1]-B.moteSize[0]),
             rot:Math.random()*Math.PI, vr:(Math.random()-0.5)*3.4,
             shape:'diamond', color:col});
  }
  /* and a ring that pushes out from the card's own edge, so the burst reads as
     coming OFF the card rather than being sprayed over it */
  for(i=0;i<B.ring;i++){
    a=(i/B.ring)*Math.PI*2;
    FX.emit({x:cx+Math.cos(a)*r.width*0.42, y:cy+Math.sin(a)*r.height*0.34,
             vx:Math.cos(a)*B.ringSpeed, vy:Math.sin(a)*B.ringSpeed-40, g:120,
             life:0.5+Math.random()*0.4, size:B.size[0],
             rot:a, vr:(Math.random()-0.5)*6,
             shape:'diamond', color:col});
  }
}
spawnCardBurst.tune={plume:44,motes:14,ring:12,
  speed:[80,250], life:[0.6,1.25], size:[6,13],
  moteLife:[1.0,1.9], moteSize:[7,15], ringSpeed:120, starShare:0.22};
"""
s = s[:i] + NEW_BURST + s[j + 1:]
n += 1
print('  ok  P664 the burst gets its weight')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('\n%d edits' % n)
