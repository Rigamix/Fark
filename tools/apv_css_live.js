/* PHASE 3 — does the rule exist, AND does it hit anything?
 *
 * Two checks, and conflating them is what let the plan overstate its coverage:
 *
 *   3a  IS THE RULE IN THE CSSOM?  `.ptcard .lwho` was swallowed whole when a
 *       comment lost its opener, and CSS error-recovery ate the rule after it.
 *       Four rounds of "the busts are too small" were that. Presence catches it.
 *
 *   3b  DID THE RULE FIND ANYTHING?  `.end-draft-slots` parsed perfectly and
 *       targeted a class that does not exist on the screen it was written for.
 *       3a passes it. Only asking whether the selector matches a live element -
 *       on the screen it is FOR - catches that. Extended to a non-zero box it
 *       also catches `.win-art`, which lost a specificity fight to
 *       `#end-ov>*{position:relative}` and collapsed to 0x0.
 *
 * WHY THIS DRIVES THE GAME rather than checking one page. A selector for the
 * match screen cannot match on the home screen, so a naive sweep reports false
 * failures for every rule not currently on stage. Each entry therefore names
 * the screen it belongs to, and the probe walks home -> match -> win overlay,
 * checking each set at the moment that screen is actually up. */
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(fn,ms)=>{const t0=Date.now();while(Date.now()-t0<ms){try{if(fn())return true;}catch(e){}await sleep(60);}return false;};
const vis=el=>{if(!el||!el.isConnected)return false;const s=getComputedStyle(el),r=el.getBoundingClientRect();
 return s.display!=='none'&&s.visibility!=='hidden'&&+s.opacity>0.05&&r.width>1&&r.height>1;};
const tap=el=>{if(!vis(el))return false;const r=el.getBoundingClientRect();
 const o={bubbles:true,cancelable:true,clientX:r.left+r.width/2,clientY:r.top+r.height/2};
 el.dispatchEvent(new PointerEvent('pointerdown',o));el.dispatchEvent(new PointerEvent('pointerup',o));
 el.dispatchEvent(new MouseEvent('click',o));return true;};

/* ── the load-bearing selectors, by the screen they belong to ──
   Chosen because each one's absence is SILENT: the page still renders, nothing
   errors, and the only symptom is that something looks wrong. box:true means a
   zero-sized match is also a failure. */
const WATCH = {
  match: [
    {sel:'.ptcard .lwho', box:false},   /* the patron bust. Lost to a comment. */
    {sel:'.ptcard .lfront', box:false},
    {sel:'#playerDiceRow', box:true}
  ],
  win: [
    {sel:'.win-art',    box:true},      /* collapsed to 0x0 on a specificity loss */
    {sel:'.win-bg',     box:true},
    {sel:'.win-panel',  box:true},
    {sel:'.win-board',  box:true},
    {sel:'.fo-offer',   box:true},      /* the three cards */
    {sel:'.fo-deck',    box:true},      /* the spread. Its predecessor was styled
                                           on a class not present here at all. */
    {sel:'.fo-skip',    box:true}
  ]
};

/* every selector the browser actually parsed */
const parsed = new Set();
for (const sh of document.styleSheets){
  let rs=null; try{ rs=sh.cssRules; }catch(e){ continue; }
  (function walk(list){ for(const r of list){
    if(r.selectorText) String(r.selectorText).split(',').forEach(s=>parsed.add(s.trim()));
    if(r.cssRules) walk(r.cssRules);
  } })(rs);
}

const out = { missingFromCSSOM:[], matchedNothing:[], zeroBox:[], checked:0 };

function checkSet(list, screen){
  for (const w of list){
    out.checked++;
    if (!parsed.has(w.sel)) out.missingFromCSSOM.push(w.sel + ' (' + screen + ')');
    const els = document.querySelectorAll(w.sel);
    if (!els.length){ out.matchedNothing.push(w.sel + ' (' + screen + ')'); continue; }
    if (w.box){
      const r = els[0].getBoundingClientRect();
      if (r.width <= 1 || r.height <= 1)
        out.zeroBox.push(w.sel + ' (' + screen + ') ' + Math.round(r.width) + 'x' + Math.round(r.height));
    }
  }
}

/* ── drive to the match screen ── */
tap(document.getElementById('hsBtnBottom')); await sleep(1800);
await until(()=>{const d=document.querySelector('.nrdie');return d&&d._floatDone;},9000);
tap(document.querySelector('.nrdie')); await sleep(1300);
tap(document.getElementById('nrTakeBtn')); await sleep(2200);
/* the patron cards are up here - .ptcard .lwho is on stage NOW */
await until(()=>[...document.querySelectorAll('.ptcard')].filter(vis).length>0,9000);
await sleep(700);
checkSet(WATCH.match.filter(w=>w.sel.indexOf('.ptcard')===0), 'patron select');

const pc=[...document.querySelectorAll('.ptcard')].filter(vis)[0]; if(pc){tap(pc);await sleep(1700);}
const sit=[...document.querySelectorAll('span,div,button')].filter(e=>vis(e)&&e.children.length<=1&&/^SIT\s*DOWN$/i.test((e.textContent||'').trim()))[0];
if(sit){tap(sit);if(sit.parentElement)tap(sit.parentElement);}
await until(()=>vis(document.getElementById('screen-match')),9000);
await until(()=>typeof G!=='undefined'&&G&&G.phase==='idle',14000);
checkSet(WATCH.match.filter(w=>w.sel.indexOf('.ptcard')!==0), 'match');

/* ── and the win overlay ── */
try{ dbgWin(); }catch(e){ out.winErr=String(e); }
await until(()=>vis(document.getElementById('end-ov')),9000);
await sleep(3000);
checkSet(WATCH.win, 'win');

out.verdict = {
  allRulesParsed:   out.missingFromCSSOM.length === 0,
  allRulesMatched:  out.matchedNothing.length === 0,
  noneCollapsed:    out.zeroBox.length === 0
};
return out;
