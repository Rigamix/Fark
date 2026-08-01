/* THE FEAT SPLASH MUST NOT PAINT - and feats must still be earned.
 * Both halves matter: silencing the overlay by breaking the award path would
 * be a worse bug than the one being fixed. Drives a real match, forces a win,
 * then watches #feat-ov while the unlock queue drains. */
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
tap(document.getElementById('nrTakeBtn'));await sleep(2200);
const pc=[...document.querySelectorAll('.ptcard')].filter(vis)[0];if(pc){tap(pc);await sleep(1700);}
const sit=[...document.querySelectorAll('span,div,button')].filter(e=>vis(e)&&e.children.length<=1&&/^SIT\s*DOWN$/i.test((e.textContent||'').trim()))[0];
if(sit){tap(sit);if(sit.parentElement)tap(sit.parentElement);}
await until(()=>vis(document.getElementById('screen-match')),9000);
await until(()=>typeof G!=='undefined'&&G&&G.phase==='idle',14000);

const out={};
/* watch the overlay for the whole window, not just at one instant - the
   splash is a 2.4s burst and a single sample can miss it entirely */
const ov=document.getElementById('feat-ov');
out.overlayExists=!!ov;
let peak=0, flashes=0, names=[];
const watch=setInterval(()=>{
  if(!ov)return;
  const o=+getComputedStyle(ov).opacity||0;
  if(o>peak)peak=o;
  if(o>0.05){flashes++;const t=(ov.textContent||'').trim();if(t&&names.indexOf(t)<0)names.push(t.slice(0,60));}
},80);

/* force the win through the real path: endMatch -> evaluateFeats -> queue */
try{ dbgWin(); }catch(e){ out.winErr=String(e); }
await sleep(2500);
out.pendingAfterWin=(S.run&&S.run._pendingFeatUnlocks||[]).slice();

/* then drain it the way initGauntletScreen does */
let drained=false;
try{ _drainFeatUnlockQueue(function(){drained=true;}); }catch(e){ out.drainErr=String(e); }
await sleep(3500);
clearInterval(watch);

out.drainCompleted=drained;
out.overlayPeakOpacity=peak;
out.overlayFlashSamples=flashes;
out.overlayNamesShown=names;
out.featsBanked=Object.keys((S&&S.featsDone)||{}).length;

out.verdict={
  splashNeverPainted: peak<=0.05 && flashes===0,
  queueStillDrains:   drained===true,
  featsStillEarned:   out.pendingAfterWin.length>0 || out.featsBanked>0
};
return out;
