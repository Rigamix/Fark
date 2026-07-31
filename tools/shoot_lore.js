/* The resolver, against the brief's own worked example and its stated rules. */
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
tap(document.getElementById('nrTakeBtn'));await sleep(2500);
_getS();
const R={};
const reset=()=>{S.run._dlgStage={};S.run._dlgHeard={};};

/* 1. the brief's worked example: Ferrand, Grog alive vs Grog beaten */
reset(); S.run.bossesBeaten=[];
R.ferrand_grogAlive=_dlgSay('ferrand');
reset(); S.run.bossesBeaten=['grog'];
const seen=new Set();
for(let i=0;i<40;i++){reset();S.run.bossesBeaten=['grog'];seen.add(_dlgSay('ferrand'));}
R.ferrand_grogBeaten_all=[...seen];

/* 2. a patron with no personal pool falls through to ambient */
reset(); S.run.tier=0;
R.noPersonal_krox=_dlgSay('krox');

/* 3. a personal line beats ambient */
reset();
R.personal_wins_golgoth=_dlgSay('golgoth');

/* 4. stage floor, not exact match: Golgoth's stage-0 line still fires later */
reset(); S.run._dlgStage['golgoth']=7;
R.floorNotExact_golgoth=_dlgSay('golgoth');

/* 5. the King pool never repeats within a run - measured against the king
      pool ONLY, since falling through to the thin ambient pool is expected */
reset(); S.run.tier=0;
const kingTexts=new Set(PATRON_LINES.filter(r=>r.p==='reaction:king').map(r=>r.t));
const gossipTexts=new Set(PATRON_LINES.filter(r=>r.p==='gossip:town').map(r=>r.t));
const drawn=[];for(let i=0;i<20;i++)drawn.push(_dlgSay('krox'));
const kingHits=drawn.filter(t=>kingTexts.has(t));
R.kingPoolSize=kingTexts.size;
R.kingDrawn=kingHits.length;
R.kingDistinct=new Set(kingHits).size;
R.kingRepeatedWithinRun=kingHits.length!==new Set(kingHits).size;
R.fellThroughToGossip=drawn.some(t=>gossipTexts.has(t));

/* 6. night_gte(6) gates the late King line */
reset(); S.run.tier=0;
let early=false;for(let i=0;i<30;i++){reset();if((_dlgSay('krox')||'').indexOf('Season')===0)early=true;}
reset(); S.run.tier=5; /* night 6 */
let late=false;for(let i=0;i<40;i++){reset();S.run.tier=5;if((_dlgSay('krox')||'').indexOf('Season')===0)late=true;}
R.lateLine_beforeNight6=early; R.lateLine_atNight6=late;

/* 7. stage advances on every call */
reset(); _dlgSay('golgoth'); _dlgSay('golgoth');
R.stageAdvances=S.run._dlgStage['golgoth'];
return R;
