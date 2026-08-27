const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(fn,ms)=>{const t0=Date.now();while(Date.now()-t0<ms){try{if(fn())return true;}catch(e){}await sleep(120);}return false;};
const tap=el=>{if(!el)return false;const r=el.getBoundingClientRect();
  const o={bubbles:true,cancelable:true,clientX:r.left+r.width/2,clientY:r.top+r.height/2};
  el.dispatchEvent(new PointerEvent('pointerdown',o));el.dispatchEvent(new PointerEvent('pointerup',o));
  el.dispatchEvent(new MouseEvent('click',o));return true;};
if(!await until(()=>typeof launchSeat==='function',20000))return {err:'no boot'};
if(typeof _getS==='function')_getS();
window._fkDiscardOk=true;
try{delete S.pendingMatch;}catch(e){}
try{if(S.run&&S.run.night){S.run.night.seatsPlayed=S.run.night.roster.map(()=>false);S.run.night.results=S.run.night.roster.map(()=>null);}}catch(e){}
launchSeat(0);
if(!await until(()=>typeof G!=='undefined'&&G&&G.phase==='idle',15000))return {err:'no match'};
await sleep(2500);
const Q=[1,5,2,3,4,6];const realE=window._enchRollM;
window._enchRollM=(m,e)=>Q.length?Q.shift():realE(m,e);
let r0=false;for(let r=0;r<3&&!r0;r++){tap(document.getElementById('btnRoll'));r0=await until(()=>G.phase==='choosing',7000);}
await sleep(500);
/* the CSS square must be gone */
const probe=document.querySelector('#playerDiceRow .die');
probe.classList.add('break-target');
const cs=getComputedStyle(probe);
const outlineOnArm={width:cs.outlineWidth,style:cs.outlineStyle};
probe.classList.remove('break-target');
/* arm steady hand: NOTHING should be marked */
const st={id:'steady_hand',fam:'iron',kind:'active',tier:2,charges:3,state:{}};
G.pF=[st];CFX.steady_hand.use(st,'p');
await sleep(300);
const armed={cardmarks:document.querySelectorAll('#playerDiceRow .die.cardmark').length,
  affordance:document.querySelectorAll('#playerDiceRow .die.break-target').length,
  status:(document.getElementById('statusMsg')||{}).textContent||''};
/* pick one: exactly that die gets the mark */
const d=(G.pool||[]).find(x=>!x.committed);
if(d&&d.el&&d.el.onclick)d.el.onclick();
await sleep(200);
const picked={cardmarks:document.querySelectorAll('#playerDiceRow .die.cardmark').length,
  onPicked:!!(d.el&&d.el.classList.contains('cardmark'))};
await sleep(1100);
const afterFade={cardmarks:document.querySelectorAll('#playerDiceRow .die.cardmark').length};
return {outlineOnArm,armed,picked,afterFade,
  hullPainterReadsMark:/cardmark/.test(String(D3X._paintSel||D3X.paintSel||'')) ||
    /cardmark/.test(document.documentElement.outerHTML),
  verdicts:{
    squareOutlineGone:outlineOnArm.style==='none'||outlineOnArm.width==='0px',
    armMarksNothing:armed.cardmarks===0,
    armKeepsAffordance:armed.affordance>0,
    pickMarksExactlyOne:picked.cardmarks===1&&picked.onPicked,
    markFades:afterFade.cardmarks===0},
  verdict:(outlineOnArm.style==='none'||outlineOnArm.width==='0px')&&armed.cardmarks===0
    &&picked.cardmarks===1&&picked.onPicked&&afterFade.cardmarks===0};
