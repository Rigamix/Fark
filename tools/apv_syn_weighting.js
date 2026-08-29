/* P870 - section 11.4's weighting checks, plus the one the SPLIT depends on.
 *
 * Three claims, and the third is the one that makes two measured runs worth
 * doing at all:
 *
 *  1. WEIGHTED, NOT FILTERED. A tagged card matching the boss must appear
 *     materially more often than an untagged one from the same pool, AND
 *     every pool member must still appear at least once. A card reaching zero
 *     across a large sample means the weighting became a filter.
 *  2. DEGRADES CLEANLY. A pool with no tags at all must draw the same with
 *     the flag on as with it off - that is what lets the pools be tagged one
 *     boss at a time.
 *  3. DARK WHILE OFF. With the flag false the distribution must be the one
 *     the game already had. Run one's ladder is the baseline for run two, so
 *     if this patch perturbs the draw even slightly while "off", the whole
 *     point of splitting them is gone. The caller compares this run's OFF
 *     numbers against a control built from the previous commit.
 */
if(typeof generateOppCards!=='function')return {err:'no generateOppCards'};
if(typeof NPC_SYN_WEIGHTING==='undefined')return {err:'flag missing - P870 did not land'};
_getS();

const N=4000;
const BOSSES=[[3,'CORVUS'],[6,'WHISPER'],[7,'AMBROSE'],[0,'GROG']];

function tally(rung,n){
  const c={};
  rung.cardPool.forEach(id=>{c[id]=0;});
  for(let i=0;i<n;i++){
    (generateOppCards(rung,0)||[]).forEach(id=>{c[id]=(c[id]||0)+1;});
  }
  const tot=Object.keys(c).reduce((a,k)=>a+c[k],0)||1;
  const f={};Object.keys(c).forEach(k=>{f[k]=+(c[k]/tot).toFixed(4);});
  return {counts:c,freq:f};
}
function isTagged(id){
  try{const d=getNpcCard(id)||getCard(id);return !!(d&&d.syn&&d.syn.length);}catch(e){return false;}
}

const out={flagDefault:NPC_SYN_WEIGHTING,N,bosses:{}};
const zeroed=[], tagLoses=[];

BOSSES.forEach(([tier,name])=>{
  const rung=TIERS[tier]&&TIERS[tier].boss; if(!rung)return;
  NPC_SYN_WEIGHTING=false; const off=tally(rung,N);
  NPC_SYN_WEIGHTING=true;  const on =tally(rung,N);
  NPC_SYN_WEIGHTING=false;

  const sig=rung.cardPool[0];
  const nonSig=rung.cardPool.filter(id=>id!==sig);
  const tagged=nonSig.filter(isTagged), untagged=nonSig.filter(id=>!isTagged(id));
  const avg=(arr,f)=>arr.length?arr.reduce((a,k)=>a+f[k],0)/arr.length:null;

  const rec={sig,tagged,untagged,
    offFreq:off.freq,onFreq:on.freq,
    avgTaggedOn:avg(tagged,on.freq),avgUntaggedOn:avg(untagged,on.freq),
    avgTaggedOff:avg(tagged,off.freq),avgUntaggedOff:avg(untagged,off.freq),
    everyMemberDrawnOn:rung.cardPool.every(id=>on.counts[id]>0),
    sigAlwaysOn:on.counts[sig]===N};
  rung.cardPool.forEach(id=>{if(on.counts[id]===0)zeroed.push(name+':'+id);});
  if(tagged.length&&untagged.length&&!(rec.avgTaggedOn>rec.avgUntaggedOn*1.2))
    tagLoses.push(name);
  out.bosses[name]=rec;
});

/* 2. an UNTAGGED pool must draw the same on and off */
let untaggedSame=null, untaggedDetail=null;
try{
  const plain={key:'plain',cardPool:['her_lucky_coin','one_more_round','grogs_bump','measure_twice','worn_thimble'],cardCount:3};
  /* strip the one tagged member so the pool is genuinely untagged */
  plain.cardPool=plain.cardPool.filter(id=>!isTagged(id));
  NPC_SYN_WEIGHTING=false; const a=tally(plain,N);
  NPC_SYN_WEIGHTING=true;  const b=tally(plain,N);
  NPC_SYN_WEIGHTING=false;
  let worst=0;
  plain.cardPool.forEach(id=>{worst=Math.max(worst,Math.abs(a.freq[id]-b.freq[id]));});
  untaggedSame=worst<0.03; untaggedDetail={pool:plain.cardPool,worstDelta:+worst.toFixed(4),off:a.freq,on:b.freq};
}catch(e){untaggedDetail={err:String(e).slice(0,90)};}

out.untaggedPool=untaggedDetail;
out.VERDICT={
  flagShipsOff:            out.flagDefault===false,
  neverAFilter_allDrawn:   zeroed.length===0,
  taggedBeatsUntagged:     tagLoses.length===0,
  signatureStillGuaranteed:Object.keys(out.bosses).every(k=>out.bosses[k].sigAlwaysOn),
  untaggedPoolUnaffected:  untaggedSame===true,
};
out.zeroedCards=zeroed; out.bossesWhereTagsDidNotWin=tagLoses;
out.PASS=Object.keys(out.VERDICT).every(k=>out.VERDICT[k]===true);
/* handed back so the caller can diff OFF against a pre-P870 control build */
out.offFreqForControlDiff={};
Object.keys(out.bosses).forEach(k=>{out.offFreqForControlDiff[k]=out.bosses[k].offFreq;});
return out;
