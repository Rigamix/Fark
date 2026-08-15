/* SUITE: exclude. IS THE CARD GLOW ACTUALLY PAINTED?
 *
 * Every previous verdict on this came from getComputedStyle, which reports
 * what the cascade RESOLVED - not one pixel of what the compositor drew.
 * It said "glow present" three times while Denis saw nothing. So this
 * probe does not look at style at all: it holds a real drag at full arm
 * and hands back the card's rect in TOP-LEVEL page coordinates so the
 * screenshot can be read directly.
 *
 * The drag is driven at real frame cadence (16ms) rather than three jumps,
 * because that is the difference between the gesture the code sees from a
 * finger and the one my earlier probe faked.
 */
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(fn,ms)=>{const t0=Date.now();while(Date.now()-t0<ms){try{if(fn())return true;}catch(e){}await sleep(80);}return false;};
const out={};
await setup();
if(!await until(()=>{const g=E('G');return g&&g.phase;},4000))return {err:'no match'};
roll();
if(!await until(()=>E('window.D3X').dice.some(d=>d.match&&d.roll),12000))return {err:'no roll'};
await until(()=>{const dx=E('window.D3X');return dx.dice.filter(d=>d.match).every(d=>!d.roll);},22000);
await sleep(400);
gw();

/* a PLAYABLE card, so the glow branch is the one under test */
E("G.pool.forEach(function(d){d.committed=false;d.sel=false;});G.pool[0].val=4;G.pool[1].val=4;G.pool[0].sel=true;G.pool[1].sel=true;G.phase='choosing';");
E("G.pF=[{id:'honeytrap',tier:2,charges:2,state:{}}];famRenderRow()");
await sleep(200);

const fcv=W.document.querySelector('#famRowP .fcv');
if(!fcv)return {err:'no card in row'};
const r=fcv.getBoundingClientRect(),x0=r.left+r.width/2,y0=r.top+r.height/2;
const mk=(t,x,y)=>{const tc=new W.Touch({identifier:1,target:fcv,clientX:x,clientY:y});
  return new W.TouchEvent(t,{touches:t==='touchend'?[]:[tc],bubbles:true,cancelable:true});};

fcv.dispatchEvent(mk('touchstart',x0,y0));
/* REAL CADENCE: 16ms steps all the way to the line, not three jumps */
for(let dy=8;dy<=200;dy+=8){
  W.document.dispatchEvent(mk('touchmove',x0,y0-dy));
  await sleep(16);
}
/* HELD - no touchend. The screenshot is taken with the card mid-air. */
await sleep(120);

const rr=fcv.getBoundingClientRect();
const fr=W.frameElement?W.frameElement.getBoundingClientRect():{left:0,top:0};
out.arm=fcv.style.getPropertyValue('--arm');
out.filter=getComputedStyle(fcv).filter.slice(0,150);
out.scale=getComputedStyle(fcv).scale;
/* the rect the screenshot must be read against: iframe offset + card rect */
out.card={x:Math.round(fr.left+rr.left),y:Math.round(fr.top+rr.top),
          w:Math.round(rr.width),h:Math.round(rr.height)};
out.dpr=window.devicePixelRatio||1;
/* what sits between the glow and the camera, if anything */
const midX=fr.left+rr.left+rr.width/2, aboveY=fr.top+rr.top-6;
const hit=document.elementFromPoint(midX,aboveY);
out.above=hit?(hit.id||hit.className||hit.tagName):'(none)';
return out;
