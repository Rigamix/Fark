/* P824: light the fuse for real (3-roll turn, commit on roll 3) and
 * catch the tray smoldering; then bank and see it die. */
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
G.pF=[{id:'short_fuse',tier:1,charges:0,state:{}}];
try{famRenderRow();}catch(e){}
const Q=[1,2,3,4,6,6];
const realE=window._enchRollM;
window._enchRollM=(m,e)=>Q.length?Q.shift():realE(m,e);
const keep=async(next)=>{const d=G.pool.find(x=>!x.committed&&(x.val===1||x.val===5));
  if(!d)return false;tap(d.el);await sleep(250);next.forEach(v=>Q.push(v));
  tap(document.getElementById('btnRoll'));
  if(!await until(()=>G.phase==='choosing',15000))return false;await sleep(400);return true;};
tap(document.getElementById('btnRoll'));
if(!await until(()=>G.phase==='choosing',15000))return {err:'no roll 1'};
await sleep(500);
if(!await keep([1,2,3,4,6]))return {err:'roll 2'};
if(!await keep([5,2,3,4]))return {err:'roll 3'};
/* commit roll 3's 5 by rolling -> lit -> the smolder must come on */
if(!await keep([5,2,3]))return {err:'roll 4'};
const el=document.getElementById('fuseSmolder');
const litOn=await until(()=>el&&el.classList.contains('on'),6000);
await sleep(1000);/* let the pulse breathe for the screenshot */
const op=el?+getComputedStyle(el).opacity:0;
const lit=!!(G.pF[0].state&&G.pF[0].state.lit);
/* bank: the smolder dies with the turn */
const five=G.pool.find(x=>!x.committed&&x.val===5);
if(five){tap(five.el);await sleep(300);}
tap(document.getElementById('btnBank'));
await until(()=>!el.classList.contains('on'),10000);
const offAfterBank=!el.classList.contains('on');
return {litOn,opacity:op,lit,offAfterBank,
  verdicts:{smolderOnWhenLit:litOn&&op>0.9&&lit,smolderDiesAtBank:offAfterBank},
  verdict:litOn&&op>0.9&&offAfterBank};
