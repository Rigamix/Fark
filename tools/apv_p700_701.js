/* P700: resume restamps the seat identity (portrait + dialogue globals).
 * P701: the bubble holds one position under 1-line, 3-line, and mid-shake.
 * SUITE: exclude */
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(fn,ms)=>{const t0=Date.now();while(Date.now()-t0<ms){try{if(fn())return true;}catch(e){}await sleep(60);}return false;};
const vis=el=>{if(!el||!el.isConnected)return false;const s=getComputedStyle(el),r=el.getBoundingClientRect();
 return s.display!=='none'&&s.visibility!=='hidden'&&+s.opacity>0.05&&r.width>1&&r.height>1;};
const tap=el=>{if(!vis(el))return false;const r=el.getBoundingClientRect();
 const o={bubbles:true,cancelable:true,clientX:r.left+r.width/2,clientY:r.top+r.height/2};
 el.dispatchEvent(new PointerEvent('pointerdown',o));el.dispatchEvent(new PointerEvent('pointerup',o));
 el.dispatchEvent(new MouseEvent('click',o));return true;};
for(let a=0;a<3;a++){tap(document.getElementById('hsBtnBottom'));await sleep(2000);
 await until(()=>document.querySelector('.nrdie'),9000);await sleep(500);
 tap(document.querySelector('.nrdie'));await sleep(1200);
 tap(document.getElementById('nrTakeBtn'));await sleep(2400);
 if(await until(()=>typeof launchSeat==='function'&&S&&S.run,9000))break;}
_getS();
/* PATRON launch: stamps identity */
try{G=null;}catch(e){}
window._fkDiscardOk=true;
launchSeat(0);
let ok=await until(()=>typeof G!=='undefined'&&G&&G.phase==='idle',16000);
if(!ok){try{G=null;}catch(e){}launchSeat(0);
 ok=await until(()=>typeof G!=='undefined'&&G&&G.phase==='idle',16000);}
if(!ok)return {err:'no idle'};
const out={};
out.launch={art:window._lastSeatArt,trait:window._lastSeatTrait,color:window._lastSeatColor,
 portrait:(getComputedStyle(document.getElementById('tokOImg')).backgroundImage||'').slice(0,60)};

/* P701: bubble geometry under three conditions */
const boxTop=()=>{const b=document.getElementById('dlgBox');return b?+b.getBoundingClientRect().top.toFixed(1):null;};
const scrollBox=()=>{const el=document.getElementById('dlgScroll');if(!el)return null;
 const r=el.getBoundingClientRect();return {t:+r.top.toFixed(1),h:+r.height.toFixed(1),c:+(r.top+r.height/2).toFixed(1)};};
out.dlgParent=document.getElementById('dlgBox').parentElement.id||document.getElementById('dlgBox').parentElement.className;
DLG.show('Short.');await sleep(700);
const s1=scrollBox(),t1=boxTop();
DLG.show('A very much longer line of patron talk that should wrap to three or so lines on a phone screen without moving anything at all.');
await sleep(700);
const s2=scrollBox(),t2=boxTop();
/* mid-shake: add the bust class to #diceArea and measure while it runs */
document.getElementById('diceArea').classList.add('bust-shake');
await sleep(120);
const t3=boxTop(),s3=scrollBox();
await sleep(600);
document.getElementById('diceArea').classList.remove('bust-shake');
out.bubble={parentOk:out.dlgParent==='screen-match'||String(out.dlgParent).indexOf('screen')>=0,
 short:s1,long:s2,boxTopStable:t1===t2&&t2===t3,
 centreDrift:+(Math.abs((s2?s2.c:0)-(s1?s1.c:0))).toFixed(1),
 shakeDrift:+(Math.abs((s3?s3.c:0)-(s2?s2.c:0))).toFixed(1)};

/* P700 resume leg: wipe the globals as a reload would, then resume */
try{exitMatch&&exitMatch();}catch(e){}
await sleep(600);
try{G=null;}catch(e){}
window._fkDiscardOk=true;
launchSeat(1);
ok=await until(()=>typeof G!=='undefined'&&G&&G.phase==='idle',16000);
if(!ok)return {...out,err:'no idle 2'};
const artAtLaunch=window._lastSeatArt;
out.pending=!!S.pendingMatch;
/* simulate the cold boot: globals gone, then resumeMatch */
window._lastSeatArt=null;window._lastSeatTrait=null;window._lastSeatColor=null;
window._fkDiscardOk=false;
try{G=null;}catch(e){}
resumeMatch();
await until(()=>typeof G!=='undefined'&&G&&vis(document.getElementById('screen-match')),12000);
await sleep(1500);
out.resume={art:window._lastSeatArt,trait:window._lastSeatTrait,color:window._lastSeatColor,
 artMatchesLaunch:window._lastSeatArt===artAtLaunch,
 portrait:(getComputedStyle(document.getElementById('tokOImg')).backgroundImage||'').slice(0,60),
 portraitHasUrl:(getComputedStyle(document.getElementById('tokOImg')).backgroundImage||'').indexOf('url')===0,
 dlgSayWorks:(function(){try{return _dlgSay(window._lastSeatArt)!==undefined;}catch(e){return 'ERR '+e;}})()};
out.verdict=!!(out.launch.art&&out.bubble.boxTopStable&&out.bubble.centreDrift<2&&out.bubble.shakeDrift<2
 &&out.pending&&out.resume.art&&out.resume.artMatchesLaunch&&out.resume.portraitHasUrl);
return out;
