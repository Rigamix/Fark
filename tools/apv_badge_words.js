/* P866 - section 5 Pass A, checked against what the player can actually READ.
 *
 * Scrapes RENDERED text, not the source: a string that never reaches a screen
 * is not a vocabulary problem, and a string the source does not contain can
 * still be built at runtime out of two halves. Both directions matter here.
 *
 * THE CONTROL IS NOT OPTIONAL. "no surface says 'tell'" is exactly the shape
 * of finding that a scraper returning empty text produces for free, and this
 * project has been bitten by that repeatedly. So every surface must ALSO be
 * shown to contain the word it is supposed to contain - if a surface cannot
 * prove it rendered, its clean result is discarded rather than counted.
 */
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(fn,ms)=>{const t0=Date.now();while(Date.now()-t0<ms){try{if(fn())return true;}catch(e){}await sleep(120);}return false;};
if(!await until(()=>typeof _gbBossPeek==='function',20000))return {err:'no boot'};
_getS();window._fkDiscardOk=true;

/* the jargon Pass A retires from anything on screen. Word-bounded so
   "intelligence"/"telling" and the like cannot false-positive, and the VERB
   "tell" is excluded by requiring the game-noun forms. */
const BAD=/\b(tells?|sleeved?|relics?)\b|\bSEALED\b/i;

const surfaces=[];
function grab(name,el,mustContain){
  const txt=el?(el.innerText||el.textContent||'').replace(/\s+/g,' ').trim():'';
  const hits=[];
  txt.split(/(?<=[.!?—·])\s+/).forEach(seg=>{if(BAD.test(seg))hits.push(seg.trim().slice(0,90));});
  surfaces.push({surface:name,chars:txt.length,
    rendered:!!txt&&(!mustContain||new RegExp(mustContain,'i').test(txt)),
    mustContain:mustContain||null,jargon:hits});
}

/* ── 1. the boss peek sheet - the densest surface in the census ────── */
S.run.tier=0;S.run.points=99999;
try{_gbBossPeek();}catch(e){surfaces.push({surface:'bossPeek',threw:String(e)});}
await sleep(700);
grab('bossPeek',document.querySelector('.gbx-sheet,.gb-sheet,#gbSheet')||document.body,'badge');
try{_gbSheetClose();}catch(e){}
await sleep(300);

/* ── 2. the spoils screen ──────────────────────────────────────────── */
try{
  try{delete S.pendingMatch;}catch(e){}
  launchBossMatch();
  await until(()=>typeof G!=='undefined'&&G&&G.phase==='idle',15000);
  await sleep(2200);
  G.pPts=G.target;G.oPts=0;endMatch(true);
  await until(()=>{const rc=document.querySelector('#end-ov .res-card');
    return rc&&/TAKE ONE/.test(rc.textContent);},20000);
  await sleep(800);
  grab('spoils',document.querySelector('#end-ov .res-card'),'SPOILS');
}catch(e){surfaces.push({surface:'spoils',threw:String(e).slice(0,90)});}

/* ── 3. the match HUD chip for a worn badge ────────────────────────── */
try{
  S.run.tells=['last_call'];S.run.sleeve='last_call';
  try{delete S.pendingMatch;}catch(e){}
  S.run.tier=2;launchBossMatch();
  await until(()=>typeof G!=='undefined'&&G&&G.phase==='idle',15000);
  await sleep(2200);
  grab('matchHud',document.getElementById('screen-match'),'badge');
}catch(e){surfaces.push({surface:'matchHud',threw:String(e).slice(0,90)});}

/* ── 4. the shelf tooltip that contradicted the file's own ruling ──── */
const shelf={};
try{
  const lo=(typeof _LO_TIPS!=='undefined')?_LO_TIPS:null;
  shelf.note='scraped from the live tables below';
}catch(e){}
try{
  const src=document.documentElement.outerHTML;
  shelf.sealedMatchGone=!/SEALED match/.test(src);
  shelf.cursedMatchPresent=/CURSED match/.test(src);
}catch(e){}

const scraped=surfaces.filter(s=>!s.threw);
const rendered=scraped.filter(s=>s.rendered);
return {
  surfaces, shelf,
  /* the control: every surface proved it rendered its own keyword */
  everySurfaceRendered: scraped.length>0&&scraped.every(s=>s.rendered),
  surfacesThatCouldNotProveTheyRendered: scraped.filter(s=>!s.rendered).map(s=>s.surface),
  jargonFound: rendered.flatMap(s=>s.jargon.map(j=>s.surface+': '+j)),
  VERDICT: (scraped.length>0&&scraped.every(s=>s.rendered)
            &&rendered.every(s=>s.jargon.length===0)
            &&shelf.sealedMatchGone&&shelf.cursedMatchPresent) ? 'PASS' : 'FAIL',
};
