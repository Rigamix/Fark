/* P842: (1) the ghost character no longer composites (visibility
 * hidden after the fade, both tab directions); (2) no per-layer
 * filters remain in the focus states - the scrims carry the recede
 * via backdrop-filter; (3) screenshot lands on the st-epick state for
 * the eyeball. */
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(fn,ms)=>{const t0=Date.now();while(Date.now()-t0<ms){try{if(fn())return true;}catch(e){}await sleep(120);}return false;};
if(!await until(()=>typeof showScreen==='function'&&typeof S!=='undefined',20000))return {err:'no boot'};
if(typeof _getS==='function')_getS();
S.run.gold=2000;try{save();}catch(e){}
showScreen('shop');
await sleep(2200);
const shop=document.getElementById('gbShop');
if(!shop)return {err:'no shop el'};
const vis=id=>{const e=document.getElementById(id);if(!e)return null;
  const cs=getComputedStyle(e);return {op:cs.opacity,vis:cs.visibility,filter:cs.filter};};
/* dice tab: stCharE must be visibility:hidden */
const diceTab={stChar:vis('stChar'),stCharE:vis('stCharE')};
/* switch to ench: after the fade stChar must hide */
try{const h2=[...document.querySelectorAll('*')].find(e=>e._setTab);if(h2)h2._setTab('ench');}catch(e){}
await sleep(900);
const enchTab={stChar:vis('stChar'),stCharE:vis('stCharE')};
/* focus states: the classes are the mechanism - drive them and read
   the computed results */
shop.classList.add('st-focus');
await sleep(600);
const focusState={
  scrimA:(()=>{const e=document.getElementById('stScrimA');if(!e)return null;
    const cs=getComputedStyle(e);return {op:cs.opacity,bf:cs.backdropFilter||cs.webkitBackdropFilter};})(),
  layerFilter:vis('stMid').filter};
shop.classList.remove('st-focus');
shop.classList.add('st-epick');
await sleep(600);
const epickState={
  scrimB:(()=>{const e=document.getElementById('stScrimB');if(!e)return null;
    const cs=getComputedStyle(e);return {op:cs.opacity,bf:cs.backdropFilter||cs.webkitBackdropFilter};})(),
  layerFilter:vis('stMid').filter};
/* leave st-epick ON for the screenshot */
return {diceTab,enchTab,focusState,epickState,
  verdicts:{
    ghostHiddenOnDiceTab:diceTab.stCharE&&diceTab.stCharE.vis==='hidden',
    ghostHiddenOnEnchTab:enchTab.stChar&&enchTab.stChar.vis==='hidden',
    activeCharVisible:enchTab.stCharE&&enchTab.stCharE.vis==='visible'&&enchTab.stCharE.op==='1',
    scrimACarriesTheBlur:!!(focusState.scrimA&&focusState.scrimA.op==='1'&&/blur/.test(focusState.scrimA.bf||'')),
    scrimBCarriesTheBlur:!!(epickState.scrimB&&epickState.scrimB.op==='1'&&/blur/.test(epickState.scrimB.bf||'')),
    noPerLayerFilters:focusState.layerFilter==='none'&&epickState.layerFilter==='none'},
  verdict:diceTab.stCharE.vis==='hidden'&&enchTab.stChar.vis==='hidden'
    &&/blur/.test((focusState.scrimA||{}).bf||'')&&/blur/.test((epickState.scrimB||{}).bf||'')
    &&focusState.layerFilter==='none'&&epickState.layerFilter==='none'};
