/* SUITE: exclude. v7: vignette in the dice area (UI untouched), real
 * glow dials incl. P731 direction, dim-mask gradient with axis. */
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(fn,ms)=>{const t0=Date.now();while(Date.now()-t0<ms){try{if(fn())return true;}catch(e){}await sleep(100);}return false;};
const out={};
await setup();
if(!await until(()=>{const g=E('G');return g&&g.phase;},4000))return {err:'no match'};
roll();
if(!await until(()=>E('window.D3X').dice.some(d=>d.match&&d.roll),15000))
  return {err:'roll never started'};
await until(()=>{const dx=E('window.D3X');
  return dx.dice.filter(d=>d.match).every(d=>!d.roll)&&dx.dice.some(d=>d.match&&d.phys);},20000);
await sleep(500);
/* vignette */
document.getElementById('vgA').value=45;
document.getElementById('vgR').value=40;
document.getElementById('vgC').value=25;
vigSet();
gw();
const vig=W.document.getElementById('labVig'),ctr=W.document.getElementById('labCenter');
out.vig=!!vig&&/radial/.test(vig.style.background);
out.ctr=!!ctr&&/radial/.test(ctr.style.background);
out.inDiceArea=vig&&!!vig.closest('.dice-area');
out.hudClean=(()=>{const hud=W.document.getElementById('hud');
  return !hud||!vig||!hud.contains(vig);})();
/* dim mask with axis */
document.getElementById('dgAmt').value=-60;
gradeDice(-60);
out.dimCfg=E('window.__labDimGrad');
out.dimOverridden=E('typeof window.__labDimOrig')==='function';
await sleep(700); /* settled dice rebake */
const dx=E('window.D3X');
const d0=dx.dice.filter(d=>d.match&&d.chip&&d.phys&&d.phys.v)[0];
out.maskedKey=(()=>{if(!d0)return 'no settled die';
  let key=null;d0.obj.traverse(o=>{if(key||!o.isMesh||o.userData.outline)return;
    const lm=o.material.userData&&o.material.userData.liveMap;
    if(lm&&lm.userData&&lm.userData.dimMaps){const ks=Object.keys(lm.userData.dimMaps);
      key=ks.find(k=>/y-0.6/.test(k))||ks[0]||'none';}});
  return key;})();
/* real glow dials + select all */
glowSelAll(true);
glowDial('sy',1.5);glowDial('dy',-10);glowDial('strength',0.9);
out.glowSy=E('D3X.GLOW.sy');
out.glowDy=E('D3X.GLOW.dy');
out.selCount=dx.dice.filter(d=>d.match&&d.chip.classList.contains('selected')).length;
out.glowInk=E('D3X._glowInk');
out.verdict=out.vig&&out.ctr&&out.hudClean&&!!out.dimCfg&&out.dimOverridden
  &&/y-0.6/.test(out.maskedKey||'')&&out.glowSy===1.5&&out.glowDy===-10&&out.selCount>0;
return out;
