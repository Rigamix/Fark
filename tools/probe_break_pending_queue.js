/* S4 - is G._breakPending really a single slot that loses a Break?

   The comment claims deferring Break to after the commit means "nothing is
   duplicated and nothing is skipped". _iconFire is called once per committed
   die (24988 in the roll path, 26933 in the bank path) and the break enchant's
   fire does G._breakPending={src:c.die} - an assignment, not a push. The
   consume is a single `if` AFTER the loop.

   So two branded faces committed together should leave exactly one Break armed
   and silently drop the other. Driven here rather than argued.

   The probe calls _iconFire directly, which is the unit the defect lives in -
   the same call the commit loop makes, one die at a time. It does NOT drive a
   real two-skull commit, and says so. */
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(f,ms)=>{const t=Date.now();while(Date.now()-t<ms){try{if(f())return true;}catch(e){}await sleep(50);}return false;};
if(typeof launchBossMatch!=='function')return{error:'globals missing'};
if(typeof _iconFire!=='function')return{error:'_iconFire is not global'};

_getS(); S.run=S.run||{}; S.run.tier=2;
S.run.dice=['bone','iron','flint','lead','amber','brass'];
S.run.cards=S.run.cards||[]; S.settings=S.settings||{}; S.settings.reducedMotion=true;
launchBossMatch();
if(!(await until(()=>typeof G!=='undefined'&&G&&G.rung,9000)))return{error:'no match'};
await sleep(700);
try{if(typeof startPTurn==='function')startPTurn();}catch(e){}
await sleep(250);
try{if(typeof handleRoll==='function')handleRoll();}catch(e){}
if(!(await until(()=>G&&G.pool&&G.pool.length>=3,9000)))return{error:'no pool'};
await sleep(700);

/* two dice wearing a Break brand, exactly as a loadout with two may carry */
const d0=G.pool[0], d1=G.pool[1];
d0.ench={t:'break'}; d1.ench={t:'break'};
G._breakPending=null;

/* count how many times the brand actually fires, and how many Breaks start */
let fires=0, begins=0;
const realBegin=window._breakBegin;
window._breakBegin=function(src){begins++;return false;/* refuse, so nothing is destroyed mid-probe */};

const _pendHead=()=>{const q=G._breakPending;if(!q)return null;
  return Array.isArray(q)?((q[0]||{}).src||null):(q.src||null);};
const seen=[];
_iconFire(d0,'p');
fires++;
seen.push({queueLen:(Array.isArray(G._breakPending)?G._breakPending.length:(G._breakPending?1:0)), after:'first fire', pendingIs: G._breakPending? (G._breakPending.src===d0?'die0':(G._breakPending.src===d1?'die1':'other')) : null});
_iconFire(d1,'p');
fires++;
seen.push({queueLen:(Array.isArray(G._breakPending)?G._breakPending.length:(G._breakPending?1:0)), after:'second fire', pendingIs: G._breakPending? (G._breakPending.src===d0?'die0':(G._breakPending.src===d1?'die1':'other')) : null});

/* the consume, through the shipped path. Post-P526 this is _drainBreakQueue,
   which starts one Break and leaves the rest queued for _breakDie to drain. */
let consumed=0;
if(typeof _drainBreakQueue==='function'){
  _drainBreakQueue(); consumed++;
  /* _breakBegin is stubbed to return false above, so the drain walks the WHOLE
     queue looking for a startable Break - which is the correct behaviour and
     means every armed brand is seen. Count begins, not queue length. */
}else{
  if(G._breakPending){ var _bp=G._breakPending; G._breakPending=null; _breakBegin(_bp.src); consumed++; }
}
const leftover=G._breakPending;

window._breakBegin=realBegin;

/* post-P526 the queue holds BOTH, so `pendingIs` reports the queue's head and
   the first brand is no longer overwritten. */
const firstWasLost = seen[1].pendingIs==='die1' && seen[0].pendingIs==='die0';
const bothArmed = seen[0].queueLen===1 && seen[1].queueLen===2;
return {
  NOTE:'_iconFire called directly - the same call the commit loop makes per die. A real two-skull commit was not driven.',
  isArrayQueue: Array.isArray(G._breakPending),
  sequence:seen,
  brandFires:fires, breaksStarted:begins, consumesRun:consumed,
  leftoverAfterConsume:leftover,
  firstBrandOverwritten:firstWasLost,
  bothBrandsArmed:bothArmed,
  verdict:
    bothArmed && begins===2
      ? 'FIXED - both brands queued and both Breaks were offered a target'
    : firstWasLost && begins===1
      ? 'DEFECT PRESENT - two brands fired, the first was overwritten, one Break ran'
      : 'UNEXPECTED - see the sequence'
};
