/* 1c DOUBLE STAKES, measured economy: two seats, same forged win, one
 * armed. Falsifiable: buyB must be exactly 2x buyA and payoutB exactly
 * 2x payoutA - measured as gold deltas, not read from code. */
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(fn,ms)=>{const t0=Date.now();while(Date.now()-t0<ms){try{if(fn())return true;}catch(e){}await sleep(120);}return false;};
if(!await until(()=>typeof launchSeat==='function'&&typeof S!=='undefined',20000))return {err:'no boot'};
_getS();
async function playSeat(idx,arm){
  S.run.gold=1000;S.run._dsArmed=!!arm;save();
  const g0=S.run.gold;
  launchSeat(idx);
  if(!await until(()=>G&&G.phase,14000))return {err:'no match '+idx};
  const g1=S.run.gold;               /* after buy */
  const buy=g0-g1;
  const dsFlag=!!(G&&G._doubleStakes);
  await sleep(2500);
  G.pPts=(G.target||1500)+100;       /* forged win */
  endMatch(true);
  if(!await until(()=>!document.getElementById('screen-match').classList.contains('active')||S.run.gold>g1,15000)){}
  await sleep(2600);                 /* the payout lands inside endMatch timers */
  const g2=S.run.gold;
  /* leave the end screen */
  try{handleContinue();await sleep(600);handleContinue();}catch(e){}
  await sleep(1200);
  return {buy:buy,payout:g2-g1,dsFlag:dsFlag};
}
const A=await playSeat(0,false);
if(A.err)return A;
const B=await playSeat(1,true);
if(B.err)return Object.assign(B,{A:A});
return {A:A,B:B,
  verdicts:{
    buyDoubles:B.buy===A.buy*2&&A.buy>0,
    flagReaches:B.dsFlag===true&&A.dsFlag===false,
    payoutDoubles:B.payout===A.payout*2&&A.payout>0
  },
  verdict:B.buy===A.buy*2&&B.dsFlag&&!A.dsFlag&&B.payout===A.payout*2&&A.payout>0};
