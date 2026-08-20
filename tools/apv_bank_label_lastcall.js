/* P819 probe A, on Grog's LAST CALL seat.
 * Leg 1: keep a 1 - the projection must refuse (caption EMPTY, plain
 * BANK, no win class) where the old label promised '+100'.
 * Leg 2: triple 1s with pPts preset near target - BANK TO WIN lights,
 * and the WINNING PRESS holds the label through the 700ms to endMatch
 * (the P728 latch, restored). */
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(fn,ms)=>{const t0=Date.now();while(Date.now()-t0<ms){try{if(fn())return true;}catch(e){}await sleep(120);}return false;};
const tap=el=>{if(!el)return false;const r=el.getBoundingClientRect();
  const o={bubbles:true,cancelable:true,clientX:r.left+r.width/2,clientY:r.top+r.height/2};
  el.dispatchEvent(new PointerEvent('pointerdown',o));
  el.dispatchEvent(new PointerEvent('pointerup',o));
  el.dispatchEvent(new MouseEvent('click',o));return true;};
const label=()=>({verb:(document.getElementById('bankVerb')||{}).textContent||'',
  cap:(document.getElementById('bankCap')||{}).textContent||'',
  win:document.getElementById('btnBank').classList.contains('bank-to-win'),
  disabled:document.getElementById('btnBank').classList.contains('disabled')});
if(!await until(()=>typeof launchSeat==='function'&&typeof G!=='undefined',20000))return {err:'no boot'};
launchSeat(0);
if(!await until(()=>G&&G.phase==='idle',14000))return {err:'no match'};
await sleep(3000);
/* the seat's seal is rolled per night - FORCE it so the refusal leg is deterministic (same activation the cursed-table probe drives) */
G._sealRule='last_call';
const lastCallActive=(typeof _ruleActive==='function')&&_ruleActive('last_call','p');
G.pF=[];try{famRenderRow();}catch(e){}
const Q=[1,1,1,2,3,4];
const realE=window._enchRollM;
window._enchRollM=(m,e)=>Q.length?Q.shift():realE(m,e);
G.pPts=(G.target||3700)-1000;try{updHUD();}catch(e){}
tap(document.getElementById('btnRoll'));
if(!await until(()=>G.phase==='choosing',15000))return {err:'no roll'};
await sleep(600);
/* LEG 1: one 1 selected - sub-threshold */
const ones=G.pool.filter(d=>!d.committed&&d.val===1);
tap(ones[0].el);await sleep(400);
const subLabel=label();
/* LEG 2: the full triple - 1000 clears LAST CALL and the target */
tap(ones[1].el);await sleep(150);tap(ones[2].el);await sleep(400);
const winLabel=label();
/* THE WINNING PRESS: the label must hold through the endMatch delay */
tap(document.getElementById('btnBank'));
await sleep(350);/* mid-window */
const midPress=label();
const ended=await until(()=>G._endMatchFired,15000);
return {lastCallActive,subLabel,winLabel,midPress,ended,
  verdicts:{
    sealActive:lastCallActive,
    subThresholdRefusedOnLabel:subLabel.cap===''&&subLabel.verb==='BANK'&&!subLabel.win,
    tripleLightsToWin:winLabel.verb==='BANK TO WIN'&&winLabel.win,
    winningPressHolds:midPress.verb==='BANK TO WIN'&&midPress.win,
    matchEnded:ended},
  verdict:lastCallActive&&subLabel.cap===''&&!subLabel.win&&winLabel.win&&midPress.win&&ended};
