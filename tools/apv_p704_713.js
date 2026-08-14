/* ONE consolidated verification for P704-P713. In-session asserts, then a
 * planted pendingMatch + reload: the final screenshot must show the TITLE
 * (P705), not the match. SUITE: exclude */
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(fn,ms)=>{const t0=Date.now();while(Date.now()-t0<ms){try{if(fn())return true;}catch(e){}await sleep(60);}return false;};
const vis=el=>{if(!el||!el.isConnected)return false;const s=getComputedStyle(el),r=el.getBoundingClientRect();
 return s.display!=='none'&&s.visibility!=='hidden'&&+s.opacity>0.05&&r.width>1&&r.height>1;};
const tap=el=>{if(!vis(el))return false;const r=el.getBoundingClientRect();
 const o={bubbles:true,cancelable:true,clientX:r.left+r.width/2,clientY:r.top+r.height/2};
 el.dispatchEvent(new PointerEvent('pointerdown',o));el.dispatchEvent(new PointerEvent('pointerup',o));
 el.dispatchEvent(new MouseEvent('click',o));return true;};
const out={};

/* ── P712 static surface: dead imgs gone, title art optimized ── */
out.deadImgs={main04:!!document.querySelector('img[src*="main_04"]'),
 settings:!!document.querySelector('img[src*="Settings/settings.png"]'),
 loadout:!!document.querySelector('img[src*="Loadout.png"]'),
 innkeeperStatic:!!document.querySelector('img.go-portrait[src*="Innkeeper"]')};
out.plateV1=(document.getElementById('matchPlate')||{src:''}).src.indexOf('?v=1')>0;
out.appleIcon=(document.querySelector('link[rel="apple-touch-icon"]')||{href:''}).href.indexOf('iOS_icon_180')>0;

/* boot into a run */
await until(()=>window.D3X&&D3X.frame,9000);
for(let a=0;a<3;a++){tap(document.getElementById('hsBtnBottom'));await sleep(2000);
 await until(()=>document.querySelector('.nrdie'),9000);await sleep(500);
 tap(document.querySelector('.nrdie'));await sleep(1200);
 tap(document.getElementById('nrTakeBtn'));await sleep(2400);
 if(await until(()=>typeof launchSeat==='function'&&S&&S.run,9000))break;}
_getS();
/* title art check (gbTitle was rendered before the run started) */
const hsB=document.getElementById('hsBase');
out.titleOptimized={bg:!!(hsB&&hsB.src.indexOf('bg_opt.webp')>0)};

/* ── launch a patron match for the in-match checks ── */
try{G=null;}catch(e){}
window._fkDiscardOk=true;
launchSeat(0);
let ok=await until(()=>typeof G!=='undefined'&&G&&G.phase==='idle',16000);
if(!ok){try{G=null;}catch(e){}launchSeat(0);
 ok=await until(()=>typeof G!=='undefined'&&G&&G.phase==='idle',16000);}
if(!ok)return {...out,err:'no idle'};

/* P706: short lines on one line, weight 400, outline 1.5 */
const lines=el=>{const r=el.getClientRects?[...el.getClientRects()]:[];
 const tr=document.createRange();tr.selectNodeContents(el);
 const rs=[...tr.getClientRects()].filter(r2=>r2.width>2);
 let ys=[];rs.forEach(r2=>{if(!ys.some(y=>Math.abs(y-r2.top)<4))ys.push(r2.top);});
 return ys.length;};
DLG.show('Fine, fine.');await sleep(600);
const te=document.getElementById('dlgText');
out.bubble={fineLines:lines(te),weight:getComputedStyle(te).fontWeight,
 strokeW:(window.DLG_BUBBLE||{}).strokeW};
DLG.show('Still worth it though.');await sleep(500);
out.bubble.stillLines=lines(te);
DLG.hide&&DLG.hide();

/* P713: armed glow + spent stillness (forced classes, computed styles) */
const card=document.querySelector('#famRowP .fcv');
if(card){
 card.classList.add('armed');await sleep(250);
 out.card={armedFilter:getComputedStyle(card).filter.indexOf('drop-shadow')>=0
   &&getComputedStyle(card).filter.indexOf('brightness')>=0};
 card.classList.remove('armed');
 card.classList.add('spent');await sleep(100);
 const inn=card.querySelector('.fcvIn');
 out.card.spentStill=inn?getComputedStyle(inn).animationName==='none':null;
 out.card.spentGrey=getComputedStyle(card).filter.indexOf('saturate')>=0;
 card.classList.remove('spent');
}else out.card={none:true};

/* P708: a right call pays the full reward even over an empty board */
G.pF=G.pF||[];
if(!G.pF.some(c=>c&&c.id==='ill_omen'))G.pF.push({id:'ill_omen',tier:1,charges:0,state:{}});
G._famIllOmen={tier:1};
const pB=G.pPts||0,oB=G.oPts=0;
famFire('rivalTurn',{actor:'p',pts:0});
await sleep(200);
out.illOmen={paid:(G.pPts-pB),expected:famDef('ill_omen').p[0][0],cleared:!G._famIllOmen};
out.illOmen.full=out.illOmen.paid===out.illOmen.expected;

/* P710: heart-loss reset relocks + reshuffles */
S.run.points=3;S.run._chalkMeta=['x','x','x'];
const rosterBefore=(S.run.night&&S.run.night.roster||[]).map(p=>p.persona).join(',');
const coinsB=S.run.coins=3;
_settleEndRoute({win:false,isBoss:true});
out.heartLoss={coins:S.run.coins,points:S.run.points,lastOrders:!!S.run._lastOrders,
 nightBack:!!(S.run.night&&S.run.night.roster&&S.run.night.roster.length),
 rosterChangedOrSame:(S.run.night&&S.run.night.roster||[]).map(p=>p.persona).join(',')!==rosterBefore?'reshuffled':'same-personas(possible)'};
delete S.run._lastOrders;save();

/* P705: plant a pending snapshot, reload - screenshot must show TITLE */
try{saveMatchState();}catch(e){}
out.pendingPlanted=!!S.pendingMatch;
setTimeout(function(){location.reload();},400);
out.verdict=!out.deadImgs.main04&&!out.deadImgs.settings&&!out.deadImgs.loadout
 &&!out.deadImgs.innkeeperStatic&&out.plateV1&&out.titleOptimized.bg
 &&out.bubble.fineLines===1&&out.bubble.stillLines===1&&out.bubble.weight==='400'
 &&out.bubble.strokeW===1.5&&out.card.armedFilter&&out.card.spentStill
 &&out.illOmen.full&&out.illOmen.cleared
 &&out.heartLoss.coins===2&&out.heartLoss.points===0&&out.heartLoss.lastOrders
 &&out.heartLoss.nightBack&&out.pendingPlanted;
return out;
