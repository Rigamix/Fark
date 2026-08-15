/* SUITE: exclude. C15c QA: presets exist for all three kinds + fallback,
 * load populates, play moves the target, rounded shell renders. */
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(fn,ms)=>{const t0=Date.now();while(Date.now()-t0<ms){try{if(fn())return true;}catch(e){}await sleep(100);}return false;};
const out={};
await until(()=>document.querySelectorAll('#catalogue details').length>5,30000);
out.catCount=document.querySelectorAll('#catalogue details').length;
await setup();
if(!await until(()=>{const g=E('G');return g&&g.phase==='idle';},4000))return {err:'no match',...out};
roll();
await until(()=>{const dx=E('window.D3X');
  return dx.dice.filter(d=>d.match).every(d=>!d.roll)&&dx.dice.some(d=>d.match&&d.phys);},20000);
await sleep(500);
/* presets resolve for a card, a mat, an ench, and an UNKNOWN card via fallback */
out.pCard=!!labPreset('preserve');
out.pMat=!!labPreset('mat:obsidian');
out.pEnch=!!labPreset('ench:ward');
const unk=labPreset('steady_hand');   /* not in ID_META -> famDef fallback */
out.pFallback=!!unk&&/family default/.test(unk.notes);
/* load fallback populates the tables */
document.getElementById('recCard').value='preserve';
loadRecipe();
out.loadedKeys=rec.keys.length;out.loadedFx=rec.fx.length;
out.notes=document.getElementById('recNotes').value.slice(0,40);
/* play moves the die */
pickT('die',0,null);
const el=tEl();const before=el.style.scale;
playRecipe();
await sleep(200);
out.movedMidPlay=el.style.scale!==''&&el.style.scale!==before;
await sleep(800);
/* the SET preset's amberShell fired during play - rounded geometry */
const dx=E('window.D3X');
const d0=dx.dice.filter(d=>d.match&&d.chip)[0];
const sh=d0&&d0.obj.getObjectByName('labShell');
out.shell=!!sh;
out.shellRounded=!!(sh&&sh.geometry.attributes.position.count>=100); /* seg-4 rounded box = 150 verts; the flat clone path no longer exists */
out.verdict=out.catCount>50&&out.pCard&&out.pMat&&out.pEnch&&out.pFallback
  &&out.loadedKeys>=3&&out.loadedFx>=3&&out.movedMidPlay&&out.shell&&out.shellRounded;
return out;
