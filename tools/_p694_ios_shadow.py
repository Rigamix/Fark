# -*- coding: utf-8 -*-
"""P694: dice shadows reach the iPhone - the offscreen-shadow trick dies.

Denis, full phone screenshot: props dressed, 3D dice rendering, and not one
dice shadow - while the same build measures full shadow ink in Chromium
emulation, patron and boss alike. The divergence is the fallback path itself:
pre-Safari-18 has no ctx.filter, so the painter drew the hull ENTIRELY OFF
THE CANVAS and let only its cast shadow (shadowBlur/shadowOffsetY) land in
place. WebKit's accelerated canvas culls primitives that lie wholly outside
the surface - and culls their shadows with them. Chromium paints the detached
shadow; the iPhone paints nothing. Exactly the reported split.

The replacement casts nothing: three concentric fills of the same hull,
scaled about its centroid (1.0 / 1.14 / 1.3) at falling alpha - a fake blur
from primitives every canvas on earth rasterises the same way. The capable
path (real ctx.filter blur, Safari 18+, all Chromium) is untouched.
"""
import io, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'fark_proto.html')
s = io.open(P, encoding='utf-8', newline='').read()

old = (u"  }else{\n"
       u"    var _d=1;try{var _t=x.getTransform&&x.getTransform();if(_t&&_t.a)_d=_t.a;}catch(e){}\n"
       u"    var _off=(x.canvas.height/_d)+80;\n"
       u"    x.shadowColor=_col;x.shadowBlur=_bl*2;\n"
       u"    x.shadowOffsetX=0;x.shadowOffsetY=_off*_d;\n"
       u"    x.fillStyle=_col;\n"
       u"    x.beginPath();\n"
       u"    hull.forEach(function(p2,i3){\n"
       u"      var hx=scx+p2[0],hy=scy+p2[1]-_off;\n"
       u"      if(i3)x.lineTo(hx,hy);else x.moveTo(hx,hy);\n"
       u"    });\n"
       u"    x.closePath();x.fill();")
new = (u"  }else{\n"
       u"    /* P694: NO cast-shadow trick. The old fallback drew the hull wholly\n"
       u"       off-canvas and let only its shadow land - WebKit's accelerated\n"
       u"       canvas culls offscreen primitives WITH their shadows, so iPhones\n"
       u"       (pre-Safari-18, no ctx.filter either) painted nothing at all while\n"
       u"       Chromium painted the detached shadow. Denis's phone screenshot vs\n"
       u"       the emulation measurements were exactly that split. Three\n"
       u"       concentric fills fake the blur from primitives every canvas\n"
       u"       rasterises identically. */\n"
       u"    x.fillStyle=_col;\n"
       u"    var _passes=[[1.0,0.55],[1.14,0.30],[1.30,0.15]];\n"
       u"    for(var _pi=0;_pi<3;_pi++){\n"
       u"      var _sc2=_passes[_pi][0];\n"
       u"      x.globalAlpha=(a>1?1:a)*_passes[_pi][1];\n"
       u"      x.beginPath();\n"
       u"      hull.forEach(function(p2,i3){\n"
       u"        var hx=scx+p2[0]*_sc2,hy=scy+p2[1]*_sc2;\n"
       u"        if(i3)x.lineTo(hx,hy);else x.moveTo(hx,hy);\n"
       u"      });\n"
       u"      x.closePath();x.fill();\n"
       u"    }")
c = s.count(old)
if c != 1:
    sys.exit('ANCHOR x%d (need 1)' % c)
io.open(P, 'w', encoding='utf-8', newline='').write(s.replace(old, new))
print('  ok  P694 portable soft shadow')
