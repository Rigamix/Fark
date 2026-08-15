/* SUITE: exclude. P738: one view, one needs table - all prior
 * behaviours hold and no card lost its gate. */
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(fn,ms)=>{const t0=Date.now();while(Date.now()-t0<ms){try{if(fn())return true;}catch(e){}await sleep(100);}return false;};
const out={};
await setup();
if(!await until(()=>{const g=E('G');return g&&g.phase;},4000))return {err:'no match'};
roll();
if(!await until(()=>E('window.D3X').dice.some(d=>d.match&&d.roll),12000))return {err:'no roll'};
await until(()=>{const dx=E('window.D3X');return dx.dice.filter(d=>d.match).every(d=>!d.roll);},22000);
await sleep(400);
const reset=()=>E("G.kept=[];G.pool.forEach(function(d){d.committed=false;d.sel=false;d._frozen=false;});");
/* 1. Denis's exact honeytrap case: kept 5s, selected 4s -> fires on 4 */
reset();
E("G.kept=[{vals:[5,5],mat:'bone',pts:100,dice:[{val:5,mat:'bone'},{val:5,mat:'bone'}]}];G.pool[0].val=4;G.pool[1].val=4;G.pool[0].sel=true;G.pool[1].sel=true;");
out.pairs=E('_tablePairs()');
E("G.pF=[{id:'honeytrap',tier:1,charges:1,state:{}},{id:'preserve',tier:1,charges:1,state:{}}]");
E("CFX.honeytrap.use(G.pF[0])");
out.honeyVal=E('G._famHoneyVal');
/* 2. selection-only pair is playable */
reset();
E("G.pool[0].val=3;G.pool[1].val=3;G.pool[0].sel=true;G.pool[1].sel=true;");
out.honeySelOnly=E('CFX.honeytrap.canUse()');
/* 3. preserve: selected 5 alone works, kept 1 still preferred */
reset();
E("G.pool[2].val=5;G.pool[2].sel=true;");
out.presSelOnly=E('CFX.preserve.canUse()');
E("G._famPreserve=null;CFX.preserve.use(G.pF[1])");
out.presSelVal=E('G._famPreserve&&G._famPreserve.val');
E("G._famPreserve=null;G.kept=[{vals:[1],mat:'iron',pts:100,dice:[{val:1,mat:'iron',ench:null,lane:4}]}];CFX.preserve.use(G.pF[1])");
out.presPrefersOne=E('G._famPreserve&&G._famPreserve.val');
/* 4. a BRANDED face is still never a preserve candidate (P534 law) */
reset();
E("G.pool[3].val=1;G.pool[3].sel=true;G.pool[3].ench={t:'ward',face:1};");
out.brandedBlocked=E('CFX.preserve.canUse()')===false;
/* 5. nothing on the table -> both gate off, and say why */
reset();
out.honeyOff=E('CFX.honeytrap.canUse()')===false;
out.presOff=E('CFX.preserve.canUse()')===false;
out.whyPair=E("_famWhyNot({id:'honeytrap',tier:1,charges:1,state:{}})");
out.whyScorer=E("_famWhyNot({id:'preserve',tier:1,charges:1,state:{}})");
out.whySpent=E("_famWhyNot({id:'honeytrap',tier:1,charges:0,state:{}})");
/* 6. no card lost its gate: every live active still answers canUse */
out.allCards=E(`(function(){var bad=[];Object.keys(FAM_LIVE).forEach(function(id){
 var d=famDef(id),fx=CFX[id];if(!d||d.kind!=='active'||!fx||!fx.canUse)return;
 try{fx.canUse({id:id,tier:1,charges:1,state:{}});}catch(e){bad.push(id+':'+e.message);}});
 return bad;})()`);
out.verdict=out.pairs[0]===4&&out.honeyVal===4&&out.honeySelOnly===true
  &&out.presSelOnly===true&&out.presSelVal===5&&out.presPrefersOne===1
  &&out.brandedBlocked&&out.honeyOff&&out.presOff
  &&/PAIR/.test(out.whyPair)&&/1 OR A 5/.test(out.whyScorer)&&/SPENT/.test(out.whySpent)
  &&out.allCards.length===0;
return out;
