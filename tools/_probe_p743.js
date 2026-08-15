const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(fn,ms)=>{const t0=Date.now();while(Date.now()-t0<ms){try{if(fn())return true;}catch(e){}await sleep(80);}return false;};
const out={};
await setup();
if(!await until(()=>{const g=E('G');return g&&g.phase;},4000))return {err:'no match'};
roll();
if(!await until(()=>E('window.D3X').dice.some(d=>d.match&&d.roll),12000))return {err:'no roll'};
await until(()=>{const dx=E('window.D3X');return dx.dice.filter(d=>d.match).every(d=>!d.roll);},22000);
await sleep(500);
gw();
/* 1. the shared beat exists and the rival path calls it */
out.hasBeat=E("typeof D3X.bustBeat")==='function';
out.rivalWired=E("(''+_oppBust||'').length>0")||E(`(function(){var src=String(runOppTurn||'');return src.indexOf('bustBeat')>=0;})()`);
E("window.__beats=[];var _ob=D3X.bustBeat.bind(D3X);D3X.bustBeat=function(s){window.__beats.push(s);return _ob(s);};");
E("G.pool.forEach(function(d){d.committed=false;d.sel=false;d.val=3;});G.pool[0].val=2;G.pool[1].val=4;G.pool[2].val=6;G.pool[3].val=2;G.pool[4].val=3;G.pool[5].val=4;G.phase='choosing';doBust()");
await sleep(250);
out.beats=E('window.__beats');
/* 2. kicks stay on the table */
const kicks=E(`D3X.dice.filter(function(d){return d.match&&d.kick;}).map(function(d){
  return {end:+(d.phys.x+d.kick.vx).toFixed(2),mag:+Math.hypot(d.kick.vx,d.kick.vz).toFixed(2)};})`);
out.kickN=kicks.length;
out.maxEnd=Math.max(...kicks.map(k=>Math.abs(k.end)));
out.maxMag=Math.max(...kicks.map(k=>k.mag));
out.onTable=out.maxEnd<=2.8;
/* 3. the arm is a gradient */
/* make honeytrap PLAYABLE so the ARMED gradient is what we measure */
E("G.pool.forEach(function(d){d.committed=false;d.sel=false;});G.pool[0].val=4;G.pool[1].val=4;G.pool[0].sel=true;G.pool[1].sel=true;G.phase='choosing';");
E("G.pF=[{id:'honeytrap',tier:2,charges:2,state:{}},{id:'preserve',tier:1,charges:0,state:{}}];famRenderRow()");
out.playable=E('CFX.honeytrap.canUse()');
await sleep(300);
const fcv=W.document.querySelector('#famRowP .fcv');
const r=fcv.getBoundingClientRect();
const mk=(t,x,y)=>{const tc=new W.Touch({identifier:1,target:fcv,clientX:x,clientY:y});
  return new W.TouchEvent(t,{touches:t==='touchend'?[]:[tc],bubbles:true,cancelable:true});};
const x0=r.left+r.width/2,y0=r.top+r.height/2;
fcv.dispatchEvent(mk('touchstart',x0,y0));
W.document.dispatchEvent(mk('touchmove',x0,y0-15));
W.document.dispatchEvent(mk('touchmove',x0,y0-60));
out.armMid=fcv.style.getPropertyValue('--arm');
W.document.dispatchEvent(mk('touchmove',x0,y0-400));
out.armFull=fcv.style.getPropertyValue('--arm');
out.midGlow=getComputedStyle(fcv).filter.slice(0,90);out.midScale=getComputedStyle(fcv).scale;
fcv.dispatchEvent(mk('touchend',x0,y0-400));
/* 4. spent card: greyed and undraggable */
const spent=W.document.querySelectorAll('#famRowP .fcv')[1];
out.spentClass=spent&&spent.classList.contains('spent');
out.spentFilter=spent?getComputedStyle(spent).filter.slice(0,30):null;
out.spentCantDrag=E('_famCanPlay(1)')===false;
out.verdict=out.hasBeat&&out.beats.length>0&&out.onTable&&out.maxEnd<=2.8
  &&+out.armMid>0&&+out.armMid<1&&+out.armFull===1&&/brightness\(1\.\d/.test(out.midGlow)&&out.playable===true
  &&out.spentClass&&out.spentCantDrag;
return out;
