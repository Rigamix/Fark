/* P837, four legs. (1) 200 night-8 patrons: no raw tier-III cards.
 * (2) with the registry seeded for all 30 names, every generated
 * seat's persona matches its name's registry entry. (3) recognition:
 * a band jump speaks the :recog line once; the next open does not; a
 * first-ever meeting records silently. (4) the rival's obsidian
 * shatters on a real roll: die out of the match, +1000 to their
 * score, the armed fog marker's lane repaired, snapshot follows. */
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(fn,ms)=>{const t0=Date.now();while(Date.now()-t0<ms){try{if(fn())return true;}catch(e){}await sleep(120);}return false;};
const tap=el=>{if(!el)return false;const r=el.getBoundingClientRect();
  const o={bubbles:true,cancelable:true,clientX:r.left+r.width/2,clientY:r.top+r.height/2};
  el.dispatchEvent(new PointerEvent('pointerdown',o));
  el.dispatchEvent(new PointerEvent('pointerup',o));
  el.dispatchEvent(new MouseEvent('click',o));return true;};
if(!await until(()=>typeof generatePatron==='function'&&typeof S!=='undefined',20000))return {err:'no boot'};
if(typeof _getS==='function')_getS();
/* leg 1: tier locks */
let t3=0,t2=0;
for(let k=0;k<200;k++){
  const p=generatePatron(7);
  (p.fcards||[]).forEach(c=>{if(c.tier===3)t3++;if(c.tier===2)t2++;});
}
/* leg 2: the registry rules generation */
S.run._artPersona={};
PT_ART_POOL.forEach((a,i)=>{S.run._artPersona[a]=['ones','hoard','aggro','triples','straights','combo'][i%6];});
delete S.run.night;S.run.tier=3;
_ensureNight();
const roster=S.run.night.roster;
const bound=roster.every(p=>p._art&&p.persona===S.run._artPersona[p._art]);
/* leg 3: recognition */
S.run._artBand={krox:0};
window._lastSeatArt='Krox';window._lastSeatTrait='steady';
S.run.tier=3;/* night 4 = band 1 */
const recog=DLG.getLine('MATCH_START');
const recogAgain=DLG.getLine('MATCH_START');
S.run._artBand={};window._lastSeatArt='Vess';
const firstEver=DLG.getLine('MATCH_START');
const vessRecorded=S.run._artBand['vess'];
window._lastSeatArt=null;
/* leg 4: the rival shatter, on a real seat */
S.run.tier=0;delete S.run.night;
launchSeat(0);
if(!await until(()=>typeof G!=='undefined'&&G&&G.phase==='idle',14000))return {err:'no match'};
await sleep(3000);
G.matchOppDice=['obsidian','bone','bone','bone','bone','bone'];
getDie('obsidian').effect.chance=1;/* force the 6% for the probe */
_lmArm('_fog',3,99);/* a marker above the doomed lane - must repair to 2 */
const o0=G.oPts;
const Q=[1,2,3,4,6,2];
const realE=window._enchRollM;
window._enchRollM=(m,e)=>Q.length?Q.shift():realE(m,e);
tap(document.getElementById('btnRoll'));
if(!await until(()=>G.phase==='choosing',15000))return {err:'no roll'};
await sleep(400);
tap(G.pool.find(d=>!d.committed&&d.val===1).el);await sleep(300);
tap(document.getElementById('btnBank'));
const shattered=await until(()=>G.matchOppDice.length===5,40000);
await sleep(600);
getDie('obsidian').effect.chance=0.06;/* restore the def */
const oGain=G.oPts-o0;
const fogLane=G._fog&&G._fog.lane;
const snapLen=(S.pendingMatch&&S.pendingMatch.matchOppDice)?S.pendingMatch.matchOppDice.length:null;
return {t3,t2,bound,recog,recogAgain,firstEver,vessRecorded,
  shattered,oGain,fogLane,snapLen,
  verdicts:{
    noRawTier3:t3===0&&t2>0,
    registryRulesGeneration:bound,
    recognitionSpeaksOnce:!!recog&&/been around|while now/i.test(recog)&&recogAgain!==recog,
    firstEverSilentRecord:vessRecorded===1&&firstEver!==null,
    rivalShattered:shattered,
    shatterPaid:oGain>=1000,
    fogLaneRepaired:fogLane===2,
    snapshotFollows:snapLen===5},
  verdict:t3===0&&bound&&!!recog&&recogAgain!==recog&&shattered&&oGain>=1000&&fogLane===2&&snapLen===5};
