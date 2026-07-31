/* The match table: the new plate, and Denis's prop dressing.
 * Two things that can fail silently - a background-image that 404s renders as
 * nothing at all, and a prop whose PNG is missing renders as a broken <img>
 * with no error anyone reads. Both are checked by asking for the bytes. */
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
await sleep(1200);

const out={};
const probe=async u=>{try{const r=await fetch(u);return r.ok?r.status:('HTTP '+r.status);}catch(e){return String(e);}};

/* 1. the plate the match screen actually asks for */
const sm=document.getElementById('screen-match');
const bg=getComputedStyle(sm,'::before').backgroundImage;
out.plateUrl=bg;
const m=bg.match(/url\(["']?([^"')]+)/);
out.plateFetch=m?await probe(m[1]):'(no url)';
out.plateSize=getComputedStyle(sm,'::before').backgroundSize;

/* 2. which template was used, and did every prop resolve */
out.pin=window.FK_PROP_PIN;
out.templates=(window.FK_PROP_TEMPLATES||[]).map(t=>t.name);
const props=[...document.querySelectorAll('#matchProps img, .fkProps img, #props img')];
out.propCount=props.length;
const broken=[],srcs=[];
for(const im of props){
  const s=im.getAttribute('src');
  srcs.push(s.split('/').pop());
  if(im.complete&&!im.naturalWidth)broken.push(s);
}
out.brokenProps=broken;
out.propNames=srcs;

/* 3. the brief's exclusion zone: nothing in the central band x 15%-85% */
const host=props[0]&&props[0].parentElement;
if(host){
  const hr=host.getBoundingClientRect();
  out.intrudes=props.map(im=>{
    const r=im.getBoundingClientRect();
    const l=100*(r.left-hr.left)/hr.width, rt=100*(r.right-hr.left)/hr.width;
    return {n:im.getAttribute('src').split('/').pop().replace('.png',''),
            l:+l.toFixed(1), r:+rt.toFixed(1)};
  }).filter(q=>q.r>15&&q.l<85);
}
return out;
