/* SUITE: exclude. A1b: cast shells, payout parks, roll returns+cracks. */
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(fn,ms)=>{const t0=Date.now();while(Date.now()-t0<ms){try{if(fn())return true;}catch(e){}await sleep(100);}return false;};
const out={};
await setup();
if(!await until(()=>{const g=E('G');return g&&g.phase;},4000))return {err:'no match'};
await sleep(400);
gw();
/* a kept 1 on the table, then the real cast */
/* a REAL kept 1: roll, then commit a die with value 1 the way the game
   does (kept dice live on the throw line under the 3D layer) */
roll();
if(!await until(()=>E('window.D3X').dice.some(d=>d.match&&d.roll),12000))return {err:'no roll'};
await until(()=>{const dx=E('window.D3X');return dx.dice.filter(d=>d.match).every(d=>!d.roll);},22000);
await sleep(500);
E("G.pool[0].val=1;G.pool[0].committed=true;if(G.pool[0].el){G.pool[0].el._trueVal=1;}");
E("G.kept=[{vals:[1],mat:G.pool[0].mat,pts:100,dice:[{val:1,mat:G.pool[0].mat,ench:null,lane:G.pool[0].lane}]}]");
await sleep(400);
E("G.pF=[{id:'preserve',tier:1,charges:1,state:{}}]");E("famRenderRow()");
E("famUse(0)");
await sleep(1200);
out.record=E("G._famPreserve&&G._famPreserve.val");
out.castShell=(()=>{const dx=E('window.D3X');
  return dx.dice.some(d=>d.obj&&d.obj.getObjectByName&&d.obj.getObjectByName('fkAmber'));})();
/* the real turn cycle: bank -> opp -> payout */
const turnBefore=E('G.turnNum');
E("handleYield()");
out.banked=await until(()=>E('G')&&E('G.phase')!=='opp'&&E('G.turnNum')>turnBefore,45000);
await sleep(1500);
out.minted=!!E('window._fkAmberChip');
out.parked=(()=>{const w=E('window._fkAmberWrap');return w&&/9cqw/.test(w.style.translate||'');})();
out.paidShell=await until(()=>{const dx=E('window.D3X');
  return dx.dice.some(d=>d.obj&&d.obj.getObjectByName&&d.obj.getObjectByName('fkAmber'));},4000);
/* the roll brings it home */
E("handleRoll()");
await until(()=>E('window.D3X').dice.some(d=>d.match&&d.roll),12000);
out.stillParkedMidRoll=(()=>{const w=E('window._fkAmberWrap');
  return w&&/9cqw/.test(w.style.translate||'');})();
await until(()=>{const dx=E('window.D3X');return dx.dice.filter(d=>d.match).every(d=>!d.roll);},25000);
out.returned=await until(()=>{const w=E('window._fkAmberWrap');
  return !w||/^0\s*0?/.test(w.style.translate||'0 0');},6000);
out.cracked=await until(()=>!E('window._fkAmberChip'),6000);
out.shellGone=(()=>{const dx=E('window.D3X');
  return !dx.dice.some(d=>d.obj&&d.obj.getObjectByName&&d.obj.getObjectByName('fkAmber'));})();
out.verdict=out.record===1&&out.castShell&&out.banked&&out.minted&&out.parked&&out.paidShell
  &&out.stillParkedMidRoll&&out.returned&&out.cracked&&out.shellGone;
return out;
