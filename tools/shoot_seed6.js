/* the seed six are seatable, their portraits load, and their lines fire */
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(fn,ms)=>{const t0=Date.now();while(Date.now()-t0<ms){try{if(fn())return true;}catch(e){}await sleep(60);}return false;};
const vis=el=>{if(!el||!el.isConnected)return false;const s=getComputedStyle(el),r=el.getBoundingClientRect();
 return s.display!=='none'&&s.visibility!=='hidden'&&+s.opacity>0.05&&r.width>1&&r.height>1;};
const tap=el=>{if(!vis(el))return false;const r=el.getBoundingClientRect();
 const o={bubbles:true,cancelable:true,clientX:r.left+r.width/2,clientY:r.top+r.height/2};
 el.dispatchEvent(new PointerEvent('pointerdown',o));el.dispatchEvent(new PointerEvent('pointerup',o));
 el.dispatchEvent(new MouseEvent('click',o));return true;};
tap(document.getElementById('hsBtnBottom'));await sleep(1800);
await until(()=>{const d=document.querySelector('.nrdie');return d&&d._floatDone;},9000);
tap(document.querySelector('.nrdie'));await sleep(1300);
tap(document.getElementById('nrTakeBtn'));await sleep(2400);
const R={poolSize:PT_ART_POOL.length,pool:PT_ART_POOL.slice(-6)};
/* every portrait resolves */
const probe=async u=>{try{return (await fetch(u)).ok;}catch(e){return false;}};
R.portraits={};
for(const n of PT_ART_POOL){R.portraits[n]=await probe(PT_CHAR+n+PT_CHAR_EXT);}
R.allPortraitsOk=Object.values(R.portraits).every(Boolean);
R.missing=Object.keys(R.portraits).filter(k=>!R.portraits[k]);
/* the seed six have lines under their file names */
R.linesByFileName={};
['odo','ollis','peck','ferrand','fenn','tam'].forEach(id=>{
  R.linesByFileName[id]=PATRON_LINES.filter(r=>String(r.p).indexOf('patron:'+id)===0).length;});
R.noOrphanHollis=PATRON_LINES.filter(r=>String(r.p).indexOf('hollis')>=0).length===0;
/* Ferrand's worked example, both branches */
S.run._dlgStage={};S.run._dlgHeard={};S.run.bossesBeaten=[];
const alive=new Set();for(let i=0;i<40;i++){S.run._dlgStage={};alive.add(_dlgSay('ferrand'));}
S.run.bossesBeaten=['grog'];
const beaten=new Set();for(let i=0;i<40;i++){S.run._dlgStage={};beaten.add(_dlgSay('ferrand'));}
R.ferrand_grogAlive=[...alive];
R.ferrand_grogBeaten=[...beaten];
/* Ollis's three-stage arc */
S.run._dlgStage={};
R.ollisArc=[_dlgSay('ollis'),_dlgSay('ollis'),_dlgSay('ollis')];
return R;
