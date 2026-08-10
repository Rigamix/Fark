/* P553 - the draft reached the way a PLAYER reaches it, not by calling
   famRunDraftShow() by hand.

   WHY THIS IS A DIFFERENT QUESTION. `sync` chooses the surface that owns the
   dice as `chips[0].closest('#loStage,#ptPanelSheet,#gbShop,#gbSheet,#nrStage,
   #screen-match')` - the FIRST live chip in document order decides for all of
   them, and every chip outside that host is then skipped. It also adds
   html.fk3d unconditionally, and since P553 that hides the draft's DOM cube.

   So if the tier screen underneath has a single sized .d3chip that sorts before
   the overlay, the draft's dice are hidden by CSS and drawn by nobody: three
   empty sockets on the first screen of a new run, which is the exact failure
   this surface has a written warning about. Calling famRunDraftShow() directly
   - which the other P553 probes do - never puts that screen underneath, so it
   cannot see this.

   The real path is renderTier's `if(S.run._famFirstDraft)famRunDraftShow()`.
   Drive the run to the gauntlet and let the game open it. */
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(f,ms)=>{const t=Date.now();while(Date.now()-t<ms){try{if(f())return true;}catch(e){}await sleep(60);}return false;};

_getS();
try{D3X.boot();}catch(e){}
if(!(await until(()=>D3X.ready,25000)))return{error:'D3X never booted'};
try{startNewRun();}catch(e){return{error:'startNewRun threw '+e.message};}
if(!S.run||!S.run._famFirstDraft)return{error:'the run did not arm the first draft'};
try{showScreen('gauntlet');}catch(e){return{error:'showScreen threw '+e.message};}
if(!(await until(()=>document.getElementById('famRunDraft'),9000)))
  return{error:'the gauntlet did not open the draft - the real entry path is broken'};
if(!(await until(()=>document.querySelectorAll('#nrDice .d3slot').length===3,9000)))
  return{error:'the draft never built its dice'};
await sleep(3000);

/* every sized chip on the page, in document order - the list sync sorts by */
const all=[...document.querySelectorAll('.d3chip')].filter(c=>{
  const r=c.getBoundingClientRect();return r.width>1&&r.height>1;});
const mineEls=[...document.querySelectorAll('#nrDice .d3chip')];
const held=(D3X.dice||[]).filter(d=>mineEls.indexOf(d.chip)>=0);
const foreign=all.filter(c=>mineEls.indexOf(c)<0);

const R={
  liveChipsOnPage:all.length,
  firstIsDraft:all.length?mineEls.indexOf(all[0])>=0:null,
  foreign:foreign.map(c=>(c.closest('[id]')||{}).id||c.className).slice(0,6),
  mount:D3X.mount&&(D3X.mount.id||D3X.mount.className),
  draftAdopted:held.length,
  draftDrawn:held.filter(d=>d.obj&&d.obj.visible).length,
  fk3d:document.documentElement.classList.contains('fk3d'),
  domCubesHidden:[...document.querySelectorAll('#nrDice .d3die')]
    .filter(e=>getComputedStyle(e).visibility==='hidden').length};

return {R,
  verdict:
    R.draftAdopted!==3 ? 'FAIL - reached the real way, D3X adopted '+R.draftAdopted
      +'/3 draft dice. Mount is '+R.mount+' and the competing chips are ['
      +R.foreign.join(', ')+'] - fk3d is '+R.fk3d+' and '+R.domCubesHidden
      +'/3 DOM cubes are hidden, so that many sockets are EMPTY'
  : R.draftDrawn!==3 ? 'FAIL - adopted but not drawn: '+R.draftDrawn+'/3'
  : !R.fk3d ? 'INCONCLUSIVE - fk3d off, so the hide rule was never in play'
  : R.domCubesHidden!==3 ? 'FAIL - the DOM cubes are not hidden, so both renderers are drawing'
  : 'PASS - the gauntlet opens the draft, '+R.liveChipsOnPage+' live chips on the page and all 3 draft dice are D3X\'s, on '+R.mount};
