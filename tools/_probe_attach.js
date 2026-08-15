/* SUITE: exclude. setup attaches: fresh-profile path AND mid-match path. */
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(fn,ms)=>{const t0=Date.now();while(Date.now()-t0<ms){try{if(fn())return true;}catch(e){}await sleep(100);}return false;};
const out={};
/* leg 1: fresh profile - full walk */
await setup();
out.leg1=await until(()=>{const g=E('G');return g&&g.phase;},4000);
out.gallery1=document.querySelectorAll('#gallery .gcard').length;
/* leg 2: the mid-match attach (Denis's case): reset panels, call setup again */
document.getElementById('gallery').innerHTML='';
_lights=[];
await setup();  /* G is live -> instant attach branch */
out.gallery2=document.querySelectorAll('#gallery .gcard').length;
out.lights2=document.querySelectorAll('#lightRow input[type=range]').length;
out.attachLogged=/ATTACHED/.test(document.getElementById('log').textContent);
out.verdict=out.leg1&&out.gallery1>50&&out.gallery2>50&&out.lights2>0&&out.attachLogged;
return out;
