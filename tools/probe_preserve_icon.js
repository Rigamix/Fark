/* M5 - can Preserve bank a face that is worth zero by law?

   A branded face banks nothing - _splitIcons exists to hold those dice out of
   scoring, and brands sit on faces 1 and 5, which are exactly the faces
   Preserve looks for. Preserve's gate reads k.vals (icons already split out)
   and its picker reads k.dice (icons still in). So the gate can pass on a real
   5 in one kept row while the picker takes an icon 1 from another.

   TWO CHECKS, because the constructed one alone would not prove the link:

     A  does a REAL commit put a branded die into k.dice? That is the load-
        bearing fact - without it the arrangement below cannot occur in play.
     B  given that arrangement, which die does Preserve take, and for how much?

   Also recorded: whether k.dice carries any way to TELL an icon die from a
   plain one. If it does not, no consumer can filter them and the fix has to
   change the record, not the reader. */
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(f,ms)=>{const t=Date.now();while(Date.now()-t<ms){try{if(f())return true;}catch(e){}await sleep(50);}return false;};
if(typeof launchBossMatch!=='function')return{error:'globals missing'};
if(!(window.CFX&&CFX.preserve))return{error:'CFX.preserve missing'};

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

/* ---- A: does a real commit put a branded die into k.dice? -------------- */
G.kept=[];
const a=G.pool[0],b=G.pool[1],c=G.pool[2],brand=G.pool[3];
a.ench=null;a.val=3; b.ench=null;b.val=3; c.ench=null;c.val=3;
brand.ench={t:'tithe',face:1}; brand.val=1; brand.mat='flint';
try{[a,b,c,brand].forEach(d=>reDrawDieFace(d));}catch(e){}
G.pool.forEach(d=>{d.sel=false;});
[a,b,c,brand].forEach(d=>{d.sel=true;});
try{refreshSelUI();}catch(e){}
await sleep(250);
try{handleRoll();}catch(e){}
await sleep(700);
const row=(G.kept||[])[0]||null;
const A={
  keptRows:(G.kept||[]).length,
  vals:row?row.vals:null,
  dice:row?row.dice:null,
  pts:row?row.pts:null,
  brandedFaceIsInDice: !!(row&&(row.dice||[]).some(dd=>dd&&dd.val===1&&dd.mat==='flint')),
  brandedFaceIsInVals: !!(row&&(row.vals||[]).some(v=>v===1)),
  diceEntriesCarryAnyBrandInfo: !!(row&&(row.dice||[]).some(dd=>dd&&(dd.ench!==undefined||dd.icon!==undefined)))
};

/* ---- B: the arrangement, and what Preserve takes -----------------------
   Rows now carry `ench` exactly as a real commit writes them - arm A proves
   that shape - so the branded entry is distinguishable and the plain ones are
   not accidentally excluded. */
G.kept=[
  {vals:[3,3,3],mat:'bone',pts:300,
   dice:[{val:3,mat:'bone',ench:null},{val:3,mat:'iron',ench:null},
         {val:3,mat:'lead',ench:null},{val:1,mat:'flint',ench:{t:'tithe',face:1}}]},
  {vals:[5],mat:'amber',pts:50,dice:[{val:5,mat:'amber',ench:null}]}
];
G._famPreserve=null;
const gatePasses=!!CFX.preserve.canUse();
const used=CFX.preserve.use({tier:1});
const P=G._famPreserve||{};
const B={
  gatePasses:gatePasses, used:used,
  preservedVal:P.val, preservedMat:P.mat, preservedPts:P.pts,
  tookTheIconFace: P.val===1&&P.mat==='flint',
  tookTheLegalFace: P.val===5&&P.mat==='amber',
  theOnlyLegalFaceWas:'the 5 on amber, worth 50'
};

/* ---- C: THE CONTROL. A plain 1 must STILL be preservable, or the fix has
   simply stopped Preserve working. Same row shape, no brand on the 1. ---- */
G.kept=[
  {vals:[1,3,3],mat:'bone',pts:100,
   dice:[{val:1,mat:'lead',ench:null},{val:3,mat:'iron',ench:null},{val:3,mat:'bone',ench:null}]}
];
G._famPreserve=null;
const cUsed=CFX.preserve.use({tier:1});
const CP=G._famPreserve||{};
const C={used:cUsed, val:CP.val, mat:CP.mat, pts:CP.pts,
         plainOneStillWorks: CP.val===1&&CP.mat==='lead'&&CP.pts===100};

return {
  A_realCommit:A, B_whatPreserveTakes:B, C_plainControl:C,
  verdict:
    !A.brandedFaceIsInDice ? 'NOT REPRODUCED - a real commit did not put the branded die into k.dice'
    : A.brandedFaceIsInVals ? 'UNEXPECTED - the branded face reached k.vals too; the split is not doing what is claimed'
    : B.tookTheIconFace
        ? 'STILL BROKEN - Preserve banked a branded face worth ZERO as '+B.preservedPts
    : !C.plainOneStillWorks
        ? 'FAIL - the fix broke ordinary Preserve: took '+C.val+' on '+C.mat+' for '+C.pts
    : B.tookTheLegalFace
        ? 'FIXED - Preserve skipped the branded face and took the legal 5, and a plain 1 still works'
    : 'UNEXPECTED - Preserve took '+B.preservedVal+' on '+B.preservedMat
};
