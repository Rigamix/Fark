/* P872 - the surname must (a) render, (b) match the seat's persona, and
 * (c) be stable for the same patron. All three driven through _ptOpenPanel,
 * which is the function that builds the parchment. */
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(fn,ms)=>{const t0=Date.now();while(Date.now()-t0<ms){try{if(fn())return true;}catch(e){}await sleep(120);}return false;};
await until(()=>typeof showScreen==='function',20000);
_getS();
const TRAITS={ones:['Slowhand','Tallyman','Pennyweight','Twicecount','Coldfoot'],
  hoard:['Tightfist','Magpie','Deeppurse','Sockful','Neverlends'],
  aggro:['Neverblink','Breakneck','Hotblood','Onemore','Firebrand'],
  triples:['Threefold','Bullneck','Ironjaw','Thricelucky','Trebles'],
  straights:['Inarow','Straightlace','Dominoes','Ladderman','Onetosix'],
  combo:['Sleight','Sidewinder','Threadneedle','Foxglove','Everyangle']};

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
