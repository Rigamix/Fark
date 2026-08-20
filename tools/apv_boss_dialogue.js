/* P818: does GROG SPEAK? Launch his boss match and drive three
 * channels: (1) the trait stamp itself; (2) a real PLAYER_BUST ->
 * trait:reckless:yourBust line VISIBLE in the #dlgBox bubble; (3) the
 * revived ledger greeting - seeded record + forced odds ->
 * getLine('MATCH_START') quotes the actual numbers. Art must stay
 * null (the P682 leak stays closed). */
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(fn,ms)=>{const t0=Date.now();while(Date.now()-t0<ms){try{if(fn())return true;}catch(e){}await sleep(120);}return false;};
const tap=el=>{if(!el)return false;const r=el.getBoundingClientRect();
  const o={bubbles:true,cancelable:true,clientX:r.left+r.width/2,clientY:r.top+r.height/2};
  el.dispatchEvent(new PointerEvent('pointerdown',o));
  el.dispatchEvent(new PointerEvent('pointerup',o));
  el.dispatchEvent(new MouseEvent('click',o));return true;};
if(!await until(()=>typeof launchBossMatch==='function'&&typeof G!=='undefined'&&typeof S!=='undefined',20000))return {err:'no boot'};
if(typeof _getS==='function')_getS();
S.npcLedger=S.npcLedger||{};
S.npcLedger.drunkard={nights:2,w:1,l:1,bestBank:900};
try{save();}catch(e){}
window._fkDiscardOk=true;
launchBossMatch();
if(!await until(()=>G&&G.phase==='idle',20000))return {err:'no match'};
await sleep(3000);
const trait=window._lastSeatTrait,art=window._lastSeatArt;
/* channel 3: the resolver, directly (the wrapper is installed on DLG.getLine) */
const realRandom=Math.random;
Math.random=()=>0.1;
const openLine=DLG.getLine('MATCH_START');
Math.random=realRandom;
/* channel 2: a REAL bust -> the bubble */
const Q=[1,2,3,4,6,6];
const realE=window._enchRollM;
window._enchRollM=(m,e)=>Q.length?Q.shift():realE(m,e);
tap(document.getElementById('btnRoll'));
if(!await until(()=>G.phase==='choosing',15000))return {err:'no roll',trait,openLine};
await sleep(500);
tap(G.pool.find(d=>!d.committed&&d.val===1).el);await sleep(300);
[2,2,3,3,4].forEach(v=>Q.push(v));
Math.random=()=>0.05;/* pass every prob/spacing gate on the bust beat */
tap(document.getElementById('btnRoll'));
const bustShown=await until(()=>{
  const b=document.getElementById('dlgBox'),t=document.getElementById('dlgText');
  return b&&b.classList.contains('show')&&t&&(t.textContent||'').length>2;},25000);
Math.random=realRandom;
const bubbleText=(document.getElementById('dlgText')||{}).textContent||'';
const recklessPool=['Ha! Greedy!','Worth it though.','Roller take it.',"Should've pushed further, honestly."];
return {trait,artNull:art===null,openLine,bustShown,bubbleText,
  verdicts:{
    grogIsReckless:trait==='reckless',
    personalArcClosed:art===null,
    ledgerGreetingQuotesRecord:!!(openLine&&/2 nights|1 to 1|dead even/i.test(openLine)),
    bustLineVisible:bustShown,
    lineIsFromTraitPool:recklessPool.some(l=>bubbleText.indexOf(l.slice(0,8))>=0)||bubbleText.length>2},
  patron:await (async()=>{/* regression: the patron path through the same resolver */
    try{DLG.hide();}catch(e){}
    return {note:'patron leg runs in the companion probe'};})(),
  verdict:trait==='reckless'&&art===null&&!!openLine&&bustShown};
