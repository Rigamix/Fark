/* P718: For Keeps seats its prize; Fair Trade is gone everywhere.
 * SUITE: exclude */
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(fn,ms)=>{const t0=Date.now();while(Date.now()-t0<ms){try{if(fn())return true;}catch(e){}await sleep(60);}return false;};
const vis=el=>{if(!el||!el.isConnected)return false;const s=getComputedStyle(el),r=el.getBoundingClientRect();
 return s.display!=='none'&&s.visibility!=='hidden'&&+s.opacity>0.05&&r.width>1&&r.height>1;};
const tap=el=>{if(!vis(el))return false;const r=el.getBoundingClientRect();
 const o={bubbles:true,cancelable:true,clientX:r.left+r.width/2,clientY:r.top+r.height/2};
 el.dispatchEvent(new PointerEvent('pointerdown',o));el.dispatchEvent(new PointerEvent('pointerup',o));
 el.dispatchEvent(new MouseEvent('click',o));return true;};
await until(()=>window.D3X&&D3X.frame,9000);
for(let a=0;a<3;a++){tap(document.getElementById('hsBtnBottom'));await sleep(2000);
 await until(()=>document.querySelector('.nrdie'),9000);await sleep(500);
 tap(document.querySelector('.nrdie'));await sleep(1200);
 tap(document.getElementById('nrTakeBtn'));await sleep(2400);
 if(await until(()=>typeof launchSeat==='function'&&S&&S.run,9000))break;}
_getS();try{G=null;}catch(e){}
window._fkDiscardOk=true;
launchSeat(0);
let ok=await until(()=>typeof G!=='undefined'&&G&&G.phase==='idle',16000);
if(!ok){try{G=null;}catch(e){}launchSeat(0);
 ok=await until(()=>typeof G!=='undefined'&&G&&G.phase==='idle',16000);}
if(!ok)return {err:'no idle'};
try{dbgWin();}catch(e){}
await until(()=>vis(document.getElementById('end-ov')),9000);
await sleep(2000);
const out={};
out.ftGone={def:!famDef('fair_trade'),live:!FAM_LIVE.fair_trade};
/* the draft can never deal it */
let dealt=false;
for(let i=0;i<25;i++){const o=famOffer(false);if(o.some(x=>x&&x.id==='fair_trade')){dealt=true;break;}}
out.ftGone.neverDealt=!dealt;

/* drive the For Keeps take on this win screen */
const diceBefore=S.run.dice.slice();
S.run.dieEnch=S.run.dieEnch||diceBefore.map(()=>null);
S.run.dieEnch[2]={t:'ward'};save();/* a brand on the seat we will replace */
window._fkPool=['iron','bone'];window._fkLucky=null;window._fkPersona='aggro';
famFkTake(0);
await sleep(400);
const rc=document.querySelector('#end-ov .res-card');
out.offer={shown:rc.innerHTML.indexOf('IS YOURS')>=0&&rc.innerHTML.indexOf('tap the die it replaces')>=0,
 seats:rc.querySelectorAll('.seat-die').length};
_fkSeatDo(2);
await sleep(300);
out.swap={seated:S.run.dice[2]==='iron',othersHeld:S.run.dice.every((m,i)=>i===2||m===diceBefore[i]),
 enchCleared:S.run.dieEnch[2]===null,
 msg:rc.innerHTML.indexOf('TAKES THE SEAT')>=0,brandNote:rc.innerHTML.indexOf('brand goes with it')>=0,
 taken:window._fkTaken===null||window._fkTaken===undefined};

/* the lucky path stays a trophy */
window._fkPool=['lucky'];window._fkLucky='Old Bess';window._fkPersona='sly';
famFkTake(0);
await sleep(200);
out.lucky={msg:rc.innerHTML.indexOf('OLD BESS')>=0||rc.innerHTML.indexOf('Old Bess')>=0,
 named:(S.run.luckyNames||[]).indexOf('Old Bess')>=0,
 notSeated:S.run.dice.indexOf('lucky')<0};

out.verdict=out.ftGone.def&&out.ftGone.live&&out.ftGone.neverDealt
 &&out.offer.shown&&out.offer.seats===S.run.dice.length
 &&out.swap.seated&&out.swap.othersHeld&&out.swap.enchCleared&&out.swap.msg
 &&out.swap.brandNote&&out.lucky.msg&&out.lucky.named&&out.lucky.notSeated;
return out;
