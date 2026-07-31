/* What does Vagabond's row actually pay, against what the rival really did? */
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(fn,ms)=>{const t0=Date.now();while(Date.now()-t0<ms){try{if(fn())return true;}catch(e){}await sleep(60);}return false;};
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

const rows=[];
for(let turn=0;turn<6;turn++){
  const oBefore=G.oPts||0;
  /* hand over */
  for(let g=0;g<8&&G.phase!=='opp';g++){
    const rb=document.getElementById('btnRoll');
    if(!rb||rb.classList.contains('disabled')||!vis(rb))break;
    tap(rb);
    await until(()=>G.phase==='choosing'||G.phase==='idle'||G.phase==='opp',14000);
    await until(()=>!(D3X.dice||[]).some(d=>d.roll),12000);
    await sleep(400);
    const free=(G.pool||[]).filter(d=>!d.committed);
    const k=free.find(d=>d.val===1||d.val===5);
    if(k){tap(k.el);await sleep(300);}
    const bb=document.getElementById('btnBank');
    if(k&&vis(bb)&&!bb.classList.contains('disabled')&&g>=1){tap(bb);break;}
  }
  if(!(await until(()=>G&&G.phase==='opp',30000)))continue;
  if(!(await until(()=>G&&G.phase==='idle',45000)))break;
  await sleep(600);
  const oAfter=G.oPts||0;
  const reallyBanked=oAfter-oBefore;          /* 0 means they busted */
  const wouldPay=Math.max(0,G._oLastBank||0); /* what the row reads now */
  rows.push({turn:turn+1, rivalActuallyBanked:reallyBanked, vagabondWouldPay:wouldPay,
             matches:reallyBanked===wouldPay});
}
return {rows, anyMismatch:rows.some(r=>!r.matches),
  paysAfterBust:rows.some(r=>r.rivalActuallyBanked===0&&r.vagabondWouldPay>0)};
