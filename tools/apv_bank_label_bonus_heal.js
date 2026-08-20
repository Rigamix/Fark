/* P819 probe B (tell neutralized to isolate the label logic).
 * Leg 1: hair-of-the-dog armed - a 100 selection captions '+200'.
 * Leg 2: slow_cook 3-roll turn - the caption carries the simmer pot.
 * Leg 3: tier-3 tamper (+300 steal) flips BANK -> BANK TO WIN with NO
 * die toggle in between (updHUD now heals the label). */
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(fn,ms)=>{const t0=Date.now();while(Date.now()-t0<ms){try{if(fn())return true;}catch(e){}await sleep(120);}return false;};
const tap=el=>{if(!el)return false;const r=el.getBoundingClientRect();
  const o={bubbles:true,cancelable:true,clientX:r.left+r.width/2,clientY:r.top+r.height/2};
  el.dispatchEvent(new PointerEvent('pointerdown',o));
  el.dispatchEvent(new PointerEvent('pointerup',o));
  el.dispatchEvent(new MouseEvent('click',o));return true;};
const label=()=>({verb:(document.getElementById('bankVerb')||{}).textContent||'',
  cap:(document.getElementById('bankCap')||{}).textContent||'',
  win:document.getElementById('btnBank').classList.contains('bank-to-win')});
if(!await until(()=>typeof launchSeat==='function'&&typeof G!=='undefined'&&typeof S!=='undefined',20000))return {err:'no boot'};
if(typeof _getS==='function')_getS();
S.run._hotdNext=true;try{save();}catch(e){}
launchSeat(0);
if(!await until(()=>G&&G.phase==='idle',14000))return {err:'no match'};
await sleep(3000);
G._tell=null;G._sealRule=null;/* isolate: no last_call on this table */
G.pF=[{id:'slow_cook',tier:1,charges:0,state:{}},{id:'tamper',tier:3,charges:1,state:{}}];
G.oF=[{id:'retort',tier:1,charges:0,state:{}}];
try{famRenderRow();}catch(e){}
const Q=[1,2,3,4,6,6];
const realE=window._enchRollM;
window._enchRollM=(m,e)=>Q.length?Q.shift():realE(m,e);
/* LEG 1: hotd caption */
tap(document.getElementById('btnRoll'));
if(!await until(()=>G.phase==='choosing',15000))return {err:'no roll 1'};
await sleep(600);
tap(G.pool.find(d=>!d.committed&&d.val===1).el);await sleep(400);
const hotdLabel=label();/* '+200' for a 100 selection */
tap(document.getElementById('btnBank'));
if(!await until(()=>G.pPts>0,15000))return {err:'no bank 1',hotdLabel};
const hotdPaid=G.pPts;/* 200 */
/* LEG 2: slow_cook pot in the caption */
if(!await until(()=>G.phase==='idle'&&(G.turnNum||0)>=2,90000))return {err:'no turn 2',hotdLabel};
await sleep(2000);
G._tell=null;/* startPTurn may have re-read the seat; keep the table neutral */
[1,2,3,4,6,6].forEach(v=>Q.push(v));
tap(document.getElementById('btnRoll'));
if(!await until(()=>G.phase==='choosing'&&(G.turnRollCount||0)===1,15000))return {err:'no roll 2a'};
await sleep(400);
const keep=async(next)=>{const d=G.pool.find(x=>!x.committed&&(x.val===1||x.val===5));
  if(!d)return false;tap(d.el);await sleep(250);next.forEach(v=>Q.push(v));
  tap(document.getElementById('btnRoll'));
  if(!await until(()=>G.phase==='choosing',15000))return false;await sleep(400);return true;};
if(!await keep([1,2,3,4,6]))return {err:'roll 2b'};
if(!await keep([5,2,3,4]))return {err:'roll 2c'};
tap(G.pool.find(x=>!x.committed&&x.val===5).el);await sleep(400);
const cookLabel=label();/* turnPts 250 + acc 150 = '+400' */
const accNow=(G.pF[0].state&&G.pF[0].state.acc)||0;
tap(document.getElementById('btnBank'));
if(!await until(()=>G.phase==='idle'&&(G.turnNum||0)>=3,90000))return {err:'no turn 3',cookLabel,accNow};
await sleep(2000);
/* LEG 3: tamper heals the label with no toggle */
G._tell=null;
G.pPts=(G.target||3700)-350;try{updHUD();}catch(e){}
[1,2,3,4,6,6].forEach(v=>Q.push(v));
tap(document.getElementById('btnRoll'));
if(!await until(()=>G.phase==='choosing'&&(G.turnRollCount||0)===1,15000))return {err:'no roll 3'};
await sleep(600);
tap(G.pool.find(d=>!d.committed&&d.val===1).el);await sleep(400);
const beforeTamper=label();/* pPts+100 < target: plain BANK */
const tamperIdx=G.pF.findIndex(c=>c.id==='tamper');
famUse(tamperIdx);
await sleep(500);
const afterTamper=label();/* +300 landed: BANK TO WIN, no toggle */
return {hotdLabel,hotdPaid,cookLabel,accNow,beforeTamper,afterTamper,
  verdicts:{
    hotdCaptionDoubles:hotdLabel.cap==='+200',
    hotdActuallyPaid200:hotdPaid===200,
    cookCaptionCarriesPot:cookLabel.cap==='+400'&&accNow===150,
    tamperBefore:beforeTamper.verb==='BANK'&&!beforeTamper.win,
    tamperHealsToWin:afterTamper.verb==='BANK TO WIN'&&afterTamper.win},
  verdict:hotdLabel.cap==='+200'&&hotdPaid===200&&cookLabel.cap==='+400'
    &&!beforeTamper.win&&afterTamper.win};
