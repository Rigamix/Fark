/* SUITE: exclude. v10: the CLICK routes (not direct calls) + the
 * dresser rebuild + the P732 baked look on the game screen. */
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(fn,ms)=>{const t0=Date.now();while(Date.now()-t0<ms){try{if(fn())return true;}catch(e){}await sleep(100);}return false;};
const click=el=>{if(!el)return false;el.click();return true;};
const out={};
await setup();
if(!await until(()=>{const g=E('G');return g&&g.phase;},4000))return {err:'no match'};
roll();
if(!await until(()=>E('window.D3X').dice.some(d=>d.match&&d.roll),15000))return {err:'no roll'};
await until(()=>{const dx=E('window.D3X');
  return dx.dice.filter(d=>d.match).every(d=>!d.roll)&&dx.dice.some(d=>d.match&&d.phys);},20000);
await sleep(500);
/* THE CLICK on a gallery card - the route Denis uses */
showTab(1);
const gc=[...document.querySelectorAll('#gallery .gcard')].find(c=>/Preserve/i.test(c.textContent));
out.clicked=click(gc);
await sleep(600);
out.wsOpen=document.getElementById('ws').classList.contains('on');
out.steps=document.querySelectorAll('#seqLane .step').length;
/* catalogue note typing via the real change event */
showTab(2);
const ta=document.querySelector('#catalogue textarea');
if(ta){ta.value='typed note works';
  ta.dispatchEvent(new Event('change'));}
await sleep(200);
out.noteTyped=(()=>{try{const ns=JSON.parse(localStorage.fkLabCardNotes);
  return Object.values(ns).includes('typed note works');}catch(e){return false;}})();
/* the dresser rebuild */
showTab(0);
pickT('die',1,null);
const dx=E('window.D3X');
const dOld=dx.dice.filter(d=>d.match&&d.chip)[1];
const chipRef=dOld&&dOld.chip;
document.getElementById('dressMat').value='obsidian';
applyMat();
out.rebuilt=await until(()=>{
  const dx2=E('window.D3X');
  const dNew=dx2.dice.find(d=>d.chip===chipRef);
  return dNew&&dNew!==dOld&&dNew.mat==='obsidian';},8000);
out.chipClass=chipRef&&/dtype-obsidian/.test(chipRef.className);
/* the P732 baked look is on the GAME screen (no lab layers) */
gw();
const lv=W.document.getElementById('matchLookVig');
out.bakedVig=!!lv&&/0\.61/.test(getComputedStyle(lv).backgroundImage||'');
out.bakedGlowSy=E('D3X.GLOW.sy');
out.bakedSidedim=E('D3X.SIDEDIM_MAX');
out.bakedGrad=E('D3X.SIDEDIM_GRAD');
out.verdict=out.wsOpen&&out.steps>0&&out.noteTyped&&out.rebuilt&&out.chipClass
  &&out.bakedVig&&out.bakedGlowSy===1.24&&out.bakedSidedim===0.82&&out.bakedGrad===0.14;
return out;
