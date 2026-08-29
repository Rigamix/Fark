const A=CARDS.filter(c=>c.type==='active');
const boss=A.filter(c=>c.npc);
return {
  activesNow:A.length,
  bossCards:boss.map(c=>({npc:c.npc,id:c.id,name:c.name,icon:c.icon,eff:c.eff,uses:c.maxUses,q:!!c.rewardQuote})),
  nonBossActives:A.filter(c=>!c.npc).map(c=>c.id),
  cardsTotal:CARDS.length,
  everyBossHasOne:['grog','mabel','finnick','corvus','brutus','aldric','whisper','ambrose']
    .filter(k=>!boss.some(c=>c.npc===k)),
  idCheck:_assertUniqueIds(),
};
