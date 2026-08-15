/* SUITE: exclude. studioCast runs the real mechanic. */
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(fn,ms)=>{const t0=Date.now();while(Date.now()-t0<ms){try{if(fn())return true;}catch(e){}await sleep(100);}return false;};
const out={};
await setup();
if(!await until(()=>{const g=E('G');return g&&g.phase;},4000))return {err:'no match'};
roll();
if(!await until(()=>E('window.D3X').dice.some(d=>d.match&&d.roll),15000))return {err:'no roll'};
await until(()=>{const dx=E('window.D3X');return dx.dice.filter(d=>d.match).every(d=>!d.roll);},20000);
await sleep(600);
/* powder_keg rerolls the whole table - a mechanic whose effect is obvious */
openStudio('powder_keg');
await sleep(500);
const before=E('G.pool.map(function(d){return d.val;}).join(",")');
studioCast();
await sleep(900);
const after=E('G.pool.map(function(d){return d.val;}).join(",")');
out.before=before;out.after=after;
out.mechanicRan=E('G.turnRollCount')>0;
out.logSaysLive=/mechanic is live|CHANGED/.test(document.getElementById('log').textContent);
out.verdict=!!out.logSaysLive;
return out;
