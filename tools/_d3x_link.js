const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(fn,ms)=>{const t0=Date.now();while(Date.now()-t0<ms){try{if(fn())return true;}catch(e){}await sleep(100);}return false;};
await until(()=>typeof launchBossMatch==='function',20000);
_getS();window._fkDiscardOk=true;
S.run.tier=1;S.run.gold=500;
try{delete S.pendingMatch;}catch(e){}
launchBossMatch();
await until(()=>typeof G!=='undefined'&&G&&G.phase==='idle',15000);
await sleep(1500);
const Q=[];for(let i=0;i<12;i++)Q.push(i%2?5:1);
const realE=window._enchRollM;window._enchRollM=(m,e)=>Q.length?Q.shift():realE(m,e);
const tap=el=>{const r=el.getBoundingClientRect();const o={bubbles:true,cancelable:true,clientX:r.left+r.width/2,clientY:r.top+r.height/2};
  el.dispatchEvent(new PointerEvent('pointerdown',o));el.dispatchEvent(new PointerEvent('pointerup',o));el.dispatchEvent(new MouseEvent('click',o));};
tap(document.getElementById('btnRoll'));
await until(()=>G.phase==='choosing',12000);
await sleep(1200);
const free=(G.pool||[]).filter(d=>!d.committed);
const d0=free[0];
return {
  d3xExists:typeof D3X!=='undefined',
  d3xDiceCount:(typeof D3X!=='undefined'&&D3X.dice)?D3X.dice.length:null,
  matchDice:(typeof D3X!=='undefined'&&D3X.dice)?D3X.dice.filter(x=>x.match).length:null,
  visibleDice:(typeof D3X!=='undefined'&&D3X.dice)?D3X.dice.filter(x=>x.match&&x.obj&&x.obj.visible).length:null,
  elIsChip:(typeof D3X!=='undefined'&&D3X.dice&&D3X.dice[0])?(D3X.dice[0].chip===d0.el):null,
  poolElHas_d3:!!(d0&&d0.el&&d0.el._d3),
  chipMatchesSomePoolEl:(typeof D3X!=='undefined'&&D3X.dice)?D3X.dice.filter(x=>x.match).map(x=>free.some(f=>f.el===x.chip)):null,
  rolling:(typeof D3X!=='undefined'&&D3X._rolling)?D3X._rolling():null,
  d3Match:window.D3_MATCH,
  glowCanvasNow:!!document.getElementById('dgCanvas'),
};
