/* P839, two legs. A: the exact construction that VOIDED pre-P839
 * (skim cuts a 1,000 bank to 700 on Grog's LAST CALL table) now PAYS
 * 700 - and a genuinely sub-floor bank still voids with the skim's
 * cut kept. B: the greeting state router - open / undefeated /
 * firstloss / beaten pools answer their ledger states. */
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(fn,ms)=>{const t0=Date.now();while(Date.now()-t0<ms){try{if(fn())return true;}catch(e){}await sleep(120);}return false;};
const tap=el=>{if(!el)return false;const r=el.getBoundingClientRect();
  const o={bubbles:true,cancelable:true,clientX:r.left+r.width/2,clientY:r.top+r.height/2};
  el.dispatchEvent(new PointerEvent('pointerdown',o));
  el.dispatchEvent(new PointerEvent('pointerup',o));
  el.dispatchEvent(new MouseEvent('click',o));return true;};
if(!await until(()=>typeof launchBossMatch==='function'&&typeof S!=='undefined',20000))return {err:'no boot'};
window._fkDiscardOk=true;
launchBossMatch();
if(!await until(()=>typeof G!=='undefined'&&G&&G.phase==='idle',20000))return {err:'no match'};
await sleep(3000);
G.oCards=['the_skim'];
G.pF=[];try{famRenderRow();}catch(e){}
G.oPts=1000;try{updHUD();}catch(e){}
const Q=[1,1,1,2,3,4];
const realE=window._enchRollM;
window._enchRollM=(m,e)=>Q.length?Q.shift():realE(m,e);
/* LEG A1: 1000 pre-take, skimmed to 700 - must PAY 700 now */
tap(document.getElementById('btnRoll'));
if(!await until(()=>G.phase==='choosing',15000))return {err:'no roll'};
await sleep(600);
const ones=G.pool.filter(d=>!d.committed&&d.val===1);
tap(ones[0].el);await sleep(120);tap(ones[1].el);await sleep(120);tap(ones[2].el);await sleep(300);
const p0=G.pPts,o0=G.oPts;
tap(document.getElementById('btnBank'));
const paid=await until(()=>G.pPts>p0,15000);
const gainA=G.pPts-p0;           /* 700 */
const skimA=G.oPts-o0;           /* +300 at minimum (before their turn) */
/* LEG A2: next turn, keep one 1 -> pre-take 100 < 800 -> still voided */
if(!await until(()=>G.phase==='idle'&&(G.turnNum||0)>=2,90000))return {err:'no turn 2',gainA};
await sleep(2000);
G.oCards=['the_skim'];/* survive any state the rival turn touched */
[1,2,3,4,6,2].forEach(v=>Q.push(v));
tap(document.getElementById('btnRoll'));
if(!await until(()=>G.phase==='choosing'&&(G.turnRollCount||0)===1,15000))return {err:'no roll 2'};
await sleep(500);
tap(G.pool.find(d=>!d.committed&&d.val===1).el);await sleep(300);
const p1=G.pPts;
tap(document.getElementById('btnBank'));
await until(()=>G.phase==='opp'||(G.turnNum||0)>=3||G.pPts>p1,15000);
await sleep(400);
const gainB=G.pPts-p1;           /* 0 - voided */
/* LEG B: the greeting router (direct resolver calls; the wrapper is
   installed on DLG.getLine and bosses always reach the original) */
const realRandom=Math.random;
Math.random=()=>0.99;/* dodge the 65% ledger record-greeting */
S.npcLedger={};
const gOpen=DLG.getLine('MATCH_START');
S.npcLedger.drunkard={nights:2,w:0,l:2,bestBank:0};
const gUndef=DLG.getLine('MATCH_START');
S.npcLedger.drunkard={nights:3,w:1,l:2,bestBank:0};
const gFirst=DLG.getLine('MATCH_START');
S.npcLedger.drunkard={nights:5,w:3,l:2,bestBank:0};
const gBeaten=DLG.getLine('MATCH_START');
Math.random=realRandom;
return {gainA,skimA,gainB,gOpen,gUndef,gFirst,gBeaten,
  verdicts:{
    clearedBankPaysPostTake:gainA===700,
    skimKeepsItsCut:skimA>=300,
    subFloorStillVoids:gainB===0,
    openLine:/Haven't seen you at my table/.test(gOpen||''),
    undefeatedLine:/Back again\? Suit yourself|Still trying|Same face/.test(gUndef||''),
    firstLossLine:/Beat me once|Wasn't expecting|got some nerve/.test(gFirst||''),
    beatenLine:/easy night|own the place|tonight's different/.test(gBeaten||'')},
  verdict:gainA===700&&skimA>=300&&gainB===0
    &&/Haven't seen/.test(gOpen||'')&&/Suit yourself|Still trying|Same face/.test(gUndef||'')
    &&/Beat me once|Wasn't expecting|nerve/.test(gFirst||'')&&/easy night|own the place|different/.test(gBeaten||'')};
