/* DICE-FEEL instrument: bust a five-die spread of mixed faces and read
 * (1) per-die flatness AFTER the kick settles - the engine's own
 * _cocked(q) is the judge; (2) the scatter geometry (x-spread from
 * the impact, kick distances); (3) min pairwise XZ distance of the
 * SETTLED pre-bust pile (the spacing question). Run before and after
 * P821: prediction pre-patch is only faces 2/5 stay flat. */
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(fn,ms)=>{const t0=Date.now();while(Date.now()-t0<ms){try{if(fn())return true;}catch(e){}await sleep(120);}return false;};
const tap=el=>{if(!el)return false;const r=el.getBoundingClientRect();
  const o={bubbles:true,cancelable:true,clientX:r.left+r.width/2,clientY:r.top+r.height/2};
  el.dispatchEvent(new PointerEvent('pointerdown',o));
  el.dispatchEvent(new PointerEvent('pointerup',o));
  el.dispatchEvent(new MouseEvent('click',o));return true;};
if(!await until(()=>typeof launchSeat==='function'&&typeof G!=='undefined',20000))return {err:'no boot'};
launchSeat(0);
if(!await until(()=>G&&G.phase==='idle',14000))return {err:'no match'};
await sleep(3000);
G.pF=[];try{famRenderRow();}catch(e){}
const Q=[1,2,3,4,6,6];
const realE=window._enchRollM;
window._enchRollM=(m,e)=>Q.length?Q.shift():realE(m,e);
tap(document.getElementById('btnRoll'));
if(!await until(()=>G.phase==='choosing',15000))return {err:'no roll'};
/* wait for the PHYSICS rest, then measure the pile spacing */
await until(()=>window.D3X&&D3X.dice.some(d=>d.match&&d.phys),9000);
await sleep(2200);
const pile=D3X.dice.filter(d=>d.match&&d.phys&&!d.dead);
const pos0=pile.map(d=>({v:d.phys.v,x:d.phys.x,z:d.phys.z}));
let minPair=99;
for(let i=0;i<pos0.length;i++)for(let j=i+1;j<pos0.length;j++){
  const dx=pos0[i].x-pos0[j].x,dz=pos0[i].z-pos0[j].z;
  minPair=Math.min(minPair,Math.hypot(dx,dz));}
await sleep(300);
tap(G.pool.find(d=>!d.committed&&d.val===1).el);await sleep(300);
/* the dead roll -> bust; faces 2,3,4,6,6 scatter */
[2,3,4,6,6].forEach(v=>Q.push(v));
const t0=performance.now();
tap(document.getElementById('btnRoll'));
/* catch the dice DURING the kick - the rival turn wipes the row */
if(!await until(()=>window.D3X&&D3X.dice.some(d=>d.kick),20000))return {err:'no kick seen',phase:G.phase};
/* the rival's next throw clears .kick fast - sample every 200ms and
   keep the LAST non-empty snapshot (later samples = further into the
   ease, more settled) */
let snap=null,snapT=0;
for(let k=0;k<10;k++){
  await sleep(200);
  const cur=D3X.dice.filter(d=>d.match&&d.phys&&d.kick);
  if(cur.length){snap=cur.map(d=>{
    /* THREE-side flatness: a cube lies flat iff one local axis is within
       ~10 deg of world up (cos 0.985) */
    const q=d.obj.quaternion;let best=0;
    [[1,0,0],[-1,0,0],[0,1,0],[0,-1,0],[0,0,1],[0,0,-1]].forEach(a=>{
      const v=new THREE.Vector3(a[0],a[1],a[2]).applyQuaternion(q);
      if(v.y>best)best=v.y;});
    return {v:d.phys.v,up:+best.toFixed(3),cocked:best<0.985,x:d.obj.position.x};});snapT=(k+1)*200;}
}
const busted=[];/* superseded by snap */
const impact=D3X._lastImpact||null;
const flat=snap||[];
const spread=(snap&&snap.length)?Math.max(...snap.map(d=>Math.abs(d.x-((impact&&impact.x)||0)))):0;
const cockedByFace={};
flat.forEach(f=>{const k=String(f.v);cockedByFace[k]=cockedByFace[k]||[];cockedByFace[k].push(!!f.cocked);});
return {minPairPreBust:+minPair.toFixed(3),impact,flat,snapT,spread:+spread.toFixed(2),
  kickMs:(D3X.KICK||{}).ms,kickDist:(D3X.KICK||{}).dist,
  allFlat:flat.length>0&&flat.every(f=>f.cocked===false),
  cockedByFace};
