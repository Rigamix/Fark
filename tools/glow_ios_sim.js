/* Drive into a live match, select a die, then measure the pixels the
   selection glow actually puts on #dgCanvas in three worlds:
     A  as-shipped here (ctx.filter real)          -> desktop / headless
     B  ctx.filter accessor removed, D3X._cf left TRUE (what _cfBlur reports
        on iOS Safari < 18 - see tools/glow_cfdetect.js)
     C  ctx.filter accessor removed AND D3X._cf=false (the stroke fallback
        the code was MEANT to take there)                                   */
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
tap(document.getElementById('btnRoll'));
await until(()=>G.phase==='choosing',12000);
await sleep(2500);

const out={};
out.fk3d=document.documentElement.classList.contains('fk3d');
out.d3xReady=!!(window.D3X&&D3X.ready);
out.d3xFail=!!(window.D3X&&D3X.fail);
out.d3xCf=D3X._cf;
out.diceRegistered=D3X.dice.length;
out.matchDice=D3X.dice.filter(d=>d.match).length;

/* select a die through the real tap path */
const pool=G.pool.filter(d=>!d.committed);
const target=pool.find(d=>d.val===1)||pool[0];
tap(target.el);
await sleep(900);
out.selClassOnChip=!!(target.el.classList.contains('selected'));
out.selCountInD3X=D3X.dice.filter(d=>d.match&&d.chip.classList.contains('selected')).length;
out.rolling=D3X._rolling();

/* count ink on the glow canvas */
function ink(tag){
  const cv=document.getElementById('dgCanvas');
  if(!cv)return {tag,cv:null};
  const x=cv.getContext('2d');
  const d=x.getImageData(0,0,cv.width,cv.height).data;
  let n=0,maxA=0,sumA=0,minX=1e9,maxX=-1,minY=1e9,maxY=-1;
  for(let p=0,px=0;p<d.length;p+=4,px++){
    const a=d[p+3];
    if(a>8){n++;sumA+=a;if(a>maxA)maxA=a;
      const yy=(px/cv.width)|0,xx=px%cv.width;
      if(xx<minX)minX=xx;if(xx>maxX)maxX=xx;if(yy<minY)minY=yy;if(yy>maxY)maxY=yy;}
  }
  return {tag,w:cv.width,h:cv.height,inkPx:n,maxAlpha:maxA,
          meanAlpha:n?+(sumA/n).toFixed(1):0,
          bboxW:maxX>=0?maxX-minX+1:0,bboxH:maxY>=0?maxY-minY+1:0,
          zIndex:getComputedStyle(cv).zIndex,
          display:getComputedStyle(cv).display,
          opacity:getComputedStyle(cv).opacity,
          parent:cv.parentElement&&cv.parentElement.id};
}
out.A_asShipped=ink('A ctx.filter real, _cf=true');

/* ---- simulate an engine with no CanvasRenderingContext2D.filter ---- */
const proto=CanvasRenderingContext2D.prototype;
const desc=Object.getOwnPropertyDescriptor(proto,'filter');
delete proto.filter;
out.simulated_detect=(function(){var c=document.createElement('canvas').getContext('2d');
  c.filter='blur(2px)';return c.filter==='blur(2px)';})();

D3X._glowTmp=null;                       /* fresh scratch surface each world */
D3X._drawGlow();
out.B_iosAsCodedNow=ink('B no ctx.filter, _cf still true');

D3X._cf=false;
D3X._glowTmp=null;
D3X._drawGlow();
out.C_iosIntendedFallback=ink('C no ctx.filter, _cf=false (stroke fallback)');

D3X._cf=true;
Object.defineProperty(proto,'filter',desc);
D3X._glowTmp=null;
D3X._drawGlow();
out.D_restored=ink('D restored');

out.verdict={
  detectionLiesOnIOS: out.simulated_detect===true,
  glowVanishesOnIOS:  out.B_iosAsCodedNow.inkPx < out.A_asShipped.inkPx*0.25,
  fallbackWouldWork:  out.C_iosIntendedFallback.inkPx > out.A_asShipped.inkPx*0.4
};
return out;
