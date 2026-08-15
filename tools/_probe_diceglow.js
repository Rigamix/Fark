/* SUITE: exclude. REGRESSION: the dice selection glow after P748 lifted
 * the painter out from under it. Denis approved this glow on his phone;
 * breaking it to fix the cards would be a bad trade.
 *
 * The last run reported found:false and I nearly read that as "fine" -
 * it meant the check never ran. So this one reports the census first and
 * refuses to return a verdict without a die it can actually light.
 */
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(fn,ms)=>{const t0=Date.now();while(Date.now()-t0<ms){try{if(fn())return true;}catch(e){}await sleep(90);}return false;};
const out={};
if(!await until(()=>typeof launchSeat==='function'&&typeof G!=='undefined',20000))
  return {err:'game never booted'};
await until(()=>document.getElementById('screen-gauntlet'),8000);
try{launchSeat(0);}catch(e){return {err:'launchSeat: '+e.message};}
if(!await until(()=>G&&G.phase,12000))return {err:'no match'};

/* the 3D layer has to be MOUNTED before a roll makes dice - handleRoll
   returning cleanly says nothing about that */
await until(()=>window.D3X&&D3X.mount,12000);
out.d3x={has:!!window.D3X,mounted:!!(window.D3X&&D3X.mount),
  phase:G&&G.phase,btn:!!document.getElementById('btnRoll')};
await sleep(700);
out.rolled=false;
/* the GAME's own roll is handleRoll - `roll()` was the LAB's helper, and
   reaching for it here is the same lab-vs-game confusion Denis flagged */
/* THE REAL ROUTE: the button the player presses. Calling handleRoll
   directly returned true and made no dice at all. */
for(let a=0;a<4&&!D3X.dice.length;a++){
  const b=document.getElementById('btnRoll');
  if(b)b.click(); else {try{handleRoll();}catch(e){out.rollErr=e.message;}}
  await until(()=>D3X.dice.length>0,4000);
}
out.rolled=D3X.dice.length>0;
await until(()=>window.D3X&&D3X.dice.some(d=>d.match&&d.roll),15000);
await until(()=>D3X.dice.filter(d=>d.match).every(d=>!d.roll),25000);
await sleep(600);

/* CENSUS FIRST - a zero below is only meaningful if there was a die */
out.census={total:D3X.dice.length,
  match:D3X.dice.filter(d=>d.match).length,
  visible:D3X.dice.filter(d=>d.match&&d.obj&&d.obj.visible).length,
  chips:D3X.dice.filter(d=>d.match&&d.chip).length};
const dm=D3X.dice.filter(d=>d.match&&d.obj&&d.obj.visible&&d.chip);
if(!dm.length)return Object.assign(out,{err:'NO DIE TO LIGHT - verdict withheld'});

const lit=(id)=>{
  const c=document.getElementById(id);
  if(!c)return {missing:true};
  const d=c.getContext('2d').getImageData(0,0,c.width,c.height).data;
  let n=0,rs=0,gs=0,bs=0;
  for(let i=3;i<d.length;i+=4)if(d[i]>8){n++;rs+=d[i-3];gs+=d[i-2];bs+=d[i-1];}
  return {lit:n,col:n?[Math.round(rs/n),Math.round(gs/n),Math.round(bs/n)]:null};
};
/* nothing selected: the canvas must be CLEAR (proves the reader works) */
dm.forEach(d=>d.chip.classList.remove('selected'));
try{D3X._drawGlow();}catch(e){out.errNone=e.message;}
await sleep(100);
out.none=lit('dgCanvas');
/* one selected: the halo must appear */
dm[0].chip.classList.add('selected');
try{D3X._drawGlow();}catch(e){out.errOne=e.message;}
await sleep(100);
out.one=lit('dgCanvas');
/* two selected: more of it */
if(dm[1]){dm[1].chip.classList.add('selected');
  try{D3X._drawGlow();}catch(e){}
  await sleep(100);out.two=lit('dgCanvas');}
out.cfBlur=(typeof _cfBlur==='function')?_cfBlur():'(n/a)';
out.verdict=(out.one.lit>2000)&&((out.none.lit||0)<out.one.lit*0.1)
  &&(!out.two||out.two.lit>=out.one.lit);
return out;
