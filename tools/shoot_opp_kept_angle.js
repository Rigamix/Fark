/* DO THE RIVAL'S KEPT DICE HOLD THEIR ANGLE ACROSS ITS REROLLS?
 *
 * The player's do - measured, quaternion delta 0.0000. Denis sees the jump on
 * the NPC side only. Suspects, in order: a kept rival die losing the d.roll /
 * d.phys its pose is clamped from (19055 _drop, 19156 row-change), or the six
 * D3.draw() calls the rival's scoring path makes on already-kept dice.
 *
 * Tracks every rival die by element across the whole turn, recording quaternion,
 * rk, and whether it still has a pose source, every time the row changes.
 */
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

let tick=0;
if(typeof D3X==='undefined')return{fatal:'D3X undefined — never reached a match',
  screen:[...document.querySelectorAll('[id^=screen-]')].filter(vis).map(e=>e.id)};

/* hand the table over */
for(let g=0;g<10&&G.phase!=='opp';g++){
  const rb=document.getElementById('btnRoll');
  if(!rb||rb.classList.contains('disabled')||!vis(rb))break;
  tap(rb);
  await until(()=>G.phase==='choosing'||G.phase==='idle'||G.phase==='opp',14000);
  await until(()=>!(D3X.dice||[]).some(d=>d.roll),12000);
  await sleep(450);
  const free=(G.pool||[]).filter(d=>!d.committed);
  const k=free.find(d=>d.val===1||d.val===5);
  if(k){tap(k.el);await sleep(300);}
  const bb=document.getElementById('btnBank');
  if(k&&vis(bb)&&!bb.classList.contains('disabled')&&g>=1){tap(bb);break;}
}
await until(()=>G&&G.phase==='opp',30000);

/* snapshot every rival die, keyed by element identity */
const seen=new Map();   // el -> [{t, q, rk, hasRoll, hasPhys, kept}]
const snap=()=>{
  tick++;
  document.querySelectorAll('#oppDiceRow .die').forEach(el=>{
    const d=(D3X.dice||[]).find(q=>q.chip===el);
    if(!d||!d.obj)return;
    const q=d.obj.quaternion;
    const rec={t:tick,
      q:[+q.x.toFixed(4),+q.y.toFixed(4),+q.z.toFixed(4),+q.w.toFixed(4)],
      rk:(()=>{try{return D3X._rowKey(d);}catch(e){return '?';}})(),
      drk:d.rk, hasRoll:!!d.roll, hasPhys:!!d.phys,
      kept:el.classList.contains('kept-still')||el.classList.contains('oppkeep')};
    if(!seen.has(el))seen.set(el,[]);
    const a=seen.get(el);
    const last=a[a.length-1];
    if(!last||last.q.join()!==rec.q.join()||last.kept!==rec.kept||last.hasRoll!==rec.hasRoll||last.hasPhys!==rec.hasPhys)a.push(rec);
  });
};
let scoreWhileMoving=0, movingSamples=0, tagSamples=0;
for(let s=0;s<90;s++){
  snap();
  try{
    const moving=(D3X.dice||[]).some(d=>d.roll&&d.chip&&d.chip.closest&&d.chip.closest('#oppDiceRow'));
    const tag=!!document.querySelector('.oppTag')||!!(document.getElementById('oppTotal')||{}).textContent;
    const keptMark=!!document.querySelector('#oppDiceRow .die.oppkeep, #oppDiceRow .die.kept-still');
    if(moving)movingSamples++;
    if(tag||keptMark)tagSamples++;
    if(moving&&(tag||keptMark))scoreWhileMoving++;
  }catch(e){}
  await sleep(160);
  if(G.phase!=='opp')break;
}

/* a kept die that moves is the bug */
const out=[];
let i=0;
seen.forEach(hist=>{
  i++;
  const firstKept=hist.findIndex(h=>h.kept);
  if(firstKept<0)return;                       // never kept, not our concern
  const after=hist.slice(firstKept);
  const q0=after[0].q;
  let worst=0,worstAt=null;
  after.forEach(h=>{const d=Math.max(...h.q.map((v,j)=>Math.abs(v-q0[j])));
    if(d>worst){worst=d;worstAt=h;}});
  out.push({die:i, samplesAfterKeep:after.length,
    maxQuatDeltaAfterKeep:+worst.toFixed(4),
    poseAtKeep:{hasRoll:after[0].hasRoll,hasPhys:after[0].hasPhys,rk:after[0].rk,drk:after[0].drk},
    poseAtWorst:worstAt?{hasRoll:worstAt.hasRoll,hasPhys:worstAt.hasPhys,rk:worstAt.rk,drk:worstAt.drk}:null});
});
return {scoreOrKeepShownWhileDiceMoving:scoreWhileMoving, movingSamples, tagSamples,
  keptRivalDiceTracked:out.length,
  anyKeptDieMoved:out.some(o=>o.maxQuatDeltaAfterKeep>0.01),
  worstDelta:out.length?Math.max(...out.map(o=>o.maxQuatDeltaAfterKeep)):null,
  detail:out};
