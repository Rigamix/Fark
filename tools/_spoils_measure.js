const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(fn,ms)=>{const t0=Date.now();while(Date.now()-t0<ms){try{if(fn())return true;}catch(e){}await sleep(120);}return false;};
if(!await until(()=>typeof launchBossMatch==='function',20000))return {err:'no boot'};
_getS();window._fkDiscardOk=true;S.run.tier=0;S.run.gold=500;
try{delete S.pendingMatch;}catch(e){}
launchBossMatch();
await until(()=>typeof G!=='undefined'&&G&&G.phase==='idle',15000);
await sleep(1600);G.pPts=G.target;G.oPts=0;endMatch(true);
await until(()=>{const rc=document.querySelector('#end-ov .res-card');return rc&&/TAKE ONE/.test(rc.textContent);},20000);
await sleep(1200);
const chain=[];
let el=document.querySelector('#end-ov .res-card [style*="grid-template-columns"]');
while(el&&chain.length<6){
  const r=el.getBoundingClientRect(),cs=getComputedStyle(el);
  chain.push({tag:el.tagName+(el.id?'#'+el.id:'')+(el.className?'.'+String(el.className).split(' ').join('.'):''),
    x:Math.round(r.x),w:Math.round(r.width),
    width:cs.width,maxWidth:cs.maxWidth,padding:cs.padding,transform:cs.transform,
    overflow:cs.overflow,boxSizing:cs.boxSizing});
  el=el.parentElement;
}
return {viewport:innerWidth,chain};
