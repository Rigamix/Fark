/* S6 arm: clean - ONE arm per browser session, because three arms in one session
   contaminated each other and arms 2 and 3 could never build their state. */
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(f,ms)=>{const t=Date.now();while(Date.now()-t<ms){try{if(f())return true;}catch(e){}await sleep(50);}return false;};
_getS(); S.run=S.run||{}; S.run.tier=2;
S.run.dice=['bone','iron','flint','lead','amber','brass'];
S.settings=S.settings||{}; S.settings.reducedMotion=true;
launchBossMatch();
if(!(await until(()=>typeof G!=='undefined'&&G&&G.rung,9000)))return{error:'no match'};
await sleep(700);
try{startPTurn();}catch(e){}
await sleep(250);
G.matchDice=['bone','iron','flint','lead','amber','brass'];
G._enchArr=[null,null,null,null,null,null];G.numDice=6;G.pool=[];
try{handleRoll();}catch(e){}
if(!(await until(()=>G&&G.pool&&G.pool.length>0,8000)))return{error:'no pool'};
await sleep(650);
if(!G.pool.length)return{error:'pool emptied'};
const keep=G.pool[0];
G.pool=[keep];
/* leave the lane alone */
const seeded=G.pool.map(d=>d.lane);
try{handleRoll();}catch(e){return{error:'roll threw '+e.message};}
await sleep(430);
const lanes=(G.pool||[]).map(d=>d.lane);
const valid=lanes.filter(L=>typeof L==='number'&&isFinite(L)&&L>=0&&L<G.matchDice.length);
const cov=new Set(valid); const missing=[];
for(let i=0;i<G.matchDice.length;i++)if(!cov.has(i))missing.push(i);
return {arm:'clean', seeded:seeded, lanesAfter:lanes,
        seatsCovered:cov.size, seatsTotal:G.matchDice.length, missing:missing,
        ok:missing.length===0};
