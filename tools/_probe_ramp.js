/* SUITE: exclude. The look must RAMP from the first pixel - sampled at
 * 3 progress points, for a playable card AND an unplayable one. */
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
const drag=(playable)=>{
  if(playable)E("G.pool.forEach(function(d){d.committed=false;d.sel=false;});G.pool[0].val=4;G.pool[1].val=4;G.pool[0].sel=true;G.pool[1].sel=true;G.phase='choosing';");
  else E("G.pool.forEach(function(d){d.sel=false;});G.kept=[];G.phase='choosing';");
  E("G.pF=[{id:'honeytrap',tier:2,charges:2,state:{}}];famRenderRow()");
  const fcv=W.document.querySelector('#famRowP .fcv');
  const r=fcv.getBoundingClientRect(),x0=r.left+r.width/2,y0=r.top+r.height/2;
  const mk=(t,x,y)=>{const tc=new W.Touch({identifier:1,target:fcv,clientX:x,clientY:y});
    return new W.TouchEvent(t,{touches:t==='touchend'?[]:[tc],bubbles:true,cancelable:true});};
  fcv.dispatchEvent(mk('touchstart',x0,y0));
  const samples=[];
  [20,120,260].forEach(dy=>{
    W.document.dispatchEvent(mk('touchmove',x0,y0-dy));
    const cs=getComputedStyle(fcv);
    samples.push({arm:+fcv.style.getPropertyValue('--arm'),
      sat:(cs.filter.match(/saturate\(([\d.]+)\)/)||[])[1],
      glow:/236, ?170|240, ?190/.test(cs.filter),
      scale:cs.scale});
  });
  /* the killer case Denis described: a frame with NO --arm must not
     collapse the card to base size */
  fcv.style.removeProperty('--arm');
  const bare=getComputedStyle(fcv);
  samples.push({arm:'unset',scale:bare.scale,
    glow:/236, ?170|240, ?190/.test(bare.filter),
    sat:(bare.filter.match(/saturate\(([\d.]+)\)/)||[])[1]});
  fcv.dispatchEvent(mk('touchend',x0,y0-260));
  return samples;
};
out.playable=drag(true);
out.unplayable=drag(false);
const p=out.playable,u=out.unplayable;
out.glowRamps=p[0].glow&&p[2].glow&&parseFloat(p[0].scale||1)<parseFloat(p[2].scale||1);
out.greyRamps=u[0].sat&&u[2].sat&&parseFloat(u[0].sat)>parseFloat(u[2].sat);
out.armGrows=p[0].arm<p[1].arm&&p[1].arm<=p[2].arm&&u[0].arm<u[2].arm;
out.unsetSafe=p[3]&&p[3].scale!=='none'&&p[3].glow===true;
out.strip=(()=>{gw();const b=W.document.getElementById('statusBot')||W.document.getElementById('statusTop');
  return b?{txt:b.textContent.slice(0,28),cls:b.className}:null;})();
out.verdict=out.glowRamps&&out.greyRamps&&out.armGrows&&out.unsetSafe;
return out;
