/* SUITE: exclude. P752: is the shadow-mask axis GLOBAL now?
 *
 * Launch, roll, let the settle dim arrive, then push the mask to an
 * exaggerated amount on axis x and hold for the screenshot. Success in
 * the composite: every die's side faces darken toward the same screen
 * side, whatever way each die rotated when it landed. A shader compile
 * failure would show as black dice and console errors - shoot.js prints
 * page errors, so an empty error list is part of the verdict.
 */
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(fn,ms)=>{const t0=Date.now();while(Date.now()-t0<ms){try{if(fn())return true;}catch(e){}await sleep(90);}return false;};
const out={};
if(!await until(()=>typeof launchSeat==='function'&&typeof G!=='undefined',20000))
  return {err:'game never booted'};
await until(()=>document.getElementById('screen-gauntlet'),8000);
try{launchSeat(0);}catch(e){return {err:'launchSeat: '+e.message};}
if(!await until(()=>G&&G.phase,12000))return {err:'no match'};
await until(()=>window.D3X&&D3X.mount,12000);
await sleep(700);
for(let a=0;a<4&&!D3X.dice.length;a++){
  const b=document.getElementById('btnRoll');
  if(b)b.click();
  await until(()=>D3X.dice.length>0,4000);
}
await until(()=>D3X.dice.some(d=>d.match&&d.roll),15000);
await until(()=>D3X.dice.filter(d=>d.match).every(d=>!d.roll),25000);
/* the settle dim ramps over ~350ms after landing */
await sleep(1400);
out.dice=D3X.dice.filter(d=>d.match).length;
/* prove the hook took: every die material carries the uniforms, and the
   settle ramp reached them */
let hooked=0,ks=[];
D3X.dice.forEach(d=>{if(!d.match||!d.obj)return;
  d.obj.traverse(o=>{if(o.isMesh&&o.material&&o.material.userData.fkG){
    hooked++;ks.push(+o.material.userData.fkG.uK.value.toFixed(3));}});});
out.hooked=hooked;
out.uK=ks.slice(0,6);
/* exaggerate for the eye */
D3X.setGrad('x',0.9);
await sleep(400);
out.grad=JSON.parse(JSON.stringify(D3X.GRAD));
return out;
