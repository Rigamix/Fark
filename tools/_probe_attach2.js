const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(fn,ms)=>{const t0=Date.now();while(Date.now()-t0<ms){try{if(fn())return true;}catch(e){}await sleep(100);}return false;};
const out={};
await setup();
out.leg1=await until(()=>{const g=E('G');return g&&g.phase;},4000);
/* diagnose the fast branch primitives directly */
out.gDirect=(()=>{try{const g=E('G');return g?String(g.phase):'null';}catch(e){return 'E-threw:'+e;}})();
document.getElementById('gallery').innerHTML='';
document.getElementById('lightRow').innerHTML='';
const logBefore=document.getElementById('log').textContent.length;
try{await setup();out.setup2='returned';}catch(e){out.setup2='THREW: '+String(e).slice(0,120);}
out.leg2log=document.getElementById('log').textContent.slice(0,document.getElementById('log').textContent.length-logBefore).split('\n').slice(0,6);
out.gallery2=document.querySelectorAll('#gallery .gcard').length;
out.lights2=document.querySelectorAll('#lightRow input[type=range]').length;
return out;
