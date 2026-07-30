/* DOES A KEPT DIE HOLD ITS ANGLE ACROSS A REROLL?
 * Records each kept die's 3D quaternion and its CSS rotate, before the reroll
 * and after it settles. A kept die is finished: it should not move at all. */
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(fn,ms)=>{const t0=Date.now();while(Date.now()-t0<ms){try{if(fn())return true;}catch(e){}await sleep(70);}return false;};
const vis=el=>{if(!el||!el.isConnected)return false;const s=getComputedStyle(el),r=el.getBoundingClientRect();
 return s.display!=='none'&&s.visibility!=='hidden'&&+s.opacity>0.05&&r.width>1&&r.height>1;};
const tap=el=>{if(!vis(el))return false;const r=el.getBoundingClientRect();
 const o={bubbles:true,cancelable:true,clientX:r.left+r.width/2,clientY:r.top+r.height/2};
 el.dispatchEvent(new PointerEvent('pointerdown',o));el.dispatchEvent(new PointerEvent('pointerup',o));
 el.dispatchEvent(new MouseEvent('click',o));return true;};
tap(document.getElementById('hsBtnBottom'));await sleep(1800);
await until(()=>{const d=document.querySelector('.nrdie');return d&&d._floatDone;},9000);
tap(document.querySelector('.nrdie'));await sleep(1300);
tap(document.getElementById('nrTakeBtn'));await sleep(1900);
const p=[...document.querySelectorAll('.ptcard')].filter(vis)[0];if(p){tap(p);await sleep(1700);}
const sit=[...document.querySelectorAll('span,div,button')].filter(e=>vis(e)&&e.children.length<=1&&/^SIT\s*DOWN$/i.test((e.textContent||'').trim()))[0];
if(sit){tap(sit);if(sit.parentElement)tap(sit.parentElement);}
await until(()=>vis(document.getElementById('screen-match')),9000);
await until(()=>typeof G!=='undefined'&&G&&G.phase==='idle',14000);

const poseOf=el=>{const d=(D3X.dice||[]).find(q=>q.chip===el);
  if(!d||!d.obj)return null;const q=d.obj.quaternion;
  return {q:[+q.x.toFixed(4),+q.y.toFixed(4),+q.z.toFixed(4),+q.w.toFixed(4)],
    css:(el.style.rotate||getComputedStyle(el).rotate||''),
    tr:(el.style.translate||''), hasRoll:!!d.roll, keptLook:!!d._keptLook};};

tap(document.getElementById('btnRoll'));
await until(()=>G.phase==='choosing'||G.phase==='idle',14000);
await until(()=>!(D3X.dice||[]).some(d=>d.roll),12000);
await sleep(800);
const free=G.pool.filter(d=>!d.committed);
const keeps=free.filter(d=>d.val===1||d.val===5).slice(0,2);
if(!keeps.length)return{skipped:'no scoring die in first roll'};
keeps.forEach(k=>tap(k.el));
await sleep(600);
const before=keeps.map(k=>({val:k.val,...poseOf(k.el)}));
const rb=document.getElementById('btnRoll');
if(!rb||rb.classList.contains('disabled'))return{skipped:'roll locked',before};
tap(rb);
await sleep(300);
const during=keeps.map(k=>({...poseOf(k.el)}));
await until(()=>G.phase==='choosing'||G.phase==='idle',14000);
await until(()=>!(D3X.dice||[]).some(d=>d.roll),12000);
await sleep(900);
const after=keeps.map(k=>({...poseOf(k.el)}));
const dq=(a,b)=>a&&b&&a.q&&b.q?Math.max(...a.q.map((v,i)=>Math.abs(v-b.q[i]))).toFixed(4):null;
return{before,during,after,
  maxQuatDelta_beforeVsAfter:before.map((b,i)=>dq(b,after[i])),
  maxQuatDelta_beforeVsDuring:before.map((b,i)=>dq(b,during[i]))};
