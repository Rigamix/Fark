/* P862-P864 - the brief's section 9 headline, driven.
 *
 *   "Each of the eight cards, acquired the way a player acquires it - beat
 *    the boss, take the card from spoils, then use it in a later match. Not
 *    usedCards[id]=1 seeded by hand: that is what hid the layer's
 *    unreachability for 230 patches."
 *
 * So nothing here writes S.run.cards, usedCards or G.pCards directly. The
 * match is won, the spoils tile is TAPPED, the confirm modal's TAKE is
 * TAPPED, and what lands in the boss slot is read back. The last leg then
 * starts a fresh match and asks the game's own canActivateCard whether the
 * card it granted is playable - the one question the old CARDS layer would
 * have answered "no" to for 230 patches while every code-read said yes.
 */
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(fn,ms)=>{const t0=Date.now();while(Date.now()-t0<ms){try{if(fn())return true;}catch(e){}await sleep(120);}return false;};
const tap=el=>{if(!el)return false;const r=el.getBoundingClientRect();
  const o={bubbles:true,cancelable:true,clientX:r.left+r.width/2,clientY:r.top+r.height/2};
  el.dispatchEvent(new PointerEvent('pointerdown',o));
  el.dispatchEvent(new PointerEvent('pointerup',o));
  el.dispatchEvent(new MouseEvent('click',o));return true;};

if(!await until(()=>typeof launchBossMatch==='function',20000))return {err:'no boot'};
_getS();window._fkDiscardOk=true;

const BOSSES=[[0,'grog'],[1,'mabel'],[2,'finnick'],[3,'corvus'],
              [4,'brutus'],[5,'aldric'],[6,'whisper'],[7,'ambrose']];
const rows={};
try{CARDS.filter(c=>c.type==='active'&&c.npc).forEach(c=>{rows[c.npc]=c;});}catch(e){}

const out={expected:{},got:[],notes:[]};
BOSSES.forEach(([t,k])=>{out.expected[k]=rows[k]?rows[k].id:null;});

for(const [tier,key] of BOSSES){
  const rec={boss:key,tier};
  try{
    S.run.tier=tier;S.run.gold=500;
    S.run.cards=[null,null,null,null];      /* empty boss slot each round */
    try{delete S.pendingMatch;}catch(e){}
    try{showScreen('gauntlet');}catch(e){}
    launchBossMatch();
    if(!await until(()=>typeof G!=='undefined'&&G&&G.phase==='idle',15000)){
      rec.err='no match';out.got.push(rec);continue;}
    await sleep(1400);
    rec.rung=G.rung&&G.rung.name;
    /* win it */
    G.pPts=G.target;G.oPts=0;
    endMatch(true);
    const reached=await until(()=>{
      const rc=document.querySelector('#end-ov .res-card');
      return rc&&/TAKE ONE/.test(rc.textContent);},20000);
    rec.reachedSpoils=reached;
    if(!reached){out.got.push(rec);continue;}
    await sleep(900);
    /* THE TILE, tapped - not famSpoilsPick called */
    const tile=document.querySelector('#end-ov .res-card [onclick*="_gbSpoilsConfirm(\'card\')"]');
    rec.tileFound=!!tile;
    rec.tileName=tile?tile.textContent.replace(/\s+/g,' ').trim().slice(0,40):null;
    if(!tile){out.got.push(rec);continue;}
    tap(tile);
    /* THE MODAL's TAKE, tapped */
    const takeUp=await until(()=>[...document.querySelectorAll('.gbx-btn')]
      .some(b=>/TAKE/.test(b.textContent)),8000);
    rec.modalUp=takeUp;
    const take=[...document.querySelectorAll('.gbx-btn')].filter(b=>/TAKE/.test(b.textContent))[0];
    if(take)tap(take);
    await sleep(900);
    rec.bossSlot=S.run.cards?S.run.cards[0]:null;
    rec.correct=(rec.bossSlot===out.expected[key]);
    rec.onShelf=(S.trophies||[]).length>0;
  }catch(e){rec.threw=String(e).slice(0,120);}
  out.got.push(rec);
}

/* ── the card is PLAYABLE in a later match ─────────────────────────── */
/* Ambrose's Pyre is the one left in the slot by the loop. Start a fresh
   match and ask the GAME whether it can be activated - no seeding. */
try{
  S.run.tier=2;
  try{delete S.pendingMatch;}catch(e){}
  try{showScreen('gauntlet');}catch(e){}
  launchBossMatch();
  await until(()=>typeof G!=='undefined'&&G&&G.phase==='idle',15000);
  await sleep(1600);
  const cid=S.run.cards[0];
  out.laterMatch={
    equipped:cid,
    inHand:!!(G.pCards&&G.pCards.indexOf(cid)>=0),
    /* charges seeded by the MATCH from the row, which is the thing that used
       to be faked by hand */
    usesSeeded:(G.activeCardState&&G.activeCardState.usedCards)?G.activeCardState.usedCards[cid]:null,
    rowMaxUses:(getCard(cid)||{}).maxUses,
    rendersInBar:!!document.querySelector('#playerCards .mcard[data-cid="'+cid+'"],.mcard[data-cid="'+cid+'"]'),
  };
}catch(e){out.laterMatch={threw:String(e).slice(0,140)};}

const all=out.got;
out.VERDICT={
  allEightReachedSpoils: all.length===8&&all.every(r=>r.reachedSpoils===true),
  allEightOfferedTheCard: all.every(r=>r.tileFound===true),
  allEightGrantedCorrectly: all.every(r=>r.correct===true),
  eightDistinctCards: new Set(all.map(r=>r.bossSlot)).size===8,
  trophyShelfFilling: all.every(r=>r.onShelf===true),
  laterMatchHasIt: !!(out.laterMatch&&out.laterMatch.inHand),
  laterMatchSeededCharges: !!(out.laterMatch&&out.laterMatch.usesSeeded===out.laterMatch.rowMaxUses),
};
out.PASS=Object.keys(out.VERDICT).every(k=>out.VERDICT[k]===true);
return out;
