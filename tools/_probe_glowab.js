/* SUITE: exclude. The glow has TWO painters: ctx.filter blur (desktop)
 * and stroked rings (iOS Safari < 18). Measure both in the SAME browser
 * from the painted canvas - extent and mass. */
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(fn,ms)=>{const t0=Date.now();while(Date.now()-t0<ms){try{if(fn())return true;}catch(e){}await sleep(100);}return false;};
const out={};
await setup();
if(!await until(()=>{const g=E('G');return g&&g.phase;},4000))return {err:'no match'};
roll();
if(!await until(()=>E('window.D3X').dice.some(d=>d.match&&d.roll),12000))return {err:'no roll'};
await until(()=>{const dx=E('window.D3X');return dx.dice.filter(d=>d.match).every(d=>!d.roll);},22000);
await sleep(600);
gw();
E("D3X.dice.forEach(function(d){if(d.match&&d.chip)d.chip.classList.add('selected');})");
out.cfNative=E('D3X._cf');
const measure=(useFilter)=>{
  E('D3X._cf='+(useFilter?'true':'false'));
  E('D3X._glowInk=false');
  E('D3X._drawGlow&&D3X._drawGlow()');
  const cv=W.document.getElementById('dgCanvas');
  if(!cv)return null;
  const cx=cv.getContext('2d');
  const w=cv.width,h=cv.height;
  const im=cx.getImageData(0,0,w,h).data;
  let mass=0,strong=0,minX=w,maxX=0,minY=h,maxY=0;
  for(let y=0;y<h;y+=2)for(let x=0;x<w;x+=2){
    const a=im[(y*w+x)*4+3];
    if(a>12){mass++;if(x<minX)minX=x;if(x>maxX)maxX=x;if(y<minY)minY=y;if(y>maxY)maxY=y;}
    if(a>110)strong++;
  }
  const dpr=w/(W.innerWidth||430);
  return {mass,strong,w:+((maxX-minX)/dpr).toFixed(1),h:+((maxY-minY)/dpr).toFixed(1),
    massCss:Math.round(mass/(dpr*dpr)),strongCss:Math.round(strong/(dpr*dpr)),dpr:+dpr.toFixed(2)};
};
out.filterBranch=measure(true);
out.strokeBranch=measure(false);
E('D3X._cf='+(out.cfNative?'true':'false'));
if(out.filterBranch&&out.strokeBranch){
  out.ratioMass=+(out.strokeBranch.mass/out.filterBranch.mass).toFixed(2);
  out.ratioStrong=+(out.strokeBranch.strong/Math.max(1,out.filterBranch.strong)).toFixed(2);
  out.ratioW=+(out.strokeBranch.w/out.filterBranch.w).toFixed(2);
}
return out;
