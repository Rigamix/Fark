/* SUITE: exclude. P737: honeytrap picks the player's pair; blocked drag
 * greys + explains and casts nothing. */
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(fn,ms)=>{const t0=Date.now();while(Date.now()-t0<ms){try{if(fn())return true;}catch(e){}await sleep(100);}return false;};
const out={};
await setup();
if(!await until(()=>{const g=E('G');return g&&g.phase;},4000))return {err:'no match'};
roll();
if(!await until(()=>E('window.D3X').dice.some(d=>d.match&&d.roll),12000))return {err:'no roll'};
await until(()=>{const dx=E('window.D3X');return dx.dice.filter(d=>d.match).every(d=>!d.roll);},22000);
await sleep(400);
/* Denis's exact case: kept 5s, then SELECTED 4s */
E("G.kept=[{vals:[5,5],mat:'bone',pts:100,dice:[{val:5,mat:'bone'},{val:5,mat:'bone'}]}]");
E("G.pool.forEach(function(d,i){d.committed=false;d.sel=false;});G.pool[0].val=4;G.pool[1].val=4;G.pool[0].sel=true;G.pool[1].sel=true;");
out.pairs=E('_honeyPairs()');
E("G.pF=[{id:'honeytrap',tier:1,charges:1,state:{}}]");E("famRenderRow()");
E("CFX.honeytrap.use(G.pF[0])");
out.honeyVal=E('G._famHoneyVal');
/* selection-only pair must be playable (was NOT NOW before) */
E("G.kept=[]");
out.canUseFromSelection=E('CFX.honeytrap.canUse()');/* selection alone must count - THAT is the fix */
/* the reasons */
E("G.pool.forEach(function(d){d.sel=false;})");
out.whyNoPair=E("_famWhyNot({id:'honeytrap',tier:1,charges:1,state:{}})");
out.whySpent=E("_famWhyNot({id:'honeytrap',tier:1,charges:0,state:{}})");
out.whyPreserve=E("_famWhyNot({id:'preserve',tier:1,charges:1,state:{}})");
/* a blocked drag: past the line, unplayable -> grey + reason, no cast */
const el=document.querySelector('#famRowP .fcv')||null;
out.blocked=(()=>{
  gw();
  const fcv=W.document.querySelector('#famRowP .fcv');
  if(!fcv)return 'no card';
  const r=fcv.getBoundingClientRect();
  const mk=(type,x,y)=>{const t=new W.Touch({identifier:1,target:fcv,clientX:x,clientY:y});
    return new W.TouchEvent(type,{touches:type==='touchend'?[]:[t],bubbles:true,cancelable:true});};
  const x0=r.left+r.width/2,y0=r.top+r.height/2;
  fcv.dispatchEvent(mk('touchstart',x0,y0));
  W.document.dispatchEvent(mk('touchmove',x0,y0-15));
  W.document.dispatchEvent(mk('touchmove',x0,y0-300));
  return {greyed:fcv.classList.contains('fcv-blocked'),
    armed:fcv.classList.contains('armed'),
    reason:(W.document.getElementById('famWhyNot')||{}).textContent};
})();
E("window.__hv=G._famHoneyVal");
gw();
const fcv=W.document.querySelector('#famRowP .fcv');
const r=fcv.getBoundingClientRect();
const t=new W.Touch({identifier:1,target:fcv,clientX:r.left,clientY:r.top-300});
fcv.dispatchEvent(new W.TouchEvent('touchend',{touches:[],bubbles:true,cancelable:true}));
await sleep(400);
out.chargesAfterBlockedRelease=E('G.pF[0].charges');
out.verdict=out.pairs&&out.pairs[0]===4&&out.honeyVal===4&&out.canUseFromSelection===true
  &&/PAIR/.test(out.whyNoPair||'')&&/SPENT/.test(out.whySpent||'')&&/1 OR A 5/.test(out.whyPreserve||'')
  &&out.blocked.greyed===true&&out.blocked.armed===false&&!!out.blocked.reason
  &&out.chargesAfterBlockedRelease===1;
return out;
