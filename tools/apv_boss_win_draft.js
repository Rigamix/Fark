/* P820: win the Grog boss match -> SPOILS grid renders -> take the
 * purse -> the FAMILY DRAFT must follow on the same card (offer
 * rendered, skip hoisted, end-btns hidden), the decline gold reads
 * from the BOSS purse, and claiming a card lands it in S.run.fcards
 * with the end screen back in 'ready'. */
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(fn,ms)=>{const t0=Date.now();while(Date.now()-t0<ms){try{if(fn())return true;}catch(e){}await sleep(120);}return false;};
const tap=el=>{if(!el)return false;const r=el.getBoundingClientRect();
  const o={bubbles:true,cancelable:true,clientX:r.left+r.width/2,clientY:r.top+r.height/2};
  el.dispatchEvent(new PointerEvent('pointerdown',o));
  el.dispatchEvent(new PointerEvent('pointerup',o));
  el.dispatchEvent(new MouseEvent('click',o));return true;};
if(!await until(()=>typeof launchBossMatch==='function'&&typeof G!=='undefined',20000))return {err:'no boot'};
window._fkDiscardOk=true;
launchBossMatch();
if(!await until(()=>G&&G.phase==='idle',20000))return {err:'no match'};
await sleep(3000);
G.pF=[];try{famRenderRow();}catch(e){}
const Q=[1,1,1,2,3,4];
const realE=window._enchRollM;
window._enchRollM=(m,e)=>Q.length?Q.shift():realE(m,e);
G.pPts=(G.target||4000)-1000;try{updHUD();}catch(e){}
tap(document.getElementById('btnRoll'));
if(!await until(()=>G.phase==='choosing',15000))return {err:'no roll'};
await sleep(600);
const ones=G.pool.filter(d=>!d.committed&&d.val===1);
tap(ones[0].el);await sleep(120);tap(ones[1].el);await sleep(120);tap(ones[2].el);await sleep(300);
const gold0=(S.run.gold||0);
tap(document.getElementById('btnBank'));
if(!await until(()=>G._endMatchFired,20000))return {err:'no win'};
/* the spoils grid */
if(!await until(()=>{const rc=document.querySelector('#end-ov .res-card');
  return rc&&rc.textContent.indexOf('SPOILS')>=0;},20000))return {err:'no spoils'};
await sleep(600);
const bossGoldStashed=S.run._lastWinGold;
/* take the purse through the pick the confirm modal targets */
const purseBefore=S.run.gold;
famSpoilsPick('purse');
/* the DRAFT must follow */
const draftShown=await until(()=>{const rc=document.querySelector('#end-ov .res-card');
  return rc&&rc.querySelectorAll('.fo-offer .fo-card, .fo-offer [class*=card]').length>0
    &&rc.textContent.indexOf('PURSE')>=0;},15000);
await sleep(700);
const rc=document.querySelector('#end-ov .res-card');
const offerCards=rc?rc.querySelectorAll('.fo-offer .fo-card,.fo-offer .focard,.fo-card').length:0;
const skipHoisted=document.querySelectorAll('#end-ov>.fo-skip').length===1;
const endBtnsHidden=(document.getElementById('end-btns')||{}).style
  &&document.getElementById('end-btns').style.display==='none';
const dg=(typeof _famDeclineGold==='function')?_famDeclineGold():null;
const fc0=(S.run.fcards||[]).length;
/* claim the first offer */
try{famDraftPick(0);}catch(e){return {err:'pick threw: '+e.message,offerCards,draftShown};}
const claimed=await until(()=>(S.run.fcards||[]).length>fc0,10000);
const ready=await until(()=>{const eb=document.getElementById('end-btns');
  return eb&&eb.style.display!=='none';},10000);
return {bossGoldStashed,purseGain:S.run.gold-purseBefore,draftShown,offerCards,
  skipHoisted,endBtnsHidden,declineGold:dg,claimed,ready,
  fcards:(S.run.fcards||[]).map(c=>c.id),
  verdicts:{
    spoilsStillPay:S.run.gold>purseBefore,
    draftFollowsSpoils:draftShown&&offerCards>0,
    skipHoistedToOverlay:skipHoisted,
    declineReadsBossPurse:!!bossGoldStashed&&dg>=Math.round(bossGoldStashed*0.75),
    cardClaimed:claimed,
    endScreenReady:ready},
  verdict:draftShown&&offerCards>0&&skipHoisted&&claimed&&ready};
