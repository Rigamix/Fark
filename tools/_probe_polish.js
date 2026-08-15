/* SUITE: exclude. P728 batch verification in one run. */
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(fn,ms)=>{const t0=Date.now();while(Date.now()-t0<ms){try{if(fn())return true;}catch(e){}await sleep(70);}return false;};
const vis=el=>{if(!el||!el.isConnected)return false;const s=getComputedStyle(el),r=el.getBoundingClientRect();
 return s.display!=='none'&&s.visibility!=='hidden'&&+s.opacity>0.05&&r.width>1&&r.height>1;};
const tap=el=>{if(!vis(el))return false;const r=el.getBoundingClientRect();
 const o={bubbles:true,cancelable:true,clientX:r.left+r.width/2,clientY:r.top+r.height/2};
 el.dispatchEvent(new PointerEvent('pointerdown',o));el.dispatchEvent(new PointerEvent('pointerup',o));
 el.dispatchEvent(new MouseEvent('click',o));return true;};
const out={};
tap(document.getElementById('hsBtnBottom'));await sleep(2000);
await until(()=>document.querySelector('.nrdie'),9000);await sleep(500);
tap(document.querySelector('.nrdie'));await sleep(1200);
tap(document.getElementById('nrTakeBtn'));await sleep(2400);
await until(()=>typeof launchSeat==='function'&&S&&S.run,9000);
_getS();try{G=null;}catch(e){}
window._fkDiscardOk=true;
launchSeat(0);
if(!await until(()=>typeof G!=='undefined'&&G&&G.phase==='idle',16000))return {err:'no idle'};
/* --- tooltip: font + tip-open hiding --- */
G.pF=[{id:'preserve',tier:1,charges:1,state:{}}];famRenderRow();await sleep(400);
famCardTap(0);await sleep(300);
const body=document.querySelector('#cardFocusTip .cft-body');
out.tipFont=body?getComputedStyle(body).fontFamily.slice(0,30):null;
out.tipOpen=document.getElementById('screen-match').classList.contains('tip-open');
_cardFocusClose();
/* --- announce strip above the dice --- */
setTurnMode(false);setStatusMsg('THE ANNOUNCE RIDES ABOVE THE DICE','gold');
await sleep(200);
const bot=document.getElementById('botStrip'),tl=document.getElementById('throwLine');
out.stripAboveDice=bot&&tl?(bot.getBoundingClientRect().bottom<=tl.getBoundingClientRect().top+2):null;
out.stripBottom=bot?Math.round(bot.getBoundingClientRect().bottom):null;
out.lineTop=tl?Math.round(tl.getBoundingClientRect().top):null;
/* --- bank-to-win latch --- */
const ctl=document.querySelector('#screen-match .controls'),bank=document.getElementById('btnBank');
bank.classList.add('bank-to-win');if(ctl)ctl.classList.add('bank-to-win');
G._lastBankForDlg=0;G.kept=[];G.turnPts=0;
try{handleYield();}catch(e){out.yieldErr=String(e).slice(0,80);}
await sleep(300);
out.latch=!!G._bankedToWin;
setBtns(true,false);
out.latchHeld=bank.classList.contains('bank-to-win');
/* --- shelf: loHud hidden + slots fade on focus --- */
S.run.fcards=S.run.fcards&&S.run.fcards.length?S.run.fcards:[{id:'preserve',tier:1}];
famLoadoutShow();await sleep(900);
const hud=document.getElementById('loHud');
out.loHudHidden=hud?getComputedStyle(hud).display==='none':'no-hud';
const card=document.querySelector('#loCardPlane .loCard');
if(card){tap(card);await sleep(600);
  const plane=document.getElementById('loCardPlane');
  const slot=document.querySelector('#loCardPlane .loSlot');
  out.planeFlat=plane?plane.classList.contains('flat'):null;
  out.slotFaded=slot?+getComputedStyle(slot).opacity:null;
}else out.planeFlat='no-card';
try{_loUnfocus();}catch(e){}
/* --- ench window-shop: plaque when broke, tray when rich --- */
if(!document.getElementById('gbShop')){const d=document.createElement('div');d.id='gbShop';document.body.appendChild(d);}
const ekey=Object.keys(ENCHANTS)[0];
S.run.gold=0;
_stEnchTap(ekey);await sleep(200);
const tray=document.getElementById('stEnchPickTray');
out.brokePlaque=tray?/NOT ENOUGH/.test(tray.textContent):null;
out.brokeDice=tray?tray.querySelectorAll('.stPickDie').length:null;
_stEnchPickClose();
S.run.gold=99999;
_stEnchTap(ekey);await sleep(200);
const tray2=document.getElementById('stEnchPickTray');
out.richDice=tray2?tray2.querySelectorAll('.stPickDie').length:null;
_stEnchPickClose();
out.verdict=/Raritas/.test(out.tipFont||'')&&out.tipOpen&&out.stripAboveDice===true
 &&out.latch&&out.latchHeld&&out.loHudHidden===true&&out.planeFlat===true&&out.slotFaded===0
 &&out.brokePlaque===true&&out.brokeDice===0&&out.richDice>0;
return out;
