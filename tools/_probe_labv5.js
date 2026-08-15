/* SUITE: exclude. v5 UI: tabs, lights, audio mute, dresser, gallery,
 * studio focus, sequencer wiring. */
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(fn,ms)=>{const t0=Date.now();while(Date.now()-t0<ms){try{if(fn())return true;}catch(e){}await sleep(100);}return false;};
const out={};
await setup();
if(!await until(()=>{const g=E('G');return g&&g.phase==='idle';},4000))return {err:'no match'};
/* lights built */
out.lights=document.querySelectorAll('#lightRow input[type=range]').length;
lightSet(0,50);
out.lightDimmed=_lights[0]&&_lights[0].intensity<(_lights[0].userData._lab0||1);
envSet(80);
gw();
const envImg=[...W.document.querySelectorAll('#screen-match img')].find(im=>!im.closest('#playerDiceRow,#oppDiceRow,#keptRow,#famRowP,#famRowO'));
out.envFiltered=envImg?/brightness/.test(envImg.style.filter):null;
const diceImg=W.document.querySelector('#playerDiceRow img');
out.diceUntouched=diceImg?!/brightness/.test(diceImg.style.filter||''):true;
sideSet(70);
out.sidedim=E('D3X.SIDEDIM_MAX');
/* audio muted by default */
out.audioMuted=[...W.document.querySelectorAll('audio')].every(a=>a.muted);
/* dresser */
pickT('die',0,null);
applyEnch();
out.enchSet=(E('S.run.dieEnch')||[])[0];
/* gallery + studio */
out.gallery=document.querySelectorAll('#gallery .gcard').length;
openStudio('preserve');
await sleep(600);
out.wsOpen=document.getElementById('ws').classList.contains('on');
out.galHidden=document.getElementById('galSec').style.display==='none';
out.dealt=((E('G')||{}).pF||[]).some(x=>x.id==='preserve');
out.steps=document.querySelectorAll('#seqLane .step').length;
/* sequencer drop wiring (synthetic event) */
laneDrop({preventDefault(){},dataTransfer:{getData:()=>'sound:chime'}});
out.stepsAfterDrop=document.querySelectorAll('#seqLane .step').length;
stepPick(rec.fx.length-1);
out.editorOpen=document.getElementById('stepEd').classList.contains('on');
/* motion drop */
laneDrop({preventDefault(){},dataTransfer:{getData:()=>'motion:pop'}});
out.motionKeys=rec.keys.length;
try{studioPlay();out.playOk=true;}catch(e){out.playOk=String(e).slice(0,60);}
await sleep(400);
showTab(1);
out.verdict=out.lights>0&&out.lightDimmed&&out.envFiltered&&out.diceUntouched
  &&Math.abs(out.sidedim-0.7)<0.01&&out.audioMuted&&!!out.enchSet
  &&out.gallery>50&&out.wsOpen&&out.galHidden&&out.dealt
  &&out.stepsAfterDrop>out.steps&&out.editorOpen&&out.motionKeys>1&&out.playOk===true;
return out;
