# -*- coding: utf-8 -*-
"""P667: the die-sparkle engine, once instead of three times.

Denis: "check all effects are using the same latest engine with the better looks
(the one that adds particles, etc to offered dice on a new run)"

THE ANSWER WAS NO, and here is the census that says so. The sparkle band on the
new-run dice offer exists in the file THREE times:

  .nrparts       the new-run offer     reads D3.SPARK, star/diamond/dot
  .stparts       the shop stand        reads D3.SPARK, star/diamond/dot
  #fcOv .fcp     the feats overlay     reads NOTHING, star/dot, gold hardcoded

The first two spawners are line-for-line identical apart from the spread being
in chip-widths rather than pixels. The third is an older builder that predates
the shape table: it picks star-or-dot on a coin flip, has no diamond at all -
and the CSS block behind it never had a .pdiamond rule, so if it ever asked for
one the particle would have rendered as a bare square.

The CSS was copied three times too - same background, same drop-shadow glow,
same nrSpark keyframe, three selectors. Only the positioning ever differed, and
that stays per-site because that is the part that is genuinely different.

SO: one _sparkBand(host, spark, opts), one span rule, three callers. `spark` is
the same {c, shape} record D3.SPARK already holds for every material, and either
field may be an array when a caller wants a mix - which is how the feats
overlay keeps its two golds while joining the shape vocabulary the dice use.

WHAT CHANGES ON SCREEN: only the feats overlay, and only in the direction Denis
asked for - it gains the diamond and the size-by-shape the dice have had since
the shape table was written. The offer and the shop are untouched, by
construction: their call passes exactly the arguments their own loop used.
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


SPAN_RULE = (u"position:absolute;left:0;top:0;background:var(--pc,#ffd98a);\n"
             u"  filter:drop-shadow(0 0 3px var(--pc,#ffd98a));opacity:0;animation:nrSpark 2.6s linear infinite}")

# ── 1. one span rule for all three bands ────────────────────────────────
sub(u".nrparts span{" + SPAN_RULE + u"\n"
    u".nrparts span.pdot{border-radius:50%}\n"
    u".nrparts span.pstar{clip-path:polygon(50% 0,61% 39%,100% 50%,61% 61%,50% 100%,39% 61%,0 50%,39% 39%)}\n"
    u".nrparts span.pdiamond{clip-path:polygon(50% 0,100% 50%,50% 100%,0 50%)}",
    u"/* P667: ONE SPARK BAND, three hosts. This rule was copied once per site -\n"
    u"   same background, same glow, same nrSpark keyframe - and the #fcOv copy was\n"
    u"   missing .pdiamond entirely, so that band could never have drawn one. Only\n"
    u"   the positioning is per-site now, because that is the only part that ever\n"
    u"   genuinely differed. */\n"
    u".nrparts span,.stparts span,#fcOv .fcp span{" + SPAN_RULE + u"\n"
    u".nrparts span.pdot,.stparts span.pdot,#fcOv .fcp span.pdot{border-radius:50%}\n"
    u".nrparts span.pstar,.stparts span.pstar,#fcOv .fcp span.pstar{clip-path:polygon(50% 0,61% 39%,100% 50%,61% 61%,50% 100%,39% 61%,0 50%,39% 39%)}\n"
    u".nrparts span.pdiamond,.stparts span.pdiamond,#fcOv .fcp span.pdiamond{clip-path:polygon(50% 0,100% 50%,50% 100%,0 50%)}",
    'P667 the one span rule')

sub(u".stparts span{" + SPAN_RULE + u"\n"
    u".stparts span.pdot{border-radius:50%}\n"
    u".stparts span.pstar{clip-path:polygon(50% 0,61% 39%,100% 50%,61% 61%,50% 100%,39% 61%,0 50%,39% 39%)}\n"
    u".stparts span.pdiamond{clip-path:polygon(50% 0,100% 50%,50% 100%,0 50%)}\n",
    u"/* P667: the .stparts copy of the span rule folded into the shared one above. */\n",
    'P667 drop the shop copy')

sub(u"#fcOv .fcp span{" + SPAN_RULE + u"\n"
    u"#fcOv .fcp span.pdot{border-radius:50%}\n"
    u"#fcOv .fcp span.pstar{clip-path:polygon(50% 0,61% 39%,100% 50%,61% 61%,50% 100%,39% 61%,0 50%,39% 39%)}\n",
    u"/* P667: the #fcOv copy folded into the shared rule above - and it gains the\n"
    u"   .pdiamond it never had. */\n",
    'P667 drop the feats copy')

# ── 2. the one spawner ──────────────────────────────────────────────────
sub(u"function spawnPixelSparks(el,count){",
    u"/* P667: THE SPARK BAND, once. The rising glitter under a zoomed die on the\n"
    u"   new-run offer, on a shop stand and over the feats overlay was three copies\n"
    u"   of this loop - two identical, the third an older one that predated the\n"
    u"   shape table and could only draw stars and dots.\n"
    u"   `spark` is the record D3.SPARK already holds per material, {c, shape}.\n"
    u"   Either field may be an ARRAY when a caller wants a mix rather than one\n"
    u"   material's look - which is how the feats overlay keeps its two golds while\n"
    u"   drawing the same shapes the dice do.\n"
    u"     host    the .nrparts / .stparts / .fcp element (emptied and refilled)\n"
    u"     opts    {count, spread, drift} - spread and drift in px, because each\n"
    u"             host sits in a differently scaled box and only the caller knows\n"
    u"   Returns the markup as well as filling the host, so a caller building a\n"
    u"   string with innerHTML (the feats overlay does) can use the same source. */\n"
    u"function _sparkBand(host,spark,opts){\n"
    u"  opts=opts||{};spark=spark||{};\n"
    u"  var pick=function(v){return Array.isArray(v)?v[(Math.random()*v.length)|0]:v;};\n"
    u"  var count=opts.count||12, spread=opts.spread||46, drift=opts.drift||26;\n"
    u"  var out='';\n"
    u"  for(var i=0;i<count;i++){\n"
    u"    var sh=pick(spark.shape)||'dot', c=pick(spark.c)||'#ffd98a', w,h,cls;\n"
    u"    if(sh==='star'){w=5+Math.random()*4;h=w;cls='pstar';}\n"
    u"    else if(sh==='diamond'){w=3+Math.random()*3;h=w*(1.5+Math.random()*0.5);cls='pdiamond';}\n"
    u"    else{w=2+Math.random()*3;h=w;cls='pdot';}\n"
    u"    out+='<span class=\"'+cls+'\" style=\"--pc:'+c+';'\n"
    u"      +'--px:'+((Math.random()*2-1)*spread).toFixed(0)+'px;'\n"
    u"      +'--dx:'+((Math.random()*2-1)*drift).toFixed(0)+'px;'\n"
    u"      +'width:'+w.toFixed(1)+'px;height:'+h.toFixed(1)+'px;'\n"
    u"      +'animation-duration:'+(2+Math.random()*1.6).toFixed(2)+'s;'\n"
    u"      +'animation-delay:'+(Math.random()*2.4).toFixed(2)+'s\"></span>';\n"
    u"  }\n"
    u"  if(host)host.innerHTML=out;\n"
    u"  return out;\n"
    u"}\n"
    u"function spawnPixelSparks(el,count){",
    'P667 the one spawner')

# ── 3. the three callers ────────────────────────────────────────────────
sub(u"  var pts=die.querySelector('.nrparts');\n"
    u"  if(pts){pts.innerHTML='';\n"
    u"    for(var p2=0;p2<12;p2++){\n"
    u"      var sp=document.createElement('span');\n"
    u"      var w2,h2;\n"
    u"      if(spk.shape==='star'){w2=5+Math.random()*4;h2=w2;sp.className='pstar';}\n"
    u"      else if(spk.shape==='diamond'){w2=3+Math.random()*3;h2=w2*(1.5+Math.random()*0.5);sp.className='pdiamond';}\n"
    u"      else{w2=2+Math.random()*3;h2=w2;sp.className='pdot';}\n"
    u"      sp.style.cssText='--pc:'+spk.c+';--px:'+((Math.random()*2-1)*46).toFixed(0)+'px;--dx:'+((Math.random()*2-1)*26).toFixed(0)+'px;'\n"
    u"        +'width:'+w2.toFixed(1)+'px;height:'+h2.toFixed(1)+'px;'\n"
    u"        +'animation-duration:'+(2+Math.random()*1.6).toFixed(2)+'s;animation-delay:'+(Math.random()*2.4).toFixed(2)+'s';\n"
    u"      pts.appendChild(sp);\n"
    u"    }}",
    u"  /* P667: the band this call draws is the one every other site now draws. The\n"
    u"     arguments are exactly what this loop used, so nothing here changed look. */\n"
    u"  _sparkBand(die.querySelector('.nrparts'),spk,{count:12,spread:46,drift:26});",
    'P667 caller: the new-run offer')

sub(u"  var pw=stand.offsetWidth*0.4;\n"
    u"  for(var p2=0;p2<12;p2++){\n"
    u"    var sp=document.createElement('span');\n"
    u"    var w2,h2;\n"
    u"    if(spk.shape==='star'){w2=5+Math.random()*4;h2=w2;sp.className='pstar';}\n"
    u"    else if(spk.shape==='diamond'){w2=3+Math.random()*3;h2=w2*(1.5+Math.random()*0.5);sp.className='pdiamond';}\n"
    u"    else{w2=2+Math.random()*3;h2=w2;sp.className='pdot';}\n"
    u"    sp.style.cssText='--pc:'+spk.c+';--px:'+((Math.random()*2-1)*pw).toFixed(0)+'px;--dx:'+((Math.random()*2-1)*pw*0.55).toFixed(0)+'px;'\n"
    u"      +'width:'+w2.toFixed(1)+'px;height:'+h2.toFixed(1)+'px;'\n"
    u"      +'animation-duration:'+(2+Math.random()*1.6).toFixed(2)+'s;animation-delay:'+(Math.random()*2.4).toFixed(2)+'s';\n"
    u"    pts.appendChild(sp);\n"
    u"  }",
    u"  var pw=stand.offsetWidth*0.4;\n"
    u"  /* P667: same band, same numbers this loop used - spread in chip widths\n"
    u"     because the stand is tiny then zoomed 2.3x. */\n"
    u"  _sparkBand(pts,spk,{count:12,spread:pw,drift:pw*0.55});",
    'P667 caller: the shop stand')

sub(u"      var parts='';\n"
    u"      for(var i=0;i<14+(n-1)*4;i++){\n"
    u"        var w2=(2.5+Math.random()*4).toFixed(1);\n"
    u"        parts+='<span class=\"'+(Math.random()<0.4?'pstar':'pdot')+'\" style=\"--pc:'+(Math.random()<0.5?'#e1a755':'#ffd98a')+';'\n"
    u"          +'--px:'+((Math.random()*2-1)*spread).toFixed(0)+'px;--dx:'+((Math.random()*2-1)*30).toFixed(0)+'px;'\n"
    u"          +'width:'+w2+'px;height:'+w2+'px;'\n"
    u"          +'animation-duration:'+(2+Math.random()*1.6).toFixed(2)+'s;animation-delay:'+(Math.random()*2).toFixed(2)+'s\"></span>';\n"
    u"      }",
    u"      /* P667: THE ONE THAT WAS BEHIND. This band had its own builder, written\n"
    u"         before the shape table: a coin flip between star and dot, no diamond\n"
    u"         at all - and the CSS behind it had no .pdiamond rule either, so it\n"
    u"         could not have drawn one. It goes through the shared band now, which\n"
    u"         is where the diamond and the size-by-shape come from. The two golds\n"
    u"         stay: they are this overlay's own colour, not a material's. */\n"
    u"      var parts=_sparkBand(null,{c:['#e1a755','#ffd98a'],\n"
    u"                                 shape:['star','star','diamond','dot','dot']},\n"
    u"                           {count:14+(n-1)*4,spread:spread,drift:30});",
    'P667 caller: the feats overlay')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('\n%d edits' % n)
