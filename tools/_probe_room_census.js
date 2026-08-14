/* Which legacy assets/ pieces are VISIBLE on the room screen? SUITE: exclude */
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
_getS();
showScreen('gauntlet');
await sleep(2500);
const q=sel=>{const e=document.querySelector(sel);return e?vis(e):null;};
const out={
 sign:q('img[src*="ui_sign_hang"]'),
 pouch:q('img[src*="Menu_Art/pouch"]'),
 plaque:q('#marksPlaque'),
 bossShadow:q('#bossShadow'),
 chalk:q('.chalkboard'),
 navBeer:q('#screen-gauntlet img[src*="beer.png"]'),
 tierBossPortrait:q('#tierBossPortrait img'),
 tierBossPortraitSrc:(document.querySelector('#tierBossPortrait img')||{src:''}).src.split('/').slice(-2).join('/'),
 seatFrames:q('img[src*="ui_frame_port"]'),
 innkeep:q('img[src*="char_innkeep"]'),
 roomBg:getComputedStyle(document.getElementById('screen-gauntlet')).backgroundImage.slice(0,80)};
return out;
