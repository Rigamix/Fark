# -*- coding: utf-8 -*-
"""P755: the mask excludes the top face by HEIGHT, not by normal; the
card halo becomes a thin under-glow that never touches the badge.

THE SEAM, found by zooming my own screenshot (Denis pointed at it): the
boundary crosses the TOP face - the face the mask excludes. The
exclusion keyed on per-pixel normals, and the die is an authored, softly
bevelled mesh: its top-face normals spread enough that the smoothstep
crosses its threshold mid-face, and where it crosses is the line. Wider
bands (P753) only moved it. A normal-keyed mask cannot be seam-free on
a hand-modelled die.

Height can. A settled die's scoring face is its HIGHEST region, and
world height is continuous across the whole mesh - no threshold can sit
on a crease that does not exist. The relight now fades out between 0.15
and 0.42 die-heights above the die's centre: side faces fully in, top
face fully out, the fade riding up the bevel like light from above. The
normal varying goes entirely - less shader, no seam mechanism left.

THE CARD HALO drops below the card: Denis wants the silhouette kept and
the level badge clear. The stamp passes now take a downward offset
(CARD_GLOW.dyF, a fraction of card height), the reach tightens (soft 11
-> 6, rim 3 -> 2.5), and the punch-out stays at the card's true position
- so the glow reads as cast light under the card, the top edge stays
clean, and the badge sits over nothing.
"""
import io, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'fark_proto.html')
s = io.open(P, encoding='utf-8', newline='').read()
edits = []


def sub(old, new, label):
    global s
    c = s.count(old)
    if c != 1:
        o2 = old.replace('\n', '\r\n')
        if s.count(o2) == 1:
            old, new = o2, new.replace('\n', '\r\n')
        else:
            sys.exit('ANCHOR x%d for %s (nothing written)' % (c, label))
    s = s.replace(old, new)
    edits.append(label)


# ── 1. the shader: height mask, no normals ──
i = s.find("    m.onBeforeCompile=function(sh){")
j = s.find("    m.needsUpdate=true;", i)
if i < 0 or j < 0:
    sys.exit('shader markers not found (nothing written)')
NEWSH = (
    "    m.onBeforeCompile=function(sh){\n"
    "      sh.uniforms.fkK=u.uK;sh.uniforms.fkAmt=u.uAmt;sh.uniforms.fkAxSel=u.uAxSel;\n"
    "      sh.uniforms.fkSpanV=u.uSpan;sh.uniforms.fkDim=u.uDim;\n"
    "      /* P753: CLIP SPACE - the fragment's ndc against the die's\n"
    "         projected centre over its projected width, so every die wears\n"
    "         the same screen direction.\n"
    "         P755: the top face is excluded by HEIGHT, not by normal. The\n"
    "         authored die is softly bevelled, so its top-face normals\n"
    "         spread - and wherever a normal threshold lands, it draws a\n"
    "         line across the face (Denis's seam, zoomed and confirmed).\n"
    "         World height is continuous over the whole mesh: the relight\n"
    "         fades out between 0.15 and 0.42 die-heights above centre,\n"
    "         side faces in, top face out, no crease anywhere. */\n"
    "      sh.vertexShader=sh.vertexShader\n"
    "        .replace('#include <common>',\n"
    "          '#include <common>\\nuniform float fkSpanV;varying vec4 vFkClip;varying vec2 vFkC2;varying vec2 vFkSp;varying float vFkHy;')\n"
    "        .replace('#include <worldpos_vertex>',\n"
    "          '#include <worldpos_vertex>\\n'\n"
    "          +'vFkClip=projectionMatrix*modelViewMatrix*vec4(position,1.0);\\n'\n"
    "          +'vec4 fkCv=modelViewMatrix*vec4(0.0,0.0,0.0,1.0);\\n'\n"
    "          +'vec4 fkCc=projectionMatrix*fkCv;\\n'\n"
    "          +'vFkC2=fkCc.xy/fkCc.w;\\n'\n"
    "          +'vec4 fkPx=projectionMatrix*(fkCv+viewMatrix*vec4(fkSpanV,0.0,0.0,0.0));\\n'\n"
    "          +'vec4 fkPy=projectionMatrix*(fkCv+viewMatrix*vec4(0.0,0.0,fkSpanV,0.0));\\n'\n"
    "          +'vFkSp=vec2(max(abs(fkPx.x/fkPx.w-vFkC2.x),1e-4),max(abs(fkPy.y/fkPy.w-vFkC2.y),1e-4));\\n'\n"
    "          +'vFkHy=((modelMatrix*vec4(position,1.0)).y-modelMatrix[3][1])/max(length(modelMatrix[1].xyz),1e-4);');\n"
    "      sh.fragmentShader=sh.fragmentShader\n"
    "        .replace('#include <common>',\n"
    "          '#include <common>\\nvarying vec4 vFkClip;varying vec2 vFkC2;varying vec2 vFkSp;varying float vFkHy;\\n'\n"
    "          +'uniform float fkK;uniform float fkAmt;uniform float fkAxSel;uniform vec3 fkDim;')\n"
    "        .replace('#include <map_fragment>',\n"
    "          '#include <map_fragment>\\n'\n"
    "          +'if(fkK>0.001&&abs(fkAmt)>0.0001){\\n'\n"
    "          +'  vec2 fkD=vFkClip.xy/vFkClip.w-vFkC2;\\n'\n"
    "          +'  float fkT=clamp(0.5+mix(fkD.x/vFkSp.x,-fkD.y/vFkSp.y,fkAxSel),0.0,1.0);\\n'\n"
    "          +'  float fkM=1.0-smoothstep(0.15,0.42,vFkHy);\\n'\n"
    "          +'  float fkKt=fkK*(1.0-abs(fkAmt)*(fkAmt>0.0?fkT:(1.0-fkT)));\\n'\n"
    "          +'  vec3 fkA=vec3(1.0)-(vec3(1.0)-fkDim)*fkKt;\\n'\n"
    "          +'  vec3 fkF=vec3(1.0)-(vec3(1.0)-fkDim)*fkK;\\n'\n"
    "          +'  diffuseColor.rgb*=mix(vec3(1.0),fkA/max(fkF,vec3(0.02)),fkM);\\n'\n"
    "          +'}');\n"
    "    };\n"
)
s = s[:i] + NEWSH + s[j:]
edits.append('height mask shader')

# ── 2. the card halo: thin under-glow ──
sub("""  CARD_GLOW:{col:'#ffe6a4', softCol:'#ffa93a', soft:11, rim:3, strength:0.91,
    round:0.075, line:0, floor:0.42},""",
    """  /* P755: a thin UNDER-glow - dyF drops the halo by that fraction of
     the card's height, so the silhouette stays the card's own and the
     level badge at the top corner sits over clean table. */
  CARD_GLOW:{col:'#ffe6a4', softCol:'#ffa93a', soft:6, rim:2.5, strength:0.91,
    dyF:0.10, round:0.075, line:0, floor:0.42},""",
    'under-glow dials')

sub("    sel.forEach(function(sh){lay(sxc,sh,SOFT,{dy:G.dy,sx:G.sx,sy:G.sy});});",
    """    /* P755: a caller-given dy drops the whole halo (the card's
       under-glow); the dice keep G.dy on the soft pass as before */
    var DY=(opts&&opts.dy!==undefined)?opts.dy:null;
    sel.forEach(function(sh){lay(sxc,sh,SOFT,{dy:(DY!==null)?DY:G.dy,sx:G.sx,sy:G.sy});});""",
    'soft pass takes dy')

sub("    sel.forEach(function(sh){lay(sxc,sh,COL,{});});",
    "    sel.forEach(function(sh){lay(sxc,sh,COL,(DY!==null)?{dy:DY}:{});});",
    'rim pass takes dy')

sub("""      self._paintHalo(cv,x,sc,dpr,[shape],e.col||CG.col,e.col||CG.softCol,
        CG.floor+(1-CG.floor)*Math.min(1,e.k),CG.line,
        {soft:CG.soft,rim:CG.rim,strength:CG.strength});""",
    """      self._paintHalo(cv,x,sc,dpr,[shape],e.col||CG.col,e.col||CG.softCol,
        CG.floor+(1-CG.floor)*Math.min(1,e.k),CG.line,
        {soft:CG.soft,rim:CG.rim,strength:CG.strength,dy:r.height*(CG.dyF||0)});""",
    'card drops its halo')

# ── 3. the look record carries dyF ──
sub("      var KC=['soft','rim','strength','floor','round','line','col','softCol'];",
    "      var KC=['soft','rim','strength','floor','round','line','col','softCol','dyF'];",
    'look carries dyF')

io.open(P, 'w', encoding='utf-8', newline='').write(s)

# ── lab: drop slider + updated defaults ──
L = os.path.join(ROOT, 'fark_lab.html')
sl = io.open(L, encoding='utf-8', newline='').read()
pairs = [
    ("    +'<br><label>reach <input type=\"range\" id=\"cgSoft\" min=\"2\" max=\"30\" value=\"11\" oninput=\"cardDial(&quot;soft&quot;,+this.value)\"></label>'",
     "    +'<br><label>reach <input type=\"range\" id=\"cgSoft\" min=\"2\" max=\"30\" value=\"6\" oninput=\"cardDial(&quot;soft&quot;,+this.value)\"></label>'",
     'reach default 6'),
    ("    +'<label>core <input type=\"range\" id=\"cgRim\" min=\"1\" max=\"10\" value=\"3\" step=\"0.5\" oninput=\"cardDial(&quot;rim&quot;,+this.value)\"></label>'",
     "    +'<label>core <input type=\"range\" id=\"cgRim\" min=\"1\" max=\"10\" value=\"2.5\" step=\"0.5\" oninput=\"cardDial(&quot;rim&quot;,+this.value)\"></label>'\n"
     "    +'<label>drop <input type=\"range\" id=\"cgDy\" min=\"0\" max=\"25\" value=\"10\" oninput=\"cardDial(&quot;dyF&quot;,this.value/100)\"></label>'",
     'drop slider'),
    ("    var cmap={soft:['cgSoft',1],rim:['cgRim',1],strength:['cgStr',100],floor:['cgFloor',100]};",
     "    var cmap={soft:['cgSoft',1],rim:['cgRim',1],strength:['cgStr',100],floor:['cgFloor',100],dyF:['cgDy',100]};",
     'lab applies dyF'),
]
for old, new, label in pairs:
    c = sl.count(old)
    if c != 1:
        o2 = old.replace('\n', '\r\n')
        if sl.count(o2) == 1:
            old, new = o2, new.replace('\n', '\r\n')
        else:
            sys.exit('ANCHOR x%d for %s (game written, lab partial!)' % (c, label))
    sl = sl.replace(old, new)
    edits.append(label)
io.open(L, 'w', encoding='utf-8', newline='').write(sl)

print('done: %d (%s)' % (len(edits), ', '.join(edits)))
