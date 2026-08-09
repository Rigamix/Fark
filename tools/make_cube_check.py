# -*- coding: utf-8 -*-
"""Generate tools/cube_check.html - does the new cube work with the GAME'S maths?

THE QUESTION THIS ANSWERS. "Is the model correct" is not the same as "will the
game show the right number on it". D3X orients a die by looking up
D3X.FACE[value] and rotating that face to camera. So the only test that means
anything is: orient the cube with the GAME'S OWN TABLE and check the expected
pip count is the one facing you. If the model and the table disagree, the die
lands on 4 when the engine thinks it rolled a 3, and every other check passes.

So the page rotates each cube by the transpose of [R|U|N] taken verbatim out of
fark_proto.html - transpose, because [R|U|N] maps local axes ONTO the face basis
and what is wanted is the inverse: bring the face's normal to +Z and its up to
+Y. Getting that backwards yields a plausible cube showing the wrong faces.

IT ALSO ANSWERS THE PERSPECTIVE COMPLAINT. The DOM die looks inside-out because
D3.draw is orthographic - it computes each face's matrix with no perspective
divide, so nothing tells the eye which corner is nearer and it reads as a Necker
cube. This page uses a real PerspectiveCamera, which is the actual fix.

three.js and GLTFLoader are lifted out of die_texture_lab.html rather than
fetched, so the page is self-contained and works over file:// as well as the
dev server.
"""
import io, os, re, sys, base64

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
GAME = os.path.join(ROOT, 'fark_proto.html')
LAB = os.path.abspath(os.path.join(ROOT, '..', '..', '..', 'die_texture_lab.html'))
# the worktree copy - the SAME one make_cube_glb.py writes. Reading the main
# checkout's copy instead is how this page ended up rendering a stale model
# built from the wrong face table.
GLB = os.path.join(ROOT, 'assets', 'models', 'die_cube.glb')
OUT = os.path.join(HERE, 'cube_check.html')

for p in (GAME, LAB, GLB):
    if not os.path.exists(p):
        sys.exit('GATE FAILED: missing ' + p)

lab = io.open(LAB, encoding='utf-8', newline='').read()

# ---- lift the two libraries out of the lab -------------------------------
blocks = re.findall(r'<script(?![^>]*type="text/plain")[^>]*>(.*?)</script>', lab, re.S)
three_js = next((b for b in blocks if 'WebGLRenderer' in b and 'PerspectiveCamera' in b), None)
loader_js = next((b for b in blocks if 'class GLTFLoader' in b or 'GLTFLoader extends' in b), None)
if not three_js:
    sys.exit('GATE FAILED: three.js not found in the lab')
if not loader_js:
    sys.exit('GATE FAILED: GLTFLoader not found in the lab')
if len(three_js) < 100000:
    sys.exit('GATE FAILED: the three.js block is %d chars, too short to be the library'
             % len(three_js))

# ---- the game's own table, verbatim --------------------------------------
g = io.open(GAME, encoding='utf-8').read()
i = g.index('  FACE:{1:')
d, j = 0, g.index('{', i)
while j < len(g):
    if g[j] == '{':
        d += 1
    elif g[j] == '}':
        d -= 1
        if d == 0:
            break
    j += 1
face_literal = g[i + len('  FACE:'):j + 1]
if face_literal.count('[[') != 6:
    sys.exit('GATE FAILED: the FACE literal does not hold 6 bases')

glb_b64 = base64.b64encode(io.open(GLB, 'rb').read()).decode()

page = """<meta charset="utf-8"><title>cube check</title>
<style>
 html,body{margin:0;height:100%;background:#140f0a;color:#e8dcc0;
   font:14px/1.4 Georgia,serif;overflow:hidden}
 #c{position:fixed;inset:0}
 #labels{position:fixed;inset:0;pointer-events:none}
 .lab{position:absolute;transform:translate(-50%,0);text-align:center;
   font-size:15px;letter-spacing:.08em;color:#e8dcc0;text-shadow:0 2px 4px #000}
 .lab b{display:block;font-size:22px;color:#ffd98a}
 #note{position:fixed;left:14px;bottom:12px;font-size:13px;color:#b8a徒}
</style>
<canvas id="c"></canvas><div id="labels"></div>
<div id="note"></div>
<script id="glb" type="text/plain">__GLB__</script>
<script>__THREE__</script>
<script>__LOADER__</script>
<script>
/* THE GAME'S TABLE, PASTED VERBATIM out of fark_proto.html by
   tools/make_cube_check.py. Each entry is [right, up, normal] for that value. */
var FACE = __FACE__;

var cv=document.getElementById('c');
var renderer=new THREE.WebGLRenderer({canvas:cv,antialias:true,alpha:false});
renderer.setPixelRatio(Math.min(2,window.devicePixelRatio||1));
var scene=new THREE.Scene(); scene.background=new THREE.Color(0x140f0a);
/* A REAL PERSPECTIVE CAMERA. The DOM renderer is orthographic, which is why
   that die reads inside-out - with no perspective divide nothing tells the eye
   which corner is nearer, so it flips like a Necker cube. */
var cam=new THREE.PerspectiveCamera(30,1,0.1,100);
scene.add(new THREE.AmbientLight(0xffffff,0.55));
var key=new THREE.DirectionalLight(0xfff0d8,0.95); key.position.set(-2,3,4); scene.add(key);
var rim=new THREE.DirectionalLight(0x88aaff,0.25); rim.position.set(3,-1,-2); scene.add(rim);

var bin=atob(document.getElementById('glb').textContent.replace(/\\s+/g,''));
var bytes=new Uint8Array(bin.length);
for(var i=0;i<bin.length;i++)bytes[i]=bin.charCodeAt(i);

var slots=[],spin=0;
new THREE.GLTFLoader().parse(bytes.buffer,'',function(gl){
  var proto=gl.scene;
  for(var v=1;v<=6;v++){
    var o=proto.clone(true);
    var f=FACE[v], R=f[0], U=f[1], N=f[2];
    /* TRANSPOSE of [R|U|N]: that matrix maps the local axes ONTO the face
       basis, and what is wanted is the inverse - bring this value's normal to
       +Z (at the camera) and its up to +Y. THREE's Matrix4.set is row-major,
       so passing R, U, N as the ROWS is the transpose. */
    var m=new THREE.Matrix4();
    m.set(R[0],R[1],R[2],0, U[0],U[1],U[2],0, N[0],N[1],N[2],0, 0,0,0,1);
    var holder=new THREE.Group();
    o.applyMatrix4(m);
    holder.add(o);
    var col=(v-1)%3, row=Math.floor((v-1)/3);
    holder.scale.setScalar(0.78);
    holder.position.set((col-1)*1.32,(0.86-row*1.72),0);
    holder.userData.v=v;
    scene.add(holder); slots.push(holder);
  }
  document.getElementById('note').textContent=
    'each cube rotated by D3X.FACE[value] so that value faces the camera - the label is what the ENGINE thinks it rolled';
  window.__ready=true;
  resize(); frame();
});

function resize(){
  var w=innerWidth,h=innerHeight;
  /* updateStyle MUST stay on. With setSize(w,h,false) the canvas keeps its
     ATTRIBUTE size as its CSS size - 1960x1560 at dpr 2 - inside a 980x780
     viewport, so the page showed the top-left quadrant and one giant die.
     inset:0 does not size a canvas; only width/height do. It looked perfect
     at dpr 1, where attribute and CSS sizes coincide. */
  renderer.setSize(w,h); cam.aspect=w/h; cam.updateProjectionMatrix();
  /* FIT THE GRID, do not hard-code a distance. A fixed 7.4 framed correctly at
     one aspect ratio and cropped to a single cube at another - the check page
     showing one die instead of six is the check silently not running. Solve
     for both the vertical and horizontal fov and take whichever needs more
     room. */
  var GW=2*1.32+1.15, GH=1.72+1.55, vf=cam.fov*Math.PI/180;
  var dV=(GH/2)/Math.tan(vf/2);
  var hf=2*Math.atan(Math.tan(vf/2)*cam.aspect);
  var dH=(GW/2)/Math.tan(hf/2);
  cam.position.set(0,0,Math.max(dV,dH)*1.08); cam.lookAt(0,0,0);
  cam.updateProjectionMatrix();
  var L=document.getElementById('labels'); L.innerHTML='';
  slots.forEach(function(s){
    var p=s.position.clone(); p.y-=0.62; p.project(cam);
    var d=document.createElement('div'); d.className='lab';
    d.style.left=((p.x*0.5+0.5)*w)+'px'; d.style.top=((-p.y*0.5+0.5)*h)+'px';
    d.innerHTML='engine says<b>'+s.userData.v+'</b>';
    L.appendChild(d);
  });
}
addEventListener('resize',resize);
/* a slow wobble, so a flat-on view cannot hide a mirrored or rotated face */
function frame(){
  spin+=0.006;
  slots.forEach(function(s){ s.rotation.y=Math.sin(spin)*0.30; s.rotation.x=Math.cos(spin*0.8)*0.16; });
  renderer.render(scene,cam);
  requestAnimationFrame(frame);
}
window.__still=function(){ slots.forEach(function(s){s.rotation.set(0,0,0);}); renderer.render(scene,cam); };
</script>
"""
page = page.replace('#b8a徒', '#b8a888')   # guard against a stray char in the template
page = (page.replace('__GLB__', glb_b64)
            .replace('__THREE__', three_js)
            .replace('__LOADER__', loader_js)
            .replace('__FACE__', face_literal))

io.open(OUT, 'w', encoding='utf-8', newline='\n').write(page)
print('tools/cube_check.html  %d KB  (three.js %dKB, loader %dKB, glb %dKB)'
      % (len(page) // 1024, len(three_js) // 1024, len(loader_js) // 1024, len(glb_b64) // 1024))
print('FACE table copied verbatim:', face_literal.replace('\n', ' ')[:90] + '...')
