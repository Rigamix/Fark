/* REFERENCE: a settled die on the first roll of a FIRST match (no purge
   has happened yet). */
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(fn,ms)=>{const t0=Date.now();while(Date.now()-t0<ms){try{if(fn())return true;}catch(e){}await sleep(100);}return false;};
const tap=el=>{if(!el)return false;const r=el.getBoundingClientRect();
  const o={bubbles:true,cancelable:true,clientX:r.left+r.width/2,clientY:r.top+r.height/2};
  el.dispatchEvent(new PointerEvent('pointerdown',o));el.dispatchEvent(new PointerEvent('pointerup',o));
  el.dispatchEvent(new MouseEvent('click',o));return true;};
if(!await until(()=>typeof launchSeat==='function',20000))return {err:'no boot'};
if(typeof _getS==='function')_getS();
window._fkDiscardOk=true;
try{delete S.pendingMatch;}catch(e){}
try{if(S.run&&S.run.night){S.run.night.seatsPlayed=S.run.night.roster.map(()=>false);S.run.night.results=S.run.night.roster.map(()=>null);}}catch(e){}
launchSeat(0);
if(!await until(()=>typeof G!=='undefined'&&G&&G.phase==='idle',15000))return {err:'no match 1'};
await sleep(2200);
/* MATCH 1: roll a few times so the dim cache is genuinely populated */
{const realE0=window._enchRollM;
 for(let i=0;i<4;i++){
   const Q0=[1,5,2,3,4,6];
   window._enchRollM=(m,e)=>Q0.length?Q0.shift():realE0(m,e);
   let ok0=false;for(let r=0;r<3&&!ok0;r++){tap(document.getElementById('btnRoll'));ok0=await until(()=>G.phase==='choosing'||G._endMatchFired,9000);}
   if(G._endMatchFired)break;
   await sleep(700);
   const one=(G.pool||[]).find(d=>!d.committed&&(d.val===1||d.val===5));
   if(one)tap(one.el);await sleep(200);
 }}
const cachedBefore=(D3X._dimOwners||[]).reduce((n,t)=>n+((t&&t.userData&&t.userData.dimMaps)?Object.keys(t.userData.dimMaps).length:0),0);
/* LEAVE -> detach -> purge */
try{showScreen('gauntlet');}catch(e){}
await sleep(1800);
const cachedAfterLeave=(D3X._dimOwners||[]).reduce((n,t)=>n+((t&&t.userData&&t.userData.dimMaps)?Object.keys(t.userData.dimMaps).length:0),0);
/* MATCH 2 */
try{delete S.pendingMatch;}catch(e){}
try{if(S.run&&S.run.night){S.run.night.seatsPlayed=S.run.night.roster.map(()=>false);S.run.night.results=S.run.night.roster.map(()=>null);}}catch(e){}
window._fkDiscardOk=true;
launchSeat(0);
if(!await until(()=>typeof G!=='undefined'&&G&&G.phase==='idle',15000))return {err:'no match 2'};
await sleep(2500);
window._purgeInfo={cachedBefore,cachedAfterLeave};
const Q=[1,2,3,4,5,6];const realE=window._enchRollM;
window._enchRollM=(m,e)=>Q.length?Q.shift():realE(m,e);
let r0=false;for(let r=0;r<3&&!r0;r++){tap(document.getElementById('btnRoll'));r0=await until(()=>G.phase==='choosing',9000);}
await sleep(2600);/* let the dim ramp finish so the dim texture is bound */
const mats=[];
(D3X.dice||[]).forEach(d=>{if(!d.match)return;
  d.obj.traverse(o=>{if(!o.isMesh||!o.material||o.userData.outline)return;
    const m=o.material;
    mats.push({hasMap:!!m.map,imgW:(m.map&&m.map.image)?m.map.image.width:null,
      isLive:!!(m.userData&&m.userData.liveMap&&m.map===m.userData.liveMap)});});});
return {phase:'MATCH 2 (after a purge)',purge:window._purgeInfo,vals:(G.pool||[]).map(d=>d.val),
  materials:mats.length,withMap:mats.filter(m=>m.hasMap).length,
  dimBound:mats.filter(m=>m.hasMap&&!m.isLive).length,
  anyZeroWidth:mats.filter(m=>m.hasMap&&!m.imgW).length};
