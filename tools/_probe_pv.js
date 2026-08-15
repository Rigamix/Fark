/* SUITE: exclude. P744: the preserved die is a REAL pool die in its lane. */
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(fn,ms)=>{const t0=Date.now();while(Date.now()-t0<ms){try{if(fn())return true;}catch(e){}await sleep(80);}return false;};
const out={};
await setup();
if(!await until(()=>{const g=E('G');return g&&g.phase;},4000))return {err:'no match'};
roll();
if(!await until(()=>E('window.D3X').dice.some(d=>d.match&&d.roll),12000))return {err:'no roll'};
await until(()=>{const dx=E('window.D3X');return dx.dice.filter(d=>d.match).every(d=>!d.roll);},22000);
await sleep(400);
/* a real kept 1 in lane 2, then the real cast + bank cycle */
E("G.pool.forEach(function(d){d.committed=false;d.sel=false;});var t=G.pool.filter(function(d){return d.lane===2;})[0]||G.pool[0];t.val=1;t.sel=true;");
E("G.pF=[{id:'preserve',tier:1,charges:1,state:{}}];famRenderRow();famUse(0)");
await sleep(600);
out.rec=E('G._famPreserve&&{v:G._famPreserve.val,lane:G._famPreserve.lane}');
const turnBefore=E('G.turnNum');
E("handleYield()");
out.banked=await until(()=>E('G')&&E('G.phase')!=='opp'&&E('G.turnNum')>turnBefore,45000);
await sleep(1200);
out.pvDie=E('G._pvDie&&{v:G._pvDie.val,lane:G._pvDie.lane}');
out.trayChips=E("document.querySelectorAll('#keptRow .die').length");
/* the roll builds it for real */
E("handleRoll()");
await until(()=>E('window.D3X').dice.some(d=>d.match&&d.roll),12000);
await sleep(300);
out.poolDie=E(`(function(){var d=(G.pool||[]).filter(function(x){return x._preserved;})[0];
 return d?{val:d.val,lane:d.lane,committed:!!d.committed,inRow:!!(d.el&&d.el.closest('#playerDiceRow')),
   size:Math.round((d.el.getBoundingClientRect().width||0))}:null;})()`);
out.laneUnique=E(`(function(){var c={};(G.pool||[]).forEach(function(d){c[d.lane]=(c[d.lane]||0)+1;});
 return Object.keys(c).every(function(k){return c[k]===1;});})()`);
out.otherSize=E(`(function(){var d=(G.pool||[]).filter(function(x){return !x._preserved&&x.el;})[0];
 return d?Math.round(d.el.getBoundingClientRect().width):0;})()`);
out.shelled=await until(()=>E(`(function(){var d=(G.pool||[]).filter(function(x){return x._preserved;})[0];
 if(!d)return false;var dd=D3X._dieOfChip(d.el);return !!(dd&&dd.obj.getObjectByName('fkAmber'));})()`),5000);
await until(()=>{const dx=E('window.D3X');return dx.dice.filter(d=>d.match).every(d=>!d.roll);},22000);
out.cracked=await until(()=>E(`(function(){var d=(G.pool||[]).filter(function(x){return x._preserved;})[0];
 if(!d)return true;var dd=D3X._dieOfChip(d.el);return !(dd&&dd.obj.getObjectByName('fkAmber'));})()`),8000);
out.verdict=!!out.rec&&out.banked&&out.trayChips===0&&!!out.poolDie&&out.poolDie.inRow
  &&out.poolDie.committed&&out.poolDie.lane===out.rec.lane&&out.laneUnique
  &&Math.abs(out.poolDie.size-out.otherSize)<=2&&out.shelled&&out.cracked;
return out;
