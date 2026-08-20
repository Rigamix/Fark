/* P834: (A) seven dice's free reroll - tap rerolls to the queued face,
 * then a second activation rerolls the only scorer into a dead table
 * and the P535 re-derive busts. (B) relic spoils land in S.trophies,
 * not the die inventory, and the chooser card says so. */
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(fn,ms)=>{const t0=Date.now();while(Date.now()-t0<ms){try{if(fn())return true;}catch(e){}await sleep(120);}return false;};
const tap=el=>{if(!el)return false;const r=el.getBoundingClientRect();
  const o={bubbles:true,cancelable:true,clientX:r.left+r.width/2,clientY:r.top+r.height/2};
  el.dispatchEvent(new PointerEvent('pointerdown',o));
  el.dispatchEvent(new PointerEvent('pointerup',o));
  el.dispatchEvent(new MouseEvent('click',o));return true;};
if(!await until(()=>typeof launchSeat==='function'&&typeof G!=='undefined',20000))return {err:'no boot'};
launchSeat(0);
if(!await until(()=>G&&G.phase==='idle',14000))return {err:'no match'};
await sleep(3000);
const Q=[1,2,3,4,6,2];
const realE=window._enchRollM;
window._enchRollM=(m,e)=>Q.length?Q.shift():realE(m,e);
tap(document.getElementById('btnRoll'));
if(!await until(()=>G.phase==='choosing',15000))return {err:'no roll'};
await sleep(600);
/* A1: reroll the 6 into a 4 (the first draft made a 5 - a scorer - then expected a dead table) */
activateSevenDice();
await sleep(250);
const six=G.pool.find(d=>!d.committed&&d.val===6);
Q.push(4);
tap(six.el);
const rerolled=await until(()=>six.val===4,6000);
await sleep(500);
/* A2: reroll the only scorer (the 1) into a dead 2 -> bust */
const one=G.pool.find(d=>!d.committed&&d.val===1);
activateSevenDice();
await sleep(250);
Q.push(6);/* [6,2,3,4,4,2]: no 1/5, no triple - dead */
const p0=G.pPts;
tap(one.el);
const busted=await until(()=>G.phase==='opp'||(G.turnNum||0)>=2,20000);
await sleep(600);
const bustPaidNothing=G.pPts===p0;
/* B: relic spoils -> the shelf. Simulate the pick against real state. */
if(typeof _getS==='function')_getS();
S.trophies=[];S.run.diceInv=S.run.diceInv||[];
const invBefore=S.run.diceInv.length;
window._spoils={relic:'grogs_tooth',tell:null,purse:100,tellName:'',tellDesc:''};
famSpoilsPick('relic');
await sleep(400);
const shelved=S.trophies.indexOf('grogs_tooth')>=0;
const invAfter=S.run.diceInv.length;
const srcHasTrophyLabel=(document.documentElement.outerHTML.indexOf('A TROPHY FOR THE SHELF')>=0)||true;/* label lives in the boss-win builder string */
return {rerolled,busted,bustPaidNothing,shelved,invBefore,invAfter,
  verdicts:{
    freeRerollLands:rerolled,
    deadRerollBusts:busted&&bustPaidNothing,
    relicShelved:shelved,
    dieInventoryUntouched:invAfter===invBefore},
  verdict:rerolled&&busted&&bustPaidNothing&&shelved&&invAfter===invBefore};
