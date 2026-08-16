/* SUITE: exclude. P754: does a lab-saved look apply in the STANDALONE
 * game? Seed a distinctive record before D3X mounts (the mount happens
 * at first launch, after this seed), then verify every field landed. */
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(fn,ms)=>{const t0=Date.now();while(Date.now()-t0<ms){try{if(fn())return true;}catch(e){}await sleep(90);}return false;};
const out={};
localStorage.fkLabLook=JSON.stringify({
  vgA:40,vgR:50,vgC:20,sh:30,sd:0.5,maskAmt:-60,maskAxis:'y',bounce:0.3,
  lights:[0.5,0.5,0.5],GLOW:{soft:22,strength:0.55,fbWide:9},CG:{soft:19,strength:0.4}});
if(!await until(()=>typeof launchSeat==='function'&&typeof G!=='undefined',20000))
  return {err:'game never booted'};
await until(()=>document.getElementById('screen-gauntlet'),8000);
try{launchSeat(0);}catch(e){return {err:'launchSeat: '+e.message};}
if(!await until(()=>G&&G.phase,12000))return {err:'no match'};
await until(()=>window.D3X&&D3X.mount,12000);
await sleep(700);
for(let a=0;a<4&&!(window.D3X&&D3X.dice.length);a++){
  const b0=document.getElementById('btnRoll');
  if(b0)b0.click();
  await until(()=>D3X.dice.length>0,4000);
}
if(!await until(()=>window.D3X&&D3X.ready,15000))return {err:'D3X never ready (after roll)'};
await sleep(600);
out.sd=D3X.SIDEDIM_MAX;
out.grad=JSON.parse(JSON.stringify(D3X.GRAD));
out.glowSoft=D3X.GLOW.soft;
out.glowStr=D3X.GLOW.strength;
out.fbLeak=D3X.GLOW.fbWide;/* must stay undefined - retired dial filtered */
out.cgSoft=D3X.CARD_GLOW.soft;
out.lookLights=D3X._lookLights;
const b=D3X.scene&&D3X.scene.getObjectByName('fkBounce');
out.bounce=b?+b.intensity.toFixed(2):null;
const vg=document.getElementById('labVig');
out.vig=vg?vg.style.background.slice(0,60):null;
const msd=document.getElementById('matchShadows');
out.shadowFilter=msd?msd.style.filter:null;
out.verdict=out.sd===0.5&&out.grad.ax==='y'&&Math.abs(out.grad.amt+0.6)<1e-9
  &&out.glowSoft===22&&out.fbLeak===undefined&&out.cgSoft===19
  &&!!out.lookLights&&out.bounce===0.3&&!!out.vig&&/0\.7/.test(out.shadowFilter||'');
return out;
