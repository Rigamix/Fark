/* P535, measured at the decision rather than at its consequences.

   The first probe watched G.phase and concluded "no bust". That cannot
   distinguish the three things it needs to:
     the timeout judged the table dead and busted
     the timeout judged it dead and a BUST SAVE absorbed it (phase unchanged)
     the timeout judged it alive because it read a stale capture
   Only the third is the defect, and phase looks identical for the last two.

   So wrap the two functions the decision actually calls - _tryBustSave and
   _delayedDoBust - and record WHAT SET was handed to them. That is the whole
   question: does the judgement see the die that was removed?

   ONE ARM PER RUN. The previous probe's later arms reported "no pool" because
   the fixture had moved on - the same degradation caught in the S6 work. */
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(f,ms)=>{const t=Date.now();while(Date.now()-t<ms){try{if(f())return true;}catch(e){}await sleep(50);}return false;};
if(typeof launchBossMatch!=='function')return{error:'globals missing'};

const calls=[];
const realSave=window._tryBustSave, realBust=window._delayedDoBust;
window._tryBustSave=function(set){
  calls.push({fn:'_tryBustSave', n:(set||[]).length, vals:(set||[]).map(d=>d&&d.val)});
  return realSave.apply(this, arguments);
};
window._delayedDoBust=function(set){
  calls.push({fn:'_delayedDoBust', n:(set||[]).length, vals:(set||[]).map(d=>d&&d.val)});
  return realBust.apply(this, arguments);
};

_getS(); S.run=S.run||{}; S.run.tier=2;
S.run.dice=['bone','iron','flint','lead','amber','brass'];
S.run.cards=[];                      /* no bust saves, so nothing absorbs it */
S.settings=S.settings||{}; S.settings.reducedMotion=true;
launchBossMatch();
if(!(await until(()=>typeof G!=='undefined'&&G&&G.rung,9000))){window._tryBustSave=realSave;window._delayedDoBust=realBust;return{error:'no match'};}
await sleep(650);
try{startPTurn();}catch(e){}
await sleep(200);
try{handleRoll();}catch(e){}
if(!(await until(()=>G&&G.pool&&G.pool.length>=4,8000))){window._tryBustSave=realSave;window._delayedDoBust=realBust;return{error:'no pool'};}
await sleep(700);
if(G.pool.length<4){window._tryBustSave=realSave;window._delayedDoBust=realBust;return{error:'pool too small'};}

const JUNK=[2,3,4,2,3];
G.pool.forEach(function(d,i){d.committed=false;d.sel=false;d._frozen=false;d.ench=null;});
G.phase='choosing';
calls.length=0;
try{CFX.powder_keg.use({tier:1});}catch(e){window._tryBustSave=realSave;window._delayedDoBust=realBust;return{error:'keg threw '+e.message};}

/* inside the keg's 500ms window: one scorer plus a dead hand, then take the
   scorer. The CAPTURED set still holds a 1; the LIVE table does not. */
await sleep(120);
G.pool.forEach(function(d,i){d.val=(i===0)?1:JUNK[(i-1)%JUNK.length];});
try{G.pool.forEach(function(d){reDrawDieFace(d);});}catch(e){}
const capturedFaces=G.pool.map(d=>d.val);
const victim=G.pool[0];
let removed=false;
if(victim&&typeof victim.lane==='number'){_removeDieAt(victim.lane);removed=!G.pool.some(d=>d.val===1);}
const liveFaces=G.pool.map(d=>d.val);
let liveDead=null;
try{const f=G.pool.filter(d=>!d.committed);
    liveDead=!anyScoring(f.map(d=>d.val),effectiveCards(),f.map(d=>d.mat),f);}catch(e){}

await sleep(1400);
window._tryBustSave=realSave; window._delayedDoBust=realBust;

const judged = calls.length ? calls[0] : null;
const sawTheRemovedDie = !!(judged && judged.vals.indexOf(1) !== -1);
return {
  capturedFaces:capturedFaces, liveFaces:liveFaces,
  scorerRemoved:removed, liveTableIsDead:liveDead,
  bustCalls:calls,
  judgedAgainst: judged ? (judged.n + ' dice: ' + JSON.stringify(judged.vals)) : 'nothing was called',
  verdict:
    !removed ? 'INCONCLUSIVE - the scorer was never removed'
    : liveDead !== true ? 'INCONCLUSIVE - the live table still scores, so no bust is correct'
    : !judged ? 'FAIL - the table was dead and the bust path was never entered at all'
    : sawTheRemovedDie ? 'FAIL - the judgement was handed the removed die (stale capture)'
    : 'PASS - the judgement was handed the LIVE table, without the removed die'
};
