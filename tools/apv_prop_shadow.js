/* THE SHADOW ACTUALLY DRAWN, versus the radial rule.
 * The angle probe showed the intended direction is only ~6 degrees off, which
 * is nothing like "doesn't follow the rule". So measure what is really on the
 * canvas: read _shJobs (the job list the shadow pass builds) and compare each
 * shadow's real offset from its prop against the radial direction from the
 * light centre. Then look for the other candidate - a shadow baked into the
 * prop's own PNG, which no code can steer. */
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
await sleep(1500);

const out={pin:window.FK_PROP_PIN, light:window.FK_LIGHT};
const jobs=window._shJobs||[];
out.jobCount=jobs.length;

/* the template the game used, so prop x/y can be paired with shadow x/y */
const tpl=(window.FK_PROP_TEMPLATES||[]).filter(t=>t.name===window.FK_PROP_PIN)[0];
const props=tpl?tpl.props:[];

out.rows=jobs.map((j,i)=>{
  const q=props[i]||{};
  /* the offset the shadow was actually given */
  const ox=j.x-(q.x||0), oy=j.y-(q.y||0);
  /* the radial direction, computed from the prop's TRUE centre.
     y is multiplied by 1.9 because x% and y% are fractions of different
     screen dimensions - the same correction the shipped code applies. */
  const a=j.a||[1,1];
  const cx=(q.x||0)+(q.w||0)/2, cy=(q.y||0)+(q.w||0)*(a[1]/a[0])*0.26;
  const rdx=cx-window.FK_LIGHT.cx*100, rdy=(cy-window.FK_LIGHT.cy*100)*1.9;
  const rDeg=Math.atan2(rdy,rdx)*180/Math.PI;
  const aDeg=Math.atan2(oy*1.9,ox)*180/Math.PI;
  let d=aDeg-rDeg; while(d>180)d-=360; while(d<-180)d+=360;
  return {n:q.n, flat:j.flat, dist:+Math.hypot(ox,oy*1.9).toFixed(2),
          drawnDeg:+aDeg.toFixed(1), radialDeg:+rDeg.toFixed(1), errDeg:+d.toFixed(1)};
});
out.maxErr=out.rows.reduce((m,r)=>Math.max(m,Math.abs(r.errDeg)),0);
out.flatApplied=out.rows.filter(r=>r.flat!==1).map(r=>r.n+' '+r.flat);
out.flatMissing=out.rows.filter(r=>r.flat===1).map(r=>r.n);
return out;
