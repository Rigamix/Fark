/* Did the P697b CSS parse, and what does the scrim/panel compute? SUITE: exclude */
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(fn,ms)=>{const t0=Date.now();while(Date.now()-t0<ms){try{if(fn())return true;}catch(e){}await sleep(60);}return false;};
const vis=el=>{if(!el||!el.isConnected)return false;const s=getComputedStyle(el),r=el.getBoundingClientRect();
 return s.display!=='none'&&s.visibility!=='hidden'&&+s.opacity>0.05&&r.width>1&&r.height>1;};
const tap=el=>{if(!vis(el))return false;const r=el.getBoundingClientRect();
 const o={bubbles:true,cancelable:true,clientX:r.left+r.width/2,clientY:r.top+r.height/2};
 el.dispatchEvent(new PointerEvent('pointerdown',o));el.dispatchEvent(new PointerEvent('pointerup',o));
 el.dispatchEvent(new MouseEvent('click',o));return true;};
/* count matching cssRules across sheets */
const ruleScan=(needle)=>{let hits=[];try{for(const sh of document.styleSheets){let rules;try{rules=sh.cssRules;}catch(e){continue;}
 for(const r of rules){if(r.selectorText&&r.selectorText.indexOf(needle)>=0)hits.push(r.selectorText.slice(0,80));}}}catch(e){}return hits;};

tap(document.getElementById('hsBtnBottom'));await sleep(1800);
await until(()=>{const d=document.querySelector('.nrdie');return d&&d._floatDone;},9000);
tap(document.querySelector('.nrdie'));await sleep(1300);
tap(document.getElementById('nrTakeBtn'));await sleep(2200);
const pc=[...document.querySelectorAll('.ptcard')].filter(vis)[0];if(pc){tap(pc);await sleep(1700);}
const sit=[...document.querySelectorAll('span,div,button')].filter(e=>vis(e)&&e.children.length<=1&&/^SIT\s*DOWN$/i.test((e.textContent||'').trim()))[0];
if(sit){tap(sit);if(sit.parentElement)tap(sit.parentElement);}
await until(()=>vis(document.getElementById('screen-match')),9000);
await until(()=>typeof G!=='undefined'&&G&&G.phase==='idle',14000);
try{dbgWin();}catch(e){}
await until(()=>vis(document.getElementById('end-ov')),9000);
await sleep(2500);
tap(document.querySelectorAll('#end-ov .fo-offer .fcv')[1]);await sleep(1000);
const scrim=document.getElementById('foFocusScrim'),pan=document.getElementById('foFocusPanel');
const sc=scrim?getComputedStyle(scrim):null,pc2=pan?getComputedStyle(pan):null;
const sr=scrim?scrim.getBoundingClientRect():null;
return {rules:{scrim:ruleScan('foFocusScrim'),panel:ruleScan('foFocusPanel').slice(0,6),claim:ruleScan('foClaimBtn').length},
 cls:document.getElementById('end-ov').classList.contains('fo-focus'),
 scrim:sc?{pos:sc.position,op:sc.opacity,z:sc.zIndex,w:sr.width.toFixed(0),h:sr.height.toFixed(0),
   parent:scrim.parentElement.className.toString().slice(0,20)}:null,
 panel:pc2?{pos:pc2.position,op:pc2.opacity,z:pc2.zIndex,transform:pc2.transform.slice(0,40)}:null};
