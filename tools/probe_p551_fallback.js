/* P551: does a WebGL failure leave a PLAYABLE table?
   The requirement is not "fail is set" - it is that the player still sees dice.
   So: break WebGLRenderer, re-boot, and check the DOM dice are VISIBLE, that
   html.fk3d is not hiding them, and that boot does not spin retrying. */
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(f,ms)=>{const t=Date.now();while(Date.now()-t<ms){try{if(f())return true;}catch(e){}await sleep(60);}return false;};
_getS(); S.run=S.run||{}; S.run.tier=2;
S.run.dice=['bone','iron','flint','amber','jade','starstone'];
S.settings=S.settings||{}; S.settings.reducedMotion=true;
if(!(await until(()=>window.D3X,8000)))return{error:'no D3X'};
/* boot is LAZY - nothing loads three.js until a surface asks for dice. So open
   the shelf FIRST, let the 3D layer come up properly, and only then take the
   context away. That also makes this a truer test: it is the path a device
   takes when WebGL works long enough to boot and then does not. */
try{famLoadoutShow();}catch(e){}
if(!(await until(()=>window.THREE&&D3X.ready,20000)))return{error:'3D never came up to be broken'};
await sleep(600);
try{document.getElementById('loStage')&&famLoadoutHide&&famLoadoutHide();}catch(e){}
await sleep(400);
let boots=0;
const realBoot=D3X.boot.bind(D3X);
D3X.boot=function(cb){boots++;return realBoot(cb);};
/* BREAK IT WHERE A REAL DEVICE BREAKS: the canvas refuses a WebGL context.
   Overriding THREE.WebGLRenderer does NOT work - boot re-appends three.min.js,
   which re-executes and restores the real constructor, so the trap vanished
   and the layer came up fine. getContext survives the reload. */
const _gc=HTMLCanvasElement.prototype.getContext;
HTMLCanvasElement.prototype.getContext=function(t){
  if(/webgl/i.test(String(t)))return null;
  return _gc.apply(this,arguments);
};
/* reset as if this device had never got a renderer up */
D3X.ready=false; D3X.loading=false; D3X.fail=false; D3X._need=[];
try{D3X.detach&&D3X.detach();}catch(e){}
document.documentElement.classList.remove('fk3d');
try{famLoadoutShow();}catch(e){}
if(!(await until(()=>document.querySelectorAll('.d3chip').length>0,9000)))return{error:'no chips'};
await sleep(3500);
const chips=[...document.querySelectorAll('.d3chip')];
const vis=chips.map(c=>{const d=c.querySelector('.die');return d?getComputedStyle(d).visibility:'no-die';});
const faces=chips.map(c=>c.querySelectorAll('.d3f').length);
return {
  d3xFail:!!D3X.fail, d3xReady:!!D3X.ready, d3xLoading:!!D3X.loading,
  needQueued:(D3X._need||[]).length, bootCalls:boots,
  fk3dOn:document.documentElement.classList.contains('fk3d'),
  chips:chips.length, domDieVisibility:vis, cssFacesPerDie:faces,
  verdict:
    !D3X.fail ? 'FAIL - the failure was not recorded, so consumers still think 3D is loading'
    : D3X.loading ? 'FAIL - still flagged loading; boot can never be called again'
    : (D3X._need||[]).length ? 'FAIL - callbacks left queued that will never fire'
    : document.documentElement.classList.contains('fk3d') ? 'FAIL - fk3d left on, so the DOM dice are hidden with nothing drawing them'
    : !chips.length ? 'INCONCLUSIVE - no dice were built at all'
    : vis.some(v=>v==='hidden') ? 'FAIL - a DOM die is hidden: '+vis.join(',')
    : faces.some(f=>f!==6) ? 'FAIL - a DOM die is not a full six-plane cube: '+faces.join(',')
    : boots>6 ? 'FAIL - boot retried '+boots+' times; fail is not terminal'
    : 'PASS - WebGL refused, fail recorded, fk3d off, '+chips.length+' DOM dice visible with six planes each, boot called '+boots+' time(s)'
};
