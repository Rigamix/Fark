/* win/loss reactions: outcome from the SPEAKER's side, boss counters separate */
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
const R={seat:window._lastSeatArt};
const P=(id,o)=>new Set(PATRON_LINES.filter(r=>r.p==='patron:'+id+':'+o).map(r=>r.t));
/* patron, both outcomes, from the speaker's side */
const art=String(window._lastSeatArt||'').toLowerCase();
R.playerWon_speakerSaysLoss=P(art,'loss').has(_dlgOutcome(true));
R.playerLost_speakerSaysWin=P(art,'win').has(_dlgOutcome(false));
/* boss: two independent counters */
G._isBoss=true; G.rung={key:'grog',name:'GROG'};
S.run._dlgWL={};
const B=(o,st)=>new Set(PATRON_LINES.filter(r=>r.p==='boss:grog:'+o&&r.s===st).map(r=>r.t));
const first=_dlgOutcome(false);                 /* grog beats you, first time */
R.boss_firstLoss_stage0=B('win',0).has(first);
const second=_dlgOutcome(false);                /* again */
R.boss_secondLoss_stage1=B('win',1).has(second);
R.counterAfterTwoLosses=S.run._dlgWL['grog:win'];
/* beating him must NOT have advanced by the above */
const beat=_dlgOutcome(true);
R.boss_firstBeat_stage0=B('loss',0).has(beat);
R.countersAreIndependent=S.run._dlgWL['grog:loss']===1&&S.run._dlgWL['grog:win']===1;
G._isBoss=false;G.rung=null;
return R;
