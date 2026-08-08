/* Does the reveal panel track the loadout, or freeze at open?
   Open First Strike, read the panel, remove a die through the central removal
   path, read it again. The panel renders two-letter die names, so a change in
   the loadout must show as a change in the panel's text. */
const sleep = ms => new Promise(r => setTimeout(r, ms));
const until = async (fn,ms)=>{const t0=Date.now();while(Date.now()-t0<ms){try{if(fn())return true;}catch(e){}await sleep(50);}return false;};
if (typeof _firstStrikeRender!=='function') return {error:'render fn missing'};
try{
  _getS(); S.run=S.run||{}; S.run.tier=2;
  S.run.dice=['bone','iron','flint','lead','amber','brass'];
  S.run.cards=S.run.cards||[]; S.settings=S.settings||{}; S.settings.reducedMotion=true;
  launchBossMatch();
}catch(e){return {error:'launch '+e.message};}
if(!(await until(()=>typeof G!=='undefined'&&G&&G.rung,9000))) return {error:'no match'};
await sleep(700);
G._firstStrikeOpen=true;
try{_firstStrikeRender();}catch(e){return {error:'render threw '+e.message};}
await sleep(200);
const box=document.getElementById('fsReveal');
const textAtOpen=box?box.textContent:null;
const diceAtOpen=(G.matchDice||[]).slice();
/* remove lane 2 through the central path */
let removed=null;
try{ removed=G.matchDice[2]; _removeDieAt(2,{permanent:true}); }catch(e){ return {error:'remove threw '+e.message}; }
await sleep(400);
const textAfter=box?box.textContent:null;
const diceAfter=(G.matchDice||[]).slice();
return {
  removedMaterial: removed,
  loadoutAtOpen: diceAtOpen, loadoutAfter: diceAfter,
  panelAtOpen: textAtOpen, panelAfter: textAfter,
  panelChanged: textAtOpen!==textAfter,
  loadoutChanged: diceAtOpen.length!==diceAfter.length,
  verdict: (diceAtOpen.length!==diceAfter.length && textAtOpen!==textAfter)
    ? 'PASS - panel tracked the loadout change'
    : (diceAtOpen.length===diceAfter.length ? 'VOID - the loadout never changed, nothing to track'
       : 'FAIL - loadout changed and the panel did not')
};
