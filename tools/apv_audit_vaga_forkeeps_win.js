/* FOR KEEPS, the WIN half: arm the seat chip (S.run._fkArmed), sit
 * down, win fast - the picker must offer the rival's dice; famFkTake
 * seats the prize into _fkTaken and renders the seat offer. */
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(fn,ms)=>{const t0=Date.now();while(Date.now()-t0<ms){try{if(fn())return true;}catch(e){}await sleep(120);}return false;};
const tap=el=>{if(!el)return false;const r=el.getBoundingClientRect();
  const o={bubbles:true,cancelable:true,clientX:r.left+r.width/2,clientY:r.top+r.height/2};
  el.dispatchEvent(new PointerEvent('pointerdown',o));
  el.dispatchEvent(new PointerEvent('pointerup',o));
  el.dispatchEvent(new MouseEvent('click',o));return true;};
if(!await until(()=>typeof launchSeat==='function'&&typeof G!=='undefined'&&typeof S!=='undefined',20000))return {err:'no boot'};
if(typeof _getS==='function')_getS();
S.run._fkArmed=true;try{save();}catch(e){}
launchSeat(0);
if(!await until(()=>G&&G.phase==='idle',14000))return {err:'no match'};
await sleep(3000);
const armed=!!G._forKeeps;
if(!armed)return {err:'not armed',fk:S.run._fkArmed};
const Q=[1,2,3,4,6,2];
const realE=window._enchRollM;
window._enchRollM=(m,e)=>Q.length?Q.shift():realE(m,e);
/* one bank away from the target */
G.pPts=(G.target||2800)-100;try{updHUD();}catch(e){}
tap(document.getElementById('btnRoll'));
if(!await until(()=>G.phase==='choosing',15000))return {err:'no roll'};
await sleep(500);
tap(G.pool.find(d=>!d.committed&&d.val===1).el);await sleep(300);
tap(document.getElementById('btnBank'));
/* the win screen with the picker */
if(!await until(()=>{const ov=document.getElementById('end-ov');return ov&&ov.textContent.indexOf('FOR KEEPS')>=0;},25000))return {err:'no picker',emf:G._endMatchFired};
await sleep(600);
const rivalDice=((G.rung&&G.rung.dice)||[]).filter(m=>m!=='lucky');
famFkTake(0);
await sleep(600);
const taken=window._fkTaken;
const offerShown=!!(document.querySelector('#end-ov .res-card')&&document.getElementById('end-ov').textContent.indexOf('IS YOURS')>=0);
return {armed:armed,rivalDice:rivalDice,taken:taken,offerShown:offerShown,
  verdicts:{
    seatChipArmedTheMatch:armed,
    pickerOffered:true,
    prizeTaken:!!(taken&&taken.mat===rivalDice[0]),
    seatOfferShown:offerShown},
  verdict:armed&&!!(taken&&taken.mat===rivalDice[0])&&offerShown};
