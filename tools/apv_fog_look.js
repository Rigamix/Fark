/* P823: the fog LOOK. Arm fog on their lane 0 through the real icon
 * keep, let their turn consume it - the blinded die must go dark
 * (d._fogDim through the dim system) and the cloud must float over
 * its seat (.fog-float in the top layer). Screenshot lands mid-beat. */
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
const Q=[1,5,2,3,4,6];
const realE=window._enchRollM;
window._enchRollM=(m,e)=>Q.length?Q.shift():realE(m,e);
G._enchArr=[{t:'fog',face:1},null,null,null,null,null];
tap(document.getElementById('btnRoll'));
if(!await until(()=>G.phase==='choosing',15000))return {err:'no roll'};
await sleep(600);
const branded=G.pool.find(d=>d.lane===0&&d.val===1);
if(!branded||!branded.ench)return {err:'no brand'};
tap(branded.el);await sleep(150);
tap(G.pool.find(d=>!d.committed&&d.val===5).el);await sleep(300);
/* their deal: lane 0 gets a 1 (their best) so the fog has a target */
const realRF=window.rollFace;
let RQ=[1,5,2,2,3,3];
window.rollFace=m=>RQ.length?RQ.shift():realRF(m);
tap(document.getElementById('btnBank'));
/* the consumption paints the look - catch the floating cloud live */
const cloudSeen=await until(()=>document.querySelector('.fog-float'),30000);
await sleep(700);/* mid-beat for the screenshot */
const fogDie=(window.D3X&&D3X.dice||[]).find(d=>d._fogDim);
const ce=document.querySelector('.fog-float');
let onTop=null,cloudRect=null,cloudCS=null;
if(ce){const r=ce.getBoundingClientRect();cloudRect={x:Math.round(r.x),y:Math.round(r.y),w:Math.round(r.width),h:Math.round(r.height)};
  cloudCS={z:getComputedStyle(ce).zIndex,disp:getComputedStyle(ce).display,fs:getComputedStyle(ce).fontSize};
  const t=document.elementFromPoint(r.x+r.width/2,r.y+r.height/2);
  onTop=t?(t.id||t.className||t.tagName):null;}
const cloudEl=document.querySelector('.fog-float');
const markSpent=!(G._fog&&G._fog.live);
return {cloudSeen,cloudAlive:!!cloudEl,cloudRect,cloudCS,onTop,
  fogDimSet:!!fogDie,fogDieVal:fogDie&&fogDie.phys?fogDie.phys.v:null,
  markSpent,
  verdicts:{
    cloudFloats:cloudSeen&&!!cloudEl,
    dieWentDark:!!fogDie,
    itWasTheirBest:!!fogDie&&fogDie.phys&&fogDie.phys.v===1},
  verdict:cloudSeen&&!!fogDie};
