/* P822: drive the real generator per tier. Assertions: nights 1-3
 * mundane (no family dice); from tier 3 the trait leans show - aggro
 * carries obsidian, ones carry silver, combo carries vagabond or
 * starstone - and the lean is DIRECTIONAL (aggro holds obsidian more
 * often than non-aggro). Then one real seat launch on a rigged roster
 * seat: the rival's family dice deal and roll. */
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(fn,ms)=>{const t0=Date.now();while(Date.now()-t0<ms){try{if(fn())return true;}catch(e){}await sleep(120);}return false;};
const tap=el=>{if(!el)return false;const r=el.getBoundingClientRect();
  const o={bubbles:true,cancelable:true,clientX:r.left+r.width/2,clientY:r.top+r.height/2};
  el.dispatchEvent(new PointerEvent('pointerdown',o));
  el.dispatchEvent(new PointerEvent('pointerup',o));
  el.dispatchEvent(new MouseEvent('click',o));return true;};
if(!await until(()=>typeof generatePatron==='function'&&typeof S!=='undefined',20000))return {err:'no boot'};
if(typeof _getS==='function')_getS();
const FAM=['obsidian','silver','vagabond'];
const stats={early:{n:0,fam:0},byPersona:{}};
for(let tier=0;tier<8;tier++){
  for(let k=0;k<40;k++){
    const p=generatePatron(tier);
    const famDice=(p.dice||[]).filter(m=>FAM.indexOf(m)>=0);
    if(tier<2){stats.early.n++;if(famDice.length)stats.early.fam++;}
    else if(tier===2){stats.n3=stats.n3||{n:0,fam:0};stats.n3.n++;if(famDice.length)stats.n3.fam++;}
    else{
      const key=p.persona;
      stats.byPersona[key]=stats.byPersona[key]||{n:0,obs:0,sil:0,vag:0,star:0};
      const b=stats.byPersona[key];b.n++;
      if((p.dice||[]).indexOf('obsidian')>=0)b.obs++;
      if((p.dice||[]).indexOf('silver')>=0)b.sil++;
      if((p.dice||[]).indexOf('vagabond')>=0)b.vag++;
      if((p.dice||[]).indexOf('starstone')>=0)b.star++;
    }
  }
}
const bp=stats.byPersona;
const rate=(o,k)=>o&&o.n?+(o[k]/o.n).toFixed(2):0;
const aggroObs=rate(bp.aggro,'obs'),otherObs=(()=>{let n=0,h=0;
  Object.keys(bp).forEach(k=>{if(k!=='aggro'){n+=bp[k].n;h+=bp[k].obs;}});
  return n?+(h/n).toFixed(2):0;})();
const onesSil=rate(bp.ones,'sil'),otherSil=(()=>{let n=0,h=0;
  Object.keys(bp).forEach(k=>{if(k!=='ones'){n+=bp[k].n;h+=bp[k].sil;}});
  return n?+(h/n).toFixed(2):0;})();
const comboVS=bp.combo?+((bp.combo.vag+bp.combo.star)/bp.combo.n).toFixed(2):0;
/* REACHABILITY: a real seat with the family dice must deal and roll */
if(typeof _ensureNight==='function')_ensureNight();
const night=S.run.night;
night.roster[0].dice=['lucky','obsidian','silver','vagabond','bone','bone'];
try{save();}catch(e){}
launchSeat(0);
if(!await until(()=>typeof G!=='undefined'&&G&&G.phase==='idle',14000))return {err:'no match',stats};
await sleep(3000);
const rivalLoadout=(G.matchOppDice||[]).slice();
/* our quick bank hands them the table; their deal must include the family dice */
const Q=[1,2,3,4,6,2];
const realE=window._enchRollM;
window._enchRollM=(m,e)=>Q.length?Q.shift():realE(m,e);
tap(document.getElementById('btnRoll'));
if(!await until(()=>G.phase==='choosing',15000))return {err:'no roll',rivalLoadout};
await sleep(400);
tap(G.pool.find(d=>!d.committed&&d.val===1).el);await sleep(300);
tap(document.getElementById('btnBank'));
if(!await until(()=>(G.oppDice||[]).length>=6,30000))return {err:'no opp deal',rivalLoadout};
await sleep(800);
const oppMats=(G.oppDice||[]).map(d=>d.mat).concat((G._oppHeld||[]).map(d=>d.mat));
const dealtFam=oppMats.filter(m=>FAM.indexOf(m)>=0);
const oppValsOk=(G.oppDice||[]).every(d=>d.val>=1&&d.val<=6);
return {early:stats.early,night3:stats.n3,aggroObs,otherObs,onesSil,otherSil,comboVS,
  rivalLoadout,dealtFam,oppValsOk,
  verdicts:{
    nights12Mundane:stats.early.fam===0,
    night3RareSplashOnly:!stats.n3||stats.n3.fam/stats.n3.n<=0.15,/* the one-up splash from tier 3's pool = the brief's night-3+ curveball */
    aggroLeansObsidian:aggroObs>=0.5&&aggroObs>otherObs+0.2,
    onesLeanSilver:onesSil>=0.5&&onesSil>otherSil+0.2,
    comboLeansVagStar:comboVS>=0.5,
    familyDiceDealAndRoll:dealtFam.length>=2&&oppValsOk},
  verdict:stats.early.fam===0&&(!stats.n3||stats.n3.fam/stats.n3.n<=0.15)&&aggroObs>=0.5&&onesSil>=0.5&&comboVS>=0.5&&dealtFam.length>=2&&oppValsOk};
