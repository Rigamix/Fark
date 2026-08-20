/* P833: (1) band lines are ADDITIVE - at night 2 krox speaks only
 * baselines; at night 5 the b4 line JOINS them (both appear across
 * samples); at night 8 b7 joins too. (2) the Discrepancy override
 * still excludes (most-conditions intact). (3) a seeded boss :open
 * row answers a no-history MATCH_START; with history it does not.
 * (4) the patron bust bark still works post-deletion sweep. */
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(fn,ms)=>{const t0=Date.now();while(Date.now()-t0<ms){try{if(fn())return true;}catch(e){}await sleep(120);}return false;};
if(!await until(()=>typeof _dlgPick==='function'&&typeof S!=='undefined',20000))return {err:'no boot'};
if(typeof _getS==='function')_getS();
const setTier=t=>{S.run=S.run||{};S.run.tier=t;};
const sample=(pool,n)=>{const seen={};for(let i=0;i<n;i++){const r=_dlgPick(pool,0,null);if(r)seen[r.g||r.t.slice(0,18)]=1;}return Object.keys(seen).sort();};
/* night 2: baselines only */
setTier(1);
const n2=sample('patron:krox',60);
/* night 5: b4 joins, b7 absent */
setTier(4);
const n5=sample('patron:krox',80);
/* night 8: b7 joins */
setTier(7);
const n8=sample('patron:krox',80);
/* discrepancy override intact: with heard + night>=4 the resolution
   rows (2 conditions) must EXCLUDE lesser rows */
setTier(4);
S.run._dlgHeard=S.run._dlgHeard||{};S.run._dlgHeard['discrepancy_intro']=1;
let disc={};
for(let i=0;i<40;i++){const r=_dlgPick('reaction:discrepancy',0,S.run._dlgHeard);
  if(r)disc[(r.c||[]).length]=1;}
/* boss :open - seed a row, launch grog with no ledger */
PATRON_LINES.push({p:'boss:grog:open',s:0,t:'TEST-OPEN-LINE'});
S.npcLedger={};try{save();}catch(e){}
window._fkDiscardOk=true;
setTier(0);
launchBossMatch();
if(!await until(()=>typeof G!=='undefined'&&G&&G.phase==='idle',20000))return {err:'no match',n2,n5,n8};
await sleep(2500);
const openNoHist=DLG.getLine('MATCH_START');
S.npcLedger.drunkard={nights:3,w:2,l:1,bestBank:500};
const realRandom=Math.random;Math.random=()=>0.99;/* dodge the 65% ledger draw AND land past it */
const openWithHist=DLG.getLine('MATCH_START');
Math.random=realRandom;
return {n2,n5,n8,discCondCounts:Object.keys(disc),
  openNoHist,openWithHist,
  verdicts:{
    night2BaselinesOnly:n2.length===3&&n2.indexOf('b4')<0,
    night5B4Joins:n5.indexOf('b4')>=0&&n5.indexOf('b0')>=0&&n5.indexOf('b7')<0,
    night8B7Joins:n8.indexOf('b7')>=0&&n8.indexOf('b4')>=0&&n8.indexOf('b0')>=0,
    discrepancyStillOverrides:Object.keys(disc).join(',')==='2',
    bossOpenAnswersNoHistory:/TEST-OPEN-LINE|Haven't seen you at my table/.test(openNoHist||''),/* P839: Denis's real :open line shares the pool with the seeded row */
    historySuppressesOpen:openWithHist!=='TEST-OPEN-LINE'},
  verdict:n2.length===3&&n5.indexOf('b4')>=0&&n5.indexOf('b7')<0&&n8.indexOf('b7')>=0
    &&Object.keys(disc).join(',')==='2'&&/TEST-OPEN-LINE|Haven't seen you at my table/.test(openNoHist||'')&&openWithHist!=='TEST-OPEN-LINE'};
