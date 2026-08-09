/* P533 arm: icononly - ONE arm per browser session (the S6 lesson).

   COMMIT IS MEASURED ON THE DICE, NOT THE KEPT TRAY. An icon-only keep is
   legal and banks zero, and 25117 only pushes to G.kept when pts>0 or the
   post-split score list is non-empty - so the tray never grows for it and
   tray-growth cannot tell "accepted" from "refused". The dice themselves
   becoming committed is the signal that survives both cases. */
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(f,ms)=>{const t=Date.now();while(Date.now()-t<ms){try{if(f())return true;}catch(e){}await sleep(50);}return false;};
if(typeof _keepIsLegal!=='function')return{error:'_keepIsLegal missing - P533 not applied'};
_getS(); S.run=S.run||{}; S.run.tier=2;
S.run.dice=['bone','iron','flint','lead','amber','brass'];
S.settings=S.settings||{}; S.settings.reducedMotion=true;
launchBossMatch();
if(!(await until(()=>typeof G!=='undefined'&&G&&G.rung,9000)))return{error:'no match'};
await sleep(700);
try{startPTurn();}catch(e){}
await sleep(250);
try{handleRoll();}catch(e){}
if(!(await until(()=>G&&G.pool&&G.pool.length>=2,9000)))return{error:'no pool'};
await sleep(800);
if(G.pool.length<2)return{error:'pool too small'};
G.pool.forEach(d=>{d.sel=false;d.ench=null;});
const a=G.pool[0];a.ench={t:'tithe',face:1};a.val=1;const dice=[a];
try{dice.forEach(d=>reDrawDieFace(d));}catch(e){}
const cards=(typeof effectiveCards==='function')?effectiveCards():[];
const sp=_splitIcons(dice);
const pts=sp.rest.length?scoreSelection(sp.rest.map(d=>d.val),cards,0,null,sp.rest.map(d=>d.mat),sp.rest.map(d=>d.ench||null)):0;
const accepted=_keepIsLegal(pts,sp.icons.length,false);
dice.forEach(d=>{d.sel=true;});
try{refreshSelUI();}catch(e){}
await sleep(300);
let lit=null;
try{const rb=document.getElementById('btnRoll');lit=rb?!rb.classList.contains('disabled'):null;}catch(e){}
try{handleRoll();}catch(e){}
await sleep(700);
const committedNow=dice.every(d=>!!d.committed);
return {arm:'icononly', pts:pts, icons:sp.icons.length, predicateAccepts:accepted,
        expectedAccept:true, rollButtonLit:lit, diceCommitted:committedNow,
        buttonMatchesPress:(lit===true)===committedNow,
        ok:(accepted===true)&&(lit===true)&&(committedNow===true)};
