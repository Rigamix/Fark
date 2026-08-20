/* P818 regression: the PATRON side of the same resolver still speaks.
 * Seat 0, real bust, odds forced - the bubble must show a line. */
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
const trait=window._lastSeatTrait,art=window._lastSeatArt;
const Q=[1,2,3,4,6,6];
const realE=window._enchRollM;
window._enchRollM=(m,e)=>Q.length?Q.shift():realE(m,e);
tap(document.getElementById('btnRoll'));
if(!await until(()=>G.phase==='choosing',15000))return {err:'no roll'};
await sleep(500);
tap(G.pool.find(d=>!d.committed&&d.val===1).el);await sleep(300);
[2,2,3,3,4].forEach(v=>Q.push(v));
const realRandom=Math.random;
Math.random=()=>0.05;
tap(document.getElementById('btnRoll'));
const shown=await until(()=>{
  const b=document.getElementById('dlgBox'),t=document.getElementById('dlgText');
  return b&&b.classList.contains('show')&&t&&(t.textContent||'').length>2;},25000);
Math.random=realRandom;
const text=(document.getElementById('dlgText')||{}).textContent||'';
return {trait,art,shown,text,
  verdicts:{patronHasIdentity:!!trait,patronSpokeOnBust:shown},
  verdict:!!trait&&shown};
