const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(fn,ms)=>{const t0=Date.now();while(Date.now()-t0<ms){try{if(fn())return true;}catch(e){}await sleep(60);}return false;};
const out={};
await setup();
if(!await until(()=>{const g=E('G');return g&&g.phase;},4000))return {err:'no match'};
roll();
if(!await until(()=>E('window.D3X').dice.some(d=>d.match&&d.roll),12000))return {err:'no roll'};
await until(()=>{const dx=E('window.D3X');return dx.dice.filter(d=>d.match).every(d=>!d.roll);},22000);
await sleep(400);
out.hold=E('D3X.AMBER.holdMs');out.fade=E('D3X.AMBER.fadeMs');
/* shell a die directly, then time the dissolve */
const has=()=>E(`(function(){var d=D3X.dice.filter(function(x){return x.match&&x.obj;})[0];
 return !!(d&&d.obj.getObjectByName('fkAmber'));})()`);
E("var d0=D3X.dice.filter(function(x){return x.match&&x.obj;})[0];D3X.amberShell(d0,true)");
out.shellOn=has();
const t0=Date.now();
E("D3X.amberShell(d0,false)");
out.stillThereImmediately=has();     /* a dissolve is NOT instant */
await sleep(200);
out.midFade=E(`(function(){var d=D3X.dice.filter(function(x){return x.match&&x.obj;})[0];
 var g=d.obj.getObjectByName('fkAmber');if(!g)return null;var o=null;
 g.traverse(function(m){if(!o&&m.isMesh)o=+m.material.opacity.toFixed(3);});
 return {op:o,scale:+g.scale.x.toFixed(3)};})()`);
await until(()=>!has(),3000);
out.goneAfterMs=Date.now()-t0;
out.verdict=out.hold>=1200&&out.stillThereImmediately===true
  &&!!out.midFade&&out.midFade.op<0.42&&out.midFade.scale>1
  &&out.goneAfterMs>=350&&out.goneAfterMs<1500;
return out;
