const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(fn,ms)=>{const t0=Date.now();while(Date.now()-t0<ms){try{if(fn())return true;}catch(e){}await sleep(120);}return false;};
const tap=el=>{if(!el)return false;const r=el.getBoundingClientRect();
  const o={bubbles:true,cancelable:true,clientX:r.left+r.width/2,clientY:r.top+r.height/2};
  el.dispatchEvent(new PointerEvent('pointerdown',o));
  el.dispatchEvent(new PointerEvent('pointerup',o));
  el.dispatchEvent(new MouseEvent('click',o));return true;};
if(!await until(()=>typeof launchBossMatch==='function',20000))return {err:'no boot'};
_getS();window._fkDiscardOk=true;
S.run.tier=1;S.run.gold=500;S.run.sleeve=null;
try{delete S.pendingMatch;}catch(e){}
launchBossMatch();
await until(()=>typeof G!=='undefined'&&G&&G.phase==='idle',15000);
await sleep(2000);
const Q=[];for(let i=0;i<20;i++)Q.push(i%2?5:1);
const realE=window._enchRollM;window._enchRollM=(m,e)=>Q.length?Q.shift():realE(m,e);
for(let i=0;i<3;i++){if(G.phase==='idle'){tap(document.getElementById('btnRoll'));break;}await sleep(400);}
await until(()=>G.phase==='choosing',12000);
await sleep(800);
const d=(G.pool||[]).find(x=>!x.committed&&!x.sel&&(x.val===1||x.val===5));
if(d&&d.el)tap(d.el);
await sleep(600);
const b=document.getElementById('btnBank');
return {held:b.classList.contains('mend-held'),disabled:b.classList.contains('disabled'),
        badge:(document.getElementById('mendVal')||{}).textContent,turnPts:G.turnPts};
