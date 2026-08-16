# -*- coding: utf-8 -*-
"""P752b: repair the shader-injection strings.

The first write went through a bash heredoc and the heredoc backslash
trap (documented in the patch workflow for exactly this reason) turned
every intended two-character \\n inside the JS string literals into a
real newline - unterminated strings, parse fail. This file is written by
the Write tool, so the escapes below survive verbatim.
"""
import io, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'fark_proto.html')
s = io.open(P, encoding='utf-8', newline='').read()

i = s.find("    m.onBeforeCompile=function(sh){")
j = s.find("    m.needsUpdate=true;", i)
if i < 0 or j < 0:
    sys.exit('markers not found (nothing written)')

NEW = (
    "    m.onBeforeCompile=function(sh){\n"
    "      sh.uniforms.fkK=u.uK;sh.uniforms.fkAmt=u.uAmt;sh.uniforms.fkAx=u.uAx;\n"
    "      sh.uniforms.fkSpan=u.uSpan;sh.uniforms.fkDim=u.uDim;\n"
    "      sh.vertexShader=sh.vertexShader\n"
    "        .replace('#include <common>',\n"
    "          '#include <common>\\nvarying vec3 vFkW;varying vec3 vFkC;varying vec3 vFkN;')\n"
    "        .replace('#include <worldpos_vertex>',\n"
    "          '#include <worldpos_vertex>\\n'\n"
    "          +'vFkW=(modelMatrix*vec4(position,1.0)).xyz;\\n'\n"
    "          +'vFkC=(modelMatrix*vec4(0.0,0.0,0.0,1.0)).xyz;\\n'\n"
    "          +'vFkN=normalize(mat3(modelMatrix[0].xyz,modelMatrix[1].xyz,modelMatrix[2].xyz)*normal);');\n"
    "      sh.fragmentShader=sh.fragmentShader\n"
    "        .replace('#include <common>',\n"
    "          '#include <common>\\nvarying vec3 vFkW;varying vec3 vFkC;varying vec3 vFkN;\\n'\n"
    "          +'uniform float fkK;uniform float fkAmt;uniform vec3 fkAx;'\n"
    "          +'uniform float fkSpan;uniform vec3 fkDim;')\n"
    "        .replace('#include <map_fragment>',\n"
    "          '#include <map_fragment>\\n'\n"
    "          +'if(fkK>0.001&&abs(fkAmt)>0.0001){\\n'\n"
    "          +'  float fkT=clamp(0.5+dot(vFkW-vFkC,fkAx)/fkSpan,0.0,1.0);\\n'\n"
    "          +'  float fkM=1.0-smoothstep(0.55,0.85,dot(normalize(vFkN),vec3(0.0,1.0,0.0)));\\n'\n"
    "          +'  float fkKt=fkK*(1.0-abs(fkAmt)*(fkAmt>0.0?fkT:(1.0-fkT)));\\n'\n"
    "          +'  vec3 fkA=vec3(1.0)-(vec3(1.0)-fkDim)*fkKt;\\n'\n"
    "          +'  vec3 fkF=vec3(1.0)-(vec3(1.0)-fkDim)*fkK;\\n'\n"
    "          +'  diffuseColor.rgb*=mix(vec3(1.0),fkA/max(fkF,vec3(0.02)),fkM);\\n'\n"
    "          +'}');\n"
    "    };\n"
)
s = s[:i] + NEW + s[j:]
io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('shader strings repaired')
