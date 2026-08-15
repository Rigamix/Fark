# -*- coding: utf-8 -*-
"""P732 (A3b): Denis's approved look, baked from his lab numbers.

The accidental-look chase ends: every number below is from the copyLook
export Denis approved in the lab (2026-08-15).

- Vignette 61% at the edges, bright pool to 48%, no extra centre light -
  a new #matchLookVig in the z:0 art band (after props, before the pause
  button), so art and props darken while every later sibling - UI, rows,
  the appended dice canvas - paints above by DOM order.
- Painted shadows 4% deeper (#matchShadows brightness .96).
- SIDEDIM_MAX 0.5 -> 0.82: stronger side dim...
- ...masked by a vertical gradient (SIDEDIM_GRAD 0.32): the dim fades
  toward each face's base - the bounce-light read from the reference.
  Scoring cell repaint unchanged, so top faces stay untouched.
- Key light 0.38 -> 0.524, plus a warm bounce fill (0xffe8c8 at 0.12)
  from below. Ambient stays 0.72 (his export matches current).
- GLOW: soft 11, rim 3, line 3.2, strength 0.91, sx 1.14, sy 1.24 -
  the taller, wider soft halo via P731's directional fields.
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


# 1) the vignette element, in the art band
sub(u"""<div id="matchProps"></div>
<div id="matchPause" onclick="SFX.nav();showQuitConfirm()">""",
    u"""<div id="matchProps"></div>
<div id="matchLookVig"></div><!-- P732: the approved look's vignette - art band, under everything interactive -->
<div id="matchPause" onclick="SFX.nav();showQuitConfirm()">""",
    'vignette element')

sub(u"#matchProps{position:absolute;inset:0;z-index:0;pointer-events:none}",
    u"#matchProps{position:absolute;inset:0;z-index:0;pointer-events:none}\n"
    u"/* P732: THE LOOK's vignette, from Denis's lab numbers (61%% edge\n"
    u"   darkness, pool to 48%%). Same z:0 band as the art it darkens; every\n"
    u"   later sibling (pause, HUD, rows, the appended canvas) paints above\n"
    u"   by DOM order. NOT #matchVignette - that is the red danger pulse. */\n"
    u"#matchLookVig{position:absolute;inset:0;z-index:0;pointer-events:none;\n"
    u"  mix-blend-mode:multiply;\n"
    u"  background:radial-gradient(ellipse at 50%% 46%%, rgba(16,10,4,0) 48%%, rgba(16,10,4,.61) 100%%)}",
    'vignette CSS')

# 2) painted shadows 4% deeper
sub(u"#matchShadows{",
    u"#matchShadows{filter:brightness(.96);/* P732: shadow depth, per the lab */",
    'shadow depth')

# 3) side dim strength + the gradient mask constant
sub(u"SIDEDIM_RAMP:{delay:0,dur:350,steps:8},/* P720: twice as fast, lands WITH the die */",
    u"SIDEDIM_RAMP:{delay:0,dur:350,steps:8},/* P720: twice as fast, lands WITH the die */\n"
    u"  /* P732: the dim is STRONGER but fades toward each face's base - the\n"
    u"     bounce-light read Denis approved. GRAD is the fraction of the dim\n"
    u"     masked away at the bottom of each cell (vertical, all dice). */\n"
    u"  SIDEDIM_GRAD:0.32,",
    'SIDEDIM_GRAD constant')

sub(u"SIDEDIM_MAX:0.5,",
    u"SIDEDIM_MAX:0.82,/* P732: 0.5 -> 0.82, masked by SIDEDIM_GRAD */",
    'SIDEDIM_MAX 0.82')

# 4) _dimMap: per-cell vertical gradient instead of the flat fill
sub(u"""    var cv=document.createElement('canvas');cv.width=w;cv.height=h;
    var cx=cv.getContext('2d');
    cx.drawImage(im,0,0,w,h);
    cx.globalCompositeOperation='multiply';
    cx.fillStyle=col;
    cx.fillRect(0,0,w,h);
    cx.globalCompositeOperation='source-over';""",
    u"""    var cv=document.createElement('canvas');cv.width=w;cv.height=h;
    var cx=cv.getContext('2d');
    cx.drawImage(im,0,0,w,h);
    cx.globalCompositeOperation='multiply';
    /* P732: the dim fades toward each face's BASE (SIDEDIM_GRAD masks
       that fraction of it) - a per-cell vertical gradient of the multiply
       colour rather than one flat fill. The scoring cell is repainted
       bright below exactly as before, so top faces are untouched. */
    var _gd=this.SIDEDIM_GRAD||0;
    var _colAt=function(kk){return 'rgb('+fc.map(function(f){
      return Math.round(255*(1-(1-f)*kk));}).join(',')+')';};
    var _cw=w/3,_ch=h/2;
    for(var _cy=0;_cy<2;_cy++)for(var _cx2=0;_cx2<3;_cx2++){
      var _x0=_cx2*_cw,_y0=_cy*_ch;
      var _gr=cx.createLinearGradient(0,_y0,0,_y0+_ch);
      _gr.addColorStop(0,_colAt(kq));
      _gr.addColorStop(1,_colAt(kq*(1-_gd)));
      cx.fillStyle=_gr;cx.fillRect(_x0,_y0,_cw,_ch);
    }
    cx.globalCompositeOperation='source-over';""",
    'dim gradient mask')

# 5) the light rig: key up, bounce fill added
sub(u"    var key=new THREE.DirectionalLight(0xffffff,0.38);key.position.set(0,0.33,0.94);sc.add(key);\n"
    u"    sc.add(new THREE.AmbientLight(0xffffff,0.72));",
    u"    /* P732: key 0.38 -> 0.524 and a warm bounce fill from below, per\n"
    u"       Denis's approved lab numbers. Ambient stays 0.72 (matched). */\n"
    u"    var key=new THREE.DirectionalLight(0xffffff,0.524);key.position.set(0,0.33,0.94);sc.add(key);\n"
    u"    sc.add(new THREE.AmbientLight(0xffffff,0.72));\n"
    u"    var bounce=new THREE.DirectionalLight(0xffe8c8,0.12);bounce.position.set(0,-1,0.6);sc.add(bounce);",
    'light rig')

# 6) GLOW numbers
sub(u"  GLOW:{soft:10, rim:3.5, rimPasses:5, softPasses:1, line:2.4, grow:1.004, clear:0.7, strength:0.78,\n"
    u"        fbWide:1.35, fbCross:0.40, fbA0:0.11, fbA1:0.30,",
    u"  /* P732: the approved numbers - stronger, taller, wider soft halo */\n"
    u"  GLOW:{soft:11, rim:3, rimPasses:5, softPasses:1, line:3.2, grow:1.004, clear:0.7, strength:0.91,\n"
    u"        fbWide:1.35, fbCross:0.40, fbA0:0.11, fbA1:0.30,",
    'GLOW numbers')

sub(u"        sx:1, sy:1, dy:0},",
    u"        sx:1.14, sy:1.24, dy:0},/* P732 */",
    'GLOW direction numbers')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d edits' % n)
