/* Trade: the WHOLE die swaps for the MATCH only; both loadouts restore at end. */
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
const R={};
/* make the swap observable: distinct materials and a brand on our side */
S.run.dice=['obsidian','bone','bone','bone','bone','bone'];
S.run.dieEnch=[{t:'tithe',face:1},null,null,null,null,null];
G.matchDice=S.run.dice.slice();
G.matchOppDice=['jade','bone','bone','bone','bone','bone'];
try{G._enchArr=S.run.dieEnch.slice();}catch(e){}
const runBefore=(S.run.dice||[]).slice();
const enchBefore=JSON.stringify(S.run.dieEnch||[]);
const L=0;
R.before={mine:G.matchDice[L],theirs:G.matchOppDice[L]};
/* fire Trade on lane 0 through its own effect */
try{ENCH_ICONS.trade.fire({lane:L,side:'p'});}catch(e){R.fireErr=String(e);}
R.afterFire={mine:G.matchDice[L],theirs:G.matchOppDice[L]};
R.swapped=G.matchDice[L]===R.before.theirs;
R.wholeDieCrossed=G.matchDice[L]==='jade';
R.brandLeftWithIt=!(G._enchArr&&G._enchArr[L]&&G._enchArr[L].t==='tithe');
R.RUN_UNTOUCHED_DURING_MATCH=(S.run.dice||[]).join()===runBefore.join()
  && JSON.stringify(S.run.dieEnch||[])===enchBefore;
/* end the match and confirm both sides restore */
try{endMatch(true);}catch(e){R.endErr=String(e);}
await sleep(600);
_getS();
R.RUN_RESTORED_AFTER_MATCH=(S.run.dice||[]).join()===runBefore.join()
  && JSON.stringify(S.run.dieEnch||[])===enchBefore;
R.runNow=(S.run.dice||[]).slice(0,3);
R.runWas=runBefore.slice(0,3);
return R;
