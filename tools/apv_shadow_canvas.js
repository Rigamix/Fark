/* WHAT IS ACTUALLY PAINTED ON THE SHADOW CANVAS.
 * The job list is radially correct to 0.2 degrees and the art has no baked
 * shadow, so the last place the direction can go wrong is between the job and
 * the pixels. Read shCanvas, find the dark mass near each prop, and measure
 * where it sits relative to that prop. */
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
tap(document.getElementById('nrTakeBtn'));await sleep(2200);
const pc=[...document.querySelectorAll('.ptcard')].filter(vis)[0];if(pc){tap(pc);await sleep(1700);}
const sit=[...document.querySelectorAll('span,div,button')].filter(e=>vis(e)&&e.children.length<=1&&/^SIT\s*DOWN$/i.test((e.textContent||'').trim()))[0];
if(sit){tap(sit);if(sit.parentElement)tap(sit.parentElement);}
await until(()=>vis(document.getElementById('screen-match')),9000);
await until(()=>typeof G!=='undefined'&&G&&G.phase==='idle',14000);
await sleep(1800);

const out={};
const sc=document.getElementById('shCanvas');
if(!sc)return {err:'no shCanvas'};
out.canvas={w:sc.width,h:sc.height,css:getComputedStyle(sc).cssText?undefined:null,
  opacity:getComputedStyle(sc).opacity, display:getComputedStyle(sc).display,
  zIndex:getComputedStyle(sc).zIndex};

const ctx=sc.getContext('2d',{willReadFrequently:true});
let img;
try{ img=ctx.getImageData(0,0,sc.width,sc.height); }
catch(e){ return {err:'readback blocked: '+e.message}; }
const d=img.data, W=sc.width, H=sc.height;

/* is anything drawn at all? */
let ink=0, maxA=0;
for(let i=3;i<d.length;i+=4){ if(d[i]>8){ink++;} if(d[i]>maxA)maxA=d[i]; }
out.inkPx=ink; out.inkFrac=+(ink/(W*H)).toFixed(4); out.maxAlpha=maxA;

/* per prop: centroid of the ink inside a box around it */
const tpl=(window.FK_PROP_TEMPLATES||[]).filter(t=>t.name===window.FK_PROP_PIN)[0];
const props=tpl?tpl.props:[];
const jobs=window._shJobs||[];
out.rows=props.map((q,i)=>{
  const j=jobs[i]||{};
  const a=j.a||[1,1];
  /* prop box in canvas px, padded so a nearby shadow is included */
  const pw=q.w/100*W, ph=pw*(a[1]/a[0]);
  const px=q.x/100*W, py=q.y/100*H;
  const pad=pw*0.6;
  const x0=Math.max(0,Math.round(px-pad)), x1=Math.min(W,Math.round(px+pw+pad));
  const y0=Math.max(0,Math.round(py-pad)), y1=Math.min(H,Math.round(py+ph+pad));
  let sx=0,sy=0,n=0;
  for(let y=y0;y<y1;y++)for(let x=x0;x<x1;x++){
    const A=d[(y*W+x)*4+3];
    if(A>16){sx+=x;sy+=y;n++;}
  }
  if(!n)return {n:q.n,ink:0,note:'no shadow ink near this prop'};
  sx/=n; sy/=n;
  const bcx=px+pw/2, bcy=py+ph/2;          /* the prop's own box centre, px */
  const dx=sx-bcx, dy=sy-bcy;
  return {n:q.n, ink:n,
          drawnDeg:+(Math.atan2(dy,dx)*180/Math.PI).toFixed(1),
          jobDeg:+(Math.atan2((j.uy||0),(j.ux||0))*180/Math.PI).toFixed(1),
          offPx:+Math.hypot(dx,dy).toFixed(1)};
});
return out;
