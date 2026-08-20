/* P827/P825: stargazer's ghost faces + honeytrap's honey marks +
 * the live-state cards + the standing chips, driven through famUse.
 * Ghost lifecycle: present after the peek (one per free die, texts =
 * the promises), GONE after the roll consumes them. */
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
G.pF=[{id:'stargazer',tier:1,charges:1,state:{}},
      {id:'honeytrap',tier:1,charges:1,state:{}},
      {id:'reprisal',tier:1,charges:0,state:{}},
      {id:'slow_cook',tier:1,charges:0,state:{}}];
G._forKeeps=true;
G.oPts=1500;/* reprisal's live gate open */
try{famRenderRow();}catch(e){}
await sleep(300);
/* P825: reprisal card armed-look while trailing; for_keeps chip standing */
const repCard=document.querySelector('#famRowP .fcv.armed');
const fkChip=(document.getElementById('famAux')||{}).textContent||'';
const Q=[5,5,2,3,4,6];
const realE=window._enchRollM;
window._enchRollM=(m,e)=>Q.length?Q.shift():realE(m,e);
tap(document.getElementById('btnRoll'));
if(!await until(()=>G.phase==='choosing'&&(G.turnRollCount||0)===1,15000))return {err:'no roll'};
await sleep(700);
/* STARGAZER: peek -> ghosts over every free die, texts = promises */
famUse(0);
await sleep(400);
const ghosts=[...document.querySelectorAll('.peek-float')];
const promises=(G._famPeekVals||[]).map(p=>String(p.val));
const ghostTexts=ghosts.map(g=>g.textContent);
const ghostsMatch=ghosts.length===promises.length&&ghostTexts.join(',')===promises.join(',');
/* HONEYTRAP: keep the pair of 5s (select both), arm -> marks on both */
const fives=G.pool.filter(d=>!d.committed&&d.val===5);
tap(fives[0].el);await sleep(150);tap(fives[1].el);await sleep(250);
famUse(1);
await sleep(400);
const marks=document.querySelectorAll('.honey-float').length;
/* roll: forces consumed -> ghosts AND marks cleared */
[1,2,3,4].forEach(v=>Q.push(v));
tap(document.getElementById('btnRoll'));
if(!await until(()=>G.phase==='choosing'&&(G.turnRollCount||0)===2,20000))return {err:'no roll 2',ghosts:ghosts.length};
await sleep(700);
const ghostsAfter=document.querySelectorAll('.peek-float').length;
const marksAfter=document.querySelectorAll('.honey-float').length;
/* SLOW COOK chip after accrual: roll to rc>=3 with the simmering chip */
const k1=G.pool.find(d=>!d.committed&&(d.val===1||d.val===5));
tap(k1.el);await sleep(250);
[1,2,3].forEach(v=>Q.push(v));
tap(document.getElementById('btnRoll'));
if(!await until(()=>G.phase==='choosing'&&(G.turnRollCount||0)===3,20000))return {err:'no roll 3'};
await sleep(600);
const auxNow=(document.getElementById('famAux')||{}).textContent||'';
return {repArmed:!!repCard,fkChip:fkChip.indexOf('FOR KEEPS')>=0,
  ghosts:ghosts.length,promises:promises.length,ghostsMatch,
  marks,ghostsAfter,marksAfter,
  simmerChip:auxNow.indexOf('SIMMERING')>=0,acc:(G.pF[3].state&&G.pF[3].state.acc)||0,
  verdicts:{
    reprisalReadsLive:!!repCard,
    forKeepsChipStands:fkChip.indexOf('FOR KEEPS')>=0,
    ghostsShowThePromises:ghostsMatch&&ghosts.length>0,
    honeyMarksThePair:marks===2,
    rollClearsBoth:ghostsAfter===0&&marksAfter===0,
    simmerChipTracks:auxNow.indexOf('SIMMERING')>=0},
  verdict:!!repCard&&fkChip.indexOf('FOR KEEPS')>=0&&ghostsMatch&&marks===2
    &&ghostsAfter===0&&marksAfter===0&&auxNow.indexOf('SIMMERING')>=0};
