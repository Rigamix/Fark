/* SUITE: exclude. C15: the lab boots the real game and fires a recipe. */
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(fn,ms)=>{const t0=Date.now();while(Date.now()-t0<ms){try{if(fn())return true;}catch(e){}await sleep(100);}return false;};
const out={};
out.frame=!!document.getElementById('game');
/* catalogue builds without a match */
out.catalogue=await until(()=>document.querySelectorAll('#catalogue details').length>5,30000);
out.catCount=document.querySelectorAll('#catalogue details').length;
/* a note saves + exports */
if(out.catalogue){
  saveNote('preserve','test note: amber sets on the tapped die');
  exportAll();
  out.noteExported=/amber sets on the tapped die/.test(document.getElementById('exportBox').value);
}
await setup();
out.matchReady=await until(()=>{const g=E('G');return g&&g.phase==='idle';},4000);
out.labLog=document.getElementById('log').textContent.slice(0,300);
out.frameURL=(()=>{try{return document.getElementById('game').contentWindow.location.pathname;}catch(e){return 'CROSS:'+e;}})();
if(!out.matchReady)return out;
document.getElementById('cardPick').value='preserve';addCard();
document.getElementById('cardPick').value='honeytrap';document.getElementById('tierPick').value='2';addCard();
roll();
const w=document.getElementById('game').contentWindow;
await until(()=>{const dx=E('window.D3X');
  return dx.dice.filter(d=>d.match).every(d=>!d.roll)&&dx.dice.some(d=>d.match&&d.phys);},20000);
await sleep(800);
r_amberSet();
await sleep(600);
out.amberOverlay=!!w.document.querySelector('.labAmber');
out.cards=w.document.querySelectorAll('#famRowP .fcv').length;
out.verdict=out.matchReady&&out.amberOverlay&&out.cards===2&&out.catalogue&&out.noteExported;
return out;
