# -*- coding: utf-8 -*-
"""P731: the selection glow learns direction and taper - defaults neutral.

Three new GLOW fields (sx, sy, dy - defaults 1/1/0, so today's look is
byte-identical until something sets them): the SOFT pass's silhouette can
be stretched horizontally/vertically and biased up or down, while the
bright rim, the crisp line and the punch-out stay hull-true. A taller,
upward-biased soft pass is exactly the reference look Denis pointed at -
tight at the base, tall above. The lab drives the dials live."""
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


sub(u"  GLOW:{soft:10, rim:3.5, rimPasses:5, softPasses:1, line:2.4, grow:1.004, clear:0.7, strength:0.78,\n"
    u"        fbWide:1.35, fbCross:0.40, fbA0:0.11, fbA1:0.30},",
    u"  GLOW:{soft:10, rim:3.5, rimPasses:5, softPasses:1, line:2.4, grow:1.004, clear:0.7, strength:0.78,\n"
    u"        fbWide:1.35, fbCross:0.40, fbA0:0.11, fbA1:0.30,\n"
    u"        /* P731: the SOFT pass can stretch and lean - sx/sy scale the\n"
    u"           silhouette, dy biases it vertically. 1/1/0 = today's look\n"
    u"           exactly; the rim, line and punch-out stay hull-true. */\n"
    u"        sx:1, sy:1, dy:0},",
    'GLOW gains sx/sy/dy')

sub(u"    var trace=function(ctx,hull,shrink,dy){\n"
    u"      var cx=0,cy=0;\n"
    u"      hull.forEach(function(p){cx+=p[0];cy+=p[1];});\n"
    u"      cx/=hull.length;cy/=hull.length;\n"
    u"      ctx.beginPath();\n"
    u"      hull.forEach(function(p,i){\n"
    u"        var dx=p[0]-cx,dyy=p[1]-cy,L=Math.sqrt(dx*dx+dyy*dyy)||1;\n"
    u"        var k=shrink?Math.max(0,(L-shrink))/L:1;\n"
    u"        var px=cx+dx*k,py=cy+dyy*k+(dy||0);\n"
    u"        if(i)ctx.lineTo(px,py);else ctx.moveTo(px,py);\n"
    u"      });\n"
    u"      ctx.closePath();\n"
    u"    };",
    u"    var trace=function(ctx,hull,shrink,dy,sx,sy){\n"
    u"      var cx=0,cy=0;\n"
    u"      hull.forEach(function(p){cx+=p[0];cy+=p[1];});\n"
    u"      cx/=hull.length;cy/=hull.length;\n"
    u"      ctx.beginPath();\n"
    u"      hull.forEach(function(p,i){\n"
    u"        var dx=p[0]-cx,dyy=p[1]-cy,L=Math.sqrt(dx*dx+dyy*dyy)||1;\n"
    u"        var k=shrink?Math.max(0,(L-shrink))/L:1;\n"
    u"        /* P731: sx/sy stretch, dy leans - undefined means 1/1/0 */\n"
    u"        var px=cx+dx*k*(sx||1),py=cy+dyy*k*(sy||1)+(dy||0);\n"
    u"        if(i)ctx.lineTo(px,py);else ctx.moveTo(px,py);\n"
    u"      });\n"
    u"      ctx.closePath();\n"
    u"    };",
    'trace takes stretch + lean')

sub(u"      /* the wide, soft falloff */\n"
    u"      gx.filter='blur('+G.soft+'px)';\n"
    u"      for(var sp=0;sp<(G.softPasses||1);sp++)\n"
    u"        sel.forEach(function(h){trace(gx,h,0);gx.fill();});",
    u"      /* the wide, soft falloff - P731: this pass alone stretches/leans */\n"
    u"      gx.filter='blur('+G.soft+'px)';\n"
    u"      for(var sp=0;sp<(G.softPasses||1);sp++)\n"
    u"        sel.forEach(function(h){trace(gx,h,0,G.dy,G.sx,G.sy);gx.fill();});",
    'soft pass goes directional')

sub(u"      var RINGS=10, widest=Math.max(6,G.soft*(G.fbWide||2));\n"
    u"      gx.lineJoin='round'; gx.lineCap='round';\n"
    u"      for(var ri=0;ri<RINGS;ri++){\n"
    u"        var f=ri/(RINGS-1);/* 0 widest and softest, 1 tightest and brightest */\n"
    u"        gx.strokeStyle=(f<(G.fbCross===undefined?0.55:G.fbCross))?SOFT:COL;\n"
    u"        gx.lineWidth=widest*(1-f)+2;\n"
    u"        gx.globalAlpha=(G.fbA0===undefined?0.09:G.fbA0)+(G.fbA1===undefined?0.23:G.fbA1)*f;\n"
    u"        sel.forEach(function(h){trace(gx,h,0);gx.stroke();});\n"
    u"      }",
    u"      var RINGS=10, widest=Math.max(6,G.soft*(G.fbWide||2));\n"
    u"      gx.lineJoin='round'; gx.lineCap='round';\n"
    u"      for(var ri=0;ri<RINGS;ri++){\n"
    u"        var f=ri/(RINGS-1);/* 0 widest and softest, 1 tightest and brightest */\n"
    u"        gx.strokeStyle=(f<(G.fbCross===undefined?0.55:G.fbCross))?SOFT:COL;\n"
    u"        gx.lineWidth=widest*(1-f)+2;\n"
    u"        gx.globalAlpha=(G.fbA0===undefined?0.09:G.fbA0)+(G.fbA1===undefined?0.23:G.fbA1)*f;\n"
    u"        /* P731: the widest rings stretch fully, the tight ones stay\n"
    u"           hull-true - the fallback's version of soft-only leaning */\n"
    u"        sel.forEach(function(h){trace(gx,h,0,(G.dy||0)*(1-f),1+((G.sx||1)-1)*(1-f),1+((G.sy||1)-1)*(1-f));gx.stroke();});\n"
    u"      }",
    'fallback rings go directional')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d edits' % n)
