/* DRAW THE RULE ON TOP OF THE RESULT.
 * The code's shadow offsets measure radially correct to 0.2 degrees and the art
 * carries no baked shadow, yet a shadow reads wrong on the table. So stop
 * reasoning and put the intended direction on screen next to the actual one:
 * a dot at each prop's assumed centre, a line along the radial direction, and a
 * ring at the light. Anything that disagrees with its line is the answer. */
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

const jobs=window._shJobs||[];
const tpl=(window.FK_PROP_TEMPLATES||[]).filter(t=>t.name===window.FK_PROP_PIN)[0];
const props=tpl?tpl.props:[];

const ov=document.createElement('div');
ov.style.cssText='position:fixed;inset:0;z-index:99999;pointer-events:none';
const svgNS='http://www.w3.org/2000/svg';
const svg=document.createElementNS(svgNS,'svg');
svg.setAttribute('width','100%');svg.setAttribute('height','100%');
svg.setAttribute('viewBox','0 0 100 100');svg.setAttribute('preserveAspectRatio','none');
ov.appendChild(svg);document.body.appendChild(ov);

const mk=(t,at)=>{const e=document.createElementNS(svgNS,t);for(const k in at)e.setAttribute(k,at[k]);svg.appendChild(e);return e;};
/* the light */
mk('circle',{cx:window.FK_LIGHT.cx*100,cy:window.FK_LIGHT.cy*100,r:1.6,
  fill:'none',stroke:'#ffe066','stroke-width':0.5});

const rows=[];
jobs.forEach((j,i)=>{
  const q=props[i]||{};
  const a=j.a||[1,1];
  const cx=(q.x||0)+(q.w||0)/2, cy=(q.y||0)+(q.w||0)*(a[1]/a[0])*0.26;
  /* GREEN = where the code says the shadow should fall */
  const L=9;
  mk('line',{x1:cx,y1:cy,x2:cx+(j.ux||0)*L,y2:cy+(j.uy||0)*L,
    stroke:'#00ff66','stroke-width':0.45});
  mk('circle',{cx:cx,cy:cy,r:0.7,fill:'#00ff66'});
  /* MAGENTA = the actual offset the shadow was drawn with, scaled up to be
     visible (it is only a couple of percent) */
  const ox=j.x-(q.x||0), oy=j.y-(q.y||0), m=Math.hypot(ox,oy)||1;
  mk('line',{x1:cx,y1:cy,x2:cx+ox/m*L*0.7,y2:cy+oy/m*L*0.7,
    stroke:'#ff00cc','stroke-width':0.3,'stroke-dasharray':'1 1'});
  rows.push({n:q.n,cx:+cx.toFixed(1),cy:+cy.toFixed(1),
    ux:j.ux,uy:j.uy,dist:+Math.hypot(ox,oy).toFixed(2),flat:j.flat});
});

/* is the shadow canvas even where we think it is? */
const sc=document.getElementById('propShadowCv')||document.querySelector('canvas[id*=hadow]');
const out={rows:rows, shadowCanvas:sc?sc.id:'(not found)',
  canvases:[...document.querySelectorAll('canvas')].map(c=>c.id+' '+c.width+'x'+c.height)};
return out;
