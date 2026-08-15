/* SUITE: exclude. THE REAL GAME, TOP-LEVEL. No lab, no iframe.
 *
 * Denis: "your screenshot is from the lab by the way not the game" - and
 * he is right that every reading I have taken on this came through the
 * lab's scaled iframe, which is how I handed a pixel reader coordinates
 * from two different systems and got a confident zero off empty chrome.
 *
 * So this drives fark_proto.html itself via the ?vagatest=1 debug entry,
 * and asks two different questions with two different instruments:
 *   1. does dgCanvasHi actually CONTAIN a halo?  (getImageData - it is a
 *      canvas, so this is the pixels themselves, not a style string)
 *   2. is the dice glow still intact?             (regression: the painter
 *      was lifted out of _drawGlow and must behave identically)
 * The screenshot taken after this answers the third question - whether
 * the thing that was painted is actually VISIBLE - and its coordinates
 * are the page's own, because there is no iframe in the way.
 */
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(fn,ms)=>{const t0=Date.now();while(Date.now()-t0<ms){try{if(fn())return true;}catch(e){}await sleep(90);}return false;};
const out={};

if(!await until(()=>typeof launchSeat==='function'&&typeof G!=='undefined',20000))
  return {err:'game never booted'};
if(!await until(()=>document.getElementById('screen-gauntlet'),8000))
  return {err:'no gauntlet screen'};
try{launchSeat(0);}catch(e){return {err:'launchSeat threw: '+e.message};}
if(!await until(()=>G&&G.phase,12000))return {err:'no match'};
try{roll();}catch(e){try{document.getElementById('rollBtn').click();}catch(e2){}}
await until(()=>window.D3X&&D3X.dice.some(d=>d.match&&d.roll),14000);
await until(()=>D3X.dice.filter(d=>d.match).every(d=>!d.roll),22000);
await sleep(500);

/* ── 1. THE DICE GLOW, unchanged? the painter was lifted out from under it ── */
/* the painter reads chip.classList - feeding it that directly is the
   exact input under test (this is a regression check on the PAINTER,
   not on selection) */
const dm=D3X.dice.filter(d=>d.match&&d.obj.visible)[0];
if(dm)dm.chip.classList.add('selected');
out.dicePre={found:!!dm};
try{D3X._drawGlow();}catch(e){out.diceErr=e.message;}
await sleep(120);
const litOf=(id)=>{
  const c=document.getElementById(id);
  if(!c)return {missing:true};
  const x=c.getContext('2d');
  const d=x.getImageData(0,0,c.width,c.height).data;
  let lit=0,rs=0,gs=0,bs=0;
  for(let i=3;i<d.length;i+=4)if(d[i]>8){lit++;rs+=d[i-3];gs+=d[i-2];bs+=d[i-1];}
  return {w:c.width,h:c.height,lit:lit,
    col:lit?[Math.round(rs/lit),Math.round(gs/lit),Math.round(bs/lit)]:null,
    z:getComputedStyle(c).zIndex};
};
out.diceGlow=litOf('dgCanvas');

/* ── 2. THE CARD GLOW ── */
G.pool.forEach(d=>{d.committed=false;d.sel=false;});
if(G.pool[0]&&G.pool[1]){G.pool[0].val=4;G.pool[1].val=4;G.pool[0].sel=true;G.pool[1].sel=true;}
G.phase='choosing';
/* powder_keg has no FAM_NEEDS entry, so it is playable whenever the
   phase allows - honeytrap needed a pair my rigging never really made,
   and the last run silently measured the fcv-cant branch instead */
G.pF=[{id:'powder_keg',tier:2,charges:2,state:{}}];
famRenderRow();
await sleep(220);
/* PROVE THE PRECONDITION. A glow is correctly absent on a card that
   cannot be played, so a zero here means nothing unless this is empty. */
out.why=(typeof _famWhyNot==='function')?(_famWhyNot(G.pF[0])||''):'(no _famWhyNot)';
out.canPlay=(typeof _famCanPlay==='function')?_famCanPlay(0):null;
if(out.why||out.canPlay===false)return Object.assign(out,{err:'card not playable: '+out.why});
const fcv=document.querySelector('#famRowP .fcv');
if(!fcv)return Object.assign(out,{err:'no card in hand'});
const r0=fcv.getBoundingClientRect(),x0=r0.left+r0.width/2,y0=r0.top+r0.height/2;
const mk=(t,x,y)=>{const tc=new Touch({identifier:1,target:fcv,clientX:x,clientY:y});
  return new TouchEvent(t,{touches:t==='touchend'?[]:[tc],bubbles:true,cancelable:true});};
fcv.dispatchEvent(mk('touchstart',x0,y0));
for(let dy=8;dy<=200;dy+=8){document.dispatchEvent(mk('touchmove',x0,y0-dy));await sleep(16);}
await sleep(120);
out.arm=fcv.style.getPropertyValue('--arm');
out.cardGlow=litOf('dgCanvasHi');
out.cant=fcv.classList.contains('fcv-cant');
/* held, so the screenshot catches it mid-air; rect is page coords - no iframe */
const rr=fcv.getBoundingClientRect();
out.card={x:Math.round(rr.left),y:Math.round(rr.top),w:Math.round(rr.width),h:Math.round(rr.height)};
out.dpr=window.devicePixelRatio||1;
out.filter=getComputedStyle(fcv).filter.slice(0,90);
return out;
