/* Ruling #32: Kindred's doubling, one shape per enchant. */
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(fn,ms)=>{const t0=Date.now();while(Date.now()-t0<ms){try{if(fn())return true;}catch(e){}await sleep(60);}return false;};
const vis=el=>{if(!el||!el.isConnected)return false;const s=getComputedStyle(el),r=el.getBoundingClientRect();
 return s.display!=='none'&&s.visibility!=='hidden'&&+s.opacity>0.05&&r.width>1&&r.height>1;};
const tap=el=>{if(!vis(el))return false;const r=el.getBoundingClientRect();
 const o={bubbles:true,cancelable:true,clientX:r.left+r.width/2,clientY:r.top+r.height/2};
 el.dispatchEvent(new PointerEvent('pointerdown',o));el.dispatchEvent(new PointerEvent('pointerup',o));
 el.dispatchEvent(new MouseEvent('click',o));return true;};
tap(document.getElementById('hsBtnBottom'));await sleep(1800);
await until(()=>{const d=document.querySelector('.nrdie');return d&&d._floatDone;},9000);
tap(document.querySelector('.nrdie'));await sleep(1300);
tap(document.getElementById('nrTakeBtn'));await sleep(1900);
const p=[...document.querySelectorAll('.ptcard')].filter(vis)[0];if(p){tap(p);await sleep(1700);}
const sit=[...document.querySelectorAll('span,div,button')].filter(e=>vis(e)&&e.children.length<=1&&/^SIT\s*DOWN$/i.test((e.textContent||'').trim()))[0];
if(sit){tap(sit);if(sit.parentElement)tap(sit.parentElement);}
await until(()=>vis(document.getElementById('screen-match')),9000);
await until(()=>typeof G!=='undefined'&&G&&G.phase==='idle',14000);
_getS();
const R={};
/* the whitelist itself */
R.whitelist={};
['tithe','ward','snare','break','trade','snuff','fog','quicksilver'].forEach(k=>{
  R.whitelist[k]=!!(ENCH_ICONS[k]&&ENCH_ICONS[k].doubles);});
/* Kindred needs 2+ worked dice in the LOADOUT and the badge active */
S.run.dieEnch=[{t:'ward',face:1},{t:'snare',face:5},null,null,null,null];
G._sealRule='counterfeit';G._tell={id:'drill_order'};
R.kindredActive=_kindredActive();
/* WARD: two-thirds, not half, and not a second arming */
G._wardArmed=false;
ENCH_ICONS.ward.fire({lane:0,side:'p',mult:2});
R.ward_boostStamped=!!G._wardBoost;
G._wardArmed=false;
ENCH_ICONS.ward.fire({lane:0,side:'p',mult:1});
R.ward_noBoostWhenPlain=!G._wardBoost;
/* SNARE: halves twice on the same shot */
ENCH_ICONS.snare.fire({lane:2,side:'p',mult:2});
R.snare_x2=!!(G._snare&&G._snare.x2);
ENCH_ICONS.snare.fire({lane:2,side:'p',mult:1});
R.snare_plain=!(G._snare&&G._snare.x2);
/* SNUFF + FOG: two opponent turns, not two lanes */
ENCH_ICONS.snuff.fire({lane:3,side:'p',mult:2});
R.snuff_turns=G._snuff&&G._snuff.turns;
R.snuff_oneLaneOnly=G._snuff&&typeof G._snuff.lane==='number';
ENCH_ICONS.fog.fire({lane:4,side:'p',mult:2});
R.fog_turns=G._fog&&G._fog.turns;
ENCH_ICONS.snuff.fire({lane:3,side:'p',mult:1});
R.snuff_plainTurns=G._snuff&&G._snuff.turns;
return R;
