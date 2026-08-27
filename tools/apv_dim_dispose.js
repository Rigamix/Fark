/* P859: the dim textures are freed at the layer's teardown, so a
 * SECOND match does not inherit the first's. The claim is about
 * retention ACROSS matches, so the probe must cross one. */
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(fn,ms)=>{const t0=Date.now();while(Date.now()-t0<ms){try{if(fn())return true;}catch(e){}await sleep(100);}return false;};
const tap=el=>{if(!el)return false;const r=el.getBoundingClientRect();
  const o={bubbles:true,cancelable:true,clientX:r.left+r.width/2,clientY:r.top+r.height/2};
  el.dispatchEvent(new PointerEvent('pointerdown',o));el.dispatchEvent(new PointerEvent('pointerup',o));
  el.dispatchEvent(new MouseEvent('click',o));return true;};
if(!await until(()=>typeof launchSeat==='function',20000))return {err:'no boot'};
if(typeof _getS==='function')_getS();
window._fkDiscardOk=true;
const tex=()=>(D3X.renderer&&D3X.renderer.info&&D3X.renderer.info.memory)?D3X.renderer.info.memory.textures:null;
const owners=()=>(D3X._dimOwners||[]).length;
const cached=()=>{let n=0;(D3X._dimOwners||[]).forEach(t=>{if(t&&t.userData&&t.userData.dimMaps)n+=Object.keys(t.userData.dimMaps).length;});return n;};
const playMatch=async(rolls)=>{
  let ok=false;
  for(let a=0;a<5&&!ok;a++){
    if(a>0){try{showScreen('gauntlet');}catch(e){}await sleep(700);}
    try{delete S.pendingMatch;}catch(e){}
    try{if(S.run&&S.run.night){S.run.night.seatsPlayed=S.run.night.roster.map(()=>false);S.run.night.results=S.run.night.roster.map(()=>null);}}catch(e){}
    window._fkDiscardOk=true;
    try{launchSeat(0);}catch(e){}
    ok=await until(()=>typeof G!=='undefined'&&G&&G.phase==='idle'&&(G.pool||[]).length===0,9000);
    if(!ok)await sleep(1200);
  }
  if(!ok)return false;
  await sleep(2200);
  window._atMatchStart={textures:tex(),owners:owners(),cached:cached()};
  const realE=window._enchRollM;
  for(let i=0;i<rolls;i++){
    const Q=[1,5,2,3,4,6];
    window._enchRollM=(m,e)=>Q.length?Q.shift():realE(m,e);
    let r0=false;for(let r=0;r<3&&!r0;r++){tap(document.getElementById('btnRoll'));r0=await until(()=>G.phase==='choosing'||G.phase==='opp'||G._endMatchFired,9000);}
    if(G._endMatchFired)break;
    await sleep(500);
    const one=(G.pool||[]).find(d=>!d.committed&&(d.val===1||d.val===5));
    if(one)tap(one.el);await sleep(200);
    if((G.pool||[]).filter(d=>!d.committed).length<=2){tap(document.getElementById('btnBank'));
      const iv=setInterval(()=>{try{if(G&&(G.phase==='opp'||G._oppTurnActive))G._ffMult=0.05;}catch(e){}},120);
      await until(()=>G.phase==='idle'&&!G._oppTurnActive,40000);clearInterval(iv);await sleep(300);}
  }
  return true;};
if(!await playMatch(8))return {err:'match 1 failed'};
const afterM1={textures:tex(),owners:owners(),cached:cached()};
/* leave the match the way the game does */
try{showScreen('gauntlet');}catch(e){}
await sleep(1500);
const afterLeave={textures:tex(),owners:owners(),cached:cached()};
if(!await playMatch(8))return {afterM1,afterLeave,err:'match 2 failed'};
const m2Start=window._atMatchStart;
const afterM2={textures:tex(),owners:owners(),cached:cached()};
return {afterM1,afterLeave,afterM2,
  freedOnLeave:afterM1.cached-afterLeave.cached,
  secondMatchInherited:afterLeave.cached,
  verdicts:{
    cacheBuiltInMatch1:afterM1.cached>10,
    purgedOnLeave:afterLeave.cached===0&&afterLeave.owners===0,
    /* the CLAIM is retention, not cache population: match 2 must BEGIN
       from a purged baseline. Comparing the two matches' absolute counts
       measures which die values happened to come up, not stacking - an
       earlier draft of this assert did that and failed a working fix. */
    secondMatchStartsClean:m2Start&&m2Start.cached===0&&m2Start.owners===0},
  m2Start,
  verdict:afterM1.cached>10&&afterLeave.cached===0&&afterLeave.owners===0
    &&!!(m2Start&&m2Start.cached===0&&m2Start.owners===0)};
