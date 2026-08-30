/* P872 - the surname must (a) render, (b) match the seat's persona, and
 * (c) be stable for the same patron. All three driven through _ptOpenPanel,
 * which is the function that builds the parchment. */
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(fn,ms)=>{const t0=Date.now();while(Date.now()-t0<ms){try{if(fn())return true;}catch(e){}await sleep(120);}return false;};
await until(()=>typeof showScreen==='function',20000);
_getS();
/* THE POOLS ARE READ OUT OF THE PAGE, not copied here. _FAMN_BY_TRAIT is a
   local inside _ptOpenPanel so it cannot be referenced directly - but a second
   copy in the probe is a copy that drifts, and a probe asserting against its
   own stale list is worse than no probe. Parsed from the source instead, so
   there is exactly one place the names live. */
const _src=document.documentElement.outerHTML;
const _tblM=_src.match(/_FAMN_BY_TRAIT=\{([\s\S]*?)\};/);
if(!_tblM)return {err:'could not read _FAMN_BY_TRAIT out of the page'};
const TRAITS={};
_tblM[1].replace(/(\w+):\[([^\]]*)\]/g,(m,k,list)=>{
  TRAITS[k]=list.split(',').map(x=>x.trim().replace(/^'|'$/g,''));return m;});

const seen=[],mismatches=[],lengths=new Set();
/* sweep several nights so plenty of given names and personas are covered */
for(let t=1;t<=6;t++){
  S.run.tier=t;S.run.gold=500;S.run.points=0;S.run.night=null;S.run._artPersona={};
  try{_ensureNight();}catch(e){}
  showScreen('gauntlet');
  await sleep(900);
  for(let i=0;i<(_ptSeats||[]).length;i++){
    const st=_ptSeats[i];
    try{_ptOpenPanel(st);}catch(e){seen.push({err:e.message});continue;}
    await sleep(60);
    const el=document.getElementById('ptvName');
    const full=(el&&el.textContent||'').replace(/\s+/g,' ').trim();
    const persona=st.pat&&st.pat.persona;
    const surname=full.split(' ').slice(1).join(' ');
    const ok=(TRAITS[persona]||[]).indexOf(surname)>=0;
    if(!ok)mismatches.push({full,persona,surname});
    lengths.add(surname.length);
    seen.push({given:st.name,persona,word:st.word,surname,full});
  }
}
/* stability: the same seat asked twice must give the same name */
let stable=true;
if(_ptSeats&&_ptSeats[0]){
  _ptOpenPanel(_ptSeats[0]);const a=document.getElementById('ptvName').textContent;
  _ptOpenPanel(_ptSeats[0]);const b=document.getElementById('ptvName').textContent;
  stable=(a===b);
}
const surnames=[...new Set(seen.filter(s=>s.surname).map(s=>s.surname))];
return {
  sampled:seen.length,
  distinctSurnames:surnames.length,
  surnames:surnames.sort(),
  examples:seen.slice(0,10).map(s=>s.full+'  ['+s.word+']'),
  mismatches,
  lengthSpread:[...lengths].sort((a,b)=>a-b),
  VERDICT:{
    rendered: seen.length>0&&seen.every(s=>!s.err),
    everySurnameMatchesPersona: mismatches.length===0,
    variedLengths: Math.max(...lengths)-Math.min(...lengths)>=4,
    stablePerPatron: stable,
  },
};
