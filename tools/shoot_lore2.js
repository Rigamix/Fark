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
tap(document.getElementById('nrTakeBtn'));await sleep(2200);
_getS();
const R={};
const T1=new Set(PATRON_LINES.filter(r=>r.tag==='king_intro').map(r=>r.t));
const T2=new Set(PATRON_LINES.filter(r=>r.p==='reaction:king'&&(r.c||[]).length===1).map(r=>r.t));
const T3=new Set(PATRON_LINES.filter(r=>r.p==='reaction:king'&&(r.c||[]).length===2).map(r=>r.t));
R.poolSizes={tier1:T1.size,tier2:T2.size,tier3:T3.size,
  gossip:PATRON_LINES.filter(r=>r.p==='gossip:town').length,
  trait:PATRON_LINES.filter(r=>String(r.p).indexOf('trait:')===0).length};

/* 1. before any intro has fired, ONLY tier 1 can be drawn */
const seenEarly=new Set();
for(let i=0;i<60;i++){S.run._dlgStage={};S.run._dlgHeard={};S.run.tier=0;
  const l=_dlgPick('reaction:king',0,S.run._dlgHeard); if(l)seenEarly.add(l.t);}
R.beforeIntro_onlyTier1=[...seenEarly].every(t=>T1.has(t));
R.beforeIntro_distinct=seenEarly.size;

/* 2. once an intro has been heard, tier 2 opens */
S.run._dlgStage={};S.run._dlgHeard={king_intro:1};S.run.tier=0;
const seenAfter=new Set();
for(let i=0;i<80;i++){const l=_dlgPick('reaction:king',0,{}); if(l)seenAfter.add(l.t);}
R.afterIntro_tier2Opens=[...seenAfter].some(t=>T2.has(t));
R.afterIntro_tier3StillShut=![...seenAfter].some(t=>T3.has(t));

/* 3. tier 3 needs BOTH the intro and night>=6 */
S.run._dlgHeard={king_intro:1};S.run.tier=5;
const late=new Set();
for(let i=0;i<80;i++){const l=_dlgPick('reaction:king',0,{}); if(l)late.add(l.t);}
R.night6_tier3Opens=[...late].some(t=>T3.has(t));

/* 4. the tag records when an intro line actually speaks. Krox cannot reach the
      King pool at all now - he has personal lines and personal always wins -
      so this uses a patron with no authored pool, which is what the ambient
      fallback is for. */
S.run._dlgStage={};S.run._dlgHeard={};
let guard=0; while(!S.run._dlgHeard.king_intro&&guard++<40)_dlgSay('nobody_here');
R.tagRecordedBySay=!!S.run._dlgHeard.king_intro;
/* 4b. and confirm the consequence: a patron WITH personal lines never reaches
       the ambient pools, because a stage-0 line is a floor and so never runs out */
S.run._dlgStage={};S.run._dlgHeard={};
const kroxSaid=new Set(); for(let i=0;i<30;i++)kroxSaid.add(_dlgSay('krox'));
const personal=new Set(PATRON_LINES.filter(r=>r.p==='patron:krox').map(r=>r.t));
R.krox_neverLeavesOwnPool=[...kroxSaid].every(t=>personal.has(t));

/* 5. the in-match pools resolve per trait and moment */
window._lastSeatArt='Sil'; window._lastSeatTrait='reckless';
R.trait_reckless_bust=_dlgEvent('bust');
R.bespoke_sil_bust=(()=>{window._lastSeatArt='Sil';return _dlgEvent('bust');})();
window._lastSeatArt='Regis'; window._lastSeatTrait='cunning';
R.bespoke_regis_bank=_dlgEvent('bank');
window._lastSeatArt='Krox'; window._lastSeatTrait='steady';
R.trait_steady_yourBank=_dlgEvent('yourBank');
R.unknownMoment=_dlgEvent('nonsense');
return R;
