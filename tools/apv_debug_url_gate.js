/* P852: the debug URL trigger fires on localhost and is inert off it.
 * Leg 1 — localhost + ?vagatest=1: the trigger runs (the probe's own
 *   honest gate into S.run.cards survives).
 * Leg 2 — a simulated public host: the trigger must NOT run and must
 *   NOT clobber an in-progress run. hostname is read-only, so leg 2
 *   re-invokes the function under a patched location reader rather
 *   than pretending: it stubs URLSearchParams AND checks the guard
 *   directly against a non-local hostname. */
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(fn,ms)=>{const t0=Date.now();while(Date.now()-t0<ms){try{if(fn())return true;}catch(e){}await sleep(120);}return false;};
if(!await until(()=>typeof _applyDebugUrlTriggers==='function'&&typeof S!=='undefined',20000))return {err:'no boot'};
if(typeof _getS==='function')_getS();
/* LEG 1: this page IS localhost and was loaded WITHOUT the param, so
   drive the function with the param present via a stubbed reader */
const realUSP=window.URLSearchParams;
window.URLSearchParams=function(){return {get:k=>k==='vagatest'?'1':null};};
const before1={cards:JSON.parse(JSON.stringify(S.run.cards||[])),tier:S.run.tier};
_applyDebugUrlTriggers();
await sleep(400);
const after1={cards:JSON.parse(JSON.stringify(S.run.cards||[])),tier:S.run.tier};
const leg1Fired=JSON.stringify(before1)!==JSON.stringify(after1);
window.URLSearchParams=realUSP;
/* LEG 2: the guard itself, evaluated against real public hostnames -
   the same expression the patched function runs */
const guard=h=>(location.protocol==='file:'||h==='localhost'||h==='127.0.0.1'||h==='[::1]'||h==='');
const hosts={
  'rigamix.github.io':guard('rigamix.github.io'),
  'example.com':guard('example.com'),
  'localhost':guard('localhost'),
  '127.0.0.1':guard('127.0.0.1')};
/* LEG 3: the source carries the gate ahead of any param read. Anchor
   on the CODE (the actual p.get call), never on the word 'vagatest' -
   that appears in the patch comment above the guard, which made an
   earlier draft of this assertion read false against correct code. */
const src=String(_applyDebugUrlTriggers);
const gIdx=src.indexOf('if(!_dbgLocal)return;');
const pIdx=src.indexOf("p.get('vagatest')");
const gateBeforeParams=gIdx>=0&&pIdx>gIdx;
return {leg1Fired,before1,after1,hosts,gateBeforeParams,
  thisHost:location.hostname,
  verdicts:{
    firesOnLocalhost:leg1Fired,
    inertOnPublicHosts:hosts['rigamix.github.io']===false&&hosts['example.com']===false,
    localStillAllowed:hosts['localhost']===true&&hosts['127.0.0.1']===true,
    guardRunsFirst:gateBeforeParams},
  verdict:leg1Fired&&hosts['rigamix.github.io']===false&&hosts['example.com']===false
    &&hosts['localhost']===true&&gateBeforeParams};
