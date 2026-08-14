# -*- coding: utf-8 -*-
"""P721: the table props arrive with the table.

Denis: "it takes a looong while for the table props to show when landing on
a match." Two causes, two fixes:

1. The dress loaded the raw PNG masters while a full optimized/ set of
   webps sat unreferenced beside them - the P712 title-master bug, prop
   edition. Both reference sites (the prop <img> and the shadow painter's
   silhouette job) point at the webps now. The randomly-picked per-match
   set drops from ~hundreds of KB of png to a fraction of that.

2. Even optimized, a cold entry fetched the picked set at dress time. The
   whole prop kit now preloads during boot idle - the same requestIdle beat
   the D3X warm uses - so by the first match the images come from cache.
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


sub(u"    img.src=PP+q.n+'.png?v=2';",
    u"    img.src=PP+'optimized/'+q.n+'_opt.webp';/* P721: the webps existed, unreferenced */",
    'prop img -> optimized')

sub(u"    _jobs.push({src:PP+q.n+'.png?v=2',",
    u"    _jobs.push({src:PP+'optimized/'+q.n+'_opt.webp',/* P721 */",
    'prop shadow job -> optimized')

sub(u"(function(){\n"
    u"  function warm(){try{if(window.D3X&&D3X.boot)D3X.boot();}catch(e){}}\n"
    u"  window.addEventListener('load',function(){\n"
    u"    if(window.requestIdleCallback)requestIdleCallback(warm,{timeout:2500});\n"
    u"    else setTimeout(warm,600);\n"
    u"  });\n"
    u"})();",
    u"(function(){\n"
    u"  function warm(){try{if(window.D3X&&D3X.boot)D3X.boot();}catch(e){}}\n"
    u"  /* P721: the prop kit rides the same idle beat - by the first match the\n"
    u"     dress finds every silhouette in cache instead of fetching the picked\n"
    u"     set while the player watches a bare table. ~38 small webps, trickled\n"
    u"     two at a time so the preload never competes with anything urgent. */\n"
    u"  function warmProps(){\n"
    u"    try{\n"
    u"      var PPw=(window.FK_ART&&FK_ART.props)||'Art/Assets/Match/Commoner/Props/';\n"
    u"      var names=['bag','bottle','bottle01','bottle02','bowl_dirty','bowl_full',\n"
    u"        'bread','candle','cauldron','cheese','coins','cork','fork','grapes',\n"
    u"        'jug','key','knife','lantern','loaf','mug01','mug_empty','olives',\n"
    u"        'package','plank','plateMetal','plateWood','pouch','pouch02','pouch03',\n"
    u"        'sausages','singleCoin','singleCoin_02','spoon','towel','towel01',\n"
    u"        'towel02','ustensils','wine'];\n"
    u"      var qi=0;\n"
    u"      (function next(){\n"
    u"        for(var b=0;b<2&&qi<names.length;b++,qi++){\n"
    u"          var im=new Image();im.src=PPw+'optimized/'+names[qi]+'_opt.webp';\n"
    u"        }\n"
    u"        if(qi<names.length)setTimeout(next,120);\n"
    u"      })();\n"
    u"    }catch(e){}\n"
    u"  }\n"
    u"  window.addEventListener('load',function(){\n"
    u"    if(window.requestIdleCallback){requestIdleCallback(warm,{timeout:2500});requestIdleCallback(warmProps,{timeout:4000});}\n"
    u"    else{setTimeout(warm,600);setTimeout(warmProps,1500);}\n"
    u"  });\n"
    u"})();",
    'prop kit preloads on idle')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d edits' % n)
