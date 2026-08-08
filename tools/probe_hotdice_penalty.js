/* Does hot dice still refund Whisper's Hex?
   Arm the Hex, reach a rolled pool, commit every die so the hot-dice branch in
   handleRoll fires, then read numDice. Two arms: with the Hex and without, so
   the no-penalty case is proven unchanged rather than assumed. */
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(f,ms)=>{const t=Date.now();while(Date.now()-t<ms){try{if(f())return true;}catch(e){}await sleep(50);}return false;};
if(typeof launchBossMatch!=='function')return{error:'globals missing'};
async function run(armHex){
  try{
    _getS(); S.run=S.run||{}; S.run.tier=2;
    S.run.dice=['bone','iron','flint','lead','amber','brass'];
    S.run.cards=S.run.cards||[]; S.settings=S.settings||{}; S.settings.reducedMotion=true;
    launchBossMatch();
  }catch(e){return{error:'launch '+e.message};}
  if(!(await until(()=>typeof G!=='undefined'&&G&&G.rung,9000)))return{error:'no match'};
  await sleep(600);
  if(armHex)G._npcHexArmed=true;
  try{if(typeof startPTurn==='function')startPTurn();}catch(e){}
  await sleep(250);
  const afterStart=G.numDice;
  try{if(typeof handleRoll==='function')handleRoll();}catch(e){}
  if(!(await until(()=>G&&G.pool&&G.pool.length>0,9000)))return{error:'no pool'};
  await sleep(500);
  const rolled=G.pool.length;
  /* commit every die so the next handleRoll takes the hot-dice branch */
  G.pool.forEach(function(d){d.committed=true;});
  try{if(typeof handleRoll==='function')handleRoll();}catch(e){}
  await sleep(900);
  return {armHex:armHex, loadout:(G.matchDice||[]).length,
          numDiceAfterStart:afterStart, diceRolled:rolled,
          numDiceAfterHotDice:G.numDice};
}
const withHex=await run(true);
await sleep(600);
const noHex=await run(false);
return {
  WITH_HEX:withHex, NO_HEX:noHex,
  verdict:(withHex.numDiceAfterHotDice===withHex.numDiceAfterStart
           && noHex.numDiceAfterHotDice===noHex.loadout)
    ? 'PASS - hot dice kept the Hex, and is unchanged without it'
    : 'FAIL - see numbers'
};
