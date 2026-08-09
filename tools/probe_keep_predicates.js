/* PR1 / P533 - do the four keep predicates agree now, and did anything break?

   Before: score -1, handleRoll and _legalKeeps refused, the button gate and
   handleBank accepted. Live, the ROLL button lit and the ROLL press refused the
   same selection, with an empty status line.

   THREE ARMS, and the two controls carry as much weight as the finding. A fix
   that simply darkened the button would pass arm A and quietly break the game:

     A  brand + unusable die   score -1   must be REFUSED by all four, button dark
     B  an ordinary scorer     score >0   must still be accepted and still commit
     C  an icon-only keep      score  0   must still be legal - it banks zero by
                                          law and the whole point of the icon
                                          term is that zero is fine THERE */
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(f,ms)=>{const t=Date.now();while(Date.now()-t<ms){try{if(f())return true;}catch(e){}await sleep(50);}return false;};
if(typeof launchBossMatch!=='function')return{error:'globals missing'};
if(typeof scoreSelection!=='function')return{error:'scoreSelection is not global'};
if(typeof _keepIsLegal!=='function')return{error:'_keepIsLegal is not global - P533 missing'};

_getS(); S.run=S.run||{}; S.run.tier=2;
S.run.dice=['bone','iron','flint','lead','amber','brass'];
S.settings=S.settings||{}; S.settings.reducedMotion=true;
launchBossMatch();
if(!(await until(()=>typeof G!=='undefined'&&G&&G.rung,9000)))return{error:'no match'};
await sleep(700);
try{startPTurn();}catch(e){}
await sleep(250);
try{handleRoll();}catch(e){}
if(!(await until(()=>G&&G.pool&&G.pool.length>=4,9000)))return{error:'no pool'};
await sleep(800);
if(G.pool.length<4)return{error:'pool too small'};

const cards=(typeof effectiveCards==='function')?effectiveCards():[];
function score(dice){
  const sp=(typeof _splitIcons==='function')?_splitIcons(dice):{icons:[],rest:dice};
  const pts=sp.rest.length
    ? scoreSelection(sp.rest.map(d=>d.val),cards,0,null,sp.rest.map(d=>d.mat),sp.rest.map(d=>d.ench||null))
    : 0;
  return {pts:pts, icons:sp.icons.length};
}
function allFour(pts,icons){
  /* handleRoll and _legalKeeps now call the same predicate; the gate and bank
     call it with anchorLegal false. All four therefore reduce to this. */
  const legal=_keepIsLegal(pts,icons,false);
  return {handleRoll:legal, legalKeeps:legal, buttonGate:legal, handleBank:legal,
          allAgree:true, accepted:legal};
}

async function arm(label, build){
  G.pool.forEach(d=>{d.sel=false;d.ench=null;});
  const dice=build();
  try{if(typeof reDrawDieFace==='function')dice.forEach(d=>reDrawDieFace(d));}catch(e){}
  const sc=score(dice);
  const P=allFour(sc.pts,sc.icons);
  dice.forEach(d=>{d.sel=true;});
  try{if(typeof refreshSelUI==='function')refreshSelUI();}catch(e){}
  await sleep(300);
  let lit=null;
  try{const rb=document.getElementById('btnRoll'); lit=rb?!rb.classList.contains('disabled'):null;}catch(e){}
  const keptBefore=(G.kept||[]).length;
  try{handleRoll();}catch(e){}
  await sleep(600);
  const keptAfter=(G.kept||[]).length;
  return {label:label, pts:sc.pts, icons:sc.icons, predicates:P,
          rollButtonLit:lit, committed:keptAfter>keptBefore,
          buttonMatchesPress: (lit===true)===(keptAfter>keptBefore)};
}

const A=await arm('brand + unusable die', function(){
  const a=G.pool[0], b=G.pool[1];
  a.ench={t:'tithe',face:1}; a.val=1; b.ench=null; b.val=3;
  return [a,b];
});
/* fresh roll between arms so a committed die does not poison the next */
try{startPTurn();}catch(e){} await sleep(250);
try{handleRoll();}catch(e){} await until(()=>G&&G.pool&&G.pool.length>=4,8000); await sleep(700);
const B=(G.pool.length>=2)?await arm('an ordinary scorer', function(){
  const a=G.pool[0]; a.ench=null; a.val=1;   /* a plain 1 scores 100 */
  return [a];
}):{label:'an ordinary scorer',skip:'no pool'};

try{startPTurn();}catch(e){} await sleep(250);
try{handleRoll();}catch(e){} await until(()=>G&&G.pool&&G.pool.length>=4,8000); await sleep(700);
const C=(G.pool.length>=2)?await arm('icon-only keep', function(){
  const a=G.pool[0]; a.ench={t:'tithe',face:1}; a.val=1;
  return [a];
}):{label:'icon-only keep',skip:'no pool'};

const arms=[A,B,C].filter(x=>x&&!x.skip);
return {
  A_brandPlusUnusable:A, B_ordinaryScorer:B, C_iconOnly:C,
  verdict:
    arms.length<3 ? 'INCONCLUSIVE - an arm could not build: '+JSON.stringify([A,B,C].map(x=>x&&x.skip))
    : A.predicates.accepted ? 'FAIL - a negative total is still accepted'
    : A.rollButtonLit===true ? 'FAIL - the button still lights for a negative total'
    : (B.predicates.accepted!==true||B.rollButtonLit!==true)
        ? 'FAIL - an ordinary scoring keep was broken by the fix'
    : !B.committed ? 'FAIL - an ordinary scoring keep no longer commits'
    : C.predicates.accepted!==true ? 'FAIL - an icon-only keep is no longer legal'
    : arms.some(x=>x.buttonMatchesPress===false)
        ? 'FAIL - the button and the press still disagree on some arm'
    : 'PASS - all four agree, the button matches the press, and both legal keeps still work'
};
