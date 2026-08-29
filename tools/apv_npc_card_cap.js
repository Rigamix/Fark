/* P868 + P869 - section 11.4's first two checks, driven.
 *
 * "The cap, driven at player card counts 0 through 4, for all eight bosses
 *  plus a patron. Reading the data proves nothing here - the Math.max lift is
 *  the half that is not in the data."
 *
 * That is exactly right and it is why this calls generateOppCards itself at
 * every hand size rather than inspecting cardCount. Before P868 the rows said
 * 2/3/3/3/3/4/4/5 and the function returned up to FOUR for every one of them
 * whenever the player held a full hand.
 *
 * THE CONTROL: a cap check passes trivially if the function returns nothing.
 * So every boss must also be shown to draw a NON-EMPTY hand, and the
 * signature must still be present - "never more than three" and "never any"
 * are the same number to an assert that only looks at the ceiling.
 */
if(typeof generateOppCards!=='function')return {err:'no generateOppCards'};
_getS();
const BOSSES=[[0,'GROG'],[1,'MABEL'],[2,'FINNICK'],[3,'CORVUS'],
              [4,'BRUTUS'],[5,'ALDRIC'],[6,'WHISPER'],[7,'AMBROSE']];
const N=200;
const rows=[];
let worst=0, everEmpty=[], sigMisses=[];

BOSSES.forEach(([tier,name])=>{
  const tierRow=TIERS[tier]; const rung=tierRow&&tierRow.boss;
  if(!rung){rows.push({boss:name,err:'no rung'});return;}
  const rec={boss:name,rungCardCount:rung.cardCount,poolSize:rung.cardPool.length,
             sig:rung.cardPool[0],byHandSize:{},maxSeen:0,minSeen:99,sigAlways:true};
  for(let hand=0;hand<=4;hand++){
    let mx=0,mn=99,sigHits=0;
    for(let i=0;i<N;i++){
      const got=generateOppCards(rung,hand)||[];
      mx=Math.max(mx,got.length); mn=Math.min(mn,got.length);
      if(got.indexOf(rung.cardPool[0])>=0)sigHits++;
    }
    rec.byHandSize[hand]={max:mx,min:mn,sigRate:+(sigHits/N).toFixed(2)};
    rec.maxSeen=Math.max(rec.maxSeen,mx); rec.minSeen=Math.min(rec.minSeen,mn);
    if(sigHits<N)rec.sigAlways=false;
  }
  worst=Math.max(worst,rec.maxSeen);
  if(rec.minSeen===0)everEmpty.push(name);
  if(!rec.sigAlways)sigMisses.push(name);
  rows.push(rec);
});

/* a patron: no signature guarantee, and P507 gives them zero cards */
let patron=null;
try{
  const p={key:'patron',cardPool:['quick_hands','the_skim','beginners_luck'],cardCount:3};
  let mx=0;
  for(let hand=0;hand<=4;hand++)for(let i=0;i<N;i++)
    mx=Math.max(mx,(generateOppCards(p,hand)||[]).length);
  patron={syntheticPatronMax:mx};
}catch(e){patron={err:String(e).slice(0,80)};}

/* the two new signatures */
const sigNow={
  whisper:(TIERS[6].boss||{}).cardPool[0],
  ambrose:(TIERS[7].boss||{}).cardPool[0],
};
const startBonusStillDrawable={
  the_royal_purse:(TIERS[6].boss||{}).cardPool.indexOf('the_royal_purse')>=0,
  communion_wine:(TIERS[7].boss||{}).cardPool.indexOf('communion_wine')>=0,
};

return {
  capConstant:(typeof NPC_CARD_CAP!=='undefined')?NPC_CARD_CAP:null,
  rows, patron, sigNow, startBonusStillDrawable,
  worstHandSeen:worst,
  bossesThatEverDrewNothing:everEmpty,
  bossesWhoseSignatureWasMissed:sigMisses,
  VERDICT:{
    /* the control first: the instrument saw real hands */
    everyBossDrewAHand: everEmpty.length===0,
    signatureStillGuaranteed: sigMisses.length===0,
    /* the claim */
    neverMoreThanThree: worst<=3,
    patronNeverMoreThanThree: !!(patron&&patron.syntheticPatronMax<=3),
    /* section 11.2 */
    whisperSignatureIsSeizure: sigNow.whisper==='royal_seizure',
    ambroseSignatureIsConfiscation: sigNow.ambrose==='blessed_confiscation',
    startBonusesKeptInPool: startBonusStillDrawable.the_royal_purse&&startBonusStillDrawable.communion_wine,
  },
};
