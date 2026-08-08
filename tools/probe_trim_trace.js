/* WHAT DISCARDS A REAL DIE A SECOND AFTER A FULL DEAL?

   Measured during the S6 work and deliberately left unfixed until traced: with
   a phantom pool entry present (a lane that is not a real seat), the deal fills
   every seat correctly and then, about a second later, the pool is one shorter
   - and the die that went was a REAL one while the phantom stayed.

     430ms   lanes [99, 0, 1, 2, 3, 4, 5]
     1300ms  lanes [99, 0, 1, 2, 3, 4]

   Denis ruled: trace what performs that trim before anyone guesses at a fix,
   because a pool entry with no seat might be legitimate on a path nobody has
   walked, and a cleanup built on the assumption that it is always garbage would
   delete a die that was supposed to be there.

   THIS PROBE FIXES NOTHING. It watches.

   Run 1 of this probe wrapped _removeDieAt and the roll never left phase
   'rolling' in 1800ms, where the earlier unwrapped run reached 'choosing' by
   1300ms. So the wrapper is a suspect for the stall and is GONE rather than
   reasoned about.

   The new hypothesis comes from afterRoll's own comment: "if anything in the
   body throws, the catch unsticks the phase from 'rolling'". A crash in
   _afterRollImpl would explain the stall AND a pool left half-updated. So this
   run captures console.error, which is where that catch logs. */
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(f,ms)=>{const t=Date.now();while(Date.now()-t<ms){try{if(f())return true;}catch(e){}await sleep(50);}return false;};
if(typeof launchBossMatch!=='function')return{error:'globals missing'};

const crashes=[];
const _ce=console.error;
console.error=function(){
  try{crashes.push(Array.from(arguments).map(String).join(' ').slice(0,300));}catch(e){}
  return _ce.apply(console,arguments);
};
window.addEventListener('error',function(e){crashes.push('window.onerror: '+e.message);});

_getS(); S.run=S.run||{}; S.run.tier=2;
S.run.dice=['bone','iron','flint','lead','amber','brass'];
S.settings=S.settings||{}; S.settings.reducedMotion=true;
launchBossMatch();
if(!(await until(()=>typeof G!=='undefined'&&G&&G.rung,9000))){console.error=_ce;return{error:'no match'};}
await sleep(700);
try{startPTurn();}catch(e){}
await sleep(250);
G.matchDice=['bone','iron','flint','lead','amber','brass'];
G._enchArr=[null,null,null,null,null,null];G.numDice=6;G.pool=[];
try{handleRoll();}catch(e){}
if(!(await until(()=>G&&G.pool&&G.pool.length>0,8000))){console.error=_ce;return{error:'no pool'};}
await sleep(650);
if(!G.pool.length){console.error=_ce;return{error:'pool emptied before the seed'};}

/* seed the phantom, exactly as the S6 arm did */
const keep=G.pool[0];
G.pool=[keep];
keep.lane=99;
crashes.length=0;

const frames=[];
let lastLen=null, dropFrame=null;
const tick=setInterval(function(){
  try{
    if(!G||!G.pool)return;
    const len=G.pool.length;
    const f={t:frames.length*40, len:len, phase:G.phase,
             md:(G.matchDice||[]).length, numDice:G.numDice,
             lanes:G.pool.map(d=>d.lane)};
    if(lastLen!==null&&len<lastLen&&dropFrame===null)dropFrame=Object.assign({},f,{from:lastLen});
    lastLen=len;
    if(frames.length<110)frames.push(f);
  }catch(e){}
},40);

try{handleRoll();}catch(e){crashes.push('handleRoll threw: '+e.message);}
await sleep(4000);
clearInterval(tick);
console.error=_ce;

return {
  crashes:crashes.slice(0,6),
  phasesSeen:Array.from(new Set(frames.map(f=>f.phase))),
  dropDetected:dropFrame,
  frames: dropFrame ? frames.filter(f=>Math.abs(f.t-dropFrame.t)<=160)
                    : frames.filter((f,i)=>i%14===0),
  finalPool:(G.pool||[]).map(d=>d.lane),
  finalMatchDice:(G.matchDice||[]).length,
  finalNumDice:G.numDice,
  domDiceInRow:document.querySelectorAll('#playerDiceRow .die').length,
  conclusion:
    (crashes.length&&dropFrame) ? 'afterRoll CRASHED and the pool shrank - the recovery path is the trim'
    : crashes.length ? 'a crash was logged but no drop seen - the crash is real, the trim is elsewhere'
    : dropFrame ? 'the pool shrank with NO crash - a filter or a rebuild did it'
    : 'no crash and no drop in this run'
};
