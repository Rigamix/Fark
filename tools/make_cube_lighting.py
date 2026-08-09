# -*- coding: utf-8 -*-
"""Generate tools/cube_lighting.html - four lighting treatments, one cube.

Denis: "lighting should be very simple, no specular, etc." That is a decision
with more than one answer, and it is far cheaper to look at four than to argue
about them, so this renders the SAME die under four treatments side by side.

  1  UNLIT              MeshBasicMaterial. The art exactly as painted, zero
                        shading. Every face identical brightness - so the cube
                        may read FLAT, which is the thing to judge.
  2  FLAT + FACE RAMP   Unlit, plus one brightness multiplier per face from a
                        fixed light vector. No specular, no gradient across a
                        face. THIS IS WHAT THE CSS RENDERER ALREADY DOES -
                        D3.LIGHT is [0,-0.33,0.94] and D3.draw multiplies each
                        face by its own constant. Closest to the current look.
  3  LAMBERT            MeshLambertMaterial, ambient + one directional. Diffuse
                        only, genuinely no specular, but shading VARIES across
                        a face, which the painted art does not expect.
  4  STANDARD           What die_cube.glb currently declares - PBR, roughness
                        0.85. Included as the control: it is the one WITH a
                        specular response, so it shows what is being rejected.

Treatment 2 uses the game's own LIGHT vector, extracted from the file rather
than typed, so "closest to current" is a claim the page can actually support.
The exact ramp D3.draw applies is a per-face opacity over three overlay layers
and is NOT reproduced here - this approximates it with a single multiplier and
says so, because a picture that silently claims to be the current look while
using a different curve would be the display vouching for itself.
"""
import io, os, re, sys, base64

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
GAME = os.path.join(ROOT, 'fark_proto.html')
LAB = os.path.abspath(os.path.join(ROOT, '..', '..', '..', 'die_texture_lab.html'))
GLB = os.path.join(ROOT, 'assets', 'models', 'die_cube.glb')
OUT = os.path.join(HERE, 'cube_lighting.html')

for p in (GAME, LAB, GLB):
    if not os.path.exists(p):
        sys.exit('GATE FAILED: missing ' + p)

lab = io.open(LAB, encoding='utf-8', newline='').read()
blocks = re.findall(r'<script(?![^>]*type="text/plain")[^>]*>(.*?)</script>', lab, re.S)
three_js = next((b for b in blocks if 'WebGLRenderer' in b and 'PerspectiveCamera' in b), None)
loader_js = next((b for b in blocks if 'class GLTFLoader' in b or 'GLTFLoader extends' in b), None)
if not three_js or len(three_js) < 100000:
    sys.exit('GATE FAILED: three.js not lifted')
if not loader_js:
    sys.exit('GATE FAILED: GLTFLoader not lifted')

g = io.open(GAME, encoding='utf-8').read()
m = re.search(r'LIGHT:\[(-?[\d.]+),(-?[\d.]+),(-?[\d.]+)\]', g)
if not m:
    sys.exit('GATE FAILED: D3.LIGHT not found - treatment 2 would be a guess')
LIGHT = '[%s,%s,%s]' % m.groups()

glb_b64 = base64.b64encode(io.open(GLB, 'rb').read()).decode()

page = """<meta charset="utf-8"><title>die lighting</title>
<style>
 html,body{margin:0;height:100%;background:#140f0a;color:#e8dcc0;
   font:14px/1.45 Georgia,serif;overflow:hidden}
 #c{position:fixed;inset:0;width:100%;height:100%}
 #labels{position:fixed;inset:0;pointer-events:none}
 .lab{position:absolute;transform:translate(-50%,0);text-align:center;width:230px}
 .lab b{display:block;font-size:17px;color:#ffd98a;letter-spacing:.06em}
 .lab i{font-style:normal;font-size:12px;color:#a99b83;display:block;margin-top:3px}
 #note{position:fixed;left:14px;bottom:10px;font-size:12.5px;color:#a99b83}
</style>
<canvas id="c"></canvas><div id="labels"></div><div id="note"></div>
<script id="glb" type="text/plain">__GLB__</script>
<script>__THREE__</script>
<script>__LOADER__</script>
<script>
/* the game's own light direction, extracted from fark_proto.html - not typed */
var D3_LIGHT = __LIGHT__;

var cv=document.getElementById('c');
var renderer=new THREE.WebGLRenderer({canvas:cv,antialias:true});
renderer.setPixelRatio(Math.min(2,window.devicePixelRatio||1));
var scene=new THREE.Scene(); scene.background=new THREE.Color(0x140f0a);
var cam=new THREE.PerspectiveCamera(28,1,0.1,100);

/* Lights exist only for treatment 3. Treatments 1, 2 and 4 either ignore them
   (Basic) or are given their own so the comparison is not confounded by one
   rig flattering one material. */
var amb=new THREE.AmbientLight(0xffffff,0.62);
var dir=new THREE.DirectionalLight(0xfff2de,0.85);
dir.position.set(D3_LIGHT[0]*4,-D3_LIGHT[1]*4,D3_LIGHT[2]*4);
scene.add(amb); scene.add(dir);

var TREAT=[
 {n:'UNLIT',        d:'art as painted, no shading'},
 {n:'FLAT + RAMP',  d:'one multiplier per face &mdash; what the CSS die does'},
 {n:'LAMBERT',      d:'diffuse only, shading varies across a face'},
 {n:'STANDARD',     d:'current glb &mdash; the one WITH specular'}
];

var bin=atob(document.getElementById('glb').textContent.replace(/\\s+/g,''));
var bytes=new Uint8Array(bin.length);
for(var i=0;i<bin.length;i++)bytes[i]=bin.charCodeAt(i);

var slots=[];
new THREE.GLTFLoader().parse(bytes.buffer,'',function(gl){
  var proto=gl.scene, tex=null;
  proto.traverse(function(o){ if(o.isMesh && o.material && o.material.map) tex=o.material.map; });
  if(!tex){ document.getElementById('note').textContent='no texture on the model'; return; }

  var L=new THREE.Vector3(D3_LIGHT[0],-D3_LIGHT[1],D3_LIGHT[2]).normalize();

  for(var t=0;t<4;t++){
    var o=proto.clone(true);
    (function(mode,obj){
      obj.traverse(function(n){
        if(!n.isMesh)return;
        if(mode===0){
          n.material=new THREE.MeshBasicMaterial({map:tex});
        }else if(mode===1){
          /* ONE CONSTANT PER FACE. The geometry has flat normals and 4 verts
             per face, so a per-vertex colour IS a per-face colour here - no
             gradient can appear across a face, which is the point. */
          var g2=n.geometry.clone(), na=g2.attributes.normal, cols=[];
          for(var v=0;v<na.count;v++){
            var d=new THREE.Vector3(na.getX(v),na.getY(v),na.getZ(v)).dot(L);
            var b=0.62+0.38*Math.max(0,d);      /* approximation of D3's ramp */
            cols.push(b,b,b);
          }
          g2.setAttribute('color',new THREE.Float32BufferAttribute(cols,3));
          n.geometry=g2;
          n.material=new THREE.MeshBasicMaterial({map:tex,vertexColors:true});
        }else if(mode===2){
          n.material=new THREE.MeshLambertMaterial({map:tex});
        }else{
          n.material=new THREE.MeshStandardMaterial({map:tex,roughness:0.85,metalness:0});
        }
        n.material.needsUpdate=true;
      });
    })(t,o);
    var holder=new THREE.Group();
    holder.add(o);
    holder.position.set((t-1.5)*1.5,0,0);
    holder.rotation.set(-0.30,0.62,0);
    holder.userData.t=t;
    scene.add(holder); slots.push(holder);
  }
  document.getElementById('note').innerHTML=
    'same cube, same texture, four treatments. Light direction is the game\\u2019s own D3.LIGHT '
    +JSON.stringify(D3_LIGHT)+'. Treatment 2 APPROXIMATES D3.draw\\u2019s ramp with a single '
    +'multiplier per face &mdash; the real one is three overlay layers, so treat it as close, not exact.';
  resize(); render();
});

function resize(){
  var w=innerWidth,h=innerHeight;
  renderer.setSize(w,h); cam.aspect=w/h;
  var GW=3*1.5+1.3, GH=1.9, vf=cam.fov*Math.PI/180;
  var dV=(GH/2)/Math.tan(vf/2);
  var hf=2*Math.atan(Math.tan(vf/2)*cam.aspect);
  var dH=(GW/2)/Math.tan(hf/2);
  cam.position.set(0,0,Math.max(dV,dH)*1.06); cam.lookAt(0,0,0);
  cam.updateProjectionMatrix();
  var L=document.getElementById('labels'); L.innerHTML='';
  slots.forEach(function(s){
    var p=s.position.clone(); p.y-=0.95; p.project(cam);
    var d=document.createElement('div'); d.className='lab';
    d.style.left=((p.x*0.5+0.5)*w)+'px'; d.style.top=((-p.y*0.5+0.5)*h)+'px';
    d.innerHTML='<b>'+TREAT[s.userData.t].n+'</b><i>'+TREAT[s.userData.t].d+'</i>';
    L.appendChild(d);
  });
  render();
}
addEventListener('resize',resize);
function render(){ renderer.render(scene,cam); }
window.__ready=true;
</script>
"""
page = (page.replace('__GLB__', glb_b64)
            .replace('__THREE__', three_js)
            .replace('__LOADER__', loader_js)
            .replace('__LIGHT__', LIGHT))
io.open(OUT, 'w', encoding='utf-8', newline='\n').write(page)
print('tools/cube_lighting.html  %d KB   D3.LIGHT %s (extracted)' % (len(page) // 1024, LIGHT))
