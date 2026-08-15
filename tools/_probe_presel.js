const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(fn,ms)=>{const t0=Date.now();while(Date.now()-t0<ms){try{if(fn())return true;}catch(e){}await sleep(100);}return false;};
const out={};
await setup();
if(!await until(()=>{const g=E('G');return g&&g.phase;},4000))return {err:'no match'};
roll();
if(!await until(()=>E('window.D3X').dice.some(d=>d.match&&d.roll),12000))return {err:'no roll'};
await until(()=>{const dx=E('window.D3X');return dx.dice.filter(d=>d.match).every(d=>!d.roll);},22000);
await sleep(400);
/* nothing kept; a 5 SELECTED (the old NOT NOW case) */
E("G.kept=[];G.pool.forEach(function(d){d.committed=false;d.sel=false;});G.pool[2].val=5;G.pool[2].sel=true;");
out.canUseSelOnly=E('CFX.preserve.canUse()');
E("G.pF=[{id:'preserve',tier:1,charges:1,state:{}}]");
E("CFX.preserve.use(G.pF[0])");
out.rec=E('G._famPreserve&&{v:G._famPreserve.val,lane:G._famPreserve.lane}');
/* and a kept 1 still beats a selected 5 (the 1 pays more) */
E("G._famPreserve=null;G.kept=[{vals:[1],mat:'iron',pts:100,dice:[{val:1,mat:'iron',ench:null,lane:4}]}]");
E("CFX.preserve.use(G.pF[0])");
out.prefersOne=E('G._famPreserve&&G._famPreserve.val');
out.verdict=out.canUseSelOnly===true&&out.rec&&out.rec.v===5&&out.prefersOne===1;
return out;
