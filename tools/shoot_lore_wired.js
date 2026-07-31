const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(fn,ms)=>{const t0=Date.now();while(Date.now()-t0<ms){try{if(fn())return true;}catch(e){}await sleep(60);}return false;};
const vis=el=>{if(!el||!el.isConnected)return false;const s=getComputedStyle(el),r=el.getBoundingClientRect();
 return s.display!=='none'&&s.visibility!=='hidden'&&+s.opacity>0.05&&r.width>1&&r.height>1;};
const tap=el=>{if(!vis(el))return false;const r=el.getBoundingClientRect();
 const o={bubbles:true,cancelable:true,clientX:r.left+r.width/2,clientY:r.top+r.height/2};
 el.dispatchEvent(new PointerEvent('pointerdown',o));el.dispatchEvent(new PointerEvent('pointerup',o));
 el.dispatchEvent(new MouseEvent('click',o));return true;};
tap(document.getElementById('hsBtnBottom'));await sleep(1800);
await until(()=>{const d=document.querySelector('.nrdie');return d&&d._floatDone;},9000);
tap(document.querySelector('.nrdie'));await sleep(1300);
tap(document.getElementById('nrTakeBtn'));await sleep(1900);
const p=[...document.querySelectorAll('.ptcard')].filter(vis)[0];if(p){tap(p);await sleep(1700);}
const sit=[...document.querySelectorAll('span,div,button')].filter(e=>vis(e)&&e.children.length<=1&&/^SIT\s*DOWN$/i.test((e.textContent||'').trim()))[0];
if(sit){tap(sit);if(sit.parentElement)tap(sit.parentElement);}
await until(()=>vis(document.getElementById('screen-match')),9000);
await until(()=>typeof G!=='undefined'&&G&&G.phase==='idle',14000);
_getS();
const LORE=new Set(PATRON_LINES.map(r=>r.t));
const R={seat:window._lastSeatArt,trait:window._lastSeatTrait,isBoss:!!G._isBoss};

/* 1. THE WIN/LOSS BEAT MUST NEVER CARRY LORE */
const wl=[];for(let i=0;i<300;i++){const l=DLG.getLine('OPP_WINS');if(l)wl.push(l);}
R.winLoss_samples=wl.length;
R.winLoss_anyLore=wl.some(l=>LORE.has(l));

/* 2. every other in-match category CAN reach lore */
const reach=(cat,n)=>{const hit=[];for(let i=0;i<n;i++){const l=DLG.getLine(cat);if(l&&LORE.has(l))hit.push(l);}return hit;};
R.matchStart_personal=reach('MATCH_START',60).length>0;
R.oppBust_trait=reach('OPP_BUST',60).length>0;
R.playerBust_trait=reach('PLAYER_BUST',60).length>0;
R.oppBigBank_trait=reach('OPP_BIG_BANK',60).length>0;
R.bigBank_trait=reach('BIG_BANK',60).length>0;
const amb=reach('EARLY_BANK',400).concat(reach('MATCH_CLOSE',400));
R.ambient_reached=amb.length>0;
const KING=new Set(PATRON_LINES.filter(r=>r.p==='reaction:king').map(r=>r.t));
const TOWN=new Set(PATRON_LINES.filter(r=>r.p==='gossip:town').map(r=>r.t));
R.ambient_king=amb.some(l=>KING.has(l));
R.ambient_town=amb.some(l=>TOWN.has(l));
R.ambient_rateApprox=+(amb.length/800).toFixed(2);
/* the King's intro tier must lead - a speculation line can't be first */
const firstKing=amb.filter(l=>KING.has(l))[0];
const INTRO=new Set(PATRON_LINES.filter(r=>r.tag==='king_intro').map(r=>r.t));
R.firstKingLineWasIntro=firstKing?INTRO.has(firstKing):null;

/* 3. a boss keeps its own voice entirely */
G._isBoss=true;
const bossLines=[];for(let i=0;i<80;i++){const l=DLG.getLine('OPP_BUST');if(l)bossLines.push(l);}
R.boss_anyLore=bossLines.some(l=>LORE.has(l));
G._isBoss=false;
return R;
