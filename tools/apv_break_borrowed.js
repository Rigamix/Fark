/* A BORROWED DIE IS AN ILLEGAL BREAK TARGET - and natural death is untouched.
 * The ruling reverses section 4b: deliberate Break can no longer take a die
 * that is on loan via Fair Trade, "same shape as a Preserved die being
 * illegal". Passive shatter of that same die is explicitly UNCHANGED, so this
 * checks both halves - a fix that also broke natural death would be worse than
 * the exploit. */
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
const pc=[...document.querySelectorAll('.ptcard')].filter(vis)[0];if(pc){tap(pc);await sleep(1700);}
const sit=[...document.querySelectorAll('span,div,button')].filter(e=>vis(e)&&e.children.length<=1&&/^SIT\s*DOWN$/i.test((e.textContent||'').trim()))[0];
if(sit){tap(sit);if(sit.parentElement)tap(sit.parentElement);}
await until(()=>vis(document.getElementById('screen-match')),9000);
await until(()=>typeof G!=='undefined'&&G&&G.phase==='idle',14000);
tap(document.getElementById('btnRoll'));
await until(()=>G.phase==='choosing',12000);
await sleep(500);

const out={};
G.target=999999;

/* ── 1. the guard itself, unit-level ── */
const free=G.pool.filter(d=>!d.committed);
out.poolSize=free.length;
if(free.length<3)return {err:'not enough free dice',pool:free.length};

const victim=free[1], lane=_laneOf(victim);
out.lane=lane;
out.beforeLoan=_breakBorrowed(victim);          /* expect false - no loan yet */

/* stage a Fair Trade loan on that lane, exactly as CFX.fair_trade writes it */
const homeMat=G.matchDice[lane];
G._fairTrade={lane:lane, was:homeMat, borrowed:'obsidian'};
G.matchDice[lane]='obsidian';
victim.mat='obsidian';
out.duringLoan=_breakBorrowed(victim);          /* expect TRUE */

/* ── 2. Break's target list must not offer it ── */
const src=free[0];
const legal=G.pool.filter(d=>!d.committed&&d!==src&&!_breakPreserved(d)&&!_breakBorrowed(d));
out.borrowedOffered=legal.indexOf(victim)>=0;   /* expect FALSE */
out.legalCount=legal.length;
out.freeMinusSrc=G.pool.filter(d=>!d.committed&&d!==src).length;

/* ── 3. and the tap path refuses it too, not just the list ── */
let refused=false;
const realLog=window.famLog;
window.famLog=function(m){ if(/ON LOAN/i.test(String(m)))refused=true; return realLog.apply(this,arguments); };
try{ _breakBegin(src); _breakDie(victim); }catch(e){ out.tapErr=String(e); }
window.famLog=realLog;
out.tapRefused=refused;
out.stillSixDice=(G.matchDice||[]).length;      /* expect unchanged */

/* ── 4. NATURAL DEATH IS UNCHANGED - the half a bad fix would break ── */
const before={matchDice:(G.matchDice||[]).slice(), numDice:G.numDice, ft:JSON.parse(JSON.stringify(G._fairTrade||null))};
try{ _removeDieAt(lane,{permanent:false}); }catch(e){ out.shatterErr=String(e); }
out.afterShatter={matchDice:(G.matchDice||[]).slice(), numDice:G.numDice,
                  ft:G._fairTrade?JSON.parse(JSON.stringify(G._fairTrade)):null};
out.lenderReturned=out.afterShatter.matchDice[lane]===homeMat;

out.verdict={
  guardOffWithoutLoan: out.beforeLoan===false,
  guardOnDuringLoan:   out.duringLoan===true,
  notOfferedToBreak:   out.borrowedOffered===false,
  tapRefused:          out.tapRefused===true,
  breakTookNothing:    out.stillSixDice===before.matchDice.length,
  naturalDeathWorks:   out.lenderReturned===true
};
return out;
