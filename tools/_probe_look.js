/* SUITE: exclude. v6 look studio: room overlay under the dice canvas,
 * shadow depth, side gradient bake, glow shells - then a SHOT with the
 * accidental-look mix applied for eyeballing. */
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(fn,ms)=>{const t0=Date.now();while(Date.now()-t0<ms){try{if(fn())return true;}catch(e){}await sleep(100);}return false;};
const out={};
await setup();
if(!await until(()=>{const g=E('G');return g&&g.phase;},4000))return {err:'no match'};
roll();
/* the roll must START before a settle-wait means anything - an empty
   match-dice list satisfies .every vacuously */
if(!await until(()=>E('window.D3X').dice.some(d=>d.match&&d.roll),15000))
  return {err:'roll never started - no match dice adopted'};
await until(()=>{const dx=E('window.D3X');
  return dx.dice.filter(d=>d.match).every(d=>!d.roll)&&dx.dice.some(d=>d.match&&d.phys);},20000);
await sleep(500);
/* apply the accidental-look mix */
roomSet(38);
shadowSet(30);
gradeDice(-45);
out.lightRowLen=document.getElementById('lightRow').innerHTML.length;
out.hasGlOn=!!document.getElementById('glOn');
out.logTail=document.getElementById('log').textContent.split(String.fromCharCode(10)).slice(0,4);
if(!out.hasGlOn)return {...out,err:'no glow studio in lightRow'};
document.getElementById('glOn').checked=true;
document.getElementById('glRim').value=104;
document.getElementById('glHalo').value=122;
document.getElementById('glA').value=55;
glowApply();
await sleep(600);
gw();
const ov=W.document.getElementById('labDark');
out.overlay=ov?+ov.style.opacity:null;
out.overlayUnderCanvas=(()=>{const cvs=W.document.getElementById('d3xCanvas');
  if(!ov||!cvs)return null;
  return (parseInt(ov.style.zIndex)||0)<(parseInt(getComputedStyle(cvs).zIndex)||0);})();
out.shadowFilter=(W.document.getElementById('matchShadows')||{}).style.filter;
const dx=E('window.D3X');
out.diceTotal=dx?dx.dice.length:null;
out.diceMatch=dx?dx.dice.filter(d=>d.match).length:null;
out.gPhase=(E('G')||{}).phase;
const d0=dx.dice.filter(d=>d.match&&d.chip)[0];
if(!d0)return {...out,err:'no match dice with chips'};
out.graded=(()=>{let g=false;d0.obj.traverse(o=>{if(o.isMesh&&o.material&&o.material.userData&&o.material.userData._gradeBase)g=true;});return g;})();
out.glow=!!d0.obj.getObjectByName('labGlow');
out.glowBackside=(()=>{const g=d0.obj.getObjectByName('labGlow');
  return g?g.userData.rim.material.side===W.__labEval('THREE').BackSide:null;})();
out.verdict=out.overlay===0.38&&out.overlayUnderCanvas===true&&/brightness/.test(out.shadowFilter||'')
  &&out.graded&&out.glow&&out.glowBackside===true;
return out;
